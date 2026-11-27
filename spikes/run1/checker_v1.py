#!/usr/bin/env python3
"""Checker v1 (contextus-seed-corpus round 1.1, amendment 2, §8a/§8b).

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
  dry-run -- fixture prompt + fixture rubric + fixture input, no network
             call, checks the request sha against the pinned known-answer
             value (§8a row for this component).
  grade   -- real run: checker-v1.md + rubric + input -> one
             generate_content call, with the F5/F6 hardening from the A2
             redo (shas checked up front, raw response written before any
             parsing, finish_reason recorded, parts-extraction failure
             writes a PARSE_FAILED finding and returns rather than raising).

Amendment 2 (spike-seed-corpus-s4 seq 325): contextus-spike found at build
time that the original two-part request (rubric + input) carried no
grading-task instructions at all -- nothing told Gemini what to do or what
to output. The request is now three parts:

request_text = prompt_text + "\n\n" + rubric_text + "\n\n" + input_text
request_sha  = sha256(request_text.encode("utf-8")).hexdigest()
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

GEMINI_SERVER_DIR = Path.home() / ".claude" / "mcp-servers" / "gemini"
MODEL = "gemini-3.1-pro-preview"

# Shared-root rater tag (qbp-architecture seq 357): the s5_r1.1_* root also
# holds the Opus verifier's own metas (Anthropic usage, not Gemini), so
# every meta.json this component writes declares which rater produced it.
RATER = "gemini-checker-v1"

FIXTURE_DIR = Path(__file__).parent / "checker_v1_fixtures"
FIXTURE_PROMPT = FIXTURE_DIR / "fixture_prompt.txt"
FIXTURE_RUBRIC = FIXTURE_DIR / "fixture_rubric.txt"
FIXTURE_INPUT = FIXTURE_DIR / "fixture_input.txt"

# Known-answer pin (§8a component test for this row). Recomputed
# independently by checker_v1_test.py from the fixture files on disk, so a
# stale pin here is caught rather than trusted. Changing any fixture file,
# or changing build_request()'s concatenation, must update this constant as
# a deliberate, reviewed edit. Dry-run only -- unrelated to the production
# rubric/prompt pins below.
FIXTURE_EXPECTED_REQUEST_SHA = (
    "e02100b4b65d641f6fe47bc0ea266c35419125190e51e842ae1f622bc38a0d54"
)

# Production rubric pin (§I4 APPROVE on gate 2, inter 2b8b2e4, live-test
# seq 5291): spikes/run1/vocab/relation-rubric-v1.txt on
# qbp-architecture/seed-corpus-s5-grades, generated from the SIGNED
# definitions (source_sha256=ea3f245e...f2d4) via the registry
# (registry_sha256=edc8fd5f...8d13). `grade` enforces this by default;
# pass --rubric-sha explicitly to override for a later rubric version.
CANONICAL_RUBRIC_SHA = (
    "f950c385c016e8c0b23b6e8e8941d0448fcb049a31eb7fa404f3ed7f1b4eed23"
)

# Production checker prompt pin (amendment 2, inter `bb3490c`):
# spikes/prereg/contextus-seed-corpus-r1.1-prompts/checker-v1.md. Carries
# the shared-grading-task-v1.md block (sha256
# 826f9cde034937920e585a25189d0cf063ef565878f27ea08147f4e2b45e6cd6) as a
# byte-exact substring, plus the checker's own framing and output contract
# ({"n","grade","reason"} lines, then GRADES-END; no doubt, no p4). `grade`
# enforces this by default; pass --prompt-sha explicitly to override for a
# later prompt version.
CANONICAL_PROMPT_SHA = (
    "cc4c6c2fd740cac29829921c9d1f0ecbef50b85668137ff9dca021a096ac8803"
)

# The output contract shared by checker-v1.md and audit-labeller-v1.md
# (amendment 2 B1): one {"n","grade","reason"} JSON line per claim, then
# exactly one GRADES-END line, nothing after -- no doubt, no p4 (those are
# verifier-only).
GRADE_SET = frozenset(
    ("faithful", "wrong-relation", "wrong-direction", "wrong-modality", "wrong-locator", "not-in-paper")
)
GRADE_LINE_KEYS = frozenset(("n", "grade", "reason"))
GRADES_END = "GRADES-END"


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# F-0b-1 (qbp-architecture, spike-seed-corpus-s4 seq 344): Gemini sometimes
# wraps the whole answer in a single ```json / ``` markdown fence. Only a
# fence wrapping the ENTIRE answer (first non-blank line is exactly ```json
# or ```, last non-blank line is exactly ```) is stripped -- nothing else is
# normalised, so a fence at only one end, the wrong fence language, a fence
# that doesn't wrap everything, or text before the opening fence are all
# still rejected by the unchanged logic below, just on the original text.
FENCE_OPEN_MARKERS = frozenset(("```json", "```"))
FENCE_CLOSE_MARKER = "```"


def _strip_wrapping_fence(text: str) -> tuple[str, bool]:
    lines = text.splitlines()
    nonblank_idx = [i for i, ln in enumerate(lines) if ln.strip()]
    if len(nonblank_idx) < 2:
        return text, False
    first_idx, last_idx = nonblank_idx[0], nonblank_idx[-1]
    if (
        lines[first_idx].strip() in FENCE_OPEN_MARKERS
        and lines[last_idx].strip() == FENCE_CLOSE_MARKER
    ):
        stripped = lines[:first_idx] + lines[first_idx + 1:last_idx] + lines[last_idx + 1:]
        return "\n".join(stripped), True
    return text, False


def parse_grade_lines(text: str, expected_ns) -> tuple[dict, bool]:
    """Parses the shared checker/audit-labeller output contract into
    {n: grade}. Reused by audit_labeller_v1.py for the same reason the
    prompt itself is shared (amendment 2 B1) -- one parser, not two that
    could silently drift apart.

    Fails loudly (SystemExit) and never silently drops or guesses a grade:
    malformed JSON, wrong keys, an out-of-category grade, a duplicate n, an
    n-set mismatch against `expected_ns`, more/less than one GRADES-END
    line, or any non-blank content after it are all rejected by name.

    Returns (grades, defenced): defenced is True iff a single wrapping
    ```json/``` fence was stripped before parsing (F-0b-1), so callers can
    report the count.
    """
    text, defenced = _strip_wrapping_fence(text)
    lines = text.splitlines()
    if lines.count(GRADES_END) != 1:
        raise SystemExit(f"expected exactly one {GRADES_END} line, found {lines.count(GRADES_END)}")
    end_idx = lines.index(GRADES_END)
    before, after = lines[:end_idx], lines[end_idx + 1:]
    if any(ln.strip() for ln in after):
        raise SystemExit(f"non-blank content after {GRADES_END}: {after!r}")

    grades = {}
    for ln in before:
        if not ln.strip():
            continue
        try:
            o = json.loads(ln)
        except json.JSONDecodeError:
            raise SystemExit(f"grade line is not JSON: {ln[:80]!r}")
        if not (isinstance(o, dict) and set(o) == GRADE_LINE_KEYS):
            raise SystemExit(f"grade line keys must be exactly {sorted(GRADE_LINE_KEYS)}: {o!r}")
        n, grade, reason = o["n"], o["grade"], o["reason"]
        if not (isinstance(n, int) and not isinstance(n, bool)):
            raise SystemExit(f"n not an int: {n!r}")
        if grade not in GRADE_SET:
            raise SystemExit(f"n={n}: grade outside the category set: {grade!r}")
        if not isinstance(reason, str) or not reason.strip():
            raise SystemExit(f"n={n}: empty or non-string reason")
        if n in grades:
            raise SystemExit(f"duplicate n in grade lines: {n}")
        grades[n] = grade

    expected = set(expected_ns)
    if set(grades) != expected:
        raise SystemExit(
            "n-set mismatch: missing "
            f"{sorted(expected - set(grades))}, extra {sorted(set(grades) - expected)}"
        )
    return grades, defenced


def build_request(prompt_text: str, rubric_text: str, input_text: str) -> str:
    return prompt_text + "\n\n" + rubric_text + "\n\n" + input_text


def rubric_id_line_of(rubric_text: str) -> str | None:
    return next(
        (line for line in rubric_text.splitlines() if line.startswith("RUBRIC-ID:")),
        None,
    )


# Gemini token-unit ruling (deming, spike-seed-corpus-s4 seq 348, confirmed
# by cartan against the API's own total_token_count on all 5 probe calls,
# seq 351): on Gemini, prompt_token_count already INCLUDES
# cached_content_token_count -- it is 16,209 on every §8b probe run whether
# cached is null or 14,158. Summing all four fields double-counts cached
# tokens. The three-field sum (prompt + thoughts + candidates) is the
# correct "tokens consumed" unit; the four-field sum is still recorded, so
# the pre-registered (incorrect) unit can be recomputed after the fact.
USAGE_FIELDS = ("prompt_token_count", "cached_content_token_count", "thoughts_token_count", "candidates_token_count")


def usage_fields_of(response) -> dict:
    """The 4 required Gemini usage fields from one response's
    usage_metadata. Reused by audit_labeller_v1.py's cmd_label, same reason
    parse_grade_lines is shared. Each field is recorded as the int value or
    None if the API didn't return it -- never silently defaulted here (only
    usage_sums_of defaults a missing field to 0, for the sum)."""
    um = response.usage_metadata
    return {f: getattr(um, f, None) for f in USAGE_FIELDS}


def usage_sums_of(fields: dict) -> dict:
    """{'four_field': ..., 'three_field': ...} from usage_fields_of's
    output (or an equivalent dict), per the unit ruling above."""
    p = fields.get("prompt_token_count") or 0
    c = fields.get("cached_content_token_count") or 0
    t = fields.get("thoughts_token_count") or 0
    a = fields.get("candidates_token_count") or 0
    return {"four_field": p + c + t + a, "three_field": p + t + a}


def validate_and_prepare(
    prompt_text: str,
    rubric_text: str,
    input_text: str,
    prompt_sha_expected: str | None,
    rubric_sha_expected: str | None,
    input_sha_expected: str | None,
) -> dict:
    """Pure validation + request construction, no I/O and no network --
    the part of `grade` that checker_v1_test.py exercises directly, without
    needing _get_client() or a real call.

    qbp-architecture, seq 329: `prompt_sha_expected` / `rubric_sha_expected`
    are never allowed to REPLACE the canonical pin -- a caller cannot
    legitimise a planted prompt or rubric by also supplying its own
    matching sha. If given, they may only ASSERT the canonical value (and
    are rejected immediately if they disagree with it, before the actual
    text's sha is even checked); the real check is always against
    CANONICAL_PROMPT_SHA / CANONICAL_RUBRIC_SHA, full stop. Only
    `input_sha_expected` stays a true per-call assertion, because the input
    legitimately varies call to call and has no canonical pin."""
    if prompt_sha_expected is not None and prompt_sha_expected != CANONICAL_PROMPT_SHA:
        raise SystemExit(
            f"--prompt-sha override does not match the canonical pin: got "
            f"{prompt_sha_expected}, canonical {CANONICAL_PROMPT_SHA}"
        )
    prompt_sha = sha256_of(prompt_text)
    if prompt_sha != CANONICAL_PROMPT_SHA:
        raise SystemExit(f"prompt sha mismatch: got {prompt_sha}, expected {CANONICAL_PROMPT_SHA}")

    if rubric_sha_expected is not None and rubric_sha_expected != CANONICAL_RUBRIC_SHA:
        raise SystemExit(
            f"--rubric-sha override does not match the canonical pin: got "
            f"{rubric_sha_expected}, canonical {CANONICAL_RUBRIC_SHA}"
        )
    rubric_sha = sha256_of(rubric_text)
    if rubric_sha != CANONICAL_RUBRIC_SHA:
        raise SystemExit(f"rubric sha mismatch: got {rubric_sha}, expected {CANONICAL_RUBRIC_SHA}")

    input_sha = sha256_of(input_text)
    if input_sha_expected and input_sha != input_sha_expected:
        raise SystemExit(f"input sha mismatch: got {input_sha}, expected {input_sha_expected}")

    request_text = build_request(prompt_text, rubric_text, input_text)
    return {
        "prompt_sha": prompt_sha,
        "rubric_sha": rubric_sha,
        "input_sha": input_sha,
        "request_text": request_text,
        "request_sha": sha256_of(request_text),
        "rubric_id_line": rubric_id_line_of(rubric_text),
    }


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
    prompt_text = FIXTURE_PROMPT.read_text()
    rubric_text = FIXTURE_RUBRIC.read_text()
    input_text = FIXTURE_INPUT.read_text()
    request_text = build_request(prompt_text, rubric_text, input_text)
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
    prompt_path = Path(args.prompt)
    rubric_path = Path(args.rubric)
    input_path = Path(args.input)
    prompt_text = prompt_path.read_text()
    rubric_text = rubric_path.read_text()
    input_text = input_path.read_text()

    prepared = validate_and_prepare(
        prompt_text, rubric_text, input_text, args.prompt_sha, args.rubric_sha, args.input_sha
    )
    prompt_sha = prepared["prompt_sha"]
    rubric_sha = prepared["rubric_sha"]
    input_sha = prepared["input_sha"]
    request_text = prepared["request_text"]
    request_sha = prepared["request_sha"]
    rubric_id_line = prepared["rubric_id_line"]

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
        usage_fields = usage_fields_of(response)
        usage_sums = usage_sums_of(usage_fields)
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
                "prompt_sha": prompt_sha,
                "rubric_sha": rubric_sha,
                "input_sha": input_sha,
                "request_sha": request_sha,
                "rubric_id_line": rubric_id_line,
                "finish_reason": finish_reason,
                "thought_tokens": thought_tokens,
                "usage": usage_fields,
                "usage_sums": usage_sums,
                "rater": RATER,
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
    p_grade.add_argument("--prompt", required=True)
    p_grade.add_argument("--prompt-sha")
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
