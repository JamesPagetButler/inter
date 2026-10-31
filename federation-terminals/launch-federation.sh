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
#     FED_MODEL_MAP=/path          # override per-seat model map for TESTING
#                                   # ONLY (reads a local file, no git lookup).
#                                   # Default source is origin/main in the
#                                   # Nidavellir checkout (see model_for()
#                                   # below) — never the local working tree.
#     REANCHOR=1                   # send the resume re-anchor to resumed, persona-file-bound
#                                   # panes (inter#142). Default on; set 0 to disable.
#     READY_TIMEOUT=75             # seconds to wait for a resumed pane's chat prompt before
#                                   # sending its re-anchor (mirrors onboard-federation.sh)
#     FETCH_TIMEOUT=10             # seconds to allow `git fetch origin main` before failing
#                                   # loud (§I4 D2) — never resolve persona-files against a
#                                   # silently-stale origin/main ref.
#     STAGGER_SECONDS=4            # crash-recovery R4 (inter#92): seconds to sleep between
#                                   # successive pane launches, so ~12 `claude --resume` starts
#                                   # don't hit the API in the same second (the 429 thundering-
#                                   # herd seen 2026-08-24 and again, on contextus, 2026-09-04).
#                                   # 0 disables. Paired with CLAUDE_CODE_RETRY_WATCHDOG=1 on the
#                                   # resume path in resume_cmd() below.
#     LAUNCH_POLICY=fresh          # inter#262 (beekeeper 2026-10-30): every seat starts FRESH
#                                   # with its persona by default (plain claude + seat-map model
#                                   # + onboarding that loads persona, wisdoms, RESUME). A seat
#                                   # resumes ONLY if named in RESUME_EXCEPTIONS with a reason.
#                                   # LAUNCH_POLICY=auto = the old resume-by-default behaviour.
#     RESUME_EXCEPTIONS=/path      # named-exception list (default: resume-exceptions.conf next
#                                   # to this script; gitignored LIVE state). Format per line:
#                                   # `persona | reason`. A line with no reason is ignored.
#     QUARANTINED_SIDS_EXTRA="..." # extra session ids that may never be resumed, on top of the
#                                   # built-in quarantine list (Nidavellir#65).
#   Whatever the policy, two guards always apply: a quarantined session id is never resumed,
#   and a session whose transcript holds a structured "stop_reason":"refusal" is never
#   resumed (that seat goes FRESH and the summary says why). `plan` prints the per-seat
#   decision table without touching tmux.
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
# crash-recovery R4 (inter#92): space out successive `claude --resume` pane
# starts so ~12 sessions don't hit the API in the same second (the 429
# thundering-herd seen on 2026-08-24 and again — on contextus — 2026-09-04).
# Seconds between pane launches; 0 disables. Paired with CLAUDE_CODE_RETRY_WATCHDOG
# on the resume path in resume_cmd() below.
STAGGER_SECONDS="${STAGGER_SECONDS:-4}"
REANCHOR_TMPL="$HERE/resume-reanchor-prompt.tmpl"
# inter#262: fresh-with-personas by default; resume only by named exception.
LAUNCH_POLICY="${LAUNCH_POLICY:-fresh}"
RESUME_EXCEPTIONS="${RESUME_EXCEPTIONS:-$HERE/resume-exceptions.conf}"
# Sessions that may NEVER be resumed by any mode (beekeeper, Nidavellir#65): 4f3fa045 is the
# contextus session quarantined after the 2026-10-27 stop. Extend via QUARANTINED_SIDS_EXTRA.
QUARANTINED_SIDS="4f3fa045-30ee-4ee3-8fcd-0eadf0d92d68 ${QUARANTINED_SIDS_EXTRA:-}"
MODE="${1:-launch}"
case "$LAUNCH_POLICY" in fresh|auto) ;; *) echo "ERROR: LAUNCH_POLICY must be fresh or auto (got '$LAUNCH_POLICY')" >&2; exit 2 ;; esac

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
FED_HANDLES='qbp-architecture|qbp-implementor|qbp-oppenheimer|qbp-cu-implementor|cth-implementor|wyrd-implementor|bma-implementor|contextus-impl|herschel|notary-implementor|edda-implementor|deming-triage|deming|hutchins|nugent'

# Per-seat model routing (deming/Nidavellir, inter#130 model×eval + CLAUDE.md
# delegation policy — ops/model-routing/README.md has the provenance). Keyed
# by persona, tab-delimited, column 2 is the exact string to pass to `claude
# --model`. A persona missing from the map, or the map unreadable/empty,
# resolves to '' — model_for()'s callers treat '' as "no --model flag", i.e.
# today's behavior (account default). This can never break a launch: a stale,
# unreachable, or absent map degrades silently to the pre-patch behavior,
# never an error.
#
# DEFAULT SOURCE IS origin/main, never the local Nidavellir working tree —
# the shared checkout is not guaranteed to be on main (inventory 2026-10-27:
# parked on arch/1-formal-spec, 15 commits behind) and a launcher should
# never route a seat's model off whatever branch that checkout happens to be
# on (qbp-architecture §I4 on Nidavellir#40). `git show origin/main:<path>`
# reads the committed-on-main blob directly, independent of the working
# tree's checked-out branch or uncommitted state.
#
# This relies on `origin/main` being reasonably fresh in the Nidavellir
# checkout's local refs; model_for() fetches it once per script run (below),
# best-effort — a failed/offline fetch falls back to whatever origin/main
# ref is already on disk (stale-but-present) rather than erroring, so a
# flaky network degrades to a slightly-stale map, never a broken launch.
NIDAVELLIR_DIR="${NIDAVELLIR_DIR:-$HOME/Documents/Nidavellir}"
MODEL_MAP_PATH="ops/model-routing/seat-model-map.tsv"
_MODEL_MAP_FETCHED=""

model_for() {
  local persona="$1"
  # TESTING override: an explicit local file, no git/origin involved at all.
  if [ -n "${FED_MODEL_MAP:-}" ]; then
    [ -f "$FED_MODEL_MAP" ] || { printf ''; return; }
    awk -v p="$persona" -F'\t' '
      $1==p && NF>=2 && $2!="" { print $2; exit }
    ' "$FED_MODEL_MAP"
    return
  fi
  # Default path: origin/main in the Nidavellir checkout, via `git show` —
  # never `cat`/read the local working-tree file.
  [ -d "$NIDAVELLIR_DIR/.git" ] || { printf ''; return; }
  if [ -z "$_MODEL_MAP_FETCHED" ]; then
    git -C "$NIDAVELLIR_DIR" fetch origin main --quiet 2>/dev/null || true
    _MODEL_MAP_FETCHED=1
  fi
  git -C "$NIDAVELLIR_DIR" show "origin/main:$MODEL_MAP_PATH" 2>/dev/null | awk -v p="$persona" -F'\t' '
    $1==p && NF>=2 && $2!="" { print $2; exit }
  '
}

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
  [ -n "$sid" ] && ! is_quarantined "$sid" && { printf '%s' "$sid"; return; }
  local pdir="$PROJECTS/$(slug_of "$workdir")"
  [ -d "$pdir" ] || { printf ''; return; }
  local f top
  # ls -t ...*.jsonl 2>/dev/null: if no jsonl matches, the glob stays literal,
  # ls errors to /dev/null and emits nothing, so the loop simply never runs —
  # no empty-pipe-into-ls-cwd footgun.
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    is_quarantined "$(basename "$f" .jsonl)" && continue   # inter#262: never a candidate
    top="$(grep -aoE "$FED_HANDLES" "$f" 2>/dev/null | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')"
    [ "$top" = "$persona" ] && { basename "$f" .jsonl; return; }
  done < <(ls -t "$pdir"/*.jsonl 2>/dev/null)
  printf ''
}

# inter#262 guards. is_quarantined: exact match against QUARANTINED_SIDS.
is_quarantined() {  # $1=session id
  local s="$1" q
  [ -n "$s" ] || return 1
  for q in $QUARANTINED_SIDS; do [ "$s" = "$q" ] && return 0; done
  return 1
}
# has_refusal: the transcript carries a STRUCTURED refusal stop (the JSON field, not the
# word "refusal" in prose). Nidavellir#65: never resume such a session.
has_refusal() {  # $1=transcript path
  [ -f "$1" ] && grep -aqE '"stop_reason"[[:space:]]*:[[:space:]]*"refusal"' "$1"
}
# Named exceptions: persona -> reason. An entry with no reason is ignored (loudly), so a
# seat can't resume by an unexplained line; ignoring it fails toward FRESH.
declare -A EXC_REASON
load_exceptions() {
  EXC_REASON=()
  [ -f "$RESUME_EXCEPTIONS" ] || return 0
  local line persona reason
  while IFS= read -r line; do
    line="${line%%#*}"
    [[ "$line" =~ ^[[:space:]]*$ ]] && continue
    IFS='|' read -r persona reason <<<"$line"
    persona="$(echo "$persona" | xargs)"
    reason="$(echo "${reason:-}" | xargs)"
    [ -z "$persona" ] && continue
    if [ -z "$reason" ]; then
      echo "⚠  resume exception for '$persona' has no reason — ignored (seat goes FRESH)" >&2
      continue
    fi
    EXC_REASON["$persona"]="$reason"
  done < "$RESUME_EXCEPTIONS"
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
  local sid="$1" persona="${2:-}"
  # Per-seat model routing (inter#130 + CLAUDE.md policy, Nidavellir
  # ops/model-routing/, sourced from origin/main — see model_for() above):
  # inject --model when this persona has a tested/policy model on record.
  # Missing persona / missing map -> model='' -> no flag -> account default.
  local model="" model_flag=""
  if [ -n "$persona" ]; then
    model="$(model_for "$persona")"
    [ -n "$model" ] && model_flag=" --model $model"
  fi
  # With a resolved id: resume it in place. Without one (e.g. a just-migrated
  # persona's first launch in a fresh dir): plain `claude` — a new session.
  # `--continue` is wrong here: it errors when the cwd has no prior conversation.
  #
  # CLAUDE_CODE_RETRY_WATCHDOG=1 makes a resumed session retry 429/529
  # rate-limit errors indefinitely instead of giving up (default ~10 attempts).
  # This is the confirmed fix for the crash-recovery relaunch 429 storm
  # (inter#92): 2026-09-04, contextus-impl resumed into 429 "attempt 9/10" and
  # only survived on the built-in retry — with the watchdog it can't exhaust.
  # Only on the resume path; a fresh `claude` has nothing to retry.
  if [ -n "$sid" ]; then echo "CLAUDE_CODE_RETRY_WATCHDOG=1 $CLAUDE_BIN --resume $sid$model_flag"
  else echo "$CLAUDE_BIN$model_flag"; fi
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

declare -a FRESH REANCHOR_PERSONA REANCHOR_WD REANCHOR_PFILE P_MODE P_NOTE

# Build the launch plan (which panes are FRESH vs. resumed, and which resumed
# panes get a resume re-anchor) from the already-loaded P_PERSONA/P_WORKDIR/
# P_SID/P_PFILE arrays. This IS cmd_launch's real per-pane decision logic,
# factored out so §I4's M2 mutation test can drive it directly — without
# spinning up tmux/claude — instead of reimplementing the gate in the test.
# Populates the global FRESH / REANCHOR_* arrays (reset first) and corrects
# P_SID in place when a pinned/resumed sid has no matching transcript file.
build_launch_plan() {
  FRESH=(); REANCHOR_PERSONA=(); REANCHOR_WD=(); REANCHOR_PFILE=(); P_MODE=(); P_NOTE=()
  load_exceptions
  local i
  for i in "${!P_PERSONA[@]}"; do
    local persona="${P_PERSONA[$i]}" wd="${P_WORKDIR[$i]}" sid="${P_SID[$i]}" pfile="${P_PFILE[$i]}"
    local mode="" note="" transcript
    # 1. Quarantine (inter#262): never resumed, whatever the policy or exception list says.
    if [ -n "$sid" ] && is_quarantined "$sid"; then
      echo "⛔ $persona: session $sid is QUARANTINED — never resumed; pane goes FRESH"
      mode="FRESH-quarantined"; note="quarantined session $sid"; sid=""
    # 2. Policy: under fresh (the default), only a named exception may resume.
    elif [ "$LAUNCH_POLICY" = "fresh" ] && [ -z "${EXC_REASON[$persona]+set}" ]; then
      mode="FRESH"; note="default (fresh-with-personas)"; sid=""
    fi
    # 3. The resumable transcript must exist.
    transcript="$PROJECTS/$(slug_of "$wd")/$sid.jsonl"
    if [ -n "$sid" ] && [ ! -f "$transcript" ]; then
      echo "⚠  $persona: session $sid not found — pane falls back to fresh 'claude'"
      mode="FRESH"; note="session $sid not found"; sid=""
    fi
    # 4. Refusal guard (Nidavellir#65): applies even to a named exception.
    if [ -n "$sid" ] && has_refusal "$transcript"; then
      echo "⛔ $persona: session $sid has a structured refusal stop — never resumed; pane goes FRESH"
      mode="FRESH-forced-by-refusal"; note="refusal stop in $sid"; sid=""
    fi
    if [ -n "$sid" ]; then
      if [ "$LAUNCH_POLICY" = "fresh" ]; then mode="RESUME-exception"; note="${EXC_REASON[$persona]}"
      else mode="RESUME"; note="LAUNCH_POLICY=auto"; fi
    elif [ -z "$mode" ]; then
      mode="FRESH"; note="no resumable session found"
    fi
    P_SID[$i]="$sid"; P_MODE[$i]="$mode"; P_NOTE[$i]="$note"
    # fresh panes (no resumable session) get auto-onboarded below
    [ -z "$sid" ] && FRESH+=("$persona")
    wants_resume_reanchor "$sid" "$pfile" && { REANCHOR_PERSONA+=("$persona"); REANCHOR_WD+=("$wd"); REANCHOR_PFILE+=("$pfile"); }
  done
}

# inter#262: the loud per-seat summary. Never silent about a gap: a missing persona file,
# wisdoms file, RESUME handoff or unmapped model is printed as MISSING and counted.
origin_has() {  # $1=path in the inter repo at origin/main
  git -C "$INTER_REPO" cat-file -e "origin/main:$1" 2>/dev/null
}
print_launch_summary() {
  local i gaps=0 persona wd pfile model pf wis res
  echo ""
  echo "Launch plan (LAUNCH_POLICY=$LAUNCH_POLICY):"
  printf '  %-20s %-24s %-17s %-10s %-8s %-8s %s\n' SEAT MODE MODEL PERSONA WISDOMS RESUME NOTE
  for i in "${!P_PERSONA[@]}"; do
    persona="${P_PERSONA[$i]}"; wd="${P_WORKDIR[$i]}"; pfile="${P_PFILE[$i]}"
    model="$(model_for "$persona")"; [ -n "$model" ] || { model="MISSING"; gaps=$((gaps+1)); }
    if [ -n "$pfile" ]; then
      origin_has "$pfile" && pf="file" || { pf="MISSING"; gaps=$((gaps+1)); }
    elif origin_has "personas/$persona.md"; then pf="generic*"
    else pf="generic"; fi
    origin_has "wisdoms/$persona.md" && wis="ok" || { wis="MISSING"; gaps=$((gaps+1)); }
    [ -f "$wd/RESUME.md" ] && res="ok" || { res="MISSING"; gaps=$((gaps+1)); }
    printf '  %-20s %-24s %-17s %-10s %-8s %-8s %s\n' "$persona" "${P_MODE[$i]:-?}" "$model" "$pf" "$wis" "$res" "${P_NOTE[$i]:-}"
  done
  echo "  PERSONA: file = persona_file column resolved at origin/main; generic* = personas/<seat>.md exists but is not wired in personas.conf."
  if [ "$gaps" -gt 0 ]; then echo "  ⚠ $gaps gap(s) marked MISSING above — fix before relying on this launch."
  else echo "  ✓ no gaps."; fi
}

cmd_plan() {
  ensure_origin_main_fresh >/dev/null 2>&1 || echo "⚠  origin/main fetch failed — persona/wisdoms columns may be stale"
  load_conf
  [ "${#P_PERSONA[@]}" -gt 0 ] || die "no personas in $CONF"
  build_launch_plan
  print_launch_summary
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
  print_launch_summary

  local i first=1
  for i in "${!P_PERSONA[@]}"; do
    local persona="${P_PERSONA[$i]}" wd="${P_WORKDIR[$i]}" sid="${P_SID[$i]}"
    local run; run="$(resume_cmd "$sid" "$persona")"

    # crash-recovery R4 (inter#92): stagger pane starts so ~12 resumes don't
    # storm the API at once. Skip the wait before the first pane (nothing to
    # stagger against yet).
    if [ $first -eq 0 ] && [ "$STAGGER_SECONDS" != "0" ]; then
      sleep "$STAGGER_SECONDS"
    fi

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
    echo "→ $persona  ($wd)  ${P_MODE[$i]}  ${sid:-[fresh claude]}"
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
    plan)      cmd_plan ;;
    list)      cmd_list ;;
    refresh)   cmd_refresh ;;
    kill)      cmd_kill ;;
    help|-h|--help) sed -n '2,/^set -uo pipefail/p' "$0" | sed '$d' | sed 's/^# \{0,1\}//' ;;
    *) die "unknown mode: $MODE (try: launch | plan | list | refresh | kill | help)" ;;
  esac
fi
