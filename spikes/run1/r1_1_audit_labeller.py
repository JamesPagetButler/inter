#!/usr/bin/env python3
"""Round 1.1 audit-labeller record builder (prereg R8, qbp-architecture
live-test seq 321/327/331: "make the driver's audit-labeller output match
the R8 format").

Takes already-parsed grades (paper -> {n: grade}) and an audit item list,
and emits one side of the `audit_labellers` bundle field exactly as
l0_checks.check_labeller_set / analysis_r11.py expect it (seq 331: identity,
rubric sha and prompt sha are read from the header ONLY):

  {"header": {"labeller": <name>, "rubric_sha": <pinned>,
              "prompt_sha": <pinned, omitted for a prompt-less labeller>,
              "blind": true},
   "records": [{"paper": p, "n": n, "grade": g}, ...]}

Per-record rubric_sha is intentionally omitted here -- this builder always
writes one rubric_sha for the whole set, at the header, and
check_labeller_set's own rule ("own sha if present, else header") covers
that case.

This module does not itself extract grades from a checker answer_RAW.txt --
audit_labeller_v1.py (the Gemini-calling component) and
checker_v1.parse_grade_lines() do that; this module is the record-shape
step only, and is exercised by test_r1_1_audit_labeller.py against the
real l0_checks.check_labeller_set as the oracle.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from checker_v1 import CANONICAL_RUBRIC_SHA  # noqa: E402


def build_labeller_set(
    labeller_name: str, grades_by_paper: dict, audit_items: list,
    rubric_sha: str = None, prompt_sha: str = None, blind: bool = True,
) -> dict:
    """grades_by_paper: {paper: {n: grade}}. audit_items: [(paper, n), ...].

    Fails loudly (SystemExit) if any audit item has no grade available --
    l0_checks.check_labeller_set's own guard is "labeller item set !=
    expected audit items" (a reject), so a short set must never be silently
    written here; it must never reach L0 in the first place.

    `blind` defaults true: the audit labeller is dispatched blind per B3,
    never told how anyone else graded the item (qbp-architecture, seq 327 --
    a missing or false `blind` in the header voids the set under L0, now at
    `b2fc451`). `blind=False` exists only so a caller building a non-blind
    labeller file can say so explicitly, never by omission.

    `prompt_sha` is omitted from the header entirely by default (None), not
    written as null -- qbp-oppenheimer's hand-label header carries no
    prompt_sha at all (L0's `PROMPT_EXEMPT_LABELLERS`), while a model
    labeller's header must carry its own (e.g.
    `audit_labeller_v1.CANONICAL_PROMPT_SHA` for "gemini-labeller"). The
    caller decides which applies; this builder doesn't guess from the name.
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

    header = {"labeller": labeller_name, "rubric_sha": rubric_sha, "blind": blind}
    if prompt_sha is not None:
        header["prompt_sha"] = prompt_sha
    return {"header": header, "records": records}


def main(argv) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labeller", required=True)
    parser.add_argument("--grades", required=True, help="JSON file: {paper: {n: grade}}")
    parser.add_argument("--audit-items", required=True, help="JSON file: [[paper, n], ...]")
    parser.add_argument("--rubric-sha")
    parser.add_argument("--prompt-sha", help="omit entirely for a prompt-less (e.g. hand) labeller")
    parser.add_argument("--not-blind", action="store_true", help="mark header.blind=false explicitly (never the default)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv[1:])

    grades_by_paper = json.loads(Path(args.grades).read_text())
    grades_by_paper = {p: {int(n): g for n, g in d.items()} for p, d in grades_by_paper.items()}
    audit_items = [(p, int(n)) for p, n in json.loads(Path(args.audit_items).read_text())]

    out = build_labeller_set(
        args.labeller, grades_by_paper, audit_items,
        args.rubric_sha, args.prompt_sha, blind=not args.not_blind,
    )
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"OK: wrote {len(out['records'])} audit-labeller records to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
