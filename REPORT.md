# Inside the Block: ordering of our own transactions in Solana leader windows

**Author:** [AUTHOR NAME] [FILL PENDING: replace with author name]

**Repository:** [FILL: repository URL PENDING]

**Measurement network:** Solana mainnet-beta, post-Alpenglow (upgrade on 2026-10-21)

**Status of this document:** research report template. Every live-run number is a placeholder
marked `PENDING` or `FILL`. The pre-live checks in their own section are real, read-only results.

## Measurement dates

All times are UTC. A session is one `OBP_DATA=data/runs/<YYYYMMDD>_<name>` directory.

| Session | Purpose | Date (UTC) | Slot range | Data directory |
|---|---|---|---|---|
| Pilot | Ten live bursts, pipeline and landing-rate check | [FILL: DATE PENDING] | [FILL: FIRST-SLOT - LAST-SLOT PENDING] | `[FILL: data/runs/... PENDING]` |
| Main, alternate arm | Same-payer and multi-payer bursts interleaved within one run; the primary test uses the same-payer subset | [FILL: DATE PENDING] | [FILL: FIRST-SLOT - LAST-SLOT PENDING] | `[FILL: data/runs/... PENDING]` |
| Repeat day | Half-size robustness repeat at a different time of day | [FILL: DATE PENDING] | [FILL: FIRST-SLOT - LAST-SLOT PENDING] | `[FILL: data/runs/... PENDING]` |

## Setup

At least six validators covering at least three distinct client labels are required. The table below
is the **dry-run target set (2026-10-25)** from
`data/runs/20261025_dryrun_mainnet_d/plan.json` plus `validators.csv` (inventory read when the plan
was created, 2026-10-25T16:15:44Z). The live run may target a different set of validators; replace
this table with the live target set when it is known.

| # | Identity | clientId | Version | Active stake (SOL) | Label used in results |
|---:|---|---|---|---:|---|
| 1 | 7QQGNm3ptwinipDCyaCF7jY5katgmFUu1ieP2f7nwLpE | Agave | 4.3.2 | 1875002.0 | Agave |
| 2 | 5Us18hLZPXJTS4QVuGSsUw137Dyd2tgBaem24Xsf5nBS | Agave | 4.3.2 | 1207980.3 | Agave |
| 3 | Fc6NNdS2j3EmrWbU6Uqt6wsKB5ef72NjaWfNxKYbULGD | AgaveBam | 4.3.2 | 4319078.0 | AgaveBam |
| 4 | 6y7V8dL673XFzm9QyC5vvh3itWkp7wztahBd2yDqsyrK | AgaveBam | 4.3.2 | 2916668.7 | AgaveBam |
| 5 | 9jxgosAfHgHzwnxsHw4RAZYaLVokMbnYtmiZBreynGFP | FireBAM | 26.10.4 | 4477330.0 | FireBAM |
| 6 | 9pBHfuE19q7PRbupJf8CZAMwv6RHjasdyMN9U9du7Nx2 | FireBAM | 26.10.4 | 197309.1 | FireBAM |
| 7 | 9eGrDohdNTAo61DRHyfMuqKWXqYnA3i254Wiszxe8FoY | Firedancer | 26.10.4 | 7038249.3 | Firedancer |
| 8 | JD549HsbJHeEKKUrKgg4Fj2iyv2RGjsV7NTZjZUrHybB | Firedancer | 26.10.4 | 6608866.5 | Firedancer |
| 9 | Fd7btgySsrjuo25CJCj7oE7VPMyezDhnx7pZkj2v69Nk | HarmonicAgave | 4.3.2 | 17099112.7 | HarmonicAgave |
| 10 | BtsmiEEvnSuUnKxqXj2PZRYpPJAc7C34mGz8gtJ1DAaH | HarmonicAgave | 4.3.2 | 4063118.3 | HarmonicAgave |
| 11 | 87CcUxpyR72ZyfaZirj86mqkbk5uuU2EfnwTegVMLJL5 | HarmonicFiredancer | 26.10.4 | 3830697.3 | HarmonicFiredancer |
| 12 | EXckihF3qmguH5znjhfzLvHsbk2E3nEW2DqNh4MMnDMm | HarmonicFiredancer | 26.10.4 | 1251487.4 | HarmonicFiredancer |
| 13 | C8Bey3LKVJHVqN6xPTeW8WJfUgFQAeGNBpT4Rp99JP1k | JitoLabs | 4.3.2 | 9216836.6 | JitoLabs |
| 14 | 5pPRHniefFjkiaArbGX3Y8NUysJmQ9tMZg3FrFGwHzSm | JitoLabs | 4.3.2 | 5973284.7 | JitoLabs |
| 15 | E3mDbFMr8yZcCAZx5wPUFCRmLX31u8Nnj4jPoPc54h3F | Rakurai | 4.3.2 | 887407.9 | Rakurai |
| 16 | 7PdKhpKz7T39vZHFL1UfcYNDsLvay6hp4KPQq1aUckFf | Rakurai | 4.3.2 | 770106.5 | Rakurai |

Source: `data/runs/20261025_dryrun_mainnet_d/validators.csv`, filtered to the identities in that
session's `plan.json`. The exact `identity`, `client_id`, `version`, `stake_sol` and `label` columns
are copied above. Stake and version change over time, so the inventory timestamp matters.

Sending setup:

| Item | Value |
|---|---|
| Probe transaction | SPL Memo, one signature, fixed CU limit |
| CU limit | 21,000 |
| Fee ladder (micro-lamports/CU) | 0, 1,000, 10,000, 100,000, 1,000,000 |
| Rotations | ascending, descending, shuffled, rotating by burst |
| Payer arms | same payer (account-lock conflict), multi payer (parallel), or alternate (same/multi by burst index; recommended for the main run) |
| Lead slots | 2 (default; blockhash/signing prepared 6 slots earlier). A 3-slot lead landed early on localnet, so the pilot compares lead 1 vs 2 |
| Send path | [FILL: RPC_URL / SEND_RPC_URL PENDING] |
| `skipPreflight` / `maxRetries` | true / 0 |
| Spend ledger | [FILL: FINAL RESERVED LAMPORTS PENDING] of `[FILL: CAP PENDING]` |
| Ledger location | Global per cluster at `$OBP_LEDGER_DIR/spend_ledger_<cluster>.json` (default `data` root, `/data` in Docker); session copy in `spend_ledger_snapshot.json` |

## Method summary

Each burst contains five memo transactions with the same instructions and the same CU limit, and
five different priority fees. The five fee levels are sent in ascending, descending or shuffled
order, rotating by burst. In the same-payer arm all five use one fee payer, forcing a write-lock
serialisation. In the multi-payer arm they use different payers, removing the lock conflict.

The planner selects future four-slot leader windows for validators from several client labels.
The sender prebuilds and signs the burst six slots before the send, waits until
`window_start - lead_slots` (default 2) with 0.05 s polling near the window, and sends with
`skipPreflight` and `maxRetries: 0`. If the final wait returns at or after the window start, the
burst is skipped before any fee is reserved. In `alternate` mode same-payer and multi-payer bursts
alternate by burst index within one run, so time of day does not confound the arms. `verify-windows`
confirms the target actually led the window. `collect` records the landing slot, actual leader,
ledger index and every transaction in the landing block. Every row, including its signature, is
written to `sent.csv` before any post-send RPC. The missing-slot sentinel is restricted to read
methods; a `sendTransaction` result must be a signature string, otherwise it is recorded as an
error.

The primary statistic is Kendall tau of ledger index against fee, and against actual send order,
within target-block groups that contain at least three of our five transactions. Primary tests keep
only rows whose landing slot was inside the planned window and whose actual leader was the planned
target. Permutation p-values are reported per burst and pooled per client label. The whole-block
check is supplementary and uses an approximate priority fee per CU.

Only bursts where at least three of our five transactions co-landed in the target block enter the
tau tests. Higher-fee transactions may land more often, so this conditions on landing and can bias
the ordering sample toward higher fees. That is a selection effect, not a finding; `results.md`
reports the landed-per-burst distribution so the reader can judge it.

The pre-registered primary test is the pooled mean `tau_fee` per client label on the same-payer
arm, using only descending + shuffled bursts and only target-window rows with the planned leader.
Holm correction is applied across the per-label primary p-values. Ascending bursts are excluded from
the primary test because there fee order equals send order (confounded); they are a consistency
check only. All other cuts are exploratory. The per-label verdict rule is: H1 if pooled mean
`tau_fee > 0` with Holm-adjusted `p < 0.05` and `tau_fee > 0` on descending bursts alone; H2 if
pooled mean `tau_send > 0` with `p < 0.05` and `tau_send > 0` on descending bursts alone; mixed if
both H1 and H2 markers hold; otherwise "no rule detected (H0 not rejected)".

## Results

Every number below is marked as pending. Replace placeholders only with values generated from the
committed session directories, and state the session next to each result.

### Leader schedule and leader types/clients

Targeted client labels: [FILL: LABELS PENDING].

| Label | Validators targeted | Planned windows | Windows with target leading all 4 slots | Window slots producing a block |
|---|---:|---:|---:|---:|
| [FILL: label PENDING] | [FILL: count PENDING] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| [FILL: label PENDING] | [FILL: count PENDING] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| [FILL: label PENDING] | [FILL: count PENDING] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |

Interpretation: [RESULT PENDING: live run]. State whether each selected label produced enough
verified windows to support a per-label result, and whether any target lost its window.

### Path from backend to the executing node

| Label | Live sends | Landed | Landing rate | On time | In window at send |
|---|---:|---:|---:|---:|---:|
| [FILL: label PENDING] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| [FILL: label PENDING] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |

| Fee level (micro/CU) | Live sends | Landed | Landing rate |
|---:|---:|---:|---:|
| 0 | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| 1,000 | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| 10,000 | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| 100,000 | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| 1,000,000 | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |

Interpretation: [RESULT PENDING: live run]. Separate what is observable (send offset, landing
rate, actual leader) from what is not observable (RPC forwarding path, SWQoS admission, relay
behaviour).

### Our transactions' interaction with each other

| Arm | Bursts | Same-block groups | Mean tau_fee | Pooled p_fee | Mean tau_send | Pooled p_send |
|---|---:|---:|---:|---:|---:|---:|
| Same payer | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| Multi payer | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |

Interpretation: [RESULT PENDING: live run]. If the same-payer arm follows fee but the multi-payer
arm does not, account-lock serialisation and parallel execution are a plausible explanation.

### Competition inside the block

| Label | Blocks checked | Non-vote txs | Mean tau_priority (approx) | Notes |
|---|---:|---:|---:|---|
| [FILL: label PENDING] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| [FILL: label PENDING] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |

Interpretation: [RESULT PENDING: live run]. This check is approximate because priority fee per CU
is inferred from total fee, signature count and CU consumed. It is supplementary to our own
transactions, not a replacement for them.

### Send order

Per-burst rotation results:

| Rotation | Bursts | Mean tau_fee | Mean tau_send | Fee direction stable | Send-order direction stable |
|---|---:|---:|---:|---|---|
| Ascending | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| Descending | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| Shuffled | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] | [RESULT PENDING: live run] |

Interpretation: [RESULT PENDING: live run].

### Noise versus rule

| Hypothesis | Expected pattern | Observed support | Verdict |
|---|---|---|---|
| H1: fee rule | Same-payer descending+shuffled: pooled mean tau_fee > 0 and Holm p < 0.05, and tau_fee > 0 on descending bursts alone; ascending is consistency only | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| H2: arrival rule | Same primary set: pooled mean tau_send > 0 with p < 0.05 and tau_send > 0 on descending bursts alone, without the H1 conditions | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| Mixed | Both H1 and H2 markers hold | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| H0: noise | Signs and magnitudes vary; pooled p not small; landing too thin | [RESULT PENDING: live run] | [RESULT PENDING: live run] |

Overall conclusion: [RESULT PENDING: live run].

## How to read the tau tables

`tau_fee` is Kendall tau of block index against fee, with the sign chosen so that a positive value
means higher fee appears earlier in the block. `tau_send` is Kendall tau of block index against
actual send order (`send_rank`, derived from `send_ts_ns`), with a positive value meaning an earlier
send appears earlier. Values range from
-1 to +1. Zero means no monotonic relation.

- H1 (fee rule): pooled mean `tau_fee` is positive with Holm-adjusted `p < 0.05` on the same-payer
  descending+shuffled primary set, and `tau_fee` is positive on descending bursts alone.
  `tau_send` may be positive in the ascending rotation by construction, but ascending bursts cannot
  support H1/H2 because fee order equals send order there.
- H2 (arrival rule): pooled mean `tau_send` is positive with `p < 0.05` on the same primary set,
  and `tau_send` is positive on descending bursts alone, while the H1 conditions do not hold.
- Mixed: both the H1 and H2 markers hold.
- H0 (noise): signs and magnitudes vary without a stable pattern, pooled p-values are not small,
  or the number of same-block groups is too small to decide.

The pre-registered primary test is the pooled mean `tau_fee` per label on the same-payer arm using
only descending + shuffled bursts; Holm correction is applied across the per-label primary
p-values.
Ascending bursts are reported as a consistency check only. Per-burst, per-mode, multi-payer and
whole-block results are exploratory and are labelled as such in `results.md`.

Read per-burst p-values with care. Groups with fewer than three of our transactions in the same
block are dropped. Because higher-fee transactions may land more often, this conditions the sample
on landing; `results.md` reports the landed-per-burst distribution. A five-transaction burst has
only 120 possible orders, so the smallest attainable two-sided per-burst permutation p-value is
about 0.017. Pooled tests use 2000 permutations, so their floor is 0.0005. A single significant
burst is weak evidence; pooled results over many bursts are the main evidence. Report the number of
bursts, transactions and same-block groups next to every tau so the reader can judge sample size.

## Pre-live checks already done

The three mainnet dry runs below (a, b, d) were read-only, with no sends, on 2026-10-25 UTC. Raw
data is in `data/runs/20261025_dryrun_mainnet_a`, `_b` and `_d`. Post-Alpenglow mainnet slot time
is about **0.212 s**, so a four-slot leader window is about **0.85 s**.

1. **Run a: old timing (15:00-15:17 UTC).** This run used lead 1 and an extra `getSlot` before
   send. It produced 107 bursts, with **51/107 on time**. Send offsets were
   **-1: 51, 0: 42, 1: 11, 2: 1, 3: 2**. `verify-windows` confirmed **109/109 windows** and
   **436/436 slots produced blocks**. It covered **13 validators / 8 labels**.

2. **Run b: lead 2 plus prebuilt transactions (15:33-15:47 UTC).** It produced 142 bursts:
   **126/142 were on time** and **142/142 were still in the window at send**. Send offsets were
   **-2: 77, -1: 49, 0: 8, 1: 6, 2: 2**.

3. **Run d: current code (16:15-16:37 UTC).** This run used lead 2, fine polling, the final guard
   and the fair gap filter. It produced **100 bursts / 500 txs over 16 validators and 8 client
   labels** (AgaveBam, JitoLabs, HarmonicAgave, HarmonicFiredancer, Firedancer, FireBAM, Rakurai,
   Agave). **99/100 bursts and 498/500 txs were on time** using the estimated per-tx slot; send
   offsets were **-2: 83, -1: 17**. `verify-windows` found **104/104 windows** had the scheduled
   target for all 4 slots and **416/416 slots produced blocks**.

4. **Localnet end-to-end (`solana-test-validator` 4.3.2).** The full pipeline
   (`run`/`collect`/`verify-windows`/`analyze`) ran successfully, **10/10 memo txs landed**, and a
   **3-slot lead landed in the block before the window**.

5. **Probe cost.** `simulateTransaction` measured the probe memo transaction at about **18.1k CU**;
   the CU limit is **21,000**. The priority fee is charged on the limit, not on actual consumption.

## What went wrong

- The public devnet faucet was unreachable from the test box, and the testnet faucet rate-limited
  requests (HTTP 429), so the end-to-end pipeline test used localnet.
- The first mainnet dry run (a) produced only 51/107 on-time bursts (about 48%). That forced a
  timing redesign: prebuilt/signed bursts, a two-slot lead, 0.05 s polling near the window,
  conservative far sleeps, a final window-start guard, and per-transaction estimated send slots.
- An initial cluster-detection bug (a wrong mainnet genesis-hash constant) was found during review
  and fixed before any live send, with a regression test in `tests/test_rpc_guard.py`.
- A three-slot lead landed transactions in the block before the target window on localnet (the
  current leader included them). The default lead is therefore two slots, and the pilot compares
  lead 1 vs 2.
- [ADD LIVE-RUN ISSUES PENDING]

## Limitations

- Network path and scheduler are not separated. The RPC forwarder, SWQoS and TPU admission add
  uncontrolled jitter.
- Ledger entry order is not the same as real execution order on parallel threads.
- Leader-side relays and block engines (BAM, Harmonic, Jito) are not isolated from the client
  scheduler by this design.
- Samples per validator and per client are small. The report must state the number of bursts and
  same-block groups behind every conclusion.
- Ordering tests only use bursts with at least three of our five transactions co-landed in the
  target block. Higher-fee transactions may land more often, so this conditions on landing and can
  bias the sample toward higher fees; the landed-per-burst distribution is reported separately.
- The whole-block priority-fee ordering is an approximation derived from total fee, signature
  count and CU consumed.
- All measurements are post-Alpenglow (after 2026-10-21) and must not be mixed with pre-upgrade
  data.

## Data availability

- Session directories: `[FILL: data/runs/... PENDING]`
- Raw send rows and signatures: `[FILL: PATH TO sent.csv PENDING]`
- Landing and block position: `[FILL: PATH TO landed.csv PENDING]`
- Full blocks: `[FILL: PATH TO blocks.csv PENDING]`
- Window verification: `[FILL: PATH TO windows.csv PENDING]`
- Derived results: `[FILL: PATH TO results.csv PENDING]`, `[FILL: PATH TO results.md PENDING]`
- Signature list for independent checking: the `signature` column of `sent.csv`, also listed in
  `[FILL: PATH TO SIGNATURE LIST PENDING]`
- Spend ledger (global per cluster): `[FILL: PATH TO spend_ledger_mainnet.json PENDING]`, normally
  `data/spend_ledger_mainnet.json` or `$OBP_LEDGER_DIR/spend_ledger_mainnet.json`; each session also
  commits `spend_ledger_snapshot.json`

`analyze` reproduces `results.csv` and `results.md` from the committed CSVs without network
access. `collect` is idempotent and does not refetch slots already present in `blocks.csv`.
