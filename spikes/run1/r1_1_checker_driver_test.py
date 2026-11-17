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


def check_samples_sha_mismatch() -> None:
    text = fixture_samples_text()
    try:
        driver.build_plan(
            text, FIXTURE_MANIFEST, Path("x"), Path("r"), "s", samples_expected_sha="0" * 64
        )
    except SystemExit:
        pass
    else:
        raise AssertionError("build_plan did not reject a samples sha mismatch")
    print("PASS (samples sha mismatch): rejected as expected.")


def check_manifest_sample_mismatch() -> None:
    import json

    text = fixture_samples_text()
    expected_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    bad_manifest = dict(FIXTURE_MANIFEST)
    del bad_manifest["PB"]  # manifest now missing a paper the samples reference
    try:
        driver.build_plan(
            text, bad_manifest, Path("x"), Path("r"), "s", samples_expected_sha=expected_sha
        )
    except SystemExit:
        pass
    else:
        raise AssertionError("build_plan did not reject a manifest/sample paper mismatch")
    print("PASS (manifest mismatch): rejected as expected.")


def check_probe_paper_not_in_manifest() -> None:
    import json

    samples = dict(FIXTURE_SAMPLES)
    samples["probe_paper"] = "NOT-IN-MANIFEST"
    text = json.dumps(samples)
    expected_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    try:
        driver.build_plan(
            text, FIXTURE_MANIFEST, Path("x"), Path("r"), "s", samples_expected_sha=expected_sha
        )
    except SystemExit:
        pass
    else:
        raise AssertionError("build_plan did not reject a probe paper missing from the manifest")
    print("PASS (probe paper missing): rejected as expected.")


def main() -> int:
    check_happy_path()
    check_samples_sha_mismatch()
    check_manifest_sample_mismatch()
    check_probe_paper_not_in_manifest()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
