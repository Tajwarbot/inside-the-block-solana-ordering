# obp results

- Analysis generated (UTC): 2026-10-31T13:40:08Z
- Measurement send window (UTC): 2026-10-25T19:07:36Z to 2026-10-31T13:30:14Z
- Plan created (UTC): n/a
- Rows: sent=1435, landed=1387, block_txs=178268

Positive tau means higher fee (or earlier send order) appears earlier in the block.
Permutation p-values use a two-sided null; small samples give weak evidence.

## Test plan: primary vs exploratory

**Pre-registered primary test:** pooled `tau_fee` per client label on the **same-payer** arm, using only **ascending + shuffled** bursts and only rows with `in_target_window=True` and `leader_is_target=True`. Descending bursts are excluded from the primary test because there fee order equals send order (confounded); desc is a consistency check only. Holm correction is applied across the per-label primary p-values below, separately for H1 (fee) and H2 (send).

Everything else (multi-payer arm, descending mode, per-burst, whole-block, landing rates) is **exploratory**. Groups with fewer than 3 of our transactions in the same block are dropped. That selection can bias the ordering sample toward bursts whose higher-fee transactions land more often (see the target-window landing distribution below). With a five-transaction burst the smallest attainable two-sided per-burst permutation p is 1/60 ≈ 0.017; pooled tests use 2000 permutations, so their floor is 0.0005.

## Verdict per label (H1 / H2 / H0)

All verdict inputs use the same-payer arm only. H1 = pooled tau_fee > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_fee > 0 in ascending bursts alone. H2 = pooled tau_send > 0 with Holm-adjusted p < 0.05 on ascending+shuffled bursts AND tau_send > 0 in ascending bursts alone. If both hold the verdict is **mixed**; if neither holds it is **no rule detected (H0 not rejected)**; zero primary groups gives **insufficient data**. Descending bursts are a consistency check only.

| label | primary bursts (asc+shuffle, same arm) | primary txs | tau_fee (same arm) | p_fee | Holm p_fee | Holm p_send | verdict | mode evidence |
|---|---|---|---|---|---|---|---|---|
| Agave | 2 | 6 | -0.333 | 0.495 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=-1.000 p=0.332 tau_send=+0.333 p=1.000; asc+shuffle (primary): tau_fee=-0.333 p=0.495 tau_send=+0.000 p=1.000; desc (consistency only): tau_fee=-0.333 p=1.000 tau_send=-0.333 p=1.000 |
| AgaveBam | 5 | 23 | +0.747 | 0.000 | 0.000 | 1.000 | H1 fee rule | asc (primary): tau_fee=+0.578 p=0.018 tau_send=-0.578 p=0.018; asc+shuffle (primary): tau_fee=+0.747 p=0.000 tau_send=-0.093 p=0.633; desc (consistency only): tau_fee=+0.267 p=0.310 tau_send=+0.133 p=0.629 |
| FireBAM | 3 | 13 | +0.156 | 0.598 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.333 p=0.746 tau_send=-0.333 p=0.746; asc+shuffle (primary): tau_fee=+0.156 p=0.598 tau_send=-0.333 p=0.229; desc (consistency only): tau_fee=+1.000 p=0.332 tau_send=+1.000 p=0.332 |
| Firedancer | 4 | 19 | +0.433 | 0.040 | 0.240 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.667 p=0.029 tau_send=-0.567 p=0.070; asc+shuffle (primary): tau_fee=+0.433 p=0.040 tau_send=-0.183 p=0.396 |
| Frankendancer | 1 | 3 | -0.333 | 1.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=-0.333 p=1.000 tau_send=-1.000 p=0.334; desc (consistency only): tau_fee=-0.267 p=0.464 tau_send=-0.267 p=0.444 |
| HarmonicAgave | 4 | 20 | +0.650 | 0.001 | 0.008 | 1.000 | H1 fee rule | asc (primary): tau_fee=+0.800 p=0.085 tau_send=-0.800 p=0.085; asc+shuffle (primary): tau_fee=+0.650 p=0.001 tau_send=-0.150 p=0.521; desc (consistency only): tau_fee=+0.267 p=0.555 tau_send=+0.267 p=0.555 |
| HarmonicFiredancer | 10 | 44 | +0.467 | 0.002 | 0.011 | 1.000 | H1 fee rule | asc (primary): tau_fee=+0.453 p=0.032 tau_send=-0.347 p=0.084; asc+shuffle (primary): tau_fee=+0.467 p=0.002 tau_send=-0.093 p=0.521; desc (consistency only): tau_fee=+0.667 p=0.162 tau_send=+0.667 p=0.162 |
| JitoLabs | 9 | 41 | +0.207 | 0.194 | 0.968 | 1.000 | no rule detected (H0 not rejected) | asc (primary): tau_fee=+0.240 p=0.299 tau_send=-0.240 p=0.299; asc+shuffle (primary): tau_fee=+0.207 p=0.194 tau_send=-0.126 p=0.445; desc (consistency only): tau_fee=+0.133 p=0.582 tau_send=+0.144 p=0.526 |
| Raiku | 0 | 0 | - | - | - | - | insufficient data | asc+shuffle (primary): tau_fee=- p=- tau_send=- p=-; desc (consistency only): tau_fee=-0.800 p=0.085 tau_send=-0.800 p=0.085 |
| Rakurai | 1 | 3 | +0.333 | 1.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) | asc+shuffle (primary): tau_fee=+0.333 p=1.000 tau_send=-1.000 p=0.334; desc (consistency only): tau_fee=+0.244 p=0.199 tau_send=+0.278 p=0.136 |

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
| Frankendancer | FBbqKvwL | multi | 463682239 | 5 | +1.000 | 0.020 | +1.000 | 0.014 |
| AgaveBam | GQzMeEMw | same | 463683466 | 4 | +1.000 | 0.085 | +0.667 | 0.334 |
| JitoLabs | FbYX2uN5 | same | 463683941 | 3 | -1.000 | 0.324 | -1.000 | 0.333 |
| JitoLabs | C8Bey3LK | multi | 463684270 | 5 | +0.000 | 1.000 | +0.000 | 1.000 |
| Agave | 7QQGNm3p | same | 463684315 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| HarmonicFiredancer | pSo1KZXg | same | 463684718 | 4 | +0.333 | 0.758 | +0.000 | 1.000 |
| FireBAM | 9jxgosAf | multi | 463684759 | 4 | -1.000 | 0.089 | -0.667 | 0.320 |
| HarmonicAgave | FBKFWadX | multi | 463684871 | 4 | +1.000 | 0.084 | -1.000 | 0.080 |
| AgaveBam | GzDfKKoZ | multi | 463684970 | 3 | +1.000 | 0.353 | +0.333 | 1.000 |
| HarmonicAgave | Hz5aLvpK | multi | 463685091 | 5 | +0.000 | 1.000 | -0.200 | 0.816 |
| JitoLabs | C8Bey3LK | multi | 463685474 | 4 | -1.000 | 0.076 | +1.000 | 0.083 |
| HarmonicFiredancer | 6yFGGAgY | multi | 463685571 | 5 | +0.400 | 0.501 | -0.400 | 0.473 |
| AgaveBam | GzDfKKoZ | same | 463685614 | 4 | +0.333 | 0.744 | -0.333 | 0.759 |
| HarmonicFiredancer | DrifTrN9 | multi | 463685654 | 4 | +0.000 | 1.000 | +0.000 | 1.000 |
| HarmonicFiredancer | Awes4Tr6 | same | 463685686 | 4 | +1.000 | 0.081 | +0.667 | 0.323 |
| HarmonicFiredancer | Awes4Tr6 | same | 463685875 | 5 | +1.000 | 0.009 | -1.000 | 0.011 |
| Raiku | 9xcXe4WR | same | 463686379 | 5 | -0.800 | 0.083 | -0.800 | 0.077 |
| Agave | 5Us18hLZ | multi | 463686415 | 5 | -0.400 | 0.474 | -0.400 | 0.493 |
| Frankendancer | 4SNKY7GC | same | 463686629 | 3 | -0.333 | 1.000 | -1.000 | 0.335 |
| HarmonicFiredancer | pSo1KZXg | multi | 463686659 | 4 | -0.333 | 0.762 | +0.333 | 0.740 |
| JitoLabs | FbYX2uN5 | same | 463687041 | 4 | +0.333 | 0.747 | +0.333 | 0.757 |
| JitoLabs | C8Bey3LK | multi | 463687075 | 4 | -0.667 | 0.325 | -0.667 | 0.349 |
| Frankendancer | FBbqKvwL | same | 463687419 | 5 | -0.200 | 0.811 | -0.200 | 0.830 |
| FireBAM | 9jxgosAf | multi | 463687454 | 5 | -0.400 | 0.479 | -0.200 | 0.803 |
| JitoLabs | GnC339vk | multi | 463688175 | 5 | -0.800 | 0.087 | -0.200 | 0.826 |
| Rakurai | ana2y2Yv | multi | 463688295 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |
| JitoLabs | 5pPRHnie | same | 463688486 | 5 | +0.400 | 0.479 | +0.400 | 0.477 |
| HarmonicFiredancer | pSo1KZXg | same | 463689822 | 3 | +1.000 | 0.327 | +1.000 | 0.324 |
| JitoLabs | 5pPRHnie | same | 463689951 | 5 | +0.400 | 0.502 | -0.400 | 0.490 |
| Frankendancer | FBbqKvwL | multi | 463689994 | 5 | +1.000 | 0.010 | +1.000 | 0.015 |
| HarmonicFiredancer | 6yFGGAgY | multi | 463690099 | 4 | +1.000 | 0.072 | -1.000 | 0.085 |
| JitoLabs | 5pPRHnie | same | 463690651 | 4 | -0.333 | 0.754 | +0.333 | 0.748 |
| HarmonicAgave | Hz5aLvpK | multi | 463690767 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| HarmonicAgave | 3psxMyr7 | same | 463691135 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |
| HarmonicFiredancer | 6yFGGAgY | multi | 463691175 | 3 | +1.000 | 0.333 | -0.333 | 1.000 |
| AgaveBam | GBQ2GvTz | same | 463691203 | 5 | +0.400 | 0.498 | -0.400 | 0.476 |
| AgaveBam | 9rkJMARq | multi | 463691393 | 5 | +0.600 | 0.229 | -0.600 | 0.235 |
| Agave | 7QQGNm3p | multi | 463700099 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| Agave | 5Us18hLZ | multi | 463700388 | 3 | +0.333 | 1.000 | -1.000 | 0.346 |
| HarmonicFiredancer | 6yFGGAgY | same | 463700564 | 4 | +0.667 | 0.318 | -0.333 | 0.754 |
| Agave | 7QQGNm3p | multi | 463700965 | 3 | -1.000 | 0.344 | +1.000 | 0.318 |
| Rakurai | ana2y2Yv | same | 463701279 | 3 | +0.333 | 1.000 | -1.000 | 0.330 |
| Rakurai | 7PdKhpKz | same | 463701413 | 3 | +0.333 | 1.000 | +0.333 | 1.000 |
| Frankendancer | FBbqKvwL | same | 463701720 | 4 | -0.333 | 0.744 | -0.333 | 0.744 |
| JitoLabs | GnC339vk | multi | 463702042 | 3 | +0.333 | 1.000 | -1.000 | 0.340 |
| Firedancer | 4VRs6A9z | multi | 463702191 | 3 | -1.000 | 0.340 | -1.000 | 0.338 |
| HarmonicAgave | 3psxMyr7 | multi | 463702488 | 4 | +0.333 | 0.733 | +0.333 | 0.737 |
| HarmonicFiredancer | Awes4Tr6 | same | 463702579 | 4 | -0.333 | 0.770 | -0.333 | 0.746 |
| Frankendancer | FBbqKvwL | multi | 463703135 | 3 | -1.000 | 0.334 | -1.000 | 0.335 |
| JitoLabs | 5pPRHnie | same | 463703538 | 3 | +1.000 | 0.325 | +1.000 | 0.337 |
| JitoLabs | GnC339vk | same | 463703665 | 5 | +0.000 | 1.000 | -0.800 | 0.087 |
| Agave | 5Us18hLZ | same | 463704443 | 3 | +0.333 | 1.000 | -0.333 | 1.000 |
| HarmonicAgave | 3psxMyr7 | multi | 463704499 | 3 | -0.333 | 1.000 | +0.333 | 1.000 |
| Frankendancer | FBbqKvwL | multi | 463704596 | 3 | +0.333 | 1.000 | -1.000 | 0.329 |
| JitoLabs | C8Bey3LK | same | 463704659 | 3 | +0.333 | 1.000 | -0.333 | 1.000 |
| Agave | mds4GEui | multi | 463704704 | 3 | -0.333 | 1.000 | -0.333 | 1.000 |
| JitoLabs | 5pPRHnie | same | 463704798 | 4 | +0.667 | 0.323 | +0.667 | 0.333 |
| HarmonicAgave | Hz5aLvpK | same | 463704984 | 5 | +0.000 | 1.000 | +0.600 | 0.230 |
| Rakurai | ana2y2Yv | same | 463705147 | 4 | +0.333 | 0.751 | +0.333 | 0.729 |
| HarmonicFiredancer | Awes4Tr6 | same | 463705239 | 4 | +0.333 | 0.750 | -0.333 | 0.758 |
| FireBAM | LA1NEzry | same | 463705494 | 3 | +1.000 | 0.340 | +1.000 | 0.344 |
| FireBAM | LA1NEzry | multi | 463705615 | 3 | +1.000 | 0.325 | +0.333 | 1.000 |
| HarmonicFiredancer | DrifTrN9 | multi | 463705826 | 3 | +0.333 | 1.000 | +1.000 | 0.326 |

## Pooled per client label (primary: target window and target leader)

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 12 | 44 | -0.406 | -0.144 | 0.014 | 0.391 |
| AgaveBam | 15 | 69 | +0.391 | -0.009 | 0.002 | 0.947 |
| FireBAM | 8 | 33 | +0.183 | -0.117 | 0.324 | 0.534 |
| Firedancer | 12 | 57 | +0.311 | -0.094 | 0.011 | 0.466 |
| Frankendancer | 7 | 28 | +0.067 | -0.219 | 0.740 | 0.285 |
| HarmonicAgave | 19 | 84 | +0.421 | -0.091 | 0.000 | 0.390 |
| HarmonicFiredancer | 22 | 92 | +0.455 | -0.088 | 0.000 | 0.415 |
| JitoLabs | 22 | 95 | +0.061 | -0.115 | 0.568 | 0.269 |
| Raiku | 1 | 5 | -0.800 | -0.800 | 0.085 | 0.085 |
| Rakurai | 10 | 43 | +0.293 | +0.120 | 0.057 | 0.464 |

## Grouped results by payer arm and order mode (exploratory)

| label | grouped by | group | bursts | txs | mean tau_fee | pooled p_fee | mean tau_send | pooled p_send |
|---|---|---|---|---|---|---|---|---|
| Agave | payer_arm | multi | 9 | 35 | -0.430 | 0.016 | -0.156 | 0.412 |
| Agave | payer_arm | same | 3 | 9 | -0.333 | 0.541 | -0.111 | 0.916 |
| Agave | order_mode | asc | 3 | 11 | -0.800 | 0.009 | +0.578 | 0.075 |
| Agave | order_mode | desc | 4 | 14 | -0.400 | 0.185 | -0.350 | 0.259 |
| Agave | order_mode | shuffle | 5 | 19 | -0.173 | 0.505 | -0.413 | 0.105 |
| AgaveBam | payer_arm | multi | 7 | 31 | +0.190 | 0.300 | -0.010 | 0.975 |
| AgaveBam | payer_arm | same | 8 | 38 | +0.567 | 0.000 | -0.008 | 0.958 |
| AgaveBam | order_mode | asc | 4 | 19 | +0.583 | 0.005 | -0.583 | 0.005 |
| AgaveBam | order_mode | desc | 4 | 20 | +0.200 | 0.374 | +0.100 | 0.665 |
| AgaveBam | order_mode | shuffle | 7 | 30 | +0.390 | 0.032 | +0.257 | 0.188 |
| FireBAM | payer_arm | multi | 4 | 17 | +0.000 | 1.000 | -0.233 | 0.387 |
| FireBAM | payer_arm | same | 4 | 16 | +0.367 | 0.158 | +0.000 | 0.975 |
| FireBAM | order_mode | asc | 2 | 9 | +0.367 | 0.286 | -0.367 | 0.286 |
| FireBAM | order_mode | desc | 3 | 10 | +0.333 | 0.439 | +0.222 | 0.537 |
| FireBAM | order_mode | shuffle | 3 | 14 | -0.089 | 0.745 | -0.289 | 0.289 |
| Firedancer | payer_arm | multi | 8 | 38 | +0.250 | 0.115 | -0.050 | 0.742 |
| Firedancer | payer_arm | same | 4 | 19 | +0.433 | 0.040 | -0.183 | 0.396 |
| Firedancer | order_mode | asc | 4 | 19 | +0.533 | 0.015 | -0.483 | 0.030 |
| Firedancer | order_mode | desc | 5 | 23 | +0.120 | 0.568 | +0.000 | 1.000 |
| Firedancer | order_mode | shuffle | 3 | 15 | +0.333 | 0.209 | +0.267 | 0.307 |
| Frankendancer | payer_arm | multi | 4 | 16 | +0.333 | 0.220 | +0.000 | 1.000 |
| Frankendancer | payer_arm | same | 3 | 12 | -0.289 | 0.373 | -0.511 | 0.097 |
| Frankendancer | order_mode | desc | 4 | 19 | +0.367 | 0.100 | +0.367 | 0.099 |
| Frankendancer | order_mode | shuffle | 3 | 9 | -0.333 | 0.561 | -1.000 | 0.004 |
| HarmonicAgave | payer_arm | multi | 13 | 56 | +0.374 | 0.003 | -0.128 | 0.347 |
| HarmonicAgave | payer_arm | same | 6 | 28 | +0.522 | 0.003 | -0.011 | 0.941 |
| HarmonicAgave | order_mode | asc | 7 | 29 | +0.362 | 0.067 | -0.457 | 0.019 |
| HarmonicAgave | order_mode | desc | 6 | 26 | +0.256 | 0.201 | +0.189 | 0.354 |
| HarmonicAgave | order_mode | shuffle | 6 | 29 | +0.656 | 0.000 | +0.056 | 0.782 |
| HarmonicFiredancer | payer_arm | multi | 10 | 41 | +0.400 | 0.011 | -0.233 | 0.150 |
| HarmonicFiredancer | payer_arm | same | 12 | 51 | +0.500 | 0.000 | +0.033 | 0.820 |
| HarmonicFiredancer | order_mode | asc | 9 | 41 | +0.526 | 0.000 | -0.467 | 0.001 |
| HarmonicFiredancer | order_mode | desc | 4 | 16 | +0.533 | 0.040 | +0.383 | 0.144 |
| HarmonicFiredancer | order_mode | shuffle | 9 | 35 | +0.348 | 0.059 | +0.081 | 0.653 |
| JitoLabs | payer_arm | multi | 7 | 31 | -0.190 | 0.309 | -0.324 | 0.081 |
| JitoLabs | payer_arm | same | 15 | 64 | +0.178 | 0.175 | -0.018 | 0.876 |
| JitoLabs | order_mode | asc | 8 | 36 | +0.125 | 0.475 | -0.150 | 0.383 |
| JitoLabs | order_mode | desc | 6 | 23 | +0.133 | 0.582 | +0.144 | 0.526 |
| JitoLabs | order_mode | shuffle | 8 | 36 | -0.058 | 0.717 | -0.275 | 0.097 |
| Raiku | payer_arm | same | 1 | 5 | -0.800 | 0.085 | -0.800 | 0.085 |
| Raiku | order_mode | desc | 1 | 5 | -0.800 | 0.085 | -0.800 | 0.085 |
| Rakurai | payer_arm | multi | 3 | 13 | +0.378 | 0.230 | +0.178 | 0.584 |
| Rakurai | payer_arm | same | 7 | 30 | +0.257 | 0.170 | +0.095 | 0.620 |
| Rakurai | order_mode | desc | 9 | 40 | +0.289 | 0.071 | +0.244 | 0.132 |
| Rakurai | order_mode | shuffle | 1 | 3 | +0.333 | 1.000 | -1.000 | 0.334 |

## Sensitivity: all landed (any leader)

Same statistic as the primary pooled table, but using every landed row regardless of `in_target_window` or `leader_is_target`. This is exploratory and shows how much the result depends on the leader filter.

| label | bursts | txs | mean tau_fee | mean tau_send | pooled p_fee | pooled p_send |
|---|---|---|---|---|---|---|
| Agave | 17 | 63 | -0.220 | -0.165 | 0.113 | 0.237 |
| AgaveBam | 30 | 124 | +0.251 | +0.020 | 0.004 | 0.837 |
| FireBAM | 15 | 59 | +0.067 | -0.027 | 0.623 | 0.860 |
| Firedancer | 18 | 78 | +0.296 | -0.107 | 0.013 | 0.374 |
| Frankendancer | 11 | 42 | +0.224 | +0.164 | 0.183 | 0.332 |
| HarmonicAgave | 31 | 126 | +0.209 | -0.030 | 0.029 | 0.741 |
| HarmonicFiredancer | 32 | 128 | +0.450 | -0.058 | 0.000 | 0.528 |
| JitoLabs | 35 | 139 | +0.128 | -0.137 | 0.169 | 0.133 |
| Raiku | 1 | 5 | -0.800 | -0.800 | 0.085 | 0.085 |
| Rakurai | 22 | 83 | +0.330 | +0.055 | 0.007 | 0.656 |
| Unknown(35988) | 2 | 6 | -0.333 | +0.000 | 0.513 | 1.000 |

## Landing and timing

Live timing uses live-only denominators. Dry-run timing is shown in separate columns so it cannot inflate a live rate. `on_time` means the per-tx estimated send slot was before `window_start`; `in_window_at_send` means the send was not after the window (`est_slot_at_send < window_start + 4`). The clearer `send_phase` column is `early` when `est_slot_at_send < window_start`, `inside` when it is in the four-slot window, and `late` otherwise.

| label | sent | live sent | landed | landing rate | live on_time | on_time rate | live in_window | in_window rate | mean live send_offset | dry sent | dry on_time | dry on_time rate | dry in_window | dry in_window rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Agave | 115 | 115 | 109 | 0.948 | 115 | 1.000 | 115 | 1.000 | -3.043 | 0 | 0 | - | 0 | - |
| AgaveBam | 205 | 205 | 199 | 0.971 | 205 | 1.000 | 205 | 1.000 | -2.829 | 0 | 0 | - | 0 | - |
| FireBAM | 115 | 115 | 112 | 0.974 | 115 | 1.000 | 115 | 1.000 | -2.826 | 0 | 0 | - | 0 | - |
| Firedancer | 100 | 100 | 96 | 0.960 | 100 | 1.000 | 100 | 1.000 | -2.300 | 0 | 0 | - | 0 | - |
| Frankendancer | 85 | 85 | 81 | 0.953 | 85 | 1.000 | 85 | 1.000 | -2.529 | 0 | 0 | - | 0 | - |
| HarmonicAgave | 240 | 240 | 229 | 0.954 | 240 | 1.000 | 240 | 1.000 | -2.875 | 0 | 0 | - | 0 | - |
| HarmonicFiredancer | 190 | 190 | 184 | 0.968 | 190 | 1.000 | 190 | 1.000 | -2.842 | 0 | 0 | - | 0 | - |
| JitoLabs | 235 | 235 | 228 | 0.970 | 235 | 1.000 | 235 | 1.000 | -2.979 | 0 | 0 | - | 0 | - |
| JitoLabs+BAM | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -5.000 | 0 | 0 | - | 0 | - |
| Raiku | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -2.000 | 0 | 0 | - | 0 | - |
| Rakurai | 125 | 125 | 124 | 0.992 | 125 | 1.000 | 125 | 1.000 | -2.600 | 0 | 0 | - | 0 | - |
| Unknown(35988) | 10 | 10 | 10 | 1.000 | 10 | 1.000 | 10 | 1.000 | -1.000 | 0 | 0 | - | 0 | - |
| Unknown(55997) | 5 | 5 | 5 | 1.000 | 5 | 1.000 | 5 | 1.000 | -5.000 | 0 | 0 | - | 0 | - |

### Landing by fee level (live only)

| cu_price (micro/CU) | live sent | landed | landing rate | live on_time | on_time rate |
|---|---|---|---|---|---|
| 0 | 287 | 271 | 0.944 | 287 | 1.000 |
| 1000 | 287 | 280 | 0.976 | 287 | 1.000 |
| 10000 | 287 | 283 | 0.986 | 287 | 1.000 |
| 100000 | 287 | 283 | 0.986 | 287 | 1.000 |
| 1000000 | 287 | 270 | 0.941 | 287 | 1.000 |

### Selected sample: our txs in the target window per burst

The primary test only uses groups with **at least 3** of our transactions co-landed in the target block. This table counts, for each live burst, how many of its transactions landed anywhere in the target window (not necessarily in the same block). Bursts with 0-2 are under-represented in the ordering tests. If higher-fee transactions also land more often, the primary sample is biased toward higher fees; that selection effect is a limitation, not a finding.

| label | live bursts | 0 | 1 | 2 | 3 | 4 | 5 | mean landed in target window |
|---|---|---|---|---|---|---|---|---|
| Agave | 23 | 10 | 0 | 0 | 5 | 1 | 7 | 2.35 |
| AgaveBam | 41 | 18 | 4 | 3 | 0 | 2 | 14 | 2.15 |
| FireBAM | 23 | 7 | 3 | 2 | 1 | 2 | 8 | 2.52 |
| Firedancer | 20 | 7 | 0 | 0 | 0 | 1 | 12 | 3.20 |
| Frankendancer | 17 | 8 | 1 | 1 | 0 | 2 | 5 | 2.12 |
| HarmonicAgave | 48 | 18 | 3 | 5 | 4 | 5 | 13 | 2.29 |
| HarmonicFiredancer | 38 | 9 | 3 | 2 | 1 | 6 | 17 | 3.13 |
| JitoLabs | 47 | 19 | 2 | 1 | 2 | 7 | 16 | 2.51 |
| JitoLabs+BAM | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 2 |
| Raiku | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |
| Rakurai | 25 | 14 | 0 | 1 | 0 | 2 | 8 | 2 |
| Unknown(35988) | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| Unknown(55997) | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 2 |

## Verified leader windows

Only windows whose `window_end` is before the current finalized slot count as verified. `leaders_ok` = the target held all 4 slots; `block_slots` = slots in those windows that actually produced a block; `planned` = not yet elapsed, not counted as verified.

| label | windows | leaders_ok | windows with blocks | block_slots | planned |
|---|---|---|---|---|---|
| Agave | 31 | 31 | 31 | 124 | 80 |
| AgaveBam | 72 | 72 | 72 | 288 | 173 |
| FireBAM | 41 | 41 | 41 | 164 | 79 |
| Firedancer | 46 | 46 | 46 | 184 | 99 |
| Frankendancer | 24 | 24 | 24 | 96 | 76 |
| HarmonicAgave | 83 | 83 | 83 | 332 | 168 |
| HarmonicFiredancer | 77 | 77 | 77 | 308 | 152 |
| JitoLabs | 83 | 83 | 83 | 332 | 168 |
| JitoLabs+BAM | 2 | 2 | 2 | 8 | 15 |
| Raiku | 6 | 6 | 6 | 24 | 18 |
| Rakurai | 52 | 52 | 52 | 208 | 94 |
| Unknown(35988) | 2 | 2 | 2 | 8 | 2 |
| Unknown(55997) | 1 | 1 | 1 | 4 | 2 |

## Whole-block priority ordering (APPROXIMATION)

Priority fee per CU is approximated as `(fee - 5000*num_sigs)*1e6/cu_consumed` for non-vote txs.
The base-fee subtraction and CU attribution are not exact; treat this as a rough check only.
Positive tau = higher approximate priority fee appears earlier in the block.

| label | slots | mean tau_priority (approx) | non-vote txs |
|---|---|---|---|
| Agave | 52 | +0.025 | 13115 |
| AgaveBam | 87 | +0.020 | 24092 |
| FireBAM | 54 | +0.045 | 14465 |
| Firedancer | 30 | -0.030 | 11388 |
| Frankendancer | 40 | +0.035 | 10171 |
| HarmonicAgave | 110 | +0.013 | 35891 |
| HarmonicFiredancer | 77 | +0.020 | 21544 |
| JitoLabs | 102 | +0.009 | 28589 |
| JitoLabs+BAM | 4 | -0.018 | 1309 |
| Raiku | 1 | +0.071 | 203 |
| Rakurai | 52 | +0.010 | 14480 |
| Unknown(35988) | 5 | -0.021 | 1201 |
| Unknown(55997) | 3 | -0.002 | 839 |

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
