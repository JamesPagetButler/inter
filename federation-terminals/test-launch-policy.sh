#!/usr/bin/env bash
#
# test-launch-policy.sh — tests for inter#262 (fresh-with-personas relaunch by default,
# named-exception resume, refusal guard, quarantine, loud summary).
#
# Drives the REAL build_launch_plan / discover_sid / print_launch_summary by sourcing
# launch-federation.sh (its dispatch is guarded, so sourcing runs nothing). All fixtures
# live under a throwaway $TMPDIR: fake ~/.claude/projects transcripts, a fake exceptions
# file, a fake roster. Never touches the real "fed" tmux session, sessionbridge, or any
# tracked file.
#
# Mutation evidence: run with MUTATE=<name> to apply one mutant to a temp copy of the
# launcher; the suite must then FAIL (KILLED). See the MUTANTS list at the bottom.
#
# Usage: ./test-launch-policy.sh            (all mutants are checked too)
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

run_suite() {  # $1 = launcher path; prints PASS/FAIL lines; returns #failures
  local launcher="$1"
  (
    export HOME="$TMPDIR/home"; mkdir -p "$HOME/.federation-watcher"
    : > "$HOME/.federation-watcher/session-roster.tsv"
    # shellcheck disable=SC1090
    source "$launcher" >/dev/null 2>&1
    PROJECTS="$TMPDIR/projects"; mkdir -p "$PROJECTS"
    fails=0
    ok()   { echo "  PASS: $1"; }
    bad()  { echo "  FAIL: $1"; fails=$((fails+1)); }

    mkwd() {  # $1=name -> echoes a workdir with a project dir
      local wd="$TMPDIR/wd-$1"; mkdir -p "$wd" "$PROJECTS/$(slug_of "$wd")"; echo "$wd"
    }
    mktr() {  # $1=workdir $2=sid $3=content
      printf '%s\n' "$3" > "$PROJECTS/$(slug_of "$1")/$2.jsonl"
    }
    plan() {  # runs build_launch_plan silently
      build_launch_plan >/dev/null 2>&1
    }

    WD_A="$(mkwd a)"; SID_A="aaaaaaaa-0000-0000-0000-000000000001"
    mktr "$WD_A" "$SID_A" '{"type":"assistant","message":{"stop_reason":"end_turn"}}'
    WD_R="$(mkwd r)"; SID_R="rrrrrrrr-0000-0000-0000-000000000002"
    mktr "$WD_R" "$SID_R" '{"type":"assistant","message":{"stop_reason":"refusal"}}'
    WD_P="$(mkwd p)"; SID_P="pppppppp-0000-0000-0000-000000000003"
    mktr "$WD_P" "$SID_P" '{"type":"user","message":{"content":"we discussed the word refusal and stop_reason in prose"}}'
    WD_Q="$(mkwd q)"; SID_Q="4f3fa045-30ee-4ee3-8fcd-0eadf0d92d68"
    mktr "$WD_Q" "$SID_Q" '{"type":"assistant","message":{"stop_reason":"end_turn"}}'

    EXC="$TMPDIR/exceptions.conf"; RESUME_EXCEPTIONS="$EXC"

    echo "== T1 default policy is fresh: a resumable seat NOT on the list goes FRESH =="
    : > "$EXC"; LAUNCH_POLICY=fresh
    P_PERSONA=(seat-a); P_WORKDIR=("$WD_A"); P_SID=("$SID_A"); P_PFILE=("")
    plan
    [ -z "${P_SID[0]}" ] && [ "${P_MODE[0]}" = "FRESH" ] && [ "${FRESH[0]:-}" = "seat-a" ] \
      && ok "T1 unlisted seat -> FRESH, sid cleared, onboarded" || bad "T1 unlisted seat -> FRESH (got mode=${P_MODE[0]:-} sid=${P_SID[0]:-})"

    echo "== T2 a named exception with a reason resumes, and the reason is recorded =="
    printf '%s\n' 'seat-a | mid-proof, context matters' > "$EXC"
    P_PERSONA=(seat-a); P_WORKDIR=("$WD_A"); P_SID=("$SID_A"); P_PFILE=("")
    plan
    [ "${P_SID[0]}" = "$SID_A" ] && [ "${P_MODE[0]}" = "RESUME-exception" ] && [ "${P_NOTE[0]}" = "mid-proof, context matters" ] \
      && ok "T2 exception resumes with its reason" || bad "T2 exception resumes (got mode=${P_MODE[0]:-} note=${P_NOTE[0]:-})"

    echo "== T3 an exception line with NO reason is ignored -> FRESH =="
    printf '%s\n' 'seat-a |' > "$EXC"
    P_PERSONA=(seat-a); P_WORKDIR=("$WD_A"); P_SID=("$SID_A"); P_PFILE=("")
    plan
    [ -z "${P_SID[0]}" ] && [ "${P_MODE[0]}" = "FRESH" ] \
      && ok "T3 reasonless exception ignored" || bad "T3 reasonless exception ignored (got mode=${P_MODE[0]:-})"

    echo "== T4 refusal guard beats the exception list =="
    printf '%s\n' 'seat-r | listed anyway' > "$EXC"
    P_PERSONA=(seat-r); P_WORKDIR=("$WD_R"); P_SID=("$SID_R"); P_PFILE=("")
    plan
    [ -z "${P_SID[0]}" ] && [ "${P_MODE[0]}" = "FRESH-forced-by-refusal" ] \
      && ok "T4 refusal transcript never resumed, even as an exception" || bad "T4 refusal guard (got mode=${P_MODE[0]:-})"

    echo "== T5 refusal guard also applies under LAUNCH_POLICY=auto =="
    : > "$EXC"; LAUNCH_POLICY=auto
    P_PERSONA=(seat-r); P_WORKDIR=("$WD_R"); P_SID=("$SID_R"); P_PFILE=("")
    plan
    [ "${P_MODE[0]}" = "FRESH-forced-by-refusal" ] \
      && ok "T5 refusal guard under auto" || bad "T5 refusal guard under auto (got mode=${P_MODE[0]:-})"

    echo "== T6 the WORD 'refusal' in prose is not a structured refusal stop =="
    LAUNCH_POLICY=auto
    P_PERSONA=(seat-p); P_WORKDIR=("$WD_P"); P_SID=("$SID_P"); P_PFILE=("")
    plan
    [ "${P_SID[0]}" = "$SID_P" ] && [ "${P_MODE[0]}" = "RESUME" ] \
      && ok "T6 prose mention does not trip the guard" || bad "T6 prose mention (got mode=${P_MODE[0]:-})"

    echo "== T7 quarantine: never resumed, under auto AND as a listed exception =="
    printf '%s\n' 'seat-q | someone listed it' > "$EXC"
    for pol in auto fresh; do
      LAUNCH_POLICY=$pol
      P_PERSONA=(seat-q); P_WORKDIR=("$WD_Q"); P_SID=("$SID_Q"); P_PFILE=("")
      plan
      [ -z "${P_SID[0]}" ] && [ "${P_MODE[0]}" = "FRESH-quarantined" ] \
        && ok "T7 quarantined sid never resumed (policy=$pol)" || bad "T7 quarantine (policy=$pol, got mode=${P_MODE[0]:-} sid=${P_SID[0]:-})"
    done

    echo "== T8 discovery never offers a quarantined session (content-sniff) =="
    FED_HANDLES='seat-q|other'
    mktr "$WD_Q" "$SID_Q" '"seat-q" "seat-q" "seat-q"'
    got="$(discover_sid seat-q "$WD_Q")"
    [ "$got" != "$SID_Q" ] && ok "T8 content-sniff skips the quarantined transcript (got '${got}')" \
      || bad "T8 content-sniff returned the quarantined sid"

    echo "== T9 discovery never offers a quarantined session (roster) =="
    printf 'seat-q\t%s\t%s\tx\n' "$WD_Q" "$SID_Q" > "$HOME/.federation-watcher/session-roster.tsv"
    ROSTER="$HOME/.federation-watcher/session-roster.tsv"
    got="$(discover_sid seat-q "$WD_Q")"
    [ "$got" != "$SID_Q" ] && ok "T9 roster entry for a quarantined sid is ignored" \
      || bad "T9 roster returned the quarantined sid"
    : > "$ROSTER"

    echo "== T10 the summary is loud: every seat printed with mode, and MISSING gaps counted =="
    LAUNCH_POLICY=fresh; : > "$EXC"
    model_for() { [ "$1" = "seat-a" ] && echo "claude-sonnet-5" || echo ""; }
    origin_has() { return 1; }
    P_PERSONA=(seat-a seat-r); P_WORKDIR=("$WD_A" "$WD_R"); P_SID=("$SID_A" "$SID_R"); P_PFILE=("" "")
    plan
    out="$(print_launch_summary 2>&1)"
    printf '%s' "$out" | grep -q '^  seat-a .*FRESH' && printf '%s' "$out" | grep -q '^  seat-r .*FRESH' \
      && printf '%s' "$out" | grep -q 'claude-sonnet-5' && printf '%s' "$out" | grep -qE 'gap\(s\) marked MISSING' \
      && ok "T10 summary lists each seat, its model, and counts gaps" || { bad "T10 summary"; printf '%s\n' "$out"; }

    echo "== T12 main phase: a 'deferred' seat is not started, onboarded or resumed =="
    LAUNCH_POLICY=fresh; LAUNCH_PHASE=main; : > "$EXC"
    P_PERSONA=(seat-a seat-d); P_WORKDIR=("$WD_A" "$WD_A"); P_SID=("$SID_A" "$SID_A"); P_PFILE=("" ""); P_FLAGS=("" "deferred,no-onboard")
    plan
    [ "${P_MODE[1]}" = "DEFERRED" ] && [ -z "${P_SID[1]}" ] && ! printf '%s\n' "${FRESH[@]}" | grep -qx seat-d \
      && printf '%s\n' "${FRESH[@]}" | grep -qx seat-a \
      && ok "T12 deferred seat held back; the main seat launches normally" || bad "T12 deferred in main phase (mode=${P_MODE[1]:-} fresh=${FRESH[*]:-})"

    echo "== T13 deferred phase: ONLY deferred seats are planned; no-onboard seats are not onboarded =="
    LAUNCH_PHASE=deferred
    P_PERSONA=(seat-a seat-d); P_WORKDIR=("$WD_A" "$WD_A"); P_SID=("$SID_A" "$SID_A"); P_PFILE=("" ""); P_FLAGS=("" "deferred,no-onboard")
    plan
    [ "${P_MODE[0]}" = "SKIP" ] && [ "${P_MODE[1]}" = "FRESH" ] && [ "${#FRESH[@]}" -eq 0 ] \
      && ok "T13 main seat SKIPped; deferred seat FRESH and not onboarded (no-onboard)" || bad "T13 deferred phase (modes=${P_MODE[*]:-} fresh=${FRESH[*]:-})"
    LAUNCH_PHASE=main

    echo "== T14 the optional 5th roster column parses (flags), comments stripped =="
    CONF="$TMPDIR/roster.conf"
    printf '%s\n' "seat-x | $WD_A | AUTO |   | deferred,no-onboard   # a comment" "seat-y | $WD_A | AUTO" > "$CONF"
    P_PERSONA=(); P_WORKDIR=(); P_SID=(); P_PFILE=(); P_FLAGS=()
    LOCAL_CONF="$TMPDIR/none.local.conf"
    load_conf >/dev/null 2>&1
    [ "${P_FLAGS[0]:-}" = "deferred,no-onboard" ] && [ -z "${P_PFILE[0]:-}" ] && [ -z "${P_FLAGS[1]:-}" ] \
      && ok "T14 flags parsed; pfile stays empty; a 3-column row has no flags" || bad "T14 parse (flags0=${P_FLAGS[0]:-} pfile0=${P_PFILE[0]:-} flags1=${P_FLAGS[1]:-})"

    echo "== T11 an invalid LAUNCH_POLICY is refused loudly =="
    if LAUNCH_POLICY=sometimes bash "$launcher" plan >/dev/null 2>&1; then bad "T11 invalid policy accepted"
    else ok "T11 invalid LAUNCH_POLICY exits non-zero"; fi

    exit "$fails"
  )
}

echo "### suite against the real launcher"
run_suite "$HERE/launch-federation.sh"; REAL_FAILS=$?

# Mutation checks: each mutant applied to a temp copy must make the suite FAIL.
declare -A MUTANTS=(
  [default-auto]='s/LAUNCH_POLICY:-fresh/LAUNCH_POLICY:-auto/'
  [no-quarantine]='s/^  for q in \$QUARANTINED_SIDS; do \[ "\$s" = "\$q" \] \&\& return 0; done/  :/'
  [no-refusal-guard]='s/grep -aqE .*"refusal".*"\$1"/false/'
  [reasonless-allowed]='s/^      continue$/      :/'
  [no-defer]='s/if \[ "\$LAUNCH_PHASE" = "main" \] \&\& has_flag "\$flags" deferred; then/if false; then/'
  [no-onboard-ignored]='s/has_flag "\$flags" no-onboard \|\| FRESH\+=/FRESH+=/'
)
echo ""
echo "### mutation checks"
MUT_SURVIVED=0
for m in "${!MUTANTS[@]}"; do
  cp "$HERE/launch-federation.sh" "$TMPDIR/mut.sh"
  sed -i -E "${MUTANTS[$m]}" "$TMPDIR/mut.sh"
  if cmp -s "$HERE/launch-federation.sh" "$TMPDIR/mut.sh"; then
    echo "  MUTANT $m: NOT APPLIED (pattern drift) — counts as a failure"; MUT_SURVIVED=$((MUT_SURVIVED+1)); continue
  fi
  if run_suite "$TMPDIR/mut.sh" >/dev/null 2>&1; then
    echo "  MUTANT $m: SURVIVED"; MUT_SURVIVED=$((MUT_SURVIVED+1))
  else
    echo "  MUTANT $m: KILLED"
  fi
done

echo ""
echo "RESULT: real-suite failures=$REAL_FAILS, mutants survived=$MUT_SURVIVED"
[ "$REAL_FAILS" -eq 0 ] && [ "$MUT_SURVIVED" -eq 0 ]
