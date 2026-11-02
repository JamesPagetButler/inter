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

Roster-only wake files (inter#271 item 3)
==========================================
A wake FILE is written only for a handle the roster resolves — the union of
config.yaml's `watch_mentions` and the canonical `personas.conf` registry
(`load_seat_personas`, the same roster `heartbeat` already reads). Every
other `@token` in a message (a commit sha, `@v7`, a typo) gets exactly one
`WAKE:SKIP` log line and no file — sender typos are already surfaced back to
the sender via sessionbridge's own `mention_warnings`, so nothing is lost,
only the junk-file growth in `wake/` is. See `resolve_roster()` /
`route_wake()`. One-off cleanup of the pre-existing junk files lives in
`quarantine_nonroster_wake_files.py` (moves, never deletes).

Aliases and extra recipients (inter#271 B1, foreman review 2026-11-01)
========================================================================
The roster-only filter above would have turned real, actively-used traffic
into dropped log lines: some senders address a seat by an older/shorthand
handle (`bragi` for `edda-implementor`, `bma` for `bma-implementor`, ...)
that was never itself a launched seat, and `antigravity` is a legitimate
non-seat wake-file reader (its own bridge-waker) with no personas.conf
entry at all. config.yaml's `aliases` map and `extra_recipients` list fix
this without cementing the pre-existing "nobody reads that file" deafness
bug into a silent drop:
  - `aliases: {alias: seat, ...}` — `route_wake()` resolves the alias to
    its seat and writes ONE wake file for the seat, never the alias's own
    file. If a message mentions both the alias and the seat, it's one
    wake carrying the HIGHEST role between them (`to` > `input` > `cc`).
  - `extra_recipients: [...]` — non-seat handles that still legitimately
    get a wake file (documented with their reader in config.yaml).
`quarantine_nonroster_wake_files.py` skips both categories — and prints a
separate "legacy alias" list for any alias's OWN leftover file on disk,
without moving it; a human (the foreman) decides those by hand. See
`resolve_mention_targets()`.

Three-role mentions (inter#271 item 2)
========================================
Every `WAKE:MENTION` line now carries a trailing `role=to|input|cc` field
(older lines, and any line from another writer that never added the field,
have no `role=` and count as `to` — see `wake-wait.sh` on the Nidavellir
side). Roles are classified from the message text alone, per `to` >
`input` > `cc`:

  - `to`    — a handle in the LEADING ADDRESSEE BLOCK (the text before the
              first " — ", space-emdash-space), outside any `(cc ...)`
              group. Responsibility: same-cycle reply, handled first.
  - `input` — any `@handle` in the BODY (after the separator). Input
              requested, not ownership — answered after that wake's `to`
              items; may decline or defer with a one-line note.
  - `cc`    — a handle inside a `(cc ...)` group in the leading block.
              Awareness only — delivered with the next real wake, or a
              `CC-DIGEST` within 4h (wake-wait.sh side).

  Fail-closed: no " — " separator, or an unclosed "(cc", and EVERY mention
  in the message is `to` — the input classifier never runs on that path (a
  parser miss can only cost an extra wake, never a missed ask).

  Always `to`, regardless of position: a message `from=beekeeper`, and any
  mention of `deming-escalate` (the escalation route).

  See `classify_mention_roles()` / `classify_roles_for_message()`.

Sender convention (recommended, not enforced by the parser): put the owner
in the leading block ("@deming — you're the §I4 reviewer"), @-name someone
in the body when you want their input but they're not on the hook
("...decision stands, cc @nugent for awareness, @wyrd-implementor what do
you think of the fallback?"), and use `(cc ...)` in the leading block for
pure awareness. Until senders adopt this, a real owner named only in the
body is classified `input` ("may decline"), not `to` — see inter#271.
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
    for key in ("wake_dir", "busy_flag", "state_dir", "deferred_queue", "personas_conf"):
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



def _parse_ts(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        return None


def initialize_last_seq_since(state_dir: Path, channel: str, since: datetime) -> int:
    """For a channel that appears AFTER the watcher started (inter#211): set
    last_seq to the highest seq posted *before* `since`, so every message posted
    since the watcher started is still delivered (a new channel's first
    @mention is not silently skipped), while older history is not replayed."""
    path = SESSIONBRIDGE_CHANNELS / f"{channel}.jsonl"
    if not path.exists():
        set_last_seq(state_dir, channel, 0)
        return 0
    before = 0
    with open(path, errors="replace") as f:
        for line in f:
            try:
                msg = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            t = _parse_ts(msg.get("ts", ""))
            if t is not None and t < since:
                before = max(before, msg.get("seq", 0))
    set_last_seq(state_dir, channel, before)
    return before


def refresh_channels(channels: list[str], state_dir: Path, since: datetime) -> list[str]:
    """Re-discover channels each poll (inter#211). Returns the names newly added
    to `channels` (mutated in place). A newly-seen channel with no state file is
    initialized via initialize_last_seq_since; one that already has state keeps it."""
    added = [ch for ch in discover_channels() if ch not in channels]
    for ch in added:
        if not (state_dir / f"last_seq_{ch}").exists():
            initialize_last_seq_since(state_dir, ch, since)
        channels.append(ch)
    return added

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


def resolve_roster(watch_mentions: list[str], personas_conf: Optional[Path]) -> set[str]:
    """The roster for item 3 (inter#271): the union of the two places a seat
    is listed today — config.yaml's `watch_mentions` and the canonical
    `personas.conf` registry `load_seat_personas()` already parses for the
    heartbeat sweep. A handle is roster if EITHER source names it, so
    reconciling the two can only widen who gets a wake file, never narrow
    it past what either config already granted."""
    roster = set(watch_mentions)
    if personas_conf is not None:
        roster.update(load_seat_personas(personas_conf))
    return roster


_ROLE_PRIORITY = {"to": 3, "input": 2, "cc": 1}


def _role_priority(role: str) -> int:
    # An unrecognised/missing role fails closed to the highest priority
    # ('to'), matching classify_mention_roles()'s own fail-closed default.
    return _ROLE_PRIORITY.get(role, 3)


def resolve_mention_targets(
    personas: list[str], aliases: dict[str, str], roles: Optional[dict[str, str]],
) -> tuple[list[str], Optional[dict[str, str]]]:
    """Resolve each mentioned handle through `aliases` to its real seat
    (inter#271 B1) — `bragi` -> `edda-implementor`, etc. — so the alias's
    OWN wake file is never written to; the resolved seat's is.

    Dedups: if a message mentions both an alias and its seat (or two
    aliases for the same seat), they collapse to ONE entry for the seat,
    keeping the HIGHEST role among all contributing mentions (to > input >
    cc — the same precedence classify_mention_roles() uses). Order is
    preserved by first occurrence among `personas`.

    `roles` may be None (the non-mention classified path has no per-
    mention roles at all); the returned role map is then also None.
    """
    resolved_order: list[str] = []
    best_role: dict[str, str] = {}
    for p in personas:
        target = aliases.get(p, p)
        if target not in resolved_order:
            resolved_order.append(target)
        if roles is not None:
            role = roles.get(p, "to")
            if target not in best_role or _role_priority(role) > _role_priority(best_role[target]):
                best_role[target] = role
    return resolved_order, (best_role if roles is not None else None)


def _waiter_pid_alive(state_dir: Path, persona: str) -> bool:
    """True iff state/<persona>.waiter.pid names a live process whose cmdline
    is wake-wait.sh for this persona (inter#157's churn-free waiter)."""
    try:
        pid = int((state_dir / f"{persona}.waiter.pid").read_text().strip())
        cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        return "wake-wait.sh" in cmd and persona in cmd.split()
    except Exception:
        return False


WAITER_REARM_GRACE_SEC = 120


def check_monitor_alive(wake_dir: Path, persona: str) -> Optional[bool]:
    """External liveness check for a persona's §2.i wake delivery.

    A seat counts as ALIVE if ANY of these holds (inter#271 follow-up: seats
    moved off the 30-min Monitor onto wake-wait.sh, and the old tail-only
    probe then reported every seat MONITOR_DEAD):
      1. wake-wait.sh waiter: state/<persona>.waiter.pid is a live process
         running wake-wait.sh for this persona;
      2. the waiter just fired: state/<persona>.offset was advanced within
         WAITER_REARM_GRACE_SEC (the one-shot exited on a real event and the
         seat is mid-turn, about to re-arm) -- not a dead seat;
      3. legacy Monitor: a literal `tail -f -n 0 {wake_dir}/{persona}` process.

    Returns True (alive) / False (dead) / None (the legacy probe itself
    failed AND no waiter evidence) so a tooling hiccup surfaces as
    "unknown" rather than a false DEAD flag.
    """
    state_dir = wake_dir.parent / "state"
    if _waiter_pid_alive(state_dir, persona):
        return True
    try:
        off = state_dir / f"{persona}.offset"
        if off.exists() and (time.time() - off.stat().st_mtime) < WAITER_REARM_GRACE_SEC:
            return True
    except Exception:
        pass
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


# ── Mention-role classification (inter#271 item 2) ──────────────────────────

_ADDRESSEE_SEP = " — "  # space, em dash, space
_MENTION_RE = re.compile(r"@([\w-]+)")
_CC_GROUP_RE = re.compile(r"\(cc\b([^()]*)\)", re.I)

# Mentions of these handles always resolve to 'to', regardless of position —
# the escalation route itself (wake/deming-escalate) and anything addressed
# to the beekeeper persona get the same unconditional-wake treatment as a
# from=beekeeper message (see classify_roles_for_message).
ALWAYS_TO_HANDLES = {"deming-escalate"}


def _handles_with_pos(text: str) -> list[tuple[str, int]]:
    return [(m.group(1), m.start()) for m in _MENTION_RE.finditer(text)]


def classify_mention_roles(text: str) -> dict[str, str]:
    """Classify every `@handle` in `text` as `to` / `input` / `cc`, per
    to > input > cc (one role per handle per message — inter#271 item 2,
    beekeeper ruling 2026-11-01).

    - `to`: a handle in the leading addressee block (before the first
      " — "), outside a `(cc ...)` group.
    - `cc`: a handle inside a `(cc ...)` group in that leading block.
    - `input`: any `@handle` in the body (after the separator). Overrides a
      `cc` classification for the same handle, but never a `to` one.

    Fail-closed: no " — " separator anywhere, or an unclosed "(cc" in the
    leading block, and EVERY mention in the whole message is `to` — the
    body/input branch below never runs on that path, so a parser miss can
    only cost an extra wake, never a missed ask.
    """
    all_handles = [h for h, _ in _handles_with_pos(text)]

    sep_idx = text.find(_ADDRESSEE_SEP)
    if sep_idx == -1:
        return {h: "to" for h in dict.fromkeys(all_handles)}

    leading = text[:sep_idx]
    body = text[sep_idx + len(_ADDRESSEE_SEP):]

    open_idx = leading.lower().find("(cc")
    if open_idx != -1 and leading.find(")", open_idx) == -1:
        # unclosed (cc ... in the leading block: fail closed, no input pass
        return {h: "to" for h in dict.fromkeys(all_handles)}

    cc_spans = [m.span() for m in _CC_GROUP_RE.finditer(leading)]

    def _in_cc(pos: int) -> bool:
        return any(s <= pos < e for s, e in cc_spans)

    roles: dict[str, str] = {}
    for h, pos in _handles_with_pos(leading):
        if _in_cc(pos):
            roles.setdefault(h, "cc")  # don't downgrade an earlier 'to'
        else:
            roles[h] = "to"  # 'to' always wins, whatever order it's seen in

    for h, _ in _handles_with_pos(body):
        if roles.get(h) != "to":
            roles[h] = "input"  # overrides a 'cc', never a 'to'

    return roles


def classify_roles_for_message(text: str, from_persona: str,
                                mentioned_personas: list[str]) -> dict[str, str]:
    """classify_mention_roles(), plus the two unconditional-`to` overrides:
    a message from=beekeeper, or a mention of an ALWAYS_TO_HANDLES handle
    (the deming-escalate route) — both wake regardless of the role the text
    alone would have produced (inter#271 item 2, C4).

    `mentioned_personas` is the caller's already-resolved mention list
    (msg["mentions"] plus any inline @name not already in it — see main()).
    A persona in that list with no @handle match in `text` itself (e.g. a
    mentions-list entry the inline regex didn't also catch) fails closed to
    `to` rather than being silently dropped from the role map.
    """
    roles = classify_mention_roles(text)
    force_to = from_persona == "beekeeper"
    for p in mentioned_personas:
        if force_to or p in ALWAYS_TO_HANDLES:
            roles[p] = "to"
        else:
            roles.setdefault(p, "to")
    return roles


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
               line: str, stdout_personas: list[str], roster: set[str],
               roles: Optional[dict[str, str]] = None,
               aliases: Optional[dict[str, str]] = None,
               extra_recipients: Optional[set[str]] = None) -> None:
    """Write wake line to each ALLOWED persona's wake file; emit to stdout
    if relevant.

    Item 3 (inter#271, R1/R2): a wake FILE is written only for a persona
    `resolve_roster()` resolves, plus `extra_recipients` (B1: legitimate
    non-seat consumers like `antigravity`) and `ALWAYS_TO_HANDLES` (the
    `deming-escalate` route). Every other mentioned token gets exactly one
    `WAKE:SKIP` log line and no file.

    B1 (inter#271 foreman review): `personas`/`roles` are resolved through
    `aliases` FIRST (`resolve_mention_targets()`) — an alias's own file is
    never written to; its seat's is, deduped to one entry with the
    highest role if both were mentioned.

    Item 2 (inter#271): when `roles` is given (the @mention path), each
    persona's own copy of the line gets ITS role appended as a trailing
    `role=to|input|cc` field — personas in one message can carry different
    roles, so the line is no longer byte-identical across every wake file
    it lands in. `roles` is omitted (None) for the non-mention classified
    path, which has no addressee structure to classify.
    """
    personas, roles = resolve_mention_targets(personas, aliases or {}, roles)
    allowed = roster | (extra_recipients or set()) | ALWAYS_TO_HANDLES

    known = [p for p in personas if p in allowed]
    unknown = [p for p in personas if p not in known]

    for persona in known:
        persona_line = line if roles is None else f"{line} role={roles.get(persona, 'to')}"
        write_wake(wake_dir, persona, persona_line)

    for persona in unknown:
        emit(f'WAKE:SKIP persona={persona} reason=not-in-roster line="{line}"')

    # Emit to stdout for personas the host terminal cares about
    if any(p in stdout_personas for p in known):
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

    # Roster for item 3 (inter#271 R1/R2): reconcile config.yaml's own
    # `personas_conf` (if set) with the heartbeat's, then union with
    # watch_mentions — see resolve_roster()'s docstring.
    personas_conf_path: Optional[Path] = cfg.get("personas_conf") or heartbeat_personas_conf
    roster: set[str] = resolve_roster(watch_mentions, personas_conf_path)

    # B1 (inter#271 foreman review): aliases + extra, non-seat recipients —
    # see the module docstring's "Aliases and extra recipients" section.
    aliases: dict[str, str] = cfg.get("aliases") or {}
    extra_recipients: set[str] = set(cfg.get("extra_recipients") or [])

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

    started_at = datetime.now(timezone.utc)
    while True:
        if channels_cfg == "auto":
            for ch in refresh_channels(channels, state_dir, started_at):
                emit(f"WATCHER_CHANNEL_ADDED channel={ch}")
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
                    roles = classify_roles_for_message(text, from_persona, mentioned_personas)
                    # Write to each mentioned persona's wake file simultaneously
                    route_wake(wake_dir, watch_mentions, mentioned_personas,
                               line, watch_mentions, roster, roles=roles,
                               aliases=aliases, extra_recipients=extra_recipients)
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
                                       line, watch_mentions, roster,
                                       aliases=aliases, extra_recipients=extra_recipients)

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
