"""Build figures/*.png from committed CSVs. Offline, deterministic (fixed seed)."""
import csv, os, random, sys
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "data", "runs")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "figures")
SLOT_MS = 212.0
SESSIONS = [("main seq 10-25", "20261025_1828_main"), ("parallel 10-25", "20261025_1907_parallel"),
            ("parallel 10-31 lead2", "20261031_par2_parallel"), ("parallel 10-31 lead2 (3)", "20261031_par3_parallel"),
            ("parallel 10-31 lead6", "20261031_par4_parallel_lead6")]
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 110, "svg.hashsalt": "obp", "path.simplify": False})


def rows(run, name):
    with open(os.path.join(RUNS, run, name), newline="") as f:
        return list(csv.DictReader(f))


def boot_ci(vals, n=2000, seed=0):
    rnd = random.Random(seed)
    means = sorted(sum(rnd.choice(vals) for _ in vals) / len(vals) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def primary(run):
    """Per-label lists of per-burst tau on the primary set: same payer, asc+shuffle, target window."""
    out = defaultdict(lambda: {"fee": [], "send": []})
    for r in rows(run, "results.csv"):
        if r["payer_arm"] == "same" and r["order_mode"] in ("asc", "shuffle") and r["in_target_window"] == "True":
            out[r["label"]]["fee"].append(float(r["tau_fee"]))
            out[r["label"]]["send"].append(float(r["tau_send"]))
    return out


def fig_tau():
    seq, par = primary("20261025_1828_main"), primary("pooled_parallel_all")
    labels = sorted(l for l in set(seq) | set(par) if not l.startswith("Unknown"))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, key, title in ((axes[0], "fee", "tau_fee (higher fee earlier = +)"),
                           (axes[1], "send", "tau_send (earlier send earlier = +)")):
        for off, (data, name, color) in enumerate(((seq, "sequential, main", "tab:blue"),
                                                   (par, "parallel, 4 sessions pooled", "tab:orange"))):
            xs, ys, lo, hi = [], [], [], []
            for i, l in enumerate(labels):
                v = data.get(l, {}).get(key, [])
                if not v:
                    continue
                m = sum(v) / len(v)
                a, b = boot_ci(v) if len(v) > 1 else (m, m)
                xs.append(i + (off - 0.5) * 0.3); ys.append(m); lo.append(m - a); hi.append(b - m)
            ax.errorbar(xs, ys, yerr=[lo, hi], fmt="o", color=color, capsize=3, label=name)
        ax.axhline(0, color="grey", lw=0.8)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels([f"{l}\nn={len(seq.get(l,{}).get(key,[]))}/{len(par.get(l,{}).get(key,[]))}" for l in labels],
                           rotation=60, fontsize=7)
        ax.set_title(title, fontsize=9); ax.set_ylim(-1.1, 1.1)
    axes[0].set_ylabel("mean per-burst Kendall tau, 95% bootstrap CI")
    axes[0].legend(fontsize=7, loc="lower left")
    fig.suptitle("Primary set: same payer, asc+shuffle, target window. n = bursts seq/parallel", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "tau_by_label.png"), metadata={"Software": None}); plt.close(fig)


def fig_offsets():
    fig, ax = plt.subplots(figsize=(8, 4))
    bins = list(range(-4, 16))
    for name, run in SESSIONS:
        off = [int(r["slot"]) - int(r["window_start"]) for r in rows(run, "landed.csv") if r["slot"] not in ("", "None")]
        off = [min(max(o, -4), 15) for o in off]
        ax.hist(off, bins=bins, histtype="step", lw=1.5, label=f"{name} (n={len(off)})", density=True)
    ax.axvspan(0, 4, color="green", alpha=0.08, label="target window (slots 0..3)")
    ax.set_xlabel("landing slot minus window start (clipped to -4..15)"); ax.set_ylabel("share of landed txs")
    ax.legend(fontsize=7); fig.tight_layout()
    fig.savefig(os.path.join(OUT, "landing_offset.png"), metadata={"Software": None}); plt.close(fig)


def fig_span():
    fig, ax = plt.subplots(figsize=(8, 4))
    data = []
    for name, run in SESSIONS:
        b = defaultdict(list)
        for r in rows(run, "sent.csv"):
            if r.get("live") == "True" and r.get("send_done_ns"):
                b[r["burst"]].append((int(r["send_ts_ns"]), int(r["send_done_ns"])))
        data.append(([(max(e for _, e in v) - min(s for s, _ in v)) / 1e6 for v in b.values()], name))
    ax.boxplot([d for d, _ in data], showfliers=False)
    ax.set_xticks(range(1, len(data) + 1)); ax.set_xticklabels([n for _, n in data], fontsize=7, rotation=15)
    for k in (1, 2, 4):
        ax.axhline(k * SLOT_MS, color="grey", ls="--", lw=0.8)
        ax.text(0.55, k * SLOT_MS + 15, f"{k} slot{'s' if k > 1 else ''} ({k*SLOT_MS:.0f} ms)", fontsize=7)
    ax.set_ylabel("burst span: first send start to last send done (ms)")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "burst_span.png"), metadata={"Software": None}); plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig_tau(); fig_offsets(); fig_span()
    print("figures written to", OUT)
