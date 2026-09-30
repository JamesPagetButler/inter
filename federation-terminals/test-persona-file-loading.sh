#!/usr/bin/env bash
#
# test-persona-file-loading.sh — unit/golden-file tests for inter#142
# (persona-file loading on launch/resume). Covers qbp-architecture's
# acceptance tests AC1-AC5. These are "unit/golden tests with fake panes" per
# the issue's stated verification boundary — the true acceptance evidence
# (a live Notary-pane restart) is a separate, post-merge, beekeeper-timed step
# and is NOT what this script attempts.
#
# Touches NO real federation state: it never targets the real "fed" tmux
# session, never calls sessionbridge, and any working-tree edit it makes to
# prove the origin/main-vs-worktree distinction (AC2) is reverted before exit
# (trap, runs even on failure/interrupt).
#
# Usage: ./test-persona-file-loading.sh
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTER_REPO="$(cd "$HERE/.." && pwd)"
TMPDIR="$(mktemp -d)"
REVERT_FILE=""
cleanup() {
  [ -n "$REVERT_FILE" ] && git -C "$INTER_REPO" checkout -- "$REVERT_FILE" 2>/dev/null
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

pass=0; fail=0
check() { if [ "$1" = "0" ]; then echo "  ✓ $2"; pass=$((pass+1)); else echo "  ✗ $2"; fail=$((fail+1)); fi; }
checkeq() { if [ "$1" = "$2" ]; then echo "  ✓ $3"; pass=$((pass+1)); else echo "  ✗ $3 (got [$1], want [$2])"; fail=$((fail+1)); fi; }

# ─────────────────────────────────────────────────────────────────────────
echo "== setup: origin/main baseline copy (old script + old conf side by side, so each resolves its OWN default CONF) =="
git -C "$INTER_REPO" show origin/main:federation-terminals/launch-federation.sh  > "$TMPDIR/old-launch.sh"
git -C "$INTER_REPO" show origin/main:federation-terminals/onboard-federation.sh > "$TMPDIR/old-onboard.sh"
git -C "$INTER_REPO" show origin/main:federation-terminals/onboard-prompt.tmpl   > "$TMPDIR/old-onboard-prompt.tmpl"
git -C "$INTER_REPO" show origin/main:federation-terminals/personas.conf        > "$TMPDIR/old-personas.conf"
git -C "$INTER_REPO" show origin/main:federation-terminals/deming-boot.tmpl     > "$TMPDIR/deming-boot.tmpl" 2>/dev/null
mkdir -p "$TMPDIR/oldft"
cp "$TMPDIR/old-launch.sh" "$TMPDIR/oldft/launch-federation.sh"
cp "$TMPDIR/old-onboard.sh" "$TMPDIR/oldft/onboard-federation.sh"
cp "$TMPDIR/old-onboard-prompt.tmpl" "$TMPDIR/oldft/onboard-prompt.tmpl"
cp "$TMPDIR/old-personas.conf" "$TMPDIR/oldft/personas.conf"
[ -f "$TMPDIR/deming-boot.tmpl" ] && cp "$TMPDIR/deming-boot.tmpl" "$TMPDIR/oldft/deming-boot.tmpl"
chmod +x "$TMPDIR/oldft/launch-federation.sh" "$TMPDIR/oldft/onboard-federation.sh"

echo "== AC5 (part 1/2): launch-federation.sh 'list' output unchanged =="
# each script run with its OWN default (same-dir) personas.conf: old-vs-old-conf,
# new-vs-new-conf — cmd_list's printed columns don't include persona_file, so
# adding that 4th column to notary's row must not change this output at all.
OLD_LIST="$("$TMPDIR/oldft/launch-federation.sh" list 2>&1)"
NEW_LIST="$("$HERE/launch-federation.sh" list 2>&1)"
checkeq "$(printf '%s' "$NEW_LIST" | md5sum | awk '{print $1}')" "$(printf '%s' "$OLD_LIST" | md5sum | awk '{print $1}')" \
  "launch-federation.sh list output byte-identical old vs new (all 12 seats, incl. notary's new 4th column)"

echo "== AC5 (part 2/2): onboard-federation.sh --dry-run output unchanged for the 11 non-notary seats =="

NON_NOTARY_SEATS="qbp-architecture qbp-implementor qbp-oppenheimer qbp-cu-implementor cth-implementor wyrd-implementor bma-implementor contextus-impl herschel edda-implementor deming"
NEW_DRY_ALL_BUT_NOTARY="$("$HERE/onboard-federation.sh" --dry-run $NON_NOTARY_SEATS 2>&1)"
OLD_DRY_SUBSET="$("$TMPDIR/oldft/onboard-federation.sh" --dry-run $NON_NOTARY_SEATS 2>&1)"
checkeq "$(printf '%s' "$NEW_DRY_ALL_BUT_NOTARY" | md5sum | awk '{print $1}')" "$(printf '%s' "$OLD_DRY_SUBSET" | md5sum | awk '{print $1}')" \
  "onboard-federation.sh --dry-run byte-identical old vs new for all 11 non-notary seats"

# ─────────────────────────────────────────────────────────────────────────
echo "== AC1: golden-render byte-identity (per-persona, full untruncated prompt) =="
# Extract render()/role_of() from OLD and NEW onboard-federation.sh and run
# each in isolation (no tmux, no CLI truncation) against the SAME 11 personas,
# proving true byte-for-byte identity of the full rendered prompt, not just
# the 160-char CLI preview.
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
         deming:/home/prime/Documents; do
  handle="${p%%:*}"; wd="${p##*:}"
  old_out="$("$TMPDIR/render_old.sh" "$handle" "$wd" "")"
  new_out="$("$TMPDIR/render_new.sh" "$handle" "$wd" "")"
  if [ "$old_out" != "$new_out" ]; then
    echo "    ✗ $handle differs"; all_ident=1
  fi
done
check "$all_ident" "all 11 non-notary personas: full rendered prompt byte-identical old vs new"

NOTARY_NEW="$("$TMPDIR/render_new.sh" notary-implementor /home/prime/Documents/notary "prompt/notary-implementor-launch-prompt.md")"
case "$NOTARY_NEW" in
  *"prompt/notary-implementor-launch-prompt.md"*"§0"*) check 0 "notary render names the persona-file path AND '§0'" ;;
  *) check 1 "notary render names the persona-file path AND '§0'" ;;
esac

# ─────────────────────────────────────────────────────────────────────────
echo "== AC2: origin/main resolution, never a worktree copy; fails loud =="
# source launch-federation.sh's functions without running cmd_launch/list/etc
# — the BASH_SOURCE-vs-$0 guard added at the bottom of the file (inter#142)
# skips the case-dispatch entirely whenever the file is sourced rather than
# executed, regardless of MODE's resolved value.
source "$HERE/launch-federation.sh"

REAL_PATH="prompt/notary-implementor-launch-prompt.md"
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

# divergent local worktree copy must NOT be used
REVERT_FILE="$REAL_PATH"
MARKER="AC2-DIVERGENCE-MARKER-$$"
printf '\n%s\n' "$MARKER" >> "$INTER_REPO/$REAL_PATH"
DIVERGED_CONTENT="$(git -C "$INTER_REPO" show "origin/main:$REAL_PATH" 2>/dev/null)"
if printf '%s' "$DIVERGED_CONTENT" | grep -q "$MARKER"; then
  check 1 "resolution reads origin/main, NOT the dirty local worktree copy"
else
  check 0 "resolution reads origin/main, NOT the dirty local worktree copy"
fi
git -C "$INTER_REPO" checkout -- "$REVERT_FILE"
REVERT_FILE=""

# ─────────────────────────────────────────────────────────────────────────
echo "== AC3: resume re-anchor mechanism (fake-pane tmux session; not a live restart) =="
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

# "WITHOUT -> nothing new (unchanged)": build the REANCHOR_* candidate list the
# way cmd_launch does and confirm a pfile-less row is never added to it.
P_PERSONA=(bma-implementor); P_WORKDIR=(/home/prime/Documents/BMA); P_SID=(deadbeef-0000-0000-0000-000000000000); P_PFILE=("")
declare -a REANCHOR_PERSONA=() REANCHOR_WD=() REANCHOR_PFILE=()
for i in "${!P_PERSONA[@]}"; do
  persona="${P_PERSONA[$i]}"; wd="${P_WORKDIR[$i]}"; sid="${P_SID[$i]}"; pfile="${P_PFILE[$i]}"
  [ -n "$sid" ] && [ -n "$pfile" ] && { REANCHOR_PERSONA+=("$persona"); REANCHOR_WD+=("$wd"); REANCHOR_PFILE+=("$pfile"); }
done
checkeq "${#REANCHOR_PERSONA[@]}" "0" "resumed pane WITHOUT persona-file: not added to the re-anchor list (unchanged)"

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

# header/frontmatter are excluded from comparison: a different-but-valid
# wrapper (frontmatter + a differently-worded header) around the SAME body
# must still pass.
COPY_FM="$TMPDIR/runtime-copy-with-frontmatter.md"
{
  printf -- '---\nname: notary-implementor\ndescription: test\n---\n'
  printf '<!-- GENERATED from JamesPagetButler/inter %s @ %s — do not edit; regenerate -->\n\n' "$REAL_PATH" "$SHA"
  printf '%s' "$CANON_BLOCK"
} > "$COPY_FM"
"$HERE/check-persona-drift.sh" "$REAL_PATH" "$COPY_FM" >/tmp/ac4_fm.$$ 2>&1
check "$?" "header + frontmatter excluded from comparison: exit 0 despite different wrapper"
rm -f /tmp/ac4_fm.$$

# mutation test (required by AC4): flip one byte in the BODY (not the header)
COPY_MUT="$TMPDIR/runtime-copy-mutated.md"
cp "$COPY" "$COPY_MUT"
python3 - "$COPY_MUT" <<'PYEOF'
import sys
p = sys.argv[1]
b = bytearray(open(p, "rb").read())
# find a body line (after the header+blank) and flip one alnum byte
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

echo "== Backward compatibility: cmd_refresh preserves format for 3-column rows, keeps a 4th column when present =="
FIXTURE2="$TMPDIR/personas-refresh.conf"
cat > "$FIXTURE2" <<EOF
gamma-persona        | /tmp/gamma-wd                | fixed-sid-aaaa
notary-implementor   | /tmp/notary-wd               | fixed-sid-bbbb | some/persona-file.md
EOF
CONF="$FIXTURE2"
cmd_refresh >/tmp/refresh_out.$$ 2>&1
ok=1
grep -Eq '^gamma-persona +\| /tmp/gamma-wd +\| fixed-sid-aaaa *$' "$FIXTURE2" || ok=0
grep -q "some/persona-file.md" "$FIXTURE2" || ok=0
[ "$ok" = "1" ] && check 0 "refresh: 3-col row stays 3-col; 4-col row keeps its persona_file" || check 1 "refresh: 3-col row stays 3-col; 4-col row keeps its persona_file"
rm -f /tmp/refresh_out.$$ "$FIXTURE2.bak"

echo
echo "RESULT: $pass passed, $fail failed"
exit $([ "$fail" -eq 0 ] && echo 0 || echo 1)
