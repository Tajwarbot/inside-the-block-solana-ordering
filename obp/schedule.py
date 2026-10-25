"""Leader schedule -> upcoming 4-slot leader windows for chosen validators. Read-only."""
import json, os, random
from collections import defaultdict
from .rpc import Rpc

WINDOW = 4  # consecutive slots per leader rotation (check this is still 4 on the current cluster)


def upcoming_windows(rpc: Rpc, cache_path: str | None = None, horizon_slots: int = 20_000,
                     min_lead_slots: int = 0):
    """Return {identity: [window_start_slot, ...]} for windows starting within horizon_slots.

    Only windows at least `min_lead_slots` after the current slot are returned, so a plan cannot
    pick a window that is already past by the time `run` starts."""
    ei = rpc.epoch_info()
    epoch_start = ei["absoluteSlot"] - ei["slotIndex"]
    now = ei["absoluteSlot"]
    sched = None
    if cache_path and os.path.exists(cache_path):
        with open(cache_path) as f:
            c = json.load(f)
        if c.get("epoch") == ei["epoch"]:
            sched = c["schedule"]
    if sched is None:
        sched = rpc.leader_schedule()  # whole epoch, all leaders (~several MB)
        if cache_path:
            with open(cache_path, "w") as f:
                json.dump({"epoch": ei["epoch"], "schedule": sched}, f)
    earliest = now + min_lead_slots
    out = defaultdict(list)
    for ident, idxs in sched.items():
        for i in idxs:
            s = epoch_start + i
            if now < s <= now + horizon_slots and s >= earliest and (i % WINDOW == 0):
                out[ident].append(s)
    return {k: sorted(v) for k, v in out.items()}, now


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
