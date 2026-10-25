# obp: order-of-block probe

`obp` measures how Solana leaders order our own transactions inside a block. It sends small
memo-only transactions into planned 4-slot leader windows, records where they land, and reports
rank correlations between block position and priority fee, and between block position and send
order. Post-Alpenglow mainnet slot time is about **0.212 s**, so a 4-slot leader window is about
**0.85 s**.

Default is dry run. `run` and `fund` send nothing without `--live`; mainnet live runs also need
`--mainnet`. The spend cap is hard-coded at 0.05 SOL.

## Results (measured 2026-10-25 UTC)

Main sequential session: 125 bursts, 625 txs, all 625 landed. Send order decided block and position for every client label and fee had no visible effect. A sequential burst spans about two slots (median 413.8 ms), so the five fees never competed in one scheduler batch. This does not show that schedulers ignore fees.

The exploratory second session used `--send-mode parallel` (66 bursts, 330 txs, 325 landed; the 5 misses were send errors at the public RPC). Higher fee tended to come first for Firedancer, HarmonicAgave, HarmonicFiredancer and same-payer AgaveBam; JitoLabs, FireBAM and Rakurai were not significant; vanilla Agave went the other way on 5 bursts (weak). Whole-block priority ordering was near zero.

Tables, p-values and caveats: [REPORT.md](REPORT.md).

## What it measures

The unit of work is a burst: five memo transactions with priority fees of 0, 1,000, 10,000,
100,000 and 1,000,000 micro-lamports per compute unit (CU). All five use the same CU limit
(21,000 by default) and the same instruction shape. The only intentional difference between them
is the priority fee.

Each burst records:

- the slot at send time and whether the send preceded the target window;
- the landing slot, the actual leader of that slot and whether it is the planned target;
- the index of each landed transaction in ledger order;
- every transaction in each block we hit, for a whole-block supplementary check.

Main statistics: Kendall tau of block index against fee, and of block index against send order,
each with a permutation p-value. Only same-burst transactions that landed in the same block are
compared. Primary statistics keep rows with `in_target_window=True` and `leader_is_target=True`;
a separate sensitivity table shows all landed rows regardless of leader.

## Design rationale

### Fee ladder independent of send order

A burst sends the same five fee levels in one of three rotations: ascending, descending or
shuffled. The mode rotates by burst number. This separates fee from send order. Descending sends
the highest fee first, so fee order and send order align there. A pure arrival rule would also
produce a positive fee tau, which makes descending the confounded rotation. Ascending sends the
highest fee last, so fee and send order oppose; ascending is therefore the discriminating
rotation. The pre-registered primary set is ascending + shuffled. If position tracks fee in
ascending bursts, the data supports a fee rule. If it tracks send sequence instead, the data
supports an arrival-order rule. If it tracks neither, the result is noise.

### Same-payer and multi-payer arms

In the `same` arm all five transactions share one fee payer, so they write-lock the same account
and the scheduler must serialise them. They cannot execute in parallel, which makes this the
cleanest test of the priority rule.

In the `multi` arm each transaction uses a different payer, so there is no account-lock conflict
and the runtime can execute them on different threads. Comparing arms shows whether the ordering
rule holds when parallel execution is possible. `--payer-arm alternate` runs both arms in one
session (`same` for even burst indices, `multi` for odd), so time-of-day cannot confound the
comparison. This is the recommended main-run mode.

### Fixed CU limit

Every probe transaction sets the same CU limit and uses the same instructions. Priority fee per CU
is the only variable the scheduler can rank on. The fee is charged on the CU limit, not on CU
consumed, so the worst-case fee is known before sending.

### Window targeting with lead slots

A leader normally holds four consecutive slots (about 0.85 s at 0.212 s/slot). The planner reads
the epoch leader schedule and chooses future windows for validators of the selected client labels.
The sender fetches the blockhash and prebuilds/signs the whole burst at
`window_start - lead_slots - 6` or earlier, then waits until `window_start - lead_slots` and sends.
The default lead is two slots. A three-slot lead on localnet landed transactions in the block
before the target window, because the current leader included them. The pilot therefore compares
lead 1 against lead 2. Polling is every 0.05 s inside the last six slots. The far-sleep stays six
slots short, so it does not overshoot the short post-Alpenglow slots. If the final wait returns a
slot at or after `window_start`, the burst is skipped before any fee is reserved.

Each row keeps the burst-level `slot_at_send`/`slot_after_send` and also records a per-transaction
`est_slot_at_send` = `slot_at_send + floor((send_ts_ns - t_wait_return_ns) / 0.212)`. The per-tx
`send_offset`, `in_window_at_send`, `send_phase` and `on_time` are based on that estimate, so a
burst that spans more than one slot is not mislabelled. `send_ts_ns` is taken immediately before
the HTTP send and `send_done_ns` immediately after it. A burst is marked `burst_late=True` when
its post-send slot is at or after `window_start + 4`.

The schedule alone does not fully predict the scheduler, so a separate step confirms what
happened.

### verify-windows

`verify-windows` queries `getSlotLeaders` and `getBlocks` for each planned window. A window is
**verified** only when its `window_end` is before the current finalized slot. Later windows are
written with `status=planned` and counted separately as "planned (not yet elapsed)". The command
records whether the target identity led all four slots and which slots produced a block. It works
on dry-run data because it needs no signatures. Transactions that landed under a different leader
get `leader_is_target=False` and `in_target_window=False`; they stay out of the primary
target-window comparison and still appear in the sensitivity table.

### Whole-block supplementary check

`blocks.csv` contains every transaction in each block where one of our transactions landed: ledger
index, fee, CU consumed, signature count, vote flag and error flag. This supports a rough check of
whether the whole block is ordered by approximate priority fee per CU, and where our transactions
sit against unrelated competition. The approximation is
`(fee - 5000 * num_sigs) * 1e6 / cu_consumed`. It ignores exact per-instruction costs and other
fee components, so results are labelled approximate throughout.

## How the brief's topics are addressed

### Leader schedule and leader types/clients

`inventory` joins `getClusterNodes`, `getVoteAccounts` and the Jito validator API. It records
identity, vote account, active stake, `clientId`, version, a human label, Jito/BAM flags and the
TPU QUIC address. `plan` reads the epoch leader schedule, converts relative slot indices to
absolute slots and selects windows for the requested number of validators per client label.
`verify-windows` confirms the leader after the fact. This covers the schedule and the client types
actually targeted. It does not claim that the gossip label fully describes the ordering path
inside a validator.

### Path from backend to the executing node

Probe transactions go through `sendTransaction` on the configured RPC. `SEND_RPC_URL` can point at
a different sender, for example a free Helius endpoint. Requests use `skipPreflight: true`,
`maxRetries: 0` and base64 encoding. Skipping preflight stops the client from rejecting a
transaction for a stale blockhash or a simulated error before the leader sees it. `maxRetries: 0`
keeps the send decision under our control. The tool never retries a send automatically.

The payer accounts are unstaked, so stake-weighted QoS (SWQoS) may give them little bandwidth.
That can lower landing rates, especially at low fees. The code records landing rates by client and
fee level rather than omitting them. The exact forwarding path through the RPC operator, the QUIC
connection to the leader's TPU and any relay in between are not observable from our data. This is
a stated limitation.

### Our transactions' interaction with each other

The `same` arm makes the interaction explicit: identical fee payer, hence a write-lock conflict,
so the five probes cannot execute in parallel. The `multi` arm removes the conflict. The fee
ladder is rotated independently of send order in both arms. If same-payer bursts follow fee but
multi-payer bursts do not, lock conflict and parallel execution become a plausible explanation.

### Competition inside the block

`blocks.csv` records every transaction in the landed blocks with an `is_vote` flag, and `analyze`
computes an approximate priority-fee ordering over the non-vote transactions. Our transactions are
a small part of a busy block. This is supplementary evidence, not the primary result. The primary
evidence is always transactions we sent ourselves.

### Send order

`send_seq` is the planned position in the burst. Sends are sequential by default
(`--send-mode seq`, 20 ms gap); `--send-mode parallel` runs them in parallel for a separate
comparison. The actual order is recorded as `send_rank`, derived by sorting `send_ts_ns`.
`tau_send` uses `send_rank` (falling back to `send_seq` only for older files). Because the
rotations repeat across bursts, a stable relationship between actual send order and block index
is distinguishable from a fee relationship.

### Noise versus rule

The tool reports tau, permutation p-values, pooled per-label results and landing/timing counts.
Small samples are expected. A single burst is not treated as evidence. The report keeps a valid
"no rule" outcome (H0) rather than forcing a fee or arrival conclusion.

The pre-registered primary test is the pooled mean `tau_fee` per client label on the same-payer
arm, using only target-window rows with the planned leader and only ascending + shuffled bursts.
Holm correction is applied across the per-label primary p-values, separately for H1 (fee) and H2
(send order). Descending bursts are excluded from the primary test because fee order equals send
order there (confounded). They are a consistency check only. Everything else (multi-payer arm,
descending mode, per-burst, whole-block, landing rates) is exploratory and is marked that way in
`results.md`.

Verdict rule per label:

| Outcome | Condition |
|---|---|
| H1 (fee rule) | Pooled mean `tau_fee > 0` with Holm-adjusted `p < 0.05` on the same-payer ascending+shuffled primary set, and `tau_fee > 0` on ascending bursts alone. |
| H2 (arrival rule) | Pooled mean `tau_send > 0` with Holm-adjusted `p < 0.05` on the same primary set, and `tau_send > 0` on ascending bursts alone. |
| Mixed | Both the H1 and H2 markers hold. |
| H0 | Otherwise, reported as "no rule detected (H0 not rejected)". |
| Insufficient data | No primary groups. |

Descending bursts cannot support H1/H2 on their own because fee order and send order coincide
there. They are reported as a consistency check.

Only bursts where at least three of our five transactions co-landed in the target block enter the
tau tests. Higher-fee transactions may land more often, so this conditions on landing and can bias
the ordering sample toward higher fees. This is a selection effect, not a finding. `results.md`
reports the landed-per-burst distribution so readers can judge it.

Dry-run timing rates, verified windows and landing rates are reported separately from the ordering
tests. Landing rates use live-only denominators; dry-run timing has its own columns.

## What this does not separate

- The experiment does not control or measure jitter from RPC forwarding, SWQoS, TPU admission and
  relay behaviour, so network path is not separated from scheduler.
- `block_index` is ledger order. On parallel threads the real execution order can differ, so
  ledger entry order is not execution order.
- Leader-side relays and block engines (BAM, Harmonic, Jito) are not separated from the client's
  own scheduler. A label such as `AgaveBam` describes a stack, not one isolated ordering
  algorithm.
- Samples per validator and per client are small. The design increases repetitions but cannot
  make a handful of bursts statistically strong.
- All data collected by this tool is post-Alpenglow. The upgrade was on 2026-10-21, so do not mix
  this data with pre-upgrade measurements. Blocks fetched now contain no vote transactions.

## Quickstart

### Docker Compose (dry run by default)

```bash
cp .env.example .env
docker compose up
```

The Compose entrypoint runs `inventory`, `plan`, three dry-run bursts, `collect`,
`verify-windows` and `analyze`. Dry-run transactions use a throwaway in-memory key. They are
signed and never sent.

The entrypoint always writes the session under `data/runs/<id>` and sets the global ledger root:

```sh
export OBP_DATA=/data/runs/${OBP_RUN_ID:-dryrun}
export OBP_LEDGER_DIR=/data
```

Overrides:

```bash
# More dry-run bursts in the default dryrun session
OBP_BURSTS=10 docker compose up

# A named session directory under data/runs/
OBP_RUN_ID=20261028_pilot docker compose up

# Live mainnet pilot (explicit opt-in, keys mounted read-only from ./keys)
OBP_RUN_ID=20261028_pilot OBP_BURSTS=10 OBP_ARGS="--live --mainnet --cap-sol 0.002" docker compose up

# Live main run with the alternating payer arm (OBP_BURSTS=0 means all planned bursts)
OBP_RUN_ID=20261028_main OBP_BURSTS=0 OBP_ARGS="--live --mainnet --cap-sol 0.04 --payer-arm alternate" docker compose up

# Run a single command in an explicit session directory
docker compose run --rm --entrypoint python \
  -e OBP_DATA=/data/runs/20261028_pilot obp -m obp analyze
```

`$OBP_LEDGER_DIR` defaults to the `data` root (in Docker, `/data`), so all sessions share one
per-cluster spend ledger. `run` and live `fund` write `spend_ledger_snapshot.json` into the
session, so the committed state travels with the run.

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
every session, so each dataset is timestamped and committed. `data/runs/` is not git-ignored;
other directories under `data/` are.

Live runs need payer keys. Every live command must write to a named session directory under
`data/runs/<id>`. Runbook order: pilot (cap 0.002) -> fund -> main (alternate arm) -> repeat ->
collect -> analyze.

```bash
export OBP_KEYPAIRS=/absolute/path/payer.json,/absolute/path/payer2.json,/absolute/path/payer3.json,/absolute/path/payer4.json,/absolute/path/payer5.json

# 1. Pilot: small cap, 10 bursts. Compare --lead-slots 1 and 2 before the main run.
export OBP_DATA=data/runs/20261028_pilot
mkdir -p "$OBP_DATA"
.venv/bin/python -m obp inventory
.venv/bin/python -m obp plan --per-label 2 --windows 6 --labels \
  AgaveBam,JitoLabs,HarmonicAgave,HarmonicFiredancer,Firedancer,FireBAM,Agave
.venv/bin/python -m obp balances
.venv/bin/python -m obp run --live --mainnet --cap-sol 0.002 --lead-slots 2 \
  --max-bursts 10 --payer-arm same
.venv/bin/python -m obp collect --wait-sec 20
.venv/bin/python -m obp verify-windows && .venv/bin/python -m obp analyze

# 2. Fund the other four payers (alternate/multi need five funded payers).
export OBP_DATA=data/runs/20261028_main
mkdir -p "$OBP_DATA"
.venv/bin/python -m obp fund --live --mainnet --lamports 5000000 --cap-sol 0.04

# 3. Main run: alternate interleaves same/multi by burst index within one run, so
#    time-of-day does not confound the arms.
.venv/bin/python -m obp inventory
.venv/bin/python -m obp plan --per-label 2 --windows 6 --labels \
  AgaveBam,JitoLabs,HarmonicAgave,HarmonicFiredancer,Firedancer,FireBAM,Agave
.venv/bin/python -m obp run --live --mainnet --cap-sol 0.04 --payer-arm alternate
.venv/bin/python -m obp collect --wait-sec 20
.venv/bin/python -m obp verify-windows && .venv/bin/python -m obp analyze

# 4. Repeat at a different time of day in a fresh data/runs/<id>, then collect and analyze.
```

The multi-payer arm needs at least one distinct payer per fee level (five by default); the
alternate arm also needs at least five. Run `fund` first, or fund the keys yourself.

With Docker, keys are read from the read-only `./keys` volume. The default paths are
`/keys/payer.json` for the same-payer arm and `/keys/payer.json` plus `/keys/payer2.json` through
`/keys/payer5.json` for the multi-payer and alternate arms. The Compose examples above use
`OBP_RUN_ID` and `OBP_ARGS`. For a single command in an explicit session, bypass the pipeline
entrypoint:

```bash
docker compose run --rm --entrypoint python \
  -e OBP_DATA=/data/runs/20261028_pilot obp -m obp analyze
```

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
                   [--min-labels N] [--min-validators N] [--min-windows N]
                   [--min-lead-slots N] [--min-gap-slots N]
```

| Flag | Default | Meaning |
|---|---|---|
| `--per-label` | `2` | Validators to target per client label. |
| `--windows` | `4` | Maximum windows to plan per selected validator. |
| `--horizon` | `20000` | Only plan windows within this many slots. |
| `--labels` | empty | Comma list restricting client labels. Empty means all labels with enough windows. |
| `--min-labels` | `3` | Abort if fewer than this many distinct labels remain after gap filtering. |
| `--min-validators` | `6` | Abort if fewer than this many distinct targets remain after gap filtering. |
| `--min-windows` | `3` | A validator must have at least this many windows in the horizon to be eligible. |
| `--min-lead-slots` | `25` | Only plan windows starting at least this many slots after the current slot. |
| `--min-gap-slots` | `12` | Never plan two windows, for any targets, that start less than this many slots apart. A fairness rule picks who gets the slot. |

Writes `plan.json` and prints the selected validators, per-label/per-validator burst counts and
the planned burst count. The global `--min-gap-slots` filter sweeps windows in time order and,
within a 64-slot slack, picks the target (then label) with the fewest kept bursts so far, so a
target with dense windows cannot starve the other labels.

### calibrate

```bash
python -m obp calibrate --sim-payer PUBKEY
```

Runs `simulateTransaction` (free, no signature verification) with an SPL Memo and prints the CU
consumed. `PUBKEY` can be any existing funded account. Read-only. Memo tags are intentionally
non-unique and short because SPL Memo costs roughly 380 CU per byte; the signature is the unique
key for all metadata.

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
subject to the 0.05 SOL hard ceiling; like `run`, it checks the global per-cluster reserved total.
Funding transfers are counted in the spend ledger.

### run

```bash
python -m obp run [--live] [--mainnet] [--cap-sol SOL] [--fee-levels LIST]
                  [--cu-limit N] [--lead-slots N] [--send-mode seq|parallel]
                  [--gap-ms N] [--payer-arm same|multi|alternate] [--max-bursts N]
```

| Flag | Default | Meaning |
|---|---|---|
| `--live` | off | Actually send. Without it nothing leaves the process. |
| `--mainnet` | off | Extra explicit opt-in required for `--live` on mainnet. |
| `--cap-sol` | `0.04` | Cap on the project-wide reserved total for this cluster (global across sessions), not a per-run allowance. Cannot exceed 0.05 SOL. |
| `--fee-levels` | `0,1000,10000,100000,1000000` | Priority fees in micro-lamports per CU. |
| `--cu-limit` | `OBP_CU_LIMIT` or `21000` | Compute-unit limit for every probe transaction. |
| `--lead-slots` | `2` | Send this many slots before the target window starts. The blockhash and signatures are prepared six slots earlier still. The pilot compares 1 vs 2; 3 landed early on localnet. |
| `--send-mode` | `seq` | Send the burst sequentially or with one thread per transaction. |
| `--gap-ms` | `20` | Sleep between sends in sequential mode. Must be >= 0. |
| `--payer-arm` | `same` | `same` (one fee payer, lock conflict), `multi` (parallel payers), or `alternate` (same/multi by burst index). |
| `--max-bursts` | `0` | Limit to the earliest N planned bursts. `0` means all. |

Reads `plan.json`, appends to `sent.csv`, writes `run_meta.json`, and reserves the per-transaction
worst-case fee in the global per-cluster spend ledger immediately before each send. A burst whose
final wait is already at/after the window start is skipped without reserving. Each row, including
its signature, is flushed and fsynced to `sent.csv` immediately after its own send and before any
post-send RPC (the `slot_after_send` lookup); if that lookup fails, `slot_after_send` stays blank
rather than losing the send. A returned signature that does not match the transaction is recorded
as `error:signature-mismatch`. Dry-run rows are written with `live=False`.

`--payer-arm alternate` is recommended for the main run: it interleaves same-payer and multi-payer
bursts within one run (`same` for even burst indices, `multi` for odd), so time-of-day cannot
confound the two arms. It needs at least five funded distinct payers, so run `fund` first. Live
`multi` and `alternate` modes reject too few distinct payers (one per fee level, and at least five
for alternate) and record `n_unique_payers` per burst.

### collect

```bash
python -m obp collect [--wait-sec N]
```

| Flag | Default | Meaning |
|---|---|---|
| `--wait-sec` | `20` | If the newest send is younger than this, sleep the remainder before checking statuses. |

Reads `sent.csv`, queries `getSignatureStatuses` for **every live row with a signature** regardless
of `send_result` (an RPC error does not prove the transaction was not forwarded), fetches blocks for
newly landed slots and writes `landed.csv` and `blocks.csv`. `send_result` is kept in `landed.csv`
as the send acknowledgement. Re-running is idempotent: slots already present in `blocks.csv` are
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

Reads `sent.csv`, `landed.csv`, `blocks.csv` and `windows.csv`, then writes `results.csv`,
`results_by_group.csv` and `results.md`. No flags. It is fully offline when those CSVs already
exist. Primary stats use only target-window rows with the planned leader; `results.md` also has the
all-landed sensitivity table, the H1/H2/H0 verdict table, grouped results by payer arm and order
mode, Holm-corrected primary p-values for fee and send order, and planned-versus-verified window
counts.

## Safety and spend control

- `run` and `fund` default to dry run. A dry-run transaction is built and signed with a throwaway
  in-memory key that is never funded and never saved.
- Live requires `--live`. On mainnet it also requires `--mainnet`. The cluster is identified from
  the genesis hash; `RPC_URL` and `SEND_RPC_URL` must report the same cluster.
- The spend ledger is persistent, split by cluster (`spend_ledger_mainnet.json`,
  `spend_ledger_localnet.json`, and so on) and global across sessions. It lives in
  `$OBP_LEDGER_DIR` (default: the `data` root; `/data` in Docker), not in the per-session
  directory. `$OBP_LEDGER_DIR` is expanded and resolved with `realpath`, so a relative or `~`
  value is recorded as an absolute path. Read-modify-write takes an OS `fcntl.flock` on a `.lock`
  file and re-reads the file inside the lock, so concurrent sessions cannot jointly exceed the
  cap. Reservations are never released, including for transactions that do not land. `run` and
  live `fund` write `spend_ledger_snapshot.json` into the session for the commit; its
  `source_ledger` field is the resolved global ledger path.
- Because the ledger is global, `--cap-sol` is a running total across every session for that
  cluster, not a fresh allowance for each run. Reservations from earlier sessions still count.
- The absolute ceiling is 0.05 SOL (50,000,000 lamports). No CLI flag or environment variable can
  raise it.
- Every probe is memo-only. It never touches another user's account, never front-runs and never
  performs MEV. There are no Jito tips and no Jito bundles.
- Keys are loaded only from the `./keys` volume, which is git-ignored, or from paths listed in
  `OBP_KEYPAIRS`. Key material is never written to the data directory or logs.
- `sendTransaction` is never retried automatically. A failed send is recorded in `sent.csv`.
- Skipped/missing-slot JSON-RPC errors (`-32004`, `-32007`, `-32009`) become a read sentinel only for
  `getBlock`, `getBlockTime`, `getBlocks` and `getSlotLeaders`. For `sendTransaction`, `getSlot`,
  `getSignatureStatuses` and every other method they are real errors. A `sendTransaction` result must
  be a signature string; a sentinel or other non-string result is recorded as an error, never `ok`.

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
| Funding four extra payer keys | 4 | ~0.00002 |
| **Total fees burned** | | **~0.011** |

The multi-payer arm uses five payer accounts (one per fee level). Their first funding also
needs rent-exempt deposits of about 0.0045 SOL. That is not burned; it is refundable when the
accounts are emptied.

## Raw data dictionary

A session lives in one directory, normally `data/runs/<YYYYMMDD>_<name>/`. The files below are
written there and are meant to be committed.

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
| `obp.log` | Timestamped log. |
| `spend_ledger_snapshot.json` | Copy of the global per-cluster ledger state, written by `run` and live `fund`. |
| `results_by_group.csv` | Grouped exploratory results by payer arm and order mode, per label. |
| `leader_schedule_cache.json` | Cached leader schedule keyed by `(cluster, epoch)` (large, optional). |

The live ledger is global, not per-session. Each session commits only
`spend_ledger_snapshot.json` (see the ledger section below).

### validators.csv

`identity`, `vote`, `stake_sol`, `client_id`, `version`, `label`, `running_jito`, `running_bam`,
`tpu_quic`.

### plan.json

`created_slot`, `created_at`, `cluster`, and `plan`. Each plan item has `target`, `label`,
`version` and `window_start`.

### sent.csv

| Column | Meaning |
|---|---|
| `run` | Run id, generated when `run` started as `%m%d%H%M`. |
| `cluster` | Cluster name from the genesis hash. |
| `burst` | Burst index within the plan, in send order. |
| `target` | Planned leader identity. |
| `label` | Client label of the target from `validators.csv`. |
| `window_start` | First slot of the target 4-slot window. |
| `send_seq` | Planned position of this transaction within the burst. |
| `send_rank` | Actual send order, assigned by sorting `send_ts_ns` (used by `tau_send`). |
| `order_mode` | Fee rotation for this burst: `asc`, `desc` or `shuffle`. |
| `payer_arm` | `same` or `multi`. |
| `n_unique_payers` | Number of distinct fee payers used in this burst. |
| `cu_price` | Priority fee in micro-lamports per CU. |
| `cu_limit` | Compute-unit limit set in the transaction. |
| `payer` | Fee-payer public key. |
| `signature` | Transaction signature. |
| `memo` | Short memo tag. Full metadata is keyed by signature in this file. |
| `send_ts_ns` | Timestamp immediately before the HTTP send, in nanoseconds since the Unix epoch. |
| `send_done_ns` | Timestamp immediately after the HTTP send returns. |
| `slot_at_send` | Burst-level processed slot when the final wait returned. |
| `est_slot_at_send` | Per-tx estimate: `slot_at_send + floor((send_ts_ns - wait_return_ns) / 0.212)`. |
| `slot_after_send` | Processed slot immediately after the burst was sent. |
| `send_offset` | `est_slot_at_send - window_start`. Negative means before the window. |
| `in_window_at_send` | True when the send was not after the window: `est_slot_at_send < window_start + 4`. |
| `send_phase` | `early` when `est_slot_at_send < window_start`, `inside` when `window_start <= est_slot_at_send < window_start + 4`, otherwise `late`. |
| `burst_late` | True when `slot_after_send >= window_start + 4`, blank if the post-send slot lookup failed. |
| `on_time` | True when `est_slot_at_send < window_start`. |
| `live` | `True` for a real send, `False` for dry run. |
| `send_result` | Send acknowledgement: `ok`, `dry-run`, `not-sent:...`, or an error string. |

### landed.csv

| Column | Meaning |
|---|---|
| `signature` | Transaction signature. |
| `run` | Run id copied from `sent.csv`. |
| `burst` | Burst index copied from `sent.csv`. |
| `target` | Planned leader identity. |
| `label` | Target client label. |
| `window_start` | Planned window start. |
| `send_seq` | Planned position within the burst. |
| `send_rank` | Actual send order from `send_ts_ns`. |
| `order_mode` | Fee rotation. |
| `payer_arm` | `same` or `multi`. |
| `cu_price` | Priority fee in micro-lamports per CU. |
| `cluster` | Cluster name. |
| `send_result` | Send acknowledgement copied from `sent.csv`. |
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
| `status` | `verified` when `window_end <` the finalized slot, else `planned` (not yet elapsed). |
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
| `tau_send` | Kendall tau of block index against actual `send_rank`. Positive means earlier send earlier. |
| `p_send` | Two-sided permutation p-value for `tau_send`. |

Rows are written only for groups with at least three of our transactions in the same block.
`results.csv` keeps only target-window rows with the planned leader. `results_by_group.csv` has
the same columns grouped by `payer_arm` and `order_mode` per label, with burst and transaction
counts.

### results.md

Human-readable report generated by `analyze`. It contains the primary-versus-exploratory note,
the H1/H2/H0 verdict table per label (same-payer ascending+shuffled primary, with raw and
Holm-corrected p-values for both fee and send order), per-burst and pooled tau tables, grouped
payer-arm/order-mode results,
the all-landed sensitivity table, landing and timing rates (live-only denominators plus separate
dry-run columns) by label and fee level, the landed-per-burst distribution in the target window
(the selection diagnostic), verified-versus-planned window counts, and the whole-block approximate
priority ordering. Tau values carry an explicit sign; rates and probabilities do not.

### run_meta.json

`created_at`, `cluster`, `args` (parsed `run` arguments), `argv`, `git_commit`, `obp_version`,
`solders_version`.

### spend_ledger_<cluster>.json

`reserved_lamports` (total worst-case fees reserved so far for that cluster) and `cap_lamports`
(the cap in force for this ledger). The file is global for the cluster, normally at
`data/spend_ledger_<cluster>.json` (or `$OBP_LEDGER_DIR/spend_ledger_<cluster>.json`). Reservations
accumulate across sessions and are never released. A session copy is written to
`spend_ledger_snapshot.json`.

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
(4.3.2): `inventory`, `plan`, three live bursts with a 1-slot lead, `collect`, `verify-windows` and
`analyze`. It refuses to send unless the genesis hash identifies an unknown/local cluster. The
final check requires at least one landed transaction.

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
scripts/            localnet end-to-end script, burst split report (burst_split.py)
data/runs/          committed measurement sessions
keys/               git-ignored keypair volume; never committed
```
