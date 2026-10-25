"""Leader schedule -> upcoming 4-slot leader windows for chosen validators. Read-only."""
import json, os, random
from collections import defaultdict, deque
from .rpc import Rpc

WINDOW = 4  # consecutive slots per leader rotation (check this is still 4 on the current cluster)


def upcoming_windows(rpc: Rpc, cache_path: str | None = None, horizon_slots: int = 20_000,
                     min_lead_slots: int = 0, cluster: str | None = None):
    """Return {identity: [window_start_slot, ...]} for windows starting within horizon_slots.

    Only windows at least `min_lead_slots` after the current slot are returned, so a plan cannot
    pick a window that is already past by the time `run` starts. The schedule cache is keyed by
    (cluster, epoch): the same epoch number on another cluster must not be reused."""
    ei = rpc.epoch_info()
    epoch_start = ei["absoluteSlot"] - ei["slotIndex"]
    now = ei["absoluteSlot"]
    if cluster is None:
        cluster = rpc.cluster() if hasattr(rpc, "cluster") else "unknown"
    sched = None
    if cache_path and os.path.exists(cache_path):
        with open(cache_path) as f:
            c = json.load(f)
        if c.get("epoch") == ei["epoch"] and c.get("cluster") == cluster:
            sched = c["schedule"]
    if sched is None:
        sched = rpc.leader_schedule()  # whole epoch, all leaders (~several MB)
        if cache_path:
            with open(cache_path, "w") as f:
                json.dump({"cluster": cluster, "epoch": ei["epoch"], "schedule": sched}, f)
    earliest = now + min_lead_slots
    out = defaultdict(list)
    for ident, idxs in sched.items():
        for i in idxs:
            s = epoch_start + i
            if now < s <= now + horizon_slots and s >= earliest and (i % WINDOW == 0):
                out[ident].append(s)
    return {k: sorted(v) for k, v in out.items()}, now


def min_gap_filter(candidates: list[dict], min_gap_slots: int = 12) -> list[dict]:
    """Apply the global gap rule with per-target round-robin, so one busy target cannot starve
    every other target/label. Within a target windows are considered earliest first."""
    queues = defaultdict(deque)
    for item in sorted(candidates, key=lambda x: (int(x["window_start"]), x.get("target", ""))):
        queues[item["target"]].append(item)
    targets = sorted(queues, key=lambda t: int(queues[t][0]["window_start"]))
    kept, last = [], None
    while any(queues[t] for t in targets):
        progressed = False
        for target in targets:
            q = queues[target]
            while q:
                item = q[0]
                ws = int(item["window_start"])
                if last is None or ws - last >= int(min_gap_slots):
                    kept.append(item)
                    q.popleft()
                    last = ws
                    progressed = True
                    break
                # `last` only moves forward, so this window can never become eligible later.
                q.popleft()
        if not progressed:
            break
    return sorted(kept, key=lambda x: int(x["window_start"]))


def validate_plan(plan: list[dict], min_validators: int = 6, min_labels: int = 3) -> dict:
    """Assert the post-gap plan still covers enough distinct validators and labels."""
    targets = {p["target"] for p in plan}
    labels = {p.get("label", "") for p in plan if p.get("label")}
    if len(targets) < min_validators:
        raise SystemExit(f"plan has only {len(targets)} distinct targets after gap filtering; "
                         f"need >= {min_validators} (widen --horizon/--windows or lower --min-gap-slots)")
    if len(labels) < min_labels:
        raise SystemExit(f"plan has only {len(labels)} distinct labels after gap filtering; "
                         f"need >= {min_labels}")
    return {"targets": targets, "labels": labels}


def pick_targets(inventory: list[dict], windows: dict, per_label: int = 2, min_labels: int = 3,
                 min_windows: int = 3, seed: int = 7):
    """Choose validators so that every client label is represented by `per_label` validators that
    have at least `min_windows` upcoming windows. Ranks by stake (more windows, more representative)."""
    rnd = random.Random(seed)
    by_label = defaultdict(list)
    for r in inventory:
        if len(windows.get(r["identity"], [])) >= min_windows:
            by_label[r["label"]].append(r)
    chosen = []
    for label, rows in by_label.items():
        rows.sort(key=lambda r: -r["stake_sol"])
        top = rows[: max(per_label * 3, per_label)]
        rnd.shuffle(top)  # avoid always the single biggest operator
        chosen += top[:per_label]
    labels = {r["label"] for r in chosen}
    if len(labels) < min_labels:
        raise SystemExit(f"only {len(labels)} client labels have enough windows; widen horizon")
    return chosen
