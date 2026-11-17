#!/usr/bin/env python3
"""Known-answer test for r1_1_checker_driver.py's build_plan(): pure logic,
no subprocess, no network, no real sample/manifest files -- a small
synthetic fixture with a known correct plan.
"""
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import r1_1_checker_driver as driver  # noqa: E402

FIXTURE_SAMPLES = {
    "seed": 1,
    "probe_paper": "PX",
    "double_graded": [["PA", 1], ["PA", 2], ["PB", 1], ["PB", 2], ["PX", 1], ["PX", 2]],
    "calibration": [["PA", 1], ["PB", 1], ["PX", 1]],
    "heldout": [["PA", 2], ["PB", 2], ["PX", 2]],
}
FIXTURE_MANIFEST = {
    "PA": ("s5_grader_inputs_A2/PA.grader_input.txt", "sha-PA"),
    "PB": ("s5_grader_inputs_A2/PB.grader_input.txt", "sha-PB"),
    "PX": ("s5_grader_inputs_A2/PX.grader_input.txt", "sha-PX"),
}


def fixture_samples_text() -> str:
    import json

    return json.dumps(FIXTURE_SAMPLES)


def check_happy_path() -> None:
    import json

    text = fixture_samples_text()
    expected_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    plan = driver.build_plan(
        text,
        FIXTURE_MANIFEST,
        Path("grader_inputs"),
        Path("rubric.txt"),
        "rubric-sha",
        samples_expected_sha=expected_sha,
    )
    # 3 papers double-graded + 5 probe runs on PX = 8 calls.
    if len(plan) != 8:
        raise AssertionError(f"expected 8 plan entries, got {len(plan)}: {plan}")
    dg = [c for c in plan if c["kind"] == "double_graded"]
    probe = [c for c in plan if c["kind"] == "probe"]
    if sorted(c["label"] for c in dg) != ["PA", "PB", "PX"]:
        raise AssertionError(f"double-graded labels wrong: {[c['label'] for c in dg]}")
    if len(probe) != 5 or any(c["label"] != "PX" for c in probe):
        raise AssertionError(f"probe calls wrong: {probe}")
    if sorted(c["run_index"] for c in probe) != [0, 1, 2, 3, 4]:
        raise AssertionError(f"probe run_index set wrong: {[c['run_index'] for c in probe]}")
    # The probe's 5 requests must be identical to each other (same rubric,
    # same input) and distinguishable only by run_index/label, per
    # qbp-architecture seq 5267 -- never by changing the input/rubric per run.
    probe_fingerprints = {(c["rubric"], c["rubric_sha"], c["input"], c["input_sha"]) for c in probe}
    if len(probe_fingerprints) != 1:
        raise AssertionError(f"probe requests are not identical across runs: {probe_fingerprints}")
    print("PASS (happy path): 3 double-graded + 5 probe = 8 calls, probe runs identical except run_index.")


def expect_system_exit(fn, expected_substring: str, label: str) -> None:
    """Assert fn() raises SystemExit whose message contains
    expected_substring -- i.e. the guard itself fired, not some unrelated
    exception that happens to also be non-zero (qbp-architecture, live-test
    seq 5295: a KeyError crash is killed-by-crash, not killed-by-guard)."""
    try:
        fn()
    except SystemExit as e:
        msg = str(e)
        if expected_substring not in msg:
            raise AssertionError(
                f"{label}: SystemExit message {msg!r} does not contain {expected_substring!r}"
            )
    except Exception as e:
        raise AssertionError(
            f"{label}: expected SystemExit containing {expected_substring!r}, "
            f"got {type(e).__name__}: {e} -- this is killed-by-crash, not killed-by-guard"
        )
    else:
        raise AssertionError(f"{label}: expected SystemExit containing {expected_substring!r}, build_plan succeeded")
    print(f"PASS ({label}): rejected with the guard's own SystemExit, containing {expected_substring!r}.")


def check_samples_sha_mismatch() -> None:
    text = fixture_samples_text()
    expect_system_exit(
        lambda: driver.build_plan(
            text, FIXTURE_MANIFEST, Path("x"), Path("r"), "s", samples_expected_sha="0" * 64
        ),
        "samples sha mismatch",
        "samples sha mismatch",
    )


def check_manifest_sample_mismatch() -> None:
    text = fixture_samples_text()
    expected_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    bad_manifest = dict(FIXTURE_MANIFEST)
    del bad_manifest["PB"]  # manifest now missing a paper the samples reference
    expect_system_exit(
        lambda: driver.build_plan(
            text, bad_manifest, Path("x"), Path("r"), "s", samples_expected_sha=expected_sha
        ),
        "manifest/sample paper mismatch",
        "manifest mismatch",
    )


def check_probe_paper_not_in_manifest() -> None:
    import json

    samples = dict(FIXTURE_SAMPLES)
    samples["probe_paper"] = "NOT-IN-MANIFEST"
    text = json.dumps(samples)
    expected_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    expect_system_exit(
        lambda: driver.build_plan(
            text, FIXTURE_MANIFEST, Path("x"), Path("r"), "s", samples_expected_sha=expected_sha
        ),
        "not in the grader-input manifest",
        "probe paper missing",
    )


def main() -> int:
    check_happy_path()
    check_samples_sha_mismatch()
    check_manifest_sample_mismatch()
    check_probe_paper_not_in_manifest()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
