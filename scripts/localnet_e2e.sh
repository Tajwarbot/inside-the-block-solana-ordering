#!/usr/bin/env bash
# Run the full pipeline against a throwaway solana-test-validator.
# Required: RPC_URL (e.g. http://127.0.0.1:18899) and OBP_KEYPAIRS pointing at funded localnet keys.
# This script refuses to send unless the genesis hash is an unknown/local cluster.
set -euo pipefail
cd "$(dirname "$0")/.."

: "${RPC_URL:?set RPC_URL to the running solana-test-validator}"
: "${OBP_KEYPAIRS:?set OBP_KEYPAIRS to one or more funded localnet keypair paths}"
PYTHON="${PYTHON:-.venv/bin/python}"
export OBP_DATA="${OBP_DATA:-data/localnet_e2e}"

cluster="$("$PYTHON" - <<'PY'
from obp.rpc import Rpc
print(Rpc().cluster())
PY
)"
case "$cluster" in
  mainnet|devnet|testnet)
    echo "ABORT: RPC_URL points at $cluster, not a local test validator" >&2
    exit 2
    ;;
esac
echo "localnet cluster check ok ($cluster); data -> $OBP_DATA"

"$PYTHON" -m obp inventory
"$PYTHON" -m obp plan --min-labels 1 --horizon 400 --windows 9 --min-lead-slots 25 --min-gap-slots 12
"$PYTHON" -m obp run --live --max-bursts 3

"$PYTHON" - "$OBP_DATA" <<'PY'
import csv, os, sys

with open(os.path.join(sys.argv[1], "sent.csv"), newline="") as f:
    sent = list(csv.DictReader(f))
live_ok = [r for r in sent if r.get("live") == "True" and r.get("send_result") == "ok"]
if not live_ok:
    sys.exit("FAIL: sent.csv has no live rows with send_result=ok")
print(f"sent.csv: {len(live_ok)} live sends ok")
PY

"$PYTHON" -m obp collect
"$PYTHON" -m obp verify-windows
"$PYTHON" -m obp analyze

"$PYTHON" - "$OBP_DATA" <<'PY'
import csv, os, sys

with open(os.path.join(sys.argv[1], "landed.csv"), newline="") as f:
    landed = list(csv.DictReader(f))
count = sum(1 for r in landed if str(r.get("landed")).lower() == "true")
if count == 0:
    sys.exit("FAIL: collect landed 0 txs")
print(f"landed.csv: {count} landed txs")
PY
