# obp results

- Analysis generated (UTC): 2026-10-31T12:56:13Z
- Measurement send window (UTC): 2026-10-31T12:04:42Z to 2026-10-31T12:41:22Z
- Plan created (UTC): 2026-10-31T12:04:37Z
- Rows: sent=565, landed=558, block_txs=70505

Positive tau means higher fee (or earlier send order) appears earlier in the block.
Permutation p-values use a two-sided null; small samples give weak evidence.

## Test plan: primary vs exploratory

**Pre-registered primary test:** pooled `tau_fee` per client label on the **same-payer** arm, using only **ascending + shuffled** bursts and only rows with `in_target_window=True` and `leader_is_target=True`. Descending bursts are excluded from the primary test because there fee order equals send order (confounded); desc is a consistency check only. Holm correction is applied across the per-label primary p-values below, separately for H1 (fee) and H2 (send).

Everything else (multi-payer arm, descending mode, per-burst, whole-block, landing rates) is **exploratory**. Groups with fewer than 3 of our transactions in the same block are dropped. That selection can bias the ordering sample toward bursts whose higher-fee transactions land more often (see the target-window landing distribution below). With a five-transaction burst the smallest attainable two-sided per-burst permutation p is 1/60 ≈ 0.017; pooled tests use 2000 permutations, so their floor is 0.0005.

## Verdict per label (H1 / H2 / H0)

All verdict inputs use the same-payer arm only. H1 = pooled tau_fee > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_fee > 0 in ascending bursts alone. H2 = pooled tau_send > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_send > 0 in ascending bursts alone. If both hold the verdict is **mixed**; if neither holds it is **no rule detected (H0 not rejected)**; zero primary groups gives **insufficient data**. Descending bursts are a consistency check only.

| label | primary bursts (asc+shuffle, same arm) | primary txs | tau_fee (same arm) | p_fee | Holm p_fee | Holm p_send | verdict | mode evidence |
|---|---|---|---|---|---|---|---|---|
| Agave | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=-; desc (consistency only): tau_fee=-0.333 p=1.000 tau_send=-0.333 p=1.000 |
| AgaveBam | 3 | 13 | +0.578 | 0.029 | 0.087 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.367 p=0.303 tau_send=-0.367 p=0.303; asc+shuffle (primary): tau_fee=+0.578 p=0.029 tau_send=-0.022 p=0.951 |
| FireBAM | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=- |
| Frankendancer | 1 | 3 | -0.333 | 1.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=-0.333 p=1.000 tau_send=-1.000 p=0.334; desc (consistency only): tau_fee=-0.200 p=0.815 tau_send=-0.200 p=0.821 |
| HarmonicAgave | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=-; desc (consistency only): tau_fee=+0.333 p=1.000 tau_send=+0.333 p=1.000 |
| HarmonicFiredancer | 3 | 13 | +0.778 | 0.002 | 0.006 | 1.000 | H1 fee rule | asc (primary): tau_fee=+0.667 p=0.029 tau_send=-0.500 p=0.128; asc+shuffle (primary): tau_fee=+0.778 p=0.002 tau_send=-0.111 p=0.662; desc (consistency only): tau_fee=+1.000 p=0.332 tau_send=+1.000 p=0.332 |
| JitoLabs | 2 | 9 | +0.033 | 0.934 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.033 p=0.934 tau_send=-0.033 p=0.934; asc+shuffle (primary): tau_fee=+0.033 p=0.934 tau_send=-0.033 p=0.934; desc (consistency only): tau_fee=-0.089 p=0.786 tau_send=-0.089 p=0.786 |
| Raiku | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=-; desc (consistency only): tau_fee=-0.800 p=0.085 tau_send=-0.800 p=0.085 |
| Rakurai | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=- |

## Per-burst Kendall tau (primary: target window and target leader)

| label | target | arm | slot | n | tau_fee | p_fee | tau_send | p_send |
|---|---|---|---|---|---|---|---|---|
| Frankendancer | FBbqKvwL | multi | 463682239 | 5 | +1.000 | 0.018 | +1.000 | 0.022 |
| AgaveBam | GQzMeEMw | same | 463683466 | 4 | +1.000 | 0.082 | +0.667 | 0.347 |
| JitoLabs | FbYX2uN5 | same | 463683941 | 3 | -1.000 | 0.327 | -1.000 | 0.349 |
| JitoLabs | C8Bey3LK | multi | 463684270 | 5 | +0.000 | 1.000 | +0.000 | 1.000 |
| Agave | 7QQGNm3p | same | 463684315 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| HarmonicFiredancer | pSo1KZXg | same | 463684718 | 4 | +0.333 | 0.747 | +0.000 | 1.000 |
| FireBAM | 9jxgosAf | multi | 463684759 | 4 | -1.000 | 0.080 | -0.667 | 0.329 |
| HarmonicAgave | FBKFWadX | multi | 463684871 | 4 | +1.000 | 0.076 | -1.000 | 0.083 |
| AgaveBam | GzDfKKoZ | multi | 463684970 | 3 | +1.000 | 0.343 | +0.333 | 1.000 |
| HarmonicAgave | Hz5aLvpK | multi | 463685091 | 5 | +0.000 | 1.000 | -0.200 | 0.818 |
| JitoLabs | C8Bey3LK | multi | 463685474 | 4 | -1.000 | 0.089 | +1.000 | 0.084 |
| HarmonicFiredancer | 6yFGGAgY | multi | 463685571 | 5 | +0.400 | 0.474 | -0.400 | 0.472 |
| AgaveBam | GzDfKKoZ | same | 463685614 | 4 | +0.333 | 0.760 | -0.333 | 0.757 |
| HarmonicFiredancer | DrifTrN9 | multi | 463685654 | 4 | +0.000 | 1.000 | +0.000 | 1.000 |
| HarmonicFiredancer | Awes4Tr6 | same | 463685686 | 4 | +1.000 | 0.077 | +0.667 | 0.327 |
| HarmonicFiredancer | Awes4Tr6 | same | 463685875 | 5 | +1.000 | 0.021 | -1.000 | 0.021 |
| Raiku | 9xcXe4WR | same | 463686379 | 5 | -0.800 | 0.086 | -0.800 | 0.081 |
| Agave | 5Us18hLZ | multi | 463686415 | 5 | -0.400 | 0.496 | -0.400 | 0.482 |
| Frankendancer | 4SNKY7GC | same | 463686629 | 3 | -0.333 | 1.000 | -1.000 | 0.327 |
| HarmonicFiredancer | pSo1KZXg | multi | 463686659 | 4 | -0.333 | 0.744 | +0.333 | 0.754 |
| JitoLabs | FbYX2uN5 | same | 463687041 | 4 | +0.333 | 0.766 | +0.333 | 0.755 |
| JitoLabs | C8Bey3LK | multi | 463687075 | 4 | -0.667 | 0.321 | -0.667 | 0.345 |
| Frankendancer | FBbqKvwL | same | 463687419 | 5 | -0.200 | 0.810 | -0.200 | 0.814 |
| FireBAM | 9jxgosAf | multi | 463687454 | 5 | -0.400 | 0.484 | -0.200 | 0.803 |
| JitoLabs | GnC339vk | multi | 463688175 | 5 | -0.800 | 0.085 | -0.200 | 0.801 |
| Rakurai | ana2y2Yv | multi | 463688295 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |
| JitoLabs | 5pPRHnie | same | 463688486 | 5 | +0.400 | 0.469 | +0.400 | 0.481 |
| HarmonicFiredancer | pSo1KZXg | same | 463689822 | 3 | +1.000 | 0.348 | +1.000 | 0.350 |
| JitoLabs | 5pPRHnie | same | 463689951 | 5 | +0.400 | 0.490 | -0.400 | 0.483 |
| Frankendancer | FBbqKvwL | multi | 463689994 | 5 | +1.000 | 0.015 | +1.000 | 0.015 |
| HarmonicFiredancer | 6yFGGAgY | multi | 463690099 | 4 | +1.000 | 0.080 | -1.000 | 0.075 |
| JitoLabs | 5pPRHnie | same | 463690651 | 4 | -0.333 | 0.750 | +0.333 | 0.765 |
| HarmonicAgave | Hz5aLvpK | multi | 463690767 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| HarmonicAgave | 3psxMyr7 | same | 463691135 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |
| HarmonicFiredancer | 6yFGGAgY | multi | 463691175 | 3 | +1.000 | 0.323 | -0.333 | 1.000 |
| AgaveBam | GBQ2GvTz | same | 463691203 | 5 | +0.400 | 0.472 | -0.400 | 0.479 |
| AgaveBam | 9rkJMARq | multi | 463691393 | 5 | +0.600 | 0.233 | -0.600 | 0.231 |

## Pooled per client label (primary: target window and target leader)

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 2 | 8 | -0.367 | -0.367 | 0.404 | 0.406 |
| AgaveBam | 5 | 21 | +0.667 | -0.067 | 0.002 | 0.751 |
| FireBAM | 2 | 9 | -0.700 | -0.433 | 0.038 | 0.185 |
| Frankendancer | 4 | 18 | +0.367 | +0.200 | 0.120 | 0.417 |
| HarmonicAgave | 4 | 15 | +0.250 | -0.300 | 0.390 | 0.308 |
| HarmonicFiredancer | 9 | 36 | +0.600 | -0.081 | 0.000 | 0.644 |
| JitoLabs | 9 | 39 | -0.296 | -0.022 | 0.066 | 0.882 |
| Raiku | 1 | 5 | -0.800 | -0.800 | 0.085 | 0.085 |
| Rakurai | 1 | 3 | +0.333 | +0.333 | 1.000 | 1.000 |

## Grouped results by payer arm and order mode (exploratory)

| label | grouped by | group | bursts | txs | mean tau_fee | pooled p_fee | mean tau_send | pooled p_send |
|---|---|---|---|---|---|---|---|---|
| Agave | payer_arm | multi | 1 | 5 | -0.400 | 0.480 | -0.400 | 0.504 |
| Agave | payer_arm | same | 1 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| Agave | order_mode | desc | 1 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| Agave | order_mode | shuffle | 1 | 5 | -0.400 | 0.480 | -0.400 | 0.504 |
| AgaveBam | payer_arm | multi | 2 | 8 | +0.800 | 0.043 | -0.133 | 0.790 |
| AgaveBam | payer_arm | same | 3 | 13 | +0.578 | 0.029 | -0.022 | 0.951 |
| AgaveBam | order_mode | asc | 3 | 14 | +0.444 | 0.081 | -0.444 | 0.081 |
| AgaveBam | order_mode | shuffle | 2 | 7 | +1.000 | 0.015 | +0.500 | 0.333 |
| FireBAM | payer_arm | multi | 2 | 9 | -0.700 | 0.038 | -0.433 | 0.185 |
| FireBAM | order_mode | desc | 1 | 4 | -1.000 | 0.081 | -0.667 | 0.334 |
| FireBAM | order_mode | shuffle | 1 | 5 | -0.400 | 0.484 | -0.200 | 0.812 |
| Frankendancer | payer_arm | multi | 2 | 10 | +1.000 | 0.000 | +1.000 | 0.000 |
| Frankendancer | payer_arm | same | 2 | 8 | -0.267 | 0.570 | -0.600 | 0.141 |
| Frankendancer | order_mode | desc | 3 | 15 | +0.600 | 0.014 | +0.600 | 0.015 |
| Frankendancer | order_mode | shuffle | 1 | 3 | -0.333 | 1.000 | -1.000 | 0.334 |
| HarmonicAgave | payer_arm | multi | 3 | 12 | +0.222 | 0.469 | -0.511 | 0.087 |
| HarmonicAgave | payer_arm | same | 1 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |
| HarmonicAgave | order_mode | asc | 2 | 7 | +0.333 | 0.425 | -0.667 | 0.148 |
| HarmonicAgave | order_mode | desc | 2 | 8 | +0.167 | 0.745 | +0.067 | 0.910 |
| HarmonicFiredancer | payer_arm | multi | 5 | 20 | +0.413 | 0.066 | -0.280 | 0.245 |
| HarmonicFiredancer | payer_arm | same | 4 | 16 | +0.833 | 0.000 | +0.167 | 0.549 |
| HarmonicFiredancer | order_mode | asc | 4 | 17 | +0.500 | 0.036 | -0.417 | 0.070 |
| HarmonicFiredancer | order_mode | desc | 2 | 7 | +0.500 | 0.333 | +0.500 | 0.333 |
| HarmonicFiredancer | order_mode | shuffle | 3 | 12 | +0.800 | 0.005 | -0.022 | 0.952 |
| JitoLabs | payer_arm | multi | 4 | 18 | -0.617 | 0.004 | +0.033 | 0.874 |
| JitoLabs | payer_arm | same | 5 | 21 | -0.040 | 0.879 | -0.067 | 0.753 |
| JitoLabs | order_mode | asc | 4 | 18 | -0.233 | 0.326 | +0.233 | 0.326 |
| JitoLabs | order_mode | desc | 3 | 12 | -0.089 | 0.786 | -0.089 | 0.786 |
| JitoLabs | order_mode | shuffle | 2 | 9 | -0.733 | 0.014 | -0.433 | 0.190 |
| Raiku | payer_arm | same | 1 | 5 | -0.800 | 0.085 | -0.800 | 0.085 |
| Raiku | order_mode | desc | 1 | 5 | -0.800 | 0.085 | -0.800 | 0.085 |
| Rakurai | payer_arm | multi | 1 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |
| Rakurai | order_mode | desc | 1 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |

## Sensitivity: all landed (any leader)

Same statistic as the primary pooled table, but using every landed row regardless of `in_target_window` or `leader_is_target`. This is exploratory and shows how much the result depends on the leader filter.

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 3 | 11 | -0.356 | -0.356 | 0.307 | 0.331 |
| AgaveBam | 10 | 37 | +0.500 | +0.033 | 0.004 | 0.848 |
| FireBAM | 6 | 24 | -0.200 | +0.167 | 0.377 | 0.452 |
| Firedancer | 4 | 13 | +0.500 | +0.250 | 0.103 | 0.494 |
| Frankendancer | 6 | 25 | +0.300 | +0.411 | 0.153 | 0.048 |
| HarmonicAgave | 11 | 38 | -0.121 | -0.079 | 0.486 | 0.663 |
| HarmonicFiredancer | 11 | 43 | +0.400 | +0.024 | 0.009 | 0.888 |
| JitoLabs | 17 | 67 | -0.051 | -0.027 | 0.700 | 0.827 |
| Raiku | 1 | 5 | -0.800 | -0.800 | 0.085 | 0.085 |
| Rakurai | 9 | 29 | +0.296 | +0.074 | 0.173 | 0.780 |
| Unknown(35988) | 2 | 6 | -0.333 | +0.000 | 0.513 | 1.000 |

## Landing and timing

Live timing uses live-only denominators. Dry-run timing is shown in separate columns so it cannot inflate a live rate. `on_time` means the per-tx estimated send slot was before `window_start`; `in_window_at_send` means the send was not after the window (`est_slot_at_send < window_start + 4`). The clearer `send_phase` column is `early` when `est_slot_at_send < window_start`, `inside` when it is in the four-slot window, and `late` otherwise.

| label | sent | live sent | landed | landing rate | live on_time | on_time rate | live in_window | in_window rate | mean live send_offset | dry sent | dry on_time | dry on_time rate | dry in_window | dry in_window rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agave | 40 | 40 | 39 | 0.975 | 40 | 1.000 | 40 | 1.000 | -1.625 | 0 | 0 | - | 0 | - |
| AgaveBam | 75 | 75 | 75 | 1.000 | 75 | 1.000 | 75 | 1.000 | -1.533 | 0 | 0 | - | 0 | - |
| FireBAM | 50 | 50 | 50 | 1.000 | 50 | 1.000 | 50 | 1.000 | -1.600 | 0 | 0 | - | 0 | - |
| Firedancer | 25 | 25 | 21 | 0.840 | 25 | 1.000 | 25 | 1.000 | -1.600 | 0 | 0 | - | 0 | - |
| Frankendancer | 50 | 50 | 48 | 0.960 | 50 | 1.000 | 50 | 1.000 | -1.500 | 0 | 0 | - | 0 | - |
| HarmonicAgave | 90 | 90 | 90 | 1.000 | 90 | 1.000 | 90 | 1.000 | -1.556 | 0 | 0 | - | 0 | - |
| HarmonicFiredancer | 60 | 60 | 60 | 1.000 | 60 | 1.000 | 60 | 1.000 | -1.417 | 0 | 0 | - | 0 | - |
| JitoLabs | 105 | 105 | 105 | 1.000 | 105 | 1.000 | 105 | 1.000 | -1.762 | 0 | 0 | - | 0 | - |
| Raiku | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -2.000 | 0 | 0 | - | 0 | - |
| Rakurai | 55 | 55 | 55 | 1.000 | 55 | 1.000 | 55 | 1.000 | -1.545 | 0 | 0 | - | 0 | - |
| Unknown(35988) | 10 | 10 | 10 | 1.000 | 10 | 1.000 | 10 | 1.000 | -1.000 | 0 | 0 | - | 0 | - |

### Landing by fee level (live only)

| cu_price (micro/CU) | live sent | landed | landing rate | live on_time | on_time rate |
|---|---|---|---|---|---|
| 0 | 113 | 111 | 0.982 | 113 | 1.000 |
| 1000 | 113 | 111 | 0.982 | 113 | 1.000 |
| 10000 | 113 | 112 | 0.991 | 113 | 1.000 |
| 100000 | 113 | 112 | 0.991 | 113 | 1.000 |
| 1000000 | 113 | 112 | 0.991 | 113 | 1.000 |

### Selected sample: our txs in the target window per burst

The primary test only uses groups with **at least 3** of our transactions co-landed in the target block. This table counts, for each live burst, how many of its transactions landed anywhere in the target window (not necessarily in the same block). Bursts with 0-2 are under-represented in the ordering tests. If higher-fee transactions also land more often, the primary sample is biased toward higher fees; that selection effect is a limitation, not a finding.

| label | live bursts | 0 | 1 | 2 | 3 | 4 | 5 | mean landed in target window |
|---|---|---|---|---|---|---|---|---|
| Agave | 8 | 6 | 0 | 0 | 0 | 0 | 2 | 1.25 |
| AgaveBam | 15 | 10 | 0 | 0 | 0 | 1 | 4 | 1.60 |
| FireBAM | 10 | 6 | 1 | 1 | 0 | 1 | 1 | 1.20 |
| Firedancer | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| Frankendancer | 10 | 6 | 0 | 0 | 0 | 0 | 4 | 2 |
| HarmonicAgave | 18 | 14 | 0 | 0 | 2 | 1 | 1 | 0.83 |
| HarmonicFiredancer | 12 | 3 | 0 | 0 | 0 | 4 | 5 | 3.42 |
| JitoLabs | 21 | 12 | 0 | 0 | 0 | 2 | 7 | 2.05 |
| Raiku | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |
| Rakurai | 11 | 10 | 0 | 0 | 0 | 0 | 1 | 0.45 |
| Unknown(35988) | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |

## Verified leader windows

Only windows whose `window_end` is before the current finalized slot count as verified. `leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that actually produced a block; `planned` = not yet elapsed, not counted as verified.

| label | windows | leaders_ok | windows with blocks | block_slots | planned |
|---|---|---|---|---|---|
| Agave | 14 | 14 | 14 | 56 | 21 |
| AgaveBam | 33 | 33 | 33 | 132 | 43 |
| FireBAM | 18 | 18 | 18 | 72 | 19 |
| Firedancer | 23 | 23 | 23 | 92 | 25 |
| Frankendancer | 13 | 13 | 13 | 52 | 17 |
| HarmonicAgave | 37 | 37 | 37 | 148 | 40 |
| HarmonicFiredancer | 34 | 34 | 34 | 136 | 35 |
| JitoLabs | 35 | 35 | 35 | 140 | 40 |
| Raiku | 4 | 4 | 4 | 16 | 4 |
| Rakurai | 27 | 27 | 27 | 108 | 30 |
| Unknown(35988) | 2 | 2 | 2 | 8 | 2 |

## Whole-block priority ordering (APPROXIMATION)

Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.
The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.
Positive tau = higher approximate priority fee appears earlier in the block.

| label | slots | mean tau_priority (approx) | non-vote txs |
|---|---|---|---|
| Agave | 23 | +0.037 | 5382 |
| AgaveBam | 39 | +0.007 | 9349 |
| FireBAM | 25 | +0.027 | 5522 |
| Firedancer | 10 | +0.011 | 2590 |
| Frankendancer | 23 | +0.022 | 4903 |
| HarmonicAgave | 48 | +0.044 | 14089 |
| HarmonicFiredancer | 26 | +0.018 | 5676 |
| JitoLabs | 48 | +0.008 | 13659 |
| Raiku | 1 | +0.071 | 203 |
| Rakurai | 27 | +0.022 | 7482 |
| Unknown(35988) | 5 | -0.021 | 1201 |

### Per-slot whole-block check

| slot | label | non-vote txs | tau_priority (approx) |
|---|---|---|---|
| 463681943 | FireBAM | 208 | -0.043 |
| 463681945 | FireBAM | 137 | +0.103 |
| 463681946 | FireBAM | 165 | +0.070 |
| 463681948 | FireBAM | 281 | +0.020 |
| 463682047 | Rakurai | 239 | +0.073 |
| 463682048 | Rakurai | 243 | +0.051 |
| 463682102 | HarmonicAgave | 261 | -0.025 |
| 463682103 | HarmonicAgave | 226 | +0.137 |
| 463682194 | Rakurai | 329 | +0.046 |
| 463682195 | Rakurai | 275 | -0.001 |
| 463682239 | Frankendancer | 192 | +0.132 |
| 463682326 | HarmonicFiredancer | 235 | +0.024 |
| 463682327 | HarmonicFiredancer | 226 | -0.230 |
| 463682328 | HarmonicFiredancer | 117 | -0.119 |
| 463682329 | HarmonicFiredancer | 220 | -0.001 |
| 463682435 | Firedancer | 297 | +0.167 |
| 463682436 | Firedancer | 366 | -0.143 |
| 463682438 | Firedancer | 249 | +0.021 |
| 463682498 | JitoLabs | 292 | +0.007 |
| 463682499 | JitoLabs | 427 | +0.078 |
| 463682665 | JitoLabs | 348 | -0.078 |
| 463682666 | JitoLabs | 282 | -0.013 |
| 463682718 | Firedancer | 359 | -0.134 |
| 463682854 | Frankendancer | 143 | +0.031 |
| 463682855 | Frankendancer | 167 | +0.065 |
| 463682857 | Frankendancer | 152 | +0.005 |
| 463682921 | Firedancer | 186 | +0.106 |
| 463682925 | Firedancer | 158 | +0.019 |
| 463683029 | JitoLabs | 205 | -0.194 |
| 463683031 | JitoLabs | 199 | -0.142 |
| 463683038 | JitoLabs | 161 | -0.141 |
| 463683132 | FireBAM | 194 | +0.026 |
| 463683133 | FireBAM | 167 | -0.067 |
| 463683352 | HarmonicFiredancer | 185 | +0.113 |
| 463683354 | HarmonicFiredancer | 201 | -0.111 |
| 463683419 | HarmonicAgave | 154 | -0.047 |
| 463683420 | HarmonicAgave | 194 | +0.195 |
| 463683466 | AgaveBam | 191 | +0.015 |
| 463683467 | AgaveBam | 200 | +0.086 |
| 463683570 | Agave | 221 | +0.179 |
| 463683571 | Agave | 165 | +0.016 |
| 463683572 | Agave | 268 | +0.070 |
| 463683654 | Agave | 181 | -0.032 |
| 463683656 | Agave | 175 | +0.174 |
| 463683657 | Agave | 180 | -0.036 |
| 463683658 | Agave | 222 | -0.060 |
| 463683730 | Rakurai | 179 | +0.052 |
| 463683731 | Rakurai | 176 | +0.055 |
| 463683732 | Rakurai | 181 | -0.240 |
| 463683785 | Frankendancer | 203 | +0.048 |
| 463683787 | Frankendancer | 222 | -0.026 |
| 463683845 | JitoLabs | 173 | +0.070 |
| 463683846 | JitoLabs | 193 | +0.058 |
| 463683907 | HarmonicAgave | 203 | +0.009 |
| 463683908 | HarmonicAgave | 151 | -0.017 |
| 463683909 | HarmonicAgave | 170 | -0.061 |
| 463683910 | HarmonicAgave | 145 | +0.041 |
| 463683941 | JitoLabs | 150 | -0.085 |
| 463683942 | JitoLabs | 189 | +0.001 |
| 463683943 | JitoLabs | 161 | -0.071 |
| 463684050 | JitoLabs | 296 | -0.025 |
| 463684051 | JitoLabs | 523 | -0.038 |
| 463684142 | AgaveBam | 190 | +0.046 |
| 463684143 | AgaveBam | 186 | -0.002 |
| 463684144 | AgaveBam | 188 | +0.047 |
| 463684230 | Agave | 227 | -0.052 |
| 463684231 | Agave | 316 | -0.172 |
| 463684232 | Agave | 362 | +0.147 |
| 463684270 | JitoLabs | 353 | -0.041 |
| 463684314 | Agave | 209 | -0.162 |
| 463684315 | Agave | 226 | -0.033 |
| 463684383 | AgaveBam | 414 | -0.047 |
| 463684384 | AgaveBam | 212 | -0.065 |
| 463684389 | AgaveBam | 336 | +0.025 |
| 463684442 | AgaveBam | 223 | +0.021 |
| 463684443 | AgaveBam | 280 | -0.213 |
| 463684445 | AgaveBam | 219 | +0.031 |
| 463684450 | AgaveBam | 222 | -0.006 |
| 463684539 | Frankendancer | 189 | +0.000 |
| 463684540 | Frankendancer | 171 | +0.102 |
| 463684615 | Rakurai | 261 | -0.015 |
| 463684616 | Rakurai | 648 | +0.189 |
| 463684681 | FireBAM | 271 | +0.020 |
| 463684682 | FireBAM | 199 | -0.042 |
| 463684683 | FireBAM | 194 | +0.050 |
| 463684684 | FireBAM | 241 | +0.221 |
| 463684718 | HarmonicFiredancer | 187 | -0.050 |
| 463684720 | HarmonicFiredancer | 221 | -0.037 |
| 463684759 | FireBAM | 172 | -0.003 |
| 463684760 | FireBAM | 204 | -0.216 |
| 463684843 | HarmonicAgave | 231 | +0.060 |
| 463684844 | HarmonicAgave | 582 | +0.085 |
| 463684845 | HarmonicAgave | 264 | -0.002 |
| 463684846 | HarmonicAgave | 246 | +0.113 |
| 463684871 | HarmonicAgave | 313 | +0.111 |
| 463684872 | HarmonicAgave | 366 | +0.159 |
| 463684922 | Agave | 246 | -0.028 |
| 463684924 | Agave | 201 | +0.102 |
| 463684926 | Agave | 255 | -0.013 |
| 463684970 | AgaveBam | 205 | +0.036 |
| 463684971 | AgaveBam | 231 | -0.050 |
| 463684975 | AgaveBam | 171 | -0.024 |
| 463685055 | HarmonicFiredancer | 271 | +0.157 |
| 463685056 | HarmonicFiredancer | 290 | +0.363 |
| 463685057 | HarmonicFiredancer | 243 | +0.037 |
| 463685091 | HarmonicAgave | 219 | -0.059 |
| 463685178 | JitoLabs | 201 | +0.115 |
| 463685179 | JitoLabs | 202 | +0.034 |
| 463685180 | JitoLabs | 226 | -0.053 |
| 463685374 | HarmonicAgave | 289 | +0.121 |
| 463685375 | HarmonicAgave | 324 | +0.097 |
| 463685431 | AgaveBam | 252 | -0.035 |
| 463685432 | AgaveBam | 194 | +0.130 |
| 463685433 | AgaveBam | 209 | +0.069 |
| 463685474 | JitoLabs | 317 | -0.025 |
| 463685475 | JitoLabs | 448 | -0.020 |
| 463685542 | AgaveBam | 235 | +0.072 |
| 463685543 | AgaveBam | 186 | +0.119 |
| 463685545 | AgaveBam | 243 | +0.106 |
| 463685571 | HarmonicFiredancer | 267 | +0.005 |
| 463685614 | AgaveBam | 200 | +0.086 |
| 463685615 | AgaveBam | 214 | +0.002 |
| 463685654 | HarmonicFiredancer | 212 | -0.003 |
| 463685655 | HarmonicFiredancer | 227 | +0.035 |
| 463685686 | HarmonicFiredancer | 205 | +0.154 |
| 463685687 | HarmonicFiredancer | 249 | -0.075 |
| 463685800 | AgaveBam | 314 | -0.002 |
| 463685801 | AgaveBam | 224 | +0.123 |
| 463685802 | AgaveBam | 239 | +0.075 |
| 463685854 | HarmonicAgave | 215 | +0.097 |
| 463685855 | HarmonicAgave | 192 | +0.032 |
| 463685856 | HarmonicAgave | 345 | +0.179 |
| 463685875 | HarmonicFiredancer | 196 | -0.036 |
| 463685953 | FireBAM | 314 | +0.034 |
| 463685954 | FireBAM | 195 | +0.102 |
| 463685955 | FireBAM | 150 | +0.078 |
| 463685956 | FireBAM | 171 | +0.003 |
| 463686086 | JitoLabs | 377 | +0.014 |
| 463686087 | JitoLabs | 427 | +0.095 |
| 463686088 | JitoLabs | 286 | +0.116 |
| 463686089 | JitoLabs | 325 | +0.018 |
| 463686090 | JitoLabs | 237 | +0.023 |
| 463686165 | AgaveBam | 201 | +0.020 |
| 463686166 | AgaveBam | 212 | -0.148 |
| 463686167 | AgaveBam | 221 | -0.106 |
| 463686356 | JitoLabs | 280 | -0.087 |
| 463686357 | JitoLabs | 207 | -0.081 |
| 463686358 | JitoLabs | 259 | -0.029 |
| 463686379 | Raiku | 203 | +0.071 |
| 463686415 | Agave | 219 | +0.319 |
| 463686470 | FireBAM | 233 | -0.044 |
| 463686471 | FireBAM | 243 | +0.011 |
| 463686591 | HarmonicAgave | 264 | +0.153 |
| 463686592 | HarmonicAgave | 480 | -0.044 |
| 463686593 | HarmonicAgave | 368 | +0.093 |
| 463686629 | Frankendancer | 140 | -0.169 |
| 463686630 | Frankendancer | 223 | +0.000 |
| 463686659 | HarmonicFiredancer | 255 | -0.008 |
| 463686660 | HarmonicFiredancer | 131 | -0.008 |
| 463686746 | Rakurai | 192 | -0.120 |
| 463686747 | Rakurai | 217 | +0.046 |
| 463686749 | Rakurai | 160 | +0.077 |
| 463686751 | Rakurai | 505 | +0.172 |
| 463687019 | Rakurai | 302 | -0.033 |
| 463687020 | Rakurai | 241 | +0.236 |
| 463687041 | JitoLabs | 281 | -0.018 |
| 463687042 | JitoLabs | 322 | -0.123 |
| 463687075 | JitoLabs | 386 | -0.007 |
| 463687076 | JitoLabs | 145 | -0.032 |
| 463687279 | Unknown(35988) | 213 | -0.095 |
| 463687280 | Unknown(35988) | 228 | -0.018 |
| 463687387 | Frankendancer | 220 | -0.099 |
| 463687388 | Frankendancer | 222 | +0.057 |
| 463687389 | Frankendancer | 258 | +0.120 |
| 463687390 | Frankendancer | 215 | +0.082 |
| 463687419 | Frankendancer | 238 | -0.009 |
| 463687454 | FireBAM | 170 | -0.016 |
| 463687514 | HarmonicAgave | 366 | +0.122 |
| 463687515 | HarmonicAgave | 348 | -0.063 |
| 463687516 | HarmonicAgave | 423 | -0.023 |
| 463687591 | Unknown(35988) | 392 | -0.121 |
| 463687592 | Unknown(35988) | 175 | +0.011 |
| 463687593 | Unknown(35988) | 193 | +0.116 |
| 463687687 | HarmonicAgave | 288 | -0.034 |
| 463687688 | HarmonicAgave | 231 | +0.113 |
| 463687689 | HarmonicAgave | 232 | +0.055 |
| 463687691 | HarmonicAgave | 291 | -0.015 |
| 463687693 | HarmonicAgave | 229 | +0.060 |
| 463687775 | HarmonicAgave | 426 | +0.077 |
| 463687776 | HarmonicAgave | 573 | -0.165 |
| 463687778 | HarmonicAgave | 355 | +0.035 |
| 463687842 | AgaveBam | 220 | +0.021 |
| 463687843 | AgaveBam | 275 | -0.061 |
| 463687926 | HarmonicAgave | 218 | -0.081 |
| 463687927 | HarmonicAgave | 556 | +0.283 |
| 463688090 | Agave | 189 | -0.037 |
| 463688091 | Agave | 251 | +0.055 |
| 463688092 | Agave | 259 | +0.202 |
| 463688093 | Agave | 204 | +0.185 |
| 463688147 | HarmonicAgave | 439 | +0.028 |
| 463688148 | HarmonicAgave | 200 | +0.084 |
| 463688149 | HarmonicAgave | 255 | +0.044 |
| 463688175 | JitoLabs | 268 | +0.075 |
| 463688256 | Rakurai | 298 | +0.066 |
| 463688257 | Rakurai | 275 | -0.108 |
| 463688258 | Rakurai | 256 | +0.083 |
| 463688294 | Rakurai | 206 | -0.092 |
| 463688295 | Rakurai | 292 | -0.099 |
| 463688356 | HarmonicAgave | 298 | +0.048 |
| 463688357 | HarmonicAgave | 194 | +0.055 |
| 463688442 | JitoLabs | 159 | +0.076 |
| 463688443 | JitoLabs | 155 | -0.013 |
| 463688444 | JitoLabs | 316 | +0.097 |
| 463688486 | JitoLabs | 292 | +0.016 |
| 463689265 | Rakurai | 307 | +0.086 |
| 463689266 | Rakurai | 290 | -0.116 |
| 463689787 | JitoLabs | 363 | -0.019 |
| 463689822 | HarmonicFiredancer | 197 | +0.028 |
| 463689823 | HarmonicFiredancer | 218 | -0.122 |
| 463689824 | HarmonicFiredancer | 137 | +0.026 |
| 463689915 | Firedancer | 226 | -0.027 |
| 463689916 | Firedancer | 280 | +0.059 |
| 463689951 | JitoLabs | 213 | +0.091 |
| 463689994 | Frankendancer | 284 | +0.008 |
| 463690067 | FireBAM | 217 | +0.072 |
| 463690068 | FireBAM | 187 | +0.065 |
| 463690099 | HarmonicFiredancer | 232 | +0.053 |
| 463690100 | HarmonicFiredancer | 277 | +0.209 |
| 463690235 | Rakurai | 242 | -0.041 |
| 463690236 | Rakurai | 428 | +0.052 |
| 463690237 | Rakurai | 325 | -0.025 |
| 463690347 | Rakurai | 147 | +0.088 |
| 463690348 | Rakurai | 268 | +0.106 |
| 463690434 | Frankendancer | 185 | +0.029 |
| 463690436 | Frankendancer | 224 | +0.023 |
| 463690437 | Frankendancer | 202 | +0.061 |
| 463690438 | Frankendancer | 228 | -0.088 |
| 463690495 | Agave | 301 | -0.109 |
| 463690496 | Agave | 308 | +0.109 |
| 463690497 | Agave | 197 | +0.033 |
| 463690565 | Firedancer | 255 | +0.026 |
| 463690566 | Firedancer | 214 | +0.018 |
| 463690621 | AgaveBam | 299 | -0.019 |
| 463690622 | AgaveBam | 317 | -0.059 |
| 463690623 | AgaveBam | 310 | -0.005 |
| 463690651 | JitoLabs | 285 | +0.050 |
| 463690652 | JitoLabs | 499 | +0.150 |
| 463690741 | HarmonicAgave | 250 | +0.014 |
| 463690742 | HarmonicAgave | 225 | +0.017 |
| 463690743 | HarmonicAgave | 185 | -0.019 |
| 463690767 | HarmonicAgave | 360 | -0.176 |
| 463690768 | HarmonicAgave | 472 | +0.159 |
| 463690892 | JitoLabs | 578 | +0.168 |
| 463690893 | JitoLabs | 269 | +0.100 |
| 463690894 | JitoLabs | 225 | +0.095 |
| 463690895 | JitoLabs | 240 | +0.012 |
| 463691102 | Frankendancer | 211 | -0.041 |
| 463691103 | Frankendancer | 261 | +0.019 |
| 463691104 | Frankendancer | 353 | +0.149 |
| 463691135 | HarmonicAgave | 206 | -0.060 |
| 463691136 | HarmonicAgave | 267 | +0.108 |
| 463691174 | HarmonicFiredancer | 212 | +0.077 |
| 463691175 | HarmonicFiredancer | 265 | -0.016 |
| 463691203 | AgaveBam | 268 | +0.063 |
| 463691314 | JitoLabs | 282 | +0.033 |
| 463691315 | JitoLabs | 246 | +0.000 |
| 463691316 | JitoLabs | 391 | +0.103 |
| 463691351 | FireBAM | 262 | +0.027 |
| 463691352 | FireBAM | 318 | +0.052 |
| 463691353 | FireBAM | 249 | +0.059 |
| 463691393 | AgaveBam | 248 | -0.001 |
| 463691472 | FireBAM | 380 | +0.103 |
| 463692225 | AgaveBam | 251 | +0.082 |
| 463692226 | AgaveBam | 269 | -0.119 |
| 463692227 | AgaveBam | 280 | -0.042 |
