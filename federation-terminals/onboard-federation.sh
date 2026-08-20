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
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="${FED_TERMINALS_CONF:-$HERE/personas.conf}"
TMPL="$HERE/onboard-prompt.tmpl"
SESSION="${FED_TMUX_SESSION:-fed}"
SKIP=" ${ONBOARD_SKIP:-} "
READY_TIMEOUT="${READY_TIMEOUT:-75}"
DRY=0; ONLY=""
for a in "$@"; do if [ "$a" = "--dry-run" ]; then DRY=1; else ONLY="$ONLY $a"; fi; done

die() { echo "ERROR: $*" >&2; exit 1; }
[ -f "$CONF" ] || die "config not found: $CONF"
[ -f "$TMPL" ] || die "template not found: $TMPL"
command -v tmux >/dev/null || die "tmux not installed"
[ "$DRY" -eq 1 ] || tmux has-session -t "$SESSION" 2>/dev/null || die "no tmux session '$SESSION'"

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

render() {  # $1=handle $2=workdir $3=role $4=template(optional, defaults to $TMPL)
  sed -e "s#{{HANDLE}}#$1#g" -e "s#{{WORKDIR}}#$2#g" -e "s#{{ROLE}}#$3#g" "${4:-$TMPL}" | tr -d '\n'
}

onboarded=0; skipped=0
while IFS= read -r line; do
  line="${line%%#*}"; [[ "$line" =~ ^[[:space:]]*$ ]] && continue
  IFS='|' read -r persona workdir _sid <<<"$line"
  persona="$(echo "$persona" | xargs)"; workdir="$(echo "$workdir" | xargs)"
  workdir="${workdir/#\~/$HOME}"
  [ -z "$persona" ] && continue
  # filters
  if [ -n "${ONLY// /}" ]; then case " $ONLY " in *" $persona "*) : ;; *) continue ;; esac; fi
  case "$SKIP" in *" $persona "*) echo "· skip $persona (ONBOARD_SKIP)"; skipped=$((skipped+1)); continue ;; esac
  role="$(role_of "$persona")"
  # deming gets its own boot directive (register/subscribe/monitor + babysit-the-team job)
  tmpl="$TMPL"; [ "$persona" = "deming" ] && [ -f "$HERE/deming-boot.tmpl" ] && tmpl="$HERE/deming-boot.tmpl"
  prompt="$(render "$persona" "$workdir" "$role" "$tmpl")"

  if [ "$DRY" -eq 1 ]; then
    echo "── $persona  ($workdir)  role=$role ──"
    echo "$prompt" | cut -c1-160; echo "   …[$(echo -n "$prompt" | wc -c) chars]"
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
