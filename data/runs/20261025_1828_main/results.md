# obp results

- Analysis generated (UTC): 2026-10-25T19:06:17Z
- Measurement send window (UTC): 2026-10-25T18:28:40Z to 2026-10-25T18:59:20Z
- Plan created (UTC): 2026-10-25T18:28:32Z
- Rows: sent=625, landed=625, block_txs=142740

Positive tau means higher fee (or earlier send order) appears earlier in the block.
Permutation p-values use a two-sided null; small samples give weak evidence.

## Test plan: primary vs exploratory

**Pre-registered primary test:** pooled `tau_fee` per client label on the **same-payer** arm, using only **ascending + shuffled** bursts and only rows with `in_target_window=True` and `leader_is_target=True`. Descending bursts are excluded from the primary test because there fee order equals send order (confounded); desc is a consistency check only. Holm correction is applied across the per-label primary p-values below, separately for H1 (fee) and H2 (send).

Everything else (multi-payer arm, descending mode, per-burst, whole-block, landing rates) is **exploratory**. Groups with fewer than 3 of our transactions in the same block are dropped. That selection can bias the ordering sample toward bursts whose higher-fee transactions land more often (see the target-window landing distribution below). With a five-transaction burst the smallest attainable two-sided per-burst permutation p is 1/60 ≈ 0.017; pooled tests use 2000 permutations, so their floor is 0.0005.

## Verdict per label (H1 / H2 / H0)

All verdict inputs use the same-payer arm only. H1 = pooled tau_fee > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_fee > 0 in ascending bursts alone. H2 = pooled tau_send > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_send > 0 in ascending bursts alone. If both hold the verdict is **mixed**; if neither holds it is **no rule detected (H0 not rejected)**; zero primary groups gives **insufficient data**. Descending bursts are a consistency check only.

| label | primary bursts (asc+shuffle, same arm) | primary txs | tau_fee (same arm) | p_fee | Holm p_fee | Holm p_send | verdict | mode evidence |
|---|---|---|---|---|---|---|---|---|
| Agave | 2 | 6 | +0.000 | 1.000 | 1.000 | 0.097 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=+0.000 p=1.000 tau_send=+1.000 p=0.049 |
| AgaveBam | 7 | 21 | -0.333 | 0.176 | 0.538 | 0.000 | H2 arrival rule | asc (primary): tau_fee=-1.000 p=0.332 tau_send=+1.000 p=0.332; asc+shuffle (primary): tau_fee=-0.333 p=0.176 tau_send=+1.000 p=0.000; desc (consistency only): tau_fee=+1.000 p=0.332 tau_send=+1.000 p=0.332 |
| FireBAM | 2 | 6 | -1.000 | 0.049 | 0.242 | 0.097 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=-1.000 p=0.049 tau_send=+1.000 p=0.049; desc (consistency only): tau_fee=+1.000 p=0.049 tau_send=+1.000 p=0.049 |
| Firedancer | 9 | 28 | -0.630 | 0.002 | 0.014 | 0.000 | H2 arrival rule | asc (primary): tau_fee=-1.000 p=0.000 tau_send=+1.000 p=0.000; asc+shuffle (primary): tau_fee=-0.630 p=0.002 tau_send=+1.000 p=0.000; desc (consistency only): tau_fee=+1.000 p=0.000 tau_send=+1.000 p=0.000 |
| HarmonicAgave | 3 | 9 | -0.333 | 0.549 | 1.000 | 0.016 | H2 arrival rule | asc (primary): tau_fee=-1.000 p=0.332 tau_send=+1.000 p=0.332; asc+shuffle (primary): tau_fee=-0.333 p=0.549 tau_send=+1.000 p=0.004; desc (consistency only): tau_fee=+1.000 p=0.332 tau_send=+1.000 p=0.332 |
| HarmonicFiredancer | 4 | 12 | -0.500 | 0.135 | 0.538 | 0.005 | H2 arrival rule | asc (primary): tau_fee=-1.000 p=0.049 tau_send=+1.000 p=0.049; asc+shuffle (primary): tau_fee=-0.500 p=0.135 tau_send=+1.000 p=0.001; desc (consistency only): tau_fee=+1.000 p=0.004 tau_send=+1.000 p=0.004 |
| JitoLabs | 6 | 18 | -0.889 | 0.001 | 0.004 | 0.003 | H2 arrival rule | asc (primary): tau_fee=-0.867 p=0.002 tau_send=+0.867 p=0.002; asc+shuffle (primary): tau_fee=-0.889 p=0.001 tau_send=+0.889 p=0.001; desc (consistency only): tau_fee=+1.000 p=0.000 tau_send=+1.000 p=0.000 |
| Rakurai | 3 | 9 | -0.778 | 0.027 | 0.162 | 0.016 | H2 arrival rule | asc (primary): tau_fee=-1.000 p=0.049 tau_send=+1.000 p=0.049; asc+shuffle (primary): tau_fee=-0.778 p=0.027 tau_send=+1.000 p=0.004 |

## Per-burst Kendall tau (primary: target window and target leader)

| label | target | arm | slot | n | tau_fee | p_fee | tau_send | p_send |
|---|---|---|---|---|---|---|---|---|
| Firedancer | JD549Hsb | same | 461359096 | 3 | -1.000 | 0.332 | +1.000 | 0.318 |
| HarmonicFiredancer | 87CcUxpy | multi | 461359124 | 3 | +1.000 | 0.335 | +1.000 | 0.347 |
| AgaveBam | Fc6NNdS2 | same | 461359194 | 3 | +0.333 | 1.000 | +1.000 | 0.332 |
| HarmonicAgave | Fd7btgyS | multi | 461359250 | 3 | -1.000 | 0.314 | +1.000 | 0.320 |
| FireBAM | A4hyMd3F | same | 461359313 | 3 | +1.000 | 0.344 | +1.000 | 0.329 |
| Firedancer | 9eGrDohd | multi | 461359373 | 3 | -0.333 | 1.000 | +1.000 | 0.330 |
| HarmonicAgave | Fd7btgyS | same | 461359466 | 3 | -1.000 | 0.332 | +1.000 | 0.326 |
| HarmonicAgave | Fd7btgyS | multi | 461359477 | 3 | +1.000 | 0.322 | +1.000 | 0.326 |
| FireBAM | SSmBEooM | same | 461359553 | 3 | -1.000 | 0.313 | +1.000 | 0.346 |
| JitoLabs | C8Bey3LK | multi | 461359627 | 3 | -1.000 | 0.327 | +1.000 | 0.322 |
| Firedancer | 9eGrDohd | same | 461359669 | 4 | +1.000 | 0.080 | +1.000 | 0.078 |
| Firedancer | JD549Hsb | multi | 461359745 | 3 | +1.000 | 0.332 | +1.000 | 0.319 |
| JitoLabs | 5pPRHnie | multi | 461359885 | 3 | +1.000 | 0.334 | +1.000 | 0.356 |
| HarmonicFiredancer | 6ptuwW4r | multi | 461359987 | 3 | -1.000 | 0.336 | +1.000 | 0.336 |
| AgaveBam | Fc6NNdS2 | same | 461360053 | 3 | +1.000 | 0.337 | +1.000 | 0.334 |
| HarmonicFiredancer | 87CcUxpy | same | 461360105 | 3 | -1.000 | 0.342 | +1.000 | 0.333 |
| HarmonicAgave | BtsmiEEv | multi | 461360117 | 3 | +1.000 | 0.327 | +1.000 | 0.338 |
| Firedancer | 9eGrDohd | same | 461360170 | 3 | +0.333 | 1.000 | +1.000 | 0.326 |
| Firedancer | JD549Hsb | multi | 461360192 | 4 | -1.000 | 0.079 | +1.000 | 0.081 |
| FireBAM | A4hyMd3F | same | 461360261 | 3 | +1.000 | 0.335 | +1.000 | 0.334 |
| JitoLabs | C8Bey3LK | same | 461360358 | 3 | -1.000 | 0.343 | +1.000 | 0.334 |
| FireBAM | A4hyMd3F | same | 461360478 | 3 | -1.000 | 0.331 | +1.000 | 0.330 |
| HarmonicAgave | Fd7btgyS | multi | 461360589 | 3 | -1.000 | 0.333 | +1.000 | 0.323 |
| JitoLabs | C8Bey3LK | same | 461360621 | 4 | +1.000 | 0.070 | +1.000 | 0.084 |
| JitoLabs | 5pPRHnie | same | 461360778 | 3 | -1.000 | 0.371 | +1.000 | 0.344 |
| AgaveBam | 6y7V8dL6 | same | 461361006 | 3 | -1.000 | 0.330 | +1.000 | 0.348 |
| JitoLabs | C8Bey3LK | multi | 461361043 | 3 | -1.000 | 0.340 | +1.000 | 0.337 |
| JitoLabs | 5pPRHnie | same | 461361125 | 3 | +1.000 | 0.322 | +1.000 | 0.323 |
| Firedancer | JD549Hsb | same | 461361273 | 4 | -1.000 | 0.080 | +1.000 | 0.085 |
| Firedancer | 9eGrDohd | multi | 461361296 | 4 | +1.000 | 0.082 | +1.000 | 0.091 |
| AgaveBam | 6y7V8dL6 | same | 461361373 | 3 | -0.333 | 1.000 | +1.000 | 0.327 |
| HarmonicFiredancer | 87CcUxpy | multi | 461361516 | 3 | +0.333 | 1.000 | +1.000 | 0.351 |
| Rakurai | 7PdKhpKz | same | 461361646 | 3 | -0.333 | 1.000 | +1.000 | 0.344 |
| JitoLabs | 5pPRHnie | multi | 461361741 | 3 | -1.000 | 0.346 | +1.000 | 0.341 |
| HarmonicFiredancer | 87CcUxpy | same | 461361753 | 3 | +1.000 | 0.317 | +1.000 | 0.336 |
| AgaveBam | 6y7V8dL6 | same | 461361869 | 3 | -1.000 | 0.334 | +1.000 | 0.322 |
| AgaveBam | Fc6NNdS2 | same | 461361934 | 3 | +0.333 | 1.000 | +1.000 | 0.345 |
| HarmonicFiredancer | 6ptuwW4r | multi | 461362071 | 3 | -1.000 | 0.345 | +1.000 | 0.337 |
| HarmonicAgave | Fd7btgyS | same | 461362110 | 3 | +1.000 | 0.342 | +1.000 | 0.335 |
| HarmonicAgave | Fd7btgyS | multi | 461362141 | 3 | +1.000 | 0.341 | +1.000 | 0.338 |
| Rakurai | 7PdKhpKz | same | 461362274 | 3 | -1.000 | 0.328 | +1.000 | 0.338 |
| HarmonicAgave | BtsmiEEv | multi | 461362294 | 3 | +1.000 | 0.333 | +1.000 | 0.329 |
| Firedancer | JD549Hsb | same | 461362349 | 3 | -1.000 | 0.328 | +1.000 | 0.348 |
| HarmonicFiredancer | 87CcUxpy | same | 461362484 | 3 | +1.000 | 0.353 | +1.000 | 0.338 |
| JitoLabs | 5pPRHnie | multi | 461362550 | 3 | -0.333 | 1.000 | +1.000 | 0.324 |
| Firedancer | 9eGrDohd | multi | 461362801 | 3 | +1.000 | 0.340 | +1.000 | 0.353 |
| JitoLabs | 5pPRHnie | same | 461362833 | 3 | -1.000 | 0.334 | +1.000 | 0.334 |
| JitoLabs | C8Bey3LK | multi | 461362850 | 3 | -1.000 | 0.338 | +1.000 | 0.321 |
| HarmonicFiredancer | 87CcUxpy | same | 461362926 | 3 | +1.000 | 0.354 | +1.000 | 0.345 |
| Agave | dxa6QFqL | multi | 461362972 | 3 | -0.333 | 1.000 | +1.000 | 0.328 |
| JitoLabs | 5pPRHnie | same | 461363030 | 3 | -1.000 | 0.335 | +1.000 | 0.332 |
| FireBAM | A4hyMd3F | multi | 461363082 | 3 | +1.000 | 0.336 | +1.000 | 0.328 |
| Firedancer | 9eGrDohd | same | 461363097 | 3 | +0.333 | 1.000 | +1.000 | 0.322 |
| Firedancer | JD549Hsb | multi | 461363292 | 3 | -0.333 | 1.000 | +1.000 | 0.329 |
| Firedancer | JD549Hsb | multi | 461363406 | 3 | +1.000 | 0.341 | +1.000 | 0.317 |
| HarmonicAgave | BtsmiEEv | same | 461363505 | 3 | -0.333 | 1.000 | +1.000 | 0.303 |
| FireBAM | SSmBEooM | multi | 461363557 | 3 | -1.000 | 0.340 | +1.000 | 0.342 |
| Firedancer | 9eGrDohd | same | 461363626 | 3 | +1.000 | 0.319 | +1.000 | 0.339 |
| Agave | rsbp8zMH | same | 461363946 | 3 | -0.333 | 1.000 | +1.000 | 0.329 |
| JitoLabs | 5pPRHnie | multi | 461364105 | 3 | -1.000 | 0.338 | +1.000 | 0.350 |
| FireBAM | SSmBEooM | multi | 461364242 | 3 | +1.000 | 0.317 | +1.000 | 0.340 |
| HarmonicFiredancer | 6ptuwW4r | same | 461364333 | 3 | -1.000 | 0.342 | +1.000 | 0.343 |
| HarmonicAgave | BtsmiEEv | multi | 461364381 | 3 | +1.000 | 0.332 | +1.000 | 0.347 |
| AgaveBam | 6y7V8dL6 | same | 461364457 | 3 | -1.000 | 0.333 | +1.000 | 0.327 |
| AgaveBam | 6y7V8dL6 | multi | 461364473 | 3 | -1.000 | 0.342 | +1.000 | 0.346 |
| Firedancer | 9eGrDohd | same | 461364569 | 3 | +1.000 | 0.331 | +1.000 | 0.344 |
| JitoLabs | 5pPRHnie | same | 461364661 | 3 | -1.000 | 0.350 | +1.000 | 0.325 |
| AgaveBam | Fc6NNdS2 | multi | 461364705 | 3 | +1.000 | 0.344 | +1.000 | 0.319 |
| Agave | dxa6QFqL | same | 461364781 | 3 | +0.333 | 1.000 | +1.000 | 0.322 |
| AgaveBam | Fc6NNdS2 | multi | 461364796 | 3 | -1.000 | 0.328 | +1.000 | 0.329 |
| Firedancer | JD549Hsb | multi | 461364828 | 3 | -1.000 | 0.333 | +1.000 | 0.303 |
| Firedancer | JD549Hsb | same | 461364848 | 3 | -1.000 | 0.352 | +1.000 | 0.308 |
| AgaveBam | 6y7V8dL6 | multi | 461364938 | 3 | +1.000 | 0.329 | +1.000 | 0.332 |
| HarmonicFiredancer | 87CcUxpy | same | 461365009 | 3 | -0.333 | 1.000 | +1.000 | 0.327 |
| HarmonicFiredancer | 87CcUxpy | multi | 461365037 | 3 | -1.000 | 0.351 | +1.000 | 0.322 |
| JitoLabs | C8Bey3LK | same | 461365058 | 3 | +1.000 | 0.329 | +1.000 | 0.355 |
| HarmonicFiredancer | 87CcUxpy | multi | 461365121 | 3 | +0.333 | 1.000 | +1.000 | 0.342 |
| AgaveBam | 6y7V8dL6 | same | 461366130 | 3 | +0.333 | 1.000 | +1.000 | 0.324 |
| JitoLabs | 5pPRHnie | same | 461366173 | 3 | +1.000 | 0.344 | +1.000 | 0.326 |
| JitoLabs | 5pPRHnie | multi | 461366243 | 3 | -0.333 | 1.000 | +1.000 | 0.333 |
| JitoLabs | C8Bey3LK | same | 461366258 | 3 | -0.333 | 1.000 | +0.333 | 1.000 |
| Firedancer | JD549Hsb | multi | 461366346 | 3 | +1.000 | 0.328 | +1.000 | 0.339 |
| HarmonicFiredancer | 87CcUxpy | same | 461366407 | 3 | +0.333 | 1.000 | +1.000 | 0.332 |
| HarmonicAgave | BtsmiEEv | multi | 461366571 | 3 | -0.333 | 1.000 | +1.000 | 0.329 |
| Rakurai | 3B2mGaZo | same | 461366642 | 3 | -1.000 | 0.311 | +1.000 | 0.338 |
| HarmonicAgave | Fd7btgyS | multi | 461366842 | 3 | -0.333 | 1.000 | +0.333 | 1.000 |
| HarmonicAgave | BtsmiEEv | multi | 461366953 | 3 | +1.000 | 0.329 | +1.000 | 0.322 |
| Firedancer | 9eGrDohd | same | 461367038 | 3 | -1.000 | 0.327 | +1.000 | 0.340 |
| HarmonicAgave | BtsmiEEv | same | 461367133 | 3 | +0.333 | 1.000 | +1.000 | 0.329 |
| Firedancer | 9eGrDohd | same | 461367441 | 3 | -1.000 | 0.312 | +1.000 | 0.336 |
| HarmonicAgave | BtsmiEEv | multi | 461367535 | 3 | +1.000 | 0.350 | +1.000 | 0.344 |
| Firedancer | 9eGrDohd | same | 461367610 | 3 | -0.333 | 1.000 | +1.000 | 0.343 |
| JitoLabs | C8Bey3LK | multi | 461367651 | 4 | -0.667 | 0.330 | +0.667 | 0.349 |
| Firedancer | JD549Hsb | same | 461367672 | 3 | +1.000 | 0.308 | +1.000 | 0.344 |
| JitoLabs | C8Bey3LK | multi | 461367759 | 3 | -1.000 | 0.334 | +1.000 | 0.337 |

## Pooled per client label (primary: target window and target leader)

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 3 | 9 | -0.111 | +1.000 | 0.922 | 0.004 |
| AgaveBam | 12 | 36 | -0.111 | +1.000 | 0.554 | 0.000 |
| FireBAM | 7 | 21 | +0.143 | +1.000 | 0.640 | 0.000 |
| Firedancer | 22 | 70 | +0.030 | +1.000 | 0.808 | 0.000 |
| HarmonicAgave | 15 | 45 | +0.289 | +0.956 | 0.102 | 0.000 |
| HarmonicFiredancer | 13 | 39 | -0.026 | +1.000 | 0.868 | 0.000 |
| JitoLabs | 20 | 62 | -0.383 | +0.950 | 0.006 | 0.000 |
| Rakurai | 3 | 9 | -0.778 | +1.000 | 0.027 | 0.004 |

## Grouped results by payer arm and order mode (exploratory)

| label | grouped by | group | bursts | txs | mean tau_fee | pooled p_fee | mean tau_send | pooled p_send |
|---|---|---|---|---|---|---|---|---|
| Agave | payer_arm | multi | 1 | 3 | -0.333 | 1.000 | +1.000 | 0.332 |
| Agave | payer_arm | same | 2 | 6 | +0.000 | 1.000 | +1.000 | 0.049 |
| Agave | order_mode | shuffle | 3 | 9 | -0.111 | 0.922 | +1.000 | 0.004 |
| AgaveBam | payer_arm | multi | 4 | 12 | +0.000 | 1.000 | +1.000 | 0.001 |
| AgaveBam | payer_arm | same | 8 | 24 | -0.167 | 0.426 | +1.000 | 0.000 |
| AgaveBam | order_mode | asc | 3 | 9 | -1.000 | 0.004 | +1.000 | 0.004 |
| AgaveBam | order_mode | desc | 3 | 9 | +1.000 | 0.004 | +1.000 | 0.004 |
| AgaveBam | order_mode | shuffle | 6 | 18 | -0.222 | 0.328 | +1.000 | 0.000 |
| FireBAM | payer_arm | multi | 3 | 9 | +0.333 | 0.551 | +1.000 | 0.004 |
| FireBAM | payer_arm | same | 4 | 12 | +0.000 | 1.000 | +1.000 | 0.001 |
| FireBAM | order_mode | asc | 1 | 3 | -1.000 | 0.332 | +1.000 | 0.332 |
| FireBAM | order_mode | desc | 3 | 9 | +1.000 | 0.004 | +1.000 | 0.004 |
| FireBAM | order_mode | shuffle | 3 | 9 | -0.333 | 0.556 | +1.000 | 0.004 |
| Firedancer | payer_arm | multi | 9 | 29 | +0.259 | 0.196 | +1.000 | 0.000 |
| Firedancer | payer_arm | same | 13 | 41 | -0.128 | 0.439 | +1.000 | 0.000 |
| Firedancer | order_mode | asc | 6 | 20 | -1.000 | 0.000 | +1.000 | 0.000 |
| Firedancer | order_mode | desc | 8 | 26 | +1.000 | 0.000 | +1.000 | 0.000 |
| Firedancer | order_mode | shuffle | 8 | 24 | -0.167 | 0.562 | +1.000 | 0.000 |
| HarmonicAgave | payer_arm | multi | 11 | 33 | +0.394 | 0.055 | +0.939 | 0.000 |
| HarmonicAgave | payer_arm | same | 4 | 12 | +0.000 | 1.000 | +1.000 | 0.001 |
| HarmonicAgave | order_mode | asc | 4 | 12 | -0.833 | 0.004 | +0.833 | 0.004 |
| HarmonicAgave | order_mode | desc | 6 | 18 | +1.000 | 0.000 | +1.000 | 0.000 |
| HarmonicAgave | order_mode | shuffle | 5 | 15 | +0.333 | 0.242 | +1.000 | 0.000 |
| HarmonicFiredancer | payer_arm | multi | 6 | 18 | -0.222 | 0.334 | +1.000 | 0.000 |
| HarmonicFiredancer | payer_arm | same | 7 | 21 | +0.143 | 0.656 | +1.000 | 0.000 |
| HarmonicFiredancer | order_mode | asc | 5 | 15 | -1.000 | 0.000 | +1.000 | 0.000 |
| HarmonicFiredancer | order_mode | desc | 4 | 12 | +1.000 | 0.001 | +1.000 | 0.001 |
| HarmonicFiredancer | order_mode | shuffle | 4 | 12 | +0.167 | 0.716 | +1.000 | 0.001 |
| JitoLabs | payer_arm | multi | 10 | 31 | -0.633 | 0.001 | +0.967 | 0.000 |
| JitoLabs | payer_arm | same | 10 | 31 | -0.133 | 0.521 | +0.933 | 0.000 |
| JitoLabs | order_mode | asc | 11 | 34 | -0.909 | 0.000 | +0.909 | 0.000 |
| JitoLabs | order_mode | desc | 5 | 16 | +1.000 | 0.000 | +1.000 | 0.000 |
| JitoLabs | order_mode | shuffle | 4 | 12 | -0.667 | 0.051 | +1.000 | 0.001 |
| Rakurai | payer_arm | same | 3 | 9 | -0.778 | 0.027 | +1.000 | 0.004 |
| Rakurai | order_mode | asc | 2 | 6 | -1.000 | 0.049 | +1.000 | 0.049 |
| Rakurai | order_mode | shuffle | 1 | 3 | -0.333 | 1.000 | +1.000 | 0.332 |

## Sensitivity: all landed (any leader)

Same statistic as the primary pooled table, but using every landed row regardless of `in_target_window` or `leader_is_target`. This is exploratory and shows how much the result depends on the leader filter.

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 3 | 9 | -0.111 | +1.000 | 0.922 | 0.004 |
| AgaveBam | 13 | 39 | -0.179 | +1.000 | 0.306 | 0.000 |
| FireBAM | 7 | 21 | +0.143 | +1.000 | 0.640 | 0.000 |
| Firedancer | 22 | 70 | +0.030 | +1.000 | 0.808 | 0.000 |
| HarmonicAgave | 15 | 45 | +0.289 | +0.956 | 0.102 | 0.000 |
| HarmonicFiredancer | 13 | 39 | -0.026 | +1.000 | 0.868 | 0.000 |
| JitoLabs | 20 | 62 | -0.383 | +0.950 | 0.006 | 0.000 |
| Rakurai | 3 | 9 | -0.778 | +1.000 | 0.027 | 0.004 |

## Landing and timing

Live timing uses live-only denominators. Dry-run timing is shown in separate columns so it cannot inflate a live rate. `on_time` means the per-tx estimated send slot was before `window_start`; `in_window_at_send` means the send was not after the window (`est_slot_at_send < window_start + 4`). The clearer `send_phase` column is `early` when `est_slot_at_send < window_start`, `inside` when it is in the four-slot window, and `late` otherwise.

| label | sent | live sent | landed | landing rate | live on_time | on_time rate | live in_window | in_window rate | mean live send_offset | dry sent | dry on_time | dry on_time rate | dry in_window | dry in_window rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agave | 25 | 25 | 25 | 1.000 | 18 | 0.720 | 25 | 1.000 | -1.040 | 0 | 0 | - | 0 | - |
| AgaveBam | 100 | 100 | 100 | 1.000 | 83 | 0.830 | 100 | 1.000 | -1.170 | 0 | 0 | - | 0 | - |
| FireBAM | 40 | 40 | 40 | 1.000 | 34 | 0.850 | 40 | 1.000 | -1.150 | 0 | 0 | - | 0 | - |
| Firedancer | 120 | 120 | 120 | 1.000 | 102 | 0.850 | 120 | 1.000 | -1.208 | 0 | 0 | - | 0 | - |
| HarmonicAgave | 110 | 110 | 110 | 1.000 | 101 | 0.918 | 110 | 1.000 | -1.364 | 0 | 0 | - | 0 | - |
| HarmonicFiredancer | 90 | 90 | 90 | 1.000 | 69 | 0.767 | 90 | 1.000 | -1.100 | 0 | 0 | - | 0 | - |
| JitoLabs | 120 | 120 | 120 | 1.000 | 106 | 0.883 | 120 | 1.000 | -1.283 | 0 | 0 | - | 0 | - |
| Rakurai | 15 | 15 | 15 | 1.000 | 10 | 0.667 | 15 | 1.000 | -0.800 | 0 | 0 | - | 0 | - |
| Unknown(35832) | 5 | 5 | 5 | 1.000 | 4 | 0.800 | 5 | 1.000 | -1.200 | 0 | 0 | - | 0 | - |

### Landing by fee level (live only)

| cu_price (micro/CU) | live sent | landed | landing rate | live on_time | on_time rate |
|---|---|---|---|---|---|
| 0 | 125 | 125 | 1.000 | 101 | 0.808 |
| 1000 | 125 | 125 | 1.000 | 112 | 0.896 |
| 10000 | 125 | 125 | 1.000 | 111 | 0.888 |
| 100000 | 125 | 125 | 1.000 | 109 | 0.872 |
| 1000000 | 125 | 125 | 1.000 | 94 | 0.752 |

### Selected sample: our txs in the target window per burst

The primary test only uses groups with **at least 3** of our transactions co-landed in the target block. This table counts, for each live burst, how many of its transactions landed anywhere in the target window (not necessarily in the same block). Bursts with 0-2 are under-represented in the ordering tests. If higher-fee transactions also land more often, the primary sample is biased toward higher fees; that selection effect is a limitation, not a finding.

| label | live bursts | 0 | 1 | 2 | 3 | 4 | 5 | mean landed in target window |
|---|---|---|---|---|---|---|---|---|
| Agave | 5 | 0 | 0 | 1 | 0 | 0 | 4 | 4.40 |
| AgaveBam | 20 | 0 | 0 | 1 | 0 | 1 | 18 | 4.80 |
| FireBAM | 8 | 0 | 0 | 0 | 0 | 0 | 8 | 5 |
| Firedancer | 24 | 0 | 0 | 0 | 0 | 0 | 24 | 5 |
| HarmonicAgave | 22 | 0 | 0 | 0 | 1 | 0 | 21 | 4.91 |
| HarmonicFiredancer | 18 | 0 | 0 | 0 | 2 | 0 | 16 | 4.78 |
| JitoLabs | 24 | 0 | 0 | 0 | 0 | 1 | 23 | 4.96 |
| Rakurai | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 5 |
| Unknown(35832) | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |

## Verified leader windows

Only windows whose `window_end` is before the current finalized slot count as verified. `leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that actually produced a block; `planned` = not yet elapsed, not counted as verified.

| label | windows | leaders_ok | windows with blocks | block_slots | planned |
|---|---|---|---|---|---|
| Agave | 5 | 5 | 5 | 20 | 2 |
| AgaveBam | 32 | 32 | 32 | 128 | 15 |
| FireBAM | 8 | 8 | 8 | 32 | 2 |
| Firedancer | 31 | 31 | 31 | 124 | 20 |
| HarmonicAgave | 34 | 34 | 34 | 136 | 12 |
| HarmonicFiredancer | 23 | 23 | 23 | 92 | 17 |
| JitoLabs | 31 | 31 | 31 | 124 | 21 |
| Rakurai | 7 | 7 | 7 | 28 | 2 |
| Unknown(35832) | 1 | 1 | 1 | 4 | 2 |

## Whole-block priority ordering (APPROXIMATION)

Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.
The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.
Positive tau = higher approximate priority fee appears earlier in the block.

| label | slots | mean tau_priority (approx) | non-vote txs |
|---|---|---|---|
| Agave | 13 | +0.051 | 5370 |
| AgaveBam | 50 | +0.041 | 22130 |
| FireBAM | 20 | +0.022 | 6708 |
| Firedancer | 55 | -0.060 | 32759 |
| HarmonicAgave | 56 | +0.012 | 25235 |
| HarmonicFiredancer | 43 | +0.023 | 17179 |
| JitoLabs | 55 | -0.002 | 27505 |
| Rakurai | 8 | -0.012 | 4463 |
| Unknown(35832) | 3 | -0.044 | 565 |

### Per-slot whole-block check

| slot | label | non-vote txs | tau_priority (approx) |
|---|---|---|---|
| 461359096 | Firedancer | 396 | -0.168 |
| 461359097 | Firedancer | 435 | -0.175 |
| 461359124 | HarmonicFiredancer | 281 | -0.036 |
| 461359125 | HarmonicFiredancer | 312 | +0.033 |
| 461359193 | AgaveBam | 327 | +0.032 |
| 461359194 | AgaveBam | 292 | +0.008 |
| 461359250 | HarmonicAgave | 305 | -0.024 |
| 461359251 | HarmonicAgave | 311 | -0.017 |
| 461359313 | FireBAM | 242 | +0.020 |
| 461359314 | FireBAM | 284 | -0.088 |
| 461359373 | Firedancer | 378 | +0.010 |
| 461359374 | Firedancer | 332 | +0.014 |
| 461359465 | HarmonicAgave | 297 | +0.017 |
| 461359466 | HarmonicAgave | 344 | -0.006 |
| 461359467 | HarmonicAgave | 400 | +0.001 |
| 461359476 | HarmonicAgave | 445 | +0.004 |
| 461359477 | HarmonicAgave | 346 | -0.000 |
| 461359478 | HarmonicAgave | 390 | -0.015 |
| 461359552 | FireBAM | 310 | +0.100 |
| 461359553 | FireBAM | 277 | +0.040 |
| 461359554 | FireBAM | 257 | -0.005 |
| 461359626 | JitoLabs | 538 | -0.003 |
| 461359627 | JitoLabs | 830 | +0.014 |
| 461359668 | Firedancer | 708 | -0.076 |
| 461359669 | Firedancer | 362 | -0.046 |
| 461359744 | Firedancer | 459 | -0.229 |
| 461359745 | Firedancer | 308 | -0.139 |
| 461359746 | Firedancer | 343 | -0.215 |
| 461359796 | Agave | 410 | +0.015 |
| 461359797 | Agave | 239 | +0.075 |
| 461359798 | Agave | 324 | +0.096 |
| 461359885 | JitoLabs | 364 | +0.027 |
| 461359886 | JitoLabs | 339 | +0.019 |
| 461359914 | AgaveBam | 284 | -0.033 |
| 461359915 | AgaveBam | 297 | +0.026 |
| 461359916 | AgaveBam | 489 | +0.042 |
| 461359987 | HarmonicFiredancer | 370 | +0.002 |
| 461359988 | HarmonicFiredancer | 376 | +0.162 |
| 461360052 | AgaveBam | 599 | +0.151 |
| 461360053 | AgaveBam | 335 | +0.058 |
| 461360054 | AgaveBam | 350 | -0.020 |
| 461360105 | HarmonicFiredancer | 367 | -0.021 |
| 461360106 | HarmonicFiredancer | 348 | +0.056 |
| 461360117 | HarmonicAgave | 453 | -0.005 |
| 461360118 | HarmonicAgave | 461 | -0.087 |
| 461360169 | Firedancer | 721 | +0.080 |
| 461360170 | Firedancer | 636 | -0.042 |
| 461360171 | Firedancer | 605 | +0.095 |
| 461360192 | Firedancer | 787 | -0.109 |
| 461360193 | Firedancer | 595 | -0.173 |
| 461360261 | FireBAM | 347 | +0.019 |
| 461360262 | FireBAM | 340 | +0.008 |
| 461360358 | JitoLabs | 489 | +0.036 |
| 461360359 | JitoLabs | 814 | -0.047 |
| 461360400 | AgaveBam | 386 | -0.050 |
| 461360401 | AgaveBam | 298 | +0.009 |
| 461360402 | AgaveBam | 346 | +0.029 |
| 461360477 | FireBAM | 551 | +0.072 |
| 461360478 | FireBAM | 538 | +0.006 |
| 461360479 | FireBAM | 504 | +0.080 |
| 461360589 | HarmonicAgave | 343 | -0.002 |
| 461360590 | HarmonicAgave | 325 | -0.012 |
| 461360621 | JitoLabs | 328 | -0.056 |
| 461360622 | JitoLabs | 344 | -0.017 |
| 461360680 | AgaveBam | 288 | +0.080 |
| 461360681 | AgaveBam | 281 | +0.049 |
| 461360682 | AgaveBam | 287 | +0.044 |
| 461360778 | JitoLabs | 336 | +0.022 |
| 461360779 | JitoLabs | 350 | +0.066 |
| 461360820 | HarmonicAgave | 280 | +0.080 |
| 461360821 | HarmonicAgave | 284 | -0.035 |
| 461360822 | HarmonicAgave | 278 | +0.023 |
| 461361005 | AgaveBam | 270 | +0.095 |
| 461361006 | AgaveBam | 245 | -0.041 |
| 461361042 | JitoLabs | 316 | -0.214 |
| 461361043 | JitoLabs | 694 | +0.046 |
| 461361125 | JitoLabs | 388 | +0.001 |
| 461361126 | JitoLabs | 415 | -0.030 |
| 461361272 | Firedancer | 526 | -0.139 |
| 461361273 | Firedancer | 404 | -0.264 |
| 461361296 | Firedancer | 660 | -0.051 |
| 461361297 | Firedancer | 435 | +0.049 |
| 461361373 | AgaveBam | 402 | +0.057 |
| 461361374 | AgaveBam | 410 | -0.000 |
| 461361404 | HarmonicAgave | 364 | -0.008 |
| 461361405 | HarmonicAgave | 543 | -0.025 |
| 461361406 | HarmonicAgave | 476 | +0.067 |
| 461361501 | HarmonicFiredancer | 327 | +0.077 |
| 461361502 | HarmonicFiredancer | 267 | -0.095 |
| 461361503 | HarmonicFiredancer | 393 | -0.025 |
| 461361516 | HarmonicFiredancer | 549 | -0.051 |
| 461361517 | HarmonicFiredancer | 285 | -0.022 |
| 461361532 | HarmonicFiredancer | 452 | +0.123 |
| 461361533 | HarmonicFiredancer | 279 | +0.014 |
| 461361534 | HarmonicFiredancer | 315 | -0.079 |
| 461361545 | JitoLabs | 343 | +0.010 |
| 461361546 | JitoLabs | 370 | +0.029 |
| 461361547 | JitoLabs | 578 | -0.079 |
| 461361645 | Rakurai | 274 | +0.016 |
| 461361646 | Rakurai | 279 | +0.052 |
| 461361647 | Rakurai | 454 | +0.039 |
| 461361741 | JitoLabs | 368 | +0.024 |
| 461361742 | JitoLabs | 353 | +0.031 |
| 461361752 | HarmonicFiredancer | 461 | -0.099 |
| 461361753 | HarmonicFiredancer | 538 | +0.044 |
| 461361754 | HarmonicFiredancer | 477 | -0.046 |
| 461361824 | Firedancer | 417 | -0.133 |
| 461361825 | Firedancer | 397 | -0.171 |
| 461361826 | Firedancer | 395 | -0.096 |
| 461361868 | AgaveBam | 699 | -0.030 |
| 461361869 | AgaveBam | 676 | +0.165 |
| 461361870 | AgaveBam | 454 | +0.002 |
| 461361893 | AgaveBam | 303 | +0.001 |
| 461361894 | AgaveBam | 260 | +0.015 |
| 461361895 | AgaveBam | 274 | +0.026 |
| 461361934 | AgaveBam | 337 | +0.128 |
| 461361935 | AgaveBam | 328 | +0.056 |
| 461362070 | HarmonicFiredancer | 377 | +0.032 |
| 461362071 | HarmonicFiredancer | 378 | +0.023 |
| 461362109 | HarmonicAgave | 277 | -0.088 |
| 461362110 | HarmonicAgave | 320 | +0.096 |
| 461362140 | HarmonicAgave | 254 | -0.065 |
| 461362141 | HarmonicAgave | 296 | -0.092 |
| 461362142 | HarmonicAgave | 285 | -0.023 |
| 461362273 | Rakurai | 274 | -0.033 |
| 461362274 | Rakurai | 368 | -0.059 |
| 461362293 | HarmonicAgave | 407 | -0.136 |
| 461362294 | HarmonicAgave | 385 | -0.003 |
| 461362295 | HarmonicAgave | 610 | +0.167 |
| 461362349 | Firedancer | 381 | -0.098 |
| 461362350 | Firedancer | 381 | -0.128 |
| 461362456 | Unknown(35832) | 198 | -0.017 |
| 461362457 | Unknown(35832) | 173 | -0.050 |
| 461362458 | Unknown(35832) | 194 | -0.065 |
| 461362484 | HarmonicFiredancer | 299 | -0.097 |
| 461362485 | HarmonicFiredancer | 253 | +0.092 |
| 461362549 | JitoLabs | 365 | +0.040 |
| 461362550 | JitoLabs | 409 | -0.003 |
| 461362673 | HarmonicAgave | 317 | +0.012 |
| 461362674 | HarmonicAgave | 347 | +0.015 |
| 461362675 | HarmonicAgave | 318 | -0.017 |
| 461362800 | Firedancer | 540 | -0.100 |
| 461362801 | Firedancer | 521 | -0.038 |
| 461362802 | Firedancer | 544 | -0.003 |
| 461362833 | JitoLabs | 331 | -0.038 |
| 461362834 | JitoLabs | 332 | +0.004 |
| 461362849 | JitoLabs | 402 | +0.016 |
| 461362850 | JitoLabs | 385 | -0.035 |
| 461362925 | HarmonicFiredancer | 255 | +0.036 |
| 461362926 | HarmonicFiredancer | 283 | -0.023 |
| 461362927 | HarmonicFiredancer | 312 | +0.008 |
| 461362972 | Agave | 363 | +0.016 |
| 461362973 | Agave | 229 | -0.027 |
| 461363030 | JitoLabs | 307 | +0.013 |
| 461363031 | JitoLabs | 359 | +0.096 |
| 461363081 | FireBAM | 187 | +0.027 |
| 461363082 | FireBAM | 306 | -0.049 |
| 461363096 | Firedancer | 484 | -0.163 |
| 461363097 | Firedancer | 316 | +0.048 |
| 461363098 | Firedancer | 290 | -0.006 |
| 461363129 | AgaveBam | 326 | +0.055 |
| 461363130 | AgaveBam | 328 | +0.071 |
| 461363131 | AgaveBam | 345 | +0.066 |
| 461363233 | JitoLabs | 265 | -0.070 |
| 461363234 | JitoLabs | 328 | -0.045 |
| 461363235 | JitoLabs | 548 | -0.125 |
| 461363292 | Firedancer | 540 | -0.094 |
| 461363293 | Firedancer | 378 | -0.062 |
| 461363405 | Firedancer | 415 | -0.144 |
| 461363406 | Firedancer | 456 | -0.181 |
| 461363505 | HarmonicAgave | 348 | -0.000 |
| 461363506 | HarmonicAgave | 317 | +0.002 |
| 461363556 | FireBAM | 312 | +0.003 |
| 461363557 | FireBAM | 248 | +0.006 |
| 461363558 | FireBAM | 293 | +0.026 |
| 461363625 | Firedancer | 383 | -0.067 |
| 461363626 | Firedancer | 372 | +0.000 |
| 461363648 | HarmonicAgave | 728 | +0.171 |
| 461363649 | HarmonicAgave | 307 | -0.013 |
| 461363650 | HarmonicAgave | 296 | -0.011 |
| 461363725 | FireBAM | 309 | -0.034 |
| 461363726 | FireBAM | 332 | +0.081 |
| 461363727 | FireBAM | 332 | +0.076 |
| 461363852 | HarmonicAgave | 650 | +0.099 |
| 461363853 | HarmonicAgave | 387 | +0.028 |
| 461363854 | HarmonicAgave | 422 | +0.095 |
| 461363945 | Agave | 344 | -0.006 |
| 461363946 | Agave | 331 | +0.014 |
| 461363947 | Agave | 408 | -0.004 |
| 461364105 | JitoLabs | 543 | -0.061 |
| 461364106 | JitoLabs | 598 | +0.016 |
| 461364241 | FireBAM | 376 | +0.033 |
| 461364242 | FireBAM | 363 | +0.026 |
| 461364333 | HarmonicFiredancer | 558 | +0.064 |
| 461364334 | HarmonicFiredancer | 356 | +0.086 |
| 461364380 | HarmonicAgave | 407 | -0.002 |
| 461364381 | HarmonicAgave | 408 | -0.027 |
| 461364382 | HarmonicAgave | 347 | +0.024 |
| 461364457 | AgaveBam | 323 | +0.075 |
| 461364458 | AgaveBam | 337 | +0.078 |
| 461364473 | AgaveBam | 369 | -0.070 |
| 461364474 | AgaveBam | 374 | -0.048 |
| 461364568 | Firedancer | 673 | -0.059 |
| 461364569 | Firedancer | 479 | -0.022 |
| 461364621 | JitoLabs | 545 | +0.102 |
| 461364622 | JitoLabs | 473 | -0.040 |
| 461364623 | JitoLabs | 762 | -0.045 |
| 461364660 | JitoLabs | 426 | +0.150 |
| 461364661 | JitoLabs | 422 | +0.065 |
| 461364662 | JitoLabs | 448 | +0.012 |
| 461364704 | AgaveBam | 660 | +0.153 |
| 461364705 | AgaveBam | 374 | -0.036 |
| 461364781 | Agave | 415 | +0.033 |
| 461364782 | Agave | 428 | -0.025 |
| 461364796 | AgaveBam | 699 | +0.253 |
| 461364797 | AgaveBam | 337 | -0.032 |
| 461364828 | Firedancer | 578 | -0.151 |
| 461364829 | Firedancer | 452 | -0.117 |
| 461364848 | Firedancer | 500 | -0.180 |
| 461364849 | Firedancer | 445 | -0.081 |
| 461364937 | AgaveBam | 358 | +0.048 |
| 461364938 | AgaveBam | 432 | +0.048 |
| 461365009 | HarmonicFiredancer | 407 | +0.010 |
| 461365010 | HarmonicFiredancer | 379 | +0.008 |
| 461365036 | HarmonicFiredancer | 475 | -0.138 |
| 461365037 | HarmonicFiredancer | 394 | -0.016 |
| 461365057 | JitoLabs | 515 | +0.009 |
| 461365058 | JitoLabs | 492 | -0.046 |
| 461365121 | HarmonicFiredancer | 330 | +0.032 |
| 461365122 | HarmonicFiredancer | 340 | -0.008 |
| 461365180 | HarmonicFiredancer | 370 | +0.086 |
| 461365181 | HarmonicFiredancer | 311 | -0.022 |
| 461365182 | HarmonicFiredancer | 393 | -0.004 |
| 461366129 | AgaveBam | 510 | +0.063 |
| 461366130 | AgaveBam | 493 | +0.051 |
| 461366152 | JitoLabs | 320 | -0.028 |
| 461366153 | JitoLabs | 520 | +0.006 |
| 461366154 | JitoLabs | 502 | +0.008 |
| 461366172 | JitoLabs | 600 | +0.094 |
| 461366173 | JitoLabs | 611 | -0.089 |
| 461366174 | JitoLabs | 565 | -0.003 |
| 461366242 | JitoLabs | 670 | +0.081 |
| 461366243 | JitoLabs | 644 | +0.020 |
| 461366257 | JitoLabs | 522 | -0.045 |
| 461366258 | JitoLabs | 528 | -0.075 |
| 461366259 | JitoLabs | 757 | -0.004 |
| 461366345 | Firedancer | 667 | -0.026 |
| 461366346 | Firedancer | 800 | -0.124 |
| 461366347 | Firedancer | 1035 | -0.026 |
| 461366407 | HarmonicFiredancer | 427 | +0.095 |
| 461366408 | HarmonicFiredancer | 368 | +0.113 |
| 461366460 | HarmonicFiredancer | 825 | +0.322 |
| 461366461 | HarmonicFiredancer | 391 | +0.092 |
| 461366462 | HarmonicFiredancer | 413 | +0.065 |
| 461366488 | HarmonicAgave | 491 | -0.077 |
| 461366489 | HarmonicAgave | 492 | +0.042 |
| 461366490 | HarmonicAgave | 503 | -0.060 |
| 461366571 | HarmonicAgave | 703 | +0.139 |
| 461366573 | HarmonicAgave | 700 | +0.048 |
| 461366641 | Rakurai | 949 | -0.100 |
| 461366642 | Rakurai | 850 | -0.043 |
| 461366643 | Rakurai | 1015 | +0.035 |
| 461366716 | Firedancer | 955 | -0.242 |
| 461366717 | Firedancer | 1080 | -0.113 |
| 461366718 | Firedancer | 929 | -0.013 |
| 461366805 | HarmonicAgave | 833 | +0.037 |
| 461366806 | HarmonicAgave | 633 | -0.001 |
| 461366807 | HarmonicAgave | 562 | +0.087 |
| 461366841 | HarmonicAgave | 318 | -0.045 |
| 461366842 | HarmonicAgave | 842 | +0.027 |
| 461366915 | Agave | 788 | +0.150 |
| 461366916 | Agave | 436 | +0.158 |
| 461366917 | Agave | 655 | +0.161 |
| 461366953 | HarmonicAgave | 618 | +0.119 |
| 461366954 | HarmonicAgave | 669 | -0.002 |
| 461367037 | Firedancer | 1389 | +0.226 |
| 461367038 | Firedancer | 1349 | +0.198 |
| 461367105 | AgaveBam | 1013 | +0.180 |
| 461367106 | AgaveBam | 509 | +0.035 |
| 461367107 | AgaveBam | 571 | +0.034 |
| 461367132 | HarmonicAgave | 862 | +0.007 |
| 461367133 | HarmonicAgave | 466 | -0.093 |
| 461367249 | AgaveBam | 804 | -0.120 |
| 461367250 | AgaveBam | 537 | -0.027 |
| 461367252 | AgaveBam | 433 | +0.005 |
| 461367265 | HarmonicFiredancer | 581 | -0.041 |
| 461367266 | HarmonicFiredancer | 384 | -0.058 |
| 461367267 | HarmonicFiredancer | 923 | +0.215 |
| 461367341 | AgaveBam | 859 | +0.265 |
| 461367342 | AgaveBam | 948 | -0.071 |
| 461367343 | AgaveBam | 674 | +0.081 |
| 461367440 | Firedancer | 1289 | +0.117 |
| 461367441 | Firedancer | 756 | +0.119 |
| 461367534 | HarmonicAgave | 771 | +0.137 |
| 461367535 | HarmonicAgave | 694 | +0.135 |
| 461367610 | Firedancer | 704 | +0.161 |
| 461367611 | Firedancer | 860 | +0.227 |
| 461367651 | JitoLabs | 908 | -0.033 |
| 461367652 | JitoLabs | 811 | +0.127 |
| 461367672 | Firedancer | 715 | -0.167 |
| 461367673 | Firedancer | 804 | -0.011 |
| 461367758 | JitoLabs | 770 | -0.061 |
| 461367759 | JitoLabs | 965 | +0.011 |
