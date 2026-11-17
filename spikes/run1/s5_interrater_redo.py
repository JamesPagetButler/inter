#!/usr/bin/env python3
"""contextus-seed-corpus round 1 -- Section 5 Gemini inter-rater, redo (A2).

Director's ruling after the VOID run (sessionbridge spike-seed-corpus-s4
seq 231/234/236/237), replacing the `review_document` MCP tool with a
direct call through the same client the live MCP server
(~/.claude/mcp-servers/gemini/server.py, sha256
7657d49e8b7d383598b736a082b53260ca716f261c8b5ddd2630e4b58f2ab0c4) uses.
`review_document` wraps its `document_content` argument in its own review
template ("Provide your review in this structure: ## Clarity ... ##
Overall Assessment"), which conflicts with inter-rater.md's own "Output
one JSON line per claim ... Nothing else." Dropping that wrapper is a
harness fix, not a rule change: it is the same function, model and prompt
FROZEN-v1 §5 names, with only the caller changed.

Verbatim by construction, not by care: request = inter-rater.md's text +
"\n\n" + the grader_input file's text, with no other wrapper. Both parts
are read straight off disk -- the frozen prompt at its frozen sha, the
packet at its already-committed sha -- and neither ever passes through
this script's own paraphrase or through a model's context before the
network call. The exact request bytes and their sha256 are written to
file BEFORE anything is sent. The prompt's sha and all 4 inputs' shas are
checked against the frozen/committed values up front, before the loop and
before any call is made, so a bad input never lets a partial run start.

The void run this replaces: `mcp__gemini__review_document`, model
gemini-3.1-pro-preview, thinking=True, thinking_budget=10000 (the tool's
defaults), paraphrased (non-verbatim) paper text -- recorded under
s5_interrater_A2_VOID/, never compared or used.

This run: same model and thinking settings, verbatim request, one call per
paper, calls made one after another (never in parallel, per deming's
box/credential clearance condition, sessionbridge seq 235). This is a new
program and does not run until deming's Thompson vet clears it.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "mcp-servers" / "gemini"))
from server import _get_client  # live server, sha256 7657d49e...c4 (verified above)

from google.genai.types import GenerateContentConfig, ThinkingConfig

RUN1 = Path(__file__).parent
PROMPT_PATH = RUN1.parent / "prereg" / "contextus-seed-corpus-r1-prompts" / "inter-rater.md"
PROMPT_SHA_FROZEN = "99f432676e6acc90bea75d6dd1d4f2f3064536f5f46c8a0a2e2ac884a53f1330"

MODEL = "gemini-3.1-pro-preview"
THINKING_BUDGET = 10000

GRADER_INPUTS_DIR = RUN1 / "s5_grader_inputs_A2"  # fetched from inter ab6c43a before running
OUT_DIR = RUN1 / "s5_interrater_A2"

# (paper_id, sha256 of s5_grader_inputs_A2/<id>.grader_input.txt as committed at
# inter ab6c43a -- cross-checked against that commit's own sha256 manifest).
TARGETS = [
    ("W4390977661", "824b7c67ebf5c3cebb896c4322e07227e9d45cbdccb6fffac70efb53ebf68b9c"),
    ("W7160385925", "002124c3b52595a934eb26e23001cf0185dccbe468373faaf734b5f276b18582"),
    ("W2015765968", "dc5d1f7c8837b3f7d633dacc97ab7f12a142453a9eec7c0c9f61ee31169b7802"),
    ("W4313326288", "00d646ed3710b800d82be593392554965c15fb609fc1fc7ff949b620d4a67e80"),
]


def sha256_of(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main():
    prompt_text = PROMPT_PATH.read_text()
    prompt_sha = sha256_of(prompt_text)
    if prompt_sha != PROMPT_SHA_FROZEN:
        raise SystemExit(
            f"inter-rater.md sha mismatch: got {prompt_sha}, expected {PROMPT_SHA_FROZEN}"
        )

    # Check ALL inputs before the loop, so a bad one never lets a partial
    # run start (Thompson vet F5).
    inputs = {}
    for paper_id, committed_sha in TARGETS:
        input_path = GRADER_INPUTS_DIR / f"{paper_id}.grader_input.txt"
        input_text = input_path.read_text()
        input_sha = sha256_of(input_text)
        if input_sha != committed_sha:
            raise SystemExit(
                f"{paper_id} grader_input sha mismatch: got {input_sha}, expected {committed_sha}"
            )
        inputs[paper_id] = input_text

    OUT_DIR.mkdir(exist_ok=True)
    client = _get_client()

    for paper_id, committed_sha in TARGETS:
        input_text = inputs[paper_id]
        input_sha = committed_sha  # already verified above

        # Verbatim request: the frozen prompt, then the packet's own text. No
        # other wrapper, no paraphrase.
        request = prompt_text + "\n\n" + input_text
        request_sha = sha256_of(request)

        (OUT_DIR / f"{paper_id}.request_SENT.txt").write_text(request)
        (OUT_DIR / f"{paper_id}.request_SENT.sha256.txt").write_text(request_sha + "\n")

        print(
            f"{paper_id}: prompt_sha={prompt_sha} input_sha={input_sha} "
            f"request_sha={request_sha} request_chars={len(request)}",
            file=sys.stderr,
        )

        config = GenerateContentConfig(
            thinking_config=ThinkingConfig(
                thinking_budget=THINKING_BUDGET,
                include_thoughts=True,
            )
        )

        try:
            response = client.models.generate_content(
                model=MODEL, contents=request, config=config
            )
        except Exception as e:
            # Over-limit or any other call failure: record as a finding, do
            # NOT condense the input and retry. The director's instruction
            # is explicit on this.
            (OUT_DIR / f"{paper_id}.CALL_FAILED.txt").write_text(
                f"request_chars={len(request)}\nrequest_sha256={request_sha}\n"
                f"exception={type(e).__name__}: {e}\n"
            )
            print(f"{paper_id}: CALL FAILED, recorded as finding: {e}", file=sys.stderr)
            continue

        # Save the raw response straight after the call, before any parsing,
        # so a parse failure never loses a paid call's answer (Thompson vet
        # F6).
        try:
            raw_dump = response.model_dump_json()
        except Exception as e:
            raw_dump = f"<model_dump_json failed: {type(e).__name__}: {e}>"
        (OUT_DIR / f"{paper_id}.response_RAW.json").write_text(raw_dump)

        finish_reason = None
        try:
            if hasattr(response, "candidates") and response.candidates:
                finish_reason = str(getattr(response.candidates[0], "finish_reason", None))
        except Exception:
            pass

        try:
            answer_parts = []
            thought_parts = []
            if hasattr(response, "candidates") and response.candidates:
                for part in response.candidates[0].content.parts:
                    text = getattr(part, "text", None) or ""
                    if getattr(part, "thought", False):
                        thought_parts.append(text)
                    else:
                        answer_parts.append(text)
            answer_text = "\n".join(answer_parts)
            thought_text = "\n".join(thought_parts)
            thought_tokens = getattr(response.usage_metadata, "thoughts_token_count", 0)
        except Exception as e:
            (OUT_DIR / f"{paper_id}.PARSE_FAILED.txt").write_text(
                f"finish_reason={finish_reason}\n"
                f"exception={type(e).__name__}: {e}\n"
                f"(raw response is in {paper_id}.response_RAW.json)\n"
            )
            print(f"{paper_id}: PARSE FAILED, recorded as finding: {e}", file=sys.stderr)
            continue

        # Write raw response to file before anything reads it.
        (OUT_DIR / f"{paper_id}.answer_RAW.txt").write_text(answer_text)
        (OUT_DIR / f"{paper_id}.thoughts_RAW.txt").write_text(thought_text)
        (OUT_DIR / f"{paper_id}.meta.json").write_text(json.dumps({
            "paper_id": paper_id,
            "model": MODEL,
            "thinking_budget": THINKING_BUDGET,
            "prompt_sha256": prompt_sha,
            "input_sha256": input_sha,
            "request_sha256": request_sha,
            "answer_sha256": sha256_of(answer_text),
            "thoughts_sha256": sha256_of(thought_text),
            "thought_tokens": thought_tokens,
            "finish_reason": finish_reason,
        }, indent=2))

        print(
            f"{paper_id}: wrote answer ({len(answer_text)} chars), "
            f"thoughts ({len(thought_text)} chars), thought_tokens={thought_tokens}, "
            f"finish_reason={finish_reason}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
