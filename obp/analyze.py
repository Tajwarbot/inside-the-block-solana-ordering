"""Per burst: rank correlation of block position vs fee and vs send order, with a permutation null.
Only pairs of OUR transactions that landed in the SAME block are compared."""
import csv, random, statistics
from collections import defaultdict
from itertools import combinations


def kendall(xs, ys):
    c = d = 0
    for (x1, y1), (x2, y2) in combinations(zip(xs, ys), 2):
        s = (x1 - x2) * (y1 - y2)
        c += s > 0; d += s < 0
    return (c - d) / (c + d) if (c + d) else None


def perm_p(xs, ys, obs, n=2000, rnd=random.Random(0)):
    if obs is None:
        return None
    hits = 0
    for _ in range(n):
        ys2 = ys[:]; rnd.shuffle(ys2)
        t = kendall(xs, ys2)
        hits += t is not None and abs(t) >= abs(obs)
    return hits / n


def analyze(landed_csv, out_csv):
    rows = [r for r in csv.DictReader(open(landed_csv)) if r["landed"] == "True" and r["block_index"] not in ("", "None")]
    groups = defaultdict(list)
    for r in rows:
        groups[(r["run"], r["burst"], r["slot"])].append(r)
    res = []
    for (run, burst, slot), g in groups.items():
        if len(g) < 3:
            continue
        idx = [int(r["block_index"]) for r in g]
        fee = [-int(r["cu_price"]) for r in g]  # negative: "higher fee earlier" -> positive tau
        seq = [int(r["send_seq"]) for r in g]
        tf, ts = kendall(idx, fee), kendall(idx, seq)
        res.append({"run": run, "burst": burst, "slot": slot, "target": g[0]["target"], "label": g[0]["label"],
                    "order_mode": g[0]["order_mode"], "payer_arm": g[0]["payer_arm"], "n_same_block": len(g),
                    "in_target_window": g[0]["in_target_window"], "tau_fee": tf, "p_fee": perm_p(idx, fee, tf),
                    "tau_send": ts, "p_send": perm_p(idx, seq, ts)})
    if res:
        with open(out_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(res[0].keys()))
            w.writeheader(); w.writerows(res)
    by = defaultdict(list)
    for r in res:
        by[(r["label"], r["target"][:8], r["payer_arm"])].append(r)
    lines = ["| client | validator | arm | bursts | mean tau(fee) | mean tau(send) |", "|---|---|---|---|---|---|"]
    for (lab, tgt, arm), g in sorted(by.items()):
        mf = statistics.mean([x["tau_fee"] for x in g if x["tau_fee"] is not None] or [0])
        ms = statistics.mean([x["tau_send"] for x in g if x["tau_send"] is not None] or [0])
        lines.append(f"| {lab} | {tgt} | {arm} | {len(g)} | {mf:+.2f} | {ms:+.2f} |")
    return "\n".join(lines)
