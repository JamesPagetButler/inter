#!/usr/bin/env bash
#
# auto-refresh-watcher.sh — run launch-federation.sh refresh automatically once
# the freshly-launched personas sign the roster / become content-discoverable.
#
# The problem it solves: at cold-boot most personas resolve to a fresh `claude`
# because their roster rows are stale (per-dir migration, inter#58). `refresh`
# can only pin their real session ids AFTER each persona has run its session-
# start sign-on. Rather than babysit that, this watcher polls the resolved
# `list` mapping and runs `refresh` whenever a persona newly becomes resolvable.
#
# Trigger = CONTENT change in `launch-federation.sh list` (a persona flips from
# "fresh" to a real id), NOT roster mtime (an unrelated edit — e.g. a row prune —
# bumps mtime without any new sign-on).
#
# Kill conditions (pre-run-resource-estimate hard gate):
#   • MAX_POLLS hard bound (default 96 polls × 300s = 8h)
#   • auto-exit if the `fed` tmux session is gone (federation killed)
#   • exits cleanly once every persona resolves to a real id (nothing left fresh)
#
# Usage:  nohup ./auto-refresh-watcher.sh >> "$LOG" 2>&1 &
# Env:    POLL_SECS=300  MAX_POLLS=96  FED_TMUX_SESSION=fed
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCH="$HERE/launch-federation.sh"
SESSION="${FED_TMUX_SESSION:-fed}"
POLL_SECS="${POLL_SECS:-300}"
MAX_POLLS="${MAX_POLLS:-96}"
LOG="${AUTO_REFRESH_LOG:-$HOME/.federation-watcher/auto-refresh.log}"

log() { printf '%s  %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*"; }

# resolved map as "persona<TAB>id-or-FRESH" lines, sorted — the content signal.
snapshot() {
  "$LAUNCH" list 2>/dev/null | awk 'NR>2 {
    persona=$1; id=$3;
    if (id=="" || id=="—") id="FRESH";
    print persona"\t"id
  }' | sort
}
fresh_count() { snapshot | grep -c $'\tFRESH$'; }

log "auto-refresh-watcher START (poll=${POLL_SECS}s max=${MAX_POLLS} session=${SESSION})"
prev="$(snapshot)"
start_fresh="$(printf '%s\n' "$prev" | grep -c $'\tFRESH$')"
log "baseline: ${start_fresh} persona(s) still fresh (awaiting sign-on)"

i=0
while [ "$i" -lt "$MAX_POLLS" ]; do
  i=$((i+1))
  sleep "$POLL_SECS"

  # federation gone → nothing to refresh, stop.
  if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    log "tmux session '$SESSION' gone — stopping watcher."; exit 0
  fi

  cur="$(snapshot)"
  if [ "$cur" != "$prev" ]; then
    newly="$(comm -13 <(printf '%s\n' "$prev") <(printf '%s\n' "$cur") | grep -v $'\tFRESH$' | cut -f1 | paste -sd, -)"
    log "poll $i/${MAX_POLLS}: resolution changed — running refresh (newly resolvable: ${newly:-none-net})"
    "$LAUNCH" refresh >/dev/null 2>&1 && log "  ✓ refresh applied" || log "  ✗ refresh failed"
    prev="$(snapshot)"
  fi

  fc="$(fresh_count)"
  if [ "$fc" -eq 0 ]; then
    log "poll $i/${MAX_POLLS}: 0 personas fresh — all pinned. Watcher done."; exit 0
  fi
done
log "reached MAX_POLLS=${MAX_POLLS} — stopping (still $(fresh_count) fresh; re-launch watcher or run refresh manually if they sign on later)."
