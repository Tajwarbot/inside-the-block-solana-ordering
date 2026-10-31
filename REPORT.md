# Inside the Block: ordering of our own transactions in Solana leader windows

**Author:** Taki Tajwar

**Repository:** https://github.com/Tajwarbot/inside-the-block-solana-ordering

**Measurement network:** Solana mainnet-beta, post-Alpenglow (upgrade on 2026-10-21)

## Measurement dates

All times are UTC. A session is one `OBP_DATA=data/runs/<YYYYMMDD>_<name>` directory.

| Session | Purpose | UTC send window | Slots | Bursts sent | Txs sent | Landed | In target window with target leader | Data directory |
|---|---|---|---|---|---|---|---|---|
| Pilot lead 1 | Pipeline and landing-rate check, lead 1 | 2026-10-25 18:22:43 to 18:23:44 | 461357406 to 461357694 | 4 (1 skipped by the start guard) | 20 | 20 | 18 | `data/runs/20261026_pilot_lead1` |
| Pilot lead 2 | Pipeline and landing-rate check, lead 2 (chosen for the main run) | 2026-10-25 18:24:39 to 18:25:30 | 461357958 to 461358199 | 5 | 25 | 25 | 25 | `data/runs/20261026_pilot_lead2` |
| Main, sequential send, alternate arm | Primary measurement; same-payer and multi-payer bursts alternate within one run | 2026-10-25 18:28:40 to 18:59:20 | 461359096 to 461367759 | 125 (144 attempts, 19 skipped; same 63, multi 62) | 625 | 625 | 611 | `data/runs/20261025_1828_main` |
| Parallel send, alternate arm | Exploratory, added after the main run to put all five transactions in front of the scheduler together | 2026-10-25 19:07:36 to 19:22:39 | 461370096 to 461374317 | 66 (72 attempts, 6 skipped; same 33, multi 33) | 330 | 325 | 325 | `data/runs/20261025_1907_parallel` |
| Parallel follow-up 2, lead 2 | Follow-up design: same parallel send, larger, different time of day | 2026-10-31 12:04:42 to 12:41:22 | 463681940 to 463692220 | 113 (200 attempts, 87 skipped; same 55, multi 58) | 565 | 558 | 175 | `data/runs/20261031_par2_parallel` |
| Parallel follow-up 3, lead 2 | Same as follow-up 2; stopped after 12 bursts because nothing landed in the target window | 2026-10-31 12:57:20 to 13:06:21 | 463696708 to 463699236 | 12 (same 6, multi 6) | 60 | 60 | 0 | `data/runs/20261031_par3_parallel` |
| Parallel follow-up 4, lead 6 | Same as follow-up 2 with lead raised to 6 slots after the lead 2 sessions landed late | 2026-10-31 13:08:49 to 13:30:14 | 463699928 to 463705916 | 96 (110 attempts, 14 skipped; same 51, multi 45) | 480 | 444 | 206 | `data/runs/20261031_par4_parallel_lead6` |

The planned sequential repeat (half size) was never run. The 2026-10-31 parallel sessions replace it as the second time-of-day sample, but they use the parallel design, not the sequential one, so they do not repeat the pre-registered test.

The pilot and fund directory names use the Dhaka date (20261026), but their sends were on 2026-10-25 UTC. Pilot lead 2 had 20/25 on time; lead 1 had 7/20. Lead 2 was chosen.

## Setup

The live main run targeted 17 validators and 9 labels. The table below is the live target set from `data/runs/20261025_1828_main/validators.csv`, filtered to the target identities in `data/runs/20261025_1828_main/sent.csv`.

| # | Identity | clientId | Version | Active stake (SOL) | Label used in results |
|---:|---|---|---|---:|---|
| 1 | dxa6QFqLcByyHykLCAW5tv1VYNVQFV3v6oovM2h8inH | Agave | 4.3.2 | 191739.8 | Agave |
| 2 | rsbp8zMHbGCpLoRktmsjspYv77VcjxAzH1KxPCD9BiU | Agave | 4.3.2 | 259143.7 | Agave |
| 3 | 6y7V8dL673XFzm9QyC5vvh3itWkp7wztahBd2yDqsyrK | AgaveBam | 4.3.2 | 2916668.7 | AgaveBam |
| 4 | Fc6NNdS2j3EmrWbU6Uqt6wsKB5ef72NjaWfNxKYbULGD | AgaveBam | 4.3.2 | 4319078.0 | AgaveBam |
| 5 | A4hyMd3FyvUJSRafDUSwtLLaQcxRP4r1BRC9w2AJ1to2 | FireBAM | 26.10.4 | 354415.6 | FireBAM |
| 6 | SSmBEooM7RkmyuXxuKgAhTvhQZ36Z3G2WsmLGJKoQLY | FireBAM | 26.10.4 | 303811.3 | FireBAM |
| 7 | 9eGrDohdNTAo61DRHyfMuqKWXqYnA3i254Wiszxe8FoY | Firedancer | 26.10.4 | 7038249.3 | Firedancer |
| 8 | JD549HsbJHeEKKUrKgg4Fj2iyv2RGjsV7NTZjZUrHybB | Firedancer | 26.10.4 | 6608866.5 | Firedancer |
| 9 | BtsmiEEvnSuUnKxqXj2PZRYpPJAc7C34mGz8gtJ1DAaH | HarmonicAgave | 4.3.2 | 4063118.3 | HarmonicAgave |
| 10 | Fd7btgySsrjuo25CJCj7oE7VPMyezDhnx7pZkj2v69Nk | HarmonicAgave | 4.3.2 | 17099112.7 | HarmonicAgave |
| 11 | 6ptuwW4rg5A3wP9hNKxeymG3QhSagugPd3grnMTGJwWG | HarmonicFiredancer | 26.10.4 | 1265525.2 | HarmonicFiredancer |
| 12 | 87CcUxpyR72ZyfaZirj86mqkbk5uuU2EfnwTegVMLJL5 | HarmonicFiredancer | 26.10.4 | 3830697.3 | HarmonicFiredancer |
| 13 | 5pPRHniefFjkiaArbGX3Y8NUysJmQ9tMZg3FrFGwHzSm | JitoLabs | 4.3.2 | 5973284.7 | JitoLabs |
| 14 | C8Bey3LKVJHVqN6xPTeW8WJfUgFQAeGNBpT4Rp99JP1k | JitoLabs | 4.3.2 | 9216836.6 | JitoLabs |
| 15 | 3B2mGaZoFwzAnWCoZ4EAKdps4FbYbDKQ48jo8u1XWynU | Rakurai | 4.3.2 | 190902.5 | Rakurai |
| 16 | 7PdKhpKz7T39vZHFL1UfcYNDsLvay6hp4KPQq1aUckFf | Rakurai | 4.3.2 | 770106.5 | Rakurai |
| 17 | Diman2GphWLwECE3swjrAEAJniezpYLxK1edUydiDZau | Unknown(35832) | 4.3.2 | 342645.8 | Unknown(35832) |

Source: `data/runs/20261025_1828_main/validators.csv` and `data/runs/20261025_1828_main/sent.csv`. Stake and version change over time, so the inventory timestamp matters. The parallel session targeted 15 validators and 8 labels; it did not send to the Unknown validator.

Sending setup:

| Item | Value |
|---|---|
| Probe transaction | SPL Memo, one signature, fixed CU limit |
| CU limit | 21,000 |
| Fee ladder (micro-lamports/CU) | 0, 1,000, 10,000, 100,000, 1,000,000 |
| Rotations | ascending, descending, shuffled, rotating by burst |
| Payer arms | alternate (same and multi by burst index; same 63, multi 62 in the main run) |
| Lead slots | 2 (blockhash and signing prepared 6 slots earlier) |
| Send path | Public RPC `https://api.mainnet-beta.solana.com` for both reads and `sendTransaction`. No `SEND_RPC_URL`, no paid or staked RPC. |
| `skipPreflight` / `maxRetries` | true / 0 |
| Spend ledger | 32,367,351 lamports reserved of the 35,000,000 ledger cap after all sessions (project budget 0.04 SOL). Session caps were 0.03 (main) and 0.035 (all parallel sessions) SOL. The ledger reserves the worst case per burst, so it is above real spend. Actual SOL burned: 19,760,964 lamports (0.01976 SOL) from 0.045 SOL funded; 25,239,036 lamports remain across the five payers. |
| Funding | 4 transfers of 3,000,000 lamports from payer to payer2..5 (`data/runs/20261026_fund`) |
| Ledger location | Global per cluster at `$OBP_LEDGER_DIR/spend_ledger_<cluster>.json` (default `data` root, `/data` in Docker); session copy in `spend_ledger_snapshot.json` |

## Method summary

Each burst contains five memo transactions with the same instructions and the same CU limit, and five different priority fees. The five fee levels are sent in ascending, descending or shuffled order, rotating by burst. Descending sends the highest fee first, so fee order and send order are aligned there (the confounded rotation). Ascending sends it last, so the two are opposed (the discriminating rotation). In the same-payer arm all five use one fee payer, forcing a write-lock serialisation. In the multi-payer arm they use different payers, removing the lock conflict.

The planner selects future four-slot leader windows for validators from several client labels. The sender prebuilds and signs the burst six slots before the send, waits until `window_start - lead_slots` (default 2) with 0.05 s polling near the window, and sends with `skipPreflight` and `maxRetries: 0`. If the final wait returns at or after the window start, the burst is skipped before any fee is reserved. In `alternate` mode same-payer and multi-payer bursts alternate by burst index within one run, so time of day does not confound the arms. `verify-windows` confirms the target actually led the window. `collect` records the landing slot, actual leader, ledger index and every transaction in the landing block. Each row, including its signature, is flushed and fsynced to `sent.csv` immediately after its own send, before any post-send RPC. `send_ts_ns` is taken immediately before the HTTP send and `send_done_ns` immediately after it; `send_phase` is `early`, `inside` or `late`, and `burst_late` marks a post-send slot at or after `window_start + 4`. The missing-slot sentinel is restricted to read methods; a `sendTransaction` result must be a signature string and must equal the transaction's own signature, otherwise it is recorded as `error:signature-mismatch`.

The primary statistic is Kendall tau of ledger index against fee, and against actual send order, within target-block groups that contain at least three of our five transactions. Primary tests keep only rows whose landing slot was inside the planned window and whose actual leader was the planned target. Permutation p-values are reported per burst and pooled per client label. The whole-block check is supplementary and uses an approximate priority fee per CU.

Only bursts where at least three of our five transactions co-landed in the target block enter the tau tests. Higher-fee transactions may land more often, so this conditions on landing and can bias the ordering sample toward higher fees. That is a selection effect, not a finding; `results.md` reports the landed-per-burst distribution so the reader can judge it.

Pre-specification: the primary test below was fixed in `obp/analyze.py` at commit `c08a131` (2026-10-25 17:13 UTC), about 70 minutes before the first live send (pilot, 18:22 UTC). It is not the same as the early design notes, which planned H1 over all three rotations, lead 1 and separate same and multi arms. Deviations from those notes: lead 2 (chosen by the pilot), the alternate arm in one run, and descending excluded from the primary set. "Pre-registered" in this report means pre-specified in code before live data, not a public registration.

The pre-registered primary test is the pooled mean `tau_fee` per client label on the same-payer arm, using only ascending + shuffled bursts and only target-window rows with the planned leader. Holm correction is applied across the per-label primary p-values, separately for H1 (fee) and H2 (send order). Descending bursts are excluded from the primary test because there fee order equals send order (confounded); they are a consistency check only. All other cuts are exploratory. The per-label verdict rule is: H1 if pooled mean `tau_fee > 0` with Holm-adjusted `p < 0.05` and `tau_fee > 0` on ascending bursts alone; H2 if pooled mean `tau_send > 0` with Holm-adjusted `p < 0.05` and `tau_send > 0` on ascending bursts alone; mixed if both H1 and H2 markers hold; "no rule detected (H0 not rejected)" if neither holds; "insufficient data" if there are no primary groups.

## Results

The main sequential session is `data/runs/20261025_1828_main`. The pre-registered primary set is the same-payer arm with ascending + shuffled bursts and target-window rows with the planned leader. Everything else, including the multi-payer arm, descending bursts, per-burst cuts, landing rates, the whole-block check and all parallel sessions, is exploratory. The parallel sessions are a follow-up design chosen after the main run. They reuse the same primary filter and verdict rule, but that rule was not pre-registered for them.

### Leader schedule and leader types/clients

Targeted labels in the main run: Agave, AgaveBam, FireBAM, Firedancer, HarmonicAgave, HarmonicFiredancer, JitoLabs, Rakurai and Unknown(35832).

| Label | Validators targeted | Bursts sent | Verified windows | Target led all 4 slots | Window slots producing a block |
|---|---:|---:|---:|---:|---:|
| Agave | 2 | 5 | 5 | 5 | 20 |
| AgaveBam | 2 | 20 | 32 | 32 | 128 |
| FireBAM | 2 | 8 | 8 | 8 | 32 |
| Firedancer | 2 | 24 | 31 | 31 | 124 |
| HarmonicAgave | 2 | 22 | 34 | 34 | 136 |
| HarmonicFiredancer | 2 | 18 | 23 | 23 | 92 |
| JitoLabs | 2 | 24 | 31 | 31 | 124 |
| Rakurai | 2 | 3 | 7 | 7 | 28 |
| Unknown(35832) | 1 | 1 | 1 | 1 | 4 |

Verified windows come from `windows.csv` and include planned windows that the max-bursts limit did not reach, so they can exceed bursts sent. Every elapsed window had the scheduled target in all four slots, and every slot in those windows produced a block. Agave (5 windows), FireBAM (8) and Rakurai (7) are small per-label window samples. Unknown(35832) has one window and is excluded from conclusions.

### Path from backend to the executing node

Main sequential session, 625 sends, 625 landed, 611 in the target window with the target leader.

| Label | Live sends | Landed | Landing rate | On time (estimated send slot before window) | Not after window end |
|---|---:|---:|---:|---:|---:|
| Agave | 25 | 25 | 1.000 | 18 | 25 |
| AgaveBam | 100 | 100 | 1.000 | 83 | 100 |
| FireBAM | 40 | 40 | 1.000 | 34 | 40 |
| Firedancer | 120 | 120 | 1.000 | 102 | 120 |
| HarmonicAgave | 110 | 110 | 1.000 | 101 | 110 |
| HarmonicFiredancer | 90 | 90 | 1.000 | 69 | 90 |
| JitoLabs | 120 | 120 | 1.000 | 106 | 120 |
| Rakurai | 15 | 15 | 1.000 | 10 | 15 |
| Unknown(35832) | 5 | 5 | 1.000 | 4 | 5 |

Not after window end is 625/625 overall and matches the live sent count for every label in `results.md`.

| Fee level (micro/CU) | Live sends | Landed | Landing rate | On time |
|---:|---:|---:|---:|---:|
| 0 | 125 | 125 | 1.000 | 101 |
| 1,000 | 125 | 125 | 1.000 | 112 |
| 10,000 | 125 | 125 | 1.000 | 111 |
| 100,000 | 125 | 125 | 1.000 | 109 |
| 1,000,000 | 125 | 125 | 1.000 | 94 |

Every fee level landed 125/125 in the main run. The on-time count falls at the 1,000,000 level because that level is sent last in ascending bursts, so it is later in time, not because of the fee. What we can observe is the send offset, landing rate and actual leader. The RPC forwarding path, SWQoS admission and relay behaviour are not observable here.

### Our transactions' interaction with each other

Main session, target-window rows with the planned leader, all three rotations. A group is a burst-block group with at least three of our five transactions in the same block.

| Arm | Groups | Txs | Mean tau_fee | Mean tau_send |
|---|---:|---:|---:|---:|
| Same payer | 51 | 156 | -0.111 | +0.987 |
| Multi payer | 44 | 135 | -0.008 | +0.977 |

Per-label pooled p-values are in `results.md` and `results_by_group.csv`; this table does not pool p-values across labels. In both arms `tau_send` is near +1, so send order predicts position regardless of the payer lock. `tau_fee` is near zero in both arms. The arms do not separate a fee rule from an arrival rule here because the sequential burst is spread over about two slots, so the five fee levels are not in one scheduler batch.

### Competition inside the block

Main session, all non-vote transactions in the landing blocks. Priority fee per CU is approximate.

| Label | Blocks checked | Non-vote txs | Mean tau_priority (approx) | Notes |
|---|---:|---:|---:|---|
| Agave | 13 | 5,370 | +0.051 | near zero |
| AgaveBam | 50 | 22,130 | +0.041 | near zero |
| FireBAM | 20 | 6,708 | +0.022 | near zero |
| Firedancer | 55 | 32,759 | -0.060 | largest negative, still small |
| HarmonicAgave | 56 | 25,235 | +0.012 | near zero |
| HarmonicFiredancer | 43 | 17,179 | +0.023 | near zero |
| JitoLabs | 55 | 27,505 | -0.002 | near zero |
| Rakurai | 8 | 4,463 | -0.012 | near zero |
| Unknown(35832) | 3 | 565 | -0.044 | excluded from conclusions |

The main blocks cover 303 slots and 142,740 transactions, with 173 to 1,390 transactions per block and a median of 402. The mean relative position of our transactions in their block is 0.45. Whole-block priority ordering is near zero for every label, between -0.060 and +0.051. The parallel session gives -0.091 to +0.058. This check is approximate because priority fee per CU is inferred from total fee, signature count and CU consumed. It is supplementary to our own transactions, not a replacement for them.

### Send order

Main session, all target-window rows with the planned leader.

| Rotation | Groups | Txs | Mean tau_fee | Mean tau_send | Fee direction | Send-order direction |
|---|---:|---:|---:|---:|---|---|
| Ascending | 32 | 99 | -0.948 | +0.948 | negative in 32/32 | positive in 32/32 |
| Descending | 29 | 90 | +1.000 | +1.000 | positive in 29/29 | positive in 29/29 |
| Shuffled | 34 | 102 | -0.137 | +1.000 | mixed (14/34 positive) | positive in 34/34 |

On ascending bursts, where fee order and send order are opposed, `tau_fee` is negative and `tau_send` is positive for every label. Per label, the ascending means are -1.000 / +1.000 for AgaveBam, FireBAM, Firedancer, HarmonicFiredancer and Rakurai, -0.833 / +0.833 for HarmonicAgave, and -0.909 / +0.909 for JitoLabs. On descending bursts, where the two orders are aligned, the means are +1.000 / +1.000 for every label with descending bursts. On shuffled bursts `tau_fee` ranges from -0.667 to +0.333, while `tau_send` is +1.000. Ascending is the discriminating rotation; descending is the consistency check.

Pooled across all modes and arms with the primary filters:

| Label | Bursts | Txs | Mean tau_fee | Mean tau_send | Pooled p_fee | Pooled p_send |
|---|---:|---:|---:|---:|---:|---:|
| Agave | 3 | 9 | -0.111 | +1.000 | 0.922 | 0.004 |
| AgaveBam | 12 | 36 | -0.111 | +1.000 | 0.554 | 0.000 |
| FireBAM | 7 | 21 | +0.143 | +1.000 | 0.640 | 0.000 |
| Firedancer | 22 | 70 | +0.030 | +1.000 | 0.808 | 0.000 |
| HarmonicAgave | 15 | 45 | +0.289 | +0.956 | 0.102 | 0.000 |
| HarmonicFiredancer | 13 | 39 | -0.026 | +1.000 | 0.868 | 0.000 |
| JitoLabs | 20 | 62 | -0.383 | +0.950 | 0.006 | 0.000 |
| Rakurai | 3 | 9 | -0.778 | +1.000 | 0.027 | 0.004 |

`p` values of 0.000 are below the 0.0005 permutation floor. The pooled fee means are small or negative while the send means are near +1, which is the same pattern as the per-rotation table.

### Where our transactions landed

`scripts/burst_split.py` reads only `landed.csv`. Reproduce with:

```bash
.venv/bin/python scripts/burst_split.py data/runs/20261025_1828_main/landed.csv
.venv/bin/python scripts/burst_split.py data/runs/20261025_1907_parallel/landed.csv
```

Main sequential session: no burst landed all five in one block. The split over slots was 3+2 in 66 bursts, 2+2+1 in 29, 3+1+1 in 24, and 4+1 in 6. Across pairs in different slots, the earlier send was in the earlier slot 818 times and the reverse 2 times. The higher fee was in the earlier slot 411 times and the reverse 409 times. In the 430 same-block pairs, send order was inverted 4 times.

The pilots show the same pattern: lead 1 had 27 versus 0 cross-slot pairs by send order and 8 versus 19 by fee; lead 2 had 33 versus 0 by send order and 16 versus 17 by fee. Lead 1 had 0 inversions in 13 same-block pairs; lead 2 had 0 in 17.

Parallel session: 52 of 66 bursts landed all five in one block. The other splits were 4+1 in 7 bursts and 3+2 in 4; the remaining 3 bursts split 4, 2 and 3+1. There were 588 same-block pairs and 315 send-order inversions. Thread start times are not arrival order there, so the send-order inversion count is expected to be high.

### Parallel-send session (exploratory, added after the main run)

This session used `--send-mode parallel`, 66 bursts and 330 transactions. All five sends in a burst start within a median 7.0 ms (p90 9.7 ms), so they reach the scheduler together. The median HTTP call took 168.3 ms and calls contend, so thread start timestamps are not arrival order. This section is exploratory and was not in the pre-registered plan.

| Label | Validators targeted | Bursts sent | Verified windows | Target led all 4 slots | Window slots producing a block |
|---|---:|---:|---:|---:|---:|
| Agave | 2 | 5 | 5 | 5 | 20 |
| AgaveBam | 2 | 10 | 12 | 12 | 48 |
| FireBAM | 1 | 4 | 6 | 6 | 24 |
| Firedancer | 2 | 11 | 12 | 12 | 48 |
| HarmonicAgave | 2 | 12 | 13 | 13 | 52 |
| HarmonicFiredancer | 2 | 10 | 11 | 11 | 44 |
| JitoLabs | 2 | 8 | 12 | 12 | 48 |
| Rakurai | 2 | 6 | 7 | 7 | 28 |

| Label | Live sends | Landed | Landing rate | On time | Not after window end |
|---|---:|---:|---:|---:|---:|
| Agave | 25 | 25 | 1.000 | 25 | 25 |
| AgaveBam | 50 | 50 | 1.000 | 50 | 50 |
| FireBAM | 20 | 20 | 1.000 | 20 | 20 |
| Firedancer | 55 | 55 | 1.000 | 55 | 55 |
| HarmonicAgave | 60 | 59 | 0.983 | 60 | 60 |
| HarmonicFiredancer | 50 | 47 | 0.940 | 50 | 50 |
| JitoLabs | 40 | 39 | 0.975 | 40 | 40 |
| Rakurai | 30 | 30 | 1.000 | 30 | 30 |

| Fee level (micro/CU) | Live sends | Landed | Landing rate | On time |
|---:|---:|---:|---:|---:|
| 0 | 66 | 65 | 0.985 | 66 |
| 1,000 | 66 | 65 | 0.985 | 66 |
| 10,000 | 66 | 65 | 0.985 | 66 |
| 100,000 | 66 | 65 | 0.985 | 66 |
| 1,000,000 | 66 | 65 | 0.985 | 66 |

The 5 misses were never accepted by the public RPC: burst 61 got HTTP 413 "You have used your data allowance", burst 64 lost 3 sends to "Remote end closed connection", and burst 70 got HTTP 429. Every transaction the RPC accepted landed. Each fee level has the same landing rate, so fee level did not change landing in this session either.

Primary verdicts for the parallel session, same-payer arm, ascending + shuffled:

| Label | Primary bursts | Txs | Mean tau_fee | Holm p_fee | Mean tau_send | Holm p_send | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Agave | 1 | 3 | -1.000 | 0.996 | +0.333 | 1.000 | no rule detected (H0 not rejected) |
| AgaveBam | 2 | 10 | +1.000 | 0.000 | -0.200 | 1.000 | H1 fee rule |
| FireBAM | 3 | 13 | +0.156 | 0.996 | -0.333 | 1.000 | no rule detected (H0 not rejected) |
| Firedancer | 4 | 19 | +0.433 | 0.200 | -0.183 | 1.000 | no rule detected (H0 not rejected) |
| HarmonicAgave | 3 | 15 | +0.867 | 0.000 | -0.400 | 0.654 | H1 fee rule |
| HarmonicFiredancer | 4 | 19 | +0.417 | 0.240 | +0.100 | 1.000 | no rule detected (H0 not rejected) |
| JitoLabs | 4 | 20 | +0.200 | 0.996 | -0.150 | 1.000 | no rule detected (H0 not rejected) |
| Rakurai | 0 | 0 | not available | not available | not available | not available | insufficient data |

Pooled across all modes and arms with the primary leader filter:

| Label | Bursts | Txs | Mean tau_fee | Mean tau_send | Pooled p_fee | Pooled p_send |
|---|---:|---:|---:|---:|---:|---:|
| Agave | 5 | 21 | -0.627 | +0.000 | 0.004 | 1.000 |
| AgaveBam | 10 | 48 | +0.253 | +0.020 | 0.067 | 0.877 |
| FireBAM | 4 | 18 | +0.217 | -0.350 | 0.331 | 0.118 |
| Firedancer | 11 | 54 | +0.430 | -0.012 | 0.001 | 0.930 |
| HarmonicAgave | 12 | 57 | +0.583 | -0.150 | 0.000 | 0.218 |
| HarmonicFiredancer | 9 | 41 | +0.400 | -0.133 | 0.009 | 0.408 |
| JitoLabs | 8 | 38 | +0.208 | -0.233 | 0.190 | 0.140 |
| Rakurai | 6 | 30 | +0.267 | +0.200 | 0.107 | 0.268 |

| Rotation | Groups | Txs | Mean tau_fee | Mean tau_send | Fee direction | Send-order direction |
|---|---:|---:|---:|---:|---|---|
| Ascending | 20 | 95 | +0.433 | -0.457 | positive in 15/20 | negative in 15/20 |
| Descending | 23 | 109 | +0.223 | +0.139 | mixed (16/23 positive) | mixed (14/23 positive) |
| Shuffled | 22 | 103 | +0.230 | +0.042 | mixed (14/22 positive) | mixed (8/22 positive) |

On ascending bursts, where fee and thread start order are opposed, the fee signal is clearer: `tau_fee` is +0.533 (p 0.015) for Firedancer, +0.550 (0.009) for HarmonicAgave, +0.600 (0.005) for HarmonicFiredancer, +0.533 (0.028) for JitoLabs, +1.000 for AgaveBam (1 burst), +0.367 (0.286) for FireBAM, and -0.700 (0.086) for Agave (2 bursts).

Whole-block priority ordering in the parallel session:

| Label | Blocks checked | Non-vote txs | Mean tau_priority (approx) |
|---|---:|---:|---:|
| Agave | 7 | 2,536 | +0.031 |
| AgaveBam | 11 | 4,297 | +0.058 |
| FireBAM | 6 | 2,145 | +0.027 |
| Firedancer | 12 | 6,187 | -0.091 |
| HarmonicAgave | 14 | 5,551 | +0.001 |
| HarmonicFiredancer | 13 | 5,545 | +0.032 |
| JitoLabs | 9 | 3,105 | +0.008 |
| Rakurai | 6 | 1,535 | +0.003 |

The parallel blocks cover 78 slots, with 111 to 806 transactions per block (median 358) and 31,059 transactions in total. Our mean relative position is 0.46. The whole-block means stay between -0.091 and +0.058.

### Parallel follow-up sessions (2026-10-31, follow-up design)

Why: the 2026-10-25 parallel session is the only design that puts the fee ladder in one scheduler batch, but it had 0 to 4 primary bursts per label. The follow-up repeats that design at a different time of day (12:04 to 13:30 UTC versus 19:07 to 19:22 UTC). Same code, same fee ladder, `--payer-arm alternate`, `--send-mode parallel`. This design was chosen after the main run and is not pre-registered. The analysis reuses the pre-registered primary filter and verdict rule unchanged.

What happened: the public RPC was much slower on 2026-10-31. Median `sendTransaction` HTTP time was 1,250 ms (p90 1,625 ms) in follow-up 2, against 168 ms on 2026-10-25. With lead 2, transactions landed 1 to 14 slots after window start (median 7), mostly in the next leader's block. Follow-up 2 had 175 of 558 landed transactions in the target window with the target leader. Follow-up 3 had 0 of 60 and was stopped after 12 bursts. Follow-up 4 raised the lead to 6 slots. That decision was made after seeing the landing offsets and before seeing any tau. Follow-up 4 landed 206 of 444 in the target window; 110 landed 1 to 3 slots early, in the previous leader's block. 36 of 480 did not land: 3 were refused by the RPC (connection aborted) and 33 were accepted but never landed.

| Session | Median send HTTP ms | Landed | In target window, target leader | Bursts with 5 in one block | Same-block pairs | Send-order inversions |
|---|---:|---:|---:|---:|---:|---:|
| 2026-10-25 parallel | 168 | 325/330 | 325 | 52 of 66 | 588 | 315 |
| Follow-up 2 (lead 2) | 1,250 | 558/565 | 175 | 17 of 113 | 496 | 249 |
| Follow-up 3 (lead 2) | 1,292 | 60/60 | 0 | not counted | not counted | not counted |
| Follow-up 4 (lead 6) | 809 | 444/480 | 206 | 9 of 96 | 354 | 194 |

The slow path also spread each burst over more slots, so fewer bursts kept 3 or more transactions in one target block. The target of at least 8 primary bursts per main label was not reached.

Primary verdicts, 2026-10-31 follow-up sessions pooled (2, 3 and 4), same-payer arm, ascending + shuffled:

| Label | Primary bursts | Txs | Mean tau_fee | Raw p_fee | Holm p_fee | Verdict |
|---|---:|---:|---:|---:|---:|---|
| Agave | 1 | 3 | +0.333 | 1.000 | 1.000 | no rule detected (H0 not rejected) |
| AgaveBam | 3 | 13 | +0.578 | 0.029 | 0.174 | no rule detected (H0 not rejected) |
| FireBAM | 0 | 0 | not available | not available | not available | insufficient data |
| Firedancer | 0 | 0 | not available | not available | not available | insufficient data |
| Frankendancer | 1 | 3 | -0.333 | 1.000 | 1.000 | no rule detected (H0 not rejected) |
| HarmonicAgave | 1 | 5 | +0.000 | 1.000 | 1.000 | no rule detected (H0 not rejected) |
| HarmonicFiredancer | 6 | 25 | +0.500 | 0.009 | 0.060 | no rule detected (H0 not rejected) |
| JitoLabs | 5 | 21 | +0.213 | 0.347 | 1.000 | no rule detected (H0 not rejected) |
| Rakurai | 1 | 3 | +0.333 | 1.000 | 1.000 | no rule detected (H0 not rejected) |
| Raiku | 0 | 0 | not available | not available | not available | insufficient data |

Every label with primary data has a positive or zero follow-up `tau_fee` except Frankendancer (1 burst). Raiku has no primary bursts; its 1 descending burst (consistency only) has `tau_fee` -0.800. The follow-up alone is too small for any Holm-significant result.

All four parallel sessions pooled (2026-10-25 plus follow-ups), same primary set. This pooling is stated here as the summary for the parallel design; per-session tables are in each `results.md`:

| Label | Primary bursts | Txs | Mean tau_fee | Raw p_fee | Holm p_fee | Ascending only tau_fee | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Agave | 2 | 6 | -0.333 | 0.495 | 1.000 | -1.000 | no rule detected (H0 not rejected) |
| AgaveBam | 5 | 23 | +0.747 | 0.000 | 0.000 | +0.578 | H1 fee rule |
| FireBAM | 3 | 13 | +0.156 | 0.598 | 1.000 | +0.333 | no rule detected (H0 not rejected) |
| Firedancer | 4 | 19 | +0.433 | 0.040 | 0.240 | +0.667 | no rule detected (H0 not rejected) |
| Frankendancer | 1 | 3 | -0.333 | 1.000 | 1.000 | not available | no rule detected (H0 not rejected) |
| HarmonicAgave | 4 | 20 | +0.650 | 0.001 | 0.008 | +0.800 | H1 fee rule |
| HarmonicFiredancer | 10 | 44 | +0.467 | 0.002 | 0.011 | +0.453 | H1 fee rule |
| JitoLabs | 9 | 41 | +0.207 | 0.194 | 0.968 | +0.240 | no rule detected (H0 not rejected) |
| Rakurai | 1 | 3 | +0.333 | 1.000 | 1.000 | not available | no rule detected (H0 not rejected) |
| Raiku | 0 | 0 | not available | not available | not available | not available | insufficient data |

Holm is applied across the 9 labels with primary data (Raiku has 0 primary bursts). `tau_send` is not Holm-significant for any label in any parallel cut; thread start time is not arrival order there.

Sensitivity, all landed rows regardless of leader (exploratory, all four parallel sessions): pooled `tau_fee` is +0.450 (32 bursts, p 0.000) for HarmonicFiredancer, +0.330 (22, p 0.007) for Rakurai, +0.296 (18, p 0.013) for Firedancer, +0.251 (30, p 0.004) for AgaveBam, +0.209 (31, p 0.029) for HarmonicAgave, +0.128 (35, p 0.169) for JitoLabs, +0.067 (15, p 0.623) for FireBAM and -0.220 (17, p 0.113) for Agave. These rows include blocks from leaders we did not target, so they describe whichever leader built the block.

Whole-block priority ordering stays near zero in the pooled parallel blocks: -0.030 to +0.045 for every label with more than 5 blocks.

Reproduce the pooled tables offline:

```bash
bash scripts/pool_sessions.sh pooled_parallel_all 20261025_1907_parallel 20261031_par2_parallel 20261031_par3_parallel 20261031_par4_parallel_lead6
bash scripts/pool_sessions.sh pooled_parallel_followup 20261031_par2_parallel 20261031_par3_parallel 20261031_par4_parallel_lead6
```

The script concatenates the per-session CSVs (each row keeps its `run` id, so bursts never merge across sessions) and runs `analyze` offline.

### Noise versus rule

The main finding is that with sequential sends, send order decides which block and which position. `tau_send` is +0.889 to +1.000 on the primary set for all 8 labels and Holm-significant for 6 (Agave and FireBAM have 2 primary bursts each and are not significant). Fee has no visible effect. That is not evidence that schedulers ignore fees. The sequential burst spans about two slots (median span 413.8 ms, p90 488.8 ms, median gap 78.9 ms, median HTTP call 56.5 ms; slot time 0.212 s). No sequential burst landed all five in one block, so the fee ladder was never inside one scheduler batch. The pre-registered primary verdicts in the main run mostly measure send order, not fee.

Primary verdicts, main sequential session, same-payer arm, ascending + shuffled:

| Label | Primary bursts | Txs | Mean tau_fee | Holm p_fee | Mean tau_send | Holm p_send | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Agave | 2 | 6 | +0.000 | 1.000 | +1.000 | 0.097 | no rule detected (H0 not rejected) |
| AgaveBam | 7 | 21 | -0.333 | 0.538 | +1.000 | 0.000 | H2 arrival rule |
| FireBAM | 2 | 6 | -1.000 | 0.242 | +1.000 | 0.097 | no rule detected (H0 not rejected) |
| Firedancer | 9 | 28 | -0.630 | 0.014 | +1.000 | 0.000 | H2 arrival rule |
| HarmonicAgave | 3 | 9 | -0.333 | 1.000 | +1.000 | 0.016 | H2 arrival rule |
| HarmonicFiredancer | 4 | 12 | -0.500 | 0.538 | +1.000 | 0.005 | H2 arrival rule |
| JitoLabs | 6 | 18 | -0.889 | 0.004 | +0.889 | 0.003 | H2 arrival rule |
| Rakurai | 3 | 9 | -0.778 | 0.162 | +1.000 | 0.016 | H2 arrival rule |

| Hypothesis | Expected pattern | Observed support | Verdict |
|---|---|---|---|
| H1: fee rule | Same-payer ascending+shuffled: pooled mean tau_fee > 0 and Holm p < 0.05, and tau_fee > 0 on ascending bursts alone; descending is consistency only | No label meets H1. On ascending bursts mean tau_fee is negative for every label, and the primary-set tau_fee is 0.000 or negative for every label. | Not supported (0/8 labels) |
| H2: arrival rule | Same primary set: pooled mean tau_send > 0 with Holm p < 0.05 and tau_send > 0 on ascending bursts alone, without the H1 conditions | The H2 markers hold for AgaveBam, Firedancer, HarmonicAgave, HarmonicFiredancer, JitoLabs and Rakurai. Agave and FireBAM show no rule. The burst spans two to three slots, so this is mostly a send-order artifact of the sequential design, not evidence of an arrival rule inside one scheduler batch. | Markers met for 6/8 labels; read as send-order association, not a scheduler rule |
| Mixed | Both H1 and H2 markers hold | No label has both markers. | Not observed |
| H0: noise | Signs and magnitudes vary; pooled p not small; landing too thin | Agave (2 primary bursts) and FireBAM (2 primary bursts) fail to reject H0. | Weak no-rule, small n |

Overall conclusion: the sequential result is a send-order result, not a fee-rule result, because the burst is too spread out in time. The parallel design puts the five transactions in front of the scheduler together. Pooled over four parallel sessions on two days, it shows a Holm-significant fee ordering for AgaveBam (5 bursts), HarmonicAgave (4) and HarmonicFiredancer (10). Firedancer is positive but not Holm-significant (4 bursts). JitoLabs is weakly positive on 9 bursts and not significant. FireBAM and Rakurai are not significant. Vanilla Agave goes the other way on 2 bursts and is weak. Whole-block priority ordering is near zero for every label in both sessions. Fee level had no consistent effect on landing: every fee level landed 125/125 in the main run and 65/66 in the 2026-10-25 parallel session. Follow-up 4 landed 83, 92, 94, 94 and 81 of 96 per fee level from 0 to 1,000,000 micro-lamports/CU, so the top fee did not land more often. The parallel fee results rest on 1 to 10 primary bursts per label and are weak except HarmonicFiredancer. Agave, FireBAM and Rakurai have 1 to 3 primary bursts in the main run as well.

Per-client summary:

| Client family | Sequential (pre-registered primary) | Parallel, 4 sessions pooled (follow-up design) | Reading |
|---|---|---|---|
| Agave | no rule, 2 bursts | tau_fee -0.333, 2 bursts, no rule | no fee rule seen; small n |
| AgaveBam | H2 markers, 7 bursts | H1 fee, +0.747, 5 bursts, Holm 0.000 | fee order when sent together |
| FireBAM | no rule, 2 bursts | +0.156, 3 bursts, no rule | no rule, small n |
| Firedancer | H2 markers, 9 bursts | +0.433, 4 bursts, Holm 0.240 | fee hint, not significant |
| HarmonicAgave | H2 markers, 3 bursts | H1 fee, +0.650, 4 bursts, Holm 0.008 | fee order when sent together |
| HarmonicFiredancer | H2 markers, 4 bursts | H1 fee, +0.467, 10 bursts, Holm 0.011 | clearest fee order, held on both days |
| JitoLabs | H2 markers, 6 bursts | +0.207, 9 bursts, Holm 0.968 | weak fee hint, not significant |
| Rakurai | H2 markers, 3 bursts | 1 burst | send order sequential only |

## How to read the tau tables

`tau_fee` is Kendall tau of block index against fee, with the sign chosen so that a positive value means higher fee appears earlier in the block. `tau_send` is Kendall tau of block index against actual send order (`send_rank`, derived from `send_ts_ns`), with a positive value meaning an earlier send appears earlier. Values range from -1 to +1. Zero means no monotonic relation.

- H1 (fee rule): pooled mean `tau_fee` is positive with Holm-adjusted `p < 0.05` on the same-payer ascending+shuffled primary set, and `tau_fee` is positive on ascending bursts alone. `tau_send` may be positive in the descending rotation by construction, but descending bursts cannot support H1/H2 because fee order equals send order there.
- H2 (arrival rule): pooled mean `tau_send` is positive with Holm-adjusted `p < 0.05` on the same primary set, and `tau_send` is positive on ascending bursts alone, while the H1 conditions do not hold.
- Mixed: both the H1 and H2 markers hold.
- H0 (noise): signs and magnitudes vary without a stable pattern, pooled p-values are not small, or the number of same-block groups is too small to decide.
- Insufficient data: there are no primary groups.

The pre-registered primary test is the pooled mean `tau_fee` per label on the same-payer arm using only ascending + shuffled bursts; Holm correction is applied across the per-label primary p-values, separately for fee and send order. Descending bursts are reported as a consistency check only. Per-burst, per-mode, multi-payer, parallel and whole-block results are exploratory and are labelled as such in `results.md`.

Read per-burst p-values with care. Groups with fewer than three of our transactions in the same block are dropped. Because higher-fee transactions may land more often, this conditions the sample on landing; `results.md` reports the landed-per-burst distribution. A five-transaction burst has only 120 possible orders, so the smallest attainable two-sided per-burst permutation p-value is about 0.017. Pooled tests use 2000 permutations, so their floor is 0.0005. A single significant burst is weak evidence; pooled results over many bursts are the main evidence. The number of bursts, transactions and same-block groups is next to every tau so the reader can judge sample size.

## Pre-live checks already done

The three mainnet dry runs below (a, b, d) were read-only, with no sends, on 2026-10-25 UTC. Raw data is in `data/runs/20261025_dryrun_mainnet_a`, `_b` and `_d`. Post-Alpenglow mainnet slot time is about 0.212 s, so a four-slot leader window is about 0.85 s.

1. Run a: old timing (15:00 to 15:17 UTC). This run used lead 1 and an extra `getSlot` before send. It produced 107 bursts, with 51/107 on time. Send offsets were -1: 51, 0: 42, 1: 11, 2: 1, 3: 2. `verify-windows` confirmed 109/109 windows and 436/436 slots produced blocks. It covered 13 validators / 8 labels.

2. Run b: lead 2 plus prebuilt transactions (15:33 to 15:47 UTC). It produced 142 bursts: 126/142 were on time and 142/142 were not after the window end. Send offsets were -2: 77, -1: 49, 0: 8, 1: 6, 2: 2.

3. Run d: final timing code (16:15 to 16:37 UTC). This run used lead 2, fine polling, the final guard and the fair gap filter. It produced 100 bursts / 500 txs over 16 validators and 8 client labels (AgaveBam, JitoLabs, HarmonicAgave, HarmonicFiredancer, Firedancer, FireBAM, Rakurai, Agave). 99/100 bursts and 498/500 txs were on time using the estimated per-tx slot; send offsets were -2: 83, -1: 17. `verify-windows` found 104/104 windows had the scheduled target for all 4 slots and 416/416 slots produced blocks.

The committed `results.md` for dry run d was regenerated on 2026-10-31 with the current analyzer, so every committed `results.md` matches `obp/analyze.py`.

4. Localnet end-to-end (`solana-test-validator` 4.3.2). The full pipeline (`run`/`collect`/`verify-windows`/`analyze`) ran successfully, 10/10 memo txs landed, and a 3-slot lead landed in the block before the window.

5. Probe cost. `simulateTransaction` measured the probe memo transaction at about 18.1k CU; the CU limit is 21,000. The priority fee is charged on the limit, not on actual consumption.

## What went wrong

- The public devnet faucet was unreachable from the test box, and the testnet faucet rate-limited requests (HTTP 429), so the end-to-end pipeline test used localnet.
- The first mainnet dry run (a) produced only 51/107 on-time bursts (about 48%). That forced a timing redesign: prebuilt/signed bursts, a two-slot lead, 0.05 s polling near the window, conservative far sleeps, a final window-start guard, and per-transaction estimated send slots.
- An initial cluster-detection bug (a wrong mainnet genesis-hash constant) was found during review and fixed before any live send, with a regression test in `tests/test_rpc_guard.py`.
- A three-slot lead landed transactions in the block before the target window on localnet (the current leader included them). The default lead is therefore two slots, and the pilot compares lead 1 vs 2.
- The sequential design (20 ms gap plus a ~57 ms HTTP round trip per send) spreads a burst over ~414 ms, about two slots. Every sequential burst split over 2 or 3 blocks, so same-block groups were mostly 3 transactions and the fee ladder was never inside one scheduler batch. The pre-registered H2 verdicts in the main run mostly show that send order decides which block and which position; they do not show that the schedulers ignore fees. This was found only after the main run. The parallel session was added as a deviation from the pre-registered plan and is labelled exploratory.
- `--max-bursts` counts attempts including guard skips: 144 attempts gave 125 sent bursts (19 skipped), and 72 gave 66.
- In the parallel session, thread start timestamps are not arrival order (HTTP calls contend, median 168 ms), so `tau_send` in that session is not a meaningful arrival measure.
- The 5 parallel transactions that did not land were never accepted by the public RPC: burst 61 got HTTP 413 "You have used your data allowance", burst 64 lost 3 sends to "Remote end closed connection", and burst 70 got HTTP 429. Every transaction the RPC accepted landed. The public RPC rate limits started near the end of the parallel session, after heavy `getBlock` use by `collect`.
- Small per-label samples: Agave, FireBAM and Rakurai have 1 to 3 primary bursts in the main run. Primary verdicts with 2 or 3 bursts are weak.
- The planned sequential repeat was never run. The second-day sample is the 2026-10-31 parallel follow-up instead.
- On 2026-10-31 the public RPC took a median 1.25 s to 1.29 s per `sendTransaction` in follow-ups 2 and 3 and 0.81 s in follow-up 4 (168 ms on 2026-10-25). With lead 2 most transactions landed after the target window, in the next leader's block. Follow-up 3 was stopped after 12 bursts with 0 in-window landings. Follow-up 4 used lead 6, chosen after seeing the landing offsets; 110 of its 444 landed transactions landed 1 to 3 slots early, in the previous leader's block.
- `--max-bursts` counted 87 skipped attempts in follow-up 2 because the slow `getSlot` replies often returned after the window start.
- The target of 8 or more primary bursts per main label in the parallel design was not met; the ledger was at 32.4M of 35M lamports when sending stopped.
- The send path is a public RPC only. The forwarding path from RPC to leader TPU and SWQoS is not observed.
- Unknown(35832) is a validator whose `clientId` number is not mapped to a name; it has 1 burst and is excluded from conclusions.

## Limitations

- Network path and scheduler are not separated. The RPC forwarder, SWQoS and TPU admission add uncontrolled jitter.
- Ledger entry order is not the same as real execution order on parallel threads.
- Leader-side relays and block engines (BAM, Harmonic, Jito) are not isolated from the client scheduler by this design.
- Samples per validator and per client are small. Every conclusion states the number of bursts and same-block groups behind it.
- Ordering tests only use bursts with at least three of our five transactions co-landed in the target block. Higher-fee transactions may land more often, so this conditions on landing and can bias the sample toward higher fees; the landed-per-burst distribution is reported separately.
- The whole-block priority-fee ordering is an approximation derived from total fee, signature count and CU consumed.
- All measurements are post-Alpenglow (after 2026-10-21) and must not be mixed with pre-upgrade data.
- The parallel sessions were added after the main run and are a follow-up design, not pre-registered. Two days and two times of day are covered for the parallel design only; the RPC path changed between them, so day and path effects are mixed.

## Data availability

| Session | `sent.csv` | `landed.csv` | `blocks.csv` | `windows.csv` | `results.csv` | `results.md` | `spend_ledger_snapshot.json` |
|---|---|---|---|---|---|---|---|
| Pilot lead 1 | `data/runs/20261026_pilot_lead1/sent.csv` | `data/runs/20261026_pilot_lead1/landed.csv` | `data/runs/20261026_pilot_lead1/blocks.csv` | `data/runs/20261026_pilot_lead1/windows.csv` | `data/runs/20261026_pilot_lead1/results.csv` | `data/runs/20261026_pilot_lead1/results.md` | `data/runs/20261026_pilot_lead1/spend_ledger_snapshot.json` |
| Pilot lead 2 | `data/runs/20261026_pilot_lead2/sent.csv` | `data/runs/20261026_pilot_lead2/landed.csv` | `data/runs/20261026_pilot_lead2/blocks.csv` | `data/runs/20261026_pilot_lead2/windows.csv` | `data/runs/20261026_pilot_lead2/results.csv` | `data/runs/20261026_pilot_lead2/results.md` | `data/runs/20261026_pilot_lead2/spend_ledger_snapshot.json` |
| Main sequential | `data/runs/20261025_1828_main/sent.csv` | `data/runs/20261025_1828_main/landed.csv` | `data/runs/20261025_1828_main/blocks.csv` | `data/runs/20261025_1828_main/windows.csv` | `data/runs/20261025_1828_main/results.csv` | `data/runs/20261025_1828_main/results.md` | `data/runs/20261025_1828_main/spend_ledger_snapshot.json` |
| Parallel | `data/runs/20261025_1907_parallel/sent.csv` | `data/runs/20261025_1907_parallel/landed.csv` | `data/runs/20261025_1907_parallel/blocks.csv` | `data/runs/20261025_1907_parallel/windows.csv` | `data/runs/20261025_1907_parallel/results.csv` | `data/runs/20261025_1907_parallel/results.md` | `data/runs/20261025_1907_parallel/spend_ledger_snapshot.json` |
| Parallel follow-up 2 | `data/runs/20261031_par2_parallel/sent.csv` | `data/runs/20261031_par2_parallel/landed.csv` | `data/runs/20261031_par2_parallel/blocks.csv` | `data/runs/20261031_par2_parallel/windows.csv` | `data/runs/20261031_par2_parallel/results.csv` | `data/runs/20261031_par2_parallel/results.md` | `data/runs/20261031_par2_parallel/spend_ledger_snapshot.json` |
| Parallel follow-up 3 | `data/runs/20261031_par3_parallel/sent.csv` | `data/runs/20261031_par3_parallel/landed.csv` | `data/runs/20261031_par3_parallel/blocks.csv` | `data/runs/20261031_par3_parallel/windows.csv` | `data/runs/20261031_par3_parallel/results.csv` | `data/runs/20261031_par3_parallel/results.md` | none (session stopped before the snapshot was written; the global ledger covers it) |
| Parallel follow-up 4 | `data/runs/20261031_par4_parallel_lead6/sent.csv` | `data/runs/20261031_par4_parallel_lead6/landed.csv` | `data/runs/20261031_par4_parallel_lead6/blocks.csv` | `data/runs/20261031_par4_parallel_lead6/windows.csv` | `data/runs/20261031_par4_parallel_lead6/results.csv` | `data/runs/20261031_par4_parallel_lead6/results.md` | `data/runs/20261031_par4_parallel_lead6/spend_ledger_snapshot.json` |
| Pooled parallel (offline) | concatenated | concatenated | concatenated | concatenated | `data/runs/pooled_parallel_all/results.csv` | `data/runs/pooled_parallel_all/results.md` | none |
| Pooled follow-up only (offline) | concatenated | concatenated | concatenated | concatenated | `data/runs/pooled_parallel_followup/results.csv` | `data/runs/pooled_parallel_followup/results.md` | none |

Each session directory also has `plan.json`, `run_meta.json`, `results_by_group.csv`, `validators.csv` and `obp.log`. The funding session is `data/runs/20261026_fund`. The global ledger is `data/spend_ledger_mainnet.json`. Signature lists for independent checking are the `signature` columns of the `sent.csv` files.

`analyze` reproduces `results.csv` and `results.md` from the committed CSVs without network access. `collect` is idempotent and does not refetch slots already present in `blocks.csv`.
