# obp results

- Analysis generated (UTC): 2026-10-31T13:08:36Z
- Measurement send window (UTC): 2026-10-31T12:57:20Z to 2026-10-31T13:06:21Z
- Plan created (UTC): 2026-10-31T12:56:50Z
- Rows: sent=60, landed=60, block_txs=8165

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

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 1 | 4 | +0.000 | -0.667 | 1.000 | 0.326 |
| AgaveBam | 3 | 10 | -0.556 | +0.333 | 0.149 | 0.438 |
| Firedancer | 1 | 3 | -1.000 | -1.000 | 0.344 | 0.344 |
| Frankendancer | 2 | 7 | +0.833 | +0.833 | 0.069 | 0.069 |
| HarmonicAgave | 1 | 3 | +0.333 | -0.333 | 1.000 | 1.000 |
| HarmonicFiredancer | 2 | 6 | +0.333 | -0.333 | 0.712 | 0.712 |
| Rakurai | 1 | 3 | +0.333 | -0.333 | 1.000 | 1.000 |

## Landing and timing

Live timing uses live-only denominators. Dry-run timing is shown in separate columns so it cannot inflate a live rate. `on_time` means the per-tx estimated send slot was before `window_start`; `in_window_at_send` means the send was not after the window (`est_slot_at_send < window_start + 4`). The clearer `send_phase` column is `early` when `est_slot_at_send < window_start`, `inside` when it is in the four-slot window, and `late` otherwise.

| label | sent | live sent | landed | landing rate | live on_time | on_time rate | live in_window | in_window rate | mean live send_offset | dry sent | dry on_time | dry on_time rate | dry in_window | dry in_window rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agave | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -1.000 | 0 | 0 | - | 0 | - |
| AgaveBam | 15 | 15 | 15 | 1.000 | 15 | 1.000 | 15 | 1.000 | -1.333 | 0 | 0 | - | 0 | - |
| Firedancer | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -1.000 | 0 | 0 | - | 0 | - |
| Frankendancer | 10 | 10 | 10 | 1.000 | 10 | 1.000 | 10 | 1.000 | -1.000 | 0 | 0 | - | 0 | - |
| HarmonicAgave | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -2.000 | 0 | 0 | - | 0 | - |
| HarmonicFiredancer | 10 | 10 | 10 | 1.000 | 10 | 1.000 | 10 | 1.000 | -1.000 | 0 | 0 | - | 0 | - |
| JitoLabs | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -2.000 | 0 | 0 | - | 0 | - |
| Rakurai | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -1.000 | 0 | 0 | - | 0 | - |

### Landing by fee level (live only)

| cu_price (micro/CU) | live sent | landed | landing rate | live on_time | on_time rate |
|---|---|---|---|---|---|
| 0 | 12 | 12 | 1.000 | 12 | 1.000 |
| 1000 | 12 | 12 | 1.000 | 12 | 1.000 |
| 10000 | 12 | 12 | 1.000 | 12 | 1.000 |
| 100000 | 12 | 12 | 1.000 | 12 | 1.000 |
| 1000000 | 12 | 12 | 1.000 | 12 | 1.000 |

### Selected sample: our txs in the target window per burst

The primary test only uses groups with **at least 3** of our transactions co-landed in the target block. This table counts, for each live burst, how many of its transactions landed anywhere in the target window (not necessarily in the same block). Bursts with 0-2 are under-represented in the ordering tests. If higher-fee transactions also land more often, the primary sample is biased toward higher fees; that selection effect is a limitation, not a finding.

| label | live bursts | 0 | 1 | 2 | 3 | 4 | 5 | mean landed in target window |
|---|---|---|---|---|---|---|---|---|
| Agave | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| AgaveBam | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| Firedancer | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| Frankendancer | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| HarmonicAgave | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| HarmonicFiredancer | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| JitoLabs | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| Rakurai | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

## Verified leader windows

Only windows whose `window_end` is before the current finalized slot count as verified. `leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that actually produced a block; `planned` = not yet elapsed, not counted as verified.

| label | windows | leaders_ok | windows with blocks | block_slots | planned |
|---|---|---|---|---|---|
| Agave | 3 | 3 | 3 | 12 | 29 |
| AgaveBam | 9 | 9 | 9 | 36 | 70 |
| FireBAM | 3 | 3 | 3 | 12 | 34 |
| Firedancer | 4 | 4 | 4 | 16 | 36 |
| Frankendancer | 4 | 4 | 4 | 16 | 32 |
| HarmonicAgave | 7 | 7 | 7 | 28 | 74 |
| HarmonicFiredancer | 9 | 9 | 9 | 36 | 63 |
| JitoLabs | 11 | 11 | 11 | 44 | 70 |
| JitoLabs+BAM | 0 | 0 | 0 | 0 | 8 |
| Raiku | 1 | 1 | 1 | 4 | 7 |
| Rakurai | 7 | 7 | 7 | 28 | 33 |

## Whole-block priority ordering (APPROXIMATION)

Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.
The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.
Positive tau = higher approximate priority fee appears earlier in the block.

| label | slots | mean tau_priority (approx) | non-vote txs |
|---|---|---|---|
| Agave | 2 | +0.033 | 351 |
| AgaveBam | 7 | +0.043 | 1814 |
| Firedancer | 2 | +0.009 | 480 |
| Frankendancer | 5 | +0.041 | 1622 |
| HarmonicAgave | 3 | +0.056 | 965 |
| HarmonicFiredancer | 6 | +0.065 | 1509 |
| JitoLabs | 3 | +0.037 | 617 |
| Rakurai | 3 | +0.039 | 754 |

### Per-slot whole-block check

| slot | label | non-vote txs | tau_priority (approx) |
|---|---|---|---|
| 463696716 | Frankendancer | 373 | +0.250 |
| 463696718 | Frankendancer | 276 | -0.054 |
| 463697208 | HarmonicAgave | 415 | +0.120 |
| 463697209 | HarmonicAgave | 273 | +0.090 |
| 463697211 | HarmonicAgave | 277 | -0.043 |
| 463697380 | Rakurai | 266 | +0.040 |
| 463697381 | Rakurai | 240 | +0.057 |
| 463697387 | Rakurai | 248 | +0.020 |
| 463697773 | JitoLabs | 170 | +0.073 |
| 463697774 | JitoLabs | 214 | +0.006 |
| 463697775 | JitoLabs | 233 | +0.033 |
| 463698195 | AgaveBam | 188 | +0.065 |
| 463698196 | AgaveBam | 317 | +0.156 |
| 463698220 | HarmonicFiredancer | 188 | +0.097 |
| 463698221 | HarmonicFiredancer | 176 | +0.046 |
| 463698222 | HarmonicFiredancer | 238 | +0.026 |
| 463698299 | Firedancer | 279 | -0.023 |
| 463698300 | Firedancer | 201 | +0.041 |
| 463698978 | AgaveBam | 249 | +0.009 |
| 463698980 | AgaveBam | 226 | -0.061 |
| 463699004 | Agave | 176 | -0.063 |
| 463699005 | Agave | 175 | +0.128 |
| 463699072 | HarmonicFiredancer | 333 | +0.269 |
| 463699073 | HarmonicFiredancer | 255 | -0.006 |
| 463699074 | HarmonicFiredancer | 319 | -0.043 |
| 463699175 | Frankendancer | 299 | +0.196 |
| 463699176 | Frankendancer | 287 | -0.117 |
| 463699177 | Frankendancer | 387 | -0.069 |
| 463699244 | AgaveBam | 306 | +0.040 |
| 463699245 | AgaveBam | 271 | +0.047 |
| 463699251 | AgaveBam | 257 | +0.042 |
