# obp results

- Analysis generated (UTC): 2026-10-31T13:39:36Z
- Measurement send window (UTC): 2026-10-31T13:08:49Z to 2026-10-31T13:30:14Z
- Plan created (UTC): 2026-10-31T13:08:43Z
- Rows: sent=480, landed=444, block_txs=68539

Positive tau means higher fee (or earlier send order) appears earlier in the block.
Permutation p-values use a two-sided null; small samples give weak evidence.

## Test plan: primary vs exploratory

**Pre-registered primary test:** pooled `tau_fee` per client label on the **same-payer** arm, using only **ascending + shuffled** bursts and only rows with `in_target_window=True` and `leader_is_target=True`. Descending bursts are excluded from the primary test because there fee order equals send order (confounded); desc is a consistency check only. Holm correction is applied across the per-label primary p-values below, separately for H1 (fee) and H2 (send).

Everything else (multi-payer arm, descending mode, per-burst, whole-block, landing rates) is **exploratory**. Groups with fewer than 3 of our transactions in the same block are dropped. That selection can bias the ordering sample toward bursts whose higher-fee transactions land more often (see the target-window landing distribution below). With a five-transaction burst the smallest attainable two-sided per-burst permutation p is 1/60 ≈ 0.017; pooled tests use 2000 permutations, so their floor is 0.0005.

## Verdict per label (H1 / H2 / H0)

All verdict inputs use the same-payer arm only. H1 = pooled tau_fee > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_fee > 0 in ascending bursts alone. H2 = pooled tau_send > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_send > 0 in ascending bursts alone. If both hold the verdict is **mixed**; if neither holds it is **no rule detected (H0 not rejected)**; zero primary groups gives **insufficient data**. Descending bursts are a consistency check only.

| label | primary bursts (asc+shuffle, same arm) | primary txs | tau_fee (same arm) | p_fee | Holm p_fee | Holm p_send | verdict | mode evidence |
|---|---|---|---|---|---|---|---|---|
| Agave | 1 | 3 | +0.333 | 1.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=+0.333 p=1.000 tau_send=-0.333 p=1.000 |
| FireBAM | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=-; desc (consistency only): tau_fee=+1.000 p=0.332 tau_send=+1.000 p=0.332 |
| Firedancer | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=- |
| Frankendancer | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=-; desc (consistency only): tau_fee=-0.333 p=0.762 tau_send=-0.333 p=0.762 |
| HarmonicAgave | 1 | 5 | +0.000 | 1.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=+0.000 p=1.000 tau_send=+0.600 p=0.228 |
| HarmonicFiredancer | 3 | 12 | +0.222 | 0.535 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.333 p=0.765 tau_send=-0.333 p=0.742; asc+shuffle (primary): tau_fee=+0.222 p=0.535 tau_send=-0.333 p=0.318 |
| JitoLabs | 3 | 12 | +0.333 | 0.298 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.333 p=1.000 tau_send=-0.333 p=1.000; asc+shuffle (primary): tau_fee=+0.333 p=0.298 tau_send=-0.156 p=0.632; desc (consistency only): tau_fee=+1.000 p=0.332 tau_send=+1.000 p=0.332 |
| Rakurai | 1 | 3 | +0.333 | 1.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=+0.333 p=1.000 tau_send=-1.000 p=0.334; desc (consistency only): tau_fee=+0.333 p=0.544 tau_send=+0.333 p=0.544 |

## Per-burst Kendall tau (primary: target window and target leader)

| label | target | arm | slot | n | tau_fee | p_fee | tau_send | p_send |
|---|---|---|---|---|---|---|---|---|
| Agave | 7QQGNm3p | multi | 463700099 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| Agave | 5Us18hLZ | multi | 463700388 | 3 | +0.333 | 1.000 | -1.000 | 0.331 |
| HarmonicFiredancer | 6yFGGAgY | same | 463700564 | 4 | +0.667 | 0.323 | -0.333 | 0.774 |
| Agave | 7QQGNm3p | multi | 463700965 | 3 | -1.000 | 0.318 | +1.000 | 0.346 |
| Rakurai | ana2y2Yv | same | 463701279 | 3 | +0.333 | 1.000 | -1.000 | 0.332 |
| Rakurai | 7PdKhpKz | same | 463701413 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |
| Frankendancer | FBbqKvwL | same | 463701720 | 4 | -0.333 | 0.734 | -0.333 | 0.750 |
| JitoLabs | GnC339vk | multi | 463702042 | 3 | +0.333 | 1.000 | -1.000 | 0.335 |
| Firedancer | 4VRs6A9z | multi | 463702191 | 3 | -1.000 | 0.332 | -1.000 | 0.322 |
| HarmonicAgave | 3psxMyr7 | multi | 463702488 | 4 | +0.333 | 0.735 | +0.333 | 0.743 |
| HarmonicFiredancer | Awes4Tr6 | same | 463702579 | 4 | -0.333 | 0.744 | -0.333 | 0.736 |
| Frankendancer | FBbqKvwL | multi | 463703135 | 3 | -1.000 | 0.342 | -1.000 | 0.340 |
| JitoLabs | 5pPRHnie | same | 463703538 | 3 | +1.000 | 0.335 | +1.000 | 0.336 |
| JitoLabs | GnC339vk | same | 463703665 | 5 | +0.000 | 1.000 | -0.800 | 0.081 |
| Agave | 5Us18hLZ | same | 463704443 | 3 | +0.333 | 1.000 | -0.333 | 1.000 |
| HarmonicAgave | 3psxMyr7 | multi | 463704499 | 3 | -0.333 | 1.000 | +0.333 | 1.000 |
| Frankendancer | FBbqKvwL | multi | 463704596 | 3 | +0.333 | 1.000 | -1.000 | 0.326 |
| JitoLabs | C8Bey3LK | same | 463704659 | 3 | +0.333 | 1.000 | -0.333 | 1.000 |
| Agave | mds4GEui | multi | 463704704 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| JitoLabs | 5pPRHnie | same | 463704798 | 4 | +0.667 | 0.335 | +0.667 | 0.331 |
| HarmonicAgave | Hz5aLvpK | same | 463704984 | 5 | +0.000 | 1.000 | +0.600 | 0.228 |
| Rakurai | ana2y2Yv | same | 463705147 | 4 | +0.333 | 0.759 | +0.333 | 0.750 |
| HarmonicFiredancer | Awes4Tr6 | same | 463705239 | 4 | +0.333 | 0.763 | -0.333 | 0.760 |
| FireBAM | LA1NEzry | same | 463705494 | 3 | +1.000 | 0.327 | +1.000 | 0.332 |
| FireBAM | LA1NEzry | multi | 463705615 | 3 | +1.000 | 0.339 | +0.333 | 1.000 |
| HarmonicFiredancer | DrifTrN9 | multi | 463705826 | 3 | +0.333 | 1.000 | +1.000 | 0.338 |

## Pooled per client label (primary: target window and target leader)

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 5 | 15 | -0.200 | -0.200 | 0.621 | 0.622 |
| FireBAM | 2 | 6 | +1.000 | +0.667 | 0.057 | 0.276 |
| Firedancer | 1 | 3 | -1.000 | -1.000 | 0.332 | 0.332 |
| Frankendancer | 3 | 10 | -0.333 | -0.778 | 0.430 | 0.018 |
| HarmonicAgave | 3 | 12 | +0.000 | +0.422 | 1.000 | 0.186 |
| HarmonicFiredancer | 4 | 15 | +0.250 | +0.000 | 0.442 | 0.881 |
| JitoLabs | 5 | 18 | +0.467 | -0.093 | 0.067 | 0.721 |
| Rakurai | 3 | 10 | +0.333 | -0.111 | 0.427 | 0.673 |

## Grouped results by payer arm and order mode (exploratory)

| label | grouped by | group | bursts | txs | mean tau_fee | pooled p_fee | mean tau_send | pooled p_send |
|---|---|---|---|---|---|---|---|---|
| Agave | payer_arm | multi | 4 | 12 | -0.333 | 0.410 | -0.167 | 0.724 |
| Agave | payer_arm | same | 1 | 3 | +0.333 | 1.000 | -0.333 | 1.000 |
| Agave | order_mode | asc | 1 | 3 | -1.000 | 0.332 | +1.000 | 0.332 |
| Agave | order_mode | desc | 1 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| Agave | order_mode | shuffle | 3 | 9 | +0.111 | 0.927 | -0.556 | 0.233 |
| FireBAM | payer_arm | multi | 1 | 3 | +1.000 | 0.334 | +0.333 | 1.000 |
| FireBAM | payer_arm | same | 1 | 3 | +1.000 | 0.332 | +1.000 | 0.332 |
| FireBAM | order_mode | desc | 2 | 6 | +1.000 | 0.057 | +0.667 | 0.276 |
| Firedancer | payer_arm | multi | 1 | 3 | -1.000 | 0.332 | -1.000 | 0.332 |
| Firedancer | order_mode | desc | 1 | 3 | -1.000 | 0.332 | -1.000 | 0.332 |
| Frankendancer | payer_arm | multi | 2 | 6 | -0.333 | 0.496 | -1.000 | 0.057 |
| Frankendancer | payer_arm | same | 1 | 4 | -0.333 | 0.762 | -0.333 | 0.762 |
| Frankendancer | order_mode | desc | 1 | 4 | -0.333 | 0.762 | -0.333 | 0.762 |
| Frankendancer | order_mode | shuffle | 2 | 6 | -0.333 | 0.496 | -1.000 | 0.057 |
| HarmonicAgave | payer_arm | multi | 2 | 7 | +0.000 | 1.000 | +0.333 | 0.570 |
| HarmonicAgave | payer_arm | same | 1 | 5 | +0.000 | 1.000 | +0.600 | 0.228 |
| HarmonicAgave | order_mode | asc | 1 | 3 | -0.333 | 1.000 | +0.333 | 1.000 |
| HarmonicAgave | order_mode | desc | 1 | 4 | +0.333 | 0.740 | +0.333 | 0.740 |
| HarmonicAgave | order_mode | shuffle | 1 | 5 | +0.000 | 1.000 | +0.600 | 0.228 |
| HarmonicFiredancer | payer_arm | multi | 1 | 3 | +0.333 | 1.000 | +1.000 | 0.344 |
| HarmonicFiredancer | payer_arm | same | 3 | 12 | +0.222 | 0.535 | -0.333 | 0.318 |
| HarmonicFiredancer | order_mode | asc | 1 | 4 | +0.333 | 0.765 | -0.333 | 0.742 |
| HarmonicFiredancer | order_mode | shuffle | 3 | 11 | +0.222 | 0.616 | +0.111 | 0.658 |
| JitoLabs | payer_arm | multi | 1 | 3 | +0.333 | 1.000 | -1.000 | 0.332 |
| JitoLabs | payer_arm | same | 4 | 15 | +0.500 | 0.070 | +0.133 | 0.653 |
| JitoLabs | order_mode | asc | 1 | 3 | +0.333 | 1.000 | -0.333 | 1.000 |
| JitoLabs | order_mode | desc | 1 | 3 | +1.000 | 0.332 | +1.000 | 0.332 |
| JitoLabs | order_mode | shuffle | 3 | 12 | +0.333 | 0.308 | -0.378 | 0.226 |
| Rakurai | payer_arm | same | 3 | 10 | +0.333 | 0.427 | -0.111 | 0.673 |
| Rakurai | order_mode | desc | 2 | 7 | +0.333 | 0.544 | +0.333 | 0.544 |
| Rakurai | order_mode | shuffle | 1 | 3 | +0.333 | 1.000 | -1.000 | 0.334 |

## Sensitivity: all landed (any leader)

Same statistic as the primary pooled table, but using every landed row regardless of `in_target_window` or `leader_is_target`. This is exploratory and shows how much the result depends on the leader filter.

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 8 | 27 | +0.058 | -0.133 | 0.792 | 0.552 |
| AgaveBam | 7 | 29 | +0.238 | -0.133 | 0.224 | 0.494 |
| FireBAM | 5 | 17 | +0.267 | +0.000 | 0.361 | 1.000 |
| Firedancer | 2 | 8 | -0.200 | -0.900 | 0.631 | 0.018 |
| Frankendancer | 3 | 10 | -0.333 | -0.778 | 0.430 | 0.018 |
| HarmonicAgave | 7 | 28 | +0.067 | +0.295 | 0.734 | 0.149 |
| HarmonicFiredancer | 10 | 38 | +0.573 | -0.027 | 0.001 | 0.871 |
| JitoLabs | 10 | 34 | +0.367 | -0.247 | 0.051 | 0.188 |
| Rakurai | 6 | 21 | +0.444 | -0.056 | 0.066 | 0.806 |

## Landing and timing

Live timing uses live-only denominators. Dry-run timing is shown in separate columns so it cannot inflate a live rate. `on_time` means the per-tx estimated send slot was before `window_start`; `in_window_at_send` means the send was not after the window (`est_slot_at_send < window_start + 4`). The clearer `send_phase` column is `early` when `est_slot_at_send < window_start`, `inside` when it is in the four-slot window, and `late` otherwise.

| label | sent | live sent | landed | landing rate | live on_time | on_time rate | live in_window | in_window rate | mean live send_offset | dry sent | dry on_time | dry on_time rate | dry in_window | dry in_window rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agave | 45 | 45 | 40 | 0.889 | 45 | 1.000 | 45 | 1.000 | -5.111 | 0 | 0 | - | 0 | - |
| AgaveBam | 65 | 65 | 59 | 0.908 | 65 | 1.000 | 65 | 1.000 | -5.385 | 0 | 0 | - | 0 | - |
| FireBAM | 45 | 45 | 42 | 0.933 | 45 | 1.000 | 45 | 1.000 | -4.556 | 0 | 0 | - | 0 | - |
| Firedancer | 15 | 15 | 15 | 1.000 | 15 | 1.000 | 15 | 1.000 | -5.333 | 0 | 0 | - | 0 | - |
| Frankendancer | 25 | 25 | 23 | 0.920 | 25 | 1.000 | 25 | 1.000 | -5.200 | 0 | 0 | - | 0 | - |
| HarmonicAgave | 85 | 85 | 75 | 0.882 | 85 | 1.000 | 85 | 1.000 | -5.059 | 0 | 0 | - | 0 | - |
| HarmonicFiredancer | 70 | 70 | 67 | 0.957 | 70 | 1.000 | 70 | 1.000 | -4.929 | 0 | 0 | - | 0 | - |
| JitoLabs | 85 | 85 | 79 | 0.929 | 85 | 1.000 | 85 | 1.000 | -5.118 | 0 | 0 | - | 0 | - |
| JitoLabs+BAM | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -5.000 | 0 | 0 | - | 0 | - |
| Rakurai | 35 | 35 | 34 | 0.971 | 35 | 1.000 | 35 | 1.000 | -5.286 | 0 | 0 | - | 0 | - |
| Unknown(55997) | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -5.000 | 0 | 0 | - | 0 | - |

### Landing by fee level (live only)

| cu_price (micro/CU) | live sent | landed | landing rate | live on_time | on_time rate |
|---|---|---|---|---|---|
| 0 | 96 | 83 | 0.865 | 96 | 1.000 |
| 1000 | 96 | 92 | 0.958 | 96 | 1.000 |
| 10000 | 96 | 94 | 0.979 | 96 | 1.000 |
| 100000 | 96 | 94 | 0.979 | 96 | 1.000 |
| 1000000 | 96 | 81 | 0.844 | 96 | 1.000 |

### Selected sample: our txs in the target window per burst

The primary test only uses groups with **at least 3** of our transactions co-landed in the target block. This table counts, for each live burst, how many of its transactions landed anywhere in the target window (not necessarily in the same block). Bursts with 0-2 are under-represented in the ordering tests. If higher-fee transactions also land more often, the primary sample is biased toward higher fees; that selection effect is a limitation, not a finding.

| label | live bursts | 0 | 1 | 2 | 3 | 4 | 5 | mean landed in target window |
|---|---|---|---|---|---|---|---|---|
| Agave | 9 | 3 | 0 | 0 | 5 | 1 | 0 | 2.11 |
| AgaveBam | 13 | 5 | 4 | 3 | 0 | 1 | 0 | 1.08 |
| FireBAM | 9 | 1 | 2 | 1 | 1 | 1 | 3 | 2.89 |
| Firedancer | 3 | 1 | 0 | 0 | 0 | 1 | 1 | 3 |
| Frankendancer | 5 | 0 | 1 | 1 | 0 | 2 | 1 | 3.20 |
| HarmonicAgave | 17 | 3 | 3 | 5 | 2 | 3 | 1 | 2.12 |
| HarmonicFiredancer | 14 | 4 | 3 | 1 | 1 | 2 | 3 | 2.21 |
| JitoLabs | 17 | 6 | 2 | 1 | 2 | 4 | 2 | 2.12 |
| JitoLabs+BAM | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 2 |
| Rakurai | 7 | 3 | 0 | 1 | 0 | 2 | 1 | 2.14 |
| Unknown(55997) | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 2 |

## Verified leader windows

Only windows whose `window_end` is before the current finalized slot count as verified. `leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that actually produced a block; `planned` = not yet elapsed, not counted as verified.

| label | windows | leaders_ok | windows with blocks | block_slots | planned |
|---|---|---|---|---|---|
| Agave | 9 | 9 | 9 | 36 | 28 |
| AgaveBam | 18 | 18 | 18 | 72 | 58 |
| FireBAM | 14 | 14 | 14 | 56 | 25 |
| Firedancer | 7 | 7 | 7 | 28 | 36 |
| Frankendancer | 7 | 7 | 7 | 28 | 27 |
| HarmonicAgave | 26 | 26 | 26 | 104 | 52 |
| HarmonicFiredancer | 23 | 23 | 23 | 92 | 50 |
| JitoLabs | 25 | 25 | 25 | 100 | 55 |
| JitoLabs+BAM | 2 | 2 | 2 | 8 | 7 |
| Raiku | 1 | 1 | 1 | 4 | 7 |
| Rakurai | 11 | 11 | 11 | 44 | 29 |
| Unknown(55997) | 1 | 1 | 1 | 4 | 2 |

## Whole-block priority ordering (APPROXIMATION)

Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.
The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.
Positive tau = higher approximate priority fee appears earlier in the block.

| label | slots | mean tau_priority (approx) | non-vote txs |
|---|---|---|---|
| Agave | 20 | +0.009 | 4846 |
| AgaveBam | 30 | +0.017 | 8632 |
| FireBAM | 23 | +0.068 | 6798 |
| Firedancer | 6 | +0.011 | 2131 |
| Frankendancer | 12 | +0.057 | 3646 |
| HarmonicAgave | 45 | -0.017 | 15286 |
| HarmonicFiredancer | 32 | +0.009 | 8814 |
| JitoLabs | 42 | +0.009 | 11208 |
| JitoLabs+BAM | 4 | -0.018 | 1309 |
| Rakurai | 16 | -0.012 | 4709 |
| Unknown(55997) | 3 | -0.002 | 839 |

### Per-slot whole-block check

| slot | label | non-vote txs | tau_priority (approx) |
|---|---|---|---|
| 463699929 | AgaveBam | 195 | -0.057 |
| 463699931 | AgaveBam | 189 | -0.061 |
| 463699933 | AgaveBam | 173 | +0.040 |
| 463699935 | AgaveBam | 336 | -0.152 |
| 463699948 | AgaveBam | 371 | +0.100 |
| 463699970 | HarmonicAgave | 286 | +0.061 |
| 463699971 | HarmonicAgave | 396 | +0.003 |
| 463699972 | HarmonicAgave | 443 | +0.054 |
| 463700003 | HarmonicFiredancer | 226 | +0.170 |
| 463700005 | HarmonicFiredancer | 253 | -0.033 |
| 463700099 | Agave | 182 | -0.131 |
| 463700100 | Agave | 341 | +0.021 |
| 463700102 | Agave | 184 | +0.068 |
| 463700117 | JitoLabs | 255 | +0.104 |
| 463700118 | JitoLabs | 204 | -0.042 |
| 463700119 | JitoLabs | 213 | +0.033 |
| 463700195 | Rakurai | 280 | +0.053 |
| 463700196 | Rakurai | 460 | +0.111 |
| 463700197 | Rakurai | 244 | +0.013 |
| 463700232 | FireBAM | 322 | +0.036 |
| 463700233 | FireBAM | 234 | +0.100 |
| 463700234 | FireBAM | 217 | +0.057 |
| 463700302 | HarmonicFiredancer | 191 | +0.074 |
| 463700303 | HarmonicFiredancer | 254 | -0.043 |
| 463700305 | HarmonicFiredancer | 241 | -0.023 |
| 463700306 | HarmonicFiredancer | 209 | +0.078 |
| 463700357 | AgaveBam | 313 | -0.068 |
| 463700358 | AgaveBam | 303 | -0.001 |
| 463700360 | AgaveBam | 266 | -0.004 |
| 463700388 | Agave | 252 | -0.058 |
| 463700393 | Agave | 337 | +0.001 |
| 463700395 | Agave | 278 | +0.044 |
| 463700441 | JitoLabs | 224 | -0.080 |
| 463700444 | JitoLabs | 138 | +0.040 |
| 463700445 | JitoLabs | 212 | -0.025 |
| 463700519 | Unknown(55997) | 206 | -0.111 |
| 463700520 | Unknown(55997) | 319 | +0.182 |
| 463700521 | Unknown(55997) | 314 | -0.077 |
| 463700564 | HarmonicFiredancer | 296 | -0.045 |
| 463700565 | HarmonicFiredancer | 312 | +0.068 |
| 463700611 | JitoLabs | 351 | -0.037 |
| 463700612 | JitoLabs | 324 | +0.073 |
| 463700613 | JitoLabs | 254 | -0.016 |
| 463700746 | Firedancer | 297 | -0.082 |
| 463700747 | Firedancer | 280 | +0.082 |
| 463700749 | Firedancer | 192 | -0.006 |
| 463700814 | HarmonicAgave | 233 | +0.071 |
| 463700815 | HarmonicAgave | 278 | -0.104 |
| 463700816 | HarmonicAgave | 246 | -0.046 |
| 463700911 | Frankendancer | 201 | +0.077 |
| 463700912 | Frankendancer | 383 | +0.204 |
| 463700913 | Frankendancer | 230 | +0.052 |
| 463700932 | FireBAM | 263 | +0.074 |
| 463700933 | FireBAM | 220 | +0.120 |
| 463700934 | FireBAM | 285 | +0.150 |
| 463700964 | Agave | 316 | +0.073 |
| 463700965 | Agave | 265 | -0.075 |
| 463700995 | AgaveBam | 233 | +0.061 |
| 463701119 | AgaveBam | 309 | -0.115 |
| 463701120 | AgaveBam | 505 | +0.072 |
| 463701192 | JitoLabs | 299 | +0.134 |
| 463701193 | JitoLabs | 296 | +0.002 |
| 463701195 | JitoLabs | 301 | +0.057 |
| 463701278 | Rakurai | 225 | -0.018 |
| 463701279 | Rakurai | 289 | -0.076 |
| 463701280 | Rakurai | 227 | -0.063 |
| 463701310 | AgaveBam | 278 | -0.077 |
| 463701311 | AgaveBam | 282 | -0.071 |
| 463701412 | Rakurai | 150 | -0.017 |
| 463701413 | Rakurai | 245 | -0.060 |
| 463701415 | Rakurai | 383 | -0.011 |
| 463701454 | FireBAM | 237 | +0.029 |
| 463701455 | FireBAM | 302 | +0.004 |
| 463701456 | FireBAM | 332 | -0.055 |
| 463701495 | FireBAM | 262 | -0.033 |
| 463701496 | FireBAM | 383 | +0.104 |
| 463701596 | JitoLabs | 292 | -0.043 |
| 463701597 | JitoLabs | 249 | +0.026 |
| 463701600 | JitoLabs | 173 | -0.079 |
| 463701663 | AgaveBam | 211 | +0.015 |
| 463701664 | AgaveBam | 436 | +0.186 |
| 463701665 | AgaveBam | 310 | +0.098 |
| 463701720 | Frankendancer | 441 | -0.049 |
| 463701722 | Frankendancer | 483 | +0.047 |
| 463701801 | AgaveBam | 264 | +0.072 |
| 463701802 | AgaveBam | 278 | +0.053 |
| 463701803 | AgaveBam | 288 | +0.087 |
| 463701804 | AgaveBam | 312 | +0.091 |
| 463701838 | HarmonicFiredancer | 298 | +0.064 |
| 463701839 | HarmonicFiredancer | 274 | -0.133 |
| 463701878 | Firedancer | 271 | -0.068 |
| 463702042 | JitoLabs | 232 | +0.104 |
| 463702044 | JitoLabs | 535 | +0.241 |
| 463702131 | HarmonicAgave | 236 | +0.027 |
| 463702132 | HarmonicAgave | 175 | -0.160 |
| 463702133 | HarmonicAgave | 213 | -0.003 |
| 463702134 | HarmonicAgave | 228 | -0.107 |
| 463702190 | Firedancer | 529 | +0.089 |
| 463702191 | Firedancer | 562 | +0.052 |
| 463702219 | Agave | 270 | +0.070 |
| 463702303 | HarmonicAgave | 284 | -0.141 |
| 463702304 | HarmonicAgave | 341 | +0.044 |
| 463702305 | HarmonicAgave | 284 | +0.067 |
| 463702306 | HarmonicAgave | 253 | -0.005 |
| 463702334 | AgaveBam | 265 | -0.044 |
| 463702336 | AgaveBam | 398 | +0.091 |
| 463702372 | JitoLabs | 253 | +0.011 |
| 463702373 | JitoLabs | 293 | -0.029 |
| 463702463 | HarmonicAgave | 398 | -0.087 |
| 463702464 | HarmonicAgave | 246 | +0.030 |
| 463702465 | HarmonicAgave | 287 | -0.008 |
| 463702488 | HarmonicAgave | 487 | +0.081 |
| 463702578 | HarmonicFiredancer | 220 | +0.049 |
| 463702579 | HarmonicFiredancer | 255 | +0.027 |
| 463702606 | FireBAM | 432 | +0.090 |
| 463702626 | HarmonicFiredancer | 312 | -0.069 |
| 463702711 | JitoLabs | 289 | -0.006 |
| 463702712 | JitoLabs | 484 | +0.131 |
| 463702877 | HarmonicFiredancer | 213 | -0.016 |
| 463702878 | HarmonicFiredancer | 301 | +0.025 |
| 463702879 | HarmonicFiredancer | 275 | +0.002 |
| 463702941 | HarmonicAgave | 306 | -0.000 |
| 463702943 | HarmonicAgave | 458 | -0.055 |
| 463702945 | HarmonicAgave | 396 | -0.028 |
| 463702946 | HarmonicAgave | 327 | -0.053 |
| 463703048 | HarmonicAgave | 520 | -0.104 |
| 463703062 | Rakurai | 231 | +0.093 |
| 463703063 | Rakurai | 297 | +0.092 |
| 463703134 | Frankendancer | 286 | +0.089 |
| 463703135 | Frankendancer | 223 | +0.042 |
| 463703166 | AgaveBam | 239 | +0.062 |
| 463703223 | HarmonicFiredancer | 301 | -0.006 |
| 463703224 | HarmonicFiredancer | 224 | +0.272 |
| 463703225 | HarmonicFiredancer | 311 | -0.032 |
| 463703375 | JitoLabs | 213 | -0.008 |
| 463703376 | JitoLabs | 243 | -0.233 |
| 463703378 | JitoLabs | 272 | -0.031 |
| 463703448 | AgaveBam | 232 | -0.035 |
| 463703449 | AgaveBam | 321 | +0.070 |
| 463703537 | JitoLabs | 215 | -0.026 |
| 463703538 | JitoLabs | 263 | -0.024 |
| 463703539 | JitoLabs | 235 | +0.050 |
| 463703581 | JitoLabs | 203 | +0.104 |
| 463703583 | JitoLabs | 240 | +0.121 |
| 463703605 | JitoLabs | 344 | +0.120 |
| 463703607 | JitoLabs | 353 | -0.032 |
| 463703639 | AgaveBam | 328 | -0.001 |
| 463703641 | AgaveBam | 202 | +0.065 |
| 463703665 | JitoLabs | 253 | +0.067 |
| 463703748 | HarmonicAgave | 1542 | +0.195 |
| 463703749 | HarmonicAgave | 782 | +0.016 |
| 463703750 | HarmonicAgave | 777 | +0.009 |
| 463703823 | Frankendancer | 326 | +0.010 |
| 463703824 | Frankendancer | 297 | +0.127 |
| 463703825 | Frankendancer | 260 | +0.052 |
| 463703928 | HarmonicAgave | 262 | -0.020 |
| 463703930 | HarmonicAgave | 222 | -0.049 |
| 463703932 | HarmonicAgave | 334 | -0.132 |
| 463703935 | HarmonicAgave | 313 | +0.048 |
| 463704020 | Rakurai | 689 | +0.059 |
| 463704076 | Rakurai | 193 | -0.257 |
| 463704077 | Rakurai | 236 | -0.076 |
| 463704170 | Agave | 189 | +0.055 |
| 463704171 | Agave | 267 | +0.037 |
| 463704172 | Agave | 246 | -0.013 |
| 463704271 | HarmonicAgave | 317 | +0.061 |
| 463704272 | HarmonicAgave | 332 | -0.108 |
| 463704273 | HarmonicAgave | 296 | -0.073 |
| 463704303 | HarmonicAgave | 227 | +0.024 |
| 463704317 | JitoLabs | 300 | -0.191 |
| 463704318 | JitoLabs | 214 | +0.105 |
| 463704319 | JitoLabs | 225 | -0.107 |
| 463704443 | Agave | 181 | -0.019 |
| 463704444 | Agave | 149 | -0.162 |
| 463704445 | Agave | 147 | +0.095 |
| 463704499 | HarmonicAgave | 223 | +0.014 |
| 463704500 | HarmonicAgave | 210 | +0.018 |
| 463704554 | JitoLabs+BAM | 351 | +0.002 |
| 463704555 | JitoLabs+BAM | 341 | -0.029 |
| 463704556 | JitoLabs+BAM | 421 | +0.043 |
| 463704557 | JitoLabs+BAM | 196 | -0.089 |
| 463704596 | Frankendancer | 329 | +0.027 |
| 463704597 | Frankendancer | 187 | +0.005 |
| 463704658 | JitoLabs | 170 | -0.103 |
| 463704659 | JitoLabs | 316 | -0.062 |
| 463704660 | JitoLabs | 198 | +0.100 |
| 463704703 | Agave | 246 | +0.006 |
| 463704704 | Agave | 326 | +0.193 |
| 463704798 | JitoLabs | 216 | -0.063 |
| 463704800 | JitoLabs | 322 | +0.127 |
| 463704830 | HarmonicAgave | 177 | -0.072 |
| 463704882 | JitoLabs | 234 | -0.096 |
| 463704883 | JitoLabs | 308 | -0.034 |
| 463704963 | AgaveBam | 252 | -0.012 |
| 463704964 | AgaveBam | 259 | +0.023 |
| 463704984 | HarmonicAgave | 338 | -0.040 |
| 463705078 | FireBAM | 227 | +0.033 |
| 463705079 | FireBAM | 183 | -0.035 |
| 463705080 | FireBAM | 389 | +0.138 |
| 463705147 | Rakurai | 281 | -0.068 |
| 463705148 | Rakurai | 279 | +0.034 |
| 463705221 | Agave | 204 | -0.101 |
| 463705225 | Agave | 193 | -0.008 |
| 463705239 | HarmonicFiredancer | 284 | -0.035 |
| 463705241 | HarmonicFiredancer | 249 | -0.018 |
| 463705333 | HarmonicAgave | 169 | -0.020 |
| 463705334 | HarmonicAgave | 212 | -0.115 |
| 463705335 | HarmonicAgave | 202 | -0.020 |
| 463705411 | HarmonicFiredancer | 346 | -0.034 |
| 463705412 | HarmonicFiredancer | 261 | +0.117 |
| 463705414 | HarmonicFiredancer | 305 | -0.036 |
| 463705438 | Agave | 273 | +0.076 |
| 463705493 | FireBAM | 292 | +0.055 |
| 463705494 | FireBAM | 289 | +0.111 |
| 463705559 | HarmonicFiredancer | 320 | +0.043 |
| 463705560 | HarmonicFiredancer | 184 | +0.029 |
| 463705590 | HarmonicFiredancer | 281 | -0.089 |
| 463705591 | HarmonicFiredancer | 247 | -0.025 |
| 463705615 | FireBAM | 396 | +0.037 |
| 463705616 | FireBAM | 594 | +0.202 |
| 463705688 | HarmonicFiredancer | 430 | -0.121 |
| 463705690 | HarmonicFiredancer | 207 | +0.023 |
| 463705765 | FireBAM | 230 | +0.016 |
| 463705766 | FireBAM | 224 | +0.124 |
| 463705767 | FireBAM | 259 | +0.103 |
| 463705768 | FireBAM | 226 | +0.109 |
| 463705826 | HarmonicFiredancer | 362 | +0.049 |
| 463705827 | HarmonicFiredancer | 372 | -0.028 |
| 463705842 | AgaveBam | 284 | +0.025 |
| 463705919 | HarmonicAgave | 309 | -0.087 |
| 463705920 | HarmonicAgave | 169 | -0.057 |
| 463705921 | HarmonicAgave | 288 | +0.038 |
| 463705922 | HarmonicAgave | 264 | +0.045 |
