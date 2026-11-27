#!/usr/bin/env python3
"""Known-answer test for r1_1_checker_driver.py's build_plan(): pure logic,
no subprocess, no network, no real sample/manifest files -- a small
synthetic fixture with a known correct plan.
"""
import hashlib
import json
import sys
import tempfile
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
        Path("prompt.txt"),
        "prompt-sha",
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
    # The probe's 5 requests must be identical to each other (same prompt,
    # same rubric, same input) and distinguishable only by run_index/label,
    # per qbp-architecture seq 5267 -- never by changing the
    # prompt/input/rubric per run.
    probe_fingerprints = {
        (c["prompt"], c["prompt_sha"], c["rubric"], c["rubric_sha"], c["input"], c["input_sha"])
        for c in probe
    }
    if len(probe_fingerprints) != 1:
        raise AssertionError(f"probe requests are not identical across runs: {probe_fingerprints}")
    if any(c["prompt"] != "prompt.txt" or c["prompt_sha"] != "prompt-sha" for c in plan):
        raise AssertionError(f"prompt/prompt_sha not threaded into every plan entry: {plan}")
    print("PASS (happy path): 3 double-graded + 5 probe = 8 calls, probe runs identical except run_index, prompt threaded through.")


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
            text, FIXTURE_MANIFEST, Path("x"), Path("r"), "s", Path("p"), "ps", samples_expected_sha="0" * 64
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
            text, bad_manifest, Path("x"), Path("r"), "s", Path("p"), "ps", samples_expected_sha=expected_sha
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
            text, FIXTURE_MANIFEST, Path("x"), Path("r"), "s", Path("p"), "ps", samples_expected_sha=expected_sha
        ),
        "not in the grader-input manifest",
        "probe paper missing",
    )


def check_build_call_cmd_uses_gemini_venv_python() -> None:
    """Live-fire finding, seq 341: execute_plan used to spawn checker_v1.py
    with `sys.executable`, which lacks google-genai on plain system python3
    and silently fails every real call (never caught by gate 0, which is
    dry-run-only). build_call_cmd must point at the gemini MCP server's own
    venv interpreter instead."""
    if not driver.GEMINI_VENV_PYTHON.is_file():
        raise AssertionError(
            f"GEMINI_VENV_PYTHON does not exist on this host: {driver.GEMINI_VENV_PYTHON} "
            "-- fix the constant or rebuild the venv per the gemini MCP README"
        )
    call = {
        "prompt": "p.txt", "prompt_sha": "ps", "rubric": "r.txt", "rubric_sha": "rs",
        "input": "i.txt", "input_sha": "is", "label": "PX", "run_index": 2,
    }
    cmd = driver.build_call_cmd(call, "out")
    if cmd[0] != str(driver.GEMINI_VENV_PYTHON):
        raise AssertionError(f"build_call_cmd did not use GEMINI_VENV_PYTHON as the interpreter: {cmd}")
    if "--run-index" not in cmd or cmd[cmd.index("--run-index") + 1] != "2":
        raise AssertionError(f"run_index not threaded into the command: {cmd}")
    print("PASS (gemini venv python): build_call_cmd uses the gemini MCP server's own venv interpreter, which exists on this host.")


def check_build_call_cmd_guards_missing_interpreter() -> None:
    """Mutation check: if GEMINI_VENV_PYTHON pointed at a nonexistent path,
    build_call_cmd must refuse loudly rather than silently fall back to a
    different interpreter (the exact failure mode this fix closes)."""
    original = driver.GEMINI_VENV_PYTHON
    driver.GEMINI_VENV_PYTHON = Path("/nonexistent/gemini-venv/bin/python")
    try:
        call = {
            "prompt": "p.txt", "prompt_sha": "ps", "rubric": "r.txt", "rubric_sha": "rs",
            "input": "i.txt", "input_sha": "is", "label": "PX", "run_index": None,
        }
        expect_system_exit(
            lambda: driver.build_call_cmd(call, "out"),
            "gemini venv python not found",
            "missing gemini venv interpreter",
        )
    finally:
        driver.GEMINI_VENV_PYTHON = original


def _write_meta(out_dir: Path, stem: str, three_field: int, four_field: int | None = None) -> None:
    if four_field is None:
        four_field = three_field
    (out_dir / f"{stem}.meta.json").write_text(
        json.dumps({"usage_sums": {"three_field": three_field, "four_field": four_field}})
    )


def check_gemini_token_budget_boundary() -> None:
    """The guard trips exactly when cumulative three-field spend + the
    per-call worst case would exceed the budget (qbp-architecture seq
    350/351) -- not a call before, not a call after."""
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        budget = 100_000
        worst = driver.GEMINI_PER_CALL_WORST_CASE

        # Right at the boundary: spend + worst == budget must NOT trip.
        _write_meta(out_dir, "a", budget - worst)
        driver.check_gemini_token_budget(out_dir, budget)
        print(
            f"PASS (budget boundary, at limit): spend {budget - worst} + worst {worst} "
            f"== budget {budget}, not tripped."
        )

        # One token over: spend + worst == budget + 1 must trip.
        _write_meta(out_dir, "b", 1)
        expect_system_exit(
            lambda: driver.check_gemini_token_budget(out_dir, budget),
            "Gemini cumulative token guard tripped",
            "budget boundary, one over",
        )


def check_gemini_token_budget_missing_usage_sums_rejected() -> None:
    """A meta.json written before this fix (no usage_sums) must fail loud,
    never silently count as zero spend."""
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        (out_dir / "old.meta.json").write_text(json.dumps({"label": "X"}))
        expect_system_exit(
            lambda: driver.check_gemini_token_budget(out_dir, 100_000),
            "has no usage_sums",
            "missing usage_sums rejected",
        )


def check_gemini_token_budget_mutant_killed() -> None:
    """Mutation check: a mutant that feeds the guard zero spend (as if
    cumulative_gemini_spend never actually read the meta.json files) must
    be caught -- demonstrated by showing it wrongly lets an over-budget run
    proceed that the real guard (and the boundary test above) correctly
    refuses."""
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        budget = 100_000
        _write_meta(out_dir, "a", budget)  # already at the full budget alone

        try:
            driver.check_gemini_token_budget(out_dir, budget)
        except SystemExit:
            pass
        else:
            raise AssertionError("real check_gemini_token_budget unexpectedly accepted an over-budget spend")

        original = driver.cumulative_gemini_spend
        driver.cumulative_gemini_spend = lambda _out_dir: {"four_field": 0, "three_field": 0}
        try:
            try:
                driver.check_gemini_token_budget(out_dir, budget)
            except SystemExit as e:
                raise AssertionError(
                    f"zero-spend mutant was still caught ({e}) -- this probe no longer "
                    "demonstrates reading real cumulative spend as load-bearing; rewrite it"
                )
        finally:
            driver.cumulative_gemini_spend = original
    print(
        "PASS (budget mutant demonstrated killed): a guard fed zero spend (as if "
        "cumulative_gemini_spend never read the real meta.json files) wrongly lets an "
        "over-budget run proceed, which the real guard (and the boundary test above) "
        "correctly refuses -- confirms reading real spend is load-bearing."
    )


def main() -> int:
    check_happy_path()
    check_samples_sha_mismatch()
    check_manifest_sample_mismatch()
    check_probe_paper_not_in_manifest()
    check_build_call_cmd_uses_gemini_venv_python()
    check_build_call_cmd_guards_missing_interpreter()
    check_gemini_token_budget_boundary()
    check_gemini_token_budget_missing_usage_sums_rejected()
    check_gemini_token_budget_mutant_killed()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
