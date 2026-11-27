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


def _write_meta(subdir: Path, stem: str, three_field: int, four_field: int | None = None) -> None:
    subdir.mkdir(parents=True, exist_ok=True)
    if four_field is None:
        four_field = three_field
    (subdir / f"{stem}.meta.json").write_text(
        json.dumps({"usage_sums": {"three_field": three_field, "four_field": four_field}})
    )


def check_gemini_token_budget_boundary() -> None:
    """The guard trips exactly when cumulative three-field spend across
    every s5_r1.1_* dir under root, plus the per-call worst case, would
    exceed the budget (qbp-architecture seq 350/351/355) -- not a call
    before, not a call after."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        out_dir = root / "s5_r1.1_checker"
        budget = 100_000
        worst = driver.GEMINI_PER_CALL_WORST_CASE

        # Right at the boundary: spend + worst == budget must NOT trip.
        _write_meta(out_dir, "a", budget - worst)
        driver.check_gemini_token_budget(out_dir, budget, root)
        print(
            f"PASS (budget boundary, at limit): spend {budget - worst} + worst {worst} "
            f"== budget {budget}, not tripped."
        )

        # One token over: spend + worst == budget + 1 must trip.
        _write_meta(out_dir, "b", 1)
        expect_system_exit(
            lambda: driver.check_gemini_token_budget(out_dir, budget, root),
            "Gemini cumulative token guard tripped",
            "budget boundary, one over",
        )


def check_gemini_token_budget_missing_usage_sums_rejected() -> None:
    """A meta.json with neither usage_sums nor a sibling response_RAW.json
    to recompute from must fail loud, never silently count as zero
    spend."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        out_dir = root / "s5_r1.1_checker"
        out_dir.mkdir(parents=True)
        (out_dir / "old.meta.json").write_text(json.dumps({"label": "X"}))
        expect_system_exit(
            lambda: driver.check_gemini_token_budget(out_dir, 100_000, root),
            "has neither usage_sums nor a sibling",
            "missing usage_sums rejected",
        )


def check_gemini_token_budget_falls_back_to_response_raw() -> None:
    """A meta.json without usage_sums (written before 70907e3) is still
    counted, via the sibling response_RAW.json's usage_metadata
    (qbp-architecture seq 355)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        out_dir = root / "s5_r1.1_checker"
        out_dir.mkdir(parents=True)
        (out_dir / "old.meta.json").write_text(json.dumps({"label": "X"}))
        (out_dir / "old.response_RAW.json").write_text(json.dumps({
            "usage_metadata": {
                "prompt_token_count": 100,
                "cached_content_token_count": 40,
                "thoughts_token_count": 20,
                "candidates_token_count": 5,
            }
        }))
        spend = driver.cumulative_gemini_spend(root)
        if spend != {"four_field": 165, "three_field": 125}:
            raise AssertionError(f"fallback sums wrong: {spend}")
    print("PASS (fallback to response_RAW.json): a meta.json without usage_sums is still counted correctly, from its sibling's usage_metadata.")


def check_out_dir_outside_root_refused() -> None:
    """An out_dir that isn't under root/s5_r1.1_*/ is refused outright,
    before any spend is even computed (qbp-architecture seq 355)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "spikes_run1"
        root.mkdir()
        outside = Path(tmp) / "somewhere_else"
        expect_system_exit(
            lambda: driver.check_gemini_token_budget(outside, 100_000, root),
            "is not under",
            "out dir outside root refused",
        )


def check_cross_component_spend_is_shared() -> None:
    """Spend already incurred in one component's directory (e.g. the
    checker) must trip another component's guard (e.g. the labeller) when
    both share the same root -- the 1.65M kill line is ONE line for all of
    round 1.1, not one per directory (qbp-architecture seq 355, the
    blocking scope correction to seq 350)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checker_dir = root / "s5_r1.1_checker"
        labeller_dir = root / "s5_r1.1_labeller"
        budget = 100_000
        _write_meta(checker_dir, "a", budget)  # checker dir alone already at the full budget
        expect_system_exit(
            lambda: driver.check_gemini_token_budget(labeller_dir, budget, root),
            "Gemini cumulative token guard tripped",
            "cross-component spend shared across sibling dirs",
        )


def check_real_probe_counted_in_cumulative_spend() -> None:
    """The actual committed §8b probe metas (3577576, written before
    usage_sums existed) are counted via the response_RAW.json fallback --
    expected three-field total 108,542 (qbp-architecture seq 355)."""
    probe_dir = driver.HERE / "s5_r1.1_probe" / "checker"
    probe_total = sum(
        driver.usage_sums_from_meta_file(p)["three_field"] for p in sorted(probe_dir.glob("*.meta.json"))
    )
    if probe_total != 108_542:
        raise AssertionError(f"probe three-field total wrong: {probe_total} != 108542")

    spend = driver.cumulative_gemini_spend(driver.HERE)
    if spend["three_field"] < probe_total:
        raise AssertionError(
            f"cumulative_gemini_spend(HERE) ({spend}) does not include the probe dir's spend ({probe_total})"
        )
    print(
        "PASS (real probe counted): the committed §8b probe metas sum to exactly 108,542 "
        "via the fallback, and are included in cumulative_gemini_spend(HERE)."
    )


def check_single_dir_scope_mutant_killed() -> None:
    """Mutation check: a mutant that scopes the guard back to just the one
    out_dir passed in (the pre-seq-355 per-directory behavior) must be
    caught -- demonstrated by showing it wrongly misses the checker dir's
    spend when checking the labeller dir's budget, which the real
    cross-root scan (and the cross-component test above) correctly
    catches."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checker_dir = root / "s5_r1.1_checker"
        labeller_dir = root / "s5_r1.1_labeller"
        budget = 100_000
        _write_meta(checker_dir, "a", budget)

        try:
            driver.check_gemini_token_budget(labeller_dir, budget, root)
        except SystemExit:
            pass
        else:
            raise AssertionError("real check_gemini_token_budget unexpectedly missed the checker dir's spend")

        def mutant_scoped_to_out_dir(out_dir, budget_=driver.GEMINI_TOKEN_BUDGET_DEFAULT, root_=driver.HERE):
            # BUG: scans cumulative_gemini_spend(out_dir) -- the single
            # directory it was called for -- instead of the whole root.
            driver.require_round_1_1_out_dir(Path(out_dir), Path(root_))
            spend = driver.cumulative_gemini_spend(Path(out_dir))
            if spend["three_field"] + driver.GEMINI_PER_CALL_WORST_CASE > budget_:
                raise SystemExit("mutant tripped (should not happen in this probe)")

        original = driver.check_gemini_token_budget
        driver.check_gemini_token_budget = mutant_scoped_to_out_dir
        try:
            try:
                driver.check_gemini_token_budget(labeller_dir, budget, root)
            except SystemExit as e:
                raise AssertionError(
                    f"single-dir-scope mutant was still caught ({e}) -- this probe no longer "
                    "demonstrates cross-root scanning as load-bearing; rewrite it"
                )
        finally:
            driver.check_gemini_token_budget = original
    print(
        "PASS (single-dir-scope mutant demonstrated killed): scoping the guard to just out_dir "
        "instead of the shared root wrongly misses the checker dir's spend when checking the "
        "labeller dir -- confirms the cross-root scan is load-bearing."
    )


def check_opus_rated_meta_ignored() -> None:
    """A meta declaring a non-Gemini rater (the Opus verifier's own metas,
    sharing the same s5_r1.1_* root) is skipped entirely -- never counted,
    never rejected for lacking Gemini usage fields (qbp-architecture
    seq 357)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checker_dir = root / "s5_r1.1_checker"
        verifier_dir = root / "s5_r1.1_verifier"
        verifier_dir.mkdir(parents=True)
        (verifier_dir / "run1.meta.json").write_text(json.dumps({"rater": "opus-verifier-v1"}))
        _write_meta(checker_dir, "a", 1000)

        spend = driver.cumulative_gemini_spend(root)
        if spend != {"four_field": 1000, "three_field": 1000}:
            raise AssertionError(f"opus-rated meta was not ignored cleanly: {spend}")
    print("PASS (opus-rated meta ignored): a non-Gemini-rated meta is skipped entirely, not rejected and not counted.")


def check_untagged_meta_with_no_usage_still_refused() -> None:
    """A meta with NO rater tag at all is not exempted by the rater check
    -- it must still resolve to real Gemini usage data or be rejected
    loudly, fail-closed (qbp-architecture seq 357)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        out_dir = root / "s5_r1.1_checker"
        out_dir.mkdir(parents=True)
        (out_dir / "mystery.meta.json").write_text(json.dumps({"label": "X"}))
        expect_system_exit(
            lambda: driver.cumulative_gemini_spend(root),
            "has neither usage_sums nor a sibling",
            "untagged meta with no usage still refused",
        )


def check_rater_skip_mutant_killed() -> None:
    """Mutation check: a mutant that skips EVERY meta carrying a rater tag
    -- gemini-rated ones included, not just non-Gemini ones -- must be
    caught, demonstrated by showing it wrongly drops a real gemini-rated
    meta's spend that the real check correctly keeps."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        out_dir = root / "s5_r1.1_checker"
        out_dir.mkdir(parents=True)
        (out_dir / "a.meta.json").write_text(
            json.dumps({"rater": "gemini-checker-v1", "usage_sums": {"three_field": 1000, "four_field": 1200}})
        )

        real_spend = driver.cumulative_gemini_spend(root)
        if real_spend["three_field"] != 1000:
            raise AssertionError(f"real cumulative_gemini_spend did not count the gemini-rated meta: {real_spend}")

        original = driver.meta_belongs_to_gemini
        driver.meta_belongs_to_gemini = lambda meta: meta.get("rater") is None  # BUG: drops every rated meta
        try:
            mutant_spend = driver.cumulative_gemini_spend(root)
            if mutant_spend["three_field"] != 0:
                raise AssertionError(
                    f"mutant unexpectedly still counted the gemini-rated meta: {mutant_spend} -- "
                    "this probe no longer demonstrates the rater check as load-bearing; rewrite it"
                )
        finally:
            driver.meta_belongs_to_gemini = original
    print(
        "PASS (rater-skip mutant demonstrated killed): a mutant that drops EVERY rated meta "
        "(gemini-rated ones included) wrongly misses real spend that the real rater check "
        "correctly keeps -- confirms checking the rater's PREFIX, not just its absence, is load-bearing."
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
    check_gemini_token_budget_falls_back_to_response_raw()
    check_out_dir_outside_root_refused()
    check_cross_component_spend_is_shared()
    check_real_probe_counted_in_cumulative_spend()
    check_single_dir_scope_mutant_killed()
    check_opus_rated_meta_ignored()
    check_untagged_meta_with_no_usage_still_refused()
    check_rater_skip_mutant_killed()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
