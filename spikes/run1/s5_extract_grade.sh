#!/usr/bin/env bash
# Extract a grader sub-agent's final report verbatim from its transcript JSONL.
# The report is the `message` of its last SubagentHandback call (or, failing
# that, its last text block). usage: s5_extract_grade.sh <transcript> <out>
set -euo pipefail
jq -rs '([.[] | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use" and .name=="SubagentHandback") | .input.message] | last) // ([.[] | select(.type=="assistant") | .message.content[]? | select(.type=="text") | .text] | last)' "$1" > "$2"
