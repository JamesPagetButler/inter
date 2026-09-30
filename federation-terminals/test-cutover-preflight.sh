#!/usr/bin/env bash
#
# test-cutover-preflight.sh — unit tests for cutover-preflight.sh
# (qbp-architecture §I4 C1 item 3, cutover-prep PR / Closes inter#92 sibling).
#
# Fully isolated: builds a throwaway bare remote + clone under $TMPDIR and
# never touches the real ~/Documents/inter repo, its federation-terminals/
# working tree, or any shared ref (same discipline as
# test-persona-file-loading.sh's §I4 D2 fixture).
#
# Usage: ./test-cutover-preflight.sh
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMPDIR="$(mktemp -d)"
cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

pass=0; fail=0
check() { if [ "$1" = "0" ]; then echo "  ✓ $2"; pass=$((pass+1)); else echo "  ✗ $2"; fail=$((fail+1)); fi; }

# ─────────────────────────────────────────────────────────────────────────
echo "== fixture: bare remote + a 'live' clone, federation-terminals/ seeded on main =="
REMOTE="$TMPDIR/remote.git"
git init -q --bare "$REMOTE"
SEED="$TMPDIR/seed"
git clone -q "$REMOTE" "$SEED"
(
  cd "$SEED"
  git checkout -q -b main 2>/dev/null || git checkout -q main
  mkdir -p federation-terminals
  echo "original launch-federation.sh content" > federation-terminals/launch-federation.sh
  echo "persona | /tmp/wd | AUTO" > federation-terminals/personas.conf
  git add federation-terminals
  git -c user.email=t@t.test -c user.name=tester commit -q -m "seed federation-terminals"
  git push -q origin main
)

LIVE="$TMPDIR/live-clone"
git clone -q "$REMOTE" "$LIVE"
(cd "$LIVE" && (git checkout -q main 2>/dev/null || true))

echo "== reconciled tree: live == origin/main -> PASS, exit 0 =="
INTER_REPO_DIR="$LIVE" "$HERE/cutover-preflight.sh" federation-terminals >/tmp/cop_pass.$$ 2>&1
rc=$?
check "$rc" "reconciled live tree: cutover-preflight.sh exits 0"
grep -qi "PASS" /tmp/cop_pass.$$ && check 0 "PASS run names PASS in its output" || check 1 "PASS run names PASS in its output"
rm -f /tmp/cop_pass.$$

echo "== planted live-only UNCOMMITTED change to a tracked file -> FAIL, non-zero, names the file =="
echo "PLANTED LIVE-ONLY CHANGE — never landed on origin/main" >> "$LIVE/federation-terminals/launch-federation.sh"
INTER_REPO_DIR="$LIVE" "$HERE/cutover-preflight.sh" federation-terminals >/tmp/cop_fail.$$ 2>&1
rc=$?
grep -q "launch-federation.sh" /tmp/cop_fail.$$ && namedok=0 || namedok=1
[ "$rc" -ne 0 ] && [ "$namedok" -eq 0 ] \
  && check 0 "planted uncommitted tracked-file change: non-zero exit, names the drifted file" \
  || { check 1 "planted uncommitted tracked-file change: non-zero exit, names the drifted file"; cat /tmp/cop_fail.$$; }
rm -f /tmp/cop_fail.$$

echo "== reverting the plant reconciles the tree again -> PASS =="
git -C "$LIVE" checkout -- federation-terminals/launch-federation.sh
INTER_REPO_DIR="$LIVE" "$HERE/cutover-preflight.sh" federation-terminals >/tmp/cop_pass2.$$ 2>&1
check "$?" "after reverting the plant: exit 0 again (reconciled)"
rm -f /tmp/cop_pass2.$$

echo "== planted live-only UNTRACKED (never-added) new file -> FAIL, non-zero, names the file =="
# git diff <ref> never reports a file that was never `git add`ed — this
# guards that gap (the script also checks `git status --porcelain`).
echo "brand new script, never committed" > "$LIVE/federation-terminals/zz-new-live-only-script.sh"
INTER_REPO_DIR="$LIVE" "$HERE/cutover-preflight.sh" federation-terminals >/tmp/cop_untracked.$$ 2>&1
rc=$?
grep -q "zz-new-live-only-script.sh" /tmp/cop_untracked.$$ && namedok=0 || namedok=1
[ "$rc" -ne 0 ] && [ "$namedok" -eq 0 ] \
  && check 0 "planted untracked new file: non-zero exit, names the file (git diff alone would miss this)" \
  || { check 1 "planted untracked new file: non-zero exit, names the file"; cat /tmp/cop_untracked.$$; }
rm -f /tmp/cop_untracked.$$
rm -f "$LIVE/federation-terminals/zz-new-live-only-script.sh"

echo "== after removing the untracked plant, tree reconciles again -> PASS =="
INTER_REPO_DIR="$LIVE" "$HERE/cutover-preflight.sh" federation-terminals >/tmp/cop_pass3.$$ 2>&1
check "$?" "after removing the untracked plant: exit 0 again (reconciled)"
rm -f /tmp/cop_pass3.$$

echo "== resolution failures fail loud (exit 2), never a silent pass =="
INTER_REPO_DIR="$LIVE" "$HERE/cutover-preflight.sh" "federation-terminals/does-not-exist-subpath" >/tmp/cop_badpath.$$ 2>&1
rc=$?
grep -qi "not found" /tmp/cop_badpath.$$ && namedok=0 || namedok=1
[ "$rc" -eq 2 ] && [ "$namedok" -eq 0 ] \
  && check 0 "missing path: fails loud, exit 2, names the path" \
  || { check 1 "missing path: fails loud, exit 2, names the path (got rc=$rc)"; cat /tmp/cop_badpath.$$; }
rm -f /tmp/cop_badpath.$$

NOTGIT="$TMPDIR/not-a-repo"; mkdir -p "$NOTGIT/federation-terminals"
INTER_REPO_DIR="$NOTGIT" "$HERE/cutover-preflight.sh" federation-terminals >/tmp/cop_notgit.$$ 2>&1
rc=$?
grep -qi "not a git working tree" /tmp/cop_notgit.$$ && namedok=0 || namedok=1
[ "$rc" -eq 2 ] && [ "$namedok" -eq 0 ] \
  && check 0 "not a git repo: fails loud, exit 2, names the problem" \
  || { check 1 "not a git repo: fails loud, exit 2, names the problem (got rc=$rc)"; cat /tmp/cop_notgit.$$; }
rm -f /tmp/cop_notgit.$$

echo
echo "RESULT: $pass passed, $fail failed"
exit $([ "$fail" -eq 0 ] && echo 0 || echo 1)
