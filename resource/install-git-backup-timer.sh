#!/usr/bin/env bash
#
# install-git-backup-timer.sh — opt-in installer for the git-backup@<seat>
# systemd --user timer.
#
# This is OPT-IN per (repo, seat) — nothing runs automatically until you
# run this. It does NOT touch refs/heads/* or push protection; it only
# arms a periodic `git-backup` (refs/backup/* mirror) for one repo.
#
# Usage:
#   ./install-git-backup-timer.sh <seat> <repo-path> [remote]
#
# Example:
#   ./install-git-backup-timer.sh bma ~/Documents/BMA origin
#
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
  echo "ERROR: don't run this with sudo/root — it's a systemd --user unit for your own account." >&2
  exit 1
fi

SEAT="${1:?usage: install-git-backup-timer.sh <seat> <repo-path> [remote]}"
REPO="${2:?usage: install-git-backup-timer.sh <seat> <repo-path> [remote]}"
REMOTE="${3:-origin}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_BACKUP_BIN="$SCRIPT_DIR/git-backup"
UNIT_DIR="$HOME/.config/systemd/user"
ENV_DIR="$HOME/.config/git-backup"

[ -x "$GIT_BACKUP_BIN" ] || { echo "ERROR: $GIT_BACKUP_BIN not found or not executable" >&2; exit 1; }
REPO="$(cd "$REPO" 2>/dev/null && pwd || true)"
[ -n "$REPO" ] && git -C "$REPO" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  || { echo "ERROR: '$2' is not a git repository" >&2; exit 1; }
command -v systemctl >/dev/null || { echo "ERROR: systemctl not found" >&2; exit 1; }
if ! systemctl --user show-environment >/dev/null 2>&1; then
  echo "ERROR: no systemd --user session bus available. Run from your login session." >&2
  exit 1
fi

echo "== git-backup@$SEAT installer =="
mkdir -p "$UNIT_DIR" "$ENV_DIR"

# 1. per-seat env file (idempotent overwrite)
ENV_FILE="$ENV_DIR/$SEAT.env"
cat > "$ENV_FILE" <<EOF
GIT_BACKUP_REPO=$REPO
GIT_BACKUP_BIN=$GIT_BACKUP_BIN
GIT_BACKUP_REMOTE=$REMOTE
EOF
echo "✓ env written: $ENV_FILE"

# 2. install the template units (canonical source: this resource/ dir)
cp "$SCRIPT_DIR/git-backup@.service" "$UNIT_DIR/git-backup@.service"
cp "$SCRIPT_DIR/git-backup@.timer" "$UNIT_DIR/git-backup@.timer"
echo "✓ units installed: $UNIT_DIR/git-backup@.{service,timer}"

# 3. enable + start the instance for this seat
systemctl --user daemon-reload
systemctl --user enable --now "git-backup@${SEAT}.timer"

if systemctl --user is-active --quiet "git-backup@${SEAT}.timer"; then
  echo "✓ timer active: git-backup@${SEAT}.timer"
else
  echo "✗ timer failed to start. Diagnostics:" >&2
  systemctl --user --no-pager status "git-backup@${SEAT}.timer" 2>&1 | tail -15
  exit 1
fi

echo
echo "Done. $REPO will back up to refs/backup/$SEAT/<branch> on '$REMOTE' every ~15min."
echo "  run once now :  systemctl --user start git-backup@${SEAT}.service"
echo "  status       :  systemctl --user status git-backup@${SEAT}.timer"
echo "  logs         :  journalctl --user -u git-backup@${SEAT}.service -f"
echo "  remove       :  systemctl --user disable --now git-backup@${SEAT}.timer && rm $ENV_FILE"
