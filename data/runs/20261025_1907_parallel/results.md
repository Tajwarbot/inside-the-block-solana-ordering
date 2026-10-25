# obp results

- Analysis generated (UTC): 2026-10-25T19:24:00Z
- Measurement send window (UTC): 2026-10-25T19:07:36Z to 2026-10-25T19:22:39Z
- Plan created (UTC): 2026-10-25T19:07:29Z
- Rows: sent=330, landed=325, block_txs=31059

Positive tau means higher fee (or earlier send order) appears earlier in the block.
Permutation p-values use a two-sided null; small samples give weak evidence.

## Test plan: primary vs exploratory

**Pre-registered primary test:** pooled `tau_fee` per client label on the **same-payer** arm, using only **ascending + shuffled** bursts and only rows with `in_target_window=True` and `leader_is_target=True`. Descending bursts are excluded from the primary test because there fee order equals send order (confounded); desc is a consistency check only. Holm correction is applied across the per-label primary p-values below, separately for H1 (fee) and H2 (send).

Everything else (multi-payer arm, descending mode, per-burst, whole-block, landing rates) is **exploratory**. Groups with fewer than 3 of our transactions in the same block are dropped. That selection can bias the ordering sample toward bursts whose higher-fee transactions land more often (see the target-window landing distribution below). With a five-transaction burst the smallest attainable two-sided per-burst permutation p is 1/60 ≈ 0.017; pooled tests use 2000 permutations, so their floor is 0.0005.

## Verdict per label (H1 / H2 / H0)

All verdict inputs use the same-payer arm only. H1 = pooled tau_fee > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_fee > 0 in ascending bursts alone. H2 = pooled tau_send > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_send > 0 in ascending bursts alone. If both hold the verdict is **mixed**; if neither holds it is **no rule detected (H0 not rejected)**; zero primary groups gives **insufficient data**. Descending bursts are a consistency check only.

| label | primary bursts (asc+shuffle, same arm) | primary txs | tau_fee (same arm) | p_fee | Holm p_fee | Holm p_send | verdict | mode evidence |
|---|---|---|---|---|---|---|---|---|
| Agave | 1 | 3 | -1.000 | 0.332 | 0.996 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=-1.000 p=0.332 tau_send=+0.333 p=1.000; asc+shuffle (primary): tau_fee=-1.000 p=0.332 tau_send=+0.333 p=1.000 |
| AgaveBam | 2 | 10 | +1.000 | 0.000 | 0.000 | 1.000 | H1 fee rule | asc (primary): tau_fee=+1.000 p=0.013 tau_send=-1.000 p=0.013; asc+shuffle (primary): tau_fee=+1.000 p=0.000 tau_send=-0.200 p=0.541; desc (consistency only): tau_fee=+0.267 p=0.310 tau_send=+0.133 p=0.629 |
| FireBAM | 3 | 13 | +0.156 | 0.598 | 0.996 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.333 p=0.746 tau_send=-0.333 p=0.746; asc+shuffle (primary): tau_fee=+0.156 p=0.598 tau_send=-0.333 p=0.229 |
| Firedancer | 4 | 19 | +0.433 | 0.040 | 0.200 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.667 p=0.029 tau_send=-0.567 p=0.070; asc+shuffle (primary): tau_fee=+0.433 p=0.040 tau_send=-0.183 p=0.396 |
| HarmonicAgave | 3 | 15 | +0.867 | 0.000 | 0.000 | 0.654 | H1 fee rule | asc (primary): tau_fee=+0.800 p=0.085 tau_send=-0.800 p=0.085; asc+shuffle (primary): tau_fee=+0.867 p=0.000 tau_send=-0.400 p=0.093; desc (consistency only): tau_fee=+0.200 p=0.818 tau_send=+0.200 p=0.818 |
| HarmonicFiredancer | 4 | 19 | +0.417 | 0.060 | 0.240 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.300 p=0.403 tau_send=-0.200 p=0.610; asc+shuffle (primary): tau_fee=+0.417 p=0.060 tau_send=+0.100 p=0.631; desc (consistency only): tau_fee=+0.333 p=0.746 tau_send=+0.333 p=0.746 |
| JitoLabs | 4 | 20 | +0.200 | 0.400 | 0.996 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.400 p=0.221 tau_send=-0.400 p=0.221; asc+shuffle (primary): tau_fee=+0.200 p=0.400 tau_send=-0.150 p=0.535; desc (consistency only): tau_fee=+0.033 p=0.998 tau_send=+0.067 p=0.906 |
| Rakurai | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=-; desc (consistency only): tau_fee=+0.200 p=0.387 tau_send=+0.250 p=0.265 |

## Per-burst Kendall tau (primary: target window and target leader)

| label | target | arm | slot | n | tau_fee | p_fee | tau_send | p_send |
|---|---|---|---|---|---|---|---|---|
| FireBAM | 9jxgosAf | same | 461370097 | 4 | +0.333 | 0.746 | -0.333 | 0.726 |
| Firedancer | JD549Hsb | multi | 461370112 | 5 | +0.800 | 0.098 | +0.600 | 0.227 |
| Agave | rsbp8zMH | multi | 461370169 | 5 | -0.400 | 0.476 | +0.400 | 0.475 |
| Rakurai | E3mDbFMr | same | 461370204 | 5 | -0.200 | 0.809 | -0.200 | 0.831 |
| HarmonicAgave | BtsmiEEv | multi | 461370277 | 5 | +0.800 | 0.076 | +0.000 | 1.000 |
| HarmonicAgave | Fd7btgyS | multi | 461370353 | 5 | +0.000 | 1.000 | -0.200 | 0.822 |
| JitoLabs | C8Bey3LK | same | 461370373 | 5 | +0.200 | 0.823 | -0.200 | 0.815 |
| HarmonicFiredancer | 87CcUxpy | multi | 461370456 | 5 | +1.000 | 0.018 | -1.000 | 0.015 |
| AgaveBam | Fc6NNdS2 | same | 461370468 | 5 | +0.800 | 0.079 | +0.200 | 0.816 |
| Firedancer | JD549Hsb | multi | 461370500 | 5 | +0.600 | 0.222 | +0.400 | 0.493 |
| Firedancer | 9eGrDohd | multi | 461370630 | 5 | +0.200 | 0.822 | -0.400 | 0.490 |
| HarmonicFiredancer | 87CcUxpy | same | 461370733 | 5 | +0.400 | 0.479 | +0.800 | 0.085 |
| Firedancer | 9eGrDohd | multi | 461370833 | 5 | -0.200 | 0.815 | +0.200 | 0.823 |
| HarmonicFiredancer | 87CcUxpy | same | 461370893 | 4 | +0.333 | 0.735 | +0.333 | 0.768 |
| HarmonicAgave | Fd7btgyS | multi | 461370966 | 4 | +0.333 | 0.742 | +0.333 | 0.758 |
| AgaveBam | Fc6NNdS2 | same | 461371044 | 5 | +1.000 | 0.018 | -1.000 | 0.017 |
| Rakurai | ana2y2Yv | multi | 461371114 | 5 | +0.600 | 0.243 | +0.000 | 1.000 |
| Firedancer | JD549Hsb | same | 461371148 | 5 | +1.000 | 0.011 | +0.400 | 0.475 |
| HarmonicFiredancer | 6ptuwW4r | multi | 461371229 | 5 | +0.800 | 0.091 | -0.800 | 0.097 |
| JitoLabs | 5pPRHnie | same | 461371290 | 5 | +0.400 | 0.478 | -0.200 | 0.827 |
| AgaveBam | 6y7V8dL6 | multi | 461371405 | 5 | -0.200 | 0.815 | +0.800 | 0.090 |
| JitoLabs | C8Bey3LK | same | 461371421 | 5 | +0.200 | 0.805 | -0.200 | 0.812 |
| Firedancer | JD549Hsb | multi | 461371436 | 5 | +0.400 | 0.490 | +0.400 | 0.472 |
| FireBAM | 9jxgosAf | same | 461371557 | 5 | -0.200 | 0.822 | +0.000 | 1.000 |
| HarmonicAgave | Fd7btgyS | multi | 461371573 | 5 | +0.400 | 0.494 | -0.400 | 0.485 |
| AgaveBam | Fc6NNdS2 | same | 461371593 | 5 | +0.200 | 0.817 | +0.200 | 0.823 |
| HarmonicAgave | Fd7btgyS | same | 461371622 | 5 | +0.800 | 0.075 | -0.800 | 0.086 |
| Firedancer | 9eGrDohd | multi | 461371729 | 5 | +0.200 | 0.815 | +0.400 | 0.490 |
| HarmonicAgave | Fd7btgyS | same | 461371849 | 5 | +0.800 | 0.077 | -0.400 | 0.492 |
| FireBAM | 9jxgosAf | multi | 461371916 | 5 | +0.400 | 0.491 | -0.400 | 0.484 |
| Rakurai | ana2y2Yv | same | 461371956 | 5 | +0.400 | 0.483 | +0.400 | 0.497 |
| Agave | rsbp8zMH | multi | 461372021 | 5 | -0.800 | 0.082 | +0.000 | 1.000 |
| HarmonicFiredancer | 6ptuwW4r | same | 461372040 | 5 | +0.600 | 0.226 | -0.600 | 0.232 |
| AgaveBam | Fc6NNdS2 | multi | 461372101 | 5 | +0.000 | 1.000 | +0.000 | 1.000 |
| JitoLabs | 5pPRHnie | same | 461372178 | 5 | -0.200 | 0.815 | +0.400 | 0.500 |
| AgaveBam | 6y7V8dL6 | same | 461372245 | 5 | -0.200 | 0.823 | +0.000 | 1.000 |
| HarmonicAgave | BtsmiEEv | multi | 461372272 | 5 | +1.000 | 0.015 | -0.200 | 0.813 |
| JitoLabs | C8Bey3LK | same | 461372294 | 5 | +0.600 | 0.215 | -0.600 | 0.235 |
| Rakurai | ana2y2Yv | multi | 461372389 | 5 | +0.200 | 0.815 | +0.200 | 0.832 |
| AgaveBam | 6y7V8dL6 | same | 461372404 | 5 | +1.000 | 0.013 | +0.600 | 0.244 |
| Firedancer | 9eGrDohd | multi | 461372468 | 5 | +1.000 | 0.015 | -1.000 | 0.019 |
| HarmonicAgave | BtsmiEEv | same | 461372562 | 5 | +0.200 | 0.817 | +0.200 | 0.818 |
| HarmonicFiredancer | 87CcUxpy | multi | 461372694 | 3 | -1.000 | 0.339 | -0.333 | 1.000 |
| HarmonicFiredancer | 6ptuwW4r | same | 461372749 | 5 | +0.000 | 1.000 | +0.200 | 0.813 |
| Agave | 5Us18hLZ | multi | 461372821 | 5 | -0.600 | 0.244 | -0.400 | 0.494 |
| HarmonicAgave | Fd7btgyS | same | 461372845 | 5 | +1.000 | 0.015 | +0.000 | 1.000 |
| HarmonicAgave | Fd7btgyS | multi | 461372860 | 4 | +0.000 | 1.000 | +0.000 | 1.000 |
| Rakurai | ana2y2Yv | same | 461372942 | 5 | +0.400 | 0.474 | +0.600 | 0.229 |
| JitoLabs | 5pPRHnie | multi | 461372993 | 5 | +0.000 | 1.000 | -0.400 | 0.478 |
| Agave | 5Us18hLZ | same | 461373077 | 3 | -1.000 | 0.312 | +0.333 | 1.000 |
| Agave | rsbp8zMH | multi | 461373133 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| FireBAM | 9jxgosAf | same | 461373209 | 4 | +0.333 | 0.740 | -0.667 | 0.339 |
| HarmonicAgave | Fd7btgyS | multi | 461373232 | 5 | +1.000 | 0.014 | -1.000 | 0.015 |
| Rakurai | E3mDbFMr | same | 461373337 | 5 | +0.200 | 0.815 | +0.200 | 0.824 |
| AgaveBam | 6y7V8dL6 | multi | 461373397 | 5 | -0.600 | 0.226 | +0.000 | 1.000 |
| Firedancer | 9eGrDohd | same | 461373424 | 5 | +1.000 | 0.013 | -0.800 | 0.081 |
| HarmonicAgave | BtsmiEEv | multi | 461373522 | 4 | +0.667 | 0.337 | +0.667 | 0.338 |
| Firedancer | JD549Hsb | same | 461373656 | 5 | -0.600 | 0.241 | +0.000 | 1.000 |
| JitoLabs | 5pPRHnie | multi | 461373793 | 5 | +0.800 | 0.075 | -1.000 | 0.021 |
| AgaveBam | Fc6NNdS2 | multi | 461373908 | 5 | +0.200 | 0.829 | +0.400 | 0.509 |
| Firedancer | JD549Hsb | same | 461373993 | 4 | +0.333 | 0.755 | -0.333 | 0.766 |
| HarmonicFiredancer | 87CcUxpy | multi | 461374068 | 5 | +0.800 | 0.077 | +0.200 | 0.819 |
| HarmonicFiredancer | 6ptuwW4r | same | 461374141 | 4 | +0.667 | 0.334 | +0.000 | 1.000 |
| JitoLabs | C8Bey3LK | same | 461374261 | 3 | -0.333 | 1.000 | +0.333 | 1.000 |
| AgaveBam | Fc6NNdS2 | multi | 461374316 | 3 | +0.333 | 1.000 | -1.000 | 0.331 |

## Pooled per client label (primary: target window and target leader)

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 5 | 21 | -0.627 | +0.000 | 0.004 | 1.000 |
| AgaveBam | 10 | 48 | +0.253 | +0.020 | 0.067 | 0.877 |
| FireBAM | 4 | 18 | +0.217 | -0.350 | 0.331 | 0.118 |
| Firedancer | 11 | 54 | +0.430 | -0.012 | 0.001 | 0.930 |
| HarmonicAgave | 12 | 57 | +0.583 | -0.150 | 0.000 | 0.218 |
| HarmonicFiredancer | 9 | 41 | +0.400 | -0.133 | 0.009 | 0.408 |
| JitoLabs | 8 | 38 | +0.208 | -0.233 | 0.190 | 0.140 |
| Rakurai | 6 | 30 | +0.267 | +0.200 | 0.107 | 0.268 |

## Grouped results by payer arm and order mode (exploratory)

| label | grouped by | group | bursts | txs | mean tau_fee | pooled p_fee | mean tau_send | pooled p_send |
|---|---|---|---|---|---|---|---|---|
| Agave | payer_arm | multi | 4 | 18 | -0.533 | 0.027 | -0.083 | 0.756 |
| Agave | payer_arm | same | 1 | 3 | -1.000 | 0.332 | +0.333 | 1.000 |
| Agave | order_mode | asc | 2 | 8 | -0.700 | 0.086 | +0.367 | 0.405 |
| Agave | order_mode | desc | 2 | 8 | -0.467 | 0.266 | -0.367 | 0.415 |
| Agave | order_mode | shuffle | 1 | 5 | -0.800 | 0.081 | +0.000 | 1.000 |
| AgaveBam | payer_arm | multi | 5 | 23 | -0.053 | 0.832 | +0.040 | 0.853 |
| AgaveBam | payer_arm | same | 5 | 25 | +0.560 | 0.003 | +0.000 | 1.000 |
| AgaveBam | order_mode | asc | 1 | 5 | +1.000 | 0.013 | -1.000 | 0.013 |
| AgaveBam | order_mode | desc | 4 | 20 | +0.200 | 0.374 | +0.100 | 0.665 |
| AgaveBam | order_mode | shuffle | 5 | 23 | +0.147 | 0.490 | +0.160 | 0.476 |
| FireBAM | payer_arm | multi | 1 | 5 | +0.400 | 0.493 | -0.400 | 0.493 |
| FireBAM | payer_arm | same | 3 | 13 | +0.156 | 0.598 | -0.333 | 0.229 |
| FireBAM | order_mode | asc | 2 | 9 | +0.367 | 0.286 | -0.367 | 0.286 |
| FireBAM | order_mode | shuffle | 2 | 9 | +0.067 | 0.889 | -0.333 | 0.332 |
| Firedancer | payer_arm | multi | 7 | 35 | +0.429 | 0.006 | +0.086 | 0.588 |
| Firedancer | payer_arm | same | 4 | 19 | +0.433 | 0.040 | -0.183 | 0.396 |
| Firedancer | order_mode | asc | 4 | 19 | +0.533 | 0.015 | -0.483 | 0.030 |
| Firedancer | order_mode | desc | 4 | 20 | +0.400 | 0.061 | +0.250 | 0.258 |
| Firedancer | order_mode | shuffle | 3 | 15 | +0.333 | 0.209 | +0.267 | 0.307 |
| HarmonicAgave | payer_arm | multi | 8 | 37 | +0.525 | 0.000 | -0.100 | 0.532 |
| HarmonicAgave | payer_arm | same | 4 | 20 | +0.700 | 0.000 | -0.250 | 0.275 |
| HarmonicAgave | order_mode | asc | 4 | 19 | +0.550 | 0.009 | -0.550 | 0.009 |
| HarmonicAgave | order_mode | desc | 3 | 14 | +0.289 | 0.266 | +0.222 | 0.435 |
| HarmonicAgave | order_mode | shuffle | 5 | 24 | +0.787 | 0.000 | -0.053 | 0.793 |
| HarmonicFiredancer | payer_arm | multi | 4 | 18 | +0.400 | 0.091 | -0.483 | 0.039 |
| HarmonicFiredancer | payer_arm | same | 5 | 23 | +0.400 | 0.040 | +0.147 | 0.464 |
| HarmonicFiredancer | order_mode | asc | 4 | 20 | +0.600 | 0.005 | -0.550 | 0.009 |
| HarmonicFiredancer | order_mode | desc | 2 | 9 | +0.567 | 0.076 | +0.267 | 0.452 |
| HarmonicFiredancer | order_mode | shuffle | 3 | 12 | +0.022 | 0.977 | +0.156 | 0.651 |
| JitoLabs | payer_arm | multi | 2 | 10 | +0.400 | 0.234 | -0.700 | 0.018 |
| JitoLabs | payer_arm | same | 6 | 28 | +0.144 | 0.462 | -0.078 | 0.719 |
| JitoLabs | order_mode | asc | 3 | 15 | +0.533 | 0.028 | -0.600 | 0.009 |
| JitoLabs | order_mode | desc | 2 | 8 | +0.033 | 0.998 | +0.067 | 0.906 |
| JitoLabs | order_mode | shuffle | 3 | 15 | +0.000 | 1.000 | -0.067 | 0.854 |
| Rakurai | payer_arm | multi | 2 | 10 | +0.400 | 0.212 | +0.100 | 0.823 |
| Rakurai | payer_arm | same | 4 | 20 | +0.200 | 0.387 | +0.250 | 0.265 |
| Rakurai | order_mode | desc | 6 | 30 | +0.267 | 0.107 | +0.200 | 0.268 |

## Sensitivity: all landed (any leader)

Same statistic as the primary pooled table, but using every landed row regardless of `in_target_window` or `leader_is_target`. This is exploratory and shows how much the result depends on the leader filter.

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 5 | 21 | -0.627 | +0.000 | 0.004 | 1.000 |
| AgaveBam | 10 | 48 | +0.253 | +0.020 | 0.067 | 0.877 |
| FireBAM | 4 | 18 | +0.217 | -0.350 | 0.331 | 0.118 |
| Firedancer | 11 | 54 | +0.430 | -0.012 | 0.001 | 0.930 |
| HarmonicAgave | 12 | 57 | +0.583 | -0.150 | 0.000 | 0.218 |
| HarmonicFiredancer | 9 | 41 | +0.400 | -0.133 | 0.009 | 0.408 |
| JitoLabs | 8 | 38 | +0.208 | -0.233 | 0.190 | 0.140 |
| Rakurai | 6 | 30 | +0.267 | +0.200 | 0.107 | 0.268 |

## Landing and timing

Live timing uses live-only denominators. Dry-run timing is shown in separate columns so it cannot inflate a live rate. `on_time` means the per-tx estimated send slot was before `window_start`; `in_window_at_send` means the send was not after the window (`est_slot_at_send < window_start + 4`). The clearer `send_phase` column is `early` when `est_slot_at_send < window_start`, `inside` when it is in the four-slot window, and `late` otherwise.

| label | sent | live sent | landed | landing rate | live on_time | on_time rate | live in_window | in_window rate | mean live send_offset | dry sent | dry on_time | dry on_time rate | dry in_window | dry in_window rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agave | 25 | 25 | 25 | 1.000 | 25 | 1.000 | 25 | 1.000 | -2.000 | 0 | 0 | - | 0 | - |
| AgaveBam | 50 | 50 | 50 | 1.000 | 50 | 1.000 | 50 | 1.000 | -1.900 | 0 | 0 | - | 0 | - |
| FireBAM | 20 | 20 | 20 | 1.000 | 20 | 1.000 | 20 | 1.000 | -2.000 | 0 | 0 | - | 0 | - |
| Firedancer | 55 | 55 | 55 | 1.000 | 55 | 1.000 | 55 | 1.000 | -1.909 | 0 | 0 | - | 0 | - |
| HarmonicAgave | 60 | 60 | 59 | 0.983 | 60 | 1.000 | 60 | 1.000 | -1.833 | 0 | 0 | - | 0 | - |
| HarmonicFiredancer | 50 | 50 | 47 | 0.940 | 50 | 1.000 | 50 | 1.000 | -2.000 | 0 | 0 | - | 0 | - |
| JitoLabs | 40 | 40 | 39 | 0.975 | 40 | 1.000 | 40 | 1.000 | -1.750 | 0 | 0 | - | 0 | - |
| Rakurai | 30 | 30 | 30 | 1.000 | 30 | 1.000 | 30 | 1.000 | -1.667 | 0 | 0 | - | 0 | - |

### Landing by fee level (live only)

| cu_price (micro/CU) | live sent | landed | landing rate | live on_time | on_time rate |
|---|---|---|---|---|---|
| 0 | 66 | 65 | 0.985 | 66 | 1.000 |
| 1000 | 66 | 65 | 0.985 | 66 | 1.000 |
| 10000 | 66 | 65 | 0.985 | 66 | 1.000 |
| 100000 | 66 | 65 | 0.985 | 66 | 1.000 |
| 1000000 | 66 | 65 | 0.985 | 66 | 1.000 |

### Selected sample: our txs in the target window per burst

The primary test only uses groups with **at least 3** of our transactions co-landed in the target block. This table counts, for each live burst, how many of its transactions landed anywhere in the target window (not necessarily in the same block). Bursts with 0-2 are under-represented in the ordering tests. If higher-fee transactions also land more often, the primary sample is biased toward higher fees; that selection effect is a limitation, not a finding.

| label | live bursts | 0 | 1 | 2 | 3 | 4 | 5 | mean landed in target window |
|---|---|---|---|---|---|---|---|---|
| Agave | 5 | 0 | 0 | 0 | 0 | 0 | 5 | 5 |
| AgaveBam | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 5 |
| FireBAM | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 5 |
| Firedancer | 11 | 0 | 0 | 0 | 0 | 0 | 11 | 5 |
| HarmonicAgave | 12 | 0 | 0 | 0 | 0 | 1 | 11 | 4.92 |
| HarmonicFiredancer | 10 | 0 | 0 | 1 | 0 | 0 | 9 | 4.70 |
| JitoLabs | 8 | 0 | 0 | 0 | 0 | 1 | 7 | 4.88 |
| Rakurai | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 5 |

## Verified leader windows

Only windows whose `window_end` is before the current finalized slot count as verified. `leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that actually produced a block; `planned` = not yet elapsed, not counted as verified.

| label | windows | leaders_ok | windows with blocks | block_slots | planned |
|---|---|---|---|---|---|
| Agave | 5 | 5 | 5 | 20 | 2 |
| AgaveBam | 12 | 12 | 12 | 48 | 2 |
| FireBAM | 6 | 6 | 6 | 24 | 1 |
| Firedancer | 12 | 12 | 12 | 48 | 2 |
| HarmonicAgave | 13 | 13 | 13 | 52 | 2 |
| HarmonicFiredancer | 11 | 11 | 11 | 44 | 4 |
| JitoLabs | 12 | 12 | 12 | 48 | 3 |
| Rakurai | 7 | 7 | 7 | 28 | 2 |

## Whole-block priority ordering (APPROXIMATION)

Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.
The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.
Positive tau = higher approximate priority fee appears earlier in the block.

| label | slots | mean tau_priority (approx) | non-vote txs |
|---|---|---|---|
| Agave | 7 | +0.031 | 2536 |
| AgaveBam | 11 | +0.058 | 4297 |
| FireBAM | 6 | +0.027 | 2145 |
| Firedancer | 12 | -0.091 | 6187 |
| HarmonicAgave | 14 | +0.001 | 5551 |
| HarmonicFiredancer | 13 | +0.032 | 5545 |
| JitoLabs | 9 | +0.008 | 3105 |
| Rakurai | 6 | +0.003 | 1535 |

### Per-slot whole-block check

| slot | label | non-vote txs | tau_priority (approx) |
|---|---|---|---|
| 461370096 | FireBAM | 324 | +0.094 |
| 461370097 | FireBAM | 380 | +0.010 |
| 461370112 | Firedancer | 547 | -0.170 |
| 461370169 | Agave | 338 | +0.012 |
| 461370204 | Rakurai | 111 | +0.024 |
| 461370277 | HarmonicAgave | 359 | -0.020 |
| 461370353 | HarmonicAgave | 344 | -0.020 |
| 461370373 | JitoLabs | 348 | -0.013 |
| 461370456 | HarmonicFiredancer | 553 | -0.103 |
| 461370468 | AgaveBam | 532 | +0.258 |
| 461370500 | Firedancer | 806 | -0.114 |
| 461370630 | Firedancer | 467 | +0.053 |
| 461370733 | HarmonicFiredancer | 392 | -0.003 |
| 461370833 | Firedancer | 433 | +0.042 |
| 461370892 | HarmonicFiredancer | 338 | -0.013 |
| 461370893 | HarmonicFiredancer | 288 | +0.071 |
| 461370965 | HarmonicAgave | 396 | +0.063 |
| 461370966 | HarmonicAgave | 334 | +0.026 |
| 461371044 | AgaveBam | 335 | +0.032 |
| 461371114 | Rakurai | 296 | -0.028 |
| 461371148 | Firedancer | 609 | -0.185 |
| 461371229 | HarmonicFiredancer | 255 | -0.025 |
| 461371290 | JitoLabs | 314 | +0.092 |
| 461371405 | AgaveBam | 235 | -0.098 |
| 461371421 | JitoLabs | 358 | -0.021 |
| 461371436 | Firedancer | 531 | -0.170 |
| 461371557 | FireBAM | 475 | +0.058 |
| 461371573 | HarmonicAgave | 507 | +0.034 |
| 461371593 | AgaveBam | 413 | +0.057 |
| 461371622 | HarmonicAgave | 326 | -0.021 |
| 461371729 | Firedancer | 423 | +0.066 |
| 461371849 | HarmonicAgave | 316 | -0.012 |
| 461371916 | FireBAM | 345 | -0.086 |
| 461371956 | Rakurai | 121 | +0.009 |
| 461372021 | Agave | 336 | +0.004 |
| 461372040 | HarmonicFiredancer | 635 | +0.055 |
| 461372101 | AgaveBam | 659 | -0.050 |
| 461372178 | JitoLabs | 497 | -0.054 |
| 461372245 | AgaveBam | 351 | +0.007 |
| 461372272 | HarmonicAgave | 360 | -0.026 |
| 461372294 | JitoLabs | 369 | +0.013 |
| 461372389 | Rakurai | 334 | +0.008 |
| 461372404 | AgaveBam | 266 | +0.099 |
| 461372468 | Firedancer | 437 | +0.057 |
| 461372562 | HarmonicAgave | 503 | +0.010 |
| 461372693 | HarmonicFiredancer | 550 | +0.122 |
| 461372694 | HarmonicFiredancer | 247 | +0.102 |
| 461372749 | HarmonicFiredancer | 595 | +0.175 |
| 461372821 | Agave | 326 | +0.028 |
| 461372845 | HarmonicAgave | 513 | -0.048 |
| 461372860 | HarmonicAgave | 373 | -0.001 |
| 461372861 | HarmonicAgave | 448 | +0.039 |
| 461372942 | Rakurai | 316 | -0.017 |
| 461372993 | JitoLabs | 352 | +0.039 |
| 461373076 | Agave | 490 | +0.111 |
| 461373077 | Agave | 404 | +0.027 |
| 461373132 | Agave | 336 | +0.062 |
| 461373133 | Agave | 306 | -0.026 |
| 461373209 | FireBAM | 300 | +0.043 |
| 461373210 | FireBAM | 321 | +0.041 |
| 461373232 | HarmonicAgave | 405 | +0.007 |
| 461373337 | Rakurai | 357 | +0.024 |
| 461373397 | AgaveBam | 327 | +0.028 |
| 461373424 | Firedancer | 611 | -0.159 |
| 461373522 | HarmonicAgave | 367 | -0.026 |
| 461373656 | Firedancer | 552 | -0.253 |
| 461373793 | JitoLabs | 312 | +0.059 |
| 461373836 | HarmonicFiredancer | 315 | +0.046 |
| 461373908 | AgaveBam | 573 | +0.279 |
| 461373992 | Firedancer | 451 | -0.185 |
| 461373993 | Firedancer | 320 | -0.077 |
| 461374068 | HarmonicFiredancer | 516 | -0.023 |
| 461374140 | HarmonicFiredancer | 543 | -0.009 |
| 461374141 | HarmonicFiredancer | 318 | +0.022 |
| 461374261 | JitoLabs | 280 | -0.005 |
| 461374262 | JitoLabs | 275 | -0.041 |
| 461374316 | AgaveBam | 348 | +0.095 |
| 461374317 | AgaveBam | 258 | -0.070 |
