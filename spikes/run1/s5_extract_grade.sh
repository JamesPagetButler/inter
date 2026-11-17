#!/usr/bin/env bash
# Extract a grader sub-agent's final text verbatim from its transcript JSONL.
# usage: s5_extract_grade.sh <transcript.jsonl> <out.grades.jsonl>
set -euo pipefail
jq -rs '[.[] | select(.type=="assistant") | .message.content[]? | select(.type=="text") | .text] | last' "$1" > "$2"
