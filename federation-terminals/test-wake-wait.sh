#!/usr/bin/env bash
# Tests for wake-wait.sh. Exercises THIS checkout's script (resolved relative to
# this test file, or $1 if given) — never the deployed ~/.federation-watcher copy.
# All state lives in a temp FED_WATCH_DIR; every waiter is time-bounded so a
# regression (e.g. a broken singleton) reports FAIL instead of hanging.
set -u
W="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/wake-wait.sh}"
[ -f "$W" ] || { echo "FAIL: script under test not found: $W"; exit 1; }
TD=$(mktemp -d)
case "$TD" in "$HOME/.federation-watcher"*) echo "refusing to run against live watcher dir"; exit 1 ;; esac
export FED_WATCH_DIR="$TD" FED_WAKE_POLL=1 FED_WAKE_SETTLE=0.3
mkdir -p "$TD/wake" "$TD/state"
F="$TD/wake/testseat"; : > "$F"
T="${WAKE_TEST_TIMEOUT:-8}"                 # hard cap (s) on any single waiter
pass=0; fail=0; pids=()
cleanup(){ for p in "${pids[@]}"; do kill "$p" 2>/dev/null; done; rm -rf "$TD"; }
trap cleanup EXIT
chk(){ if eval "$2"; then echo "PASS: $1"; pass=$((pass+1)); else echo "FAIL: $1"; fail=$((fail+1)); fi; }
waitexit(){ for _ in $(seq 1 30); do kill -0 "$1" 2>/dev/null || return 0; sleep 0.2; done; return 1; }
if command -v inotifywait >/dev/null 2>&1; then echo "# script: $W  (wait path: inotify)"
else echo "# script: $W  (wait path: polling fallback)"; fi

echo "== Test A: fires + exits on a new wake line, emits it, advances offset =="
oA="$TD/oA"; timeout "$T" bash "$W" testseat >"$oA" 2>&1 & wp=$!; pids+=("$wp")
sleep 0.6; echo "WAKE:MENTION line-1" >> "$F"
waitexit $wp
chk "A fires + exits"            "! kill -0 $wp 2>/dev/null"
chk "A emits the new line"       "grep -q 'WAKE:MENTION line-1' '$oA'"
chk "A offset advanced to 1"     "[ \"\$(cat $TD/state/testseat.offset 2>/dev/null)\" = 1 ]"

echo "== Test B: no-skip — a mention that lands during handling is caught, not skipped =="
echo "WAKE:MENTION line-2" >> "$F"          # lands before re-arm (the gap)
oB="$TD/oB"; timeout "$T" bash "$W" testseat >"$oB" 2>&1 & wp2=$!; pids+=("$wp2")
waitexit $wp2
chk "B catches the gap-mention" "grep -q 'WAKE:MENTION line-2' '$oB'"
chk "B does NOT re-emit line-1" "! grep -q 'line-1' '$oB'"
chk "B offset advanced to 2"    "[ \"\$(cat $TD/state/testseat.offset 2>/dev/null)\" = 2 ]"

echo "== Test C: singleton — a second waiter exits immediately while one is live =="
oC="$TD/oC"; oD="$TD/oD"
timeout "$T" bash "$W" testseat >"$oC" 2>&1 & w1=$!; pids+=("$w1")   # waiter1 blocks
sleep 0.6
timeout 3 bash "$W" testseat >"$oD" 2>&1    # waiter2 (fg, bounded) should bail now
chk "C second waiter bails"     "grep -q 'already running' '$oD'"
chk "C first waiter still live" "kill -0 $w1 2>/dev/null"
kill $w1 2>/dev/null; wait $w1 2>/dev/null

echo "== Test D: first arm on a non-empty file does NOT replay history =="
FF="$TD/wake/freshseat"; printf 'OLD-1\nOLD-2\nOLD-3\n' > "$FF"
oE="$TD/oE"; timeout "$T" bash "$W" freshseat >"$oE" 2>&1 & wpd=$!; pids+=("$wpd")
sleep 1.0
chk "D does not replay history"      "! grep -q 'OLD-' '$oE'"
chk "D still blocking (waits new)"   "kill -0 $wpd 2>/dev/null"
chk "D seeded offset to EOF (3)"     "[ \"\$(cat $TD/state/freshseat.offset 2>/dev/null)\" = 3 ]"
echo 'WAKE:MENTION fresh-new' >> "$FF"
waitexit $wpd
chk "D fires on new line only"       "grep -q 'fresh-new' '$oE' && ! grep -q 'OLD-' '$oE'"

echo "== Test E: offset advances only AFTER a successful emit (failed emit keeps the line) =="
FE="$TD/wake/fullseat"; : > "$FE"; echo 0 > "$TD/state/fullseat.offset"
timeout "$T" bash "$W" fullseat >/dev/full 2>/dev/null & wpe=$!; pids+=("$wpe")
sleep 0.6; echo 'WAKE:MENTION must-not-lose' >> "$FE"
waitexit $wpe; wait $wpe 2>/dev/null; rcE=$?
chk "E waiter exited with emit error" "[ $rcE -ne 0 ] && [ $rcE -ne 124 ]"
chk "E offset NOT advanced (still 0)" "[ \"\$(cat $TD/state/fullseat.offset 2>/dev/null)\" = 0 ]"
oF="$TD/oF"; timeout "$T" bash "$W" fullseat >"$oF" 2>&1 & wpf=$!; pids+=("$wpf")
waitexit $wpf
chk "E re-arm delivers the line"      "grep -q 'must-not-lose' '$oF'"

echo "== Test F: wake file rotated (shorter than offset) — resumes from the new start =="
FR="$TD/wake/rotseat"; : > "$FR"; echo 5 > "$TD/state/rotseat.offset"
oG="$TD/oG"; timeout "$T" bash "$W" rotseat >"$oG" 2>&1 & wpg=$!; pids+=("$wpg")
sleep 0.6; echo 'WAKE:MENTION post-rotate' >> "$FR"
waitexit $wpg
chk "F fires after rotation"          "grep -q 'post-rotate' '$oG'"
chk "F offset reset to 1"             "[ \"\$(cat $TD/state/rotseat.offset 2>/dev/null)\" = 1 ]"

echo "---- $pass passed, $fail failed ----"
[ "$fail" = 0 ]
