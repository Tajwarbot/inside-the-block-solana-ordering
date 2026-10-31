#!/usr/bin/env bash
# Offline rebuild of every results.md/results.csv, the pooled tables and figures from committed CSVs.
# No network, no keys. Usage: bash scripts/reproduce.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
export OBP_LEDGER_DIR=${OBP_LEDGER_DIR:-$(mktemp -d)}
sha256sum --quiet -c data/CHECKSUMS.sha256
for d in data/runs/*/; do
  d=${d%/}; case "$(basename "$d")" in pooled_*) continue;; esac
  [ -s "$d/landed.csv" ] || continue
  $PY -m obp analyze --run-dir "$d" >/dev/null
done
bash scripts/pool_sessions.sh pooled_parallel_all 20261025_1907_parallel 20261031_par2_parallel 20261031_par3_parallel 20261031_par4_parallel_lead6 >/dev/null
bash scripts/pool_sessions.sh pooled_parallel_followup 20261031_par2_parallel 20261031_par3_parallel 20261031_par4_parallel_lead6 >/dev/null
$PY scripts/make_figures.py figures
echo "reproduce: OK"
