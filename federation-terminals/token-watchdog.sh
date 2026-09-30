#!/usr/bin/env bash
#
# token-watchdog.sh — detect a federation-wide token/usage-limit stall and
# auto-recover once the limit resets.
#
# WHY THIS IS PURE BASH (no claude): when the account hits its usage limit,
# EVERY claude session stalls at once — including deming, the orchestrator. So
# the rescuer cannot itself consume tokens. This daemon uses only bash + tmux,
# runs as a systemd --user service (like the federation-watcher), and therefore
# keeps working through a total token blackout. On each cycle while a pane shows
# a limit signature it sends a resume nudge; before the limit resets the nudge
# is harmless, and the FIRST nudge after reset succeeds — self-correcting, no
# need to parse the exact reset time.
#
# Install (proposed): copy to ~/Documents/inter/federation-terminals/, then a
# systemd --user unit with Restart=always + `loginctl enable-linger $USER`.
#
# Env: FED_TMUX_SESSION=fed  WATCHDOG_INTERVAL=600  TOKEN_SIG='...'
set -uo pipefail

SESSION="${FED_TMUX_SESSION:-fed}"
INTERVAL="${WATCHDOG_INTERVAL:-600}"          # seconds between scans (10 min)
LOG="${TOKEN_WATCHDOG_LOG:-$HOME/.federation-watcher/token-watchdog.log}"

# Exact Claude Code usage-limit banners (confirmed via claude-code-guide research,
# 2026). The middle bullet is U+00B7. "Server is temporarily..." is server-side
# throttling (also a stall worth nudging). Limit is ACCOUNT-WIDE → all sessions
# stall together, which is why this rescuer is tokenless.
SIG="${TOKEN_SIG:-hit your (session|weekly|Opus) limit|Server is temporarily limiting requests}"

log(){ printf '%s %s\n' "$(date -Is)" "$*" >> "$LOG"; }
mkdir -p "$(dirname "$LOG")"
log "token-watchdog START (session=$SESSION interval=${INTERVAL}s)"

stalled=0
while true; do
  sleep "$INTERVAL"
  tmux has-session -t "$SESSION" 2>/dev/null || { log "no '$SESSION' tmux session — idle"; continue; }

  hits=""
  for p in $(tmux list-panes -t "$SESSION" -F '#{pane_id}' 2>/dev/null); do
    # current screen only (not scrollback) so a RESUMED pane's new output no
    # longer matches the old limit banner.
    if tmux capture-pane -p -t "$p" 2>/dev/null | grep -qiE "$SIG"; then
      hits="$hits $p"
    fi
  done

  if [ -n "$hits" ]; then
    if [ "$stalled" -eq 0 ]; then
      # surface the reset time from the banner (rolling window, per-account)
      rt=$(for p in $hits; do tmux capture-pane -p -t "$p" 2>/dev/null | grep -oP "resets \K[^·\n]+"; done | head -1)
      log "STALL DETECTED — token-limit signature on panes:$hits ${rt:+(banner: resets $rt)}"
    fi
    stalled=1
    for p in $hits; do
      tmux send-keys -t "$p" C-u 2>/dev/null            # clear any half-typed input
      tmux send-keys -t "$p" -l "resume: your Claude usage limit appears to have reset — continue your Sprint-3 wave work, and poll_inbox for any @mentions you missed while stalled."
      sleep 0.3
      tmux send-keys -t "$p" Enter
    done
    log "recovery nudge sent to:$hits (no-op until the limit resets, then it takes)"
  else
    [ "$stalled" -eq 1 ] && log "RECOVERED — no limit signature on any pane; federation active again"
    stalled=0
  fi
done
