"""Fire bursts of tagged memo transactions into chosen leaders' windows.
DRY-RUN BY DEFAULT: transactions are built (and signed by a throwaway in-memory key that is never saved
or funded) and logged, but never sent. Real sending needs --live AND keypair files mounted via env."""
import base64, csv, json, logging, os, random, time, threading
from collections import defaultdict
from solders.keypair import Keypair
from solders.signature import Signature
from solders.transaction import VersionedTransaction
from .rpc import Rpc, RpcError, expect_signature
from .txbuild import build_memo_tx, memo_tag
from .spendcap import SpendCapExceeded, SpendLedger, worst_case_fee

log = logging.getLogger("obp.probe")

SLOT_TIME_S = 0.212  # measured mainnet slot time post-Alpenglow (2026-10-25)
MAX_CU_LIMIT = 1_400_000


def validate_fee_levels(levels):
    if not levels or any(not isinstance(p, int) or isinstance(p, bool) or p < 0 for p in levels):
        raise ValueError("fee levels must be a non-empty list of non-negative integers")
    return levels


def validate_cu_limit(cu_limit):
    if not isinstance(cu_limit, int) or isinstance(cu_limit, bool) or not 1 <= cu_limit <= MAX_CU_LIMIT:
        raise ValueError(f"cu_limit must be an integer in 1..{MAX_CU_LIMIT}")
    return cu_limit


def _append_sent_rows(path, rows):
    new_file = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SENT_FIELDS)
        if new_file:
            w.writeheader()
        for r in rows:
            w.writerow(r)
        f.flush()
        os.fsync(f.fileno())


def _fill_sent_fields(path, rows, fields):
    values = {r["signature"]: {f: r.get(f, "") for f in fields} for r in rows}
    with open(path, newline="") as f:
        all_rows = list(csv.DictReader(f))
    for r in all_rows:
        v = values.get(r.get("signature"))
        if v:
            r.update(v)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SENT_FIELDS)
        w.writeheader()
        w.writerows(all_rows)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _fill_slot_after_send(path, rows):
    _fill_sent_fields(path, rows, ["slot_after_send", "burst_late"])

DEFAULT_MAIN = "/keys/payer.json"
DEFAULT_EXTRA = [f"/keys/payer{i}.json" for i in range(2, 6)]

SENT_FIELDS = ["run", "cluster", "burst", "target", "label", "window_start", "send_seq", "send_rank",
               "order_mode", "payer_arm", "n_unique_payers", "cu_price", "cu_limit", "payer",
               "signature", "memo", "send_ts_ns", "send_done_ns", "slot_at_send", "est_slot_at_send",
               "slot_after_send", "send_offset", "in_window_at_send", "send_phase", "burst_late",
               "on_time", "live", "send_result"]


def keypair_paths(env_value: str | None = None, payer_arm: str = "same") -> list[str]:
    """OBP_KEYPAIRS wins. Otherwise: main payer only for the same arm, all five for multi/alternate."""
    if env_value:
        return [p.strip() for p in env_value.split(",") if p.strip()]
    return [DEFAULT_MAIN] if payer_arm == "same" else [DEFAULT_MAIN, *DEFAULT_EXTRA]


def all_default_paths() -> list[str]:
    return [DEFAULT_MAIN, *DEFAULT_EXTRA]


def load_keypair(path: str):
    with open(path) as f:
        return Keypair.from_bytes(bytes(json.load(f)))


def load_keypairs(env_value: str | None = None, payer_arm: str = "same") -> list:
    return [load_keypair(path) for path in keypair_paths(env_value, payer_arm)]


def calibrate_cu(rpc: Rpc, payer_pubkey: str, memo_len: int | None = None) -> int | None:
    """simulateTransaction with sigVerify=false: read-only, costs nothing. payer_pubkey must be an
    existing system account with lamports (any public one works for simulation)."""
    from solders.pubkey import Pubkey
    from solders.message import MessageV0
    from solders.hash import Hash
    from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
    from solders.instruction import Instruction, AccountMeta
    from .txbuild import MEMO_PROGRAM
    if memo_len is None:
        memo_len = len(memo_tag(0, 0, 0, 0, "asc"))  # same size as a real probe tag, not 40 bytes
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


def _wait_for_slot(rpc: Rpc, target_slot: int, poll=0.05, give_up_after=900):
    t0 = time.time()
    while time.time() - t0 < give_up_after:
        s = rpc.slot("processed")
        if s >= target_slot:
            return s
        remaining = target_slot - s
        if remaining <= 6:
            time.sleep(poll)
        else:
            # At 0.212 s/slot the old 0.3 s-per-slot far sleep overshot. Stay six slots short and
            # use a conservative 0.15 s/slot estimate, but never sleep less than one poll interval.
            time.sleep(max(poll, min(5.0, (remaining - 6) * 0.15)))
    return None


def run_bursts(rpc: Rpc, send_rpc: Rpc, plan: list[dict], out_csv: str, ledger: SpendLedger, *,
               live: bool, keypairs: list, run_id: str, fee_levels: list[int], cu_limit: int,
               lead_slots: int = 2, send_mode: str = "seq", gap_ms: int = 20, payer_arm: str = "same",
               seed: int = 1, cluster: str = "localnet"):
    if live and not keypairs:
        raise SystemExit("--live needs payer keypairs (OBP_KEYPAIRS or the default /keys/payer*.json files)")
    validate_cu_limit(cu_limit)
    if not isinstance(gap_ms, int) or isinstance(gap_ms, bool) or gap_ms < 0:
        raise ValueError("gap_ms must be a non-negative integer")
    levels = sorted(validate_fee_levels(fee_levels))
    if live and payer_arm in ("multi", "alternate"):
        distinct = {str(kp.pubkey()) for kp in keypairs}
        need = len(levels) if payer_arm == "multi" else max(5, len(levels))
        if len(distinct) < need:
            raise SystemExit(f"payer_arm={payer_arm} needs >= {need} distinct payers "
                             f"(one per fee level; alternate needs at least five); got {len(distinct)}")
    payers = keypairs if live else [Keypair()]  # dry-run: throwaway, in memory only, never funded
    rnd = random.Random(seed)
    modes = ["asc", "desc", "shuffle"]

    def payer_for(seq, arm):
        return payers[seq % len(payers)] if (arm == "multi" and live) else payers[0]

    _append_sent_rows(out_csv, [])  # create the header even if every window is skipped
    prev_slot_after_send = None
    for b, item in enumerate(sorted(plan, key=lambda x: x["window_start"])):
        ws = item["window_start"]
        cur = rpc.slot("processed")
        if cur >= ws:
            log.info("skip window %s of %s (already at %s)", ws, item["target"][:8], cur)
            continue
        if prev_slot_after_send is not None and ws - prev_slot_after_send <= 8:
            log.info("skip window %s of %s: previous burst at slot %s is within 8 slots",
                     ws, item["target"][:8], prev_slot_after_send)
            continue
        mode = modes[b % 3]
        order = {"asc": levels, "desc": levels[::-1], "shuffle": rnd.sample(levels, len(levels))}[mode]
        arm = ("same" if b % 2 == 0 else "multi") if payer_arm == "alternate" else payer_arm

        # Check payer balances against this burst's worst-case fee BEFORE waiting/sending.
        if live:
            need = defaultdict(int)
            for seq, price in enumerate(order):
                need[str(payer_for(seq, arm).pubkey())] += worst_case_fee(1, cu_limit, price)
            for pk, amount in need.items():
                bal = rpc.balance(pk)
                if bal < amount:
                    raise SystemExit(f"payer {pk} has {bal} lamports but this burst can cost up to "
                                     f"{amount}; aborting before sending")

        # Fetch the blockhash and build/sign six slots before the send, never after the final wait.
        built_slot = _wait_for_slot(rpc, ws - lead_slots - 6)
        if built_slot is None:
            log.warning("skip window %s of %s: never reached build slot", ws, item["target"][:8])
            continue
        bh = rpc.latest_blockhash()["blockhash"]
        txs = []
        for seq, price in enumerate(order):
            payer = payer_for(seq, arm)
            memo = memo_tag(run_id, b, seq, price, mode)
            fee = worst_case_fee(1, cu_limit, price)
            txs.append((seq, price, payer, memo, fee, build_memo_tx(payer, bh, memo, cu_limit, price)))
        n_unique_payers = len({str(t[2].pubkey()) for t in txs})

        slot_at_send = _wait_for_slot(rpc, ws - lead_slots)
        if slot_at_send is None:
            log.warning("skip window %s of %s: never reached send slot", ws, item["target"][:8])
            continue
        if slot_at_send >= ws:
            # Final guard: the window already started, so a send cannot be on time and fees
            # would be wasted. Nothing has been reserved yet, so skipping is free.
            log.warning("skip window %s of %s: wait returned slot %s >= window start",
                        ws, item["target"][:8], slot_at_send)
            continue
        t_wait_return_ns = time.time_ns()
        rows, cap_errors = [], []
        sent_lock = threading.Lock()

        def send(seq, price, payer, memo, fee, tx):
            ts = time.time_ns()
            done = ts
            res = "dry-run"
            row = {"run": run_id, "cluster": cluster, "burst": b, "target": item["target"],
                   "label": item["label"], "window_start": ws, "send_seq": seq, "send_rank": "",
                   "order_mode": mode, "payer_arm": arm, "n_unique_payers": n_unique_payers,
                   "cu_price": price, "cu_limit": cu_limit, "payer": str(payer.pubkey()),
                   "signature": str(tx.signatures[0]), "memo": memo, "send_ts_ns": ts,
                   "send_done_ns": done, "slot_at_send": slot_at_send, "est_slot_at_send": "",
                   "slot_after_send": "", "send_offset": "", "in_window_at_send": "",
                   "send_phase": "", "burst_late": "", "on_time": "", "live": live,
                   "send_result": res}
            try:
                if live:
                    try:
                        ledger.reserve(fee, memo)  # only right before this send
                        ts = time.time_ns()  # immediately before the HTTP call
                        row["send_ts_ns"] = ts
                        try:
                            sig = send_rpc.call("sendTransaction", [base64.b64encode(bytes(tx)).decode(),
                                                {"encoding": "base64", "skipPreflight": True, "maxRetries": 0}])
                        finally:
                            done = time.time_ns()  # immediately after the HTTP call
                            row["send_done_ns"] = done
                        expect_signature(sig, str(tx.signatures[0]))
                        res = "ok"
                    except SpendCapExceeded as e:
                        cap_errors.append(e)
                        res = f"not-sent:{e}"[:200]
                    except RpcError as e:
                        res = ("error:signature-mismatch" if str(e).startswith("signature-mismatch")
                               else f"error:{e}"[:200])
                    except Exception as e:  # noqa: BLE001
                        res = f"error:{e}"[:200]
                est = slot_at_send + int((ts - t_wait_return_ns) // int(SLOT_TIME_S * 1e9))
                phase = "early" if est < ws else ("inside" if est < ws + 4 else "late")
                row.update(est_slot_at_send=est, send_offset=est - ws,
                           in_window_at_send=est < ws + 4, send_phase=phase,
                           on_time=est < ws, send_result=res)
            finally:
                # Persist this signature immediately, even if the send or a later step raises.
                with sent_lock:
                    _append_sent_rows(out_csv, [row])
                rows.append(row)

        if send_mode == "parallel":
            th = [threading.Thread(target=send, args=t) for t in txs]
            [t.start() for t in th]; [t.join() for t in th]
        else:
            for t in txs:
                send(*t)
                time.sleep(gap_ms / 1000)
        for rank, r in enumerate(sorted(rows, key=lambda r: r["send_ts_ns"])):
            r["send_rank"] = rank
        # Rows are already on disk; fill the derived order now and slot_after_send after the RPC.
        _fill_sent_fields(out_csv, rows, ["send_rank"])
        try:
            slot_after_send = rpc.slot("processed")
        except Exception as e:  # noqa: BLE001 - never lose sent signatures to a read failure
            log.warning("post-send slot lookup failed after burst %d: %s", b, e)
            slot_after_send = None
        burst_late = None
        if slot_after_send is not None:
            burst_late = slot_after_send >= ws + 4
            for r in rows:
                r["slot_after_send"] = slot_after_send
                r["burst_late"] = burst_late
            _fill_slot_after_send(out_csv, rows)
            if burst_late:
                log.warning("burst %d is late: slot_after_send %s >= window_start+4 (%s)",
                            b, slot_after_send, ws + 4)
        prev_slot_after_send = slot_after_send
        log.info("burst %d -> %s (%s) window %d mode=%s arm=%s sent_at_slot=%d offset=[%d..%d] after=%s "
                 "late=%s %s payers=%d remaining_cap=%s", b, item["target"][:8], item["label"], ws,
                 mode, arm, slot_at_send, min(r["send_offset"] for r in rows),
                 max(r["send_offset"] for r in rows), slot_after_send, burst_late,
                 "LIVE" if live else "DRY", n_unique_payers, ledger.remaining if live else "-")
        if cap_errors:
            raise cap_errors[0]
