#!/usr/bin/env python3
"""Driver for audit_labeller_v1.py (round 1.1, prereg R8/amendment-2 B3):
one fresh, blind Gemini session per audit paper, each covering that paper's
own subset of the audit set.

The audit item list is a runtime input, not a pre-registered draw -- per
§8, audit items are double-graded items where verifier grade == checker
grade == agreed_grade, so the actual set only exists once the 120-set has
been graded.

Plan-only by default. `--execute` is gated the same way as
r1_1_checker_driver.py's: nothing paid runs without it.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
LABELLER = HERE / "audit_labeller_v1.py"


def load_manifest(manifest_path: Path) -> dict:
    """paper_id -> (input_relpath, input_sha), parsed from a `sha  path` manifest."""
    out = {}
    for line in manifest_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        sha, relpath = line.split(None, 1)
        paper_id = Path(relpath).name.split(".")[0]
        out[paper_id] = (relpath, sha)
    return out


def build_plan(
    audit_items,
    manifest: dict,
    grader_inputs_dir: Path,
    rubric_path: Path,
    rubric_sha: str,
    prompt_path: Path,
    prompt_sha: str,
) -> list:
    """audit_items: [(paper, n), ...]. One call per distinct paper, covering
    every n that paper contributes to the audit set -- never split across
    multiple calls, since each paper gets exactly one fresh labeller
    session (B3)."""
    if not audit_items:
        raise SystemExit("audit_items is empty -- nothing to plan")
    by_paper = {}
    for paper, n in audit_items:
        by_paper.setdefault(paper, []).append(int(n))

    missing = sorted(set(by_paper) - set(manifest))
    if missing:
        raise SystemExit(f"audit paper(s) not in the grader-input manifest: {missing}")

    plan = []
    for paper in sorted(by_paper):
        relpath, input_sha = manifest[paper]
        claim_numbers = sorted(set(by_paper[paper]))
        if len(claim_numbers) != len(by_paper[paper]):
            raise SystemExit(f"{paper}: duplicate (paper, n) pair in audit_items")
        plan.append(
            {
                "paper": paper,
                "claim_numbers": claim_numbers,
                "prompt": str(prompt_path),
                "prompt_sha": prompt_sha,
                "rubric": str(rubric_path),
                "rubric_sha": rubric_sha,
                "input": str(grader_inputs_dir / Path(relpath).name),
                "input_sha": input_sha,
            }
        )
    return plan


def print_plan(plan: list) -> None:
    total_claims = sum(len(c["claim_numbers"]) for c in plan)
    print(f"Plan: {len(plan)} audit-labeller calls (one per paper) covering {total_claims} claims total.")
    for call in plan:
        print(f"  [audit] {call['paper']} claims={call['claim_numbers']}")


def execute_plan(plan: list, out_dir: str) -> int:
    for call in plan:
        cmd = [
            sys.executable,
            "-I",
            str(LABELLER),
            "label",
            "--prompt",
            call["prompt"],
            "--prompt-sha",
            call["prompt_sha"],
            "--rubric",
            call["rubric"],
            "--rubric-sha",
            call["rubric_sha"],
            "--input",
            call["input"],
            "--input-sha",
            call["input_sha"],
            "--claims",
            ",".join(str(n) for n in call["claim_numbers"]),
            "--paper",
            call["paper"],
            "--label",
            call["paper"],
            "--out-dir",
            out_dir,
        ]
        print("RUN:", " ".join(cmd))
        subprocess.run(cmd, check=True)
    return 0


def collect_grades(out_dir: Path, plan: list) -> dict:
    """qbp-architecture, seq 329: "the glue for {stem}.grades.json ->
    {paper: {n: grade}} can go in now, because the shape is fixed by R8."

    Reads each planned paper's own `{paper}.grades.json` (written by
    audit_labeller_v1.py's `label` command) and assembles exactly the
    `grades_by_paper` shape r1_1_audit_labeller.build_labeller_set() takes.
    Fails loudly, by paper, if a planned paper's grades file is missing --
    never silently drops a paper from the merged result."""
    out_dir = Path(out_dir)
    grades_by_paper = {}
    missing = []
    for call in plan:
        paper = call["paper"]
        grades_path = out_dir / f"{paper}.grades.json"
        if not grades_path.exists():
            missing.append(paper)
            continue
        grades_by_paper[paper] = {int(n): g for n, g in json.loads(grades_path.read_text()).items()}
    if missing:
        raise SystemExit(f"missing {{paper}}.grades.json for planned paper(s): {missing}")
    return grades_by_paper


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-items", required=True, help="JSON file: [[paper, n], ...]")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--grader-inputs-dir", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--prompt-sha", required=True)
    parser.add_argument("--rubric", required=True)
    parser.add_argument("--rubric-sha", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="actually invoke audit_labeller_v1.py; default is plan-only (nothing paid runs)",
    )
    parser.add_argument(
        "--merge-grades-out",
        help="after --execute, collect every planned paper's {paper}.grades.json into "
        "{paper: {n: grade}} and write it here, ready for r1_1_audit_labeller.py --grades",
    )
    args = parser.parse_args()

    audit_items = [(p, int(n)) for p, n in json.loads(Path(args.audit_items).read_text())]
    manifest = load_manifest(Path(args.manifest))
    plan = build_plan(
        audit_items,
        manifest,
        Path(args.grader_inputs_dir),
        Path(args.rubric),
        args.rubric_sha,
        Path(args.prompt),
        args.prompt_sha,
    )
    print_plan(plan)

    if not args.execute:
        print("Plan-only (pass --execute to actually call audit_labeller_v1.py). Nothing paid ran.")
        return 0

    rc = execute_plan(plan, args.out_dir)
    if rc != 0 or not args.merge_grades_out:
        return rc

    grades_by_paper = collect_grades(Path(args.out_dir), plan)
    Path(args.merge_grades_out).write_text(json.dumps(grades_by_paper, indent=2, sort_keys=True))
    print(f"OK: merged {len(grades_by_paper)} papers' grades to {args.merge_grades_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
