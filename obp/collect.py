"""Find where our transactions landed: slot, leader, intra-block index. Read-only.
Also dumps every transaction of those blocks (index, fee, CUs) as supplementary data."""
import csv, logging
from .rpc import Rpc

log = logging.getLogger("obp.collect")
LANDED_FIELDS = ["signature", "run", "burst", "target", "label", "window_start", "send_seq", "order_mode",
                 "payer_arm", "cu_price", "landed", "slot", "slot_leader", "in_target_window", "block_index",
                 "block_tx_count", "err"]


def _leader(rpc, slot, cache):
    if slot not in cache:
        cache[slot] = rpc.slot_leaders(slot, 1)[0]
    return cache[slot]


def collect(rpc: Rpc, sent_csv: str, landed_csv: str, blocks_csv: str):
    sent = [r for r in csv.DictReader(open(sent_csv)) if r["live"] == "True" and r["send_result"] == "ok"]
    if not sent:
        log.warning("no live sends in %s (dry-run data has nothing to collect)", sent_csv)
        return []
    st = rpc.signature_statuses([r["signature"] for r in sent])
    slots = sorted({s["slot"] for s in st if s})
    index_of, count_of, leaders = {}, {}, {}
    with open(blocks_csv, "a", newline="") as bf:
        bw = csv.writer(bf)
        if bf.tell() == 0:
            bw.writerow(["slot", "index", "signature", "fee", "cu_consumed", "num_sigs", "is_vote", "err"])
        for slot in slots:
            blk = rpc.block(slot, "full")
            if isinstance(blk, dict) and "__error__" in blk:
                continue
            txs = blk["transactions"]
            count_of[slot] = len(txs)
            for i, t in enumerate(txs):
                sig = t["transaction"]["signatures"][0]
                index_of[sig] = (slot, i)
                keys = t["transaction"]["message"]["accountKeys"]
                is_vote = "Vote111111111111111111111111111111111111111" in keys
                m = t.get("meta") or {}
                bw.writerow([slot, i, sig, m.get("fee"), m.get("computeUnitsConsumed"),
                             len(t["transaction"]["signatures"]), is_vote, bool(m.get("err"))])
    out, lcache = [], {}
    for r, s in zip(sent, st):
        row = {k: r.get(k) for k in LANDED_FIELDS if k in r}
        row.update(landed=bool(s), slot="", slot_leader="", in_target_window="", block_index="",
                   block_tx_count="", err="")
        if s:
            slot, idx = index_of.get(r["signature"], (s["slot"], None))
            ws = int(r["window_start"])
            row.update(slot=slot, slot_leader=_leader(rpc, slot, lcache), in_target_window=ws <= slot < ws + 4,
                       block_index=idx, block_tx_count=count_of.get(slot), err=s.get("err") or "")
        out.append(row)
    with open(landed_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LANDED_FIELDS)
        w.writeheader(); w.writerows(out)
    log.info("landed %d/%d", sum(1 for r in out if r["landed"]), len(out))
    return out
