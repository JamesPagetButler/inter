#!/usr/bin/env python3
"""check_state.py — the inter#232 seat-state lint (S1 of roadmap §2.9).

A seat-state file is a *view* over the record (Nidavellir#38 L2 over L1): every entry is a pointer
plus one line, so the file can be lost and re-derived. This lint checks the shape mechanically:

  * one ```yaml state block, with only the schema's top-level keys;
  * every decision has a `ptr`, and every pointer is in the resolvable grammar (fully qualified
    `<repo>#N`, `<repo>#N:issuecomment-ID`, `<repo>@<sha>`, `bus:<channel>:<seq>`, or a GitHub URL);
  * `applies_when` and `defeated_by` are present on every decision — empty is legal, absence is not;
  * `authority` is a role (`role:<name>`), never a person, so it migrates without a schema change;
  * the F/E grade uses the ratified two-axis model (inter#223);
  * no bus pointer is newer than the seat's own `last_seen` for that channel.

It checks *syntax and internal consistency*, not that a pointer resolves on GitHub or the bus;
resolution is the rebuild dry-run (inter#232 AC4). Report mode (default) prints and exits 0;
`--strict` exits 1 on any problem. Schema: best-practices/seat-state.md.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import yaml

TOP_KEYS = {"seat", "persona", "updated", "last_seen", "obligations", "infra", "active", "decisions", "watch"}
REQUIRED = ("seat", "persona", "updated", "last_seen", "decisions")
F_AXIS = {"napkin", "research", "formal"}
E_AXIS = {"unconfronted", "consistent", "validated", "falsified"}

_REPO = r"[A-Za-z][A-Za-z0-9._-]*"
POINTER = re.compile(
    rf"(?:{_REPO}#\d+(?::issuecomment-\d+)?"
    rf"|{_REPO}@[0-9a-f]{{7,40}}"
    r"|bus:[a-z0-9][a-z0-9-]*:\d+"
    r"|https://github\.com/JamesPagetButler/\S+)"
)
BUS = re.compile(r"bus:([a-z0-9][a-z0-9-]*):(\d+)")
BLOCK = re.compile(r"^```yaml state\s*\n(.*?)^```", re.M | re.S)


def _pointers(state: dict):
    """Yield (where, pointer) for every pointer-bearing field."""
    for i, d in enumerate(state.get("decisions") or []):
        if isinstance(d, dict) and "ptr" in d:
            yield f"decisions[{i}].ptr", str(d["ptr"])
    for i, o in enumerate(state.get("obligations") or []):
        if isinstance(o, dict) and "ask" in o:
            yield f"obligations[{i}].ask", str(o["ask"])
    for i, w in enumerate(state.get("watch") or []):
        if isinstance(w, dict) and "ptr" in w:
            yield f"watch[{i}].ptr", str(w["ptr"])


def check_state(state: dict) -> list[str]:
    probs: list[str] = []
    for k in state:
        if k not in TOP_KEYS:
            probs.append(f"unknown top-level key `{k}` (state holds pointers, not memory)")
    for k in REQUIRED:
        if k not in state:
            probs.append(f"required key `{k}` missing")

    for i, d in enumerate(state.get("decisions") or []):
        if not isinstance(d, dict):
            probs.append(f"decisions[{i}]: not a mapping")
            continue
        if "ptr" not in d:
            probs.append(f"decisions[{i}]: no `ptr` (a decision without its source is declared, not derived)")
        for f in ("applies_when", "defeated_by"):
            if f not in d:
                probs.append(f"decisions[{i}]: `{f}` absent (write it empty if none; omission is an overclaim)")
        auth = str(d.get("authority", ""))
        if not re.fullmatch(r"role:[a-z][a-z0-9-]*", auth):
            probs.append(f"decisions[{i}]: authority must be `role:<name>`, got {auth!r}")
        g = d.get("grade") or {}
        if g.get("F") not in F_AXIS:
            probs.append(f"decisions[{i}]: grade.F must be one of {sorted(F_AXIS)}, got {g.get('F')!r}")
        if g.get("E") not in E_AXIS:
            probs.append(f"decisions[{i}]: grade.E must be one of {sorted(E_AXIS)}, got {g.get('E')!r}")

    last_seen = state.get("last_seen") or {}
    for where, ptr in _pointers(state):
        if not POINTER.fullmatch(ptr):
            probs.append(f"{where}: {ptr!r} is not a resolvable pointer")
            continue
        m = BUS.fullmatch(ptr)
        if m:
            ch, seq = m.group(1), int(m.group(2))
            if ch not in last_seen:
                probs.append(f"{where}: {ptr} on a channel with no last_seen entry")
            elif seq > int(last_seen[ch]):
                probs.append(f"{where}: {ptr} is newer than last_seen[{ch}]={last_seen[ch]}")
    return probs


def check_text(text: str, name: str) -> list[str]:
    m = BLOCK.search(text)
    if not m:
        return [f"{name}: no ```yaml state block"]
    try:
        state = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        return [f"{name}: state block does not parse: {exc}"]
    if not isinstance(state, dict):
        return [f"{name}: state block is not a mapping"]
    return check_state(state)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+", type=pathlib.Path)
    ap.add_argument("--strict", action="store_true", help="exit 1 on any problem (the gate)")
    a = ap.parse_args(argv)
    failed = 0
    for f in a.files:
        probs = check_text(f.read_text(), str(f)) if f.is_file() else [f"{f}: state file not found"]
        print(f"{'OK  ' if not probs else 'FAIL'} {f}")
        for p in probs:
            print(f"     - {p}")
        failed += bool(probs)
    print(f"\n{len(a.files) - failed}/{len(a.files)} state files clean")
    return 1 if (a.strict and failed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
