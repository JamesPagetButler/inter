#!/usr/bin/env bash
# Test run-bounded's three guarantees: normal job passes, memory runaway is
# OOM-killed at the cap, time runaway is killed at the deadline. Uses a
# throwaway ledger. Requires rootless systemd --user memory-cgroup delegation.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RB="$HERE/run-bounded"
export RUN_BOUNDED_LEDGER="$(mktemp)"
pass=0; fail=0
check() { if [ "$1" = "$2" ]; then echo "  ✓ $3 (rc=$1)"; pass=$((pass+1)); else echo "  ✗ $3 (got rc=$1, want $2)"; fail=$((fail+1)); fi; }

echo "== 1. a well-behaved job under the cap → exit 0 =="
"$RB" 256M 10 python3 -c "b=bytearray(50*1024*1024); print('ok')" >/dev/null 2>&1
check $? 0 "bounded job completes"

echo "== 2. memory runaway (allocate 400MB, touched, under 128M cap) → OOM-killed (137) =="
"$RB" 128M 30 python3 -c "
buf=[]
for i in range(400):
    b=bytearray(1024*1024)
    for j in range(0,len(b),4096): b[j]=1
    buf.append(b)
" >/dev/null 2>&1
check $? 137 "memory runaway OOM-killed at cap"

echo "== 3. time runaway (sleep 60 under a 3s cap) → timed out (124) =="
"$RB" 128M 3 sleep 60 >/dev/null 2>&1
check $? 124 "time runaway killed at deadline"

echo "== 4. ledger recorded all three launches (START+DONE pairs) =="
starts=$(grep -c $'\tSTART\t' "$RUN_BOUNDED_LEDGER" 2>/dev/null || echo 0)
dones=$(grep -c $'\tDONE\t' "$RUN_BOUNDED_LEDGER" 2>/dev/null || echo 0)
check "$starts/$dones" "3/3" "ledger has 3 START + 3 DONE rows"

echo "== 5. box unharmed (federation still up) =="
[ "$(tmux has-session -t fed 2>/dev/null && echo up)" = "up" ] && { echo "  ✓ fed tmux still up"; pass=$((pass+1)); } || { echo "  (fed not running — skipped)"; }

rm -f "$RUN_BOUNDED_LEDGER"
echo
echo "RESULT: $pass passed, $fail failed"
exit $([ $fail -eq 0 ] && echo 0 || echo 1)
