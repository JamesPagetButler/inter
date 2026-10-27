#!/usr/bin/env python3
"""check_personas.py — the inter#228 seat-rebuild gate, column (a)+(b) made mechanical.

For every seat in federation-terminals/personas.conf, require:
  * a persona-file (4th column) wired, pointing at a file that exists in this tree;
  * that persona has front-matter `refined:`, a `## §0` boot section and a `## §7` doctrine section;
  * a `wisdoms/<seat>.md` exists.

Report mode (default, used in CI) prints the per-seat matrix and exits 0 — it must not turn every
inter PR red while seats are still outstanding. `--strict` exits 1 on any gap; it is the rebuild gate.
Run against origin/main content (CI checks out the PR head; the gate runs on main), never a stale
shared checkout (inter#228 correction).
"""
from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
import sys

SECTION0 = re.compile(r"^##\s*§\s*0\b", re.M)
SECTION7 = re.compile(r"^##\s*§\s*7\b", re.M)
REFINED = re.compile(r"^refined:\s*\S", re.M)


@dataclasses.dataclass
class Row:
    seat: str
    workdir: str
    persona_file: str | None


@dataclasses.dataclass
class Result:
    seat: str
    ok: bool
    problems: list[str]


def read_roster(root: pathlib.Path) -> list[Row]:
    rows = []
    for raw in (root / "federation-terminals" / "personas.conf").read_text().splitlines():
        line = raw.split("#", 1)[0].strip()  # inline comments are not columns
        if not line:
            continue
        cols = [c.strip() for c in line.split("|")]
        if len(cols) < 3:
            continue
        pf = cols[3] if len(cols) > 3 and cols[3] else None
        rows.append(Row(cols[0], cols[1], pf))
    return rows


def front_matter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end]
    return ""


def check(root: pathlib.Path) -> list[Result]:
    out = []
    for row in read_roster(root):
        probs: list[str] = []
        if not row.persona_file:
            probs.append("no persona-file column in personas.conf (seat boots the generic onboard)")
        else:
            pf = root / row.persona_file
            if not pf.is_file():
                probs.append(f"persona-file {row.persona_file} not found")
            else:
                text = pf.read_text()
                if not REFINED.search(front_matter(text)):
                    probs.append(f"{row.persona_file}: front-matter lacks `refined:`")
                if not SECTION0.search(text):
                    probs.append(f"{row.persona_file}: no `## §0` boot/re-anchor section")
                if not SECTION7.search(text):
                    probs.append(f"{row.persona_file}: no `## §7` operating-doctrine section")
        if not (root / "wisdoms" / f"{row.seat}.md").is_file():
            probs.append(f"wisdoms/{row.seat}.md not found")
        out.append(Result(row.seat, not probs, probs))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent.parent))
    ap.add_argument("--strict", action="store_true", help="exit 1 on any gap (the rebuild gate)")
    a = ap.parse_args(argv)
    results = check(pathlib.Path(a.root))
    green = sum(r.ok for r in results)
    print(f"inter#228 persona gate: {green}/{len(results)} seats green")
    for r in results:
        print(f"  {'OK ' if r.ok else 'GAP'} {r.seat}")
        for p in r.problems:
            print(f"        - {p}")
    return 1 if a.strict and green < len(results) else 0


if __name__ == "__main__":
    sys.exit(main())
