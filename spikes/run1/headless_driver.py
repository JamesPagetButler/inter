#!/usr/bin/env python3
"""contextus-seed-corpus — headless subprocess driver (replaces the
chat-driven sub-agent dispatch, which accumulated context and ran ~4x over
token budget in the §4 pilot — see 2026-11-11 Hall-return note).

Runs ONE pipeline stage (restatement or extraction) for ONE paper per
`claude -p` subprocess call. No chat session, no sub-agent context
accumulation: each call is a fresh, non-persistent CLI invocation with an
empty cwd outside ~/Documents (so no CLAUDE.md auto-loads) and a frozen
system prompt supplied verbatim.

Argv shape (confirmed working by the foreman, 2026-11-11):

    claude -p --tools "" --strict-mcp-config --setting-sources "" \
        --disable-slash-commands --no-session-persistence \
        --system-prompt "<frozen prompt text>" --model <haiku|opus> \
        --output-format json "<stage input text>"

Stage input shapes (per the frozen prompts in
spikes/prereg/contextus-seed-corpus-r1-prompts/):
  - restatement: the raw paper text (abstract/intro/statements extract).
  - extraction:  the restatement stage's own output text.
Both are passed as the single trailing positional argument (the user
message), never via stdin.

Telemetry: one JSONL line per call appended to --out. Never logs full paper
text or full result text (spike discipline: no paper text in git/logs) —
only the result's sha256 + length. Each line also logs prompt_sha256, the
sha256 of the EXACT string passed to --system-prompt that call; this is
checked against FROZEN_PROMPT_SHA256 before any subprocess call is made
(fail closed: a mismatch refuses the call and exits nonzero rather than
silently proceeding with a drifted or wrong prompt file).

Retry: one retry with backoff on non-zero exit or timeout; a second
failure is recorded and the call moves on (no unbounded loop). A model
decline (is_error, or a refusal-shaped result) is recorded as `declined`
and is NOT retried and NOT rerouted to another model (spike rule §2a:
a decline halts at that paper).
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

RUN_DIR = os.path.dirname(os.path.abspath(__file__))

# Frozen prompt integrity (director requirement, qbp-architecture,
# 2026-11-11): sha256 of the EXACT text string passed to --system-prompt,
# computed over the file content as read (Python text-mode open().read()),
# not the file's own on-disk hash via a different tool. Verified against
# spikes/prereg/contextus-seed-corpus-r1-prompts/{restatement,extraction}.md
# with `sha256sum` + a matching Python hashlib read at build time.
FROZEN_PROMPT_SHA256 = {
    "restatement": "bcab237a938ee7b97a4ed3463c2f72e3c739f422f1f2c121b922724d73c01681",
    "extraction": "0c3334686f5e9636a6ecb9659f61b760fee2b2a411e92b1a0714af75216ec104",
}


class PromptIntegrityError(RuntimeError):
    """Raised when the --prompt-file content does not hash to the frozen
    sha256 for the given --stage. Fail-closed: no subprocess call is made
    when this fires."""


def check_prompt_integrity(stage, prompt_text):
    """Compute sha256 of the exact prompt string and verify it against the
    frozen hash for `stage`. Returns the digest on success; raises
    PromptIntegrityError on any mismatch or unknown stage (fail closed —
    never silently proceed)."""
    digest = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
    expected = FROZEN_PROMPT_SHA256.get(stage)
    if expected is None:
        raise PromptIntegrityError(
            "no frozen prompt_sha256 registered for stage %r — refusing "
            "to call claude -p" % stage)
    if digest != expected:
        raise PromptIntegrityError(
            "prompt_sha256 mismatch for stage %r: got %s, expected %s "
            "(the --prompt-file content has drifted from the frozen "
            "pre-registration, or the wrong file was passed — refusing "
            "to call claude -p)" % (stage, digest, expected))
    return digest


DEFAULT_TIMEOUT_S = 120
MAX_ATTEMPTS = 2  # one try + one retry
BACKOFF_S = 5.0
MAX_CONCURRENCY = 2

_DECLINE_MARKERS = (
    "i can't help with that",
    "i cannot help with that",
    "i can't assist with that",
    "i cannot assist with",
    "i'm not able to help with that",
    "i won't be able to help with that",
    "i'm unable to help with that",
    "i must decline",
    "i have to decline",
)

_out_lock = threading.Lock()


def build_argv(claude_bin, prompt_text, model, input_text):
    """Construct the exact subprocess argv for one `claude -p` call."""
    return [
        claude_bin,
        "-p",
        "--tools", "",
        "--strict-mcp-config",
        "--setting-sources", "",
        "--disable-slash-commands",
        "--no-session-persistence",
        "--system-prompt", prompt_text,
        "--model", model,
        "--output-format", "json",
        input_text,
    ]


def _looks_like_decline(result_text):
    if not result_text:
        return False
    head = result_text.strip().lower()[:400]
    return any(marker in head for marker in _DECLINE_MARKERS)


def _sha256_len(text):
    if text is None:
        return None, 0
    b = text.encode("utf-8", errors="replace")
    return hashlib.sha256(b).hexdigest(), len(b)


def run_one_call(claude_bin, prompt_text, model, input_text, timeout_s):
    """Run a single `claude -p` subprocess call in a dedicated empty tmp
    cwd outside ~/Documents. Returns a dict with raw outcome fields; does
    NOT retry (caller handles retry) and does NOT write telemetry."""
    argv = build_argv(claude_bin, prompt_text, model, input_text)
    tmp_cwd = tempfile.mkdtemp(prefix="cxs4-driver-")
    t0 = time.monotonic()
    outcome = {
        "argv": argv,
        "exit_code": None,
        "wall_ms": None,
        "stdout": None,
        "stderr": None,
        "timed_out": False,
        "parse_error": None,
    }
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            cwd=tmp_cwd,
            timeout=timeout_s,
        )
        outcome["exit_code"] = proc.returncode
        outcome["stdout"] = proc.stdout
        outcome["stderr"] = proc.stderr
    except subprocess.TimeoutExpired as e:
        outcome["timed_out"] = True
        outcome["exit_code"] = None
        outcome["stdout"] = e.stdout if isinstance(e.stdout, str) else None
        outcome["stderr"] = e.stderr if isinstance(e.stderr, str) else None
    finally:
        outcome["wall_ms"] = int((time.monotonic() - t0) * 1000)
        shutil.rmtree(tmp_cwd, ignore_errors=True)
    return outcome


def run_stage_call(claude_bin, paper_id, stage, model, prompt_text,
                    input_text, timeout_s=DEFAULT_TIMEOUT_S):
    """Run one paper/stage call with the retry + decline policy. Returns
    the telemetry record (dict) ready to append as JSONL. Never raises for
    an ordinary subprocess failure; a programmer error in argument
    construction still raises."""
    # Fail closed, per call, right before building the subprocess argv:
    # re-verify the prompt text hashes to the frozen value for this stage.
    # (Entry points also check this once up front before any dispatch;
    # this is defense in depth and is what populates prompt_sha256 below.)
    prompt_sha256 = check_prompt_integrity(stage, prompt_text)

    rec = {
        "paper_id": paper_id,
        "stage": stage,
        "model_requested": model,
        "model_canonical": None,
        "prompt_sha256": prompt_sha256,
        "input_tokens": None,
        "cache_creation_input_tokens": None,
        "cache_read_input_tokens": None,
        "output_tokens": None,
        "exit_code": None,
        "wall_ms": None,
        "ts": None,
        "result_text_sha256": None,
        "result_text_len": None,
    }

    # NOTE on exit_code semantics: rec["exit_code"] reflects the FINAL
    # outcome of the call (after retries), not necessarily the literal
    # subprocess returncode of the last attempt. A timeout is recorded as
    # -1; a JSON-parse failure that survives both attempts (subprocess
    # exited 0 but produced unusable output) is recorded as -2, so that
    # "exit_code == 0" reliably means "got a usable, parsed response" for
    # every caller that filters telemetry on exit_code.
    attempt_errors = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        is_last_attempt = attempt == MAX_ATTEMPTS
        rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        outcome = run_one_call(claude_bin, prompt_text, model, input_text,
                                timeout_s)
        rec["wall_ms"] = outcome["wall_ms"]

        if outcome["timed_out"]:
            attempt_errors.append("timeout after %ss (attempt %d/%d)" % (
                timeout_s, attempt, MAX_ATTEMPTS))
            if not is_last_attempt:
                time.sleep(BACKOFF_S)
                continue
            rec["exit_code"] = -1
            rec["error"] = "; ".join(attempt_errors)
            return rec

        if outcome["exit_code"] != 0:
            attempt_errors.append(
                "non-zero exit %s (attempt %d/%d): %s" % (
                    outcome["exit_code"], attempt, MAX_ATTEMPTS,
                    (outcome["stderr"] or "")[:500]))
            if not is_last_attempt:
                time.sleep(BACKOFF_S)
                continue
            rec["exit_code"] = outcome["exit_code"]
            rec["error"] = "; ".join(attempt_errors)
            return rec

        # exit 0 — parse JSON stdout.
        try:
            payload = json.loads(outcome["stdout"])
        except (json.JSONDecodeError, TypeError) as e:
            attempt_errors.append("JSON parse error (attempt %d/%d): %s" % (
                attempt, MAX_ATTEMPTS, e))
            if not is_last_attempt:
                time.sleep(BACKOFF_S)
                continue
            # Subprocess exited 0 but gave unusable output on every
            # attempt — record this as a failure (exit_code != 0), not a
            # silent success.
            rec["exit_code"] = -2
            rec["error"] = "; ".join(attempt_errors)
            return rec

        # Got a parseable response — this attempt is the final outcome,
        # whether or not earlier attempts failed transiently.
        rec["exit_code"] = 0
        if attempt_errors:
            rec["retried"] = True
            rec["prior_attempt_errors"] = "; ".join(attempt_errors)

        usage = payload.get("usage") or {}
        rec["input_tokens"] = usage.get("input_tokens")
        rec["cache_creation_input_tokens"] = usage.get(
            "cache_creation_input_tokens")
        rec["cache_read_input_tokens"] = usage.get("cache_read_input_tokens")
        rec["output_tokens"] = usage.get("output_tokens")

        model_usage = payload.get("modelUsage") or {}
        for model_id, mu in model_usage.items():
            canonical = (mu or {}).get("canonicalModel")
            if canonical:
                rec["model_canonical"] = canonical
                break
        if rec["model_canonical"] is None and model_usage:
            rec["model_canonical"] = next(iter(model_usage.keys()))

        result_text = payload.get("result")
        sha, length = _sha256_len(result_text if isinstance(result_text, str) else None)
        rec["result_text_sha256"] = sha
        rec["result_text_len"] = length

        is_error = bool(payload.get("is_error"))
        declined = is_error or _looks_like_decline(
            result_text if isinstance(result_text, str) else "")
        if declined:
            rec["declined"] = True
            # Spike rule §2a: a decline halts at this paper. No retry, no
            # model reroute.
            return rec

        # success
        return rec

    # Should not fall through, but guard anyway.
    return rec


def append_jsonl(path, rec):
    with _out_lock:
        with open(path, "a") as f:
            f.write(json.dumps(rec) + "\n")


def _load_text(path):
    with open(path, "r") as f:
        return f.read()


def run_single_paper_cli(args):
    prompt_text = _load_text(args.prompt_file)
    # Fail closed BEFORE any subprocess call is made.
    check_prompt_integrity(args.stage, prompt_text)
    input_text = _load_text(args.input_file)
    rec = run_stage_call(
        claude_bin=args.claude_bin,
        paper_id=args.paper_id,
        stage=args.stage,
        model=args.model,
        prompt_text=prompt_text,
        input_text=input_text,
        timeout_s=args.timeout,
    )
    append_jsonl(args.out, rec)
    return rec


def run_batch_manifest(args):
    prompt_text = _load_text(args.prompt_file)
    # Fail closed BEFORE any subprocess call is made, and before spinning
    # up the pool — one mismatched prompt file would otherwise fail every
    # row identically after wasted subprocess spin-up.
    check_prompt_integrity(args.stage, prompt_text)
    rows = []
    with open(args.batch_manifest, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    def _worker(row):
        input_text = _load_text(row["input_file"])
        rec = run_stage_call(
            claude_bin=args.claude_bin,
            paper_id=row["paper_id"],
            stage=args.stage,
            model=args.model,
            prompt_text=prompt_text,
            input_text=input_text,
            timeout_s=args.timeout,
        )
        append_jsonl(args.out, rec)
        return rec

    results = []
    # Cap concurrency at MAX_CONCURRENCY (<=2 subprocess calls in flight).
    workers = min(MAX_CONCURRENCY, max(1, len(rows)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for rec in ex.map(_worker, rows):
            results.append(rec)
    return results


def build_parser():
    p = argparse.ArgumentParser(
        description="headless subprocess driver: one claude -p call per "
                    "paper per stage, no chat/sub-agent context accumulation.")
    p.add_argument("--stage", choices=["restatement", "extraction"],
                    required=True)
    p.add_argument("--model", choices=["haiku", "opus"], required=True)
    p.add_argument("--prompt-file", required=True,
                    help="path to the frozen stage prompt (read verbatim, "
                         "passed as --system-prompt)")
    p.add_argument("--out", required=True,
                    help="telemetry JSONL path (appended to)")
    p.add_argument("--claude-bin", default="claude",
                    help="override the claude CLI binary (for testing "
                         "against a shim; default: claude)")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S,
                    help="subprocess timeout in seconds (default %d)" %
                         DEFAULT_TIMEOUT_S)

    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--paper-id", help="single-paper mode: openalex id")
    mode.add_argument("--batch-manifest",
                       help="batch mode: jsonl with {paper_id, input_file} "
                            "rows, driven under the <=2 concurrency cap")

    p.add_argument("--input-file",
                    help="single-paper mode: path to the text to send "
                         "(raw paper text for restatement, restatement "
                         "output text for extraction). Required with "
                         "--paper-id.")
    return p


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)

    if args.paper_id and not args.input_file:
        p.error("--input-file is required with --paper-id")

    try:
        if args.paper_id:
            rec = run_single_paper_cli(args)
            print(json.dumps(rec, indent=2))
            return (0 if rec.get("exit_code") == 0 and not rec.get("declined")
                     else 1)
        else:
            recs = run_batch_manifest(args)
            print(json.dumps(recs, indent=2))
            failures = [r for r in recs
                        if r.get("exit_code") != 0 or r.get("declined")]
            return 1 if failures else 0
    except PromptIntegrityError as e:
        print("headless_driver: PROMPT INTEGRITY CHECK FAILED — refusing "
              "to call claude -p: %s" % e, file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
