#!/usr/bin/env bash
#
# install-friction-scout-systemd.sh — install + activate the friction-scout
# as a systemd --user timer (inter#83), so it runs on a durable cadence
# without a manual re-dispatch each cycle (closes-when criterion 1).
#
# Modeled directly on federation-watcher/install-systemd.sh (the federation's
# proven systemd --user installer pattern) and token-watchdog's systemd unit,
# adapted for a timer+oneshot pair instead of a persistent Type=simple loop —
# each friction-scout run is a short subprocess (gather signals + one Haiku
# triage call + a conditional post), so timer+oneshot is the idiomatic fit;
# the timer supplies the cadence instead of an internal sleep loop.
#
# Idempotent and safe to re-run. Run it from your desktop login session.
#
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIT_DIR="$HOME/.config/systemd/user"
SERVICE_UNIT="$UNIT_DIR/friction-scout.service"
TIMER_UNIT="$UNIT_DIR/friction-scout.timer"
RUN_SCRIPT="$HERE/run-scout.sh"
LOG_DIR="$HOME/.federation-watcher/friction-scout"

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

echo "== friction-scout systemd installer (inter#83) =="

# 0. must run as the normal user, NOT root — this is a systemd --user service.
if [ "$(id -u)" -eq 0 ]; then
  echo "ERROR: don't run this with sudo/root." >&2
  echo "  This is a systemd --user service for your own account — run it as yourself:" >&2
  echo "      ./install-friction-scout-systemd.sh" >&2
  exit 1
fi

# 0b. sanity checks
[ -x "$RUN_SCRIPT" ] || { echo "ERROR: run-scout.sh not found or not executable at $RUN_SCRIPT" >&2; exit 1; }
[ -f "$HERE/scout-prompt.md" ] || { echo "ERROR: scout-prompt.md missing next to run-scout.sh" >&2; exit 1; }
[ -x "$HERE/gather-signals.sh" ] || { echo "ERROR: gather-signals.sh not found or not executable at $HERE" >&2; exit 1; }
command -v claude >/dev/null || { echo "ERROR: claude CLI not found on PATH" >&2; exit 1; }
SESSIONBRIDGE_PY="$HOME/.claude/mcp-servers/sessionbridge/venv/bin/python"
[ -x "$SESSIONBRIDGE_PY" ] || { echo "ERROR: sessionbridge venv python not found at $SESSIONBRIDGE_PY (needed by sessionbridge_post.py)" >&2; exit 1; }
command -v systemctl >/dev/null || { echo "ERROR: systemctl not found" >&2; exit 1; }
if ! systemctl --user show-environment >/dev/null 2>&1; then
  echo "ERROR: no systemd --user session bus available." >&2
  echo "       Run this from your graphical/login session (not a bare ssh/su)." >&2
  exit 1
fi

# WARNING: this installer targets the CANONICAL inter repo path
# (~/Documents/inter/federation-terminals/friction-scout), because the
# systemd units hard-code %h/Documents/inter/... (matching every other
# federation systemd unit's convention — see federation-watcher's
# install-systemd.sh). If you're running this from a worktree (e.g. this
# builder's own ~/Documents/inter-scout during development), install AFTER
# the PR merges to main, not from the worktree — a worktree-installed timer
# would silently break the moment the worktree is torn down.
if [[ "$HERE" != "$HOME/Documents/inter/federation-terminals/friction-scout" ]]; then
  echo "⚠ WARNING: running from '$HERE', not the canonical"
  echo "  '$HOME/Documents/inter/federation-terminals/friction-scout'."
  echo "  The systemd units point at the canonical path regardless of where"
  echo "  this installer runs from. If this is a worktree/dev checkout, the"
  echo "  installed timer will run the CANONICAL copy's scripts, not this"
  echo "  one — merge first, then install from the canonical checkout."
  read -r -p "  Continue anyway? [y/N] " ans
  [[ "$ans" =~ ^[Yy]$ ]] || { echo "aborted."; exit 1; }
fi

mkdir -p "$UNIT_DIR" "$LOG_DIR"

# 1. write the unit files (canonical source lives alongside this installer;
# idempotent overwrite, copied not symlinked — same convention as
# federation-watcher's installer).
cp "$HERE/friction-scout.service" "$SERVICE_UNIT"
cp "$HERE/friction-scout.timer" "$TIMER_UNIT"
echo "✓ units written: $SERVICE_UNIT"
echo "✓ units written: $TIMER_UNIT"

# 2. reload + enable + start the TIMER (not the service directly — the
# service is oneshot and only fires on-demand or via the timer).
systemctl --user daemon-reload
systemctl --user enable --now friction-scout.timer

# 3. verify the timer is actually scheduled
if systemctl --user is-active --quiet friction-scout.timer; then
  next="$(systemctl --user list-timers friction-scout.timer --no-pager 2>/dev/null | sed -n '2p')"
  echo "✓ timer active. Next run: ${next:-<see 'systemctl --user list-timers'>}"
else
  echo "✗ timer failed to activate. Diagnostics:" >&2
  systemctl --user --no-pager status friction-scout.timer 2>&1 | tail -15
  exit 1
fi

# 4. linger — start at boot even before GUI login (best-effort; may need sudo)
if loginctl show-user "$USER" 2>/dev/null | grep -q 'Linger=yes'; then
  echo "✓ linger already enabled (starts at boot)"
elif loginctl enable-linger "$USER" 2>/dev/null; then
  echo "✓ linger enabled (starts at boot, before GUI login)"
else
  echo "⚠ could not enable linger automatically. For boot-before-login start, run:"
  echo "      sudo loginctl enable-linger $USER"
fi

echo
echo "Done. The friction-scout now sweeps on a 10-min cadence (see friction-scout.timer)."
echo "  status      :  systemctl --user status  friction-scout.timer"
echo "  next runs   :  systemctl --user list-timers friction-scout.timer"
echo "  force a run now (manual, respects DRY_RUN if exported first):"
echo "                 systemctl --user start friction-scout.service"
echo "  logs        :  tail -f $LOG_DIR/scout.log     (triage decisions)"
echo "               :  journalctl --user -u friction-scout -f   (systemd/stderr)"
echo "  disable     :  systemctl --user disable --now friction-scout.timer"
echo "  dry-run test (no post, safe to run anytime):"
echo "                 SCOUT_DRY_RUN=1 $RUN_SCRIPT"
