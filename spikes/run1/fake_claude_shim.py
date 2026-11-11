#!/usr/bin/env python3
"""Test-only stand-in for the real `claude -p ... --output-format json`
CLI, used to unit-test headless_driver.py's argument construction and JSON
parsing WITHOUT making any real API call.

Mimics the argv shape the driver constructs:
    fake_claude_shim.py -p --tools "" --strict-mcp-config \
        --setting-sources "" --disable-slash-commands \
        --no-session-persistence --system-prompt "<prompt>" \
        --model <haiku|opus> --output-format json "<input text>"

Behavior is controlled by markers inside the trailing positional input
text, so tests can drive every driver code path deterministically:
  - "TRIGGER_DECLINE"     -> is_error: true, refusal-shaped result text.
  - "TRIGGER_FAIL_ONCE"   -> exits 1 on the first call for a given input,
                             exits 0 (success) on a retry. State is kept
                             in a per-input counter file under
                             $CXS4_SHIM_STATE_DIR (default: system tmp).
  - "TRIGGER_FAIL_ALWAYS" -> always exits 1 (non-zero exit).
  - "TRIGGER_TIMEOUT"     -> sleeps 10s (use a short --timeout in the
                             caller to force a TimeoutExpired).
  - "TRIGGER_BAD_JSON"    -> exits 0 but prints non-JSON stdout.
  - anything else         -> ordinary success response.
"""
import hashlib
import json
import os
import sys
import tempfile
import time


def _state_path(input_text):
    state_dir = os.environ.get("CXS4_SHIM_STATE_DIR") or tempfile.gettempdir()
    os.makedirs(state_dir, exist_ok=True)
    key = hashlib.sha256(input_text.encode("utf-8")).hexdigest()[:16]
    return os.path.join(state_dir, "cxs4-shim-%s.count" % key)


def main():
    argv = sys.argv[1:]
    if not argv:
        print("fake_claude_shim: no args", file=sys.stderr)
        return 2
    input_text = argv[-1]

    try:
        model_idx = argv.index("--model")
        model = argv[model_idx + 1]
    except (ValueError, IndexError):
        model = "unknown"

    canonical = {
        "haiku": "claude-haiku-4-5-20251001",
        "opus": "claude-opus-4-5-20251101",
    }.get(model, "claude-unknown")

    if "TRIGGER_TIMEOUT" in input_text:
        time.sleep(10)
        # fall through to a normal success if not killed by the caller's
        # own timeout first.

    if "TRIGGER_BAD_JSON" in input_text:
        print("not json at all {{{")
        return 0

    if "TRIGGER_FAIL_ALWAYS" in input_text:
        print("simulated hard failure", file=sys.stderr)
        return 1

    if "TRIGGER_FAIL_ONCE" in input_text:
        path = _state_path(input_text)
        count = 0
        if os.path.exists(path):
            with open(path) as f:
                count = int(f.read().strip() or "0")
        count += 1
        with open(path, "w") as f:
            f.write(str(count))
        if count == 1:
            print("simulated transient failure (attempt 1)", file=sys.stderr)
            return 1
        # second+ attempt: succeed below.

    if "TRIGGER_DECLINE" in input_text:
        payload = {
            "result": "I can't help with that request.",
            "is_error": True,
            "usage": {
                "input_tokens": 120,
                "output_tokens": 12,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            },
            "modelUsage": {
                "fake/%s" % model: {"canonicalModel": canonical},
            },
        }
        print(json.dumps(payload))
        return 0

    payload = {
        "result": "Shim OK — stage output for model=%s, input_len=%d" % (
            model, len(input_text)),
        "is_error": False,
        "usage": {
            "input_tokens": 500 + len(input_text) % 100,
            "output_tokens": 80,
            "cache_creation_input_tokens": 400,
            "cache_read_input_tokens": 0,
        },
        "modelUsage": {
            "fake/%s" % model: {"canonicalModel": canonical},
        },
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
