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
sid="$(ls -t "$pdir"/????????-????-????-????-????????????.jsonl 2>/dev/null \
        | head -1 | xargs -r -n1 basename | sed 's/\.jsonl$//')"
[ -n "$sid" ] || { echo "ERROR: could not determine session id in $pdir" >&2; exit 1; }

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
