"""CLI. Default is dry-run everywhere. Examples:
  python -m obp inventory
  python -m obp plan --per-label 2 --windows 4
  python -m obp run                       # dry-run: builds + logs, sends nothing
  python -m obp run --live --cap-sol 0.04 # real sends (needs OBP_KEYPAIRS)
  python -m obp collect && python -m obp analyze
"""
import argparse, csv, json, logging, os, time
from .rpc import Rpc
from . import inventory, schedule, probe, collect, analyze
from .spendcap import SpendLedger, LAMPORTS_PER_SOL

DATA = os.environ.get("OBP_DATA", "data")


def p(*a):
    return os.path.join(DATA, *a)


def main():
    ap = argparse.ArgumentParser(prog="obp")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("inventory")
    pl = sub.add_parser("plan"); pl.add_argument("--per-label", type=int, default=2)
    pl.add_argument("--windows", type=int, default=4); pl.add_argument("--horizon", type=int, default=20_000)
    pl.add_argument("--labels", default="", help="comma list to restrict client labels")
    rn = sub.add_parser("run")
    rn.add_argument("--live", action="store_true", help="REALLY send. Without it nothing is sent.")
    rn.add_argument("--cap-sol", type=float, default=0.04)
    rn.add_argument("--fee-levels", default="0,1000,10000,100000,1000000", help="micro-lamports per CU")
    rn.add_argument("--cu-limit", type=int, default=int(os.environ.get("OBP_CU_LIMIT", 21000)))
    rn.add_argument("--lead-slots", type=int, default=1)
    rn.add_argument("--send-mode", choices=["seq", "parallel"], default="seq")
    rn.add_argument("--gap-ms", type=int, default=20)
    rn.add_argument("--payer-arm", choices=["same", "multi"], default="same")
    rn.add_argument("--max-bursts", type=int, default=0)
    cal = sub.add_parser("calibrate"); cal.add_argument("--sim-payer", required=True,
                                                     help="any existing funded pubkey; simulation only")
    sub.add_parser("collect"); sub.add_parser("analyze")
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
        wins, now = schedule.upcoming_windows(rpc, p("leader_schedule_cache.json"), a.horizon)
        tg = schedule.pick_targets(inv, wins, per_label=a.per_label)
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
        plan = json.load(open(p("plan.json")))["plan"]
        if a.max_bursts:
            plan = sorted(plan, key=lambda x: x["window_start"])[: a.max_bursts]
        ledger = SpendLedger(p("spend_ledger.json"), int(a.cap_sol * LAMPORTS_PER_SOL))
        kps = probe.load_keypairs(os.environ.get("OBP_KEYPAIRS")) if a.live else []
        if a.live:
            print(f"LIVE MODE. cap={ledger.cap} lamports, already reserved={ledger.reserved}")
        probe.run_bursts(rpc, send_rpc, plan, p("sent.csv"), ledger, live=a.live, keypairs=kps,
                         run_id=time.strftime("%m%d%H%M"), fee_levels=[int(x) for x in a.fee_levels.split(",")],
                         cu_limit=a.cu_limit, lead_slots=a.lead_slots, send_mode=a.send_mode, gap_ms=a.gap_ms,
                         payer_arm=a.payer_arm)
    elif a.cmd == "calibrate":
        print("memo tx compute units:", probe.calibrate_cu(rpc, a.sim_payer))
    elif a.cmd == "collect":
        collect.collect(rpc, p("sent.csv"), p("landed.csv"), p("blocks.csv"))
    elif a.cmd == "analyze":
        print(analyze.analyze(p("landed.csv"), p("results.csv")))


if __name__ == "__main__":
    main()
