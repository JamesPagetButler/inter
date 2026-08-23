#!/usr/bin/env bash
#
# run-scout.sh — one friction-scout sweep (inter#83).
#
# Cadence-invoked by the friction-scout.timer systemd --user unit (modeled on
# token-watchdog.sh's systemd pattern per the inter#83 dispatch). Pipeline:
#
#   1. gather-signals.sh   — tokenless bash: pane/channel/resource/daemon sweep
#   2. claude -p --model haiku — the one paid call: triage judgment against
#      scout-prompt.md's false-positive classes, emits a triage verdict
#   3. parse the verdict's first line:
#        "SCOUT: all clear"  -> log, exit. Deming stays dormant.
#        "SCOUT: N item(s)"  -> post the whole verdict to live-test (@deming
#                                is already in the text scout-prompt.md's
#                                output contract front-loads), via
#                                sessionbridge_post.py (tokenless).
#
# De-dup: a triage report identical (by hash) to the last one actually posted
# is NOT re-posted — Deming already woke for it once; re-posting every cadence
# tick until the underlying condition clears would defeat "Deming stays
# dormant." The condition re-posts the moment its content changes (new pane
# text, new channel seq, resource flag flips), so a genuinely worsening or
# changing situation is never suppressed — only an exact repeat is.
#
# Env:
#   SCOUT_DRY_RUN=1        run gather+triage but do NOT post; print the
#                           would-be post to stdout/log instead. Use this for
#                           any manual verification run — never smoke-test
#                           against live-test without it.
#   SCOUT_CHANNEL=live-test         channel to sweep + post to
#   SCOUT_MODEL=haiku               --model passed to claude -p
#   SCOUT_STATE_DIR=~/.federation-watcher/friction-scout
#   SCOUT_LOG=$SCOUT_STATE_DIR/scout.log
#   (gather-signals.sh's env overrides also apply — see that script's header)
#
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="${SCOUT_STATE_DIR:-$HOME/.federation-watcher/friction-scout}"
LOG="${SCOUT_LOG:-$STATE_DIR/scout.log}"
CHANNEL="${SCOUT_CHANNEL:-live-test}"
MODEL="${SCOUT_MODEL:-haiku}"
DRY_RUN="${SCOUT_DRY_RUN:-0}"
CLAUDE_BIN="$(command -v claude || echo "$HOME/.local/bin/claude")"
SESSIONBRIDGE_PY="$HOME/.claude/mcp-servers/sessionbridge/venv/bin/python"
LAST_POST_HASH_FILE="$STATE_DIR/last_post_hash_${CHANNEL}"

mkdir -p "$STATE_DIR"
log() { printf '%s %s\n' "$(date -Is)" "$*" >> "$LOG"; }

[ -x "$CLAUDE_BIN" ] || { log "FATAL: claude binary not found"; exit 1; }
[ -f "$HERE/scout-prompt.md" ] || { log "FATAL: scout-prompt.md missing next to run-scout.sh"; exit 1; }

log "RUN start (channel=$CHANNEL model=$MODEL dry_run=$DRY_RUN)"

signals="$("$HERE/gather-signals.sh" 2>>"$LOG")"
if [ -z "$signals" ]; then
  log "FATAL: gather-signals.sh produced no output — skipping this cycle"
  exit 1
fi

prompt="$(cat "$HERE/scout-prompt.md")
$signals"

verdict="$("$CLAUDE_BIN" -p "$prompt" --model "$MODEL" 2>>"$LOG")"
rc=$?
if [ $rc -ne 0 ] || [ -z "$verdict" ]; then
  log "FATAL: claude -p triage call failed (rc=$rc) or returned empty — skipping this cycle, no post (fail-silent, not fail-loud: a broken scout must not spam Deming every tick)"
  exit 1
fi

# Belt-and-suspenders against a model that wraps the contract-mandated first
# line in a markdown code fence despite the prompt forbidding it (observed in
# testing) — strip a leading/trailing ``` fence line if present, rather than
# rejecting an otherwise-correct triage as malformed.
verdict="$(printf '%s\n' "$verdict" | sed -e '1{/^```/d}' -e '${/^```/d}')"

first_line="$(printf '%s\n' "$verdict" | head -n1)"

if printf '%s' "$first_line" | grep -qE '^SCOUT: all clear'; then
  log "all clear — $first_line"
  vitals_line="$(printf '%s\n' "$verdict" | sed -n '2p')"
  [ -n "$vitals_line" ] && log "  $vitals_line"
  exit 0
fi

if ! printf '%s' "$first_line" | grep -qE '^SCOUT: [1-9][0-9]* item\(s\)'; then
  log "FATAL: triage output did not match the output contract — first line was: $first_line — skipping post (malformed output is not treated as an escalation)"
  log "full verdict was: $verdict"
  exit 1
fi

# de-dup: same exact verdict as last time we actually posted -> already woke
# Deming for this, don't re-wake for an unchanged condition.
verdict_hash="$(printf '%s' "$verdict" | sha256sum | cut -d' ' -f1)"
last_hash=""
[ -f "$LAST_POST_HASH_FILE" ] && last_hash="$(cat "$LAST_POST_HASH_FILE" 2>/dev/null || true)"
if [ "$verdict_hash" = "$last_hash" ]; then
  log "ITEMS FOUND but identical to last posted verdict (hash=$verdict_hash) — de-duped, not re-posting: $first_line"
  exit 0
fi

log "ITEMS FOUND — $first_line"
log "$verdict"

message="@deming — friction-scout sweep found something:
$verdict"

if [ "$DRY_RUN" = "1" ]; then
  log "DRY_RUN=1 — would have posted to '$CHANNEL':"
  log "$message"
  printf '%s\n' "$message"
  exit 0
fi

post_out="$("$SESSIONBRIDGE_PY" "$HERE/sessionbridge_post.py" --channel "$CHANNEL" --message "$message" 2>>"$LOG")"
post_rc=$?
if [ $post_rc -ne 0 ]; then
  log "FATAL: sessionbridge post failed (rc=$post_rc) — item was found but Deming was NOT notified this cycle. See log above for the sessionbridge_post.py stderr."
  exit 1
fi
log "posted: $post_out"
echo "$verdict_hash" > "$LAST_POST_HASH_FILE"
log "RUN end (posted)"
