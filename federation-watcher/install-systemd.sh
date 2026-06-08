#!/usr/bin/env bash
#
# install-systemd.sh — install + activate the federation-watcher as a
# systemd --user service, so the daemon self-heals on crash and starts on boot.
#
# This replaces the manual `nohup python3 watcher.py &` launch. After the
# 2026-06-03 host power-down the daemon stayed dead until relaunched by hand;
# this makes the next hard-down a no-op (systemd restarts it; with linger,
# even before GUI login).
#
# Idempotent and safe to re-run. Run it from your desktop login session.
#
set -uo pipefail

UNIT_DIR="$HOME/.config/systemd/user"
UNIT="$UNIT_DIR/federation-watcher.service"
WATCHER="$HOME/Documents/inter/federation-watcher/watcher.py"
LOG="$HOME/.federation-watcher/watcher.log"

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

echo "== federation-watcher systemd installer =="

# 0. must run as the normal user, NOT root — this is a systemd --user service.
# sudo would set HOME=/root and register the service for the wrong account.
if [ "$(id -u)" -eq 0 ]; then
  echo "ERROR: don't run this with sudo/root." >&2
  echo "  This is a systemd --user service for your own account — run it as yourself:" >&2
  echo "      ./install-systemd.sh" >&2
  echo "  (only the optional linger step may need sudo; the script prints that line for you.)" >&2
  exit 1
fi

# 0b. sanity checks
[ -f "$WATCHER" ] || { echo "ERROR: watcher.py not found at $WATCHER" >&2; exit 1; }
command -v systemctl >/dev/null || { echo "ERROR: systemctl not found" >&2; exit 1; }
if ! systemctl --user show-environment >/dev/null 2>&1; then
  echo "ERROR: no systemd --user session bus available." >&2
  echo "       Run this from your graphical/login session (not a bare ssh/su)." >&2
  exit 1
fi

mkdir -p "$UNIT_DIR" "$(dirname "$LOG")"

# 1. write the unit file (canonical source lives here; idempotent overwrite)
cat > "$UNIT" <<'EOF'
[Unit]
Description=Federation watcher — routes sessionbridge @mention/IMMEDIATE events to per-persona wake files
After=default.target

[Service]
Type=simple
WorkingDirectory=%h/Documents/inter/federation-watcher
ExecStart=/usr/bin/python3 %h/Documents/inter/federation-watcher/watcher.py
# self-heal: restart on any exit (crash, OOM-kill, transient error)
Restart=always
RestartSec=5
# keep the existing log file working (append, don't truncate)
StandardOutput=append:%h/.federation-watcher/watcher.log
StandardError=append:%h/.federation-watcher/watcher.log
# don't thrash if it's genuinely crash-looping on a bug
StartLimitIntervalSec=120
StartLimitBurst=5

[Install]
WantedBy=default.target
EOF
echo "✓ unit written: $UNIT"

# 2. ensure a SINGLE router: stop any managed instance, then kill leftover nohup ones
systemctl --user stop federation-watcher.service 2>/dev/null || true
if pgrep -f "python3 .*watcher\.py" >/dev/null 2>&1; then
  pkill -f "python3 .*watcher\.py" 2>/dev/null || true
  sleep 1
  echo "✓ stopped pre-existing watcher process(es)"
fi

# 3. reload + enable + start under systemd
systemctl --user daemon-reload
systemctl --user enable --now federation-watcher.service
sleep 2

# 4. verify it's actually up
if systemctl --user is-active --quiet federation-watcher.service; then
  pid="$(systemctl --user show -p MainPID --value federation-watcher.service 2>/dev/null)"
  echo "✓ service active (MainPID $pid)"
else
  echo "✗ service failed to start. Diagnostics:" >&2
  systemctl --user --no-pager status federation-watcher.service 2>&1 | tail -15
  exit 1
fi

# 5. linger — start at boot even before GUI login (best-effort; may need sudo)
if loginctl show-user "$USER" 2>/dev/null | grep -q 'Linger=yes'; then
  echo "✓ linger already enabled (starts at boot)"
elif loginctl enable-linger "$USER" 2>/dev/null; then
  echo "✓ linger enabled (starts at boot, before GUI login)"
else
  echo "⚠ could not enable linger automatically. For boot-before-login start, run:"
  echo "      sudo loginctl enable-linger $USER"
  echo "  (Without linger it still starts on GUI login — fine for your normal usage.)"
fi

echo
echo "Done. The watcher is now a managed, self-healing service."
echo "  status :  systemctl --user status  federation-watcher"
echo "  restart:  systemctl --user restart federation-watcher"
echo "  logs   :  journalctl --user -u federation-watcher -f   (or: tail -f $LOG)"
echo "  remove :  systemctl --user disable --now federation-watcher && rm $UNIT"
echo
echo "Reboot test: after a reboot,"
echo "  systemctl --user is-active federation-watcher"
echo "should print 'active' with no manual start. Your armed Monitor keeps working"
echo "across the swap — it tails the wake file, not the daemon process."
