# obp results

- Analysis generated (UTC): 2026-10-25T18:25:56Z
- Measurement send window (UTC): 2026-10-25T18:24:39Z to 2026-10-25T18:25:30Z
- Plan created (UTC): 2026-10-25T18:24:11Z
- Rows: sent=25, landed=25, block_txs=4745

Positive tau means higher fee (or earlier send order) appears earlier in the block.
Permutation p-values use a two-sided null; small samples give weak evidence.

## Test plan: primary vs exploratory

**Pre-registered primary test:** pooled `tau_fee` per client label on the **same-payer** arm, using only **ascending + shuffled** bursts and only rows with `in_target_window=True` and `leader_is_target=True`. Descending bursts are excluded from the primary test because there fee order equals send order (confounded); desc is a consistency check only. Holm correction is applied across the per-label primary p-values below, separately for H1 (fee) and H2 (send).

Everything else (multi-payer arm, descending mode, per-burst, whole-block, landing rates) is **exploratory**. Groups with fewer than 3 of our transactions in the same block are dropped. That selection can bias the ordering sample toward bursts whose higher-fee transactions land more often (see the target-window landing distribution below). With a five-transaction burst the smallest attainable two-sided per-burst permutation p is 1/60 ≈ 0.017; pooled tests use 2000 permutations, so their floor is 0.0005.

## Verdict per label (H1 / H2 / H0)

All verdict inputs use the same-payer arm only. H1 = pooled tau_fee > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_fee > 0 in ascending bursts alone. H2 = pooled tau_send > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_send > 0 in ascending bursts alone. If both hold the verdict is **mixed**; if neither holds it is **no rule detected (H0 not rejected)**; zero primary groups gives **insufficient data**. Descending bursts are a consistency check only.

| label | primary bursts (asc+shuffle, same arm) | primary txs | tau_fee (same arm) | p_fee | Holm p_fee | Holm p_send | verdict | mode evidence |
|---|---|---|---|---|---|---|---|---|
| Agave | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=-; desc (consistency only): tau_fee=+1.000 p=0.332 tau_send=+1.000 p=0.332 |
| Firedancer | 1 | 3 | -1.000 | 0.332 | 0.996 | 0.996 | no rule detected (H0 not rejected) | asc (primary): tau_fee=-1.000 p=0.332 tau_send=+1.000 p=0.332; asc+shuffle (primary): tau_fee=-1.000 p=0.332 tau_send=+1.000 p=0.332 |
| HarmonicAgave | 1 | 3 | -1.000 | 0.332 | 0.996 | 0.996 | no rule detected (H0 not rejected) | asc (primary): tau_fee=-1.000 p=0.332 tau_send=+1.000 p=0.332; asc+shuffle (primary): tau_fee=-1.000 p=0.332 tau_send=+1.000 p=0.332 |
| JitoLabs | 1 | 3 | +0.333 | 1.000 | 1.000 | 0.996 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=+0.333 p=1.000 tau_send=+1.000 p=0.332 |

## Per-burst Kendall tau (primary: target window and target leader)

| label | target | arm | slot | n | tau_fee | p_fee | tau_send | p_send |
|---|---|---|---|---|---|---|---|---|
| HarmonicAgave | FBKFWadX | same | 461357959 | 3 | -1.000 | 0.332 | +1.000 | 0.318 |
| Agave | 7QQGNm3p | same | 461358005 | 3 | +1.000 | 0.335 | +1.000 | 0.347 |
| JitoLabs | C8Bey3LK | same | 461358046 | 3 | +0.333 | 1.000 | +1.000 | 0.332 |
| Firedancer | 9eGrDohd | same | 461358097 | 3 | -1.000 | 0.314 | +1.000 | 0.320 |

## Pooled per client label (primary: target window and target leader)

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 1 | 3 | +1.000 | +1.000 | 0.332 | 0.332 |
| Firedancer | 1 | 3 | -1.000 | +1.000 | 0.332 | 0.332 |
| HarmonicAgave | 1 | 3 | -1.000 | +1.000 | 0.332 | 0.332 |
| JitoLabs | 1 | 3 | +0.333 | +1.000 | 1.000 | 0.332 |

## Grouped results by payer arm and order mode (exploratory)

| label | grouped by | group | bursts | txs | mean tau_fee | pooled p_fee | mean tau_send | pooled p_send |
|---|---|---|---|---|---|---|---|---|
| Agave | payer_arm | same | 1 | 3 | +1.000 | 0.332 | +1.000 | 0.332 |
| Agave | order_mode | desc | 1 | 3 | +1.000 | 0.332 | +1.000 | 0.332 |
| Firedancer | payer_arm | same | 1 | 3 | -1.000 | 0.332 | +1.000 | 0.332 |
| Firedancer | order_mode | asc | 1 | 3 | -1.000 | 0.332 | +1.000 | 0.332 |
| HarmonicAgave | payer_arm | same | 1 | 3 | -1.000 | 0.332 | +1.000 | 0.332 |
| HarmonicAgave | order_mode | asc | 1 | 3 | -1.000 | 0.332 | +1.000 | 0.332 |
| JitoLabs | payer_arm | same | 1 | 3 | +0.333 | 1.000 | +1.000 | 0.332 |
| JitoLabs | order_mode | shuffle | 1 | 3 | +0.333 | 1.000 | +1.000 | 0.332 |

## Sensitivity: all landed (any leader)

Same statistic as the primary pooled table, but using every landed row regardless of `in_target_window` or `leader_is_target`. This is exploratory and shows how much the result depends on the leader filter.

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 1 | 3 | +1.000 | +1.000 | 0.332 | 0.332 |
| Firedancer | 1 | 3 | -1.000 | +1.000 | 0.332 | 0.332 |
| HarmonicAgave | 1 | 3 | -1.000 | +1.000 | 0.332 | 0.332 |
| JitoLabs | 1 | 3 | +0.333 | +1.000 | 1.000 | 0.332 |

## Landing and timing

Live timing uses live-only denominators. Dry-run timing is shown in separate columns so it cannot inflate a live rate. `on_time` means the per-tx estimated send slot was before `window_start`; `in_window_at_send` means the send was not after the window (`est_slot_at_send < window_start + 4`). The clearer `send_phase` column is `early` when `est_slot_at_send < window_start`, `inside` when it is in the four-slot window, and `late` otherwise.

| label | sent | live sent | landed | landing rate | live on_time | on_time rate | live in_window | in_window rate | mean live send_offset | dry sent | dry on_time | dry on_time rate | dry in_window | dry in_window rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agave | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -1.600 | 0 | 0 | - | 0 | - |
| Firedancer | 5 | 5 | 5 | 1.000 | 4 | 0.800 | 5 | 1.000 | -1.000 | 0 | 0 | - | 0 | - |
| HarmonicAgave | 5 | 5 | 5 | 1.000 | 2 | 0.400 | 5 | 1.000 | -0.400 | 0 | 0 | - | 0 | - |
| JitoLabs | 10 | 10 | 10 | 1.000 | 9 | 0.900 | 10 | 1.000 | -1.300 | 0 | 0 | - | 0 | - |

### Landing by fee level (live only)

| cu_price (micro/CU) | live sent | landed | landing rate | live on_time | on_time rate |
|---|---|---|---|---|---|
| 0 | 5 | 5 | 1.000 | 4 | 0.800 |
| 1000 | 5 | 5 | 1.000 | 5 | 1.000 |
| 10000 | 5 | 5 | 1.000 | 4 | 0.800 |
| 100000 | 5 | 5 | 1.000 | 4 | 0.800 |
| 1000000 | 5 | 5 | 1.000 | 3 | 0.600 |

### Selected sample: our txs in the target window per burst

The primary test only uses groups with **at least 3** of our transactions co-landed in the target block. This table counts, for each live burst, how many of its transactions landed anywhere in the target window (not necessarily in the same block). Bursts with 0-2 are under-represented in the ordering tests. If higher-fee transactions also land more often, the primary sample is biased toward higher fees; that selection effect is a limitation, not a finding.

| label | live bursts | 0 | 1 | 2 | 3 | 4 | 5 | mean landed in target window |
|---|---|---|---|---|---|---|---|---|
| Agave | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |
| Firedancer | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |
| HarmonicAgave | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |
| JitoLabs | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 5 |

## Verified leader windows

Only windows whose `window_end` is before the current finalized slot count as verified. `leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that actually produced a block; `planned` = not yet elapsed, not counted as verified.

| label | windows | leaders_ok | windows with blocks | block_slots | planned |
|---|---|---|---|---|---|
| Agave | 1 | 1 | 1 | 4 | 2 |
| AgaveBam | 0 | 0 | 0 | 0 | 5 |
| FireBAM | 0 | 0 | 0 | 0 | 3 |
| Firedancer | 1 | 1 | 1 | 4 | 6 |
| HarmonicAgave | 1 | 1 | 1 | 4 | 4 |
| HarmonicFiredancer | 0 | 0 | 0 | 0 | 4 |
| JitoLabs | 3 | 3 | 3 | 12 | 5 |

## Whole-block priority ordering (APPROXIMATION)

Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.
The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.
Positive tau = higher approximate priority fee appears earlier in the block.

| label | slots | mean tau_priority (approx) | non-vote txs |
|---|---|---|---|
| Agave | 2 | -0.020 | 953 |
| Firedancer | 2 | +0.035 | 733 |
| HarmonicAgave | 2 | +0.050 | 827 |
| JitoLabs | 6 | -0.076 | 2209 |

### Per-slot whole-block check

| slot | label | non-vote txs | tau_priority (approx) |
|---|---|---|---|
| 461357958 | HarmonicAgave | 385 | +0.095 |
| 461357959 | HarmonicAgave | 442 | +0.005 |
| 461358005 | Agave | 441 | -0.100 |
| 461358006 | Agave | 512 | +0.060 |
| 461358045 | JitoLabs | 342 | -0.059 |
| 461358046 | JitoLabs | 319 | -0.147 |
| 461358047 | JitoLabs | 501 | -0.104 |
| 461358097 | Firedancer | 322 | +0.037 |
| 461358098 | Firedancer | 411 | +0.033 |
| 461358197 | JitoLabs | 335 | +0.006 |
| 461358198 | JitoLabs | 247 | -0.066 |
| 461358199 | JitoLabs | 465 | -0.087 |
