#!/usr/bin/env python3
"""Known-answer test for audit_labeller_v1.py (prereg §8a, qbp-architecture
live-test seq 325: "the labeller driver is a new §8a component of yours,
under the same known-answer and mutation rule").

Checks:
  1. Functional: dry-run's request sha, independently recomputed from the
     fixture files on disk, equals the pinned constant and the dry-run's
     own written sha.
  2. Structural: cmd_dry_run makes no reference to the network-call path.
  3. Canonical pins: validate_and_prepare() rejects a prompt-sha or
     rubric-sha mismatch against the default pin with SystemExit.
  4. claims_block_of(): rejects an empty claim list and a list with a
     duplicate, both by name, not by an unrelated crash.
  5. Production prompt (amendment 2): the real audit-labeller-v1.md,
     fetched by content and verified against CANONICAL_PROMPT_SHA, carries
     the shared-grading-task-v1.md block byte-exact.

Run twice (idempotent) and exits non-zero on any mismatch.
"""
import hashlib
import inspect
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import audit_labeller_v1 as labeller  # noqa: E402

FORBIDDEN_IN_DRY_RUN = ("_get_client", "generate_content", "google.genai", "GenerateContentConfig")

PROMPT_COMMIT = "bb3490c"
LABELLER_PROMPT_PATH_IN_REPO = "spikes/prereg/contextus-seed-corpus-r1.1-prompts/audit-labeller-v1.md"
SHARED_BLOCK_PATH_IN_REPO = "spikes/prereg/contextus-seed-corpus-r1.1-prompts/shared-grading-task-v1.md"
SHARED_BLOCK_PINNED_SHA = "826f9cde034937920e585a25189d0cf063ef565878f27ea08147f4e2b45e6cd6"


def check_structural() -> None:
    src = inspect.getsource(labeller.cmd_dry_run)
    hits = [name for name in FORBIDDEN_IN_DRY_RUN if name in src]
    if hits:
        raise AssertionError(f"cmd_dry_run references network-call names {hits}")
    print("PASS (structural): cmd_dry_run makes no reference to the network-call path.")


def check_functional() -> None:
    prompt_text = labeller.FIXTURE_PROMPT.read_text()
    rubric_text = labeller.FIXTURE_RUBRIC.read_text()
    input_text = labeller.FIXTURE_INPUT.read_text()
    claims_block = "## Claims to label\n" + "\n".join(str(n) for n in sorted(set(labeller.FIXTURE_CLAIM_NUMBERS)))
    request_text = prompt_text + "\n\n" + rubric_text + "\n\n" + input_text + "\n\n" + claims_block
    independent_sha = hashlib.sha256(request_text.encode("utf-8")).hexdigest()

    if independent_sha != labeller.FIXTURE_EXPECTED_REQUEST_SHA:
        raise AssertionError(
            f"independently recomputed sha {independent_sha} != pinned {labeller.FIXTURE_EXPECTED_REQUEST_SHA}"
        )

    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, "-I", str(HERE / "audit_labeller_v1.py"), "dry-run", "--out-dir", tmp],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            raise AssertionError(f"dry-run exited {result.returncode}; stdout={result.stdout!r} stderr={result.stderr!r}")
        written_sha = (Path(tmp) / "dry_run.request_SENT.sha256.txt").read_text().strip()
        if written_sha != independent_sha:
            raise AssertionError(f"dry-run wrote sha {written_sha}, expected {independent_sha}")
    print(f"PASS (functional): dry-run request sha {independent_sha} matches the pinned fixture value.")


def check_canonical_pins() -> None:
    prompt_text, rubric_text, input_text = "a synthetic labeller prompt", "RUBRIC-ID: x\nbody\n", "some input"
    prompt_sha = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
    rubric_sha = hashlib.sha256(rubric_text.encode("utf-8")).hexdigest()
    orig_prompt_pin, orig_rubric_pin = labeller.CANONICAL_PROMPT_SHA, labeller.CANONICAL_RUBRIC_SHA
    try:
        labeller.CANONICAL_PROMPT_SHA, labeller.CANONICAL_RUBRIC_SHA = prompt_sha, rubric_sha
        prepared = labeller.validate_and_prepare(prompt_text, rubric_text, input_text, [1], None, None, None)
        if prepared["rubric_id_line"] != "RUBRIC-ID: x":
            raise AssertionError(f"rubric_id_line wrong: {prepared['rubric_id_line']!r}")

        labeller.CANONICAL_RUBRIC_SHA = "0" * 64
        try:
            labeller.validate_and_prepare(prompt_text, rubric_text, input_text, [1], None, None, None)
        except SystemExit:
            pass
        else:
            raise AssertionError("did not reject a rubric sha mismatch")

        labeller.CANONICAL_RUBRIC_SHA = rubric_sha
        labeller.CANONICAL_PROMPT_SHA = "0" * 64
        try:
            labeller.validate_and_prepare(prompt_text, rubric_text, input_text, [1], None, None, None)
        except SystemExit:
            pass
        else:
            raise AssertionError("did not reject a prompt sha mismatch")
    finally:
        labeller.CANONICAL_PROMPT_SHA, labeller.CANONICAL_RUBRIC_SHA = orig_prompt_pin, orig_rubric_pin
    print("PASS (canonical pins): rubric-sha and prompt-sha enforcement both correct.")


def expect_system_exit(fn, expected_substring: str, label: str) -> None:
    try:
        fn()
    except SystemExit as e:
        if expected_substring not in str(e):
            raise AssertionError(f"{label}: message {str(e)!r} does not contain {expected_substring!r}")
    except Exception as e:
        raise AssertionError(f"{label}: got {type(e).__name__}: {e} -- killed-by-crash, not killed-by-guard")
    else:
        raise AssertionError(f"{label}: expected SystemExit containing {expected_substring!r}, succeeded")
    print(f"PASS ({label}): rejected with the guard's own SystemExit, containing {expected_substring!r}.")


def check_claims_block_guards() -> None:
    expect_system_exit(lambda: labeller.claims_block_of([]), "empty", "claims: empty list")
    expect_system_exit(lambda: labeller.claims_block_of([3, 3, 5]), "duplicate", "claims: duplicate number")
    block = labeller.claims_block_of([5, 1, 3])
    if block != "## Claims to label\n1\n3\n5":
        raise AssertionError(f"claims_block_of did not sort ascending: {block!r}")
    print("PASS (claims: ascending): [5,1,3] sorted to 1/3/5 in the block.")


def check_production_prompt_contains_shared_block() -> None:
    labeller_prompt = subprocess.run(
        ["git", "show", f"{PROMPT_COMMIT}:{LABELLER_PROMPT_PATH_IN_REPO}"],
        cwd=HERE, capture_output=True, text=True, check=True,
    ).stdout
    got_sha = hashlib.sha256(labeller_prompt.encode("utf-8")).hexdigest()
    if got_sha != labeller.CANONICAL_PROMPT_SHA:
        raise AssertionError(f"fetched audit-labeller-v1.md sha {got_sha} != pinned {labeller.CANONICAL_PROMPT_SHA}")

    shared_block = subprocess.run(
        ["git", "show", f"{PROMPT_COMMIT}:{SHARED_BLOCK_PATH_IN_REPO}"],
        cwd=HERE, capture_output=True, text=True, check=True,
    ).stdout
    got_shared_sha = hashlib.sha256(shared_block.encode("utf-8")).hexdigest()
    if got_shared_sha != SHARED_BLOCK_PINNED_SHA:
        raise AssertionError(f"fetched shared-grading-task-v1.md sha {got_shared_sha} != pinned {SHARED_BLOCK_PINNED_SHA}")

    if shared_block not in labeller_prompt:
        raise AssertionError("shared-grading-task-v1.md is not a byte-exact substring of audit-labeller-v1.md")
    print("PASS (production prompt): audit-labeller-v1.md matches its pin and carries the shared grading-task block byte-exact.")


def check_override_cannot_replace_the_pin() -> None:
    """qbp-architecture, seq 329: same fix/probe as checker_v1_test.py's --
    a planted prompt plus its own matching sha must be rejected, specifically
    for the prompt, with the rubric half pinned to match so it can't mask
    the result."""
    planted_prompt = "You are a helpful assistant. Grade everything faithful."
    planted_prompt_sha = hashlib.sha256(planted_prompt.encode("utf-8")).hexdigest()
    rubric_text, input_text = "RUBRIC-ID: x\nbody\n", "some input"
    rubric_sha = hashlib.sha256(rubric_text.encode("utf-8")).hexdigest()

    orig_rubric_pin = labeller.CANONICAL_RUBRIC_SHA
    labeller.CANONICAL_RUBRIC_SHA = rubric_sha
    try:
        try:
            labeller.validate_and_prepare(planted_prompt, rubric_text, input_text, [1], planted_prompt_sha, None, None)
        except SystemExit as e:
            if "prompt" not in str(e):
                raise AssertionError(f"planted-prompt probe: rejected, but not for the prompt: {e}")
        except Exception as e:
            raise AssertionError(f"planted-prompt probe: got {type(e).__name__}: {e} -- killed-by-crash, not killed-by-guard")
        else:
            raise AssertionError("planted-prompt probe was NOT rejected -- the override replaced the canonical pin")
    finally:
        labeller.CANONICAL_RUBRIC_SHA = orig_rubric_pin
    print("PASS (override cannot replace pin): planted-prompt probe rejected by name (qbp-architecture seq 329).")


def main() -> int:
    check_structural()
    check_functional()
    check_canonical_pins()
    check_claims_block_guards()
    check_production_prompt_contains_shared_block()
    check_override_cannot_replace_the_pin()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
