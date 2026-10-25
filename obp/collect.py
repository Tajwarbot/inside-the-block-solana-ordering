"""Find where our transactions landed: slot, leader, intra-block index. Read-only.
Also dumps every transaction of those blocks (index, fee, CUs) as supplementary data.
Re-running is idempotent: slots already in blocks.csv are not fetched/written again."""
import csv, logging, os, time
from collections import defaultdict
from .rpc import Rpc

log = logging.getLogger("obp.collect")
LANDED_FIELDS = ["signature", "run", "burst", "target", "label", "window_start", "send_seq", "order_mode",
                 "payer_arm", "cu_price", "cluster", "landed", "slot", "slot_leader", "leader_is_target",
                 "in_target_window", "block_index", "block_tx_count", "block_time", "our_tx_count", "err"]
BLOCK_FIELDS = ["slot", "block_time", "index", "signature", "fee", "cu_consumed", "num_sigs", "is_vote", "err"]


def _leader(rpc, slot, cache):
    if slot not in cache:
        try:
            res = rpc.slot_leaders(slot, 1)
            cache[slot] = res[0] if isinstance(res, list) and res else ""
        except Exception as e:  # noqa: BLE001 - a skipped slot can have no leader lookup
            log.warning("leader lookup failed for slot %s: %s", slot, e)
            cache[slot] = ""
    return cache[slot]


def _read_blocks(path):
    """Load what we already have so a re-run neither refetches nor duplicates it."""
    index_of, count_of, time_of, slots = {}, {}, {}, set()
    if not path:
        return index_of, count_of, time_of, slots
    try:
        fh = open(path, newline="")
    except FileNotFoundError:
        return index_of, count_of, time_of, slots
    with fh:
        for row in csv.DictReader(fh):
            try:
                slot = int(row["slot"])
                idx = int(row["index"])
            except (KeyError, TypeError, ValueError):
                continue
            slots.add(slot)
            count_of[slot] = count_of.get(slot, 0) + 1
            index_of[row.get("signature", "")] = (slot, idx)
            bt = row.get("block_time")
            if bt not in (None, "", "None"):
                time_of[slot] = int(bt)
    return index_of, count_of, time_of, slots


def _wait_for_newest_send(sent_rows, wait_sec):
    """Sleep until the newest send in sent.csv is at least `wait_sec` old, so a status check that
    runs immediately after a burst does not miss a transaction that confirms a second or two later."""
    if not wait_sec or wait_sec <= 0:
        return
    newest = None
    for r in sent_rows:
        try:
            ts_ns = int(r.get("send_ts_ns"))
        except (TypeError, ValueError):
            continue
        newest = ts_ns if newest is None else max(newest, ts_ns)
    if newest is None:
        return
    age = time.time() - newest / 1e9
    if age < wait_sec:
        delay = wait_sec - age
        log.info("newest send is %.1fs old; waiting %.1fs before collecting", age, delay)
        time.sleep(delay)


def collect(rpc: Rpc, sent_csv: str, landed_csv: str, blocks_csv: str, wait_sec: float = 0):
    sent_rows = list(csv.DictReader(open(sent_csv)))
    _wait_for_newest_send(sent_rows, wait_sec)
    sent = [r for r in sent_rows if r["live"] == "True" and r["send_result"] == "ok"]
    if not sent:
        log.warning("no live sends in %s (dry-run data has nothing to collect)", sent_csv)
        return []
    sent_sigs = {r["signature"] for r in sent}
    st = rpc.signature_statuses([r["signature"] for r in sent])
    slots = sorted({s["slot"] for s in st if s})

    index_of, count_of, time_of, done = _read_blocks(blocks_csv)
    our_count = defaultdict(int)
    for sig, (slot, _idx) in index_of.items():
        if sig in sent_sigs:
            our_count[slot] += 1

    new_file = not blocks_csv or not os.path.exists(blocks_csv) or os.path.getsize(blocks_csv) == 0
    with open(blocks_csv, "a", newline="") as bf:
        bw = csv.writer(bf)
        if new_file:
            bw.writerow(BLOCK_FIELDS)
        for slot in slots:
            if slot in done:
                continue  # idempotent: already recorded (confirmed blocks are immutable)
            blk = rpc.block(slot, "full")
            if isinstance(blk, dict) and "__error__" in blk:
                log.warning("skip slot %s: %s", slot, blk["__error__"].get("message", blk["__error__"]))
                continue
            if not blk:
                continue
            txs = blk.get("transactions") or []
            count_of[slot] = len(txs)
            time_of[slot] = blk.get("blockTime")
            for i, t in enumerate(txs):
                sig = t["transaction"]["signatures"][0]
                index_of[sig] = (slot, i)
                if sig in sent_sigs:
                    our_count[slot] += 1
                keys = t["transaction"]["message"]["accountKeys"]
                is_vote = "Vote111111111111111111111111111111111111111" in keys
                m = t.get("meta") or {}
                bw.writerow([slot, blk.get("blockTime"), i, sig, m.get("fee"), m.get("computeUnitsConsumed"),
                             len(t["transaction"]["signatures"]), is_vote, bool(m.get("err"))])

    out, lcache = [], {}
    for r, s in zip(sent, st):
        row = {k: r.get(k) for k in LANDED_FIELDS if k in r}
        row.update(landed=bool(s), slot="", slot_leader="", leader_is_target="", in_target_window="",
                   block_index="", block_tx_count="", block_time="", our_tx_count="", err="")
        if s:
            slot, idx = index_of.get(r["signature"], (s["slot"], None))
            ws = int(r["window_start"])
            leader = _leader(rpc, slot, lcache)
            row.update(slot=slot, slot_leader=leader,
                       leader_is_target=(leader == r["target"]) if leader else "",
                       in_target_window=ws <= slot < ws + 4, block_index="" if idx is None else idx,
                       block_tx_count=count_of.get(slot, ""), block_time=time_of.get(slot, ""),
                       our_tx_count=our_count.get(slot, 0), err=s.get("err") or "")
        out.append(row)
    with open(landed_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LANDED_FIELDS)
        w.writeheader(); w.writerows(out)
    log.info("landed %d/%d", sum(1 for r in out if r["landed"]), len(out))
    return out
