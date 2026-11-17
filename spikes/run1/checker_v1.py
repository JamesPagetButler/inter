#!/usr/bin/env python3
"""Checker v1 (contextus-seed-corpus round 1.1, inter#300 draft r2, §8a/§8b).

Direct google-genai `generate_content` calls, request bytes hashed to a file
before any network call (the A2 inter-rater redo pattern). Serves three
callers with the same request construction and the same hash-before-call
discipline:
  - the 120-item double-graded set (prereg §4);
  - L1 doubt escalations, full grader-input text, same input form as the
    120-set calls (qbp-architecture, live-test seq 5270);
  - the §8b repeatability probe (5 fresh-session runs on one paper; the
    request bytes are identical across runs by design, so run_index is
    carried only in the output filenames and meta.json, never folded into
    the hashed request text -- qbp-architecture, live-test seq 5267).

Modes:
  dry-run -- fixture rubric + fixture input, no network call, checks the
             request sha against the pinned known-answer value (§8a row
             for this component).
  grade   -- real run: rubric + input -> one generate_content call, with
             the F5/F6 hardening from the A2 redo (shas checked up front,
             raw response written before any parsing, finish_reason
             recorded, parts-extraction failure writes a PARSE_FAILED
             finding and returns rather than raising).

request_text = rubric_text + "\n\n" + input_text
request_sha  = sha256(request_text.encode("utf-8")).hexdigest()
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

GEMINI_SERVER_DIR = Path.home() / ".claude" / "mcp-servers" / "gemini"
MODEL = "gemini-3.1-pro-preview"

FIXTURE_DIR = Path(__file__).parent / "checker_v1_fixtures"
FIXTURE_RUBRIC = FIXTURE_DIR / "fixture_rubric.txt"
FIXTURE_INPUT = FIXTURE_DIR / "fixture_input.txt"

# Known-answer pin (§8a component test for this row). Recomputed
# independently by checker_v1_test.py from the fixture files on disk, so a
# stale pin here is caught rather than trusted. Changing either fixture
# file, or changing build_request()'s concatenation, must update this
# constant as a deliberate, reviewed edit.
FIXTURE_EXPECTED_REQUEST_SHA = (
    "cd68da07338865d8e93d43a9ab07bb655964ee308d333d572b1183c90f48eccf"
)


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_request(rubric_text: str, input_text: str) -> str:
    return rubric_text + "\n\n" + input_text


def _get_client():
    # Lazy import, inside this function only. cmd_dry_run never calls this
    # function and never imports google.genai -- that is what makes "the
    # dry run makes no network call" a structural property of the code,
    # not just an observation about one run. See checker_v1_test.py's
    # static check.
    sys.path.insert(0, str(GEMINI_SERVER_DIR))
    from server import _get_client as _live_get_client  # type: ignore

    return _live_get_client()


def cmd_dry_run(args) -> int:
    rubric_text = FIXTURE_RUBRIC.read_text()
    input_text = FIXTURE_INPUT.read_text()
    request_text = build_request(rubric_text, input_text)
    request_sha = sha256_of(request_text)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dry_run.request_SENT.txt").write_text(request_text)
    (out_dir / "dry_run.request_SENT.sha256.txt").write_text(request_sha + "\n")

    if request_sha != FIXTURE_EXPECTED_REQUEST_SHA:
        print(
            f"FAIL: request sha {request_sha} != pinned {FIXTURE_EXPECTED_REQUEST_SHA}"
        )
        return 1
    print(
        f"OK: dry-run request sha {request_sha} matches the pinned fixture value."
        " No network call made."
    )
    return 0


def cmd_grade(args) -> int:
    rubric_path = Path(args.rubric)
    input_path = Path(args.input)
    rubric_text = rubric_path.read_text()
    input_text = input_path.read_text()

    rubric_sha = sha256_of(rubric_text)
    if args.rubric_sha and rubric_sha != args.rubric_sha:
        raise SystemExit(f"rubric sha mismatch: got {rubric_sha}, expected {args.rubric_sha}")
    input_sha = sha256_of(input_text)
    if args.input_sha and input_sha != args.input_sha:
        raise SystemExit(f"input sha mismatch: got {input_sha}, expected {args.input_sha}")

    request_text = build_request(rubric_text, input_text)
    request_sha = sha256_of(request_text)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_suffix = f".run{args.run_index}" if args.run_index is not None else ""
    stem = f"{args.label}{run_suffix}"

    existing = sorted(out_dir.glob(f"{stem}.*"))
    if existing:
        raise SystemExit(
            f"refusing to overwrite existing output for {stem}: {existing}"
        )

    (out_dir / f"{stem}.request_SENT.txt").write_text(request_text)
    (out_dir / f"{stem}.request_SENT.sha256.txt").write_text(request_sha + "\n")

    client = _get_client()
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
    (out_dir / f"{stem}.meta.json").write_text(
        json.dumps(
            {
                "label": args.label,
                "run_index": args.run_index,
                "model": MODEL,
                "thinking_budget": 10000,
                "rubric_sha": rubric_sha,
                "input_sha": input_sha,
                "request_sha": request_sha,
                "finish_reason": finish_reason,
                "thought_tokens": thought_tokens,
            },
            indent=2,
        )
    )
    print(f"OK: {stem} finish_reason={finish_reason}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)

    p_dry = sub.add_parser("dry-run")
    p_dry.add_argument("--out-dir", required=True)
    p_dry.set_defaults(func=cmd_dry_run)

    p_grade = sub.add_parser("grade")
    p_grade.add_argument("--rubric", required=True)
    p_grade.add_argument("--rubric-sha")
    p_grade.add_argument("--input", required=True)
    p_grade.add_argument("--input-sha")
    p_grade.add_argument("--label", required=True)
    p_grade.add_argument("--run-index", type=int, default=None)
    p_grade.add_argument("--out-dir", required=True)
    p_grade.set_defaults(func=cmd_grade)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
