#!/usr/bin/env python3
"""
federation-watcher — polls sessionbridge channels and prints actionable events.

Designed to run under the Monitor tool (persistent=True). The main agent wakes
on any stdout line starting with WAKE:. Deferred items go to a queue file and
are silent on stdout.

Output format:
  WATCHER_START  channels=[...] mentions=[...] filter=...
  WAKE:MENTION   channel=... seq=... from=... persona=... snippet="..."
  WAKE:CLASSIFIED channel=... seq=... from=... filter=regex|haiku snippet="..."
  QUEUED         channel=... seq=... from=... reason=busy|deferred
  WATCHER_ERROR  msg=...

Busy flag protocol:
  @mentions always wake (ignore busy flag).
  Non-mention IMMEDIATE items are deferred when busy flag file exists.
  Set:   touch ~/.federation-watcher/busy
  Clear: rm   ~/.federation-watcher/busy

Deferred queue:
  ~/.federation-watcher/deferred.jsonl — one JSON object per line.
  Main agent reads this at task boundaries.
"""

import json
import os
import re
import sys
import time
import yaml
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

CONFIG_PATH = Path(__file__).parent / "config.yaml"
SESSIONBRIDGE_CHANNELS = Path.home() / ".claude/mcp-servers/sessionbridge/state/channels"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    # Expand ~ in path fields
    for key in ("busy_flag", "state_dir", "deferred_queue"):
        if key in cfg:
            cfg[key] = Path(os.path.expanduser(cfg[key]))
    return cfg


# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def get_last_seq(state_dir: Path, channel: str) -> int:
    f = state_dir / f"last_seq_{channel}"
    return int(f.read_text().strip()) if f.exists() else -1


def set_last_seq(state_dir: Path, channel: str, seq: int) -> None:
    f = state_dir / f"last_seq_{channel}"
    f.write_text(str(seq))


def discover_channels() -> list[str]:
    """Return all channel names from *.jsonl files that look like real channels."""
    if not SESSIONBRIDGE_CHANNELS.exists():
        return []
    names = []
    for p in SESSIONBRIDGE_CHANNELS.glob("*.jsonl"):
        name = p.stem
        # Skip files with spaces (chime-in variants) and '#'-prefixed
        if " " not in name and not name.startswith("#"):
            names.append(name)
    return sorted(names)


def read_new_messages(channel: str, last_seq: int) -> list[dict]:
    path = SESSIONBRIDGE_CHANNELS / f"{channel}.jsonl"
    if not path.exists():
        return []
    msgs = []
    with open(path, errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                if msg.get("seq", 0) > last_seq:
                    msgs.append(msg)
            except json.JSONDecodeError:
                pass
    return sorted(msgs, key=lambda m: m.get("seq", 0))


def initialize_last_seq(state_dir: Path, channel: str) -> int:
    """On first run, set last_seq to current max so we don't replay history."""
    path = SESSIONBRIDGE_CHANNELS / f"{channel}.jsonl"
    if not path.exists():
        return 0
    max_seq = 0
    with open(path, errors="replace") as f:
        for line in f:
            try:
                msg = json.loads(line.strip())
                max_seq = max(max_seq, msg.get("seq", 0))
            except json.JSONDecodeError:
                pass
    set_last_seq(state_dir, channel, max_seq)
    return max_seq


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

# Regex patterns for quick noise detection (checked first, cheapest)
_NOISE_RE = [
    re.compile(r"^\s*ack\b", re.I),
    re.compile(r"^\s*acknowledged\b", re.I),
    re.compile(r"^\s*received\b", re.I),
    re.compile(r"^\s*lgtm\b", re.I),
    re.compile(r"^\s*\+1\b"),
    re.compile(r"^\s*👍"),
    re.compile(r"^\s*thank(s| you)\b", re.I),
    re.compile(r"progress\(\d+\)"),          # TLC progress lines
    re.compile(r"states generated"),         # TLC progress lines
    re.compile(r"checkpointing", re.I),
]

# Regex patterns that flag IMMEDIATE attention
_IMMEDIATE_RE = [
    re.compile(r"§i4", re.I),
    re.compile(r"\b(approve|reject|block|defer|veto)\b", re.I),
    re.compile(r"\?"),                        # any question
    re.compile(r"\bblocked\b", re.I),
    re.compile(r"\bsla\b", re.I),
    re.compile(r"\b(do|can|would|could|will) you\b", re.I),
    re.compile(r"\baction required\b", re.I),
    re.compile(r"\bneeds? (response|review|sign.?off)\b", re.I),
    re.compile(r"\bplease\b.{0,40}\breview\b", re.I),
    re.compile(r"\byour (read|review|verdict|sign.?off)\b", re.I),
    re.compile(r"\bescalat", re.I),
    re.compile(r"\bgate\b.{0,20}\bblock", re.I),
]


def classify_regex(text: str) -> str:
    """Return IMMEDIATE | DEFERRED | NOISE."""
    # Short messages with no question are almost always acks
    stripped = text.strip()
    if len(stripped) < 60 and "?" not in stripped:
        for pat in _NOISE_RE:
            if pat.search(stripped):
                return "NOISE"
        # Short, no question, no noise pattern → still likely low-signal
        return "NOISE"

    # Check explicit noise patterns
    for pat in _NOISE_RE:
        if pat.search(stripped[:200]):
            return "NOISE"

    # Check immediate patterns
    for pat in _IMMEDIATE_RE:
        if pat.search(stripped):
            return "IMMEDIATE"

    # Substantive length but no immediate trigger → DEFERRED
    if len(stripped) > 300:
        return "DEFERRED"

    return "NOISE"


def classify_haiku(msg: dict, model: str) -> str:
    """Return IMMEDIATE | DEFERRED | NOISE using Claude Haiku API.
    Falls back to regex on any error.
    """
    try:
        import requests as req

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return classify_regex(msg.get("text", ""))

        text = msg.get("text", "")[:600]
        from_persona = msg.get("from", "unknown")
        channel = msg.get("channel", "unknown")

        prompt = (
            f"You are a message classifier for a software federation coordination channel.\n\n"
            f"Message from @{from_persona} on #{channel}:\n{text}\n\n"
            "Classify as exactly one of:\n"
            "- IMMEDIATE: needs a response soon (review requests, direct questions, §I4 obligations, blocking issues, action items, escalations)\n"
            "- DEFERRED: substantive but not urgent (design proposals, progress reports, FYI updates, long analysis posts)\n"
            "- NOISE: acks, confirmations, routine status, no action needed\n\n"
            "Reply with only the single classification word."
        )

        resp = req.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 10,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=8,
        )
        resp.raise_for_status()
        verdict = resp.json()["content"][0]["text"].strip().upper()
        if verdict in ("IMMEDIATE", "DEFERRED", "NOISE"):
            return verdict
        return "DEFERRED"

    except Exception:
        return classify_regex(msg.get("text", ""))


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def snip(text: str, max_len: int = 130) -> str:
    text = text.replace("\n", " ").strip()
    return (text[:max_len] + "…") if len(text) > max_len else text


def emit(line: str) -> None:
    print(line, flush=True)


def queue_message(queue_path: Path, msg: dict, reason: str) -> None:
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with open(queue_path, "a") as f:
        f.write(json.dumps({**msg, "watcher_reason": reason}) + "\n")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    cfg = load_config()

    watch_mentions: list[str] = cfg.get("watch_mentions", [])
    channels_cfg = cfg.get("channels", "auto")
    filter_mode: str = cfg.get("filter_mode", "off")
    poll_interval: int = int(cfg.get("poll_interval", 10))
    haiku_model: str = cfg.get("haiku_model", "claude-haiku-4-5-20251001")
    busy_flag: Path = cfg["busy_flag"]
    state_dir: Path = cfg["state_dir"]
    deferred_queue: Path = cfg["deferred_queue"]

    state_dir.mkdir(parents=True, exist_ok=True)

    # Resolve channel list
    if channels_cfg == "auto":
        channels = discover_channels()
    else:
        channels = list(channels_cfg)

    if not channels:
        emit("WATCHER_ERROR msg=\"no channels found — check sessionbridge state dir\"")
        sys.exit(1)

    # Initialize last_seq for any channel we haven't seen before
    for ch in channels:
        if not (state_dir / f"last_seq_{ch}").exists():
            initialize_last_seq(state_dir, ch)

    emit(
        f"WATCHER_START channels={channels} "
        f"mentions={watch_mentions} filter={filter_mode} "
        f"poll={poll_interval}s"
    )

    while True:
        for channel in channels:
            last_seq = get_last_seq(state_dir, channel)
            new_msgs = read_new_messages(channel, last_seq)

            if not new_msgs:
                continue

            max_seq = last_seq
            for msg in new_msgs:
                seq = msg.get("seq", 0)
                from_persona = msg.get("from", "?")
                text = msg.get("text", "")
                mentions: list[str] = msg.get("mentions", [])

                # --- @mention check (always immediate, no filtering, no busy gate) ---
                matched_persona = next(
                    (p for p in watch_mentions if p in mentions or f"@{p}" in text),
                    None,
                )
                if matched_persona:
                    emit(
                        f"WAKE:MENTION channel={channel} seq={seq} "
                        f"from={from_persona} persona={matched_persona} "
                        f"snippet=\"{snip(text)}\""
                    )
                    max_seq = max(max_seq, seq)
                    continue

                # --- Non-mention: apply filter ---
                if filter_mode == "off":
                    pass  # Only mentions wake; everything else is ignored

                elif filter_mode in ("regex", "haiku"):
                    if filter_mode == "haiku":
                        verdict = classify_haiku({**msg, "channel": channel}, haiku_model)
                    else:
                        verdict = classify_regex(text)

                    if verdict == "IMMEDIATE":
                        if busy_flag.exists():
                            queue_message(deferred_queue, {**msg, "channel": channel}, "busy")
                            emit(
                                f"QUEUED channel={channel} seq={seq} "
                                f"from={from_persona} reason=busy"
                            )
                        else:
                            emit(
                                f"WAKE:CLASSIFIED channel={channel} seq={seq} "
                                f"from={from_persona} filter={filter_mode} "
                                f"snippet=\"{snip(text)}\""
                            )

                    elif verdict == "DEFERRED":
                        queue_message(deferred_queue, {**msg, "channel": channel}, "deferred")
                        # Silent — don't wake main agent

                    # NOISE → nothing

                max_seq = max(max_seq, seq)

            if max_seq > last_seq:
                set_last_seq(state_dir, channel, max_seq)

        time.sleep(poll_interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        emit(f"WATCHER_ERROR msg=\"{e}\"")
        sys.exit(1)
