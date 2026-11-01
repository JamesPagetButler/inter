#!/usr/bin/env python3
"""quarantine_nonroster_wake_files.py — inter#271 item 3, one-off cleanup.

watcher.py now writes a wake FILE only for a roster handle (see
resolve_roster() / route_wake() in watcher.py). This script cleans up the
~100 pre-existing junk files (commit shas, `@v7`-style tokens, typos) that
accumulated in `wake/` under the old behaviour.

It MOVES, never deletes: every top-level, non-hidden regular file in the
wake dir whose name is not in the roster is moved into
`<wake-dir>/.quarantine-2026-11-01/`, and the move list is printed. Already-
quarantined files are never revisited (the scan is top-level only), so
re-running this script is a no-op the second time.

Default is a DRY RUN — it only prints what it WOULD move. Pass --apply to
actually perform the moves.

Usage:
    python3 federation-watcher/quarantine_nonroster_wake_files.py \
        [--wake-dir ~/.federation-watcher/wake] \
        [--personas-conf ~/Documents/inter/federation-terminals/personas.conf] \
        [--apply]

With no --wake-dir/--personas-conf, both default to config.yaml's values
(personas_conf, falling back to heartbeat.personas_conf; watch_mentions is
always included in the roster regardless of which personas_conf is used).
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Optional

WATCHER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(WATCHER_DIR))

import watcher  # noqa: E402

QUARANTINE_DIRNAME = ".quarantine-2026-11-01"


def find_nonroster_files(wake_dir: Path, roster: set[str]) -> list[Path]:
    """Every regular, non-hidden, TOP-LEVEL file in `wake_dir` whose name is
    not in `roster`. Never descends into subdirectories (e.g. a previous
    quarantine dir), so a second run never re-visits an already-moved
    file."""
    if not wake_dir.is_dir():
        return []
    out = []
    for p in sorted(wake_dir.iterdir()):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if p.name not in roster:
            out.append(p)
    return out


def quarantine(wake_dir: Path, roster: set[str], apply: bool) -> list[Path]:
    """Return the files that are (or, with apply=False, would be) moved.
    MOVES, never deletes — matches architect ruling, inter#271."""
    junk = find_nonroster_files(wake_dir, roster)
    if apply and junk:
        qdir = wake_dir / QUARANTINE_DIRNAME
        qdir.mkdir(parents=True, exist_ok=True)
        for p in junk:
            shutil.move(str(p), str(qdir / p.name))
    return junk


def _resolve_personas_conf(cfg: dict, override: Optional[Path]) -> Optional[Path]:
    if override is not None:
        return override
    if cfg.get("personas_conf") is not None:
        return cfg["personas_conf"]
    heartbeat = cfg.get("heartbeat") or {}
    return heartbeat.get("personas_conf")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wake-dir", type=Path, default=None,
                     help="defaults to config.yaml's wake_dir")
    ap.add_argument("--personas-conf", type=Path, default=None,
                     help="defaults to config.yaml's personas_conf, else heartbeat.personas_conf")
    ap.add_argument("--apply", action="store_true",
                     help="actually move the files (default: dry run, print only)")
    args = ap.parse_args(argv)

    cfg = watcher.load_config()
    wake_dir: Path = args.wake_dir or cfg["wake_dir"]
    personas_conf = _resolve_personas_conf(cfg, args.personas_conf)
    watch_mentions = cfg.get("watch_mentions", [])
    roster = watcher.resolve_roster(watch_mentions, personas_conf)

    junk = quarantine(wake_dir, roster, apply=args.apply)
    verb = "MOVED" if args.apply else "WOULD MOVE"
    if not junk:
        print("quarantine: no non-roster wake files found")
    for p in junk:
        dest = wake_dir / QUARANTINE_DIRNAME / p.name
        print(f"{verb} {p} -> {dest}")
    if not args.apply and junk:
        print(f"(dry run — {len(junk)} file(s) would move; pass --apply to actually move them)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
