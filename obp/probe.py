"""Fire bursts of tagged memo transactions into chosen leaders' windows.
DRY-RUN BY DEFAULT: transactions are built (and signed by a throwaway in-memory key that is never saved
or funded) and logged, but never sent. Real sending needs --live AND keypair files mounted via env."""
import base64, csv, json, logging, os, random, time, threading
from solders.keypair import Keypair
from solders.signature import Signature
from solders.transaction import VersionedTransaction
from .rpc import Rpc
from .txbuild import build_memo_tx, memo_tag
from .spendcap import SpendLedger, worst_case_fee

log = logging.getLogger("obp.probe")
SENT_FIELDS = ["run", "burst", "target", "label", "window_start", "send_seq", "order_mode", "payer_arm",
               "cu_price", "cu_limit", "payer", "signature", "memo", "send_ts_ns", "slot_at_send",
               "on_time", "live", "send_result"]


def load_keypairs(env_value: str | None):
    if not env_value:
        return []
    kps = []
    for p in env_value.split(","):
        with open(p.strip()) as f:
            kps.append(Keypair.from_bytes(bytes(json.load(f))))
    return kps


def calibrate_cu(rpc: Rpc, payer_pubkey: str, memo_len: int = 40) -> int | None:
    """simulateTransaction with sigVerify=false: read-only, costs nothing. payer_pubkey must be an
    existing system account with lamports (any public one works for simulation)."""
    from solders.pubkey import Pubkey
    from solders.message import MessageV0
    from solders.hash import Hash
    from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
    from solders.instruction import Instruction, AccountMeta
    from .txbuild import MEMO_PROGRAM
    pk = Pubkey.from_string(payer_pubkey)
    ixs = [set_compute_unit_limit(200_000), set_compute_unit_price(1),
           Instruction(MEMO_PROGRAM, b"x" * memo_len, [AccountMeta(pk, True, False)])]
    msg = MessageV0.try_compile(pk, ixs, [], Hash.default())
    tx = VersionedTransaction.populate(msg, [Signature.default()])
    res = rpc.call("simulateTransaction", [base64.b64encode(bytes(tx)).decode(),
                                           {"sigVerify": False, "replaceRecentBlockhash": True, "encoding": "base64"}])
    v = res["value"]
    if v.get("err"):
        log.warning("simulation error: %s", v["err"])
        return None
    return v.get("unitsConsumed")


def _wait_for_slot(rpc: Rpc, target_slot: int, poll=0.2, give_up_after=900):
    t0 = time.time()
    while time.time() - t0 < give_up_after:
        s = rpc.slot("processed")
        if s >= target_slot:
            return s
        time.sleep(poll if target_slot - s < 20 else min(5, (target_slot - s) * 0.3))
    return None


def run_bursts(rpc: Rpc, send_rpc: Rpc, plan: list[dict], out_csv: str, ledger: SpendLedger, *,
               live: bool, keypairs: list, run_id: str, fee_levels: list[int], cu_limit: int,
               lead_slots: int = 1, send_mode: str = "seq", gap_ms: int = 20, payer_arm: str = "same",
               seed: int = 1):
    if live and not keypairs:
        raise SystemExit("--live needs OBP_KEYPAIRS (paths to keypair JSON files, mounted as a volume)")
    payers = keypairs if live else [Keypair()]  # dry-run: throwaway, in memory only, never funded
    if payer_arm == "multi" and len(payers) < 2 and live:
        raise SystemExit("payer_arm=multi needs >=2 keypairs")
    rnd = random.Random(seed)
    modes = ["asc", "desc", "shuffle"]
    new_file = not os.path.exists(out_csv)
    with open(out_csv, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SENT_FIELDS)
        if new_file:
            w.writeheader()
        for b, item in enumerate(sorted(plan, key=lambda x: x["window_start"])):
            ws = item["window_start"]
            cur = rpc.slot("processed")
            if cur >= ws:
                log.info("skip window %s of %s (already at %s)", ws, item["target"][:8], cur)
                continue
            mode = modes[b % 3]
            levels = sorted(fee_levels)
            order = {"asc": levels, "desc": levels[::-1], "shuffle": rnd.sample(levels, len(levels))}[mode]
            _wait_for_slot(rpc, ws - lead_slots - 1)
            bh = rpc.latest_blockhash()["blockhash"]
            _wait_for_slot(rpc, ws - lead_slots)
            txs = []
            for seq, price in enumerate(order):
                payer = payers[seq % len(payers)] if (payer_arm == "multi" and live) else payers[0]
                memo = memo_tag(run_id, b, seq, price, mode)
                fee = worst_case_fee(1, cu_limit, price)
                if live:
                    ledger.reserve(fee, memo)  # raises SpendCapExceeded -> run stops
                txs.append((seq, price, payer, memo, build_memo_tx(payer, bh, memo, cu_limit, price)))
            slot_at_send = rpc.slot("processed")
            rows = []

            def send(seq, price, payer, memo, tx):
                ts = time.time_ns()
                res = "dry-run"
                if live:
                    try:
                        res = send_rpc.call("sendTransaction", [base64.b64encode(bytes(tx)).decode(),
                                            {"encoding": "base64", "skipPreflight": True, "maxRetries": 0}])
                        res = "ok"
                    except Exception as e:  # noqa: BLE001
                        res = f"error:{e}"[:200]
                rows.append({"run": run_id, "burst": b, "target": item["target"], "label": item["label"],
                             "window_start": ws, "send_seq": seq, "order_mode": mode, "payer_arm": payer_arm,
                             "cu_price": price, "cu_limit": cu_limit, "payer": str(payer.pubkey()),
                             "signature": str(tx.signatures[0]), "memo": memo, "send_ts_ns": ts,
                             "slot_at_send": slot_at_send, "on_time": slot_at_send < ws, "live": live, "send_result": res})

            if send_mode == "parallel":
                th = [threading.Thread(target=send, args=t) for t in txs]
                [t.start() for t in th]; [t.join() for t in th]
            else:
                for t in txs:
                    send(*t)
                    time.sleep(gap_ms / 1000)
            for r in sorted(rows, key=lambda r: r["send_seq"]):
                w.writerow(r)
            f.flush()
            log.info("burst %d -> %s (%s) window %d mode=%s sent_at_slot=%d %s remaining_cap=%s",
                     b, item["target"][:8], item["label"], ws, mode, slot_at_send,
                     "LIVE" if live else "DRY", ledger.remaining if live else "-")
