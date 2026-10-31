# obp results

- Analysis generated (UTC): 2026-10-31T13:40:32Z
- Measurement send window (UTC): 2026-10-25T16:15:51Z to 2026-10-25T16:36:51Z
- Plan created (UTC): 2026-10-25T16:15:44Z
- Rows: sent=500, landed=0, block_txs=0

Positive tau means higher fee (or earlier send order) appears earlier in the block.
Permutation p-values use a two-sided null; small samples give weak evidence.

## Test plan: primary vs exploratory

**Pre-registered primary test:** pooled `tau_fee` per client label on the **same-payer** arm, using only **ascending + shuffled** bursts and only rows with `in_target_window=True` and `leader_is_target=True`. Descending bursts are excluded from the primary test because there fee order equals send order (confounded); desc is a consistency check only. Holm correction is applied across the per-label primary p-values below, separately for H1 (fee) and H2 (send).

Everything else (multi-payer arm, descending mode, per-burst, whole-block, landing rates) is **exploratory**. Groups with fewer than 3 of our transactions in the same block are dropped. That selection can bias the ordering sample toward bursts whose higher-fee transactions land more often (see the target-window landing distribution below). With a five-transaction burst the smallest attainable two-sided per-burst permutation p is 1/60 ≈ 0.017; pooled tests use 2000 permutations, so their floor is 0.0005.

## Verdict per label (H1 / H2 / H0)

All verdict inputs use the same-payer arm only. H1 = pooled tau_fee > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_fee > 0 in ascending bursts alone. H2 = pooled tau_send > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_send > 0 in ascending bursts alone. If both hold the verdict is **mixed**; if neither holds it is **no rule detected (H0 not rejected)**; zero primary groups gives **insufficient data**. Descending bursts are a consistency check only.

_No same-block groups with >=3 target-window txs._

## Per-burst Kendall tau (primary: target window and target leader)

_No same-block groups with >=3 of our txs._

## Pooled per client label (primary: target window and target leader)

_No pooled data._

## Grouped results by payer arm and order mode (exploratory)

_No grouped data._

## Sensitivity: all landed (any leader)

Same statistic as the primary pooled table, but using every landed row regardless of `in_target_window` or `leader_is_target`. This is exploratory and shows how much the result depends on the leader filter.

_No landed data._

## Landing and timing

Live timing uses live-only denominators. Dry-run timing is shown in separate columns so it cannot inflate a live rate. `on_time` means the per-tx estimated send slot was before `window_start`; `in_window_at_send` means the send was not after the window (`est_slot_at_send < window_start + 4`). The clearer `send_phase` column is `early` when `est_slot_at_send < window_start`, `inside` when it is in the four-slot window, and `late` otherwise.

| label | sent | live sent | landed | landing rate | live on_time | on_time rate | live in_window | in_window rate | mean live send_offset | dry sent | dry on_time | dry on_time rate | dry in_window | dry in_window rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agave | 45 | 0 | 0 | - | 0 | - | 0 | - | - | 45 | 45 | 1.000 | 45 | 1.000 |
| AgaveBam | 65 | 0 | 0 | - | 0 | - | 0 | - | - | 65 | 65 | 1.000 | 65 | 1.000 |
| FireBAM | 55 | 0 | 0 | - | 0 | - | 0 | - | - | 55 | 53 | 0.964 | 53 | 0.964 |
| Firedancer | 85 | 0 | 0 | - | 0 | - | 0 | - | - | 85 | 85 | 1.000 | 85 | 1.000 |
| HarmonicAgave | 80 | 0 | 0 | - | 0 | - | 0 | - | - | 80 | 80 | 1.000 | 80 | 1.000 |
| HarmonicFiredancer | 55 | 0 | 0 | - | 0 | - | 0 | - | - | 55 | 55 | 1.000 | 55 | 1.000 |
| JitoLabs | 80 | 0 | 0 | - | 0 | - | 0 | - | - | 80 | 80 | 1.000 | 80 | 1.000 |
| Rakurai | 35 | 0 | 0 | - | 0 | - | 0 | - | - | 35 | 35 | 1.000 | 35 | 1.000 |

### Landing by fee level (live only)

| cu_price (micro/CU) | live sent | landed | landing rate | live on_time | on_time rate |
|---|---|---|---|---|---|
| 0 | 0 | 0 | - | 0 | - |
| 1000 | 0 | 0 | - | 0 | - |
| 10000 | 0 | 0 | - | 0 | - |
| 100000 | 0 | 0 | - | 0 | - |
| 1000000 | 0 | 0 | - | 0 | - |

### Selected sample: our txs in the target window per burst

The primary test only uses groups with **at least 3** of our transactions co-landed in the target block. This table counts, for each live burst, how many of its transactions landed anywhere in the target window (not necessarily in the same block). Bursts with 0-2 are under-represented in the ordering tests. If higher-fee transactions also land more often, the primary sample is biased toward higher fees; that selection effect is a limitation, not a finding.

_No live bursts._

## Verified leader windows

Only windows whose `window_end` is before the current finalized slot count as verified. `leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that actually produced a block; `planned` = not yet elapsed, not counted as verified.

| label | windows | leaders_ok | windows with blocks | block_slots | planned |
|---|---|---|---|---|---|
| Agave | 9 | 9 | 9 | 36 | 0 |
| AgaveBam | 15 | 15 | 15 | 60 | 0 |
| FireBAM | 11 | 11 | 11 | 44 | 0 |
| Firedancer | 18 | 18 | 18 | 72 | 0 |
| HarmonicAgave | 16 | 16 | 16 | 64 | 0 |
| HarmonicFiredancer | 12 | 12 | 12 | 48 | 0 |
| JitoLabs | 16 | 16 | 16 | 64 | 0 |
| Rakurai | 7 | 7 | 7 | 28 | 0 |

## Whole-block priority ordering (APPROXIMATION)

Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.
The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.
Positive tau = higher approximate priority fee appears earlier in the block.

_No labelled blocks with >=3 non-vote txs._

### Per-slot whole-block check

_No per-slot data._
