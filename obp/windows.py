"""Post-hoc, read-only check of planned/sent leader windows.
Uses getSlotLeaders(window_start, 4) and getBlocks(window_start, window_start+3). It works on
dry-run sent.csv too (dry rows have live=False), so leader windows can be confirmed for free.
"""
import csv, json, logging, os, time
from .rpc import Rpc
from .schedule import WINDOW

log = logging.getLogger("obp.windows")
WINDOW_FIELDS = ["window_start", "window_end", "target", "label", "leaders", "leaders_ok",
                 "block_slots", "block_count", "expected", "sources", "status", "err", "checked_at"]


def _load_windows(plan_json: str, sent_csv: str):
    wins = {}
    if plan_json and os.path.exists(plan_json):
        try:
            for item in json.load(open(plan_json)).get("plan", []):
                key = (int(item["window_start"]), item["target"])
                d = wins.setdefault(key, {"window_start": key[0], "target": key[1],
                                          "label": item.get("label", ""), "sources": set()})
                d["sources"].add("plan")
                if item.get("label"):
                    d["label"] = item["label"]
        except (OSError, ValueError, KeyError) as e:
            log.warning("could not read %s: %s", plan_json, e)
    if sent_csv and os.path.exists(sent_csv):
        with open(sent_csv, newline="") as f:
            for r in csv.DictReader(f):
                try:
                    ws = int(r["window_start"])
                except (KeyError, TypeError, ValueError):
                    continue
                target = r.get("target", "")
                if not target:
                    continue
                key = (ws, target)
                d = wins.setdefault(key, {"window_start": ws, "target": target,
                                          "label": r.get("label", ""), "sources": set()})
                d["sources"].add("sent")
                if r.get("label") and not d.get("label"):
                    d["label"] = r["label"]
    return wins


def verify_windows(rpc: Rpc, plan_json: str, sent_csv: str, out_csv: str):
    wins = _load_windows(plan_json, sent_csv)
    rows = []
    checked_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        finalized = rpc.slot("finalized")
    except Exception as e:  # noqa: BLE001
        finalized = None
        log.warning("could not read finalized slot (%s); elapsed status will not be split", e)
    for (ws, target), d in sorted(wins.items()):
        window_end = ws + WINDOW - 1
        if finalized is not None and window_end >= finalized:
            rows.append({
                "window_start": ws, "window_end": window_end, "target": target, "label": d.get("label", ""),
                "leaders": "", "leaders_ok": False, "block_slots": "", "block_count": 0,
                "expected": WINDOW, "sources": "+".join(sorted(d.get("sources", []))),
                "status": "planned", "err": "", "checked_at": checked_at,
            })
            continue
        err = ""
        try:
            leaders = rpc.slot_leaders(ws, WINDOW)
        except Exception as e:  # noqa: BLE001
            leaders, err = [], f"slotLeaders:{e}"[:200]
        if isinstance(leaders, dict) and "__error__" in leaders:
            err = str(leaders["__error__"])[:200]
            leaders = []
        try:
            block_slots = rpc.blocks(ws, ws + WINDOW - 1)
        except Exception as e:  # noqa: BLE001
            block_slots, err = [], (err + f" getBlocks:{e}").strip()[:200]
        if isinstance(block_slots, dict) and "__error__" in block_slots:
            err = (err + " " + str(block_slots["__error__"])).strip()[:200]
            block_slots = []
        leaders_ok = len(leaders) == WINDOW and all(x == target for x in leaders)
        rows.append({
            "window_start": ws, "window_end": window_end, "target": target, "label": d.get("label", ""),
            "leaders": ";".join(leaders), "leaders_ok": leaders_ok,
            "block_slots": ";".join(str(x) for x in block_slots), "block_count": len(block_slots),
            "expected": WINDOW, "sources": "+".join(sorted(d.get("sources", []))),
            "status": "verified", "err": err, "checked_at": checked_at,
        })
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=WINDOW_FIELDS)
        w.writeheader(); w.writerows(rows)
    verified = [r for r in rows if r["status"] == "verified"]
    planned = len(rows) - len(verified)
    ok = sum(1 for r in verified if r["leaders_ok"])
    log.info("checked %d windows: %d verified (%d target led all %d slots), %d planned/not yet elapsed",
             len(rows), len(verified), ok, WINDOW, planned)
    return rows
