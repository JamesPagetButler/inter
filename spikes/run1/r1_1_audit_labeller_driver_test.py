#!/usr/bin/env python3
"""Known-answer test for r1_1_audit_labeller_driver.py's build_plan(): pure
logic, no subprocess, no network, no real manifest/grader-input files -- a
small synthetic fixture with a known correct plan.
"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import r1_1_audit_labeller_driver as driver  # noqa: E402

FIXTURE_MANIFEST = {
    "PA": ("s5_grader_inputs_A2/PA.grader_input.txt", "sha-PA"),
    "PB": ("s5_grader_inputs_A2/PB.grader_input.txt", "sha-PB"),
}


def check_happy_path() -> None:
    audit_items = [("PA", 1), ("PA", 5), ("PB", 2)]
    plan = driver.build_plan(
        audit_items, FIXTURE_MANIFEST, Path("grader_inputs"), Path("rubric.txt"), "rubric-sha",
        Path("prompt.txt"), "prompt-sha",
    )
    if len(plan) != 2:
        raise AssertionError(f"expected one call per paper (2 papers), got {len(plan)}: {plan}")
    by_paper = {c["paper"]: c for c in plan}
    if by_paper["PA"]["claim_numbers"] != [1, 5]:
        raise AssertionError(f"PA claim numbers wrong: {by_paper['PA']['claim_numbers']}")
    if by_paper["PB"]["claim_numbers"] != [2]:
        raise AssertionError(f"PB claim numbers wrong: {by_paper['PB']['claim_numbers']}")
    for c in plan:
        if c["prompt"] != "prompt.txt" or c["prompt_sha"] != "prompt-sha":
            raise AssertionError(f"prompt not threaded through: {c}")
    print("PASS (happy path): 2 audit papers -> 2 calls, claim numbers grouped and sorted correctly.")


def expect_system_exit(fn, expected_substring: str, label: str) -> None:
    try:
        fn()
    except SystemExit as e:
        if expected_substring not in str(e):
            raise AssertionError(f"{label}: message {str(e)!r} does not contain {expected_substring!r}")
    except Exception as e:
        raise AssertionError(f"{label}: got {type(e).__name__}: {e} -- killed-by-crash, not killed-by-guard")
    else:
        raise AssertionError(f"{label}: expected SystemExit containing {expected_substring!r}, build_plan succeeded")
    print(f"PASS ({label}): rejected with the guard's own SystemExit, containing {expected_substring!r}.")


def check_empty_audit_items() -> None:
    expect_system_exit(
        lambda: driver.build_plan([], FIXTURE_MANIFEST, Path("x"), Path("r"), "s", Path("p"), "ps"),
        "empty", "empty audit_items",
    )


def check_paper_not_in_manifest() -> None:
    expect_system_exit(
        lambda: driver.build_plan(
            [("PZ", 1)], FIXTURE_MANIFEST, Path("x"), Path("r"), "s", Path("p"), "ps"
        ),
        "not in the grader-input manifest", "audit paper missing from manifest",
    )


def check_duplicate_pair() -> None:
    expect_system_exit(
        lambda: driver.build_plan(
            [("PA", 1), ("PA", 1)], FIXTURE_MANIFEST, Path("x"), Path("r"), "s", Path("p"), "ps"
        ),
        "duplicate", "duplicate (paper, n) pair",
    )


def check_collect_grades_happy_path() -> None:
    plan = [
        {"paper": "PA", "claim_numbers": [1, 5]},
        {"paper": "PB", "claim_numbers": [2]},
    ]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "PA.grades.json").write_text(json.dumps({"1": "faithful", "5": "wrong-relation"}))
        (tmp / "PB.grades.json").write_text(json.dumps({"2": "faithful"}))
        merged = driver.collect_grades(tmp, plan)
    expected = {"PA": {1: "faithful", 5: "wrong-relation"}, "PB": {2: "faithful"}}
    if merged != expected:
        raise AssertionError(f"collect_grades wrong: {merged}")
    print("PASS (collect_grades happy path): two papers merged into {paper: {n: grade}} with int keys.")


def check_collect_grades_missing_file() -> None:
    plan = [{"paper": "PA", "claim_numbers": [1]}, {"paper": "PB", "claim_numbers": [2]}]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "PA.grades.json").write_text(json.dumps({"1": "faithful"}))
        # PB.grades.json deliberately not written.
        try:
            driver.collect_grades(tmp, plan)
        except SystemExit as e:
            if "PB" not in str(e):
                raise AssertionError(f"SystemExit doesn't name the missing paper: {e}")
        except Exception as e:
            raise AssertionError(f"got {type(e).__name__}: {e} -- killed-by-crash, not killed-by-guard")
        else:
            raise AssertionError("expected SystemExit for a missing grades.json, collect_grades succeeded")
    print("PASS (collect_grades missing file): rejected with the guard's own SystemExit, naming the missing paper.")


def main() -> int:
    check_happy_path()
    check_empty_audit_items()
    check_paper_not_in_manifest()
    check_duplicate_pair()
    check_collect_grades_happy_path()
    check_collect_grades_missing_file()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
