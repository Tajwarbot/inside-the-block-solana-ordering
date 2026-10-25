# obp: Solana intra-block ordering probe (starter)

Dry-run by default. Nothing is sent unless you pass `--live` **and** mount keypair files via `OBP_KEYPAIRS`.

```bash
cp .env.example .env
docker compose up                      # inventory -> plan -> 3 dry-run bursts -> collect -> analyze
# local (no docker):
pip install -r requirements.txt
python -m obp inventory                # data/validators.csv  (clientId, version, stake, Jito/BAM flags)
python -m obp plan --per-label 2 --windows 6 --labels JitoLabs,AgaveBam,HarmonicAgave,HarmonicFiredancer,Firedancer,Agave
python -m obp calibrate --sim-payer <any funded pubkey>   # CU of the probe tx via simulateTransaction (free)
python -m obp run                      # DRY RUN: builds + signs with a throwaway in-memory key, logs, never sends
python -m obp run --live --cap-sol 0.04 --payer-arm same   # REAL. needs OBP_KEYPAIRS=/keys/payer0.json[,...]
python -m obp collect                  # data/landed.csv (slot, leader, in_target_window, block_index) + data/blocks.csv
python -m obp analyze                  # data/results.csv: Kendall tau of block index vs fee and vs send order
```

Spend cap (`obp/spendcap.py`):
- Every transaction reserves its worst-case fee (5,000 × signatures + CU limit × price) *before* it is sent.
- Reservations are never released and persist in `data/spend_ledger.json`.
- The hard ceiling is 0.05 SOL whatever the CLI says.

Raw data for judges: `data/sent.csv` (every signature, send time, slot at send), `data/landed.csv`, `data/blocks.csv`, `data/obp.log`.

TODO before a real entry:
- Report writer with plots.
- A per-run timestamped data folder.
- Optional direct-QUIC sender to compare send paths.
- Tests on `solana-test-validator`.
