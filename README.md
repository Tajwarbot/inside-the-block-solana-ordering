# obp: order-of-block probe

`obp` measures how Solana leaders order our own transactions inside a block. It sends small
memo-only transactions into planned 4-slot leader windows, records where they land, and reports
rank correlations between block position and priority fee, and between block position and send
order.

The default mode is dry run. Nothing is sent unless `run` or `fund` receives `--live`; mainnet
also requires `--mainnet`. The spend cap is hard-coded at 0.05 SOL.

## What it measures

The unit of work is a burst: five memo transactions with priority fees of 0, 1,000, 10,000,
100,000 and 1,000,000 micro-lamports per compute unit (CU). All five use the same CU limit
(21,000 by default) and the same instruction shape. The only intentional difference between them
is the priority fee.

For every burst the tool records:

- the slot at send time and whether the send preceded the target window;
- the landing slot, the actual leader of that slot and whether it is the planned target;
- the index of each landed transaction in ledger order;
- every transaction in each block we hit, for a whole-block supplementary check.

The main statistics are Kendall tau of block index against fee and of block index against send
sequence, each with a permutation p-value. Only transactions from the same burst that landed in
the same block are compared.

## Design and why

### Fee ladder independent of send order

A burst sends the same five fee levels in one of three rotations: ascending, descending or
shuffled. The mode rotates by burst number. This separates fee from send order. If position
tracks fee under all three rotations, the data supports a fee rule. If it tracks send sequence
instead, the data supports an arrival-order rule. If it tracks neither, the result is noise.

### Same-payer and multi-payer arms

In the `same` arm all five transactions use one fee payer, so they write-lock the same account and
the scheduler must serialise them. This is the cleanest test of the priority rule because the
transactions cannot execute in parallel.

In the `multi` arm the five transactions use different payers, so there is no account-lock
conflict and the runtime can execute them on different threads. Comparing the two arms shows
whether the ordering rule still holds when parallel execution is possible.

### Fixed CU limit

Every probe transaction sets the same CU limit and contains the same instructions. Priority fee
per CU is therefore the only variable the scheduler can rank on. The fee is charged on the CU
limit, not on CU actually consumed, so the worst-case fee is known before sending.

### Window targeting with lead slots

A leader normally holds four consecutive slots. The planner reads the epoch leader schedule and
chooses future windows for validators of the selected client labels. The sender prebuilds and
signs the whole burst, waits until `window_start - lead_slots`, then sends. The default lead is
two slots. Each row records `slot_at_send`, `send_offset` (send slot minus window start) and
`on_time` (`slot_at_send < window_start`).

The scheduler is not perfectly predictable from the schedule alone, so a separate step confirms
what actually happened.

### verify-windows

`verify-windows` queries `getSlotLeaders` and `getBlocks` for each planned window. It records
whether the target identity led all four slots and which slots in the window produced a block.
It works on dry-run data because it needs no signatures. Transactions that landed under a
different leader are marked `leader_is_target=False` and `in_target_window=False`, and are kept
out of the target-window comparison.

### Whole-block supplementary check

`blocks.csv` contains every transaction in each block that one of our transactions landed in:
ledger index, fee, CU consumed, signature count, vote flag and error flag. This supports a rough
check of whether the whole block is ordered by approximate priority fee per CU, and where our
transactions sit relative to unrelated competition. The approximation is
`(fee - 5000 * num_sigs) * 1e6 / cu_consumed`. It ignores exact per-instruction costs and other
fee components, so it is reported as an approximation everywhere.

## How the brief's topics are addressed

### Leader schedule and leader types/clients

`inventory` joins `getClusterNodes`, `getVoteAccounts` and the Jito validator API. It records
identity, vote account, active stake, `clientId`, version, a human label, Jito/BAM flags and the
TPU QUIC address. `plan` reads the epoch leader schedule, converts relative slot indices to
absolute slots and selects windows for the requested number of validators per client label.
`verify-windows` confirms the leader after the fact. This covers the schedule and the client
types that were actually targeted. It does not claim that the gossip label fully describes the
ordering path inside a validator.

### Path from backend to the executing node

Probe transactions are sent with `sendTransaction` through the configured RPC. `SEND_RPC_URL` can
point at a different sender, for example a free Helius endpoint. Requests use `skipPreflight:
true`, `maxRetries: 0` and base64 encoding. Preflight is skipped so the client does not reject a
transaction for a stale blockhash or a simulated error before the leader sees it. `maxRetries: 0`
keeps the sending decision under our control; the tool never retries a send automatically.

The payer accounts are unstaked, so stake-weighted QoS (SWQoS) can give them little bandwidth.
This may reduce landing rates, especially at low fees. The code records landing rates by client
and fee level instead of hiding this. The exact forwarding path through the RPC operator, the
QUIC connection to the leader's TPU and any relay in between are not observable from our data.
That is one of the stated limitations.

### Our transactions' interaction with each other

The `same` arm makes the interaction explicit: identical fee payer, hence a write-lock conflict,
so the five probes cannot execute in parallel. The `multi` arm removes the conflict. The fee
ladder is rotated independently of send order in both arms. If same-payer bursts follow fee but
multi-payer bursts do not, lock conflict and parallel execution are a plausible explanation.

### Competition inside the block

`blocks.csv` records every non-vote transaction in the landed blocks, and `analyze` computes an
approximate priority-fee ordering for each block. Our transactions are a small part of a busy
block, so this is supplementary evidence, not the primary result. The primary evidence is always
transactions we sent ourselves.

### Send order

`send_seq` is the position in the burst. The sender is sequential by default (`--send-mode seq`,
20 ms gap), and can run the sends in parallel (`--send-mode parallel`) for a separate comparison.
Because ascending, descending and shuffled rotations repeat across bursts, a stable relationship
between `send_seq` and block index is distinguishable from a fee relationship.

### Noise versus rule

The tool reports tau, permutation p-values, pooled per-label results and landing/timing counts.
Small samples are expected. A single burst is not treated as evidence. The report keeps a valid
"no rule" outcome (H0) instead of forcing a fee or arrival story. Dry-run timing rates, verified
windows and landing rates are reported separately from the ordering tests.

## What this does not separate

- Network path versus scheduler. RPC forwarding, SWQoS, TPU admission and relay behaviour add
  jitter that the experiment does not control or measure directly.
- Ledger entry order versus real execution order. `block_index` is the order in the ledger. On
  parallel threads the actual execution order can differ.
- Leader-side relays and block engines (BAM, Harmonic, Jito) versus the client's own scheduler.
  A label such as `AgaveBam` describes a stack, not one isolated ordering algorithm.
- Small samples per validator and per client. The design increases repetitions, but it cannot
  make a handful of bursts statistically strong.
- Alpenglow. The upgrade was on 2026-10-21. All data collected by this tool is post-upgrade and
  must not be mixed with pre-upgrade measurements. Blocks fetched now contain no vote
  transactions.

## Quickstart

### Docker Compose (dry run by default)

```bash
cp .env.example .env
docker compose up
```

The Compose entrypoint runs `inventory`, `plan`, three dry-run bursts, `collect`,
`verify-windows` and `analyze`. Dry-run transactions are built and signed with a throwaway
in-memory key and never sent.

Useful overrides:

```bash
# More dry-run bursts
OBP_BURSTS=10 docker compose up

# A timestamped session directory (create it on the host first)
mkdir -p data/runs/20261028_pilot
docker compose run --rm -e OBP_DATA=/data/runs/20261028_pilot obp

# Live mainnet (explicit opt-in, keys mounted read-only from ./keys)
OBP_ARGS="--live --mainnet --cap-sol 0.04" docker compose up
```

### Plain Python environment

Python 3.12 is recommended. `solders` is the only Solana-specific dependency.

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env

# One directory per measurement session. data/runs/ is committed to git.
export OBP_DATA=data/runs/$(date -u +%Y%m%d)_pilot
mkdir -p "$OBP_DATA"

.venv/bin/python -m obp inventory
.venv/bin/python -m obp plan --per-label 2 --windows 6 --labels \
  AgaveBam,JitoLabs,HarmonicAgave,HarmonicFiredancer,Firedancer,FireBAM,Agave
.venv/bin/python -m obp calibrate --sim-payer <any-funded-pubkey>
.venv/bin/python -m obp run                      # dry run
.venv/bin/python -m obp collect --wait-sec 20
.venv/bin/python -m obp verify-windows
.venv/bin/python -m obp analyze
```

`--run-dir DIR` is a per-command alternative to `export OBP_DATA` and is accepted before or
after the subcommand:

```bash
.venv/bin/python -m obp --run-dir data/runs/20261028_pilot inventory
.venv/bin/python -m obp inventory --run-dir data/runs/20261028_pilot
```

Precedence is `--run-dir`, then `OBP_DATA`, then `data`. The default remains `data` when neither
is set. For a real measurement campaign, set a fresh `OBP_DATA=data/runs/<YYYYMMDD>_<name>` for
every session so the data is timestamped and committed. `data/runs/` is not git-ignored; other
directories under `data/` are.

Payer keys for a live run:

```bash
export OBP_KEYPAIRS=/absolute/path/payer.json,/absolute/path/payer2.json,/absolute/path/payer3.json
.venv/bin/python -m obp balances
.venv/bin/python -m obp run --live --mainnet --cap-sol 0.04 --payer-arm same
```

With Docker, keys are read from the read-only `./keys` volume. The default paths are
`/keys/payer.json` for the same-payer arm and `/keys/payer.json` plus `/keys/payer2.json` through
`/keys/payer5.json` for the multi-payer arm.

## CLI reference

Global option:

| Option | Default | Meaning |
|---|---|---|
| `--run-dir DIR` | `OBP_DATA`, else `data` | Data directory for this invocation. Accepted before or after the subcommand. |

### inventory

```bash
python -m obp inventory
```

Reads nodes, vote accounts and the Jito API, then writes `validators.csv` and prints a summary
per client label. No flags. Read-only.

### plan

```bash
python -m obp plan [--per-label N] [--windows N] [--horizon SLOTS] [--labels LIST]
                   [--min-labels N] [--min-windows N] [--min-lead-slots N]
                   [--min-gap-slots N]
```

| Flag | Default | Meaning |
|---|---|---|
| `--per-label` | `2` | Validators to target per client label. |
| `--windows` | `4` | Maximum windows to plan per selected validator. |
| `--horizon` | `20000` | Only plan windows within this many slots. |
| `--labels` | empty | Comma list restricting client labels. Empty means all labels with enough windows. |
| `--min-labels` | `3` | Abort if fewer than this many distinct labels can be selected. |
| `--min-windows` | `3` | A validator must have at least this many windows in the horizon to be eligible. |
| `--min-lead-slots` | `25` | Only plan windows starting at least this many slots after the current slot. |
| `--min-gap-slots` | `12` | Never plan two windows, for any targets, that start less than this many slots apart. The earliest is kept. |

Writes `plan.json` and prints the selected validators and planned burst count.

### calibrate

```bash
python -m obp calibrate --sim-payer PUBKEY
```

Runs `simulateTransaction` (free, no signature verification) with an SPL Memo and prints the CU
consumed. `PUBKEY` can be any existing funded account. Read-only.

### balances

```bash
python -m obp balances
```

Prints lamports and SOL for each configured payer. Uses `OBP_KEYPAIRS` when set; otherwise it
checks the default `/keys/payer*.json` paths. Read-only.

### fund

```bash
python -m obp fund --lamports N [--live] [--mainnet] [--cap-sol SOL]
```

Transfers `N` lamports from the first payer to every other configured payer. Dry run unless
`--live` is passed; mainnet live also needs `--mainnet`. The cap defaults to 0.04 SOL and is
subject to the 0.05 SOL hard ceiling. Funding transfers are counted in the spend ledger.

### run

```bash
python -m obp run [--live] [--mainnet] [--cap-sol SOL] [--fee-levels LIST]
                  [--cu-limit N] [--lead-slots N] [--send-mode seq|parallel]
                  [--gap-ms N] [--payer-arm same|multi] [--max-bursts N]
```

| Flag | Default | Meaning |
|---|---|---|
| `--live` | off | Actually send. Without it nothing leaves the process. |
| `--mainnet` | off | Extra explicit opt-in required for `--live` on mainnet. |
| `--cap-sol` | `0.04` | Spend cap for this run. Cannot exceed 0.05 SOL. |
| `--fee-levels` | `0,1000,10000,100000,1000000` | Priority fees in micro-lamports per CU. |
| `--cu-limit` | `OBP_CU_LIMIT` or `21000` | Compute-unit limit for every probe transaction. |
| `--lead-slots` | `2` | Send this many slots before the target window starts. |
| `--send-mode` | `seq` | Send the burst sequentially or with one thread per transaction. |
| `--gap-ms` | `20` | Sleep between sends in sequential mode. |
| `--payer-arm` | `same` | One fee payer (lock conflict) or multiple payers (parallel). |
| `--max-bursts` | `0` | Limit to the earliest N planned bursts. `0` means all. |

Reads `plan.json`, appends to `sent.csv`, writes `run_meta.json`, and updates the per-cluster
spend ledger before each send. Dry-run rows are written with `live=False`.

### collect

```bash
python -m obp collect [--wait-sec N]
```

| Flag | Default | Meaning |
|---|---|---|
| `--wait-sec` | `20` | If the newest send is younger than this, sleep the remainder before checking statuses. |

Reads `sent.csv`, queries `getSignatureStatuses`, fetches blocks for newly landed slots and writes
`landed.csv` and `blocks.csv`. Re-running is idempotent: slots already present in `blocks.csv` are
not fetched or duplicated, and `landed.csv` is rewritten from the same sent rows.

### verify-windows

```bash
python -m obp verify-windows
```

Reads `plan.json` and `sent.csv`, calls `getSlotLeaders` and `getBlocks` for each window and
writes `windows.csv`. It reports whether the target led all four slots and how many of those
slots produced blocks. Works on dry-run data. Read-only.

### analyze

```bash
python -m obp analyze
```

Reads `sent.csv`, `landed.csv`, `blocks.csv` and `windows.csv`, then writes `results.csv` and
`results.md`. No flags. It is fully offline when those CSVs already exist.

## Safety and spend control

- Dry run is the default for `run` and `fund`. A dry-run transaction is built and signed with a
  throwaway in-memory key that is never funded and never saved.
- Live requires `--live`. On mainnet it also requires `--mainnet`. The cluster is identified from
  the genesis hash; `RPC_URL` and `SEND_RPC_URL` must report the same cluster.
- The spend ledger is persistent and split by cluster (`spend_ledger_mainnet.json`,
  `spend_ledger_localnet.json`, and so on). Reservations are never released, including for
  transactions that do not land.
- The absolute ceiling is 0.05 SOL (50,000,000 lamports). No CLI flag or environment variable can
  raise it.
- Every probe is memo-only. It never touches another user's account, never front-runs and never
  performs MEV. There are no Jito tips and no Jito bundles.
- Keys are loaded only from the `./keys` volume, which is git-ignored, or from paths listed in
  `OBP_KEYPAIRS`. Key material is never written to the data directory or logs.
- `sendTransaction` is never retried automatically. A failed send is recorded in `sent.csv`.

## Cost

Priority fee per transaction equals `ceil(CU limit * price / 1,000,000)` lamports. With a 21,000 CU
limit, the five ladder levels cost 0, 21, 210, 2,100 and 21,000 lamports. Base fee is 5,000
lamports per signature.

| Fee level (micro-lamports/CU) | Priority fee (lamports) |
|---:|---:|
| 0 | 0 |
| 1,000 | 21 |
| 10,000 | 210 |
| 100,000 | 2,100 |
| 1,000,000 | 21,000 |

Worst case per burst: 5 x 5,000 base + 23,331 priority = **48,331 lamports**.

| Item | Transactions | SOL |
|---|---:|---:|
| Pilot, 10 bursts | 50 | ~0.0005 |
| Main run, 720 txs (12 validators x 6 bursts x 2 arms) | 720 | ~0.0070 |
| Repeat day, half size | 360 | ~0.0035 |
| Funding three extra payer keys | 3 | ~0.00002 |
| **Total fees burned** | | **~0.011** |

The first funding of four payer accounts also needs rent-exempt deposits of about 0.0036 SOL.
That is not burned; it is refundable when the accounts are emptied.

## Raw data dictionary

A session lives in one directory, normally `data/runs/<YYYYMMDD>_<name>/`. The files below are
written there and are intended to be committed.

| File | Contents |
|---|---|
| `validators.csv` | Node inventory used by `plan`. |
| `plan.json` | Selected validators and planned windows. |
| `sent.csv` | One row per probe transaction the tool built. |
| `landed.csv` | One row per live send, with landing and block position. |
| `blocks.csv` | Every transaction in the blocks we landed in. |
| `windows.csv` | Post-hoc verification of each planned window. |
| `results.csv` | Per-burst Kendall tau results. |
| `results.md` | Human-readable summary of `results.csv` and the block checks. |
| `run_meta.json` | Run metadata for the latest `run` invocation. |
| `spend_ledger_<cluster>.json` | Persistent spend reservations for that cluster. |
| `obp.log` | Timestamped log. |
| `leader_schedule_cache.json` | Cached epoch leader schedule (large, optional). |

### validators.csv

`identity`, `vote`, `stake_sol`, `client_id`, `version`, `label`, `running_jito`, `running_bam`,
`tpu_quic`.

### plan.json

`created_slot`, `created_at`, and `plan`. Each plan item has `target`, `label`, `version` and
`window_start`.

### sent.csv

| Column | Meaning |
|---|---|
| `run` | Run id, generated from the UTC time when `run` started. |
| `cluster` | Cluster name from the genesis hash. |
| `burst` | Burst index within the plan, in send order. |
| `target` | Planned leader identity. |
| `label` | Client label of the target from `validators.csv`. |
| `window_start` | First slot of the target 4-slot window. |
| `send_seq` | Position of this transaction within the burst. |
| `order_mode` | Fee rotation for this burst: `asc`, `desc` or `shuffle`. |
| `payer_arm` | `same` or `multi`. |
| `cu_price` | Priority fee in micro-lamports per CU. |
| `cu_limit` | Compute-unit limit set in the transaction. |
| `payer` | Fee-payer public key. |
| `signature` | Transaction signature. |
| `memo` | Short memo tag. Full metadata is keyed by signature in this file. |
| `send_ts_ns` | Send timestamp in nanoseconds since the Unix epoch. |
| `slot_at_send` | Current processed slot when the send was issued. |
| `slot_after_send` | Processed slot immediately after the burst was sent. |
| `send_offset` | `slot_at_send - window_start`. Negative means before the window. |
| `in_window_at_send` | True when `slot_at_send < window_start + 4`. |
| `on_time` | True when `slot_at_send < window_start`. |
| `live` | `True` for a real send, `False` for dry run. |
| `send_result` | `ok`, `dry-run`, or an error string. |

### landed.csv

| Column | Meaning |
|---|---|
| `signature` | Transaction signature. |
| `run` | Run id copied from `sent.csv`. |
| `burst` | Burst index copied from `sent.csv`. |
| `target` | Planned leader identity. |
| `label` | Target client label. |
| `window_start` | Planned window start. |
| `send_seq` | Position within the burst. |
| `order_mode` | Fee rotation. |
| `payer_arm` | `same` or `multi`. |
| `cu_price` | Priority fee in micro-lamports per CU. |
| `cluster` | Cluster name. |
| `landed` | True when `getSignatureStatuses` returned a status. |
| `slot` | Landing slot. |
| `slot_leader` | Actual leader of the landing slot. |
| `leader_is_target` | True when the actual leader equals `target`. |
| `in_target_window` | True when `window_start <= slot < window_start + 4`. |
| `block_index` | Zero-based index in ledger order, or blank if the block was unavailable. |
| `block_tx_count` | Number of transactions in the landing block. |
| `block_time` | Block time from the RPC, in Unix seconds. |
| `our_tx_count` | Number of our signatures found in that block. |
| `err` | Transaction error from the status response, if any. |

### blocks.csv

| Column | Meaning |
|---|---|
| `slot` | Block slot. |
| `block_time` | Block time in Unix seconds. |
| `index` | Zero-based position in the block's transaction list (ledger order). |
| `signature` | Transaction signature. |
| `fee` | Total fee in lamports. |
| `cu_consumed` | Compute units consumed. |
| `num_sigs` | Number of signatures. |
| `is_vote` | True for a vote transaction. |
| `err` | True when the transaction failed. |

### windows.csv

| Column | Meaning |
|---|---|
| `window_start` | First slot of the planned 4-slot window. |
| `window_end` | Last slot of the window (`window_start + 3`). |
| `target` | Planned leader identity. |
| `label` | Target client label. |
| `leaders` | Actual leaders for the four slots, semicolon-separated. |
| `leaders_ok` | True when all four leaders equal `target`. |
| `block_slots` | Slots in the window that produced a block, semicolon-separated. |
| `block_count` | Number of slots that produced a block. |
| `expected` | Expected number of leaders/blocks (4). |
| `sources` | `plan`, `sent`, or `plan+sent`. |
| `err` | RPC error, if any. |
| `checked_at` | UTC timestamp of the check. |

### results.csv

| Column | Meaning |
|---|---|
| `run` | Run id. |
| `burst` | Burst index. |
| `slot` | Common landing slot of the group. |
| `target` | Planned leader identity. |
| `label` | Target client label. |
| `order_mode` | Fee rotation. |
| `payer_arm` | `same` or `multi`. |
| `n_same_block` | Number of our transactions from this burst in this block. |
| `in_target_window` | Whether the landing slot was inside the planned window. |
| `tau_fee` | Kendall tau of block index against fee. Positive means higher fee earlier. |
| `p_fee` | Two-sided permutation p-value for `tau_fee`. |
| `tau_send` | Kendall tau of block index against `send_seq`. Positive means earlier send earlier. |
| `p_send` | Two-sided permutation p-value for `tau_send`. |

Rows are written only for groups with at least three of our transactions in the same block.

### results.md

Human-readable report generated by `analyze`. It contains the serialized landed count, the
measurement send window, per-burst tau tables, pooled per-label tau tables, landing and timing
rates by label and fee level, verified window counts, and the whole-block approximate priority
ordering. Tau values carry an explicit sign; rates and probabilities do not.

### run_meta.json

`created_at`, `cluster`, `args` (parsed `run` arguments), `argv`, `git_commit`, `obp_version`,
`solders_version`.

### spend_ledger_<cluster>.json

`reserved_lamports` (total worst-case fees reserved so far for that cluster) and `cap_lamports`
(the cap in force for this ledger). Reservations accumulate across runs and are never released.

## Reproducing from raw data

`analyze` is fully offline when `sent.csv`, `landed.csv`, `blocks.csv` and `windows.csv` are
present. `collect` is idempotent: it does not refetch slots already in `blocks.csv`, and it
rewrites `landed.csv` from the same sent rows.

```bash
# Rebuild derived files from a committed session
.venv/bin/python -m obp --run-dir data/runs/20261028_pilot analyze

# If needed, re-run collection first (network required for statuses and new slots)
.venv/bin/python -m obp --run-dir data/runs/20261028_pilot collect --wait-sec 0
.venv/bin/python -m obp --run-dir data/runs/20261028_pilot verify-windows
.venv/bin/python -m obp --run-dir data/runs/20261028_pilot analyze
```

The signature list is the `signature` column of `sent.csv`; each one can be checked on any Solana
explorer or with `getSignatureStatuses`. `landed.csv` adds the landing slot and block index.

## Tests

Unit tests:

```bash
.venv/bin/python -m pytest -q
```

Localnet end-to-end:

`scripts/localnet_e2e.sh` runs the full pipeline against a throwaway `solana-test-validator`
(4.3.2): `inventory`, `plan`, three live bursts, `collect`, `verify-windows` and `analyze`. It
refuses to send unless the genesis hash identifies an unknown/local cluster. The final check
requires all five probe transactions to land.

```bash
solana-test-validator --reset --quiet &
RPC_URL=http://127.0.0.1:8899 \
OBP_KEYPAIRS=/path/to/localnet/payer.json \
scripts/localnet_e2e.sh
```

The localnet keys must be funded with the test validator's own faucet or a local transfer; the
script never touches mainnet, devnet or testnet.

## Repository layout

```text
obp/                Python package and CLI
tests/              pytest suite
scripts/            localnet end-to-end script
data/runs/          committed measurement sessions
keys/               git-ignored keypair volume; never committed
```
