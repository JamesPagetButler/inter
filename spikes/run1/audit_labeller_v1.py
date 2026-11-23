#!/usr/bin/env python3
"""Audit labeller v1 (contextus-seed-corpus round 1.1, amendment 2 B3, §8a
new component -- qbp-architecture live-test seq 325).

A fresh, separate Gemini session per audit paper, sent only that paper's
audit claim numbers, blind (never told how anyone else graded them). This
is `audit_labellers.labeller_b` ("the Gemini labeller") in the R8 bundle
field -- never the double-graded-120 checker calls reused, which would make
G2 tautological (B3).

Shares checker_v1.py's output contract and grade-line parser
(amendment 2 B1: one shared grading task, the checker and the audit
labeller differ only in framing and in which claims get an output line).

Modes:
  dry-run -- fixture prompt + fixture rubric + fixture input + a fixed
             fixture claim-number list, no network call, checks the request
             sha against the pinned known-answer value.
  label   -- real run: audit-labeller-v1.md + rubric + input + the claim
             numbers to label -> one generate_content call, same F5/F6
             hardening as checker_v1.py's `grade`, then
             checker_v1.parse_grade_lines() on the answer, restricted to
             exactly the requested claim numbers.

request_text = prompt_text + "\n\n" + rubric_text + "\n\n" + input_text
                + "\n\n" + "## Claims to label\n" + "\n".join(claim numbers, ascending)
request_sha  = sha256(request_text.encode("utf-8")).hexdigest()
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import checker_v1  # noqa: E402

FIXTURE_DIR = HERE / "audit_labeller_v1_fixtures"
FIXTURE_PROMPT = FIXTURE_DIR / "fixture_prompt.txt"
# Reuses checker_v1's generic synthetic rubric/input fixtures -- neither is
# checker-specific, and duplicating them here would just be two copies to
# keep in sync.
FIXTURE_RUBRIC = checker_v1.FIXTURE_RUBRIC
FIXTURE_INPUT = checker_v1.FIXTURE_INPUT
FIXTURE_CLAIM_NUMBERS = [1]

# Known-answer pin (§8a component test for this row). Recomputed
# independently by audit_labeller_v1_test.py from the fixture files on
# disk, so a stale pin here is caught rather than trusted.
FIXTURE_EXPECTED_REQUEST_SHA = (
    "0c867d654fc26f8376cec41fe6ef306ad3dd809baae035b209e1f88136987234"
)

# Shared with checker_v1.py: same rubric pin.
CANONICAL_RUBRIC_SHA = checker_v1.CANONICAL_RUBRIC_SHA

# Production audit-labeller prompt pin (amendment 2, inter `bb3490c`):
# spikes/prereg/contextus-seed-corpus-r1.1-prompts/audit-labeller-v1.md.
# Carries the shared-grading-task-v1.md block as a byte-exact substring,
# plus the labeller's own framing (blind, labels only the listed claims)
# and output contract ({"n","grade","reason"} lines, then GRADES-END; no
# doubt, no p4). `label` enforces this by default; pass --prompt-sha
# explicitly to override for a later prompt version.
CANONICAL_PROMPT_SHA = (
    "9d4d784ea13945f0207bb37c8974d9914097ae17445f2508ae8efec8fd955eff"
)

MODEL = checker_v1.MODEL


def claims_block_of(claim_numbers) -> str:
    ns = sorted(set(claim_numbers))
    if not ns:
        raise SystemExit("claim_numbers is empty -- nothing to label")
    if len(ns) != len(list(claim_numbers)):
        raise SystemExit(f"duplicate claim numbers passed in: {list(claim_numbers)}")
    return "## Claims to label\n" + "\n".join(str(n) for n in ns)


def build_request(prompt_text: str, rubric_text: str, input_text: str, claim_numbers) -> str:
    return prompt_text + "\n\n" + rubric_text + "\n\n" + input_text + "\n\n" + claims_block_of(claim_numbers)


def validate_and_prepare(
    prompt_text: str,
    rubric_text: str,
    input_text: str,
    claim_numbers,
    prompt_sha_expected: str | None,
    rubric_sha_expected: str | None,
    input_sha_expected: str | None,
) -> dict:
    """Pure validation + request construction, no I/O and no network --
    mirrors checker_v1.validate_and_prepare, plus the claim-number block."""
    prompt_sha = checker_v1.sha256_of(prompt_text)
    expected_prompt_sha = prompt_sha_expected or CANONICAL_PROMPT_SHA
    if prompt_sha != expected_prompt_sha:
        raise SystemExit(f"prompt sha mismatch: got {prompt_sha}, expected {expected_prompt_sha}")
    rubric_sha = checker_v1.sha256_of(rubric_text)
    expected_rubric_sha = rubric_sha_expected or CANONICAL_RUBRIC_SHA
    if rubric_sha != expected_rubric_sha:
        raise SystemExit(f"rubric sha mismatch: got {rubric_sha}, expected {expected_rubric_sha}")
    input_sha = checker_v1.sha256_of(input_text)
    if input_sha_expected and input_sha != input_sha_expected:
        raise SystemExit(f"input sha mismatch: got {input_sha}, expected {input_sha_expected}")

    request_text = build_request(prompt_text, rubric_text, input_text, claim_numbers)
    return {
        "prompt_sha": prompt_sha,
        "rubric_sha": rubric_sha,
        "input_sha": input_sha,
        "request_text": request_text,
        "request_sha": checker_v1.sha256_of(request_text),
        "rubric_id_line": checker_v1.rubric_id_line_of(rubric_text),
    }


def cmd_dry_run(args) -> int:
    prompt_text = FIXTURE_PROMPT.read_text()
    rubric_text = FIXTURE_RUBRIC.read_text()
    input_text = FIXTURE_INPUT.read_text()
    request_text = build_request(prompt_text, rubric_text, input_text, FIXTURE_CLAIM_NUMBERS)
    request_sha = checker_v1.sha256_of(request_text)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dry_run.request_SENT.txt").write_text(request_text)
    (out_dir / "dry_run.request_SENT.sha256.txt").write_text(request_sha + "\n")

    if request_sha != FIXTURE_EXPECTED_REQUEST_SHA:
        print(f"FAIL: request sha {request_sha} != pinned {FIXTURE_EXPECTED_REQUEST_SHA}")
        return 1
    print(f"OK: dry-run request sha {request_sha} matches the pinned fixture value. No network call made.")
    return 0


def cmd_label(args) -> int:
    prompt_text = Path(args.prompt).read_text()
    rubric_text = Path(args.rubric).read_text()
    input_text = Path(args.input).read_text()
    claim_numbers = sorted(set(int(x) for x in args.claims.split(",")))

    prepared = validate_and_prepare(
        prompt_text, rubric_text, input_text, claim_numbers,
        args.prompt_sha, args.rubric_sha, args.input_sha,
    )
    request_text, request_sha = prepared["request_text"], prepared["request_sha"]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = args.label
    existing = sorted(out_dir.glob(f"{stem}.*"))
    if existing:
        raise SystemExit(f"refusing to overwrite existing output for {stem}: {existing}")

    (out_dir / f"{stem}.request_SENT.txt").write_text(request_text)
    (out_dir / f"{stem}.request_SENT.sha256.txt").write_text(request_sha + "\n")

    client = checker_v1._get_client()
    from google.genai.types import GenerateContentConfig, ThinkingConfig  # type: ignore

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=request_text,
            config=GenerateContentConfig(
                thinking_config=ThinkingConfig(thinking_budget=10000, include_thoughts=True)
            ),
        )
    except Exception as e:
        (out_dir / f"{stem}.CALL_FAILED.txt").write_text(f"{type(e).__name__}: {e}")
        return 1

    try:
        raw_dump = response.model_dump_json()
    except Exception as e:
        raw_dump = f"<model_dump_json failed: {type(e).__name__}: {e}>"
    (out_dir / f"{stem}.response_RAW.json").write_text(raw_dump)

    finish_reason = str(getattr(response.candidates[0], "finish_reason", None))

    try:
        answer_parts, thought_parts = [], []
        for part in response.candidates[0].content.parts:
            text = getattr(part, "text", None) or ""
            (thought_parts if getattr(part, "thought", False) else answer_parts).append(text)
        answer_text = "\n".join(answer_parts)
        thought_text = "\n".join(thought_parts)
        thought_tokens = getattr(response.usage_metadata, "thoughts_token_count", 0)
    except Exception as e:
        (out_dir / f"{stem}.PARSE_FAILED.txt").write_text(
            f"{type(e).__name__}: {e} -- see {stem}.response_RAW.json"
        )
        return 0

    (out_dir / f"{stem}.answer_RAW.txt").write_text(answer_text)
    (out_dir / f"{stem}.thoughts_RAW.txt").write_text(thought_text)

    try:
        grades = checker_v1.parse_grade_lines(answer_text, claim_numbers)
    except SystemExit as e:
        (out_dir / f"{stem}.PARSE_FAILED.txt").write_text(f"{e} -- see {stem}.answer_RAW.txt")
        return 0
    (out_dir / f"{stem}.grades.json").write_text(json.dumps(grades, indent=2, sort_keys=True))

    (out_dir / f"{stem}.meta.json").write_text(
        json.dumps(
            {
                "label": args.label,
                "paper": args.paper,
                "claim_numbers": claim_numbers,
                "blind": True,
                "model": MODEL,
                "thinking_budget": 10000,
                "prompt_sha": prepared["prompt_sha"],
                "rubric_sha": prepared["rubric_sha"],
                "input_sha": prepared["input_sha"],
                "request_sha": request_sha,
                "rubric_id_line": prepared["rubric_id_line"],
                "finish_reason": finish_reason,
                "thought_tokens": thought_tokens,
            },
            indent=2,
        )
    )
    print(f"OK: {stem} finish_reason={finish_reason} grades={grades}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)

    p_dry = sub.add_parser("dry-run")
    p_dry.add_argument("--out-dir", required=True)
    p_dry.set_defaults(func=cmd_dry_run)

    p_label = sub.add_parser("label")
    p_label.add_argument("--prompt", required=True)
    p_label.add_argument("--prompt-sha")
    p_label.add_argument("--rubric", required=True)
    p_label.add_argument("--rubric-sha")
    p_label.add_argument("--input", required=True)
    p_label.add_argument("--input-sha")
    p_label.add_argument("--claims", required=True, help="comma-separated claim numbers to label, e.g. 3,7,12")
    p_label.add_argument("--paper", required=True)
    p_label.add_argument("--label", required=True)
    p_label.add_argument("--out-dir", required=True)
    p_label.set_defaults(func=cmd_label)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
