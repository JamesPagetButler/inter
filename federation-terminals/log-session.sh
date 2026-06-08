#!/usr/bin/env bash
#
# log-session.sh <persona> [workdir] — federation sign-on session-id logger.
#
# Run this as the FIRST action when a persona signs on to sessionbridge. It
# records THIS claude session's id into the central roster, so the federation
# always has an authoritative persona -> session-id mapping for resume-after-crash.
#
# WHY: persona->session-id cannot be reverse-engineered from transcript content —
# personas cross-talk too much (a cth-implementor session mentions qbp-implementor
# hundreds of times). The session self-reporting at sign-on is the only source of
# truth. See ~/Documents/inter/federation-terminals/SIGN-ON-ADDENDUM.md.
#
# Reliable because: the transcript file this session is actively appending to is
# the most-recently-modified UUID-named *.jsonl in its project-history dir.
#
set -uo pipefail

PERSONA="${1:?usage: log-session.sh <persona> [workdir]}"
WORKDIR="${2:-$PWD}"
ROSTER="$HOME/.federation-watcher/session-roster.tsv"
PROJECTS="$HOME/.claude/projects"

slug="$(printf '%s' "$WORKDIR" | sed 's#/#-#g')"
pdir="$PROJECTS/$slug"
[ -d "$pdir" ] || { echo "ERROR: no project history dir for $WORKDIR ($pdir)" >&2; exit 1; }

# own session = newest UUID-named transcript (exclude subagent agent-*.jsonl)
newest="$(ls -t "$pdir"/????????-????-????-????-????????????.jsonl 2>/dev/null | head -1)"
[ -n "$newest" ] || { echo "ERROR: could not determine session id in $pdir" >&2; exit 1; }
sid="$(basename "$newest" .jsonl)"

# Staleness guard (bma-implementor, seq=471). The LIVE session's transcript is
# written continuously — running this command itself writes to it — so an active
# session's pick is SECONDS old. A pick that is minutes/hours old means the wrong
# session was matched: usually the shell's cwd is not this session's workdir, or
# another session is newer in a shared project dir (~/Documents). Refuse rather
# than silently log a stale row (the exact footgun that mis-logged 75e1c976).
now="$(date +%s)"; mt="$(stat -c %Y "$newest" 2>/dev/null || echo "$now")"
age=$(( now - mt ))
if [ "$age" -gt 60 ] && [ "${FORCE:-0}" != "1" ]; then
  echo "⚠ REFUSING: matched transcript is ${age}s old — not a live session." >&2
  echo "  Your shell cwd ($WORKDIR) is probably not this session's workdir, or a" >&2
  echo "  newer session exists in a shared project dir. Pass the workdir explicitly:" >&2
  echo "      log-session.sh $PERSONA /home/prime/Documents" >&2
  echo "  and re-check the echoed id against a path your own harness shows you." >&2
  echo "  (Override with FORCE=1 only if you are certain.)" >&2
  exit 2
fi

mkdir -p "$(dirname "$ROSTER")"
ts="$(date -Iseconds 2>/dev/null || date)"

# rewrite: header + all rows except this persona's old one + the fresh row
tmp="$(mktemp)"
{
  printf 'persona\tworkdir\tsession_id\tlogged_at\n'
  [ -f "$ROSTER" ] && awk -v p="$PERSONA" -F'\t' 'NR==1&&$1=="persona"{next} $1!=p' "$ROSTER"
  printf '%s\t%s\t%s\t%s\n' "$PERSONA" "$WORKDIR" "$sid" "$ts"
} > "$tmp"
mv "$tmp" "$ROSTER"

echo "✓ logged: $PERSONA -> $sid  ($WORKDIR)  @ $ts"
echo "  roster: $ROSTER"
