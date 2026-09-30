#!/usr/bin/env bash
#
# onboard-federation.sh — drive each fresh persona pane through its federation
# boot protocol (ground → register → subscribe → arm §2.i Monitor → re-anchor),
# so a launched pane comes up FULLY OPERATIONAL and responsive on chat, not as a
# blank claude session. Reads personas.conf, finds each persona's pane in the
# tmux session by cwd, and sends it the substituted onboard-prompt.tmpl.
#
# Prereqs (so onboarding runs hands-free): the persona dirs are pre-trusted
# (hasTrustDialogAccepted) AND the sessionbridge/Monitor tools are allowlisted in
# each dir's .claude/settings.local.json — i.e. federation-optimization #1 + #2.
# Without those, each register/subscribe/Monitor call stalls at an approval prompt.
#
# Usage:
#   ./onboard-federation.sh                 # onboard every persona in personas.conf
#   ./onboard-federation.sh bma-implementor wyrd-implementor   # only these handles
#   ./onboard-federation.sh --dry-run       # print what would be sent, send nothing
# Env:
#   FED_TMUX_SESSION=fed         # tmux session (default: fed)
#   FED_TERMINALS_CONF=/path     # personas.conf override
#   ONBOARD_SKIP="a b"           # handles to skip (e.g. resumed/grounded sessions)
#   READY_TIMEOUT=75             # seconds to wait for a pane's chat prompt
#                                # (needs headroom: 11 concurrent claude boots on
#                                #  a slow host can take >30s to reach the prompt)
#   ONBOARD_RENDER_FULL=1        # with --dry-run, print the full rendered prompt
#                                # instead of the 160-char preview (debugging /
#                                # golden-file testing; default unset — unset
#                                # behavior is byte-for-byte what it was before
#                                # inter#142, so this is purely additive)
#   FETCH_TIMEOUT=10             # seconds to allow `git fetch origin main` before failing
#                                # loud (§I4 D2) — never resolve persona-files against a
#                                # silently-stale origin/main ref.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="${FED_TERMINALS_CONF:-$HERE/personas.conf}"
TMPL="$HERE/onboard-prompt.tmpl"
PERSONAFILE_TMPL="$HERE/onboard-prompt-personafile.tmpl"
INTER_REPO="${INTER_REPO_DIR:-$(cd "$HERE/.." && pwd)}"
SESSION="${FED_TMUX_SESSION:-fed}"
SKIP=" ${ONBOARD_SKIP:-} "
READY_TIMEOUT="${READY_TIMEOUT:-75}"
FETCH_TIMEOUT="${FETCH_TIMEOUT:-10}"
DRY=0; ONLY=""
for a in "$@"; do if [ "$a" = "--dry-run" ]; then DRY=1; else ONLY="$ONLY $a"; fi; done

die() { echo "ERROR: $*" >&2; exit 1; }
[ -f "$CONF" ] || die "config not found: $CONF"
[ -f "$TMPL" ] || die "template not found: $TMPL"
[ -f "$PERSONAFILE_TMPL" ] || die "template not found: $PERSONAFILE_TMPL"
command -v tmux >/dev/null || die "tmux not installed"
[ "$DRY" -eq 1 ] || tmux has-session -t "$SESSION" 2>/dev/null || die "no tmux session '$SESSION'"

# D2 (§I4): `git show origin/main:<path>` only reads the LOCAL remote-tracking
# ref — a stale one would onboard a fresh pane with an old persona while
# believing it read main. Runs the actual fetch once per process before the
# first resolution. On failure: FAIL LOUD and name the local ref's age —
# never silently resolve against a possibly-stale ref. (Same contract as
# launch-federation.sh's copy of this function.)
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
# non-zero. Callers MUST NOT silently fall back to the generic onboard on
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

# handle -> sessionbridge role tag (free-form; keep in step with the roster)
role_of() {
  case "$1" in
    *-architecture)  echo "architect" ;;
    *oppenheimer)    echo "strategic-lead" ;;
    herschel)        echo "sprint-driver" ;;
    notary-*)        echo "verification-function" ;;
    *-impl|*-implementor) echo "implementor" ;;
    *)               echo "implementor" ;;
  esac
}

# first pane in $SESSION whose cwd == $1 (tilde-expanded); '' if none
pane_for_cwd() {
  local want="$1" p path
  for p in $(tmux list-panes -t "$SESSION" -F '#{pane_id}' 2>/dev/null); do
    path="$(tmux display -p -t "$p" '#{pane_current_path}' 2>/dev/null)"
    [ "$path" = "$want" ] && { printf '%s' "$p"; return; }
  done
  printf ''
}

# wait until a pane shows a chat input prompt (❯) or timeout; best-effort
wait_ready() {
  local p="$1" end=$(( SECONDS + READY_TIMEOUT ))
  while [ "$SECONDS" -lt "$end" ]; do
    tmux capture-pane -p -t "$p" 2>/dev/null | grep -q '❯' && return 0
    sleep 1
  done
  return 1
}

render() {  # $1=handle $2=workdir $3=role $4=template(optional, defaults to $TMPL) $5=persona_file(optional)
  sed -e "s#{{HANDLE}}#$1#g" -e "s#{{WORKDIR}}#$2#g" -e "s#{{ROLE}}#$3#g" -e "s#{{PERSONA_FILE}}#${5:-}#g" "${4:-$TMPL}" | tr -d '\n'
}

onboarded=0; skipped=0
while IFS= read -r line; do
  line="${line%%#*}"; [[ "$line" =~ ^[[:space:]]*$ ]] && continue
  IFS='|' read -r persona workdir _sid pfile <<<"$line"
  persona="$(echo "$persona" | xargs)"; workdir="$(echo "$workdir" | xargs)"
  pfile="$(echo "${pfile:-}" | xargs)"
  workdir="${workdir/#\~/$HOME}"
  [ -z "$persona" ] && continue
  # filters
  if [ -n "${ONLY// /}" ]; then case " $ONLY " in *" $persona "*) : ;; *) continue ;; esac; fi
  case "$SKIP" in *" $persona "*) echo "· skip $persona (ONBOARD_SKIP)"; skipped=$((skipped+1)); continue ;; esac
  role="$(role_of "$persona")"
  # persona-file column (inter#142): a canonical persona def replaces the
  # generic boot text, naming the path + "run its §0" — but only once its
  # origin/main path is verified to resolve (AC2: no silent fallback on
  # failure; empty column = today's generic onboard, unchanged, for every
  # other seat).
  tmpl="$TMPL"; pf_arg=""
  if [ -n "$pfile" ]; then
    if resolve_persona_file "$pfile"; then
      tmpl="$PERSONAFILE_TMPL"; pf_arg="$pfile"
    else
      echo "⚠ $persona: persona-file '$pfile' FAILED to resolve from origin/main — refusing to onboard with an unverified identity (no silent fallback to the generic onboard). Beekeeper must fix personas.conf or origin/main."
      skipped=$((skipped+1)); continue
    fi
  fi
  # deming gets its own boot directive (register/subscribe/monitor + babysit-the-team job)
  [ "$persona" = "deming" ] && [ -f "$HERE/deming-boot.tmpl" ] && tmpl="$HERE/deming-boot.tmpl"
  prompt="$(render "$persona" "$workdir" "$role" "$tmpl" "$pf_arg")"

  if [ "$DRY" -eq 1 ]; then
    echo "── $persona  ($workdir)  role=$role ──"
    if [ "${ONBOARD_RENDER_FULL:-0}" = "1" ]; then
      echo "$prompt"
    else
      echo "$prompt" | cut -c1-160; echo "   …[$(echo -n "$prompt" | wc -c) chars]"
    fi
    onboarded=$((onboarded+1)); continue
  fi

  pane="$(pane_for_cwd "$workdir")"
  [ -z "$pane" ] && { echo "⚠ $persona: no pane with cwd $workdir — skipping"; skipped=$((skipped+1)); continue; }
  wait_ready "$pane" || echo "  (⚠ $persona pane $pane not showing a prompt after ${READY_TIMEOUT}s — sending anyway)"
  tmux send-keys -t "$pane" -l "$prompt"
  sleep 0.4
  tmux send-keys -t "$pane" Enter
  echo "→ onboarded $persona  (pane $pane, cwd $workdir)"
  onboarded=$((onboarded+1))
done < "$CONF"

echo "✓ onboard pass complete: $onboarded onboarded, $skipped skipped."
