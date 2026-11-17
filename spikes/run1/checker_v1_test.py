#!/usr/bin/env python3
"""Known-answer test for checker_v1.py's dry-run mode (prereg §8a row:
"request bytes are hashed before the call; a dry run against a fixture
gives the expected request sha with no network call").

Two checks, both of which must pass:
  1. Functional: dry-run's request sha, independently recomputed from the
     fixture files on disk (not from checker_v1's pinned constant), equals
     checker_v1's pinned constant AND equals the dry-run's own computed and
     written sha.
  2. Structural: cmd_dry_run's source contains no reference to the network
     call path (_get_client, generate_content, google.genai) -- so "no
     network call" is a property the code enforces, not an observation
     about one run that a later edit could silently break.

Run twice (idempotent: this test only reads files and writes to a fresh
temp dir each run, review_ledger_writers convention) and exits non-zero on
any mismatch.
"""
import hashlib
import inspect
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import checker_v1  # noqa: E402

FORBIDDEN_IN_DRY_RUN = ("_get_client", "generate_content", "google.genai", "GenerateContentConfig")


def check_structural() -> None:
    src = inspect.getsource(checker_v1.cmd_dry_run)
    hits = [name for name in FORBIDDEN_IN_DRY_RUN if name in src]
    if hits:
        raise AssertionError(
            f"cmd_dry_run references network-call names {hits} -- "
            "this would make 'no network call' an accident, not a guarantee"
        )
    print("PASS (structural): cmd_dry_run makes no reference to the network-call path.")


def check_functional() -> None:
    rubric_text = checker_v1.FIXTURE_RUBRIC.read_text()
    input_text = checker_v1.FIXTURE_INPUT.read_text()
    request_text = rubric_text + "\n\n" + input_text
    independent_sha = hashlib.sha256(request_text.encode("utf-8")).hexdigest()

    if independent_sha != checker_v1.FIXTURE_EXPECTED_REQUEST_SHA:
        raise AssertionError(
            f"independently recomputed sha {independent_sha} != "
            f"checker_v1's pinned constant {checker_v1.FIXTURE_EXPECTED_REQUEST_SHA} "
            "-- the pin is stale (a fixture file or build_request() changed)"
        )

    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, "-I", str(HERE / "checker_v1.py"), "dry-run", "--out-dir", tmp],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise AssertionError(
                f"dry-run exited {result.returncode}; stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        written_sha = (Path(tmp) / "dry_run.request_SENT.sha256.txt").read_text().strip()
        if written_sha != independent_sha:
            raise AssertionError(
                f"dry-run wrote sha {written_sha}, expected {independent_sha}"
            )
    print(f"PASS (functional): dry-run request sha {independent_sha} matches the pinned fixture value.")


def check_canonical_rubric_pin() -> None:
    """validate_and_prepare() is the pure logic cmd_grade calls before any
    network access -- exercised directly here, no _get_client, no call."""
    rubric_text = "RUBRIC-ID: relation-types-v1 source_sha256=abc registry_sha256=def\nbody\n"
    input_text = "some input"

    # Right sha (the canonical pin itself): passes, and the RUBRIC-ID line
    # is extracted verbatim for the output record.
    rubric_sha = hashlib.sha256(rubric_text.encode("utf-8")).hexdigest()
    checker_v1.CANONICAL_RUBRIC_SHA = rubric_sha  # patch for this synthetic text
    try:
        prepared = checker_v1.validate_and_prepare(rubric_text, input_text, None, None)
    finally:
        pass
    if prepared["rubric_id_line"] != "RUBRIC-ID: relation-types-v1 source_sha256=abc registry_sha256=def":
        raise AssertionError(f"rubric_id_line not extracted correctly: {prepared['rubric_id_line']!r}")

    # Wrong sha: a default-pin mismatch must raise SystemExit, not silently proceed.
    checker_v1.CANONICAL_RUBRIC_SHA = "0" * 64
    try:
        checker_v1.validate_and_prepare(rubric_text, input_text, None, None)
    except SystemExit:
        pass
    else:
        raise AssertionError("validate_and_prepare did not reject a rubric sha mismatch against the default pin")

    print("PASS (canonical pin): RUBRIC-ID extraction and default-pin enforcement both correct.")


def main() -> int:
    check_structural()
    check_functional()
    check_canonical_rubric_pin()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
