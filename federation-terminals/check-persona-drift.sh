#!/usr/bin/env bash
#
# check-persona-drift.sh — detect when an on-disk runtime copy of a canonical
# persona file has drifted from the origin/main source of truth (inter#142).
#
# Canonical source: the fenced code block under the "## The prompt" heading in
# <source-path> at origin/main of this (inter) repo — never a local/worktree
# copy (AC2: same "never a worktree" resolution rule as the launch/resume
# boot text uses).
#
# Runtime copy: per persona-v0.2 §12, a generated file whose body must be
# byte-identical to that canonical block. It may be preceded by:
#   - runtime-specific YAML frontmatter (a `---` ... `---` block, e.g.
#     Antigravity's name/description/tools), and then
#   - exactly one header comment line: `<!-- GENERATED from ... -->`
# Both are excluded from the comparison (§12; inter#142 AC4) — only the body
# after them has to match, byte for byte.
#
# Usage:
#   ./check-persona-drift.sh <source-path-in-inter-repo> <runtime-copy-file>
#
# Exit codes:
#   0  byte-identical (no drift)
#   1  drift detected — names the runtime-copy file, prints a diff
#   2  resolution failure (git unavailable, source path missing at
#      origin/main, runtime-copy file missing, or no "## The prompt" fenced
#      block found) — FAILS LOUD, never a silent pass (AC2 applied to AC4)
#
# Env:
#   INTER_REPO_DIR=/path   override the inter repo root (default: parent of
#                          this script's directory)
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTER_REPO="${INTER_REPO_DIR:-$(cd "$HERE/.." && pwd)}"

usage() { echo "usage: $(basename "$0") <source-path-in-inter-repo> <runtime-copy-file>" >&2; exit 2; }
[ $# -eq 2 ] || usage
SRC_PATH="$1"
COPY_FILE="$2"

die_loud() { echo "DRIFT-CHECK RESOLUTION FAILED: $*" >&2; exit 2; }

command -v git >/dev/null 2>&1 || die_loud "git not available — cannot resolve '$SRC_PATH' from origin/main. NO silent pass."
[ -f "$COPY_FILE" ] || die_loud "runtime-copy file not found: $COPY_FILE"

CANON_SRC="$(git -C "$INTER_REPO" show "origin/main:$SRC_PATH" 2>&1)" \
  || die_loud "'$SRC_PATH' not found at origin/main of $INTER_REPO (git show: $CANON_SRC)"

# Extract the fenced ``` block that follows the "## The prompt" heading.
extract_prompt_block() {
  awk '
    BEGIN { in_section = 0; in_fence = 0 }
    /^## The prompt/ { in_section = 1; next }
    in_section && /^```/ {
      if (in_fence) { exit } else { in_fence = 1; next }
    }
    in_fence { print }
  '
}

# Strip a leading YAML frontmatter block, then a single "<!-- GENERATED ...
# -->" header line, then a single blank separator line — whichever of those
# are actually present, in that order (persona-v0.2 §12.2).
strip_runtime_wrapper() {
  awk '
    { lines[NR] = $0 }
    END {
      n = NR; i = 1
      if (n >= 1 && lines[1] == "---") {
        close_idx = 0
        for (j = 2; j <= n; j++) { if (lines[j] == "---") { close_idx = j; break } }
        if (close_idx > 0) i = close_idx + 1
      }
      if (i <= n && lines[i] ~ /^<!-- GENERATED /) i++
      if (i <= n && lines[i] == "") i++
      for (; i <= n; i++) print lines[i]
    }
  '
}

CANON_BLOCK="$(printf '%s' "$CANON_SRC" | extract_prompt_block)"
[ -n "$CANON_BLOCK" ] || die_loud "no '## The prompt' fenced block found in origin/main:$SRC_PATH"

COPY_BODY="$(strip_runtime_wrapper < "$COPY_FILE")"

if [ "$CANON_BLOCK" = "$COPY_BODY" ]; then
  echo "OK: $COPY_FILE is byte-identical to origin/main:$SRC_PATH (header/frontmatter excluded)"
  exit 0
fi

echo "DRIFT DETECTED: $COPY_FILE diverges from origin/main:$SRC_PATH" >&2
diff <(printf '%s\n' "$CANON_BLOCK") <(printf '%s\n' "$COPY_BODY") >&2
exit 1
