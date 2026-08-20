#!/usr/bin/env bash
#
# launch-federation.sh — cold-boot the federation persona sessions in tmux.
#
# Builds a tmux session with one pane (or window) per persona from personas.conf,
# each cd'd to that persona's workdir and resuming its specific claude session
# (claude --resume <id>). Ensures the federation-watcher daemon is up first, so a
# post-crash restart is a single command. Because it's tmux, closing the terminal
# no longer kills the sessions — just `tmux attach -t fed` to get back in.
#
# Usage:
#     ./launch-federation.sh                 # build + attach (panes, tiled)
#     ./launch-federation.sh launch          # same
#     ./launch-federation.sh list            # show resolved mapping, build nothing
#     ./launch-federation.sh refresh         # re-derive session ids by handle, rewrite conf (.bak kept)
#     ./launch-federation.sh kill            # kill the tmux session
#     ./launch-federation.sh help
#
# Env:
#     LAYOUT=windows               # one tmux window per persona instead of tiled panes (default: panes)
#     FED_TMUX_SESSION=fed         # tmux session name (default: fed)
#     FED_TERMINALS_CONF=/path     # override config location
#
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="${FED_TERMINALS_CONF:-$HERE/personas.conf}"
PROJECTS="$HOME/.claude/projects"
CLAUDE_BIN="$(command -v claude || echo "$HOME/.local/bin/claude")"
WATCHER_DIR="$HOME/Documents/inter/federation-watcher"
SESSION="${FED_TMUX_SESSION:-fed}"
LAYOUT="${LAYOUT:-panes}"          # panes | windows
MODE="${1:-launch}"

die() { echo "ERROR: $*" >&2; exit 1; }

[ -f "$CONF" ] || die "config not found: $CONF"
command -v tmux >/dev/null || die "tmux not installed"

# path -> claude project-history slug  (/home/prime/Documents -> -home-prime-Documents)
slug_of() { printf '%s' "$1" | sed 's#/#-#g'; }

ROSTER="$HOME/.federation-watcher/session-roster.tsv"

# authoritative: persona -> session_id from the sign-on roster (self-reported).
# Workdir-matched: a roster row only counts if its workdir matches the launch
# workdir. This is what makes per-dir migration (inter#58) safe — a persona whose
# conf workdir moved to ~/Documents/<Repo> will NOT match its stale ~/Documents
# roster row, so AUTO falls through to content-sniff in the new dir (fresh on the
# first launch there, self-healing once it signs the roster from the new cwd)
# instead of resuming a wrong-dir session. Roster stores ~ form; caller passes the
# tilde-expanded path — normalize the roster's ~ to $HOME before comparing.
roster_sid() {
  local persona="$1" workdir="$2"
  [ -f "$ROSTER" ] || { printf ''; return; }
  awk -v p="$persona" -v wd="$workdir" -v home="$HOME" -F'\t' '
    $1==p { rwd=$2; sub(/^~/, home, rwd); if (rwd==wd) { print $3; exit } }
  ' "$ROSTER"
}

# Known federation persona handles — the content-sniff dominance check ranks
# against these. Keep in sync with the persona rows below.
FED_HANDLES='qbp-architecture|qbp-implementor|qbp-oppenheimer|qbp-cu-implementor|cth-implementor|wyrd-implementor|bma-implementor|contextus-impl|herschel|notary-implementor|edda-implementor|deming'

# AUTO resolution order: roster (authoritative, workdir-matched) -> content sniff.
# Content sniff = newest *.jsonl in the project dir where THIS persona is the
# DOMINANT handle (more mentions than any other federation handle). Dominance —
# not mere mention — is what makes it safe: a sibling's transcript that merely
# discusses this persona (e.g. oppenheimer's session mentioning qbp-implementor)
# is no longer mis-resolved as this persona's own session. Returns '' (→ fresh
# claude) when no jsonl is dominated by this persona — the correct outcome for a
# freshly-migrated dir whose only history belongs to a persona moving out.
discover_sid() {
  local persona="$1" workdir="$2"
  local sid; sid="$(roster_sid "$persona" "$workdir")"
  [ -n "$sid" ] && { printf '%s' "$sid"; return; }
  local pdir="$PROJECTS/$(slug_of "$workdir")"
  [ -d "$pdir" ] || { printf ''; return; }
  local f top
  # ls -t ...*.jsonl 2>/dev/null: if no jsonl matches, the glob stays literal,
  # ls errors to /dev/null and emits nothing, so the loop simply never runs —
  # no empty-pipe-into-ls-cwd footgun.
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    top="$(grep -aoE "$FED_HANDLES" "$f" 2>/dev/null | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')"
    [ "$top" = "$persona" ] && { basename "$f" .jsonl; return; }
  done < <(ls -t "$pdir"/*.jsonl 2>/dev/null)
  printf ''
}

declare -a P_PERSONA P_WORKDIR P_SID
load_conf() {
  while IFS= read -r line; do
    line="${line%%#*}"
    [[ "$line" =~ ^[[:space:]]*$ ]] && continue
    IFS='|' read -r persona workdir sid <<<"$line"
    persona="$(echo "$persona" | xargs)"
    workdir="$(echo "$workdir" | xargs)"
    sid="$(echo "$sid" | xargs)"
    workdir="${workdir/#\~/$HOME}"
    [ -z "$persona" ] && continue
    if [ "$sid" = "AUTO" ] || [ -z "$sid" ]; then
      sid="$(discover_sid "$persona" "$workdir")"
    fi
    P_PERSONA+=("$persona"); P_WORKDIR+=("$workdir"); P_SID+=("$sid")
  done < "$CONF"
}

ensure_watcher() {
  if pgrep -f "watcher.py" >/dev/null 2>&1; then
    echo "✓ federation-watcher already running (pid $(pgrep -f watcher.py | head -1))"
  elif [ -f "$WATCHER_DIR/watcher.py" ]; then
    ( cd "$WATCHER_DIR" && nohup python3 watcher.py >> "$HOME/.federation-watcher/watcher.log" 2>&1 & )
    sleep 2
    pgrep -f watcher.py >/dev/null \
      && echo "✓ federation-watcher started (pid $(pgrep -f watcher.py | head -1))" \
      || echo "✗ federation-watcher failed — check $HOME/.federation-watcher/watcher.log"
  else
    echo "… watcher.py not found at $WATCHER_DIR — skipping daemon start"
  fi
}

# the command typed into each pane/window
resume_cmd() {
  local sid="$1"
  # With a resolved id: resume it in place. Without one (e.g. a just-migrated
  # persona's first launch in a fresh dir): plain `claude` — a new session.
  # `--continue` is wrong here: it errors when the cwd has no prior conversation.
  if [ -n "$sid" ]; then echo "$CLAUDE_BIN --resume $sid"
  else echo "$CLAUDE_BIN"; fi
}

cmd_list() {
  load_conf
  printf '%-20s %-22s %s\n' "PERSONA" "WORKDIR" "SESSION-ID (resolved)"
  printf '%-20s %-22s %s\n' "-------" "-------" "---------------------"
  local i
  for i in "${!P_PERSONA[@]}"; do
    local sid="${P_SID[$i]}" note=""
    if [ -z "$sid" ]; then note="  (none found → fresh 'claude')"
    elif [ ! -f "$PROJECTS/$(slug_of "${P_WORKDIR[$i]}")/$sid.jsonl" ]; then note="  (!! session file missing)"; fi
    printf '%-20s %-22s %s%s\n' "${P_PERSONA[$i]}" "${P_WORKDIR[$i]/#$HOME/\~}" "${sid:-—}" "$note"
  done
}

cmd_refresh() {
  cp "$CONF" "$CONF.bak" 2>/dev/null
  local tmp; tmp="$(mktemp)"
  while IFS= read -r line; do
    local raw="$line"; line="${line%%#*}"
    [[ "$line" =~ ^[[:space:]]*$ ]] && { echo "$raw" >> "$tmp"; continue; }
    IFS='|' read -r persona workdir sid <<<"$line"
    persona="$(echo "$persona" | xargs)"; workdir="$(echo "$workdir" | xargs)"
    local wd="${workdir/#\~/$HOME}" newsid
    newsid="$(discover_sid "$persona" "$wd")"
    [ -z "$newsid" ] && newsid="$(echo "$sid" | xargs)"
    printf '%-20s | %-18s | %s\n' "$persona" "$workdir" "$newsid" >> "$tmp"
  done < "$CONF"
  mv "$tmp" "$CONF"
  echo "✓ refreshed $CONF (backup at $CONF.bak)"; cmd_list
}

cmd_kill() {
  tmux has-session -t "$SESSION" 2>/dev/null \
    && { tmux kill-session -t "$SESSION"; echo "✓ killed tmux session '$SESSION'"; } \
    || echo "no tmux session '$SESSION'"
}

cmd_launch() {
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "tmux session '$SESSION' already exists — attaching (use 'kill' to rebuild)."
    [ -n "${TMUX:-}" ] && exec tmux switch-client -t "$SESSION" || exec tmux attach -t "$SESSION"
  fi

  ensure_watcher
  load_conf
  [ "${#P_PERSONA[@]}" -gt 0 ] || die "no personas in $CONF"

  local i first=1
  local -a FRESH=()
  for i in "${!P_PERSONA[@]}"; do
    local persona="${P_PERSONA[$i]}" wd="${P_WORKDIR[$i]}" sid="${P_SID[$i]}"
    if [ -n "$sid" ] && [ ! -f "$PROJECTS/$(slug_of "$wd")/$sid.jsonl" ]; then
      echo "⚠  $persona: session $sid not found — pane falls back to fresh 'claude'"
      sid=""
    fi
    # fresh panes (no resumable session) get auto-onboarded below
    [ -z "$sid" ] && FRESH+=("$persona")
    local run; run="$(resume_cmd "$sid")"

    if [ "$LAYOUT" = "windows" ]; then
      if [ $first -eq 1 ]; then tmux new-session -d -s "$SESSION" -n "$persona" -c "$wd"
      else tmux new-window -t "$SESSION" -n "$persona" -c "$wd"; fi
      tmux send-keys -t "$SESSION:$persona" "$run" C-m
    else
      if [ $first -eq 1 ]; then
        tmux new-session -d -s "$SESSION" -n federation -c "$wd"
      else
        tmux split-window -t "$SESSION" -c "$wd"
        tmux select-layout -t "$SESSION" tiled >/dev/null
      fi
      tmux select-pane -t "$SESSION" -T "$persona" 2>/dev/null
      tmux send-keys -t "$SESSION" "$run" C-m
    fi
    echo "→ $persona  ($wd)  ${sid:-[fresh claude]}"
    first=0
  done

  if [ "$LAYOUT" != "windows" ]; then
    tmux select-layout -t "$SESSION" tiled >/dev/null
    tmux set -t "$SESSION" pane-border-status top 2>/dev/null
    tmux set -t "$SESSION" pane-border-format " #T " 2>/dev/null
  fi
  echo "✓ built tmux session '$SESSION' (${LAYOUT})."

  # auto-onboard fresh panes (federation-optimization #6): ground → register →
  # subscribe → arm §2.i Monitor → re-anchor, so each comes up fully operational
  # and responsive on chat instead of as a blank claude. Resumed panes keep their
  # own context and are skipped (only FRESH handles are passed). Gate: ONBOARD=1
  # (default). Relies on pre-trusted dirs + sessionbridge/Monitor allowlist (#1/#2)
  # so the boot-protocol tool calls run without approval stalls.
  if [ "${ONBOARD:-1}" = "1" ] && [ "${#FRESH[@]}" -gt 0 ] && [ -x "$HERE/onboard-federation.sh" ]; then
    echo "  Auto-onboarding ${#FRESH[@]} fresh pane(s): ${FRESH[*]}"
    "$HERE/onboard-federation.sh" "${FRESH[@]}" || echo "  ⚠ onboard pass reported issues (see above)"
  else
    echo "  Each persona re-arms its own §2.i Monitor on session start (federation-watcher boot protocol)."
  fi

  if [ -t 1 ]; then
    [ -n "${TMUX:-}" ] && exec tmux switch-client -t "$SESSION" || exec tmux attach -t "$SESSION"
  else
    echo "  Not a TTY — attach with:  tmux attach -t $SESSION"
  fi
}

case "$MODE" in
  launch|"") cmd_launch ;;
  list)      cmd_list ;;
  refresh)   cmd_refresh ;;
  kill)      cmd_kill ;;
  help|-h|--help) sed -n '2,33p' "$0" | sed 's/^# \{0,1\}//' ;;
  *) die "unknown mode: $MODE (try: launch | list | refresh | kill | help)" ;;
esac
