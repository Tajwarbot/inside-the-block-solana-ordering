"""Analyze ordering data.

Primary tests use only bursts where the landing slot was inside the planned window AND the actual
leader was the planned target. A separate sensitivity table shows all landed rows regardless of
leader/target. Only pairs of OUR transactions that landed in the SAME block are compared.

The pre-registered primary test is pooled tau_fee per client label on the same-payer arm, using
only descending and shuffled bursts. Ascending bursts are excluded from the primary test because
there fee order equals send order (confounded); they are a consistency check only. Holm correction
is applied to those per-label p-values. Everything else (multi-payer arm, per-burst, per-mode,
whole-block) is exploratory.

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
        return f"{v:.{nd}f}"
    return str(v)


def _tau(v, nd=3):
    if v is None:
        return "-"
    return f"{v:+.{nd}f}"


def _md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(_fmt(v) for v in row) + " |")
    return "\n".join(out)


def _send_rank(r):
    v = r.get("send_rank")
    if v not in (None, "", "None"):
        return int(v)
    return int(r["send_seq"])


def _per_burst(landed_rows, require_target=True):
    rows = [r for r in landed_rows if _truth(r.get("landed")) and r.get("block_index") not in ("", "None", None)]
    if require_target:
        rows = [r for r in rows if _truth(r.get("in_target_window")) and _truth(r.get("leader_is_target"))]
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
        seq = [_send_rank(r) for r in g]
        tf, ts = kendall(idx, fee), kendall(idx, seq)
        res.append({"run": g[0].get("run", ""), "burst": g[0].get("burst", ""), "slot": g[0].get("slot", ""),
                    "target": g[0].get("target", ""), "label": g[0].get("label", ""),
                    "order_mode": g[0].get("order_mode", ""), "payer_arm": g[0].get("payer_arm", ""),
                    "n_same_block": len(g), "in_target_window": g[0].get("in_target_window", ""),
                    "tau_fee": tf, "p_fee": perm_p(idx, fee, tf, rnd=rnd),
                    "tau_send": ts, "p_send": perm_p(idx, seq, ts, rnd=rnd)})
        bursts.append({"label": g[0].get("label", ""), "payer_arm": g[0].get("payer_arm", ""),
                       "order_mode": g[0].get("order_mode", ""), "n": len(g),
                       "idx": idx, "fee": fee, "seq": seq, "tf": tf, "ts": ts})
    return res, bursts


def _summarize(bursts):
    return {"bursts": len(bursts), "txs": sum(b.get("n", 0) for b in bursts),
            "mean_tau_fee": _mean([b["tf"] for b in bursts]),
            "mean_tau_send": _mean([b["ts"] for b in bursts]),
            "p_fee": pooled_perm_p(bursts, "tf"), "p_send": pooled_perm_p(bursts, "ts")}


def _pooled(bursts):
    by = defaultdict(list)
    for b in bursts:
        by[b["label"]].append(b)
    return [{"label": label, **_summarize(g)} for label, g in sorted(by.items())]


def _group_stats(bursts, key):
    by = defaultdict(list)
    for b in bursts:
        by[b.get(key, "")].append(b)
    return [{"group": group, **_summarize(g)} for group, g in sorted(by.items(), key=lambda kv: str(kv[0]))]


def _grouped(bursts):
    out = []
    for label in sorted({b["label"] for b in bursts}):
        lb = [b for b in bursts if b["label"] == label]
        for scope in ("payer_arm", "order_mode"):
            for r in _group_stats(lb, scope):
                out.append({"label": label, "group_by": scope, **r})
    return out


def _holm(pvalues: dict) -> dict:
    items = sorted(((k, p) for k, p in pvalues.items() if p is not None), key=lambda kv: kv[1])
    m, prev, out = len(items), 0.0, {}
    for i, (label, p) in enumerate(items):
        adj = min(1.0, max(prev, p * (m - i)))
        out[label] = adj
        prev = adj
    return out


def _pos_sig(g, value_key, p_key):
    return bool(g) and g[value_key] is not None and g[value_key] > 0 and \
        g[p_key] is not None and g[p_key] < 0.05


def _verdicts(bursts):
    # Primary test: same-payer arm only. Ascending bursts are confounded (fee order == send order),
    # so the verdict uses descending + shuffled bursts; asc is shown as a consistency check.
    labels = sorted({b["label"] for b in bursts})
    same = [b for b in bursts if b["payer_arm"] == "same"]
    primary = {label: _summarize([b for b in same
                                  if b["label"] == label and b["order_mode"] in ("desc", "shuffle")])
               for label in labels}
    holm = _holm({label: primary[label]["p_fee"] for label in labels})
    out = []
    for label in labels:
        desc_bursts = [b for b in same if b["label"] == label and b["order_mode"] == "desc"]
        asc_bursts = [b for b in same if b["label"] == label and b["order_mode"] == "asc"]
        desc = _summarize(desc_bursts) if desc_bursts else None
        asc = _summarize(asc_bursts) if asc_bursts else None
        p = primary[label]
        h1 = (p["mean_tau_fee"] is not None and p["mean_tau_fee"] > 0
              and holm.get(label) is not None and holm[label] < 0.05
              and desc is not None and desc["mean_tau_fee"] is not None and desc["mean_tau_fee"] > 0)
        h2 = (p["mean_tau_send"] is not None and p["mean_tau_send"] > 0
              and p["p_send"] is not None and p["p_send"] < 0.05
              and desc is not None and desc["mean_tau_send"] is not None and desc["mean_tau_send"] > 0)
        if h1 and h2:
            verdict = "mixed (both H1 and H2 markers)"
        elif h1:
            verdict = "H1 fee rule"
        elif h2:
            verdict = "H2 arrival rule"
        else:
            verdict = "no rule detected (H0 not rejected)"
        evidence = []
        for name, g in (("desc", desc), ("desc+shuffle (primary)", p), ("asc (consistency only)", asc)):
            if g:
                evidence.append(f"{name}: tau_fee={_tau(g['mean_tau_fee'])} p={_fmt(g['p_fee'])} "
                                f"tau_send={_tau(g['mean_tau_send'])} p={_fmt(g['p_send'])}")
        out.append({"label": label, "bursts": p["bursts"], "txs": p["txs"],
                    "tau_fee": p["mean_tau_fee"], "p_fee": p["p_fee"], "p_holm": holm.get(label),
                    "tau_send": p["mean_tau_send"], "p_send": p["p_send"],
                    "verdict": verdict, "evidence": "; ".join(evidence)})
    return out


def _landing_distribution(sent_rows, landed_rows):
    """For each live burst, count how many of its txs landed in the target window."""
    landed = {r.get("signature"): r for r in landed_rows if _truth(r.get("landed"))}
    by_burst = defaultdict(int)
    labels = {}
    for r in sent_rows:
        if not _truth(r.get("live")):
            continue
        key = (r.get("run", ""), r.get("burst", ""))
        labels[key] = r.get("label") or "(unknown)"
        lr = landed.get(r.get("signature"))
        if lr and _truth(lr.get("in_target_window")) and _truth(lr.get("leader_is_target")):
            by_burst[key] += 1
    by_label = defaultdict(list)
    for key, label in labels.items():
        by_label[label].append(by_burst.get(key, 0))
    out = []
    for label, counts in sorted(by_label.items()):
        dist = [sum(1 for c in counts if c == n) for n in range(6)]
        out.append({"label": label, "bursts": len(counts), "mean": _mean(counts), "dist": dist})
    return out


def _landing(sent_rows, landed_sigs):
    # values: total, live, landed, live_on_time, live_in_window, offset_sum, offset_n,
    #         dry, dry_on_time, dry_in_window
    by_label = defaultdict(lambda: [0] * 10)
    by_fee = defaultdict(lambda: [0] * 10)
    for r in sent_rows:
        label = r.get("label") or "(unknown)"
        fee = _int(r.get("cu_price"))
        live = _truth(r.get("live"))
        on_time = _truth(r.get("on_time"))
        in_window = _truth(r.get("in_window_at_send"))
        landed = live and r.get("signature") in landed_sigs
        offset = _int(r.get("send_offset"))
        if offset is None:
            at = _int(r.get("est_slot_at_send"))
            if at is None:
                at = _int(r.get("slot_at_send"))
            ws = _int(r.get("window_start"))
            offset = at - ws if at is not None and ws is not None else None
        for bucket, key in ((by_label, label), (by_fee, fee)):
            if key is None:
                continue
            v = bucket[key]
            v[0] += 1
            if live:
                v[1] += 1
                v[2] += int(landed)
                v[3] += int(on_time)
                v[4] += int(in_window)
                if offset is not None:
                    v[5] += offset
                    v[6] += 1
            else:
                v[7] += 1
                v[8] += int(on_time)
                v[9] += int(in_window)
    labels = []
    for label, v in sorted(by_label.items()):
        labels.append({"label": label, "sent": v[0], "live_sent": v[1], "landed": v[2],
                       "landing_rate": v[2] / v[1] if v[1] else None,
                       "live_on_time": v[3], "on_time_rate": v[3] / v[1] if v[1] else None,
                       "live_in_window": v[4], "in_window_rate": v[4] / v[1] if v[1] else None,
                       "mean_send_offset": v[5] / v[6] if v[6] else None,
                       "dry_sent": v[7], "dry_on_time": v[8],
                       "dry_on_time_rate": v[8] / v[7] if v[7] else None,
                       "dry_in_window": v[9], "dry_in_window_rate": v[9] / v[7] if v[7] else None})
    fees = []
    for fee, v in sorted(by_fee.items()):
        fees.append({"cu_price": fee, "sent": v[0], "live_sent": v[1], "landed": v[2],
                     "landing_rate": v[2] / v[1] if v[1] else None,
                     "live_on_time": v[3], "on_time_rate": v[3] / v[1] if v[1] else None})
    return labels, fees


def _window_summary(rows):
    by_label = defaultdict(list)
    for r in rows:
        by_label[r.get("label") or "(unknown)"].append(r)
    out = []
    for label, g in sorted(by_label.items()):
        verified = [r for r in g if r.get("status") in (None, "", "verified")]
        out.append({
            "label": label,
            "windows": len(verified),
            "leaders_ok": sum(1 for r in verified if _truth(r.get("leaders_ok"))),
            "windows_with_blocks": sum(1 for r in verified if (_int(r.get("block_count")) or 0) > 0),
            "block_slots": sum(_int(r.get("block_count")) or 0 for r in verified),
            "planned": len(g) - len(verified),
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
    res, bursts = _per_burst(landed_rows, require_target=True)
    _all_res, all_bursts = _per_burst(landed_rows, require_target=False)
    with open(out_csv, "w", newline="") as f:
        fields = ["run", "burst", "slot", "target", "label", "order_mode", "payer_arm", "n_same_block",
                  "in_target_window", "tau_fee", "p_fee", "tau_send", "p_send"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(res)

    grouped = _grouped(bursts)
    group_csv = os.path.join(os.path.dirname(os.path.abspath(out_csv)) or ".", "results_by_group.csv")
    with open(group_csv, "w", newline="") as f:
        fields = ["label", "group_by", "group", "bursts", "txs", "mean_tau_fee", "p_fee",
                  "mean_tau_send", "p_send"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(grouped)

    landed_sigs = {r.get("signature") for r in landed_rows if _truth(r.get("landed"))}
    landing_labels, landing_fees = _landing(sent_rows, landed_sigs)
    landing_dist = _landing_distribution(sent_rows, landed_rows)
    window_labels = _window_summary(window_rows)
    pooled = _pooled(bursts)
    sensitivity = _pooled(all_bursts)
    verdicts = _verdicts(bursts)
    per_slot, block_summary = _whole_block(block_rows, landed_rows)

    landed_true = sum(1 for r in landed_rows if _truth(r.get("landed")))
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
        f"- Rows: sent={len(sent_rows)}, landed={landed_true}, block_txs={len(block_rows)}",
        "",
        "Positive tau means higher fee (or earlier send order) appears earlier in the block.",
        "Permutation p-values use a two-sided null; small samples give weak evidence.",
        "",
        "## Test plan: primary vs exploratory",
        "",
        "**Pre-registered primary test:** pooled `tau_fee` per client label on the **same-payer** arm, "
        "using only **descending + shuffled** bursts and only rows with `in_target_window=True` and "
        "`leader_is_target=True`. Ascending bursts are excluded from the primary test because there "
        "fee order equals send order (confounded); asc is a consistency check only. Holm correction is "
        "applied across the per-label primary p-values below.",
        "",
        "Everything else (multi-payer arm, ascending mode, per-burst, whole-block, landing rates) is "
        "**exploratory**. Groups with fewer than 3 of our transactions in the same block are dropped. "
        "That selection can bias the ordering sample toward bursts whose higher-fee transactions land "
        "more often (see the target-window landing distribution below). With a five-transaction burst "
        "the smallest attainable two-sided per-burst permutation p is 1/60 ≈ 0.017; pooled tests use "
        "2000 permutations, so their floor is 0.0005.",
        "",
        "## Verdict per label (H1 / H2 / H0)",
        "",
        "All verdict inputs use the same-payer arm only. H1 = pooled tau_fee > 0 with Holm-adjusted "
        "p < 0.05 on descending+shuffled bursts AND tau_fee > 0 in descending bursts alone. "
        "H2 = pooled tau_send > 0 with p < 0.05 on descending+shuffled bursts AND tau_send > 0 in "
        "descending bursts alone. If both hold the verdict is **mixed**; if neither holds it is "
        "**no rule detected (H0 not rejected)**. Ascending bursts are a consistency check only.",
        "",
        _md_table(["label", "primary bursts (desc+shuffle, same arm)", "primary txs",
                   "tau_fee (same arm)", "p_fee", "Holm p", "verdict", "mode evidence"],
                  [[r["label"], r["bursts"], r["txs"], _tau(r["tau_fee"]), _fmt(r["p_fee"]),
                    _fmt(r["p_holm"]), r["verdict"], r["evidence"]] for r in verdicts])
        if verdicts else "_No same-block groups with >=3 target-window txs._",
        "",
        "## Per-burst Kendall tau (primary: target window and target leader)",
        "",
        _md_table(["label", "target", "arm", "slot", "n", "tau_fee", "p_fee", "tau_send", "p_send"],
                  [[r["label"], r["target"][:8], r["payer_arm"], r["slot"], r["n_same_block"],
                    _tau(r["tau_fee"]), r["p_fee"], _tau(r["tau_send"]), r["p_send"]] for r in res]) if res else "_No same-block groups with >=3 of our txs._",
        "",
        "## Pooled per client label (primary: target window and target leader)",
        "",
        _md_table(["label", "bursts", "txs", "mean tau_fee", "mean tau_send", "pooled p_fee", "pooled p_send"],
                  [[r["label"], r["bursts"], r["txs"], _tau(r["mean_tau_fee"]), _tau(r["mean_tau_send"]),
                    r["p_fee"], r["p_send"]] for r in pooled]) if pooled else "_No pooled data._",
        "",
        "## Grouped results by payer arm and order mode (exploratory)",
        "",
        _md_table(["label", "grouped by", "group", "bursts", "txs", "mean tau_fee", "pooled p_fee",
                   "mean tau_send", "pooled p_send"],
                  [[r["label"], r["group_by"], r["group"], r["bursts"], r["txs"], _tau(r["mean_tau_fee"]),
                    r["p_fee"], _tau(r["mean_tau_send"]), r["p_send"]] for r in grouped])
        if grouped else "_No grouped data._",
        "",
        "## Sensitivity: all landed (any leader)",
        "",
        "Same statistic as the primary pooled table, but using every landed row regardless of "
        "`in_target_window` or `leader_is_target`. This is exploratory and shows how much the result "
        "depends on the leader filter.",
        "",
        _md_table(["label", "bursts", "txs", "mean tau_fee", "mean tau_send", "pooled p_fee", "pooled p_send"],
                  [[r["label"], r["bursts"], r["txs"], _tau(r["mean_tau_fee"]), _tau(r["mean_tau_send"]),
                    r["p_fee"], r["p_send"]] for r in sensitivity]) if sensitivity else "_No landed data._",
        "",
        "## Landing and timing",
        "",
        "Live timing uses live-only denominators. Dry-run timing is shown in separate columns so it "
        "cannot inflate a live rate. `on_time` means the per-tx estimated send slot was before "
        "`window_start`; `in_window_at_send` means it was before `window_start + 4`.",
        "",
        _md_table(["label", "sent", "live sent", "landed", "landing rate", "live on_time", "on_time rate",
                   "live in_window", "in_window rate", "mean live send_offset", "dry sent", "dry on_time",
                   "dry on_time rate", "dry in_window", "dry in_window rate"],
                  [[r["label"], r["sent"], r["live_sent"], r["landed"], r["landing_rate"], r["live_on_time"],
                    r["on_time_rate"], r["live_in_window"], r["in_window_rate"], r["mean_send_offset"],
                    r["dry_sent"], r["dry_on_time"], r["dry_on_time_rate"], r["dry_in_window"],
                    r["dry_in_window_rate"]] for r in landing_labels]) if landing_labels else "_No sent rows._",
        "",
        "### Landing by fee level (live only)",
        "",
        _md_table(["cu_price (micro/CU)", "live sent", "landed", "landing rate", "live on_time", "on_time rate"],
                  [[r["cu_price"], r["live_sent"], r["landed"], r["landing_rate"], r["live_on_time"],
                    r["on_time_rate"]] for r in landing_fees]) if landing_fees else "_No fee data._",
        "",
        "### Selected sample: our txs in the target window per burst",
        "",
        "The primary test only uses groups with **at least 3** of our transactions co-landed in the "
        "target block. This table counts, for each live burst, how many of its transactions landed "
        "anywhere in the target window (not necessarily in the same block). Bursts with 0-2 are "
        "under-represented in the ordering tests. If higher-fee transactions also land more often, the "
        "primary sample is biased toward higher fees; that selection effect is a limitation, not a "
        "finding.",
        "",
        _md_table(["label", "live bursts", "0", "1", "2", "3", "4", "5", "mean landed in target window"],
                  [[r["label"], r["bursts"], *r["dist"], _fmt(r["mean"], 2)] for r in landing_dist])
        if landing_dist else "_No live bursts._",
        "",
        "## Verified leader windows",
        "",
        "Only windows whose `window_end` is before the current finalized slot count as verified. "
        "`leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that "
        "actually produced a block; `planned` = not yet elapsed, not counted as verified.",
        "",
        _md_table(["label", "windows", "leaders_ok", "windows with blocks", "block_slots", "planned"],
                  [[r["label"], r["windows"], r["leaders_ok"], r["windows_with_blocks"], r["block_slots"],
                    r["planned"]] for r in window_labels]) if window_labels else "_No windows.csv data._",
        "",
        "## Whole-block priority ordering (APPROXIMATION)",
        "",
        "Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.",
        "The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.",
        "Positive tau = higher approximate priority fee appears earlier in the block.",
        "",
        _md_table(["label", "slots", "mean tau_priority (approx)", "non-vote txs"],
                  [[r["label"], r["slots"], _tau(r["mean_tau_priority_approx"]), r["non_vote_txs"]]
                   for r in block_summary]) if block_summary else "_No labelled blocks with >=3 non-vote txs._",
        "",
        "### Per-slot whole-block check",
        "",
        _md_table(["slot", "label", "non-vote txs", "tau_priority (approx)"],
                  [[r["slot"], r["label"], r["n_non_vote"], _tau(r["tau_priority_approx"])] for r in per_slot])
        if per_slot else "_No per-slot data._",
        "",
    ]
    md_text = "\n".join(md)
    if md_path:
        with open(md_path, "w") as f:
            f.write(md_text)
    return md_text
