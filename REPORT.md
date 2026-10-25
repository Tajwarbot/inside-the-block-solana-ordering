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
| Main, same-payer | Fee ladder with one fee payer per burst | [FILL: DATE PENDING] | [FILL: FIRST-SLOT - LAST-SLOT PENDING] | `[FILL: data/runs/... PENDING]` |
| Main, multi-payer | Fee ladder with different fee payers | [FILL: DATE PENDING] | [FILL: FIRST-SLOT - LAST-SLOT PENDING] | `[FILL: data/runs/... PENDING]` |
| Repeat day | Half-size robustness repeat at a different time of day | [FILL: DATE PENDING] | [FILL: FIRST-SLOT - LAST-SLOT PENDING] | `[FILL: data/runs/... PENDING]` |

## Setup

At least six validators covering at least three distinct client labels are required. One row per
validator actually targeted by a live burst.

| # | Identity | clientId | Version | Active stake (SOL) | Label used in results |
|---:|---|---|---|---:|---|
| 1 | [FILL: identity PENDING] | [FILL: clientId PENDING] | [FILL: version PENDING] | [FILL: stake PENDING] | [FILL: label PENDING] |
| 2 | [FILL: identity PENDING] | [FILL: clientId PENDING] | [FILL: version PENDING] | [FILL: stake PENDING] | [FILL: label PENDING] |
| 3 | [FILL: identity PENDING] | [FILL: clientId PENDING] | [FILL: version PENDING] | [FILL: stake PENDING] | [FILL: label PENDING] |
| 4 | [FILL: identity PENDING] | [FILL: clientId PENDING] | [FILL: version PENDING] | [FILL: stake PENDING] | [FILL: label PENDING] |
| 5 | [FILL: identity PENDING] | [FILL: clientId PENDING] | [FILL: version PENDING] | [FILL: stake PENDING] | [FILL: label PENDING] |
| 6 | [FILL: identity PENDING] | [FILL: clientId PENDING] | [FILL: version PENDING] | [FILL: stake PENDING] | [FILL: label PENDING] |
| 7 | [FILL: identity PENDING] | [FILL: clientId PENDING] | [FILL: version PENDING] | [FILL: stake PENDING] | [FILL: label PENDING] |
| 8 | [FILL: identity PENDING] | [FILL: clientId PENDING] | [FILL: version PENDING] | [FILL: stake PENDING] | [FILL: label PENDING] |

Source: `[FILL FROM data/runs/.../validators.csv]`. Copy the exact `identity`, `client_id`,
`version`, `stake_sol` and `label` columns. Record the inventory timestamp because stake and
version change.

Sending setup:

| Item | Value |
|---|---|
| Probe transaction | SPL Memo, one signature, fixed CU limit |
| CU limit | [FILL: CU LIMIT PENDING, default 21,000] |
| Fee ladder (micro-lamports/CU) | 0, 1,000, 10,000, 100,000, 1,000,000 |
| Rotations | ascending, descending, shuffled, rotating by burst |
| Payer arms | same payer (account-lock conflict) and multi payer (parallel) |
| Lead slots | [FILL: LEAD SLOTS PENDING, default 2] |
| Send path | [FILL: RPC_URL / SEND_RPC_URL PENDING] |
| `skipPreflight` / `maxRetries` | true / 0 |
| Spend ledger | [FILL: FINAL RESERVED LAMPORTS PENDING] of `[FILL: CAP PENDING]` |

## Method summary

Each burst contains five memo transactions with the same instructions and the same CU limit, and
five different priority fees. The five fee levels are sent in ascending, descending or shuffled
order, rotating by burst. In the same-payer arm all five use one fee payer, forcing a write-lock
serialisation. In the multi-payer arm they use different payers, removing the lock conflict.

The planner selects future four-slot leader windows for validators from several client labels.
The sender prebuilds and signs the burst, waits until the lead slot and sends with
`skipPreflight` and `maxRetries: 0`. `verify-windows` confirms the target actually led the
window. `collect` records the landing slot, actual leader, ledger index and every transaction in
the landing block.

The primary statistic is Kendall tau of ledger index against fee, and against send sequence,
within bursts that landed at least three transactions in the same block. Permutation p-values are
reported per burst and pooled per client label. The whole-block check is supplementary and uses
an approximate priority fee per CU.

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
| H1: fee rule | Positive tau_fee in all rotations and both arms; pooled p small | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| H2: arrival rule | Positive tau_send in all rotations; fee effect absent or unstable | [RESULT PENDING: live run] | [RESULT PENDING: live run] |
| H0: noise | Signs and magnitudes vary; pooled p not small; landing too thin | [RESULT PENDING: live run] | [RESULT PENDING: live run] |

Overall conclusion: [RESULT PENDING: live run].

## How to read the tau tables

`tau_fee` is Kendall tau of block index against fee, with the sign chosen so that a positive value
means higher fee appears earlier in the block. `tau_send` is Kendall tau of block index against
send sequence, with a positive value meaning an earlier send appears earlier. Values range from
-1 to +1. Zero means no monotonic relation.

- H1 (fee rule): `tau_fee` stays positive across ascending, descending and shuffled rotations,
  and across both payer arms. The pooled p-value is small. `tau_send` may be positive in the
  ascending rotation by construction, but it should not stay positive under descending and
  shuffled rotations.
- H2 (arrival rule): `tau_send` stays positive under all rotations, while `tau_fee` changes sign
  or loses significance when the rotation changes.
- H0 (noise): signs and magnitudes vary without a stable pattern, pooled p-values are not small,
  or the number of same-block groups is too small to decide.

Read per-burst p-values with care. A five-transaction burst has only 120 possible orders, so the
smallest two-sided permutation p-value is about 0.017. A single significant burst is weak
evidence. Pooled results over many bursts are the main evidence. Report the number of
same-block groups next to every tau so the reader can judge sample size.

## Pre-live checks already done

All work in this section was read-only on 2026-10-25 between 15:00 and 15:30 UTC. No live
transactions were sent.

1. **Mainnet dry run and leader-window verification.** A 16-minute mainnet dry run with no sends
   covered 13 validators across 8 client labels: AgaveBam, JitoLabs, HarmonicAgave,
   HarmonicFiredancer, Firedancer, FireBAM, Rakurai and Agave. It planned 109 windows.
   `verify-windows` confirmed that the scheduled target led all four slots in 109/109 windows, and
   all 436 window slots produced blocks.

2. **Send timing under the old design.** With the old timing (lead of 1 slot and an extra
   `getSlot` before sending), only 51 of 107 bursts were on time, meaning the send slot was before
   the window start. The send-offset distribution was: -1: 51, 0: 42, 1: 11, 2: 1, 3: 2. This
   led to the timing change: prebuild the transactions before the final wait, and use a lead of
   2 slots. [SECOND DRY-RUN RESULT PENDING]

3. **Localnet end-to-end.** Against `solana-test-validator` 4.3.2, 5 of 5 memo transactions
   landed in one block. The full pipeline (`collect`, `verify-windows`, `analyze`) ran
   successfully.

4. **Probe cost.** One probe memo transaction measured with `simulateTransaction` consumed about
   18.1k CU. The CU limit was set to 21,000, leaving about 5% headroom. The priority fee is
   charged on the limit, not on actual consumption.

## What went wrong

- The public devnet faucet was unreachable or rate-limited, so localnet was used for the
  end-to-end pipeline test instead of devnet.
- The old timing produced only 51/107 on-time bursts (about 48%). This was fixed with prebuilt
  transactions and a two-slot lead before the live runs.
- The payer accounts are unstaked, so SWQoS may allow only a small share of sends to land,
  especially at low fees. Landing rates are reported as a result rather than treated as a bug.
- [ADD LIVE-RUN ISSUES] [FILL PENDING: replace with issues observed during the live runs]

## Limitations

- Network path and scheduler are not separated. The RPC forwarder, SWQoS and TPU admission add
  uncontrolled jitter.
- Ledger entry order is not the same as real execution order on parallel threads.
- Leader-side relays and block engines (BAM, Harmonic, Jito) are not isolated from the client
  scheduler by this design.
- Samples per validator and per client are small. The report must state the number of bursts and
  same-block groups behind every conclusion.
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
- Spend ledger: `[FILL: PATH TO spend_ledger_mainnet.json PENDING]`

`analyze` reproduces `results.csv` and `results.md` from the committed CSVs without network
access. `collect` is idempotent and does not refetch slots already present in `blocks.csv`.
