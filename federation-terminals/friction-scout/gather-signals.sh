#!/usr/bin/env bash
#
# gather-signals.sh — tokenless bash sweep that collects the raw signal blob
# the friction-scout's Haiku triage call reasons over (inter#83).
#
# Deliberately does ZERO judgment here — every "is this actually friction"
# call belongs to the Haiku triage step (scout-prompt.md), because that's the
# distinction a regex reliably gets wrong (see scout-prompt.md's
# false-positive classes). This script only does the things that ARE safe to
# decide deterministically in bash:
#   - daemon liveness via `systemctl --user is-active` (NOT log recency —
#     token-watchdog only logs on a stall, so log silence is healthy, not
#     stale; this is a bash-level decision, not something we hand to Haiku)
#   - resource threshold comparison (load/RAM/disk vs a numeric threshold)
#   - stripping the token/usage-limit banner lines from pane captures, so the
#     scout never re-flags what token-watchdog.sh already owns (no
#     double-alarm — the concern the inter#83 reader-list named)
#
# Everything else (is this pane really stuck vs. a correct gated-hold; is
# this channel message a substantive ask) is left as raw text for the model.
#
# Output: a single text blob to stdout, four sections (PANES / CHANNEL /
# RESOURCE / DAEMONS), designed to be appended directly under scout-prompt.md's
# "## SIGNALS" heading.
#
# Env overrides:
#   FED_TMUX_SESSION=fed              tmux session to sweep panes of
#   SCOUT_CHANNEL=live-test           sessionbridge channel to sweep
#   SCOUT_STATE_DIR=~/.federation-watcher/friction-scout   cursor state
#   SCOUT_PANE_LINES=40               tail lines captured per pane
#   SCOUT_CHANNEL_MAX=30              max new channel messages shown per run
#   SCOUT_LOAD_WARN_RATIO=1.5         1m-load / nproc warn threshold
#   SCOUT_RAM_WARN_PCT=90             RAM used% warn threshold
#   SCOUT_DISK_WARN_PCT=90            disk used% warn threshold (on $HOME)
#   SCOUT_DAEMONS="token-watchdog.service federation-watcher.service"
#
set -uo pipefail

SESSION="${FED_TMUX_SESSION:-fed}"
CHANNEL="${SCOUT_CHANNEL:-live-test}"
STATE_DIR="${SCOUT_STATE_DIR:-$HOME/.federation-watcher/friction-scout}"
PANE_LINES="${SCOUT_PANE_LINES:-40}"
CHANNEL_MAX="${SCOUT_CHANNEL_MAX:-30}"
LOAD_WARN_RATIO="${SCOUT_LOAD_WARN_RATIO:-1.5}"
RAM_WARN_PCT="${SCOUT_RAM_WARN_PCT:-90}"
DISK_WARN_PCT="${SCOUT_DISK_WARN_PCT:-90}"
DAEMONS="${SCOUT_DAEMONS:-token-watchdog.service federation-watcher.service}"
CHANNELS_DIR="$HOME/.claude/mcp-servers/sessionbridge/state/channels"

mkdir -p "$STATE_DIR"

# token/usage-limit banner signature — kept identical to token-watchdog.sh's
# SIG so we strip exactly what it already owns. If that daemon's signature
# changes, update both in the same PR (documented drift risk).
TOKEN_SIG='hit your (session|weekly|Opus) limit|Server is temporarily limiting requests'

echo "### PANES (session=$SESSION, tail=${PANE_LINES}L, token-limit banner lines stripped — token-watchdog's domain)"
if tmux has-session -t "$SESSION" 2>/dev/null; then
  panes="$(tmux list-panes -t "$SESSION" -F '#{pane_id} #{pane_title}' 2>/dev/null)"
  pane_count=0
  if [ -n "$panes" ]; then
    while IFS= read -r line; do
      pid="${line%% *}"
      title="${line#* }"
      pane_count=$((pane_count + 1))
      echo "--- pane $pid ($title) ---"
      tmux capture-pane -p -t "$pid" 2>/dev/null \
        | grep -viE "$TOKEN_SIG" \
        | tail -n "$PANE_LINES"
    done <<< "$panes"
  fi
  echo "--- pane_count=$pane_count ---"
else
  echo "(no '$SESSION' tmux session found — federation not launched, or scout running off-host)"
fi

echo
echo "### CHANNEL ($CHANNEL, since last scout cursor)"
LAST_SEQ_FILE="$STATE_DIR/last_seq_${CHANNEL}"
last_seq=0
[ -f "$LAST_SEQ_FILE" ] && last_seq="$(cat "$LAST_SEQ_FILE" 2>/dev/null || echo 0)"
case "$last_seq" in ''|*[!0-9]*) last_seq=0 ;; esac

chan_file="$CHANNELS_DIR/${CHANNEL}.jsonl"
max_seq="$last_seq"
new_count=0
if [ -f "$chan_file" ]; then
  new_msgs="$(python3 - "$chan_file" "$last_seq" "$CHANNEL_MAX" <<'PYEOF'
import json, sys
path, last_seq, max_n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rows = []
with open(path, errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("seq", 0) > last_seq:
            rows.append(d)
rows.sort(key=lambda d: d.get("seq", 0))
rows = rows[-max_n:]
for d in rows:
    mentions = ",".join(d.get("mentions", []))
    text = (d.get("text", "") or "").replace("\n", " ")[:400]
    print(f"seq={d.get('seq')} from={d.get('from')} mentions=[{mentions}] :: {text}")
if rows:
    print(f"__MAX_SEQ__{rows[-1].get('seq', last_seq)}")
PYEOF
)"
  if [ -n "$new_msgs" ]; then
    echo "$new_msgs" | grep '^seq='
    new_count="$(echo "$new_msgs" | grep -c '^seq=')"
    ms="$(echo "$new_msgs" | sed -n 's/^__MAX_SEQ__//p')"
    [ -n "$ms" ] && max_seq="$ms"
  else
    echo "(no new messages since seq=$last_seq)"
  fi
else
  echo "(channel file not found: $chan_file)"
fi
# advance cursor regardless of triage outcome — a message only needs to be
# shown to the scout once; re-triaging the same old message every cycle is
# how false-positive spam happens.
echo "$max_seq" > "$LAST_SEQ_FILE"

echo
echo "### RESOURCE"
nproc_n="$(nproc 2>/dev/null || echo 1)"
load1="$(awk '{print $1}' /proc/loadavg 2>/dev/null || echo 0)"
load_ratio="$(awk -v l="$load1" -v n="$nproc_n" 'BEGIN{ if (n<=0) n=1; printf "%.2f", l/n }')"
load_flag="OK"
awk -v r="$load_ratio" -v w="$LOAD_WARN_RATIO" 'BEGIN{exit !(r>w)}' && load_flag="WARN"
echo "load: 1m=${load1} nproc=${nproc_n} ratio=${load_ratio} threshold=${LOAD_WARN_RATIO} flag=${load_flag}"

ram_line="$(free -m | awk '/^Mem:/{printf "%d %d", $3, $2}')"
ram_used="${ram_line% *}"
ram_total="${ram_line#* }"
ram_pct="$(awk -v u="$ram_used" -v t="$ram_total" 'BEGIN{ if (t<=0) t=1; printf "%.0f", (u/t)*100 }')"
ram_flag="OK"
[ "$ram_pct" -ge "$RAM_WARN_PCT" ] && ram_flag="WARN"
echo "ram: used=${ram_used}MB total=${ram_total}MB pct=${ram_pct}% threshold=${RAM_WARN_PCT}% flag=${ram_flag}"

disk_pct="$(df -P "$HOME" 2>/dev/null | awk 'NR==2{gsub("%","",$5); print $5}')"
disk_pct="${disk_pct:-0}"
disk_flag="OK"
[ "$disk_pct" -ge "$DISK_WARN_PCT" ] && disk_flag="WARN"
echo "disk: pct=${disk_pct}% threshold=${DISK_WARN_PCT}% flag=${disk_flag} (mount of \$HOME)"

echo
echo "### DAEMONS"
for d in $DAEMONS; do
  if systemctl --user is-active --quiet "$d" 2>/dev/null; then
    echo "$d: OK"
  else
    echo "$d: DOWN"
  fi
done
