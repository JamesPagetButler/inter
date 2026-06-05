#!/usr/bin/env bash
#
# selftest.sh <persona> — federation-watcher MONITOR liveness check.
#
# The daemon now self-heals (systemd), but the per-session Monitor
# (tail -f -n 0 ~/.federation-watcher/wake/<persona>) dies SILENTLY with the
# session or a host crash — and there is no other signal that it died. You only
# notice when you realize you've been missing @mentions. (edda-implementor missed
# the roster directive + the whole survey this way, 2026-06-04.)
#
# This appends a SELFTEST marker to your wake file. If your Monitor is ALIVE you
# will receive a wake event containing the nonce within a few seconds. If you do
# NOT, your Monitor is dead — re-arm it.
#
# Wake files are append-only, so adding a marker alongside the daemon's writes is
# race-safe (single atomic line append, not a rewrite).
#
# SESSION-START PROTOCOL:
#   1. systemctl --user is-active federation-watcher   # daemon up?
#   2. Monitor(tail -f -n 0 ~/.federation-watcher/wake/<persona>, persistent=True)
#   3. selftest.sh <persona>  →  confirm the SELFTEST wake arrives. If not, re-arm.
#
set -uo pipefail

PERSONA="${1:?usage: selftest.sh <persona>}"
WAKE="$HOME/.federation-watcher/wake/$PERSONA"

mkdir -p "$(dirname "$WAKE")"
nonce="LIVE-$(date +%s)-$$"
ts="$(date -Iseconds 2>/dev/null || date)"

printf 'SELFTEST %s %s — monitor liveness check; if your Monitor delivered this line, it is ALIVE\n' \
  "$nonce" "$ts" >> "$WAKE"

echo "✓ selftest marker written to $WAKE"
echo "  nonce: $nonce"
echo
echo "→ Within ~5s you should receive a wake event containing: $nonce"
echo "  • Arrived  → Monitor is ALIVE."
echo "  • Silence  → Monitor is DEAD. Re-arm it:"
echo "      Monitor(command=\"tail -f -n 0 $WAKE\", persistent=True)"
