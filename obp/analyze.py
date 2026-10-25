"""Analyze ordering data.

Per burst: rank correlation of block position vs fee and vs send order, with a permutation null.
Only pairs of OUR transactions that landed in the SAME block are compared.
Also: pooled per-label tests, landing/on-time rates, and a whole-block priority-fee check.
Whole-block priority fee per CU is an APPROXIMATION:
    (fee - 5000 * num_sigs) * 1e6 / cu_consumed
It ignores exact per-instruction costs and any other fee components. It is labelled as an
approximation everywhere it is reported.
"""
import csv, os, random, statistics, time
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations


def kendall(xs, ys):
    c = d = 0
    for (x1, y1), (x2, y2) in combinations(zip(xs, ys), 2):
        s = (x1 - x2) * (y1 - y2)
        c += s > 0
        d += s < 0
    return (c - d) / (c + d) if (c + d) else None


def perm_p(xs, ys, obs, n=2000, rnd=None):
    if obs is None:
        return None
    rnd = rnd or random.Random(0)
    hits = 0
    for _ in range(n):
        ys2 = ys[:]
        rnd.shuffle(ys2)
        t = kendall(xs, ys2)
        hits += t is not None and abs(t) >= abs(obs)
    return hits / n


def pooled_perm_p(bursts, key, n=2000, seed=0):
    """Observed sum of per-burst taus vs a null that shuffles fee/send order within each burst."""
    valid = [b for b in bursts if b[key] is not None]
    if not valid:
        return None
    obs = sum(b[key] for b in valid)
    ys_key = "fee" if key == "tf" else "seq"
    rnd = random.Random(seed)
    hits = 0
    for _ in range(n):
        total = 0.0
        for b in valid:
            ys = b[ys_key][:]
            rnd.shuffle(ys)
            t = kendall(b["idx"], ys)
            if t is not None:
                total += t
        hits += abs(total) >= abs(obs)
    return hits / n


def _read_csv(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _truth(v):
    return str(v).lower() in ("true", "1", "yes")


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _mean(vals):
    vals = [v for v in vals if v is not None]
    return statistics.mean(vals) if vals else None


def _utc(ns):
    try:
        return datetime.fromtimestamp(int(ns) / 1e9, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError, OSError):
        return None


def _fmt(v, nd=3):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:+.{nd}f}"
    return str(v)


def _md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(_fmt(v) for v in row) + " |")
    return "\n".join(out)


def _per_burst(landed_rows):
    rows = [r for r in landed_rows if _truth(r.get("landed")) and r.get("block_index") not in ("", "None", None)]
    groups = defaultdict(list)
    for r in rows:
        groups[(r.get("run", ""), r.get("burst", ""), r.get("slot", ""))].append(r)
    res, bursts = [], []
    rnd = random.Random(0)
    for (_run, _burst, _slot), g in groups.items():
        if len(g) < 3:
            continue
        idx = [int(r["block_index"]) for r in g]
        fee = [-int(r["cu_price"]) for r in g]  # negative: higher fee earlier -> positive tau
        seq = [int(r["send_seq"]) for r in g]
        tf, ts = kendall(idx, fee), kendall(idx, seq)
        res.append({"run": g[0].get("run", ""), "burst": g[0].get("burst", ""), "slot": g[0].get("slot", ""),
                    "target": g[0].get("target", ""), "label": g[0].get("label", ""),
                    "order_mode": g[0].get("order_mode", ""), "payer_arm": g[0].get("payer_arm", ""),
                    "n_same_block": len(g), "in_target_window": g[0].get("in_target_window", ""),
                    "tau_fee": tf, "p_fee": perm_p(idx, fee, tf, rnd=rnd),
                    "tau_send": ts, "p_send": perm_p(idx, seq, ts, rnd=rnd)})
        bursts.append({"label": g[0].get("label", ""), "idx": idx, "fee": fee, "seq": seq, "tf": tf, "ts": ts})
    return res, bursts


def _pooled(bursts):
    by = defaultdict(list)
    for b in bursts:
        by[b["label"]].append(b)
    out = []
    for label, g in sorted(by.items()):
        out.append({"label": label, "bursts": len(g),
                    "mean_tau_fee": _mean([b["tf"] for b in g]),
                    "mean_tau_send": _mean([b["ts"] for b in g]),
                    "p_fee": pooled_perm_p(g, "tf"), "p_send": pooled_perm_p(g, "ts")})
    return out


def _landing(sent_rows, landed_sigs):
    by_label = defaultdict(lambda: [0] * 7)
    by_fee = defaultdict(lambda: [0] * 7)
    # values: sent, live_sent, landed, on_time, in_window, send_offset_sum, send_offset_n
    for r in sent_rows:
        label = r.get("label") or "(unknown)"
        fee = _int(r.get("cu_price"))
        live = _truth(r.get("live"))
        on_time = _truth(r.get("on_time"))
        in_window = _truth(r.get("in_window_at_send"))
        landed = live and r.get("signature") in landed_sigs
        offset = _int(r.get("send_offset"))
        if offset is None:
            at, ws = _int(r.get("slot_at_send")), _int(r.get("window_start"))
            offset = at - ws if at is not None and ws is not None else None
        for bucket, key in ((by_label, label), (by_fee, fee)):
            if key is None:
                continue
            v = bucket[key]
            v[0] += 1
            v[1] += int(live)
            v[2] += int(landed)
            v[3] += int(on_time)
            v[4] += int(in_window)
            if offset is not None:
                v[5] += offset
                v[6] += 1
    labels = []
    for label, v in sorted(by_label.items()):
        labels.append({"label": label, "sent": v[0], "live_sent": v[1], "landed": v[2],
                       "landing_rate": v[2] / v[1] if v[1] else None,
                       "on_time": v[3], "on_time_rate": v[3] / v[0] if v[0] else None,
                       "in_window": v[4], "in_window_rate": v[4] / v[0] if v[0] else None,
                       "mean_send_offset": v[5] / v[6] if v[6] else None})
    fees = []
    for fee, v in sorted(by_fee.items()):
        fees.append({"cu_price": fee, "sent": v[0], "live_sent": v[1], "landed": v[2],
                     "landing_rate": v[2] / v[1] if v[1] else None,
                     "on_time": v[3], "on_time_rate": v[3] / v[0] if v[0] else None})
    return labels, fees


def _window_summary(rows):
    by_label = defaultdict(list)
    for r in rows:
        by_label[r.get("label") or "(unknown)"].append(r)
    out = []
    for label, g in sorted(by_label.items()):
        out.append({
            "label": label,
            "windows": len(g),
            "leaders_ok": sum(1 for r in g if _truth(r.get("leaders_ok"))),
            "windows_with_blocks": sum(1 for r in g if (_int(r.get("block_count")) or 0) > 0),
            "block_slots": sum(_int(r.get("block_count")) or 0 for r in g),
        })
    return out


def _whole_block(block_rows, landed_rows):
    slot_labels = defaultdict(set)
    for r in landed_rows:
        if _truth(r.get("landed")):
            slot = _int(r.get("slot"))
            if slot is not None:
                slot_labels[slot].add(r.get("label") or "(unknown)")
    slot_label = {s: "+".join(sorted(v)) for s, v in slot_labels.items()}

    by_slot = defaultdict(list)
    for r in block_rows:
        if _truth(r.get("is_vote")):
            continue
        slot = _int(r.get("slot"))
        idx, fee, cu, nsig = _int(r.get("index")), _int(r.get("fee")), _int(r.get("cu_consumed")), _int(r.get("num_sigs"))
        if None in (slot, idx, fee, cu, nsig) or cu <= 0:
            continue
        # APPROXIMATION: base fee = 5000 per signature; ignores exact compute/other fee components.
        prio_per_cu = (fee - 5000 * nsig) * 1_000_000 / cu
        by_slot[slot].append((idx, prio_per_cu))

    per_slot = []
    for slot, vals in sorted(by_slot.items()):
        if len(vals) < 3:
            continue
        vals.sort()
        idx = [v[0] for v in vals]
        prio = [v[1] for v in vals]
        # sign-flipped so positive tau = higher priority fee appears earlier (H1 direction)
        tau = kendall(idx, [-p for p in prio])
        per_slot.append({"slot": slot, "label": slot_label.get(slot, "(unmapped)"),
                         "n_non_vote": len(vals), "tau_priority_approx": tau})

    by_label = defaultdict(list)
    for r in per_slot:
        by_label[r["label"]].append(r)
    summary = [{"label": label, "slots": len(g),
                "mean_tau_priority_approx": _mean([r["tau_priority_approx"] for r in g]),
                "non_vote_txs": sum(r["n_non_vote"] for r in g)}
               for label, g in sorted(by_label.items())]
    return per_slot, summary


def analyze(landed_csv, out_csv, sent_csv=None, blocks_csv=None, md_path=None, windows_csv=None):
    data_dir = os.path.dirname(os.path.abspath(landed_csv)) or "."
    if windows_csv is None:
        candidate = os.path.join(data_dir, "windows.csv")
        windows_csv = candidate if os.path.exists(candidate) else None
    landed_rows = _read_csv(landed_csv)
    sent_rows = _read_csv(sent_csv)
    block_rows = _read_csv(blocks_csv)
    window_rows = _read_csv(windows_csv)
    res, bursts = _per_burst(landed_rows)
    with open(out_csv, "w", newline="") as f:
        fields = ["run", "burst", "slot", "target", "label", "order_mode", "payer_arm", "n_same_block",
                  "in_target_window", "tau_fee", "p_fee", "tau_send", "p_send"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(res)

    landed_sigs = {r.get("signature") for r in landed_rows if _truth(r.get("landed"))}
    landing_labels, landing_fees = _landing(sent_rows, landed_sigs)
    window_labels = _window_summary(window_rows)
    pooled = _pooled(bursts)
    per_slot, block_summary = _whole_block(block_rows, landed_rows)

    send_times = [t for t in (_utc(r.get("send_ts_ns")) for r in sent_rows) if t]
    plan_created = None
    plan_path = os.path.join(data_dir, "plan.json")
    if os.path.exists(plan_path):
        try:
            import json
            plan_created = json.load(open(plan_path)).get("created_at")
        except (OSError, ValueError):
            pass

    md = [
        "# obp results",
        "",
        f"- Analysis generated (UTC): {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        f"- Measurement send window (UTC): {send_times[0] if send_times else 'n/a'}"
        f" to {send_times[-1] if send_times else 'n/a'}",
        f"- Plan created (UTC): {plan_created or 'n/a'}",
        f"- Rows: sent={len(sent_rows)}, landed={len(landed_rows)}, block_txs={len(block_rows)}",
        "",
        "Positive tau means higher fee (or earlier send order) appears earlier in the block.",
        "Permutation p-values use a two-sided null; small samples give weak evidence.",
        "",
        "## Per-burst Kendall tau",
        "",
        _md_table(["label", "target", "arm", "slot", "n", "tau_fee", "p_fee", "tau_send", "p_send"],
                  [[r["label"], r["target"][:8], r["payer_arm"], r["slot"], r["n_same_block"],
                    r["tau_fee"], r["p_fee"], r["tau_send"], r["p_send"]] for r in res]) if res else "_No same-block groups with >=3 of our txs._",
        "",
        "## Pooled per client label",
        "",
        _md_table(["label", "bursts", "mean tau_fee", "mean tau_send", "pooled p_fee", "pooled p_send"],
                  [[r["label"], r["bursts"], r["mean_tau_fee"], r["mean_tau_send"], r["p_fee"], r["p_send"]]
                   for r in pooled]) if pooled else "_No pooled data._",
        "",
        "## Landing and timing",
        "",
        "`on_time` means `slot_at_send < window_start`; `in_window_at_send` means "
        "`slot_at_send < window_start + 4`. Both rates include dry-run rows.",
        "",
        _md_table(["label", "sent", "live_sent", "landed", "landing rate", "on_time", "on_time rate",
                   "in_window_at_send", "in_window rate", "mean send_offset"],
                  [[r["label"], r["sent"], r["live_sent"], r["landed"], r["landing_rate"], r["on_time"],
                    r["on_time_rate"], r["in_window"], r["in_window_rate"], r["mean_send_offset"]]
                   for r in landing_labels]) if landing_labels else "_No sent rows._",
        "",
        "### Landing by fee level",
        "",
        _md_table(["cu_price (micro/CU)", "sent", "live_sent", "landed", "landing rate", "on_time", "on_time rate"],
                  [[r["cu_price"], r["sent"], r["live_sent"], r["landed"], r["landing_rate"], r["on_time"],
                    r["on_time_rate"]] for r in landing_fees]) if landing_fees else "_No fee data._",
        "",
        "## Verified leader windows",
        "",
        "`leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that "
        "actually produced a block. Works on dry-run data because it needs no signatures.",
        "",
        _md_table(["label", "windows", "leaders_ok", "windows with blocks", "block_slots"],
                  [[r["label"], r["windows"], r["leaders_ok"], r["windows_with_blocks"], r["block_slots"]]
                   for r in window_labels]) if window_labels else "_No windows.csv data._",
        "",
        "## Whole-block priority ordering (APPROXIMATION)",
        "",
        "Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.",
        "The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.",
        "Positive tau = higher approximate priority fee appears earlier in the block.",
        "",
        _md_table(["label", "slots", "mean tau_priority (approx)", "non-vote txs"],
                  [[r["label"], r["slots"], r["mean_tau_priority_approx"], r["non_vote_txs"]]
                   for r in block_summary]) if block_summary else "_No labelled blocks with >=3 non-vote txs._",
        "",
        "### Per-slot whole-block check",
        "",
        _md_table(["slot", "label", "non-vote txs", "tau_priority (approx)"],
                  [[r["slot"], r["label"], r["n_non_vote"], r["tau_priority_approx"]] for r in per_slot])
        if per_slot else "_No per-slot data._",
        "",
    ]
    md_text = "\n".join(md)
    if md_path:
        with open(md_path, "w") as f:
            f.write(md_text)
    return md_text
