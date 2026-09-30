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
#     FED_TERMINALS_CONF=/path     # override config location (structure)
#     FED_TERMINALS_LOCAL_CONF=/path  # override overlay location (ephemeral pins, inter#142
#                                   # reissue). Default: personas.local.conf next to CONF.
#                                   # Missing/empty file = AUTO for all seats (AC7).
#     REANCHOR=1                   # send the resume re-anchor to resumed, persona-file-bound
#                                   # panes (inter#142). Default on; set 0 to disable.
#     READY_TIMEOUT=75             # seconds to wait for a resumed pane's chat prompt before
#                                   # sending its re-anchor (mirrors onboard-federation.sh)
#     FETCH_TIMEOUT=10             # seconds to allow `git fetch origin main` before failing
#                                   # loud (§I4 D2) — never resolve persona-files against a
#                                   # silently-stale origin/main ref.
#
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="${FED_TERMINALS_CONF:-$HERE/personas.conf}"
LOCAL_CONF="${FED_TERMINALS_LOCAL_CONF:-$HERE/personas.local.conf}"
PROJECTS="$HOME/.claude/projects"
CLAUDE_BIN="$(command -v claude || echo "$HOME/.local/bin/claude")"
WATCHER_DIR="$HOME/Documents/inter/federation-watcher"
INTER_REPO="${INTER_REPO_DIR:-$(cd "$HERE/.." && pwd)}"
SESSION="${FED_TMUX_SESSION:-fed}"
LAYOUT="${LAYOUT:-panes}"          # panes | windows
REANCHOR="${REANCHOR:-1}"          # send resume re-anchor to persona-file-bound resumed panes
READY_TIMEOUT="${READY_TIMEOUT:-75}"
FETCH_TIMEOUT="${FETCH_TIMEOUT:-10}"
REANCHOR_TMPL="$HERE/resume-reanchor-prompt.tmpl"
MODE="${1:-launch}"

die() { echo "ERROR: $*" >&2; exit 1; }

[ -f "$CONF" ] || die "config not found: $CONF"
command -v tmux >/dev/null || die "tmux not installed"

# D2 (§I4): `git show origin/main:<path>` only reads the LOCAL remote-tracking
# ref — if nothing has fetched since the last persona-file update landed on
# main, a seat can boot an old persona while believing it read main. Runs the
# actual fetch once per process (guarded by ORIGIN_MAIN_FRESH) before the
# first resolution. On failure: FAIL LOUD and name the local ref's age —
# never silently resolve against a possibly-stale ref.
ORIGIN_MAIN_FRESH=0
ensure_origin_main_fresh() {
  [ "$ORIGIN_MAIN_FRESH" = "1" ] && return 0
  if ! command -v git >/dev/null 2>&1; then
    echo "ORIGIN/MAIN FETCH FAILED: git not available — cannot fetch origin/main of $INTER_REPO." >&2
    return 1
  fi
  local age="" last
  last="$(git -C "$INTER_REPO" log -1 --format=%ct origin/main 2>/dev/null)"
  [ -n "$last" ] && age="$(( $(date +%s) - last ))"
  local errout; errout="$(mktemp)"
  if ! timeout "$FETCH_TIMEOUT" git -C "$INTER_REPO" fetch origin main >"$errout" 2>&1; then
    local agemsg=""
    [ -n "$age" ] && agemsg=" — local origin/main ref is ${age}s old"
    echo "ORIGIN/MAIN FETCH FAILED: \`git fetch origin main\` (timeout ${FETCH_TIMEOUT}s) did not succeed for $INTER_REPO${agemsg}. Refusing to resolve persona-files against a possibly-stale ref. $(cat "$errout" 2>/dev/null)" >&2
    rm -f "$errout"
    return 1
  fi
  rm -f "$errout"
  ORIGIN_MAIN_FRESH=1
  return 0
}

# Resolve a personas.conf persona-file (4th column) against origin/main of THIS
# repo (inter#142 AC2) — never a local/worktree copy. Prints nothing on
# success; on failure prints a loud, path-naming error to stderr and returns
# non-zero. Callers MUST NOT silently fall back to generic behavior on
# failure — that silent fallback is exactly the fault mode AC2 guards against.
resolve_persona_file() {
  local path="$1" out
  if ! command -v git >/dev/null 2>&1; then
    echo "PERSONA-FILE RESOLUTION FAILED: git not available — cannot resolve '$path' from origin/main. NO silent fallback." >&2
    return 1
  fi
  ensure_origin_main_fresh || return 1
  if ! out="$(git -C "$INTER_REPO" show "origin/main:$path" 2>&1)"; then
    echo "PERSONA-FILE RESOLUTION FAILED: '$path' not found at origin/main of $INTER_REPO (git show: $out). NO silent fallback." >&2
    return 1
  fi
  return 0
}

# first pane in $SESSION whose cwd == $1 (tilde-expanded); '' if none
# (mirrors onboard-federation.sh's helper of the same name)
pane_for_cwd() {
  local want="$1" p path
  for p in $(tmux list-panes -t "$SESSION" -F '#{pane_id}' 2>/dev/null); do
    path="$(tmux display -p -t "$p" '#{pane_current_path}' 2>/dev/null)"
    [ "$path" = "$want" ] && { printf '%s' "$p"; return; }
  done
  printf ''
}

# wait until a pane shows a chat input prompt (❯) or timeout; best-effort
# (mirrors onboard-federation.sh's helper of the same name)
wait_ready() {
  local p="$1" end=$(( SECONDS + READY_TIMEOUT ))
  while [ "$SECONDS" -lt "$end" ]; do
    tmux capture-pane -p -t "$p" 2>/dev/null | grep -q '❯' && return 0
    sleep 1
  done
  return 1
}

render_reanchor() {  # $1=handle $2=workdir $3=persona_file
  sed -e "s#{{HANDLE}}#$1#g" -e "s#{{WORKDIR}}#$2#g" -e "s#{{PERSONA_FILE}}#$3#g" "$REANCHOR_TMPL" | tr -d '\n'
}

# Resume re-anchor (inter#142, AC3): a RESUMED pane whose persona-file column
# is set gets sent a short prompt telling it to re-read that file (from
# origin/main) and re-run its §0 boot protocol — this is what fixes the
# 2026-09-18 notary identity-loss fault (a resumed seat with a stale/forked
# def in context, thinking it was a qbp-architecture subagent). A resumed pane
# WITHOUT a persona-file gets nothing new (unchanged).
send_resume_reanchor() {  # $1=persona $2=workdir $3=persona_file
  local persona="$1" wd="$2" pfile="$3"
  if ! resolve_persona_file "$pfile"; then
    echo "  ⚠ $persona: persona-file resolution FAILED — skipping resume re-anchor (no silent fallback)"
    return 1
  fi
  local pane; pane="$(pane_for_cwd "$wd")"
  if [ -z "$pane" ]; then
    echo "  ⚠ $persona: no pane found for cwd $wd — skipping resume re-anchor"
    return 1
  fi
  wait_ready "$pane" || echo "  (⚠ $persona pane $pane not showing a prompt after ${READY_TIMEOUT}s — sending anyway)"
  local msg; msg="$(render_reanchor "$persona" "$wd" "$pfile")"
  tmux send-keys -t "$pane" -l "$msg"
  sleep 0.4
  tmux send-keys -t "$pane" Enter
  echo "  → resume re-anchor sent to $persona (pane $pane)"
}

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

declare -a P_PERSONA P_WORKDIR P_SID P_PFILE
declare -A OVERLAY_SID

# Overlay split (inter#142 reissue, §I4 addendum): ephemeral per-boot pins
# live in the gitignored personas.local.conf, NOT in the tracked personas.conf
# (format here: `persona | session_id`, comments/blank lines skipped). Missing
# or empty file => OVERLAY_SID stays empty => every persona falls through to
# ordinary AUTO discovery, unchanged from before the overlay existed (AC7).
load_overlay() {
  OVERLAY_SID=()
  [ -f "$LOCAL_CONF" ] || return 0
  while IFS= read -r line; do
    line="${line%%#*}"
    [[ "$line" =~ ^[[:space:]]*$ ]] && continue
    local persona sid
    IFS='|' read -r persona sid <<<"$line"
    persona="$(echo "$persona" | xargs)"
    sid="$(echo "${sid:-}" | xargs)"
    [ -z "$persona" ] && continue
    OVERLAY_SID["$persona"]="$sid"
  done < "$LOCAL_CONF"
}

load_conf() {
  load_overlay
  while IFS= read -r line; do
    line="${line%%#*}"
    [[ "$line" =~ ^[[:space:]]*$ ]] && continue
    # 4th field (persona_file, inter#142) is OPTIONAL: a 3-field row leaves
    # pfile unset, and `${pfile:-}` below treats that identically to an
    # explicit empty 4th field — this is the backward-compatibility contract.
    IFS='|' read -r persona workdir sid pfile <<<"$line"
    persona="$(echo "$persona" | xargs)"
    workdir="$(echo "$workdir" | xargs)"
    sid="$(echo "$sid" | xargs)"
    pfile="$(echo "${pfile:-}" | xargs)"
    workdir="${workdir/#\~/$HOME}"
    [ -z "$persona" ] && continue
    if [ "$sid" = "AUTO" ] || [ -z "$sid" ]; then
      # AC6: an overlay pin for this seat wins over its structural AUTO.
      if [ -n "${OVERLAY_SID[$persona]+set}" ] && [ -n "${OVERLAY_SID[$persona]}" ]; then
        sid="${OVERLAY_SID[$persona]}"
      else
        sid="$(discover_sid "$persona" "$workdir")"
      fi
    fi
    P_PERSONA+=("$persona"); P_WORKDIR+=("$workdir"); P_SID+=("$sid"); P_PFILE+=("$pfile")
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
  # Overlay split (inter#142 reissue): refresh NEVER rewrites the tracked
  # personas.conf (structure) — it writes freshly-discovered session ids to
  # the gitignored personas.local.conf overlay ONLY. This is the fix for the
  # root cause behind the dead edda 2ac20822 pin: an ephemeral discovered
  # value has no business landing in a committed file.
  load_overlay
  local -A NEW_OVERLAY
  local k
  for k in "${!OVERLAY_SID[@]}"; do NEW_OVERLAY["$k"]="${OVERLAY_SID[$k]}"; done
  while IFS= read -r line; do
    line="${line%%#*}"
    [[ "$line" =~ ^[[:space:]]*$ ]] && continue
    local persona workdir sid pfile
    IFS='|' read -r persona workdir sid pfile <<<"$line"
    persona="$(echo "$persona" | xargs)"; workdir="$(echo "$workdir" | xargs)"
    local wd="${workdir/#\~/$HOME}" newsid
    newsid="$(discover_sid "$persona" "$wd")"
    [ -n "$newsid" ] && NEW_OVERLAY["$persona"]="$newsid"
  done < "$CONF"
  [ -f "$LOCAL_CONF" ] && cp "$LOCAL_CONF" "$LOCAL_CONF.bak" 2>/dev/null
  {
    echo "# personas.local.conf — ephemeral per-boot session-id pins (inter#142 reissue overlay"
    echo "# split). Gitignored; NOT tracked in git. Format: persona | session_id. Written by"
    echo "# 'launch-federation.sh refresh'; layered on top of personas.conf's structural AUTO"
    echo "# at load time (an overlay pin wins over AUTO — AC6). Missing/empty file = AUTO for"
    echo "# every seat, unchanged backward-compatible behavior (AC7)."
    local p
    for p in "${!NEW_OVERLAY[@]}"; do
      printf '%-20s | %s\n' "$p" "${NEW_OVERLAY[$p]}"
    done
  } > "$LOCAL_CONF"
  echo "✓ refreshed overlay $LOCAL_CONF (personas.conf untouched — structure stays pin-free)"
  cmd_list
}

cmd_kill() {
  tmux has-session -t "$SESSION" 2>/dev/null \
    && { tmux kill-session -t "$SESSION"; echo "✓ killed tmux session '$SESSION'"; } \
    || echo "no tmux session '$SESSION'"
}

# The resume re-anchor gate (inter#142 AC3): a genuinely-RESUMED pane
# (non-empty sid) WITH a persona-file gets queued for the resume re-anchor.
# Factored out of cmd_launch's loop so tests can drive the EXACT boolean the
# real launch path uses (§I4 M2) instead of reimplementing the condition.
wants_resume_reanchor() {  # $1=sid $2=pfile
  [ -n "$1" ] && [ -n "$2" ]
}

declare -a FRESH REANCHOR_PERSONA REANCHOR_WD REANCHOR_PFILE

# Build the launch plan (which panes are FRESH vs. resumed, and which resumed
# panes get a resume re-anchor) from the already-loaded P_PERSONA/P_WORKDIR/
# P_SID/P_PFILE arrays. This IS cmd_launch's real per-pane decision logic,
# factored out so §I4's M2 mutation test can drive it directly — without
# spinning up tmux/claude — instead of reimplementing the gate in the test.
# Populates the global FRESH / REANCHOR_* arrays (reset first) and corrects
# P_SID in place when a pinned/resumed sid has no matching transcript file.
build_launch_plan() {
  FRESH=(); REANCHOR_PERSONA=(); REANCHOR_WD=(); REANCHOR_PFILE=()
  local i
  for i in "${!P_PERSONA[@]}"; do
    local persona="${P_PERSONA[$i]}" wd="${P_WORKDIR[$i]}" sid="${P_SID[$i]}" pfile="${P_PFILE[$i]}"
    if [ -n "$sid" ] && [ ! -f "$PROJECTS/$(slug_of "$wd")/$sid.jsonl" ]; then
      echo "⚠  $persona: session $sid not found — pane falls back to fresh 'claude'"
      sid=""
      P_SID[$i]="$sid"
    fi
    # fresh panes (no resumable session) get auto-onboarded below
    [ -z "$sid" ] && FRESH+=("$persona")
    wants_resume_reanchor "$sid" "$pfile" && { REANCHOR_PERSONA+=("$persona"); REANCHOR_WD+=("$wd"); REANCHOR_PFILE+=("$pfile"); }
  done
}

cmd_launch() {
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "tmux session '$SESSION' already exists — attaching (use 'kill' to rebuild)."
    [ -n "${TMUX:-}" ] && exec tmux switch-client -t "$SESSION" || exec tmux attach -t "$SESSION"
  fi

  ensure_watcher
  load_conf
  [ "${#P_PERSONA[@]}" -gt 0 ] || die "no personas in $CONF"

  build_launch_plan

  local i first=1
  for i in "${!P_PERSONA[@]}"; do
    local persona="${P_PERSONA[$i]}" wd="${P_WORKDIR[$i]}" sid="${P_SID[$i]}"
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

  # resume re-anchor (inter#142 AC3): resumed, persona-file-bound panes only —
  # tells them to re-read their canonical persona file and re-run its §0.
  # Gate: REANCHOR=1 (default). A resumed pane with no persona-file is
  # untouched by this block (REANCHOR_* arrays simply don't include it).
  if [ "$REANCHOR" = "1" ] && [ "${#REANCHOR_PERSONA[@]}" -gt 0 ]; then
    echo "  Sending resume re-anchor to ${#REANCHOR_PERSONA[@]} persona-file-bound resumed pane(s): ${REANCHOR_PERSONA[*]}"
    for i in "${!REANCHOR_PERSONA[@]}"; do
      send_resume_reanchor "${REANCHOR_PERSONA[$i]}" "${REANCHOR_WD[$i]}" "${REANCHOR_PFILE[$i]}"
    done
  fi

  if [ -t 1 ]; then
    [ -n "${TMUX:-}" ] && exec tmux switch-client -t "$SESSION" || exec tmux attach -t "$SESSION"
  else
    echo "  Not a TTY — attach with:  tmux attach -t $SESSION"
  fi
}

# Guard the dispatch so this file can be `source`d (e.g. by
# test-persona-file-loading.sh, inter#142) to unit-test its functions in
# isolation without ever running cmd_launch/cmd_refresh/cmd_kill. When run
# normally (./launch-federation.sh ...) BASH_SOURCE[0] == $0 and this is a
# no-op — behavior is unchanged.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  case "$MODE" in
    launch|"") cmd_launch ;;
    list)      cmd_list ;;
    refresh)   cmd_refresh ;;
    kill)      cmd_kill ;;
    help|-h|--help) sed -n '2,27p' "$0" | sed 's/^# \{0,1\}//' ;;
    *) die "unknown mode: $MODE (try: launch | list | refresh | kill | help)" ;;
  esac
fi
