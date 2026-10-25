"""CLI. Default is dry-run everywhere. Examples:
  python -m obp inventory
  python -m obp plan --per-label 2 --windows 4 --min-labels 1
  python -m obp run                       # dry-run: builds + logs, sends nothing
  python -m obp run --live --cap-sol 0.04 # real sends (needs payer keys)
  python -m obp run --live --mainnet      # additionally required on mainnet
  python -m obp fund --lamports 1000000   # dry-run unless --live
  python -m obp balances
  python -m obp collect && python -m obp verify-windows && python -m obp analyze
"""
import argparse, base64, csv, json, logging, os, subprocess, sys, time
import solders
from .rpc import Rpc, guard_live_cluster
from . import __version__, inventory, schedule, probe, collect, analyze, windows
from .spendcap import SpendLedger, LAMPORTS_PER_SOL, ledger_path, worst_case_fee
from .txbuild import build_transfer_tx

DATA = os.environ.get("OBP_DATA", "data")


def p(*a):
    return os.path.join(DATA, *a)


def _git_commit():
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                           cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _write_run_meta(a, cluster):
    meta = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cluster": cluster,
        "args": vars(a),
        "argv": sys.argv[1:],
        "git_commit": _git_commit(),
        "obp_version": __version__,
        "solders_version": getattr(solders, "__version__", None),
    }
    with open(p("run_meta.json"), "w") as f:
        json.dump(meta, f, indent=1)


def _checked_cluster(a, rpc, send_rpc):
    cluster = rpc.cluster()
    if getattr(a, "live", False):
        send_cluster = send_rpc.cluster()
        if send_cluster != cluster:
            raise SystemExit(f"RPC_URL is {cluster} but SEND_RPC_URL is {send_cluster}; refusing to mix clusters")
        cluster = send_cluster
        guard_live_cluster(cluster, live=True, allow_mainnet=getattr(a, "mainnet", False))
    return cluster


def _load_keys(env_value, payer_arm):
    try:
        return probe.load_keypairs(env_value, payer_arm)
    except FileNotFoundError as e:
        raise SystemExit(f"missing payer key file: {e.filename} (set OBP_KEYPAIRS or add the default /keys/payer*.json)")


def cmd_balances(rpc):
    env = os.environ.get("OBP_KEYPAIRS")
    paths = probe.keypair_paths(env, "multi")
    if not env:
        paths = [x for x in paths if os.path.exists(x)]
    if not paths:
        raise SystemExit("no payer keypair files found (expected /keys/payer.json or OBP_KEYPAIRS)")
    for path in paths:
        try:
            kp = probe.load_keypair(path)
        except OSError as e:
            raise SystemExit(f"cannot read keypair file {path}: {e}")
        bal = rpc.balance(str(kp.pubkey()))
        name = os.path.splitext(os.path.basename(path))[0]
        print(f"{name:<8} {kp.pubkey()} {bal:>15} lamports  {bal / LAMPORTS_PER_SOL:.9f} SOL")


def cmd_fund(a, rpc, send_rpc):
    env = os.environ.get("OBP_KEYPAIRS")
    kps = _load_keys(env, "multi")
    if len(kps) < 2:
        raise SystemExit("fund needs a main payer plus at least one extra payer (OBP_KEYPAIRS comma list)")
    cluster = _checked_cluster(a, rpc, send_rpc) if a.live else rpc.cluster()
    main, extras = kps[0], kps[1:]
    fee = worst_case_fee(1, 0, 0)
    total = (a.lamports + fee) * len(extras)
    print(f"cluster={cluster} source={main.pubkey()} recipients={len(extras)} "
          f"lamports each={a.lamports} fee each={fee} total={total}")
    for kp in extras:
        print(f"  -> {kp.pubkey()}")
    if not a.live:
        print("DRY RUN: no transfer sent (use --live; mainnet also needs --mainnet)")
        return
    ledger = SpendLedger(ledger_path(DATA, cluster), int(a.cap_sol * LAMPORTS_PER_SOL))
    bal = rpc.balance(str(main.pubkey()))
    if bal < total:
        raise SystemExit(f"source payer {main.pubkey()} has {bal} lamports < required {total} (transfers+fees)")
    if ledger.remaining < total:
        raise SystemExit(f"spend cap remaining {ledger.remaining} < required {total}")
    ledger.reserve(total, "fund extra payers")
    bh = rpc.latest_blockhash()["blockhash"]
    failed = []
    for kp in extras:
        tx = build_transfer_tx(main, kp.pubkey(), a.lamports, bh)
        try:
            send_rpc.call("sendTransaction", [base64.b64encode(bytes(tx)).decode(),
                          {"encoding": "base64", "skipPreflight": True, "maxRetries": 0}])
            print(f"sent {a.lamports} lamports -> {kp.pubkey()} sig={tx.signatures[0]}")
        except Exception as e:  # noqa: BLE001
            failed.append(kp.pubkey())
            print(f"FAILED -> {kp.pubkey()}: {e}")
    if failed:
        raise SystemExit(f"{len(failed)} funding transfer(s) failed")


def main():
    ap = argparse.ArgumentParser(prog="obp")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("inventory")
    pl = sub.add_parser("plan"); pl.add_argument("--per-label", type=int, default=2)
    pl.add_argument("--windows", type=int, default=4); pl.add_argument("--horizon", type=int, default=20_000)
    pl.add_argument("--labels", default="", help="comma list to restrict client labels")
    pl.add_argument("--min-labels", type=int, default=3)
    pl.add_argument("--min-windows", type=int, default=3)
    pl.add_argument("--min-lead-slots", type=int, default=25,
                    help="only plan windows starting at least this many slots after the current slot")
    rn = sub.add_parser("run")
    rn.add_argument("--live", action="store_true", help="REALLY send. Without it nothing is sent.")
    rn.add_argument("--mainnet", action="store_true", help="extra explicit opt-in required for --live on mainnet")
    rn.add_argument("--cap-sol", type=float, default=0.04)
    rn.add_argument("--fee-levels", default="0,1000,10000,100000,1000000", help="micro-lamports per CU")
    rn.add_argument("--cu-limit", type=int, default=int(os.environ.get("OBP_CU_LIMIT", 21000)))
    rn.add_argument("--lead-slots", type=int, default=2)
    rn.add_argument("--send-mode", choices=["seq", "parallel"], default="seq")
    rn.add_argument("--gap-ms", type=int, default=20)
    rn.add_argument("--payer-arm", choices=["same", "multi"], default="same")
    rn.add_argument("--max-bursts", type=int, default=0)
    fu = sub.add_parser("fund")
    fu.add_argument("--lamports", type=int, required=True)
    fu.add_argument("--live", action="store_true", help="REALLY transfer. Without it nothing is sent.")
    fu.add_argument("--mainnet", action="store_true", help="extra explicit opt-in required for --live on mainnet")
    fu.add_argument("--cap-sol", type=float, default=0.04)
    sub.add_parser("balances")
    cal = sub.add_parser("calibrate"); cal.add_argument("--sim-payer", required=True,
                                                     help="any existing funded pubkey; simulation only")
    sub.add_parser("collect"); sub.add_parser("verify-windows"); sub.add_parser("analyze")
    a = ap.parse_args()
    os.makedirs(DATA, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler(p("obp.log"))])
    rpc = Rpc()
    send_rpc = Rpc(os.environ.get("SEND_RPC_URL", rpc.url), max_retries=1)

    if a.cmd == "inventory":
        rows = inventory.build(rpc, p("validators.csv"))
        for s in inventory.summary(rows):
            print(f"{s[0]:<22} nodes={s[1]:<5} stake%={s[2]:<6} versions={s[3]}")
    elif a.cmd == "plan":
        inv = list(csv.DictReader(open(p("validators.csv"))))
        for r in inv:
            r["stake_sol"] = float(r["stake_sol"])
        if a.labels:
            keep = set(a.labels.split(",")); inv = [r for r in inv if r["label"] in keep]
        wins, now = schedule.upcoming_windows(rpc, p("leader_schedule_cache.json"), a.horizon,
                                             min_lead_slots=a.min_lead_slots)
        tg = schedule.pick_targets(inv, wins, per_label=a.per_label, min_labels=a.min_labels,
                                   min_windows=a.min_windows)
        plan = [{"target": t["identity"], "label": t["label"], "version": t["version"], "window_start": w}
                for t in tg for w in wins[t["identity"]][: a.windows]]
        json.dump({"created_slot": now, "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "plan": plan}, open(p("plan.json"), "w"), indent=1)
        for t in tg:
            first = wins[t["identity"]][0]
            print(f"{t['label']:<20} {t['identity'][:10]} v{t['version']:<14} stake={t['stake_sol']:>12,.0f} "
                  f"next window in ~{(first - now) * 0.4 / 60:.1f} min ({len(wins[t['identity']])} windows in horizon)")
        print(f"{len(plan)} bursts planned -> {p('plan.json')}")
    elif a.cmd == "run":
        cluster = _checked_cluster(a, rpc, send_rpc)
        plan = json.load(open(p("plan.json")))["plan"]
        if a.max_bursts:
            plan = sorted(plan, key=lambda x: x["window_start"])[: a.max_bursts]
        ledger = SpendLedger(ledger_path(DATA, cluster), int(a.cap_sol * LAMPORTS_PER_SOL))
        kps = _load_keys(os.environ.get("OBP_KEYPAIRS"), a.payer_arm) if a.live else []
        _write_run_meta(a, cluster)
        print(f"cluster={cluster} mode={'LIVE' if a.live else 'DRY-RUN'} ledger={ledger.path} "
              f"cap={ledger.cap} already_reserved={ledger.reserved}")
        probe.run_bursts(rpc, send_rpc, plan, p("sent.csv"), ledger, live=a.live, keypairs=kps,
                         run_id=time.strftime("%m%d%H%M"), fee_levels=[int(x) for x in a.fee_levels.split(",")],
                         cu_limit=a.cu_limit, lead_slots=a.lead_slots, send_mode=a.send_mode, gap_ms=a.gap_ms,
                         payer_arm=a.payer_arm, cluster=cluster)
    elif a.cmd == "fund":
        cmd_fund(a, rpc, send_rpc)
    elif a.cmd == "balances":
        cmd_balances(rpc)
    elif a.cmd == "calibrate":
        print("memo tx compute units:", probe.calibrate_cu(rpc, a.sim_payer))
    elif a.cmd == "collect":
        collect.collect(rpc, p("sent.csv"), p("landed.csv"), p("blocks.csv"))
    elif a.cmd == "verify-windows":
        rows = windows.verify_windows(rpc, p("plan.json"), p("sent.csv"), p("windows.csv"))
        print(f"{len(rows)} windows -> {p('windows.csv')} "
              f"({sum(1 for r in rows if r['leaders_ok'])} have the target for all 4 slots)")
    elif a.cmd == "analyze":
        print(analyze.analyze(p("landed.csv"), p("results.csv"), sent_csv=p("sent.csv"),
                              blocks_csv=p("blocks.csv"), windows_csv=p("windows.csv"),
                              md_path=p("results.md")))


if __name__ == "__main__":
    main()
