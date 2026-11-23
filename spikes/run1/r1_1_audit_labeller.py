#!/usr/bin/env python3
"""Round 1.1 audit-labeller record builder (prereg R8, qbp-architecture
live-test seq 321: "make the driver's audit-labeller output match the R8
format").

Takes already-parsed grades (paper -> {n: grade}) and an audit item list,
and emits one side of the `audit_labellers` bundle field exactly as
l0_checks.check_labeller_set / analysis_r11.py expect it:

  {"labeller": <name>, "header": {"rubric_sha": <pinned>},
   "records": [{"paper": p, "n": n, "grade": g}, ...]}

Per-record rubric_sha is intentionally omitted here -- this builder always
writes one rubric_sha for the whole set, at the header, and
check_labeller_set's own rule ("own sha if present, else header") covers
that case.

This module does not itself extract grades from a checker answer_RAW.txt --
that parser is a separate, still-open question (seq 324) pending
confirmation of the checker's own output contract. This module is the
record-shape step only, and is exercised by test_r1_1_audit_labeller.py
against the real l0_checks.check_labeller_set as the oracle.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from checker_v1 import CANONICAL_RUBRIC_SHA  # noqa: E402


def build_labeller_set(labeller_name: str, grades_by_paper: dict, audit_items: list, rubric_sha: str = None) -> dict:
    """grades_by_paper: {paper: {n: grade}}. audit_items: [(paper, n), ...].

    Fails loudly (SystemExit) if any audit item has no grade available --
    l0_checks.check_labeller_set's own guard is "labeller item set !=
    expected audit items" (a reject), so a short set must never be silently
    written here; it must never reach L0 in the first place.
    """
    rubric_sha = rubric_sha or CANONICAL_RUBRIC_SHA
    records = []
    missing = []
    for paper, n in audit_items:
        grades = grades_by_paper.get(paper) or {}
        if n not in grades:
            missing.append((paper, n))
            continue
        records.append({"paper": paper, "n": n, "grade": grades[n]})
    if missing:
        raise SystemExit(f"audit-labeller build: missing grades for {missing}")
    return {"labeller": labeller_name, "header": {"rubric_sha": rubric_sha}, "records": records}


def main(argv) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labeller", required=True)
    parser.add_argument("--grades", required=True, help="JSON file: {paper: {n: grade}}")
    parser.add_argument("--audit-items", required=True, help="JSON file: [[paper, n], ...]")
    parser.add_argument("--rubric-sha")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv[1:])

    grades_by_paper = json.loads(Path(args.grades).read_text())
    grades_by_paper = {p: {int(n): g for n, g in d.items()} for p, d in grades_by_paper.items()}
    audit_items = [(p, int(n)) for p, n in json.loads(Path(args.audit_items).read_text())]

    out = build_labeller_set(args.labeller, grades_by_paper, audit_items, args.rubric_sha)
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"OK: wrote {len(out['records'])} audit-labeller records to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
