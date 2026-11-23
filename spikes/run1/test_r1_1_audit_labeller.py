#!/usr/bin/env python3
"""Known-answer test for r1_1_audit_labeller.py's build_labeller_set(),
checked against the REAL l0_checks.check_labeller_set (the director's own
gate-0 oracle, amendment-1 pin e868421c...d69) rather than a reimplementation
of its rules -- so this test can't silently drift from what L0 actually
enforces.

l0_checks.py is not on this branch; it is fetched by content, not by a
branch head that could move, and its bytes are verified against the pinned
sha before anything imports it.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import r1_1_audit_labeller as builder  # noqa: E402

L0_CHECKS_PINNED_SHA = "e868421ce01fc2aca101274611c7157d305a66dd1698329b4176a8a69bfb8d69"
L0_CHECKS_COMMIT = "8e25297"
L0_CHECKS_PATH_IN_REPO = "spikes/run1/r1.1/l0_checks.py"

CANONICAL_RUBRIC_SHA = "f950c385c016e8c0b23b6e8e8941d0448fcb049a31eb7fa404f3ed7f1b4eed23"


def load_l0_checks():
    src = subprocess.run(
        ["git", "show", f"{L0_CHECKS_COMMIT}:{L0_CHECKS_PATH_IN_REPO}"],
        cwd=HERE, capture_output=True, text=True, check=True,
    ).stdout
    got_sha = hashlib.sha256(src.encode("utf-8")).hexdigest()
    if got_sha != L0_CHECKS_PINNED_SHA:
        raise AssertionError(f"l0_checks.py content sha {got_sha} != pinned {L0_CHECKS_PINNED_SHA} -- refusing to use it as the oracle")
    out_path = HERE / "_l0_checks_oracle_FETCHED.py"
    out_path.write_text(src)
    spec = importlib.util.spec_from_file_location("l0_checks_oracle", out_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out_path.unlink()
    return mod


def check_happy_path(l0) -> None:
    grades_by_paper = {
        "PA": {1: "faithful", 2: "wrong-relation"},
        "PB": {1: "faithful"},
    }
    audit_items = [("PA", 1), ("PA", 2), ("PB", 1)]
    ls = builder.build_labeller_set("gemini-audit", grades_by_paper, audit_items)

    if ls["labeller"] != "gemini-audit":
        raise AssertionError(f"labeller name wrong: {ls}")
    if ls["header"] != {"rubric_sha": CANONICAL_RUBRIC_SHA, "blind": True}:
        raise AssertionError(f"header wrong: {ls['header']}")
    expected_records = [
        {"paper": "PA", "n": 1, "grade": "faithful"},
        {"paper": "PA", "n": 2, "grade": "wrong-relation"},
        {"paper": "PB", "n": 1, "grade": "faithful"},
    ]
    if ls["records"] != expected_records:
        raise AssertionError(f"records wrong: {ls['records']}")

    verdict = l0.check_labeller_set(ls, CANONICAL_RUBRIC_SHA, set(audit_items))
    if verdict["status"] != "ok":
        raise AssertionError(f"oracle rejected a well-formed labeller set: {verdict}")
    print("PASS (happy path): builder output accepted as 'ok' by the real check_labeller_set.")


def check_missing_grade_fails_loudly() -> None:
    grades_by_paper = {"PA": {1: "faithful"}}  # PA/2 has no grade
    audit_items = [("PA", 1), ("PA", 2)]
    try:
        builder.build_labeller_set("gemini-audit", grades_by_paper, audit_items)
    except SystemExit as e:
        if "PA" not in str(e) or "2" not in str(e):
            raise AssertionError(f"SystemExit message doesn't name the missing item: {e}")
    except Exception as e:
        raise AssertionError(f"expected SystemExit, got {type(e).__name__}: {e} -- killed-by-crash, not killed-by-guard")
    else:
        raise AssertionError("expected SystemExit for a missing audit-item grade, build_labeller_set succeeded")
    print("PASS (missing grade): rejected with the guard's own SystemExit, naming the missing item.")


def check_wrong_rubric_sha_voids_under_the_oracle(l0) -> None:
    grades_by_paper = {"PA": {1: "faithful"}}
    audit_items = [("PA", 1)]
    ls = builder.build_labeller_set("gemini-audit", grades_by_paper, audit_items, rubric_sha="0" * 64)
    verdict = l0.check_labeller_set(ls, CANONICAL_RUBRIC_SHA, set(audit_items))
    if verdict["status"] != "void":
        raise AssertionError(f"expected void from the oracle on a wrong rubric sha, got: {verdict}")
    print("PASS (wrong rubric sha): the real check_labeller_set reads it as void, as expected.")


def check_blind_defaults_true_and_is_overridable() -> None:
    grades_by_paper = {"PA": {1: "faithful"}}
    audit_items = [("PA", 1)]
    default_ls = builder.build_labeller_set("gemini-audit", grades_by_paper, audit_items)
    if default_ls["header"]["blind"] is not True:
        raise AssertionError(f"blind should default to True: {default_ls['header']}")
    explicit_ls = builder.build_labeller_set("hand-labeller", grades_by_paper, audit_items, blind=False)
    if explicit_ls["header"]["blind"] is not False:
        raise AssertionError(f"blind=False override did not take: {explicit_ls['header']}")
    print("PASS (blind field): defaults true (qbp-architecture seq 327), explicit override to false also works.")


def main() -> int:
    l0 = load_l0_checks()
    check_happy_path(l0)
    check_missing_grade_fails_loudly()
    check_wrong_rubric_sha_voids_under_the_oracle(l0)
    check_blind_defaults_true_and_is_overridable()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
