#!/usr/bin/env bash
# Federation per-seat wake waiter — the churn-free replacement for the Monitor tool.
#
# WHY: the Monitor tool caps at 30 min, so a quiet seat burns a model turn every
# 30 min just to re-arm (the re-arm churn). This is a Bash `run_in_background`
# one-shot: background tasks have NO cap and re-invoke the session only when they
# EXIT — so this blocks on the seat's wake file and exits only on a real new WAKE
# line. Zero timer-driven wakes. (Architect's mechanism, live-test seq 2453,
# hardened here for the three defects they flagged.)
#
# USAGE:  bash wake-wait.sh <seat>        # invoke via Bash run_in_background
#   On a new wake line it prints the new line(s) and exits (re-invoking the
#   session). The session reads them, handles the mention, then re-arms.
#
# DEFECTS FIXED vs the raw version:
#   #1 no-skip  — resumes from a persisted offset (state/<seat>.offset), advanced
#                 only after the lines are emitted, so a mention that lands during
#                 handling is caught by the next waiter instead of being skipped.
#   #2 singleton — a pidfile (state/<seat>.waiter.pid); a second arm exits at once.
#   #3 session-death — a bg task survives turns, NOT a session restart. Still a
#                 single point of failure → needs inter#91 liveness (the watcher
#                 verifies a live waiter per active seat). Documented, not solved here.
set -euo pipefail
seat="${1:?usage: wake-wait.sh <seat>}"
WDIR="${FED_WATCH_DIR:-$HOME/.federation-watcher}"
F="$WDIR/wake/$seat"
STATE="$WDIR/state"; mkdir -p "$STATE"
OFF="$STATE/$seat.offset"
PID="$STATE/$seat.waiter.pid"
SETTLE="${FED_WAKE_SETTLE:-1}"   # let a multi-line burst finish writing
POLL="${FED_WAKE_POLL:-10}"      # fallback poll interval when inotify absent

# --- #2 singleton: if a live waiter already watches this seat, exit now ---
if [ -f "$PID" ] && kill -0 "$(cat "$PID" 2>/dev/null)" 2>/dev/null; then
  echo "wake-wait[$seat]: live waiter pid $(cat "$PID") already running — exiting"; exit 0
fi
echo $$ > "$PID"
trap 'rm -f "$PID"' EXIT

[ -f "$F" ] || : > "$F"
# --- #1 no-skip: start from the persisted offset, not the current EOF ---
n=$(cat "$OFF" 2>/dev/null || echo 0)
case "$n" in ''|*[!0-9]*) n=0 ;; esac
cur=$(wc -l < "$F")
[ "$n" -gt "$cur" ] && n=0        # file rotated/truncated → reset

have_inotify=0; command -v inotifywait >/dev/null 2>&1 && have_inotify=1
while :; do
  cur=$(wc -l < "$F")
  if [ "$cur" -gt "$n" ]; then
    sleep "$SETTLE"
    cur=$(wc -l < "$F")
    sed -n "$((n+1)),${cur}p" "$F"
    echo "$cur" > "$OFF"          # advance ONLY after emitting (#1)
    exit 0
  fi
  if [ "$have_inotify" = 1 ]; then
    timeout "$POLL" inotifywait -qq -e modify,create "$F" >/dev/null 2>&1 || true
  else
    sleep "$POLL"
  fi
done
