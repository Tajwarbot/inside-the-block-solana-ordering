"""Cross-slot and within-block order of our own transactions, per session.

Usage: python scripts/burst_split.py data/runs/<session>/landed.csv [more landed.csv ...]

For each burst it counts how the landed transactions were split over slots (e.g. 3+2).
For every pair of our transactions from the same burst that landed in different slots it
checks whether the earlier send (send_rank) or the higher fee (cu_price) went to the earlier
slot. For pairs in the same block it counts inversions of send order by block_index.
Reads only the committed CSV, no network.
"""
import collections
import csv
import itertools
import sys


def summarize(path):
    rows = [r for r in csv.DictReader(open(path)) if r["landed"] == "True"]
    by = collections.defaultdict(list)
    for r in rows:
        by[r["burst"]].append(r)
    splits = collections.Counter()
    send_fwd = send_rev = fee_fwd = fee_rev = 0
    same_block_pairs = inversions = 0
    for rs in by.values():
        slots = collections.Counter(r["slot"] for r in rs)
        splits["+".join(str(n) for n in sorted(slots.values(), reverse=True))] += 1
        for a, c in itertools.combinations(rs, 2):
            ds = int(a["slot"]) - int(c["slot"])
            if ds == 0:
                same_block_pairs += 1
                if (int(a["block_index"]) - int(c["block_index"])) * (int(a["send_rank"]) - int(c["send_rank"])) < 0:
                    inversions += 1
                continue
            s = ds * (int(a["send_rank"]) - int(c["send_rank"]))
            send_fwd += s > 0
            send_rev += s < 0
            f = ds * (int(c["cu_price"]) - int(a["cu_price"]))
            fee_fwd += f > 0
            fee_rev += f < 0
    print(path)
    print(f"  bursts with a landed tx: {len(by)}")
    print("  split of landed txs over slots: " + ", ".join(f"{k}: {v}" for k, v in splits.most_common()))
    print(f"  cross-slot pairs, earlier send in earlier slot: {send_fwd}, reverse: {send_rev}")
    print(f"  cross-slot pairs, higher fee in earlier slot: {fee_fwd}, reverse: {fee_rev}")
    print(f"  same-block pairs: {same_block_pairs}, send-order inversions: {inversions}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        summarize(p)
