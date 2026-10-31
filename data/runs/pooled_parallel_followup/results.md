# obp results

- Analysis generated (UTC): 2026-10-31T13:39:58Z
- Measurement send window (UTC): 2026-10-31T12:04:42Z to 2026-10-31T13:30:14Z
- Plan created (UTC): n/a
- Rows: sent=1105, landed=1062, block_txs=147209

Positive tau means higher fee (or earlier send order) appears earlier in the block.
Permutation p-values use a two-sided null; small samples give weak evidence.

## Test plan: primary vs exploratory

**Pre-registered primary test:** pooled `tau_fee` per client label on the **same-payer** arm, using only **ascending + shuffled** bursts and only rows with `in_target_window=True` and `leader_is_target=True`. Descending bursts are excluded from the primary test because there fee order equals send order (confounded); desc is a consistency check only. Holm correction is applied across the per-label primary p-values below, separately for H1 (fee) and H2 (send).

Everything else (multi-payer arm, descending mode, per-burst, whole-block, landing rates) is **exploratory**. Groups with fewer than 3 of our transactions in the same block are dropped. That selection can bias the ordering sample toward bursts whose higher-fee transactions land more often (see the target-window landing distribution below). With a five-transaction burst the smallest attainable two-sided per-burst permutation p is 1/60 ≈ 0.017; pooled tests use 2000 permutations, so their floor is 0.0005.

## Verdict per label (H1 / H2 / H0)

All verdict inputs use the same-payer arm only. H1 = pooled tau_fee > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_fee > 0 in ascending bursts alone. H2 = pooled tau_send > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_send > 0 in ascending bursts alone. If both hold the verdict is **mixed**; if neither holds it is **no rule detected (H0 not rejected)**; zero primary groups gives **insufficient data**. Descending bursts are a consistency check only.

| label | primary bursts (asc+shuffle, same arm) | primary txs | tau_fee (same arm) | p_fee | Holm p_fee | Holm p_send | verdict | mode evidence |
|---|---|---|---|---|---|---|---|---|
| Agave | 1 | 3 | +0.333 | 1.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=+0.333 p=1.000 tau_send=-0.333 p=1.000; desc (consistency only): tau_fee=-0.333 p=1.000 tau_send=-0.333 p=1.000 |
| AgaveBam | 3 | 13 | +0.578 | 0.029 | 0.174 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.367 p=0.303 tau_send=-0.367 p=0.303; asc+shuffle (primary): tau_fee=+0.578 p=0.029 tau_send=-0.022 p=0.951 |
| FireBAM | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=-; desc (consistency only): tau_fee=+1.000 p=0.332 tau_send=+1.000 p=0.332 |
| Firedancer | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=- |
| Frankendancer | 1 | 3 | -0.333 | 1.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=-0.333 p=1.000 tau_send=-1.000 p=0.334; desc (consistency only): tau_fee=-0.267 p=0.464 tau_send=-0.267 p=0.444 |
| HarmonicAgave | 1 | 5 | +0.000 | 1.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=+0.000 p=1.000 tau_send=+0.600 p=0.228; desc (consistency only): tau_fee=+0.333 p=1.000 tau_send=+0.333 p=1.000 |
| HarmonicFiredancer | 6 | 25 | +0.500 | 0.009 | 0.060 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.556 p=0.041 tau_send=-0.444 p=0.096; asc+shuffle (primary): tau_fee=+0.500 p=0.009 tau_send=-0.222 p=0.259; desc (consistency only): tau_fee=+1.000 p=0.332 tau_send=+1.000 p=0.332 |
| JitoLabs | 5 | 21 | +0.213 | 0.347 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.133 p=0.694 tau_send=-0.133 p=0.694; asc+shuffle (primary): tau_fee=+0.213 p=0.347 tau_send=-0.107 p=0.633; desc (consistency only): tau_fee=+0.183 p=0.536 tau_send=+0.183 p=0.536 |
| Raiku | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=-; desc (consistency only): tau_fee=-0.800 p=0.085 tau_send=-0.800 p=0.085 |
| Rakurai | 1 | 3 | +0.333 | 1.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=+0.333 p=1.000 tau_send=-1.000 p=0.334; desc (consistency only): tau_fee=+0.333 p=0.544 tau_send=+0.333 p=0.544 |

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
| Agave | 7QQGNm3p | multi | 463700099 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| Agave | 5Us18hLZ | multi | 463700388 | 3 | +0.333 | 1.000 | -1.000 | 0.354 |
| HarmonicFiredancer | 6yFGGAgY | same | 463700564 | 4 | +0.667 | 0.345 | -0.333 | 0.751 |
| Agave | 7QQGNm3p | multi | 463700965 | 3 | -1.000 | 0.340 | +1.000 | 0.330 |
| Rakurai | ana2y2Yv | same | 463701279 | 3 | +0.333 | 1.000 | -1.000 | 0.335 |
| Rakurai | 7PdKhpKz | same | 463701413 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |
| Frankendancer | FBbqKvwL | same | 463701720 | 4 | -0.333 | 0.757 | -0.333 | 0.750 |
| JitoLabs | GnC339vk | multi | 463702042 | 3 | +0.333 | 1.000 | -1.000 | 0.335 |
| Firedancer | 4VRs6A9z | multi | 463702191 | 3 | -1.000 | 0.335 | -1.000 | 0.326 |
| HarmonicAgave | 3psxMyr7 | multi | 463702488 | 4 | +0.333 | 0.760 | +0.333 | 0.758 |
| HarmonicFiredancer | Awes4Tr6 | same | 463702579 | 4 | -0.333 | 0.761 | -0.333 | 0.751 |
| Frankendancer | FBbqKvwL | multi | 463703135 | 3 | -1.000 | 0.308 | -1.000 | 0.335 |
| JitoLabs | 5pPRHnie | same | 463703538 | 3 | +1.000 | 0.333 | +1.000 | 0.323 |
| JitoLabs | GnC339vk | same | 463703665 | 5 | +0.000 | 1.000 | -0.800 | 0.080 |
| Agave | 5Us18hLZ | same | 463704443 | 3 | +0.333 | 1.000 | -0.333 | 1.000 |
| HarmonicAgave | 3psxMyr7 | multi | 463704499 | 3 | -0.333 | 1.000 | +0.333 | 1.000 |
| Frankendancer | FBbqKvwL | multi | 463704596 | 3 | +0.333 | 1.000 | -1.000 | 0.340 |
| JitoLabs | C8Bey3LK | same | 463704659 | 3 | +0.333 | 1.000 | -0.333 | 1.000 |
| Agave | mds4GEui | multi | 463704704 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| JitoLabs | 5pPRHnie | same | 463704798 | 4 | +0.667 | 0.326 | +0.667 | 0.333 |
| HarmonicAgave | Hz5aLvpK | same | 463704984 | 5 | +0.000 | 1.000 | +0.600 | 0.225 |
| Rakurai | ana2y2Yv | same | 463705147 | 4 | +0.333 | 0.755 | +0.333 | 0.762 |
| HarmonicFiredancer | Awes4Tr6 | same | 463705239 | 4 | +0.333 | 0.747 | -0.333 | 0.774 |
| FireBAM | LA1NEzry | same | 463705494 | 3 | +1.000 | 0.336 | +1.000 | 0.324 |
| FireBAM | LA1NEzry | multi | 463705615 | 3 | +1.000 | 0.325 | +0.333 | 1.000 |
| HarmonicFiredancer | DrifTrN9 | multi | 463705826 | 3 | +0.333 | 1.000 | +1.000 | 0.341 |

## Pooled per client label (primary: target window and target leader)

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 7 | 23 | -0.248 | -0.248 | 0.275 | 0.288 |
| AgaveBam | 5 | 21 | +0.667 | -0.067 | 0.002 | 0.751 |
| FireBAM | 4 | 15 | +0.150 | +0.117 | 0.613 | 0.664 |
| Firedancer | 1 | 3 | -1.000 | -1.000 | 0.332 | 0.332 |
| Frankendancer | 7 | 28 | +0.067 | -0.219 | 0.740 | 0.285 |
| HarmonicAgave | 7 | 27 | +0.143 | +0.010 | 0.485 | 0.983 |
| HarmonicFiredancer | 13 | 51 | +0.492 | -0.056 | 0.000 | 0.700 |
| JitoLabs | 14 | 57 | -0.024 | -0.048 | 0.847 | 0.740 |
| Raiku | 1 | 5 | -0.800 | -0.800 | 0.085 | 0.085 |
| Rakurai | 4 | 13 | +0.333 | -0.000 | 0.323 | 0.935 |

## Grouped results by payer arm and order mode (exploratory)

| label | grouped by | group | bursts | txs | mean tau_fee | pooled p_fee | mean tau_send | pooled p_send |
|---|---|---|---|---|---|---|---|---|
| Agave | payer_arm | multi | 5 | 17 | -0.347 | 0.220 | -0.213 | 0.440 |
| Agave | payer_arm | same | 2 | 6 | +0.000 | 1.000 | -0.333 | 0.729 |
| Agave | order_mode | asc | 1 | 3 | -1.000 | 0.332 | +1.000 | 0.332 |
| Agave | order_mode | desc | 2 | 6 | -0.333 | 0.720 | -0.333 | 0.720 |
| Agave | order_mode | shuffle | 4 | 14 | -0.017 | 0.977 | -0.517 | 0.095 |
| AgaveBam | payer_arm | multi | 2 | 8 | +0.800 | 0.043 | -0.133 | 0.790 |
| AgaveBam | payer_arm | same | 3 | 13 | +0.578 | 0.029 | -0.022 | 0.951 |
| AgaveBam | order_mode | asc | 3 | 14 | +0.444 | 0.081 | -0.444 | 0.081 |
| AgaveBam | order_mode | shuffle | 2 | 7 | +1.000 | 0.015 | +0.500 | 0.333 |
| FireBAM | payer_arm | multi | 3 | 12 | -0.133 | 0.683 | -0.178 | 0.591 |
| FireBAM | payer_arm | same | 1 | 3 | +1.000 | 0.332 | +1.000 | 0.332 |
| FireBAM | order_mode | desc | 3 | 10 | +0.333 | 0.439 | +0.222 | 0.537 |
| FireBAM | order_mode | shuffle | 1 | 5 | -0.400 | 0.484 | -0.200 | 0.812 |
| Firedancer | payer_arm | multi | 1 | 3 | -1.000 | 0.332 | -1.000 | 0.332 |
| Firedancer | order_mode | desc | 1 | 3 | -1.000 | 0.332 | -1.000 | 0.332 |
| Frankendancer | payer_arm | multi | 4 | 16 | +0.333 | 0.220 | +0.000 | 1.000 |
| Frankendancer | payer_arm | same | 3 | 12 | -0.289 | 0.373 | -0.511 | 0.097 |
| Frankendancer | order_mode | desc | 4 | 19 | +0.367 | 0.100 | +0.367 | 0.099 |
| Frankendancer | order_mode | shuffle | 3 | 9 | -0.333 | 0.561 | -1.000 | 0.004 |
| HarmonicAgave | payer_arm | multi | 5 | 19 | +0.133 | 0.591 | -0.173 | 0.511 |
| HarmonicAgave | payer_arm | same | 2 | 8 | +0.167 | 0.731 | +0.467 | 0.275 |
| HarmonicAgave | order_mode | asc | 3 | 10 | +0.111 | 0.683 | -0.333 | 0.447 |
| HarmonicAgave | order_mode | desc | 3 | 12 | +0.222 | 0.498 | +0.156 | 0.639 |
| HarmonicAgave | order_mode | shuffle | 1 | 5 | +0.000 | 1.000 | +0.600 | 0.228 |
| HarmonicFiredancer | payer_arm | multi | 6 | 23 | +0.400 | 0.067 | -0.067 | 0.776 |
| HarmonicFiredancer | payer_arm | same | 7 | 28 | +0.571 | 0.001 | -0.048 | 0.821 |
| HarmonicFiredancer | order_mode | asc | 5 | 21 | +0.467 | 0.022 | -0.400 | 0.063 |
| HarmonicFiredancer | order_mode | desc | 2 | 7 | +0.500 | 0.333 | +0.500 | 0.333 |
| HarmonicFiredancer | order_mode | shuffle | 6 | 23 | +0.511 | 0.018 | +0.044 | 0.843 |
| JitoLabs | payer_arm | multi | 5 | 21 | -0.427 | 0.056 | -0.173 | 0.460 |
| JitoLabs | payer_arm | same | 9 | 36 | +0.200 | 0.263 | +0.022 | 0.906 |
| JitoLabs | order_mode | asc | 5 | 21 | -0.120 | 0.600 | +0.120 | 0.600 |
| JitoLabs | order_mode | desc | 4 | 15 | +0.183 | 0.536 | +0.183 | 0.536 |
| JitoLabs | order_mode | shuffle | 5 | 21 | -0.093 | 0.674 | -0.400 | 0.075 |
| Raiku | payer_arm | same | 1 | 5 | -0.800 | 0.085 | -0.800 | 0.085 |
| Raiku | order_mode | desc | 1 | 5 | -0.800 | 0.085 | -0.800 | 0.085 |
| Rakurai | payer_arm | multi | 1 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |
| Rakurai | payer_arm | same | 3 | 10 | +0.333 | 0.427 | -0.111 | 0.673 |
| Rakurai | order_mode | desc | 3 | 10 | +0.333 | 0.423 | +0.333 | 0.423 |
| Rakurai | order_mode | shuffle | 1 | 3 | +0.333 | 1.000 | -1.000 | 0.334 |

## Sensitivity: all landed (any leader)

Same statistic as the primary pooled table, but using every landed row regardless of `in_target_window` or `leader_is_target`. This is exploratory and shows how much the result depends on the leader filter.

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 12 | 42 | -0.050 | -0.233 | 0.768 | 0.177 |
| AgaveBam | 20 | 76 | +0.250 | +0.020 | 0.049 | 0.862 |
| FireBAM | 11 | 41 | +0.012 | +0.091 | 0.947 | 0.584 |
| Firedancer | 7 | 24 | +0.086 | -0.257 | 0.690 | 0.248 |
| Frankendancer | 11 | 42 | +0.224 | +0.164 | 0.183 | 0.332 |
| HarmonicAgave | 19 | 69 | -0.028 | +0.046 | 0.839 | 0.721 |
| HarmonicFiredancer | 23 | 87 | +0.470 | -0.029 | 0.000 | 0.806 |
| JitoLabs | 27 | 101 | +0.104 | -0.109 | 0.319 | 0.314 |
| Raiku | 1 | 5 | -0.800 | -0.800 | 0.085 | 0.085 |
| Rakurai | 16 | 53 | +0.354 | -0.000 | 0.023 | 0.983 |
| Unknown(35988) | 2 | 6 | -0.333 | +0.000 | 0.513 | 1.000 |

## Landing and timing

Live timing uses live-only denominators. Dry-run timing is shown in separate columns so it cannot inflate a live rate. `on_time` means the per-tx estimated send slot was before `window_start`; `in_window_at_send` means the send was not after the window (`est_slot_at_send < window_start + 4`). The clearer `send_phase` column is `early` when `est_slot_at_send < window_start`, `inside` when it is in the four-slot window, and `late` otherwise.

| label | sent | live sent | landed | landing rate | live on_time | on_time rate | live in_window | in_window rate | mean live send_offset | dry sent | dry on_time | dry on_time rate | dry in_window | dry in_window rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agave | 90 | 90 | 84 | 0.933 | 90 | 1.000 | 90 | 1.000 | -3.333 | 0 | 0 | - | 0 | - |
| AgaveBam | 155 | 155 | 149 | 0.961 | 155 | 1.000 | 155 | 1.000 | -3.129 | 0 | 0 | - | 0 | - |
| FireBAM | 95 | 95 | 92 | 0.968 | 95 | 1.000 | 95 | 1.000 | -3.000 | 0 | 0 | - | 0 | - |
| Firedancer | 45 | 45 | 41 | 0.911 | 45 | 1.000 | 45 | 1.000 | -2.778 | 0 | 0 | - | 0 | - |
| Frankendancer | 85 | 85 | 81 | 0.953 | 85 | 1.000 | 85 | 1.000 | -2.529 | 0 | 0 | - | 0 | - |
| HarmonicAgave | 180 | 180 | 170 | 0.944 | 180 | 1.000 | 180 | 1.000 | -3.222 | 0 | 0 | - | 0 | - |
| HarmonicFiredancer | 140 | 140 | 137 | 0.979 | 140 | 1.000 | 140 | 1.000 | -3.143 | 0 | 0 | - | 0 | - |
| JitoLabs | 195 | 195 | 189 | 0.969 | 195 | 1.000 | 195 | 1.000 | -3.231 | 0 | 0 | - | 0 | - |
| JitoLabs+BAM | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -5.000 | 0 | 0 | - | 0 | - |
| Raiku | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -2.000 | 0 | 0 | - | 0 | - |
| Rakurai | 95 | 95 | 94 | 0.989 | 95 | 1.000 | 95 | 1.000 | -2.895 | 0 | 0 | - | 0 | - |
| Unknown(35988) | 10 | 10 | 10 | 1.000 | 10 | 1.000 | 10 | 1.000 | -1.000 | 0 | 0 | - | 0 | - |
| Unknown(55997) | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -5.000 | 0 | 0 | - | 0 | - |

### Landing by fee level (live only)

| cu_price (micro/CU) | live sent | landed | landing rate | live on_time | on_time rate |
|---|---|---|---|---|---|
| 0 | 221 | 206 | 0.932 | 221 | 1.000 |
| 1000 | 221 | 215 | 0.973 | 221 | 1.000 |
| 10000 | 221 | 218 | 0.986 | 221 | 1.000 |
| 100000 | 221 | 218 | 0.986 | 221 | 1.000 |
| 1000000 | 221 | 205 | 0.928 | 221 | 1.000 |

### Selected sample: our txs in the target window per burst

The primary test only uses groups with **at least 3** of our transactions co-landed in the target block. This table counts, for each live burst, how many of its transactions landed anywhere in the target window (not necessarily in the same block). Bursts with 0-2 are under-represented in the ordering tests. If higher-fee transactions also land more often, the primary sample is biased toward higher fees; that selection effect is a limitation, not a finding.

| label | live bursts | 0 | 1 | 2 | 3 | 4 | 5 | mean landed in target window |
|---|---|---|---|---|---|---|---|---|
| Agave | 18 | 10 | 0 | 0 | 5 | 1 | 2 | 1.61 |
| AgaveBam | 31 | 18 | 4 | 3 | 0 | 2 | 4 | 1.23 |
| FireBAM | 19 | 7 | 3 | 2 | 1 | 2 | 4 | 2 |
| Firedancer | 9 | 7 | 0 | 0 | 0 | 1 | 1 | 1 |
| Frankendancer | 17 | 8 | 1 | 1 | 0 | 2 | 5 | 2.12 |
| HarmonicAgave | 36 | 18 | 3 | 5 | 4 | 4 | 2 | 1.42 |
| HarmonicFiredancer | 28 | 9 | 3 | 1 | 1 | 6 | 8 | 2.57 |
| JitoLabs | 39 | 19 | 2 | 1 | 2 | 6 | 9 | 2.03 |
| JitoLabs+BAM | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 2 |
| Raiku | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |
| Rakurai | 19 | 14 | 0 | 1 | 0 | 2 | 2 | 1.05 |
| Unknown(35988) | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| Unknown(55997) | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 2 |

## Verified leader windows

Only windows whose `window_end` is before the current finalized slot count as verified. `leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that actually produced a block; `planned` = not yet elapsed, not counted as verified.

| label | windows | leaders_ok | windows with blocks | block_slots | planned |
|---|---|---|---|---|---|
| Agave | 26 | 26 | 26 | 104 | 78 |
| AgaveBam | 60 | 60 | 60 | 240 | 171 |
| FireBAM | 35 | 35 | 35 | 140 | 78 |
| Firedancer | 34 | 34 | 34 | 136 | 97 |
| Frankendancer | 24 | 24 | 24 | 96 | 76 |
| HarmonicAgave | 70 | 70 | 70 | 280 | 166 |
| HarmonicFiredancer | 66 | 66 | 66 | 264 | 148 |
| JitoLabs | 71 | 71 | 71 | 284 | 165 |
| JitoLabs+BAM | 2 | 2 | 2 | 8 | 15 |
| Raiku | 6 | 6 | 6 | 24 | 18 |
| Rakurai | 45 | 45 | 45 | 180 | 92 |
| Unknown(35988) | 2 | 2 | 2 | 8 | 2 |
| Unknown(55997) | 1 | 1 | 1 | 4 | 2 |

## Whole-block priority ordering (APPROXIMATION)

Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.
The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.
Positive tau = higher approximate priority fee appears earlier in the block.

| label | slots | mean tau_priority (approx) | non-vote txs |
|---|---|---|---|
| Agave | 45 | +0.024 | 10579 |
| AgaveBam | 76 | +0.014 | 19795 |
| FireBAM | 48 | +0.047 | 12320 |
| Firedancer | 18 | +0.011 | 5201 |
| Frankendancer | 40 | +0.035 | 10171 |
| HarmonicAgave | 96 | +0.015 | 30340 |
| HarmonicFiredancer | 64 | +0.018 | 15999 |
| JitoLabs | 93 | +0.009 | 25484 |
| JitoLabs+BAM | 4 | -0.018 | 1309 |
| Raiku | 1 | +0.071 | 203 |
| Rakurai | 46 | +0.011 | 12945 |
| Unknown(35988) | 5 | -0.021 | 1201 |
| Unknown(55997) | 3 | -0.002 | 839 |

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
