#!/usr/bin/env python3
"""
federation-watcher — polls sessionbridge channels and routes wake events to
per-persona wake files so multiple agent terminals fire simultaneously.

Architecture
============
One daemon process polls all channels. When it detects an actionable event it
writes to ~/.federation-watcher/wake/{persona} for every persona mentioned.
Each agent terminal runs:

    Monitor(command="tail -f -n 0 ~/.federation-watcher/wake/PERSONA",
            persistent=True)

The Monitor fires the moment the watcher appends a line — fan-out is
simultaneous because all wake files are written in the same iteration.

Wake file line format (also printed to stdout for the host terminal):
    WAKE:MENTION    channel=... seq=... from=... persona=... snippet="..."
    WAKE:CLASSIFIED channel=... seq=... from=... filter=... snippet="..."
    QUEUED          channel=... seq=... from=... reason=busy|deferred

Busy flag
=========
Global: ~/.federation-watcher/busy
Per-persona: ~/.federation-watcher/busy.{persona}

@mention events are ALWAYS written to wake files regardless of busy flags
(§2.i — named mention requires same-cycle response).

Non-mention IMMEDIATE events are deferred when the relevant busy flag exists.
"""

import json
import os
import re
import subprocess
import sys
import time
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path(__file__).parent / "config.yaml"
SESSIONBRIDGE_CHANNELS = Path.home() / ".claude/mcp-servers/sessionbridge/state/channels"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Config ────────────────────────────────────────────────────────────────

def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    for key in ("wake_dir", "busy_flag", "state_dir", "deferred_queue"):
        if key in cfg:
            cfg[key] = Path(os.path.expanduser(str(cfg[key])))
    hb = cfg.get("heartbeat")
    if hb:
        for key in ("personas_conf", "status_file"):
            if key in hb:
                hb[key] = Path(os.path.expanduser(str(hb[key])))
    return cfg


# ── State helpers ─────────────────────────────────────────────────────────

def get_last_seq(state_dir: Path, channel: str) -> int:
    f = state_dir / f"last_seq_{channel}"
    return int(f.read_text().strip()) if f.exists() else -1


def set_last_seq(state_dir: Path, channel: str, seq: int) -> None:
    (state_dir / f"last_seq_{channel}").write_text(str(seq))


def discover_channels() -> list[str]:
    if not SESSIONBRIDGE_CHANNELS.exists():
        return []
    return sorted(
        p.stem for p in SESSIONBRIDGE_CHANNELS.glob("*.jsonl")
        if " " not in p.stem and not p.stem.startswith("#")
    )


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
    """Set last_seq to current max on first run — don't replay history."""
    path = SESSIONBRIDGE_CHANNELS / f"{channel}.jsonl"
    if not path.exists():
        return 0
    max_seq = 0
    with open(path, errors="replace") as f:
        for line in f:
            try:
                max_seq = max(max_seq, json.loads(line.strip()).get("seq", 0))
            except json.JSONDecodeError:
                pass
    set_last_seq(state_dir, channel, max_seq)
    return max_seq


# ── Fan-out routing ───────────────────────────────────────────────────────

def ensure_wake_file(wake_dir: Path, persona: str) -> Path:
    """Return path to persona's wake file, creating it if needed."""
    wake_dir.mkdir(parents=True, exist_ok=True)
    p = wake_dir / persona
    p.touch(exist_ok=True)
    return p


def write_wake(wake_dir: Path, persona: str, line: str) -> None:
    """Append a wake event line to a persona's wake file."""
    path = ensure_wake_file(wake_dir, persona)
    with open(path, "a") as f:
        f.write(line + "\n")


def is_persona_busy(busy_flag: Path, persona: str) -> bool:
    """True if global busy flag OR persona-specific busy flag is set."""
    return busy_flag.exists() or (busy_flag.parent / f"busy.{persona}").exists()


# ── Monitor-liveness heartbeat (crash-recovery R3, inter#91) ────────────────
# "Armed ≠ alive" — the wake-file fan-out above only *delivers* events; it
# never confirmed a seat's §2.i Monitor was still there to receive them.
# This section adds a periodic, low-overhead liveness sweep on top of it.

def load_seat_personas(personas_conf: Path) -> list[str]:
    """Parse persona names out of personas.conf — the same roster
    launch-federation.sh uses to open panes, so "active seat" here means
    exactly what it means there. Comment/blank lines skipped; the ADVISERS
    block is entirely commented (`# gemini | ...`) so it's excluded for
    free — advisers hold no seat and no Monitor to check."""
    if not personas_conf.exists():
        return []
    out: list[str] = []
    with open(personas_conf, errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            persona = line.split("|", 1)[0].strip()
            if persona:
                out.append(persona)
    return out


def check_monitor_alive(wake_dir: Path, persona: str) -> Optional[bool]:
    """External liveness check for a persona's §2.i wake-file Monitor.

    Each agent terminal arms its Monitor as a literal
    `tail -f -n 0 {wake_dir}/{persona}` child process on this host (see the
    module docstring's fan-out architecture) — so `pgrep -f` against that
    command line is a direct, zero-cost, zero-noise liveness probe: it never
    touches the persona's own wake file, so a healthy seat gets no extra
    wake event out of this check.

    Returns True (alive) / False (dead) / None (the check itself failed —
    e.g. pgrep unavailable) so a tooling hiccup surfaces as "unknown"
    rather than a false DEAD flag.
    """
    wake_path = wake_dir / persona
    try:
        result = subprocess.run(
            ["pgrep", "-f", f"tail -f -n 0 {wake_path}"],
            capture_output=True, text=True, timeout=5,
        )
        return bool(result.stdout.strip())
    except Exception:
        return None


def load_heartbeat_state(status_file: Path) -> dict:
    if not status_file.exists():
        return {}
    try:
        return json.loads(status_file.read_text())
    except json.JSONDecodeError:
        return {}


def save_heartbeat_state(status_file: Path, state: dict) -> None:
    """Atomic write via tmp + rename — deming polls this file, so a reader
    should never see a half-written one."""
    status_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = status_file.with_suffix(status_file.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(status_file)


def run_heartbeat_sweep(wake_dir: Path, personas_conf: Path,
                         notify_persona: str, prev_state: dict) -> dict:
    """One liveness sweep over every seat in personas.conf.

    Always updates every persona's entry in the returned state (cheap: one
    pgrep per seat). Only WRITES a wake-file notification on a genuine
    alive<->dead transition — a seat that's been dead for hours doesn't
    re-page deming every interval, and an `alive is None` (check failure)
    never counts as a transition in either direction.
    """
    now = _now_iso()
    personas = load_seat_personas(personas_conf)
    new_state: dict = {}
    for persona in personas:
        alive = check_monitor_alive(wake_dir, persona)
        prev = prev_state.get(persona, {})
        prev_alive = prev.get("alive")
        since = now if alive != prev_alive else prev.get("since", now)
        new_state[persona] = {"alive": alive, "last_checked": now, "since": since}

        if alive is False and prev_alive is not False:
            line = (
                f"MONITOR_DEAD persona={persona} last_checked={now} "
                f"msg=\"no live wake-file Monitor process found for {persona}\""
            )
            if persona != notify_persona:
                write_wake(wake_dir, notify_persona, line)
            emit(line)
        elif alive is True and prev_alive is False:
            line = f"MONITOR_RECOVERED persona={persona} last_checked={now}"
            if persona != notify_persona:
                write_wake(wake_dir, notify_persona, line)
            emit(line)

    return new_state


# ── Classification ────────────────────────────────────────────────────────

_NOISE_RE = [
    re.compile(r"^\s*ack\b", re.I),
    re.compile(r"^\s*acknowledged\b", re.I),
    re.compile(r"^\s*received\b", re.I),
    re.compile(r"^\s*lgtm\b", re.I),
    re.compile(r"^\s*\+1\b"),
    re.compile(r"^\s*👍"),
    re.compile(r"^\s*thank(s| you)\b", re.I),
    re.compile(r"progress\(\d+\)"),
    re.compile(r"states generated"),
    re.compile(r"checkpointing", re.I),
]

_IMMEDIATE_RE = [
    re.compile(r"§i4", re.I),
    re.compile(r"\b(approve|reject|block|defer|veto)\b", re.I),
    re.compile(r"\?"),
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
    stripped = text.strip()
    if len(stripped) < 60 and "?" not in stripped:
        return "NOISE"
    for pat in _NOISE_RE:
        if pat.search(stripped[:200]):
            return "NOISE"
    for pat in _IMMEDIATE_RE:
        if pat.search(stripped):
            return "IMMEDIATE"
    return "DEFERRED" if len(stripped) > 300 else "NOISE"


def classify_haiku(msg: dict, model: str) -> str:
    try:
        import requests as req
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return classify_regex(msg.get("text", ""))

        text = msg.get("text", "")[:600]
        prompt = (
            f"You are a message classifier for a software federation coordination channel.\n\n"
            f"Message from @{msg.get('from','?')} on #{msg.get('channel','?')}:\n{text}\n\n"
            "Classify as exactly one of:\n"
            "- IMMEDIATE: needs a response soon (review requests, direct questions, "
            "§I4 obligations, blocking issues, action items, escalations)\n"
            "- DEFERRED: substantive but not urgent (design proposals, progress "
            "reports, FYI updates)\n"
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
            json={"model": model, "max_tokens": 10,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=8,
        )
        resp.raise_for_status()
        verdict = resp.json()["content"][0]["text"].strip().upper()
        return verdict if verdict in ("IMMEDIATE", "DEFERRED", "NOISE") else "DEFERRED"
    except Exception:
        return classify_regex(msg.get("text", ""))


# ── Output helpers ────────────────────────────────────────────────────────

def snip(text: str, n: int = 130) -> str:
    text = text.replace("\n", " ").strip()
    return (text[:n] + "…") if len(text) > n else text


def emit(line: str) -> None:
    """Print to stdout (wakes the host terminal's Monitor if watching stdout)."""
    print(line, flush=True)


def route_wake(wake_dir: Path, watch_mentions: list[str], personas: list[str],
               line: str, stdout_personas: list[str]) -> None:
    """Write wake line to each persona's wake file; emit to stdout if relevant."""
    for persona in personas:
        write_wake(wake_dir, persona, line)
    # Emit to stdout for personas the host terminal cares about
    if any(p in stdout_personas for p in personas):
        emit(line)


def queue_message(queue_path: Path, msg: dict, reason: str) -> None:
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with open(queue_path, "a") as f:
        f.write(json.dumps({**msg, "watcher_reason": reason}) + "\n")


# ── Main loop ─────────────────────────────────────────────────────────────

def main() -> None:
    cfg = load_config()

    watch_mentions: list[str] = cfg.get("watch_mentions", [])
    channels_cfg = cfg.get("channels", "auto")
    filter_mode: str = cfg.get("filter_mode", "off")
    poll_interval: int = int(cfg.get("poll_interval", 10))
    haiku_model: str = cfg.get("haiku_model", "claude-haiku-4-5-20251001")
    busy_flag: Path = cfg["busy_flag"]
    wake_dir: Path = cfg["wake_dir"]
    state_dir: Path = cfg["state_dir"]
    deferred_queue: Path = cfg["deferred_queue"]

    heartbeat_cfg: dict = cfg.get("heartbeat") or {}
    heartbeat_enabled: bool = bool(heartbeat_cfg.get("enabled", False))
    heartbeat_interval: int = int(heartbeat_cfg.get("interval", 60))
    heartbeat_personas_conf: Optional[Path] = heartbeat_cfg.get("personas_conf")
    heartbeat_status_file: Optional[Path] = heartbeat_cfg.get("status_file")
    heartbeat_notify: str = heartbeat_cfg.get("notify_persona", "deming")
    if heartbeat_enabled and not (heartbeat_personas_conf and heartbeat_status_file):
        emit('WATCHER_ERROR msg="heartbeat.enabled but personas_conf/status_file missing"')
        heartbeat_enabled = False

    state_dir.mkdir(parents=True, exist_ok=True)
    wake_dir.mkdir(parents=True, exist_ok=True)

    channels = discover_channels() if channels_cfg == "auto" else list(channels_cfg)
    if not channels:
        emit('WATCHER_ERROR msg="no channels found"')
        sys.exit(1)

    # Initialize last_seq for unseen channels
    for ch in channels:
        if not (state_dir / f"last_seq_{ch}").exists():
            initialize_last_seq(state_dir, ch)

    # Pre-create wake files for known personas so tail -f -n 0 can open them
    for persona in watch_mentions:
        ensure_wake_file(wake_dir, persona)

    emit(
        f"WATCHER_START channels={channels} mentions={watch_mentions} "
        f"filter={filter_mode} poll={poll_interval}s "
        f"wake_dir={wake_dir} heartbeat={'on:' + str(heartbeat_interval) + 's' if heartbeat_enabled else 'off'}"
    )

    heartbeat_state: dict = {}
    last_heartbeat: float = 0.0
    if heartbeat_enabled:
        heartbeat_state = load_heartbeat_state(heartbeat_status_file)

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

                # ── @mention path — always fires, no filtering, no busy gate ──
                # Collect every mentioned persona (from mentions list + inline @name)
                mentioned_personas = list({
                    p for p in mentions
                    if p != from_persona  # don't self-notify
                })
                # Also catch inline @name patterns not in mentions list
                for m in re.findall(r"@([\w-]+)", text):
                    if m != from_persona and m not in mentioned_personas:
                        mentioned_personas.append(m)

                if mentioned_personas:
                    line = (
                        f"WAKE:MENTION channel={channel} seq={seq} "
                        f"from={from_persona} personas={mentioned_personas} "
                        f"snippet=\"{snip(text)}\""
                    )
                    # Write to each mentioned persona's wake file simultaneously
                    route_wake(wake_dir, watch_mentions, mentioned_personas,
                               line, watch_mentions)
                    max_seq = max(max_seq, seq)
                    continue

                # ── Non-mention path — apply filter ──
                if filter_mode == "off":
                    pass

                elif filter_mode in ("regex", "haiku"):
                    verdict = (
                        classify_haiku({**msg, "channel": channel}, haiku_model)
                        if filter_mode == "haiku"
                        else classify_regex(text)
                    )

                    if verdict == "IMMEDIATE":
                        # Route to all watch_mentions personas unless they're busy
                        # (non-mention messages don't know which persona they're for,
                        #  so we route to all configured watch_mentions personas)
                        active = [
                            p for p in watch_mentions
                            if not is_persona_busy(busy_flag, p)
                        ]
                        deferred_for = [
                            p for p in watch_mentions
                            if is_persona_busy(busy_flag, p)
                        ]

                        if active:
                            line = (
                                f"WAKE:CLASSIFIED channel={channel} seq={seq} "
                                f"from={from_persona} filter={filter_mode} "
                                f"snippet=\"{snip(text)}\""
                            )
                            route_wake(wake_dir, watch_mentions, active,
                                       line, watch_mentions)

                        if deferred_for:
                            queue_message(
                                deferred_queue,
                                {**msg, "channel": channel,
                                 "watcher_verdict": verdict,
                                 "deferred_for": deferred_for},
                                "busy",
                            )

                    elif verdict == "DEFERRED":
                        queue_message(
                            deferred_queue,
                            {**msg, "channel": channel, "watcher_verdict": verdict},
                            "deferred",
                        )
                    # NOISE → nothing

                max_seq = max(max_seq, seq)

            if max_seq > last_seq:
                set_last_seq(state_dir, channel, max_seq)

        if heartbeat_enabled and (time.time() - last_heartbeat) >= heartbeat_interval:
            heartbeat_state = run_heartbeat_sweep(
                wake_dir, heartbeat_personas_conf, heartbeat_notify, heartbeat_state
            )
            save_heartbeat_state(heartbeat_status_file, heartbeat_state)
            last_heartbeat = time.time()

        time.sleep(poll_interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        emit(f'WATCHER_ERROR msg="{e}"')
        sys.exit(1)
