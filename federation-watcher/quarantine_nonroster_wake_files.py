#!/usr/bin/env python3
"""quarantine_nonroster_wake_files.py — inter#271 item 3, one-off cleanup.

watcher.py now writes a wake FILE only for an ALLOWED handle (see
route_wake() in watcher.py: roster, extra_recipients, or an alias's
resolved seat). This script cleans up the ~100 pre-existing junk files
(commit shas, `@v7`-style tokens, typos) that accumulated in `wake/` under
the old behaviour.

It MOVES, never deletes: every top-level, non-hidden regular file in the
wake dir whose name is not PROTECTED is moved into
`<wake-dir>/.quarantine-2026-11-01/`, and the move list is printed. Already-
quarantined files are never revisited (the scan is top-level only), so
re-running this script is a no-op the second time.

PROTECTED (never moved, by this script, ever) is the union of:
  - the roster (personas.conf + watch_mentions)
  - `extra_recipients` from config.yaml (e.g. `antigravity`)
  - every alias NAME from config.yaml's `aliases` map (e.g. `bragi`, `bma`)
    — an alias is a real, currently-used sender handle (inter#271 B1); its
    own leftover wake file is real traffic nobody reads, not junk, and
    this script is not the place to decide what to do about it.
  - ALWAYS_TO_HANDLES (the deming-escalate route)

Of those, alias NAMES get their own separate "LEGACY ALIAS" listing (any
alias's own file that still exists on disk) — printed, never moved, so the
foreman can decide those by hand.

Default is a DRY RUN — it only prints what it WOULD move. Pass --apply to
actually perform the moves.

Usage:
    python3 federation-watcher/quarantine_nonroster_wake_files.py \
        [--wake-dir ~/.federation-watcher/wake] \
        [--personas-conf ~/Documents/inter/federation-terminals/personas.conf] \
        [--apply]

With no --wake-dir/--personas-conf, both default to config.yaml's values
(personas_conf, falling back to heartbeat.personas_conf; watch_mentions,
aliases and extra_recipients are always read from config.yaml directly).
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


def _top_level_files(wake_dir: Path) -> list[Path]:
    """Every regular, non-hidden, TOP-LEVEL file in `wake_dir`. Never
    descends into subdirectories (e.g. a previous quarantine dir), so a
    second run never re-visits an already-moved file."""
    if not wake_dir.is_dir():
        return []
    return [
        p for p in sorted(wake_dir.iterdir())
        if p.is_file() and not p.name.startswith(".")
    ]


def find_nonroster_files(wake_dir: Path, protected: set[str]) -> list[Path]:
    """Every top-level wake file whose name is NOT in `protected` (B1:
    roster UNION extra_recipients UNION alias names UNION
    ALWAYS_TO_HANDLES) — the genuinely junk ones this script moves."""
    return [p for p in _top_level_files(wake_dir) if p.name not in protected]


def find_legacy_alias_files(wake_dir: Path, alias_names: set[str]) -> list[Path]:
    """Any alias's OWN leftover wake file (e.g. `bragi`, `bma`) that still
    exists on disk — real traffic, never moved by this script, listed
    separately so a human decides."""
    return [p for p in _top_level_files(wake_dir) if p.name in alias_names]


def quarantine(wake_dir: Path, protected: set[str], apply: bool) -> list[Path]:
    """Return the files that are (or, with apply=False, would be) moved.
    MOVES, never deletes — matches architect ruling, inter#271."""
    junk = find_nonroster_files(wake_dir, protected)
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
    aliases: dict[str, str] = cfg.get("aliases") or {}
    extra_recipients: set[str] = set(cfg.get("extra_recipients") or [])
    alias_names: set[str] = set(aliases.keys())

    protected = roster | extra_recipients | alias_names | watcher.ALWAYS_TO_HANDLES

    legacy = find_legacy_alias_files(wake_dir, alias_names)
    for p in legacy:
        print(f"LEGACY ALIAS (not moved, decide by hand): {p} -> {aliases.get(p.name, '?')}")

    junk = quarantine(wake_dir, protected, apply=args.apply)
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
