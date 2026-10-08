#!/usr/bin/env bash
#
# cutover-preflight.sh — pre-flight check before switching the LIVE
# federation-terminals/ checkout onto a new branch/tag/ref (a "cutover").
#
# Cutover prerequisite (qbp-architecture §I4 C1 item 3). A checkout-switch
# (`git checkout <target>`, a hard reset, a fresh clone swap) silently
# discards any working-tree state that isn't reconciled with the target
# first — the same "no silent drop" rule the persona-file tier table
# enforces (never resolve/act against unaccounted local state; fail loud
# instead). This script is the mechanical guard for federation-terminals/:
# it diffs the LIVE working tree against origin/main and FAILS (non-zero) if
# there is any live-only delta — committed-on-a-branch, staged, unstaged, OR
# untracked-new-file — that hasn't yet landed on main. This is exactly the
# situation this PR itself resolves: inter#92's R4 crash-recovery hardening
# sat uncommitted on process/52-rules-gaps, invisible to `git diff HEAD`,
# until the cutover-prep PR ported it forward — a checkout-switch run before
# that port would have silently thrown it away.
#
# Usage:
#   ./cutover-preflight.sh [<path-within-repo>]     # default: federation-terminals
#
# Exit codes:
#   0  reconciled — the live tree at <path> matches origin/main exactly; safe to cut over
#   1  UNACCOUNTED live-only change detected — prints the diff/paths; NOT safe to cut over
#   2  resolution failure (git unavailable, not a repo, path missing, fetch
#      failed) — FAILS LOUD, never a silent pass
#
# Env:
#   INTER_REPO_DIR=/path   override the repo root (default: parent of this script's directory)
#   FETCH_TIMEOUT=10       seconds to allow `git fetch origin main` before failing loud (§I4 D2 pattern)
#
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTER_REPO="${INTER_REPO_DIR:-$(cd "$HERE/.." && pwd)}"
TARGET_PATH="${1:-federation-terminals}"
FETCH_TIMEOUT="${FETCH_TIMEOUT:-10}"

die_loud() { echo "CUTOVER-PREFLIGHT RESOLUTION FAILED: $*" >&2; exit 2; }

command -v git >/dev/null 2>&1 \
  || die_loud "git not available — cannot diff '$TARGET_PATH' against origin/main. NO silent pass."
git -C "$INTER_REPO" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  || die_loud "$INTER_REPO is not a git working tree."
[ -e "$INTER_REPO/$TARGET_PATH" ] \
  || die_loud "path not found in live tree: $INTER_REPO/$TARGET_PATH"

# D2 (§I4 pattern, same contract as launch-federation.sh / check-persona-drift.sh):
# keep origin/main fresh before diffing. On fetch failure: fail loud, name the
# local ref's age, never silently diff against a possibly-stale ref.
AGE=""
LAST="$(git -C "$INTER_REPO" log -1 --format=%ct origin/main 2>/dev/null)"
[ -n "$LAST" ] && AGE="$(( $(date +%s) - LAST ))"
FETCH_ERR="$(mktemp)"
if ! timeout "$FETCH_TIMEOUT" git -C "$INTER_REPO" fetch origin main >"$FETCH_ERR" 2>&1; then
  AGEMSG=""
  [ -n "$AGE" ] && AGEMSG=" — local origin/main ref is ${AGE}s old"
  ERRTXT="$(cat "$FETCH_ERR" 2>/dev/null)"
  rm -f "$FETCH_ERR"
  die_loud "\`git fetch origin main\` (timeout ${FETCH_TIMEOUT}s) did not succeed for $INTER_REPO${AGEMSG}. $ERRTXT"
fi
rm -f "$FETCH_ERR"

# Tracked-file delta: `git diff <ref> -- <path>` compares the ref straight to
# the WORKING TREE (not to HEAD), so this catches committed-on-current-branch,
# staged, AND unstaged changes alike — including the uncommitted-forever kind
# (inter#92's R4 before this PR).
TRACKED_DIFF="$(git -C "$INTER_REPO" diff origin/main -- "$TARGET_PATH" 2>&1)"
tracked_rc=$?
[ $tracked_rc -eq 0 ] || die_loud "git diff failed: $TRACKED_DIFF"

# Untracked-new-file delta: `git diff` never reports files that were never
# `git add`ed, so a brand-new script sitting only in the live tree would
# otherwise pass silently — exactly the kind of live-only state a cutover
# must not drop. `git status --porcelain` surfaces those ('??' entries).
UNTRACKED="$(git -C "$INTER_REPO" status --porcelain -- "$TARGET_PATH" 2>&1 | grep '^??' || true)"

if [ -n "$TRACKED_DIFF" ] || [ -n "$UNTRACKED" ]; then
  echo "CUTOVER PRE-FLIGHT: FAIL — live '$TARGET_PATH' has unaccounted-for change(s) vs. origin/main:" >&2
  if [ -n "$TRACKED_DIFF" ]; then
    echo "$TRACKED_DIFF" >&2
  fi
  if [ -n "$UNTRACKED" ]; then
    echo "-- untracked (never committed) --" >&2
    echo "$UNTRACKED" >&2
  fi
  echo "Not safe to cut over: reconcile (port forward, or commit + merge to main) before switching the live checkout." >&2
  exit 1
fi

echo "CUTOVER PRE-FLIGHT: PASS — live '$TARGET_PATH' is reconciled with origin/main (no unaccounted change)."
exit 0
