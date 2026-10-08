#!/usr/bin/env bash
#
# test-persona-file-loading.sh — unit/golden-file tests for inter#142
# (persona-file loading on launch/resume), REISSUED after qbp-architecture's
# §I4 CHANGES-REQUESTED on PR #143. Covers AC1-AC7 plus the mutation-kill
# evidence the review required (M1/M1b/M2 KILLED) and the D1 overlay split
# (personas.local.conf).
#
# These are "unit/golden tests with fake panes" per the issue's stated
# verification boundary — the true acceptance evidence (a live Notary-pane
# restart) is a separate, post-merge, beekeeper-timed step and is NOT what
# this script attempts.
#
# Touches NO real federation state: never targets the real "fed" tmux
# session, never calls sessionbridge, never mutates the tracked working-tree
# copy of any file in this repo (§I4 N2 — the old AC2 test appended to the
# REAL prompt file and relied on a trap to revert it; a SIGKILL mid-test would
# have left it dirty). All divergence/mutation fixtures below live entirely
# under $TMPDIR (throwaway git worktrees, throwaway bare repos, throwaway
# personas.conf/personas.local.conf files) and are destroyed on exit.
#
# Usage: ./test-persona-file-loading.sh
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTER_REPO="$(cd "$HERE/.." && pwd)"
TMPDIR="$(mktemp -d)"
DIVERGE_WT=""
STAGGER_TEST_SESSION=""
cleanup() {
  if [ -n "$DIVERGE_WT" ]; then
    git -C "$INTER_REPO" worktree remove --force "$DIVERGE_WT" 2>/dev/null
    git -C "$INTER_REPO" worktree prune 2>/dev/null
  fi
  [ -n "$STAGGER_TEST_SESSION" ] && tmux kill-session -t "$STAGGER_TEST_SESSION" 2>/dev/null
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

pass=0; fail=0
check() { if [ "$1" = "0" ]; then echo "  ✓ $2"; pass=$((pass+1)); else echo "  ✗ $2"; fail=$((fail+1)); fi; }
checkeq() { if [ "$1" = "$2" ]; then echo "  ✓ $3"; pass=$((pass+1)); else echo "  ✗ $3 (got [$1], want [$2])"; fail=$((fail+1)); fi; }

REAL_PATH="prompt/notary-implementor-launch-prompt.md"

# ─────────────────────────────────────────────────────────────────────────
echo "== setup: origin/main baseline copy (old script + old conf side by side, so each resolves its OWN default CONF) =="
git -C "$INTER_REPO" fetch origin main >/dev/null 2>&1
git -C "$INTER_REPO" show origin/main:federation-terminals/launch-federation.sh  > "$TMPDIR/old-launch.sh"
git -C "$INTER_REPO" show origin/main:federation-terminals/onboard-federation.sh > "$TMPDIR/old-onboard.sh"
git -C "$INTER_REPO" show origin/main:federation-terminals/onboard-prompt.tmpl   > "$TMPDIR/old-onboard-prompt.tmpl"
# onboard-federation.sh (origin/main, post-#143) now hard-requires its own
# PERSONAFILE_TMPL to exist next to it (`die` if missing) — the "old" fixture
# needs this sibling too, or the AC5-part-2 dry-run comparison below fails on
# a bootstrap error before either side even renders anything. Fixed
# (cutover-prep PR, unrelated to this PR's own scope): fetch it alongside
# the other old-* origin/main copies.
git -C "$INTER_REPO" show origin/main:federation-terminals/onboard-prompt-personafile.tmpl > "$TMPDIR/old-onboard-prompt-personafile.tmpl"
git -C "$INTER_REPO" show origin/main:federation-terminals/personas.conf        > "$TMPDIR/old-personas.conf"
git -C "$INTER_REPO" show origin/main:federation-terminals/deming-boot.tmpl     > "$TMPDIR/deming-boot.tmpl" 2>/dev/null
mkdir -p "$TMPDIR/oldft"
cp "$TMPDIR/old-launch.sh" "$TMPDIR/oldft/launch-federation.sh"
cp "$TMPDIR/old-onboard.sh" "$TMPDIR/oldft/onboard-federation.sh"
cp "$TMPDIR/old-onboard-prompt.tmpl" "$TMPDIR/oldft/onboard-prompt.tmpl"
cp "$TMPDIR/old-onboard-prompt-personafile.tmpl" "$TMPDIR/oldft/onboard-prompt-personafile.tmpl"
cp "$TMPDIR/old-personas.conf" "$TMPDIR/oldft/personas.conf"
[ -f "$TMPDIR/deming-boot.tmpl" ] && cp "$TMPDIR/deming-boot.tmpl" "$TMPDIR/oldft/deming-boot.tmpl"
chmod +x "$TMPDIR/oldft/launch-federation.sh" "$TMPDIR/oldft/onboard-federation.sh"

# Originally (pre-#145 D1) origin/main pinned qbp-oppenheimer inline
# (cc9bae42...); the reissue moved that pin to the gitignored overlay and
# left personas.conf all-AUTO. #145 (D1 roster reconciliation) has SINCE
# merged and flipped origin/main's own personas.conf row to AUTO too — so
# extracting the 3rd column here now yields the literal string "AUTO", not a
# real session id. Fixed (cutover-prep PR, unrelated to this PR's own
# scope): only synthesize an overlay pin when a REAL sid was extracted;
# otherwise leave the overlay empty so both OLD and NEW fall through to
# their own (matching) ordinary AUTO discovery — a literal "AUTO" string
# must never be written into the overlay as if it were a resolved sid (that
# previously made NEW report "AUTO (!! session file missing)" while OLD's
# genuine AUTO discovery correctly resolved the real session, a spurious
# byte-mismatch unrelated to any real behavior difference).
OPPENHEIMER_PIN="$(awk -F'|' '/^qbp-oppenheimer/ { gsub(/^[ \t]+|[ \t]+$/, "", $3); print $3 }' "$TMPDIR/old-personas.conf")"
AC5_OVERLAY="$TMPDIR/ac5-personas.local.conf"
if [ -n "$OPPENHEIMER_PIN" ] && [ "$OPPENHEIMER_PIN" != "AUTO" ]; then
  printf 'qbp-oppenheimer | %s\n' "$OPPENHEIMER_PIN" > "$AC5_OVERLAY"
else
  : > "$AC5_OVERLAY"
fi

echo "== AC5 (part 1/2): launch-federation.sh 'list' output unchanged (structure+overlay reproduces old inline-pin behavior) =="
OLD_LIST="$("$TMPDIR/oldft/launch-federation.sh" list 2>&1)"
NEW_LIST="$(FED_TERMINALS_LOCAL_CONF="$AC5_OVERLAY" "$HERE/launch-federation.sh" list 2>&1)"
# The hutchins row is EXCLUDED from this byte-identical comparison (inter#143
# C1 item 1, qbp-architecture §I4): FED_HANDLES on this branch now includes
# hutchins, so on a machine with a real hutchins-dominant transcript under
# $PROJECTS, NEW correctly content-sniffs a session-id that OLD (origin/main,
# still missing hutchins from FED_HANDLES) structurally cannot see. That row
# is EXPECTED to diverge — it's the fix, not a regression — and is verified
# directly by the dedicated content-sniff test below instead.
OLD_LIST_CMP="$(printf '%s\n' "$OLD_LIST" | grep -v '^hutchins ')"
NEW_LIST_CMP="$(printf '%s\n' "$NEW_LIST" | grep -v '^hutchins ')"
checkeq "$(printf '%s' "$NEW_LIST_CMP" | md5sum | awk '{print $1}')" "$(printf '%s' "$OLD_LIST_CMP" | md5sum | awk '{print $1}')" \
  "launch-federation.sh list output byte-identical old vs new (12 of 13 seats, incl. notary's new 4th column, via structure+overlay; hutchins row excluded here — its intentional divergence is covered by the dedicated content-sniff test below)"

echo "== AC5 (part 2/2): onboard-federation.sh --dry-run output unchanged for the 12 non-notary seats =="

NON_NOTARY_SEATS="qbp-architecture qbp-implementor qbp-oppenheimer qbp-cu-implementor cth-implementor wyrd-implementor bma-implementor contextus-impl herschel edda-implementor deming hutchins"
NEW_DRY_ALL_BUT_NOTARY="$("$HERE/onboard-federation.sh" --dry-run $NON_NOTARY_SEATS 2>&1)"
OLD_DRY_SUBSET="$("$TMPDIR/oldft/onboard-federation.sh" --dry-run $NON_NOTARY_SEATS 2>&1)"
checkeq "$(printf '%s' "$NEW_DRY_ALL_BUT_NOTARY" | md5sum | awk '{print $1}')" "$(printf '%s' "$OLD_DRY_SUBSET" | md5sum | awk '{print $1}')" \
  "onboard-federation.sh --dry-run byte-identical old vs new for all 12 non-notary seats (incl. hutchins)"

# ─────────────────────────────────────────────────────────────────────────
echo "== AC1: golden-render byte-identity (per-persona, full untruncated prompt) =="
extract_fn() { awk -v fn="$1" '$0 ~ "^"fn"\\(\\) \\{" {p=1} p {print} p && /^}/ {exit}' "$2"; }

make_render_wrapper() {  # $1=out-file $2=source-onboard.sh $3=tmpl-file $4=personafile-tmpl(or "")
  {
    echo '#!/usr/bin/env bash'
    echo "TMPL='$3'"
    echo "PERSONAFILE_TMPL='${4:-}'"
    extract_fn role_of "$2"
    extract_fn render "$2"
    echo 'persona="$1"; workdir="$2"; pfile="${3:-}"'
    echo 'role="$(role_of "$persona")"'
    echo 'tmpl="$TMPL"; [ -n "$pfile" ] && tmpl="$PERSONAFILE_TMPL"'
    echo 'render "$persona" "$workdir" "$role" "$tmpl" "$pfile"'
  } > "$1"
  chmod +x "$1"
}

make_render_wrapper "$TMPDIR/render_old.sh" "$TMPDIR/oldft/onboard-federation.sh" "$TMPDIR/old-onboard-prompt.tmpl" ""
make_render_wrapper "$TMPDIR/render_new.sh" "$HERE/onboard-federation.sh" "$HERE/onboard-prompt.tmpl" "$HERE/onboard-prompt-personafile.tmpl"

all_ident=0
for p in qbp-architecture:/home/prime/Documents/inter \
         qbp-implementor:/home/prime/Documents/QBP-implementor \
         qbp-oppenheimer:/home/prime/Documents/QBP \
         qbp-cu-implementor:/home/prime/Documents/QBP-Compute-Unit \
         cth-implementor:/home/prime/Documents/CTH \
         wyrd-implementor:/home/prime/Documents/Wyrd \
         bma-implementor:/home/prime/Documents/BMA \
         contextus-impl:/home/prime/Documents/Contextus \
         herschel:/home/prime/Documents/herschel \
         edda-implementor:/home/prime/Documents/Edda \
         deming:/home/prime/Documents \
         hutchins:/home/prime/Documents/Craft; do
  handle="${p%%:*}"; wd="${p##*:}"
  old_out="$("$TMPDIR/render_old.sh" "$handle" "$wd" "")"
  new_out="$("$TMPDIR/render_new.sh" "$handle" "$wd" "")"
  if [ "$old_out" != "$new_out" ]; then
    echo "    ✗ $handle differs"; all_ident=1
  fi
done
check "$all_ident" "all 12 non-notary personas (incl. hutchins): full rendered prompt byte-identical old vs new"

NOTARY_NEW="$("$TMPDIR/render_new.sh" notary-implementor /home/prime/Documents/notary "$REAL_PATH")"
case "$NOTARY_NEW" in
  *"$REAL_PATH"*"§0"*) check 0 "notary render names the persona-file path AND '§0'" ;;
  *) check 1 "notary render names the persona-file path AND '§0'" ;;
esac

echo "== Golden: both templates literally instruct 'git show origin/main:<path>' (that instruction IS the runtime property — §I4) =="
grep -q 'git show origin/main:{{PERSONA_FILE}}' "$HERE/onboard-prompt-personafile.tmpl" \
  && check 0 "onboard-prompt-personafile.tmpl source contains the literal git-show-origin/main instruction" \
  || check 1 "onboard-prompt-personafile.tmpl source contains the literal git-show-origin/main instruction"
grep -q 'git show origin/main:{{PERSONA_FILE}}' "$HERE/resume-reanchor-prompt.tmpl" \
  && check 0 "resume-reanchor-prompt.tmpl source contains the literal git-show-origin/main instruction" \
  || check 1 "resume-reanchor-prompt.tmpl source contains the literal git-show-origin/main instruction"
case "$NOTARY_NEW" in
  *"git show origin/main:$REAL_PATH"*) check 0 "RENDERED onboard prompt contains the literal 'git show origin/main:$REAL_PATH' instruction" ;;
  *) check 1 "RENDERED onboard prompt contains the literal 'git show origin/main:$REAL_PATH' instruction" ;;
esac
REANCHOR_GOLDEN="$(sed -e "s#{{HANDLE}}#notary-implementor#g" -e "s#{{WORKDIR}}#/home/prime/Documents/notary#g" -e "s#{{PERSONA_FILE}}#$REAL_PATH#g" "$HERE/resume-reanchor-prompt.tmpl" | tr -d '\n')"
case "$REANCHOR_GOLDEN" in
  *"git show origin/main:$REAL_PATH"*) check 0 "RENDERED resume re-anchor contains the literal 'git show origin/main:$REAL_PATH' instruction" ;;
  *) check 1 "RENDERED resume re-anchor contains the literal 'git show origin/main:$REAL_PATH' instruction" ;;
esac

# ─────────────────────────────────────────────────────────────────────────
echo "== AC2 / §I4 M1+M1b: origin/main resolution DRIVES resolve_persona_file (real function, not reimplemented); never a worktree copy; fails loud =="
# source launch-federation.sh's functions without running cmd_launch/list/etc
# — the BASH_SOURCE-vs-$0 guard added at the bottom of the file (inter#142)
# skips the case-dispatch entirely whenever the file is sourced rather than
# executed, regardless of MODE's resolved value.
source "$HERE/launch-federation.sh"

resolve_persona_file "$REAL_PATH" >/dev/null 2>&1
check "$?" "resolve_persona_file succeeds for a real origin/main path ($REAL_PATH)"

resolve_persona_file "prompt/this-file-does-not-exist-142.md" >/tmp/ac2_badpath.$$ 2>&1
rc=$?
grep -q "this-file-does-not-exist-142.md" /tmp/ac2_badpath.$$ && namedok=0 || namedok=1
[ "$rc" -ne 0 ] && [ "$namedok" -eq 0 ] && check 0 "unknown path: non-zero AND names the path" || check 1 "unknown path: non-zero AND names the path"
rm -f /tmp/ac2_badpath.$$

PATH="/nonexistent-$$" resolve_persona_file "$REAL_PATH" >/tmp/ac2_nogit.$$ 2>&1
rc=$?
grep -qi "git not available" /tmp/ac2_nogit.$$ && loudok=0 || loudok=1
[ "$rc" -ne 0 ] && [ "$loudok" -eq 0 ] && check 0 "git unavailable: fails loud, non-zero, no silent fallback" || check 1 "git unavailable: fails loud, non-zero, no silent fallback"
rm -f /tmp/ac2_nogit.$$

# §I4 M1/M1b mutation-kill: the old test called `git show origin/main` ITSELF
# and never called resolve_persona_file — it proved git works, not that the
# launcher uses origin/main (mutant `git show origin/main:$path` -> `cat
# "$INTER_REPO/$path"` SURVIVED). The fix: a throwaway DETACHED git worktree
# at origin/main (shares this repo's object db/refs — never touches the real
# tracked working tree, satisfying N2), diverged on disk WITHOUT committing,
# then resolve_persona_file is called with INTER_REPO pointed at it and the
# REAL function's return code is asserted. Two directions, both required to
# kill the mutant:
#   Test A: a path that exists ONLY in the local worktree (untracked,
#            absent from origin/main) — real code MUST FAIL (git show
#            origin/main can't find it); mutant `cat` would SUCCEED.
#   Test B: a path that exists at origin/main but is DELETED from the local
#            worktree (uncommitted rm) — real code MUST SUCCEED (git show
#            reads the object db, independent of working-tree state);
#            mutant `cat` would FAIL (no such file).
# Asserting both directions means a mutant surviving one is still caught by
# the other — this is what M1 requires ("drive the real code path").
DIVERGE_WT="$TMPDIR/diverge-worktree"
git -C "$INTER_REPO" worktree add --detach "$DIVERGE_WT" origin/main >/tmp/wt_add.$$ 2>&1
if [ $? -ne 0 ]; then
  check 1 "M1 setup: throwaway detached worktree at origin/main created"
  cat /tmp/wt_add.$$
else
  check 0 "M1 setup: throwaway detached worktree at origin/main created"
fi
rm -f /tmp/wt_add.$$

LOCAL_ONLY_PATH="prompt/zz-mutation-test-local-only-$$.md"
mkdir -p "$(dirname "$DIVERGE_WT/$LOCAL_ONLY_PATH")"
echo "local-only content, never committed, never at origin/main" > "$DIVERGE_WT/$LOCAL_ONLY_PATH"

ORIG_INTER_REPO="$INTER_REPO"
INTER_REPO="$DIVERGE_WT"
resolve_persona_file "$LOCAL_ONLY_PATH" >/tmp/m1_a.$$ 2>&1
rc_a=$?
[ "$rc_a" -ne 0 ] && check 0 "§I4 M1 kill (launch-federation.sh) Test A: path exists ONLY in local worktree -> resolve_persona_file FAILS (real git-show-origin/main; a 'cat local worktree' mutant would wrongly SUCCEED here)" \
  || check 1 "§I4 M1 kill (launch-federation.sh) Test A: path exists ONLY in local worktree -> resolve_persona_file FAILS (real git-show-origin/main; a 'cat local worktree' mutant would wrongly SUCCEED here)"
rm -f /tmp/m1_a.$$ "$DIVERGE_WT/$LOCAL_ONLY_PATH"

rm -f "$DIVERGE_WT/$REAL_PATH"
resolve_persona_file "$REAL_PATH" >/tmp/m1_b.$$ 2>&1
rc_b=$?
[ "$rc_b" -eq 0 ] && check 0 "§I4 M1 kill (launch-federation.sh) Test B: path DELETED locally but present at origin/main -> resolve_persona_file SUCCEEDS (real git-show-origin/main reads the object db; a 'cat local worktree' mutant would wrongly FAIL here)" \
  || { check 1 "§I4 M1 kill (launch-federation.sh) Test B: path DELETED locally but present at origin/main -> resolve_persona_file SUCCEEDS (real git-show-origin/main reads the object db; a 'cat local worktree' mutant would wrongly FAIL here)"; cat /tmp/m1_b.$$; }
rm -f /tmp/m1_b.$$
git -C "$DIVERGE_WT" checkout -- "$REAL_PATH" 2>/dev/null
INTER_REPO="$ORIG_INTER_REPO"

# §I4 M1b: the identical mutation in onboard-federation.sh's OWN copy of
# resolve_persona_file — source it in a subshell (it has its own top-level
# flow, so isolate via a subshell rather than double-sourcing into this one).
M1B_RESULT="$(
  source "$HERE/onboard-federation.sh" --dry-run deming >/dev/null 2>&1 || true
  INTER_REPO="$DIVERGE_WT"
  mkdir -p "$(dirname "$DIVERGE_WT/$LOCAL_ONLY_PATH")"
  echo "local-only" > "$DIVERGE_WT/$LOCAL_ONLY_PATH"
  resolve_persona_file "$LOCAL_ONLY_PATH" >/dev/null 2>&1
  rc_a=$?
  rm -f "$DIVERGE_WT/$LOCAL_ONLY_PATH"
  rm -f "$DIVERGE_WT/$REAL_PATH"
  resolve_persona_file "$REAL_PATH" >/dev/null 2>&1
  rc_b=$?
  git -C "$DIVERGE_WT" checkout -- "$REAL_PATH" 2>/dev/null
  echo "$rc_a $rc_b"
)"
M1B_A="$(echo "$M1B_RESULT" | awk '{print $1}')"
M1B_B="$(echo "$M1B_RESULT" | awk '{print $2}')"
[ "$M1B_A" != "0" ] && check 0 "§I4 M1b kill (onboard-federation.sh) Test A: local-only path -> resolve_persona_file FAILS" \
  || check 1 "§I4 M1b kill (onboard-federation.sh) Test A: local-only path -> resolve_persona_file FAILS"
[ "$M1B_B" = "0" ] && check 0 "§I4 M1b kill (onboard-federation.sh) Test B: path deleted locally, present at origin/main -> resolve_persona_file SUCCEEDS" \
  || check 1 "§I4 M1b kill (onboard-federation.sh) Test B: path deleted locally, present at origin/main -> resolve_persona_file SUCCEEDS"

# ─────────────────────────────────────────────────────────────────────────
echo "== §I4 D2: origin/main freshness — fetch before resolution; stale ref resolves to newer, or fails loud =="
# Fully isolated sandbox (bare repo + 3 local clones) — never touches the
# real ~/Documents/inter repo/worktrees or any shared ref.
D2_REMOTE="$TMPDIR/d2-remote.git"
git init -q --bare "$D2_REMOTE"
D2_SEED="$TMPDIR/d2-seed"
git clone -q "$D2_REMOTE" "$D2_SEED"
(
  cd "$D2_SEED"
  git checkout -q -b main 2>/dev/null || git checkout -q main
  echo "v1" > testfile.md
  git add testfile.md
  git -c user.email=t@t.test -c user.name=tester commit -q -m v1
  git push -q origin main
)
# "the launcher's repo" — clones v1, does NOT re-fetch before the remote moves
D2_LAUNCHER_REPO="$TMPDIR/d2-launcher-repo"
git clone -q "$D2_REMOTE" "$D2_LAUNCHER_REPO"
# a third clone pushes v2 directly to the bare remote, simulating someone
# else's merge landing on main after the launcher's last fetch
D2_PUSHER="$TMPDIR/d2-pusher"
git clone -q "$D2_REMOTE" "$D2_PUSHER"
(
  cd "$D2_PUSHER"
  git checkout -q main 2>/dev/null || git checkout -q -b main origin/main
  echo "v2" > testfile.md
  git add testfile.md
  git -c user.email=t@t.test -c user.name=tester commit -q -m v2
  git push -q origin main
)

ORIG_INTER_REPO="$INTER_REPO"
INTER_REPO="$D2_LAUNCHER_REPO"; ORIGIN_MAIN_FRESH=0
ensure_origin_main_fresh
CONTENT_BEFORE_ARG="$(git -C "$D2_LAUNCHER_REPO" show origin/main:testfile.md 2>/dev/null)"
checkeq "$CONTENT_BEFORE_ARG" "v2" "D2: ensure_origin_main_fresh() fetches; local ref resolves to the NEWER remote content, not the stale-at-clone-time v1"

# fail-loud path: point origin at a nonexistent remote, force the fetch to fail
D2_BADREMOTE_REPO="$TMPDIR/d2-badremote-repo"
git clone -q "$D2_REMOTE" "$D2_BADREMOTE_REPO"
git -C "$D2_BADREMOTE_REPO" remote set-url origin "$TMPDIR/does-not-exist-remote-$$"
INTER_REPO="$D2_BADREMOTE_REPO"; ORIGIN_MAIN_FRESH=0
ensure_origin_main_fresh >/tmp/d2_fail.$$ 2>&1
rc=$?
grep -qi "FETCH FAILED" /tmp/d2_fail.$$ && loud=0 || loud=1
grep -Eq '[0-9]+s old' /tmp/d2_fail.$$ && namesage=0 || namesage=1
[ "$rc" -ne 0 ] && [ "$loud" -eq 0 ] && [ "$namesage" -eq 0 ] && check 0 "D2: fetch failure fails loud (non-zero, names 'FETCH FAILED' + local ref age), no silent stale-ref use" \
  || { check 1 "D2: fetch failure fails loud (non-zero, names 'FETCH FAILED' + local ref age), no silent stale-ref use"; cat /tmp/d2_fail.$$; }
rm -f /tmp/d2_fail.$$
INTER_REPO="$ORIG_INTER_REPO"; ORIGIN_MAIN_FRESH=0

# smoke-check onboard-federation.sh carries the identical contract (subshell,
# reusing the same D2 fixtures — cheap, no need to rebuild the remote)
D2_ONBOARD_RESULT="$(
  source "$HERE/onboard-federation.sh" --dry-run deming >/dev/null 2>&1 || true
  INTER_REPO="$D2_LAUNCHER_REPO"; ORIGIN_MAIN_FRESH=0
  ensure_origin_main_fresh >/dev/null 2>&1
  echo $?
)"
checkeq "$D2_ONBOARD_RESULT" "0" "D2 (onboard-federation.sh): ensure_origin_main_fresh() present and succeeds against the same fixture"

# ─────────────────────────────────────────────────────────────────────────
echo "== AC3 / §I4 M2: resume re-anchor mechanism drives the REAL cmd_launch gate (build_launch_plan), not a reimplementation =="
TESTSESSION="fed-test-142-$$"
FAKEDIR="$TMPDIR/fake-notary-workdir"
mkdir -p "$FAKEDIR"
tmux kill-session -t "$TESTSESSION" 2>/dev/null
tmux new-session -d -s "$TESTSESSION" -c "$FAKEDIR" "bash --norc --noprofile"
tmux send-keys -t "$TESTSESSION" "PS1='❯ '; clear" C-m
sleep 1

SESSION="$TESTSESSION"; READY_TIMEOUT=10
send_resume_reanchor "notary-implementor" "$FAKEDIR" "$REAL_PATH" >/tmp/ac3.$$ 2>&1
sleep 0.5
PANE_CONTENT="$(tmux capture-pane -p -t "$TESTSESSION" 2>/dev/null)"
tmux kill-session -t "$TESTSESSION" 2>/dev/null

if printf '%s' "$PANE_CONTENT" | grep -q "Resume re-anchor" && printf '%s' "$PANE_CONTENT" | grep -q "$REAL_PATH" && printf '%s' "$PANE_CONTENT" | grep -q '§0'; then
  check 0 "resumed pane WITH persona-file receives the re-anchor send-keys (names path + §0)"
else
  check 1 "resumed pane WITH persona-file receives the re-anchor send-keys (names path + §0)"
  cat /tmp/ac3.$$
fi
rm -f /tmp/ac3.$$

# §I4 M2 kill: drive the REAL gate. cmd_launch's per-pane decision logic was
# factored into build_launch_plan() (called by cmd_launch itself, unchanged
# behavior) precisely so this test can call the SAME function instead of
# reimplementing `[ -n "$sid" ] && [ -n "$pfile" ]` inline. Covers the full
# SID x PFILE truth table, including the "sid pinned but no matching
# transcript file -> falls to FRESH, never reanchored" case cmd_launch
# actually implements.
FAKE_PROJDIR="$TMPDIR/fake-projects"
mkdir -p "$FAKE_PROJDIR"
HAS_SESSION_WD="$TMPDIR/has-session-wd"; mkdir -p "$HAS_SESSION_WD"
HAS_SESSION_SID="deadbeef-0000-0000-0000-m2session001"
mkdir -p "$FAKE_PROJDIR/$(slug_of "$HAS_SESSION_WD")"
: > "$FAKE_PROJDIR/$(slug_of "$HAS_SESSION_WD")/$HAS_SESSION_SID.jsonl"
NO_SESSION_WD="$TMPDIR/no-session-wd"; mkdir -p "$NO_SESSION_WD"
NO_SESSION_SID="deadbeef-0000-0000-0000-m2missingfil"

ORIG_PROJECTS="$PROJECTS"
PROJECTS="$FAKE_PROJDIR"
P_PERSONA=(resumed-no-pfile resumed-with-pfile pinned-no-transcript fresh-already)
P_WORKDIR=("$HAS_SESSION_WD" "$HAS_SESSION_WD" "$NO_SESSION_WD" "$HAS_SESSION_WD")
P_SID=("$HAS_SESSION_SID" "$HAS_SESSION_SID" "$NO_SESSION_SID" "")
P_PFILE=("" "$REAL_PATH" "$REAL_PATH" "$REAL_PATH")
build_launch_plan >/tmp/m2.$$ 2>&1

in_array() { local needle="$1"; shift; local x; for x in "$@"; do [ "$x" = "$needle" ] && return 0; done; return 1; }

in_array "resumed-no-pfile" "${REANCHOR_PERSONA[@]:-}" && r1=0 || r1=1
[ "$r1" -eq 1 ] && check 0 "M2 kill: resumed pane WITHOUT persona-file -> NOT added to the real cmd_launch reanchor plan" \
  || check 1 "M2 kill: resumed pane WITHOUT persona-file -> NOT added to the real cmd_launch reanchor plan"

in_array "resumed-with-pfile" "${REANCHOR_PERSONA[@]:-}" && r2=0 || r2=1
[ "$r2" -eq 0 ] && check 0 "M2: resumed pane WITH persona-file -> IS added to the real cmd_launch reanchor plan" \
  || check 1 "M2: resumed pane WITH persona-file -> IS added to the real cmd_launch reanchor plan"

in_array "pinned-no-transcript" "${REANCHOR_PERSONA[@]:-}" && r3=1 || r3=0
in_array "pinned-no-transcript" "${FRESH[@]:-}" && r3f=0 || r3f=1
[ "$r3" -eq 0 ] && [ "$r3f" -eq 0 ] && check 0 "M2: pinned sid with NO matching transcript file -> cleared to FRESH by the real gate, never reanchored (not a reimplementation: build_launch_plan did the clearing)" \
  || check 1 "M2: pinned sid with NO matching transcript file -> cleared to FRESH by the real gate, never reanchored"

in_array "fresh-already" "${FRESH[@]:-}" && r4=0 || r4=1
[ "$r4" -eq 0 ] && check 0 "M2: already-fresh (no sid) row -> in FRESH plan" || check 1 "M2: already-fresh (no sid) row -> in FRESH plan"

PROJECTS="$ORIG_PROJECTS"
rm -f /tmp/m2.$$

# "WITHOUT -> nothing new (unchanged)" via the exact production boolean too
wants_resume_reanchor "deadbeef" "" && w1=0 || w1=1
[ "$w1" -eq 1 ] && check 0 "wants_resume_reanchor: sid set, pfile empty -> false (same boolean cmd_launch calls)" || check 1 "wants_resume_reanchor: sid set, pfile empty -> false"
wants_resume_reanchor "deadbeef" "$REAL_PATH" && w2=0 || w2=1
[ "$w2" -eq 0 ] && check 0 "wants_resume_reanchor: sid set, pfile set -> true" || check 1 "wants_resume_reanchor: sid set, pfile set -> true"
wants_resume_reanchor "" "$REAL_PATH" && w3=0 || w3=1
[ "$w3" -eq 1 ] && check 0 "wants_resume_reanchor: sid empty (fresh, not resumed) -> false" || check 1 "wants_resume_reanchor: sid empty (fresh, not resumed) -> false"

# ─────────────────────────────────────────────────────────────────────────
echo "== AC4: drift-check — byte-identical passes; 1-byte mutation fails loud, naming the file =="
CANON="$(git -C "$INTER_REPO" show "origin/main:$REAL_PATH")"
CANON_BLOCK="$(printf '%s' "$CANON" | awk '
  BEGIN{in_section=0;in_fence=0}
  /^## The prompt/ {in_section=1; next}
  in_section && /^```/ { if (in_fence) exit; else { in_fence=1; next } }
  in_fence { print }
')"

COPY="$TMPDIR/runtime-copy.md"
SHA="$(git -C "$INTER_REPO" rev-parse origin/main)"
{
  printf '<!-- GENERATED from JamesPagetButler/inter %s @ %s — do not edit; regenerate -->\n\n' "$REAL_PATH" "$SHA"
  printf '%s' "$CANON_BLOCK"
} > "$COPY"

"$HERE/check-persona-drift.sh" "$REAL_PATH" "$COPY" >/tmp/ac4_ok.$$ 2>&1
check "$?" "byte-identical runtime copy: exit 0"
rm -f /tmp/ac4_ok.$$

COPY_FM="$TMPDIR/runtime-copy-with-frontmatter.md"
{
  printf -- '---\nname: notary-implementor\ndescription: test\n---\n'
  printf '<!-- GENERATED from JamesPagetButler/inter %s @ %s — do not edit; regenerate -->\n\n' "$REAL_PATH" "$SHA"
  printf '%s' "$CANON_BLOCK"
} > "$COPY_FM"
"$HERE/check-persona-drift.sh" "$REAL_PATH" "$COPY_FM" >/tmp/ac4_fm.$$ 2>&1
check "$?" "header + frontmatter excluded from comparison: exit 0 despite different wrapper"
rm -f /tmp/ac4_fm.$$

COPY_MUT="$TMPDIR/runtime-copy-mutated.md"
cp "$COPY" "$COPY_MUT"
python3 - "$COPY_MUT" <<'PYEOF'
import sys
p = sys.argv[1]
b = bytearray(open(p, "rb").read())
lines = b.split(b"\n")
for i in range(2, len(lines)):
    line = bytearray(lines[i])
    changed = False
    for j, ch in enumerate(line):
        if 97 <= ch <= 122:  # a-z
            line[j] = ch - 32  # uppercase it: a 1-byte mutation
            changed = True
            break
    if changed:
        lines[i] = bytes(line)
        break
open(p, "wb").write(b"\n".join(lines))
PYEOF
"$HERE/check-persona-drift.sh" "$REAL_PATH" "$COPY_MUT" >/tmp/ac4_mut.$$ 2>&1
rc=$?
grep -q "$COPY_MUT" /tmp/ac4_mut.$$ && namedok=0 || namedok=1
[ "$rc" -ne 0 ] && [ "$namedok" -eq 0 ] && check 0 "1-byte body mutation: non-zero exit, names the drifted file" || check 1 "1-byte body mutation: non-zero exit, names the drifted file"
cat /tmp/ac4_mut.$$ | sed 's/^/    /'
rm -f /tmp/ac4_mut.$$

echo "== §I4 N1: extract_prompt_block guard — an inner-fence-truncated block (no §0) fails loud instead of silently comparing partial content =="
# check-persona-drift.sh now also enforces D2 (fetch origin main first), so
# the fixture needs a REAL origin remote, not a bare `git init`.
N1_REMOTE="$TMPDIR/n1-remote.git"
git init -q --bare "$N1_REMOTE"
N1_REPO="$TMPDIR/n1-repo"
git clone -q "$N1_REMOTE" "$N1_REPO"
git -C "$N1_REPO" checkout -q -b main 2>/dev/null || git -C "$N1_REPO" checkout -q main
mkdir -p "$N1_REPO/prompt"
{
  echo "# Fake persona (N1 fixture)"
  echo
  echo "## The prompt"
  echo
  echo '```'
  echo "Intro line before an inner fence — this is all extract_prompt_block will see."
  echo '```yaml'
  echo "key: value"
  echo '```'
  echo '§0 Identity check — never reached, because the block already truncated above.'
  echo '```'
} > "$N1_REPO/prompt/fake-persona.md"
git -C "$N1_REPO" add -A
git -C "$N1_REPO" -c user.email=t@t.test -c user.name=tester commit -q -m "N1 fixture: inner-fence-truncated prompt block"
git -C "$N1_REPO" push -q origin main

N1_COPY="$TMPDIR/n1-copy.md"
: > "$N1_COPY"
INTER_REPO_DIR="$N1_REPO" "$HERE/check-persona-drift.sh" "prompt/fake-persona.md" "$N1_COPY" >/tmp/n1.$$ 2>&1
rc=$?
grep -qi '§0' /tmp/n1.$$ && named0=0 || named0=1
[ "$rc" -eq 2 ] && [ "$named0" -eq 0 ] && check 0 "N1 guard: inner-fence truncation (no §0 in extracted block) -> fails loud, exit 2, names '§0'" \
  || { check 1 "N1 guard: inner-fence truncation (no §0 in extracted block) -> fails loud, exit 2, names '§0'"; cat /tmp/n1.$$ | sed 's/^/    /'; }
rm -f /tmp/n1.$$
# and confirm it's NOT a false positive against the real, well-formed (v0.2,
# no-inner-fences) notary block already proven byte-identical above.
case "$CANON_BLOCK" in
  *'§0'*) check 0 "N1 guard: NOT a false positive — the real notary prompt block (no inner fences) contains §0 and passes" ;;
  *) check 1 "N1 guard: NOT a false positive — the real notary prompt block (no inner fences) contains §0 and passes" ;;
esac

# ─────────────────────────────────────────────────────────────────────────
echo "== Backward compatibility: personas.conf rows with no 4th column still parse and launch =="
FIXTURE="$TMPDIR/personas-backcompat.conf"
cat > "$FIXTURE" <<EOF
alpha-persona | /tmp/alpha-wd | AUTO
beta-persona  | /tmp/beta-wd  | some-fixed-sid-1234
EOF
unset P_PERSONA P_WORKDIR P_SID P_PFILE 2>/dev/null
declare -a P_PERSONA=() P_WORKDIR=() P_SID=() P_PFILE=()
CONF="$FIXTURE"
LOCAL_CONF="/nonexistent-overlay-backcompat-$$.conf"
ROSTER="/nonexistent-roster-$$"
load_conf
ok=1
[ "${#P_PERSONA[@]}" -eq 2 ] || ok=0
[ "${P_PERSONA[0]}" = "alpha-persona" ] || ok=0
[ "${P_WORKDIR[1]}" = "/tmp/beta-wd" ] || ok=0
[ "${P_SID[1]}" = "some-fixed-sid-1234" ] || ok=0
[ -z "${P_PFILE[0]}" ] || ok=0
[ -z "${P_PFILE[1]}" ] || ok=0
[ "$ok" = "1" ] && check 0 "3-column rows parse correctly (persona/workdir/sid intact, pfile empty)" || check 1 "3-column rows parse correctly (persona/workdir/sid intact, pfile empty)"

# ─────────────────────────────────────────────────────────────────────────
echo "== AC6: an overlay pin for a seat wins over its structural AUTO =="
# Hermetic: use a fake empty $PROJECTS dir (not the real ~/.claude/projects)
# so AUTO-discovery's content-sniff can never coincidentally reproduce the
# same value this machine's real history happens to carry — a genuine
# resolution here can ONLY have come from the overlay.
AC6_FAKE_PROJECTS="$TMPDIR/ac6-fake-projects"; mkdir -p "$AC6_FAKE_PROJECTS"
AC6_WD="$TMPDIR/ac6-fake-qbp-wd"; mkdir -p "$AC6_WD"
AC6_CONF="$TMPDIR/personas-ac6.conf"
cat > "$AC6_CONF" <<EOF
qbp-oppenheimer | $AC6_WD | AUTO
EOF
AC6_OVERLAY="$TMPDIR/personas-ac6.local.conf"
printf 'qbp-oppenheimer | %s\n' "$OPPENHEIMER_PIN" > "$AC6_OVERLAY"
ORIG_PROJECTS_AC="$PROJECTS"; PROJECTS="$AC6_FAKE_PROJECTS"
unset P_PERSONA P_WORKDIR P_SID P_PFILE 2>/dev/null
declare -a P_PERSONA=() P_WORKDIR=() P_SID=() P_PFILE=()
CONF="$AC6_CONF"; LOCAL_CONF="$AC6_OVERLAY"; ROSTER="/nonexistent-roster-ac6-$$"
load_conf
checkeq "${P_SID[0]}" "$OPPENHEIMER_PIN" "AC6: overlay pin wins over structural AUTO (roster + content-sniff both hermetically empty — proves the overlay, not a coincidental match, supplied the sid)"

echo "== AC7: missing/empty overlay => AUTO resolution for all seats (backward-compat: no overlay = today's behavior) =="
unset P_PERSONA P_WORKDIR P_SID P_PFILE 2>/dev/null
declare -a P_PERSONA=() P_WORKDIR=() P_SID=() P_PFILE=()
CONF="$AC6_CONF"
LOCAL_CONF="/nonexistent-overlay-ac7-$$.conf"
ROSTER="/nonexistent-roster-ac7-$$"
load_conf
checkeq "${P_SID[0]}" "" "AC7: missing overlay file => falls through to ordinary AUTO discovery (empty here: no roster match, no jsonl to content-sniff) — unchanged backward-compat behavior"

: > "$AC6_OVERLAY.empty"
unset P_PERSONA P_WORKDIR P_SID P_PFILE 2>/dev/null
declare -a P_PERSONA=() P_WORKDIR=() P_SID=() P_PFILE=()
CONF="$AC6_CONF"; LOCAL_CONF="$AC6_OVERLAY.empty"; ROSTER="/nonexistent-roster-ac7b-$$"
load_conf
checkeq "${P_SID[0]}" "" "AC7: EMPTY (present but zero-entry) overlay file => same as missing — AUTO for all seats"
PROJECTS="$ORIG_PROJECTS_AC"

echo "== Content-sniff: a transcript dominated by 'hutchins' mentions resolves to the hutchins seat (inter#143 C1 item 1, qbp-architecture §I4 — hutchins is a committed roster seat, FED_HANDLES now carries |hutchins so AUTO content-sniff can match it) =="
# Hermetic, same shape as AC6/AC7: fake PROJECTS dir, real discover_sid (not a
# reimplementation). A jsonl fixture where 'hutchins' is the DOMINANT handle
# (more mentions than any other federation handle) must resolve to hutchins —
# proving |hutchins is live in the FED_HANDLES grep alternation, not just
# declared in a comment.
CS_FAKE_PROJECTS="$TMPDIR/cs-fake-projects"; mkdir -p "$CS_FAKE_PROJECTS"
CS_WD="$TMPDIR/cs-fake-craft-wd"; mkdir -p "$CS_WD"
CS_PDIR="$CS_FAKE_PROJECTS/$(slug_of "$CS_WD")"
mkdir -p "$CS_PDIR"
CS_SID="deadbeef-0000-0000-0000-cshutchins01"
cat > "$CS_PDIR/$CS_SID.jsonl" <<'EOF'
{"role":"user","text":"@hutchins please pick up the render pipeline task"}
{"role":"assistant","text":"hutchins here, on it"}
{"role":"user","text":"thanks hutchins — one more thing for hutchins"}
EOF
ORIG_PROJECTS_CS="$PROJECTS"; PROJECTS="$CS_FAKE_PROJECTS"
CS_RESULT="$(discover_sid "hutchins" "$CS_WD")"
PROJECTS="$ORIG_PROJECTS_CS"
checkeq "$CS_RESULT" "$CS_SID" "content-sniff: pane content dominated by 'hutchins' mentions resolves to the hutchins seat via discover_sid (hermetic fixture, no roster match — content-sniff alone supplied the sid)"

echo "== Overlay split: tracked personas.conf is pin-free (grep-assert zero session-id pins) =="
PINS="$(awk -F'|' '
  { line=$0; sub(/#.*/, "", line); if (line ~ /^[[:space:]]*$/) next }
  { n=split(line, f, "|"); if (n<3) next; sid=f[3]; gsub(/^[ \t]+|[ \t]+$/, "", sid); if (sid != "" && sid != "AUTO") print f[1] ": " sid }
' "$HERE/personas.conf")"
if [ -z "$PINS" ]; then
  check 0 "tracked personas.conf: zero session-id pins (all-AUTO; overlay carries every ephemeral pin, incl. the moved qbp-oppenheimer $OPPENHEIMER_PIN)"
else
  check 1 "tracked personas.conf: zero session-id pins (all-AUTO; overlay carries every ephemeral pin)"
  echo "$PINS" | sed 's/^/    still pinned: /'
fi

echo "== Overlay: refresh writes discovered pins to personas.local.conf ONLY — personas.conf is never rewritten =="
REFRESH_CONF="$TMPDIR/personas-refresh.conf"
cat > "$REFRESH_CONF" <<EOF
gamma-persona        | /tmp/gamma-wd-$$                | AUTO
notary-implementor   | /tmp/notary-wd-$$               | AUTO | some/persona-file.md
EOF
BEFORE_HASH="$(md5sum "$REFRESH_CONF" | awk '{print $1}')"
CONF="$REFRESH_CONF"; LOCAL_CONF="$TMPDIR/refresh.local.conf"; ROSTER="/nonexistent-roster-refresh-$$"
rm -f "$LOCAL_CONF"
cmd_refresh >/tmp/refresh_out.$$ 2>&1
AFTER_HASH="$(md5sum "$REFRESH_CONF" | awk '{print $1}')"
checkeq "$AFTER_HASH" "$BEFORE_HASH" "refresh: personas.conf byte-unchanged (structure file never rewritten; pins live only in the overlay)"
[ -f "$LOCAL_CONF" ] && check 0 "refresh: personas.local.conf overlay file created" || check 1 "refresh: personas.local.conf overlay file created"
rm -f /tmp/refresh_out.$$

echo "== Overlay: refresh actually WRITES a discovered pin into the overlay (real discover_sid against a fake roster row) =="
REFRESH2_CONF="$TMPDIR/personas-refresh2.conf"
DELTA_WD="$TMPDIR/delta-wd"; mkdir -p "$DELTA_WD"
cat > "$REFRESH2_CONF" <<EOF
delta-persona | $DELTA_WD | AUTO
EOF
FAKE_ROSTER="$TMPDIR/fake-roster.tsv"
printf 'delta-persona\t%s\tdeadbeef-refresh-0000-0000-000000000000\n' "$DELTA_WD" > "$FAKE_ROSTER"
CONF="$REFRESH2_CONF"; LOCAL_CONF="$TMPDIR/refresh2.local.conf"; ROSTER="$FAKE_ROSTER"
rm -f "$LOCAL_CONF"
cmd_refresh >/tmp/refresh2_out.$$ 2>&1
grep -q "deadbeef-refresh-0000-0000-000000000000" "$LOCAL_CONF" 2>/dev/null \
  && check 0 "refresh: a freshly-discovered (roster-matched) pin lands in the overlay" \
  || { check 1 "refresh: a freshly-discovered (roster-matched) pin lands in the overlay"; cat "$LOCAL_CONF" 2>/dev/null; }
grep -Eq '^delta-persona +\|' "$REFRESH2_CONF" && grep -q ' AUTO' "$REFRESH2_CONF" \
  && check 0 "refresh: personas.conf row for that same persona is STILL AUTO (untouched)" \
  || check 1 "refresh: personas.conf row for that same persona is STILL AUTO (untouched)"
rm -f /tmp/refresh2_out.$$

# ─────────────────────────────────────────────────────────────────────────
echo "== inter#92 (Part A, cutover-prep): resumed pane's command carries CLAUDE_CODE_RETRY_WATCHDOG=1; fresh pane does NOT =="
# resume_cmd() is already live in this shell from the `source` above — driving
# the real function, not a reimplementation of the 429-retry fix.
RESUMED_CMD="$(resume_cmd "some-fake-sid-1234")"
case "$RESUMED_CMD" in
  CLAUDE_CODE_RETRY_WATCHDOG=1\ *--resume\ some-fake-sid-1234)
    check 0 "resumed pane's launch command is prefixed with CLAUDE_CODE_RETRY_WATCHDOG=1 (so a resumed session retries 429/529 instead of dying)" ;;
  *)
    check 1 "resumed pane's launch command is prefixed with CLAUDE_CODE_RETRY_WATCHDOG=1 (got: $RESUMED_CMD)" ;;
esac

FRESH_CMD="$(resume_cmd "")"
case "$FRESH_CMD" in
  CLAUDE_CODE_RETRY_WATCHDOG=1*)
    check 1 "fresh (non-resumed) pane's command does NOT carry the watchdog prefix — nothing to retry (got: $FRESH_CMD)" ;;
  *)
    check 0 "fresh (non-resumed) pane's command does NOT carry the watchdog prefix — nothing to retry" ;;
esac

echo "== inter#92 (Part A, cutover-prep): STAGGER_SECONDS gates the real cmd_launch inter-pane wait (not a reimplementation) =="
STAGGER_TEST_SESSION="fed-test-92-stagger-$$"
STAGGER_CONF="$TMPDIR/personas-stagger.conf"
STAGGER_A_WD="$TMPDIR/stagger-a-wd"; STAGGER_B_WD="$TMPDIR/stagger-b-wd"
mkdir -p "$STAGGER_A_WD" "$STAGGER_B_WD"
cat > "$STAGGER_CONF" <<EOF
stagger-a | $STAGGER_A_WD |
stagger-b | $STAGGER_B_WD |
EOF
STAGGER_FAKE_PROJECTS="$TMPDIR/stagger-fake-projects"; mkdir -p "$STAGGER_FAKE_PROJECTS"
tmux kill-session -t "$STAGGER_TEST_SESSION" 2>/dev/null

# Drives the REAL cmd_launch loop (build_launch_plan + the launch for-loop +
# the stagger sleep inside it), with ONBOARD/REANCHOR disabled and CLAUDE_BIN
# swapped for /bin/true so no onboarding traffic or real `claude` process is
# ever spawned — only the timing of the loop itself is under test. Echoes the
# whole-second elapsed wall time for a 2-persona launch at the given
# STAGGER_SECONDS value.
run_stagger_launch() {
  local secs="$1" start end
  unset P_PERSONA P_WORKDIR P_SID P_PFILE 2>/dev/null
  declare -a P_PERSONA=() P_WORKDIR=() P_SID=() P_PFILE=()
  CONF="$STAGGER_CONF"
  LOCAL_CONF="/nonexistent-overlay-stagger-$$.conf"
  ROSTER="/nonexistent-roster-stagger-$$"
  PROJECTS="$STAGGER_FAKE_PROJECTS"
  WATCHER_DIR="/nonexistent-watcher-dir-$$"
  FED_TMUX_SESSION="$STAGGER_TEST_SESSION"; SESSION="$STAGGER_TEST_SESSION"
  CLAUDE_BIN="/bin/true"
  LAYOUT="panes"
  ONBOARD=0
  REANCHOR=0
  STAGGER_SECONDS="$secs"
  start=$(date +%s)
  cmd_launch >/tmp/stagger_launch.$$ 2>&1
  end=$(date +%s)
  tmux kill-session -t "$STAGGER_TEST_SESSION" 2>/dev/null
  rm -f /tmp/stagger_launch.$$
  echo $(( end - start ))
}

ELAPSED_ON="$(run_stagger_launch 3)"
[ "$ELAPSED_ON" -ge 3 ] \
  && check 0 "STAGGER_SECONDS=3 (nonzero): the real cmd_launch loop actually waits before the 2nd pane (elapsed ${ELAPSED_ON}s >= 3s)" \
  || check 1 "STAGGER_SECONDS=3 (nonzero): the real cmd_launch loop actually waits before the 2nd pane (got ${ELAPSED_ON}s, want >=3s)"

ELAPSED_OFF="$(run_stagger_launch 0)"
[ "$ELAPSED_OFF" -lt 3 ] \
  && check 0 "STAGGER_SECONDS=0 disables the inter-launch wait (elapsed ${ELAPSED_OFF}s < 3s)" \
  || check 1 "STAGGER_SECONDS=0 disables the inter-launch wait (got ${ELAPSED_OFF}s, want <3s)"
STAGGER_TEST_SESSION=""

echo
echo "RESULT: $pass passed, $fail failed"
exit $([ "$fail" -eq 0 ] && echo 0 || echo 1)
