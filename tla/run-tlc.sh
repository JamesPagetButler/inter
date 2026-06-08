#!/bin/bash
# run-tlc.sh — safe TLC launcher with pre-run resource check
#
# Usage:
#   ./run-tlc.sh -config <cfg> [-mode simulate|bfs|dfid] [-depth N]
#                [-traces N] [-workers N] [-force] <spec.tla>
#
# Defaults: simulate, depth=20, traces=100000, workers=4
# Never runs unbounded BFS without --force flag.

set -euo pipefail

TLA2TOOLS="${TLA2TOOLS:-$HOME/.local/lib/tla2tools.jar}"
DISK_WARN_PCT=50        # warn if estimate exceeds this % of free disk
DISK_BLOCK_PCT=80       # refuse if estimate exceeds this % of free disk

# ── Defaults ──────────────────────────────────────────────────────────────────
MODE="simulate"
DEPTH=20
TRACES=100000
WORKERS=4
CONFIG=""
SPEC=""
FORCE=0

usage() {
  echo "Usage: $0 -config <cfg> [options] <spec.tla>"
  echo "  -mode simulate|bfs|dfid  (default: simulate)"
  echo "  -depth N                 (default: 20)"
  echo "  -traces N                (default: 100000, simulate only)"
  echo "  -workers N               (default: 4)"
  echo "  -force                   skip resource block (still warns)"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -config)   CONFIG="$2";  shift 2 ;;
    -mode)     MODE="$2";    shift 2 ;;
    -depth)    DEPTH="$2";   shift 2 ;;
    -traces)   TRACES="$2";  shift 2 ;;
    -workers)  WORKERS="$2"; shift 2 ;;
    -force)    FORCE=1;      shift   ;;
    -*)        echo "Unknown option: $1"; usage ;;
    *)         SPEC="$1";    shift   ;;
  esac
done

[[ -z "$SPEC" || -z "$CONFIG" ]] && usage

# ── Mode validation ────────────────────────────────────────────────────────────
if [[ "$MODE" == "bfs" && "$FORCE" -eq 0 ]]; then
  echo "ERROR: unbounded BFS requires -force flag."
  echo "  BFS disk usage scales with total distinct states × ~150 bytes/state."
  echo "  Estimate first or use -mode simulate / -mode dfid instead."
  exit 1
fi

# ── Disk headroom check ────────────────────────────────────────────────────────
FREE_KB=$(df -k . | awk 'NR==2 {print $4}')
FREE_GB=$(echo "scale=1; $FREE_KB / 1048576" | bc)

# Rough estimates per mode
case "$MODE" in
  simulate) EST_GB="0.01" ;; # simulation: ~10MB for checkpoint files
  dfid)     EST_GB="1.0"  ;; # dfid: stack-based, ~1GB for deep specs
  bfs)      EST_GB="???"  ;; # unbounded: unknown; user must estimate
esac

echo "═══════════════════════════════════════════════════"
echo "  TLC resource pre-check"
echo "  Spec:    $SPEC"
echo "  Config:  $CONFIG"
echo "  Mode:    $MODE  depth=$DEPTH  workers=$WORKERS"
[[ "$MODE" == "simulate" ]] && echo "  Traces:  $TRACES"
echo "  Free disk: ${FREE_GB} GB"
echo "  Estimated disk: ~${EST_GB} GB"
echo "═══════════════════════════════════════════════════"

if [[ "$MODE" == "bfs" ]]; then
  echo "WARNING: unbounded BFS — disk usage is unbounded."
  echo "  You must estimate state space size × 150 bytes/state manually."
  echo "  Proceeding because -force was passed."
else
  # Check estimate against free disk
  WARN_THRESHOLD=$(echo "scale=2; $FREE_GB * $DISK_WARN_PCT / 100" | bc)
  BLOCK_THRESHOLD=$(echo "scale=2; $FREE_GB * $DISK_BLOCK_PCT / 100" | bc)
  EXCEEDS_BLOCK=$(echo "$EST_GB > $BLOCK_THRESHOLD" | bc -l 2>/dev/null || echo 0)
  if [[ "$EXCEEDS_BLOCK" -eq 1 && "$FORCE" -eq 0 ]]; then
    echo "ERROR: estimated disk usage (${EST_GB} GB) exceeds ${DISK_BLOCK_PCT}% of"
    echo "  free disk (${FREE_GB} GB). Add -force to override."
    exit 1
  fi
fi

echo ""

# ── Build TLC command ──────────────────────────────────────────────────────────
CMD="java -XX:+UseParallelGC -cp $TLA2TOOLS tlc2.TLC"
CMD+=" -deadlock -workers $WORKERS"
CMD+=" -config $CONFIG"

case "$MODE" in
  simulate)
    CMD+=" -simulate num=$TRACES -depth $DEPTH"
    ;;
  dfid)
    CMD+=" -dfid $DEPTH"
    ;;
  bfs)
    # No depth flag — truly unbounded. User accepted this with -force.
    ;;
esac

CMD+=" $SPEC"

echo "Launching: $CMD"
echo ""
exec $CMD
