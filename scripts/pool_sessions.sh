# usage: scripts/pool_sessions.sh OUTNAME run1 run2 ...
cd "$(dirname "$0")/.."
OUT=data/runs/$1; shift; mkdir -p $OUT
for f in landed sent blocks windows; do
  first=1; : > $OUT/$f.csv
  for r in "$@"; do
    [ -f data/runs/$r/$f.csv ] || continue
    if [ $first = 1 ]; then cat data/runs/$r/$f.csv >> $OUT/$f.csv; first=0; else tail -n +2 data/runs/$r/$f.csv >> $OUT/$f.csv; fi
  done
done
echo "$@" > $OUT/SOURCES.txt
OBP_LEDGER_DIR=data .venv/bin/python -m obp analyze --run-dir $OUT
