#!/usr/bin/env python3
"""
federation-nudger — the safety net for a dead wake-waiter (inter#75).

Why
===
`wake-wait.sh` is a one-shot, session-bound waiter. When a seat doesn't re-arm
it after a fire, or the session dies, the seat goes deaf silently: watcher.py
keeps appending WAKE lines to `wake/<persona>`, and nobody reads them. This
process closes that gap by *pushing*: when a seat has unconsumed wake lines and
no live waiter, and its pane is provably idle, it types one fixed-template
nudge into the seat's tmux pane. watcher.py is untouched (D1).

Decisions (spec: inter#75 "Strike spec", D1-D9)
==============================================
D2  Unconsumed = wake-file lines past `state/<persona>.offset` (the waiter's
    lines-consumed counter). Only the structural `channel=` / `seq=` fields of
    `WAKE:MENTION` / `WAKE:CLASSIFIED` lines are parsed; the snippet is never
    read into a nudge.
D3  A live waiter (`state/<persona>.waiter.pid`, pid alive and really a
    wake-wait process) means do nothing.
D4  Targets are only `fed:<persona>` windows for personas.conf rows.
D5  Idle = composer is `❯` + nothing, or only dim (SGR 2) ghost suggestion;
    no `esc to interrupt`; no permission/choice dialog; pane command `claude`.
    Anything unrecognised is UNKNOWN, and UNKNOWN is not idle (fail-closed).
D6  Nudge text is a fixed template from a validated channel + int seq.
D7  `send-keys -l <text>` then `Enter`; never a bare Enter. Re-capture after
    sending: text still in the composer = not delivered.
D8  One nudge per wake, persisted. Ack = the waiter offset passing the line
    within ACK_MIN. No ack, or non-delivery -> escalate ONCE (escalation log +
    a wake line to herschel; herschel's own case goes to deming). No re-nudge.
D9  --dry-run is the default; only --enforce sends or writes escalations.

Every decision is a pure function below; tmux, the filesystem, the clock and
process liveness sit behind thin interfaces so the tests use fakes.

Run:
    python3 federation-watcher/nudger.py --once          # one dry-run tick
    python3 federation-watcher/nudger.py                 # dry-run daemon
    python3 federation-watcher/nudger.py --enforce       # beekeeper go only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

# ── Constants ─────────────────────────────────────────────────────────────

IDLE, BUSY, TYPED, DIALOG, UNKNOWN = "IDLE", "BUSY", "TYPED", "DIALOG", "UNKNOWN"
SCREEN_CLASSES = (IDLE, BUSY, TYPED, DIALOG, UNKNOWN)

TMUX_SESSION = "fed"                 # D4: the only session the nudger touches
ESCALATE_TO = "herschel"             # D8: first escalation tier
ESCALATE_TO_FALLBACK = "deming"      # D8: herschel's own case goes here

NAME_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")       # channel AND persona
SEQ_RE = re.compile(r"[0-9]{1,15}")                    # plain non-negative int
NUDGE_TEMPLATE = "[wake] @mention on {channel} seq {seq}: check your sessionbridge inbox"
NUDGE_MARKER = "[wake] @mention on"                    # used by post-send verify

# Structural prefix of watcher.py's two wake formats (see watcher.py main()):
#   WAKE:MENTION    channel=<c> seq=<n> from=... personas=[...] snippet="..."
#   WAKE:CLASSIFIED channel=<c> seq=<n> from=... filter=... snippet="..."
# Anchored at the start of the line, so text inside the snippet can never
# supply a channel/seq. Any other line (MONITOR_DEAD, our own escalation lines,
# QUEUED, ...) is not a nudgeable wake.
WAKE_LINE_RE = re.compile(r"^WAKE:(MENTION|CLASSIFIED) channel=(\S+) seq=(\S+)(?: |$)")

DEFAULT_WATCH_DIR = Path(os.path.expanduser("~/.federation-watcher"))
DEFAULT_PERSONAS_CONF = (Path(__file__).resolve().parent.parent
                         / "federation-terminals" / "personas.conf")
DEFAULT_ACK_MIN = 15.0
DEFAULT_POLL_SEC = 30.0
DEFAULT_VERIFY_DELAY_SEC = 2.0
TAIL_LINES = 25          # only the bottom of the screen is classified
PRUNE_AFTER_SEC = 14 * 24 * 3600


def now_iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).isoformat(timespec="seconds")


# ── D6: nudge text ────────────────────────────────────────────────────────

def validate_channel(channel: object) -> str:
    if not isinstance(channel, str) or not NAME_RE.fullmatch(channel):
        raise ValueError(f"refused channel {channel!r}")
    return channel


def validate_seq(seq: object) -> int:
    if isinstance(seq, bool):
        raise ValueError(f"refused seq {seq!r}")
    if isinstance(seq, int):
        if seq < 0:
            raise ValueError(f"refused seq {seq!r}")
        return seq
    if isinstance(seq, str) and SEQ_RE.fullmatch(seq):
        return int(seq)
    raise ValueError(f"refused seq {seq!r}")


def build_nudge_text(channel: object, seq: object) -> str:
    """The ONLY way a nudge string is made: fixed template, validated fields."""
    return NUDGE_TEMPLATE.format(channel=validate_channel(channel), seq=validate_seq(seq))


# ── D2: wake lines and offsets ────────────────────────────────────────────

@dataclass(frozen=True)
class Wake:
    line_no: int          # 1-based line number in the wake file
    kind: str             # MENTION | CLASSIFIED
    channel: str          # raw, NOT yet validated
    seq: str              # raw, NOT yet validated

    def key(self, persona: str) -> str:
        return f"{persona}|{self.channel}|{self.seq}"


def parse_wake_line(line: str, line_no: int = 0) -> Optional[Wake]:
    """Structural fields only. Returns None for a non-wake line."""
    m = WAKE_LINE_RE.match(line)
    if not m:
        return None
    return Wake(line_no=line_no, kind=m.group(1), channel=m.group(2), seq=m.group(3))


def complete_lines(text: str) -> list[str]:
    """Lines terminated by a newline, as `wc -l` (and so wake-wait.sh) counts
    them. A partially written last line is not yet a line."""
    parts = text.split("\n")
    return parts[:-1]


def effective_offset(offset_text: Optional[str], line_count: int,
                     baseline: Optional[int]) -> int:
    """Mirror wake-wait.sh's reading of `<persona>.offset`:
    - digits -> that value; larger than the file (rotated) -> 0;
    - present but garbage -> the waiter treats it as EOF, so do we;
    - missing (the waiter never armed) -> the nudger's own first-seen baseline,
      so history is never replayed (same rule as watcher.initialize_last_seq).
    """
    if offset_text is None:
        return min(baseline if baseline is not None else line_count, line_count)
    s = offset_text.strip()
    if not s.isdigit():
        return line_count
    n = int(s)
    return 0 if n > line_count else n


def unconsumed_wakes(lines: list[str], offset: int) -> list[Wake]:
    out = []
    for idx in range(max(offset, 0), len(lines)):
        w = parse_wake_line(lines[idx], idx + 1)
        if w is not None:
            out.append(w)
    return out


# ── D3: waiter liveness ───────────────────────────────────────────────────

def _proc_cmdline(pid: int) -> Optional[list[str]]:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return None
    return [a.decode(errors="replace") for a in raw.split(b"\0") if a]


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def waiter_alive(pidfile: Path, persona: str,
                 pid_exists: Callable[[int], bool] = _pid_exists,
                 cmdline: Callable[[int], Optional[list[str]]] = _proc_cmdline) -> bool:
    """True only for a pidfile naming a live process that is this persona's
    wake-wait. A missing/garbage pidfile, a dead pid, or a pid recycled by an
    unrelated process are all NOT a live waiter (the nudger must not stand
    down for a stale pidfile)."""
    try:
        s = pidfile.read_text().strip()
    except OSError:
        return False
    if not s.isdigit() or int(s) <= 0:
        return False
    pid = int(s)
    if not pid_exists(pid):
        return False
    argv = cmdline(pid)
    if argv is None:
        return True       # no /proc to check: trust the live pid
    return any("wake-wait" in a for a in argv) and persona in argv


# ── D5: screen classifier ─────────────────────────────────────────────────

_ESC_RE = re.compile(
    r"\x1b(?:\[([0-9;:?<=>]*)[ -/]*([@-~])"   # CSI ... final
    r"|\][^\x07\x1b]*(?:\x07|\x1b\\)"         # OSC ... BEL/ST
    r"|[@-Z\\-_])"                            # other 2-byte escapes
)
_DIALOG_PHRASES = ("do you want to proceed",)
_OPTION_CURSOR_RE = re.compile(r"❯\s*\d+\.\s")


def _apply_sgr(params: str, dim: bool) -> bool:
    """Track only the dim (SGR 2) attribute. Extended colours (38/48/58;5;n and
    ;2;r;g;b) are skipped whole so a colour index of 2 is never read as dim."""
    if params == "":
        return False
    parts = params.split(";")
    i = 0
    while i < len(parts):
        part = parts[i]
        head = part.split(":")[0]
        n = int(head) if head.isdigit() else 0
        if n == 0 or n == 22:
            dim = False
        elif n == 2:
            dim = True
        elif n in (38, 48, 58) and ":" not in part and i + 1 < len(parts):
            mode = parts[i + 1]
            i += 2 if mode == "5" else 4 if mode == "2" else 0
        i += 1
    return dim


def parse_screen(screen: str) -> list[list[tuple[str, bool]]]:
    """-> one list of (char, is_dim) cells per line. SGR state carries across
    lines, as tmux `capture-pane -e` emits it."""
    dim = False
    out: list[list[tuple[str, bool]]] = []
    for line in screen.split("\n"):
        cells: list[tuple[str, bool]] = []
        pos = 0
        for m in _ESC_RE.finditer(line):
            for ch in line[pos:m.start()]:
                cells.append((ch, dim))
            if m.group(2) == "m":
                dim = _apply_sgr(m.group(1) or "", dim)
            pos = m.end()
        for ch in line[pos:]:
            if ch != "\r":
                cells.append((ch, dim))
        out.append(cells)
    return out


def _text(cells: list[tuple[str, bool]]) -> str:
    return "".join(c for c, _ in cells)


def _is_rule(text: str) -> bool:
    return text.strip().startswith("───")


@dataclass
class _Screen:
    lines: list[list[tuple[str, bool]]]
    texts: list[str]
    composer: Optional[int]       # index into lines of the `❯` composer line


def _analyse(screen: str) -> _Screen:
    lines = parse_screen(screen)
    while lines and not _text(lines[-1]).strip():
        lines.pop()
    lines = lines[-TAIL_LINES:]
    texts = [_text(c) for c in lines]
    composer = None
    for i in range(1, len(lines)):
        if texts[i].lstrip().startswith("❯") and _is_rule(texts[i - 1]):
            composer = i
    return _Screen(lines, texts, composer)


def _composer_typed(sc: _Screen) -> str:
    """Non-dim text after the `❯` on the composer line ('' if none)."""
    if sc.composer is None:
        return ""
    cells = sc.lines[sc.composer]
    start = next(i for i, (c, _) in enumerate(cells) if c == "❯") + 1
    return "".join(c for c, d in cells[start:] if not d).strip()


def classify_screen(screen: Optional[str], current_command: Optional[str]) -> str:
    """IDLE / BUSY / TYPED / DIALOG / UNKNOWN. Only a positively recognised
    idle composer is IDLE; everything else fails closed."""
    if current_command != "claude" or not screen:
        return UNKNOWN
    sc = _analyse(screen)
    if not any(t.strip() for t in sc.texts):
        return UNKNOWN
    busy_from = 0 if sc.composer is None else max(sc.composer - 3, 0)
    if any("esc to interrupt" in t.lower() for t in sc.texts[busy_from:]):
        return BUSY
    for i, t in enumerate(sc.texts):
        if i == sc.composer:
            continue
        if _OPTION_CURSOR_RE.search(t) or any(p in t.lower() for p in _DIALOG_PHRASES):
            return DIALOG
    if sc.composer is None:
        return UNKNOWN
    if _composer_typed(sc):
        return TYPED
    return IDLE


def composer_typed_text(screen: Optional[str]) -> str:
    if not screen:
        return ""
    return _composer_typed(_analyse(screen))


def nudge_undelivered(screen_after: Optional[str]) -> bool:
    """D7 post-send check: the nudge still sitting in the composer (or a pane
    we can no longer read) means it was not delivered."""
    if screen_after is None:
        return True
    return NUDGE_MARKER in composer_typed_text(screen_after)


# ── D4: target allowlist ──────────────────────────────────────────────────

def tmux_target(persona: str) -> str:
    """Exact-match target (`=` disables tmux's prefix/fnmatch matching)."""
    return f"={TMUX_SESSION}:={persona}"


def is_allowed_target(target: str, personas: list[str]) -> bool:
    if target.count(":") != 1:
        return False
    session, window = target.split(":")
    session, window = session.removeprefix("="), window.removeprefix("=")
    return (session == TMUX_SESSION and window in personas
            and NAME_RE.fullmatch(window) is not None)


# ── D8: ack / escalation decisions ────────────────────────────────────────

def ack_status(nudged_at: float, line_no: int, offset: int, now: float,
               ack_window_sec: float) -> str:
    """'acked' | 'escalate' | 'wait'. The window is inclusive: an ack seen at
    exactly ACK_MIN counts."""
    if offset >= line_no:
        return "acked"
    if now - nudged_at > ack_window_sec:
        return "escalate"
    return "wait"


def escalation_target(persona: str) -> str:
    return ESCALATE_TO_FALLBACK if persona == ESCALATE_TO else ESCALATE_TO


def escalation_wake_line(persona: str, channel: str, seq: str, reason: str, ts: float) -> str:
    # Not a WAKE:MENTION/CLASSIFIED line, so the nudger never nudges on it.
    return (f"WAKE:NUDGE_ESCALATION persona={persona} channel={channel} seq={seq} "
            f"reason={reason} at={now_iso(ts)}")


def escalation_log_entry(persona: str, channel: str, seq: str, reason: str,
                         notify: str, ts: float) -> str:
    # Matches the escalation-log.md entry shape (one line per escalation).
    return (f"- **{now_iso(ts)} · {persona} / wake {channel} seq {seq} · "
            f"nudger→{notify}** · CAUSE: {reason} · resolution: pending "
            f"(escalated by federation-nudger, inter#75) · TTR —")


# ── personas.conf ─────────────────────────────────────────────────────────

def load_personas(personas_conf: Path) -> list[str]:
    """Same row rule as watcher.load_seat_personas; names must also be valid."""
    out: list[str] = []
    try:
        text = personas_conf.read_text(errors="replace")
    except OSError:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        persona = line.split("|", 1)[0].strip()
        if NAME_RE.fullmatch(persona):
            out.append(persona)
    return out


# ── Thin I/O interfaces ───────────────────────────────────────────────────

class Tmux:
    """Real tmux. Every call is to an exact-match `=fed:=<persona>` target, and
    send_keys re-checks the allowlist itself."""

    def __init__(self, personas: list[str]):
        self.personas = personas

    def _run(self, args: list[str]) -> Optional[str]:
        try:
            r = subprocess.run(["tmux", *args], capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return r.stdout if r.returncode == 0 else None

    def current_command(self, target: str) -> Optional[str]:
        out = self._run(["display-message", "-p", "-t", target, "#{pane_current_command}"])
        return None if out is None else out.strip()

    def capture(self, target: str) -> Optional[str]:
        return self._run(["capture-pane", "-e", "-p", "-t", target])

    def send_keys(self, target: str, args: list[str]) -> bool:
        if not is_allowed_target(target, self.personas):
            return False
        return self._run(["send-keys", "-t", target, *args]) is not None


class Files:
    """The watcher directory layout (all paths derived from one root)."""

    def __init__(self, watch_dir: Path, enforce: bool):
        self.root = watch_dir
        self.wake_dir = watch_dir / "wake"
        self.state_dir = watch_dir / "state"
        self.escalation_log = watch_dir / "escalation-log.md"
        name = "nudger-state.json" if enforce else "nudger-state.dry-run.json"
        self.state_file = self.state_dir / name

    def read(self, path: Path) -> Optional[str]:
        try:
            return path.read_text(errors="replace")
        except OSError:
            return None

    def append(self, path: Path, line: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(line + "\n")

    def load_state(self) -> dict:
        try:
            st = json.loads(self.state_file.read_text())
        except (OSError, json.JSONDecodeError):
            return {"version": 1, "baseline": {}, "records": {}}
        st.setdefault("baseline", {})
        st.setdefault("records", {})
        return st

    def save_state(self, state: dict) -> None:
        """Atomic (tmp + rename) so a restart never reads half a file."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, sort_keys=True))
        tmp.replace(self.state_file)


# ── The engine ────────────────────────────────────────────────────────────

class Nudger:
    def __init__(self, personas: list[str], files: Files, tmux, *, enforce: bool = False,
                 ack_min: float = DEFAULT_ACK_MIN, verify_delay: float = DEFAULT_VERIFY_DELAY_SEC,
                 clock: Callable[[], float] = time.time,
                 sleep: Callable[[float], None] = time.sleep,
                 alive: Callable[[Path, str], bool] = waiter_alive,
                 log: Callable[[str], None] = lambda s: print(s, flush=True)):
        self.personas = personas
        self.files = files
        self.tmux = tmux
        self.enforce = enforce
        self.ack_window = ack_min * 60.0
        self.verify_delay = verify_delay
        self.clock = clock
        self.sleep = sleep
        self.alive = alive
        self._log = log
        self.state = files.load_state()

    @property
    def mode(self) -> str:
        return "enforce" if self.enforce else "dry-run"

    def log(self, persona: str, action: str, **kv) -> None:
        fields = " ".join(f"{k}={v}" for k, v in kv.items())
        self._log(f"NUDGER {now_iso(self.clock())} mode={self.mode} persona={persona} "
                  f"action={action}" + (f" {fields}" if fields else ""))

    # -- one poll -------------------------------------------------------------
    def tick(self) -> None:
        for persona in self.personas:
            self._tick_persona(persona)
        self._prune()
        self.files.save_state(self.state)

    def _tick_persona(self, persona: str) -> None:
        records = self.state["records"]
        now = self.clock()
        text = self.files.read(self.files.wake_dir / persona)
        lines = complete_lines(text or "")
        baseline = self.state["baseline"].setdefault(persona, len(lines))
        offset = effective_offset(
            self.files.read(self.files.state_dir / f"{persona}.offset"), len(lines), baseline)

        # 1. outstanding nudges: ack or (once) escalate
        outstanding = None
        for key, rec in records.items():
            if rec.get("persona") != persona or rec.get("status") != "nudged":
                continue
            st = ack_status(rec["at"], rec["line_no"], offset, now, self.ack_window)
            if st == "acked":
                rec["status"] = "acked"
                rec["acked_at"] = now
                self.log(persona, "acked", channel=rec["channel"], seq=rec["seq"])
            elif st == "escalate":
                self._escalate(persona, rec, "no-ack")
            else:
                outstanding = key

        # 2. new wakes
        new = [w for w in unconsumed_wakes(lines, offset) if w.key(persona) not in records]
        if not new:
            return
        if self.alive(self.files.state_dir / f"{persona}.waiter.pid", persona):
            return      # D3: a live waiter delivers; leave them unrecorded
        if outstanding is not None:
            for w in new:   # the pending nudge already tells the seat to look
                records[w.key(persona)] = self._rec(persona, w, "covered", now, by=outstanding)
            return

        valid: list[Wake] = []
        for w in new:
            try:
                validate_channel(w.channel)
                validate_seq(w.seq)
                valid.append(w)
            except ValueError as e:
                records[w.key(persona)] = self._rec(persona, w, "refused", now, reason=str(e))
                self.log(persona, "refused-wake", line=w.line_no, reason="bad-channel-or-seq")
        if not valid:
            return
        head, rest = valid[0], valid[1:]
        rec = self._rec(persona, head, "pending", now)
        records[head.key(persona)] = rec
        for w in rest:
            records[w.key(persona)] = self._rec(persona, w, "covered", now, by=head.key(persona))
        self._attempt(persona, rec)

    @staticmethod
    def _rec(persona: str, w: Wake, status: str, now: float, **extra) -> dict:
        return {"persona": persona, "channel": w.channel, "seq": w.seq,
                "line_no": w.line_no, "status": status, "at": now, **extra}

    # -- D4/D5/D7: one delivery attempt -------------------------------------
    def _attempt(self, persona: str, rec: dict) -> None:
        text = build_nudge_text(rec["channel"], rec["seq"])
        target = tmux_target(persona)
        if not is_allowed_target(target, self.personas):
            rec["status"] = "refused"
            self.log(persona, "refused-target", target=target)
            return
        cmd = self.tmux.current_command(target)
        if cmd is None:
            self._escalate(persona, rec, "pane-missing")
            return
        cls = classify_screen(self.tmux.capture(target), cmd)
        if cls != IDLE:
            self._escalate(persona, rec, f"not-idle:{cls}")
            return
        if not self.enforce:
            rec["status"] = "nudged"
            self.log(persona, "would-nudge", target=target, text=json.dumps(text))
            return
        sent = (self.tmux.send_keys(target, ["-l", text])
                and self.tmux.send_keys(target, ["Enter"]))
        rec["status"] = "nudged"
        rec["at"] = self.clock()
        if not sent:
            self._escalate(persona, rec, "send-failed")
            return
        self.log(persona, "nudged", target=target, text=json.dumps(text))
        self.sleep(self.verify_delay)
        if nudge_undelivered(self.tmux.capture(target)):
            self._escalate(persona, rec, "undelivered")

    # -- D8: escalate exactly once ------------------------------------------
    def _escalate(self, persona: str, rec: dict, reason: str) -> None:
        if rec.get("status") == "escalated":
            return
        now = self.clock()
        notify = escalation_target(persona)
        rec["status"] = "escalated"
        rec["reason"] = reason
        rec["escalated_at"] = now
        if not self.enforce:
            self.log(persona, "would-escalate", notify=notify, reason=reason,
                     channel=rec["channel"], seq=rec["seq"])
            return
        self.files.append(self.files.escalation_log, escalation_log_entry(
            persona, rec["channel"], rec["seq"], reason, notify, now))
        self.files.append(self.files.wake_dir / notify, escalation_wake_line(
            persona, rec["channel"], rec["seq"], reason, now))
        self.log(persona, "escalated", notify=notify, reason=reason,
                 channel=rec["channel"], seq=rec["seq"])

    def _prune(self) -> None:
        """Drop old terminal records, but only once their line is consumed —
        so pruning can never cause a re-nudge."""
        now = self.clock()
        records = self.state["records"]
        for key in list(records):
            rec = records[key]
            if rec["status"] in ("nudged", "pending") or now - rec["at"] < PRUNE_AFTER_SEC:
                continue
            p = rec["persona"]
            text = self.files.read(self.files.wake_dir / p)
            n = len(complete_lines(text or ""))
            off = effective_offset(self.files.read(self.files.state_dir / f"{p}.offset"),
                                   n, self.state["baseline"].get(p))
            if off >= rec["line_no"]:
                del records[key]


# ── CLI ───────────────────────────────────────────────────────────────────

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    env = os.environ
    ap = argparse.ArgumentParser(description="federation wake nudger (inter#75)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="enforce", action="store_false",
                      help="log intended actions only (DEFAULT)")
    mode.add_argument("--enforce", dest="enforce", action="store_true",
                      help="really send-keys and write escalations (beekeeper go only)")
    ap.set_defaults(enforce=False)
    ap.add_argument("--watch-dir", type=Path,
                    default=Path(env.get("FED_WATCH_DIR", str(DEFAULT_WATCH_DIR))))
    ap.add_argument("--personas-conf", type=Path,
                    default=Path(env.get("FED_PERSONAS_CONF", str(DEFAULT_PERSONAS_CONF))))
    ap.add_argument("--ack-min", type=float,
                    default=float(env.get("NUDGER_ACK_MIN", DEFAULT_ACK_MIN)))
    ap.add_argument("--poll", type=float,
                    default=float(env.get("NUDGER_POLL", DEFAULT_POLL_SEC)))
    ap.add_argument("--verify-delay", type=float,
                    default=float(env.get("NUDGER_VERIFY_DELAY", DEFAULT_VERIFY_DELAY_SEC)))
    ap.add_argument("--once", action="store_true", help="run one tick and exit")
    return ap.parse_args(argv)


def build_nudger(args: argparse.Namespace, tmux=None, **kw) -> Nudger:
    personas = load_personas(args.personas_conf)
    files = Files(args.watch_dir.expanduser(), args.enforce)
    return Nudger(personas, files, tmux if tmux is not None else Tmux(personas),
                  enforce=args.enforce, ack_min=args.ack_min,
                  verify_delay=args.verify_delay, **kw)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    n = build_nudger(args)
    print(f"NUDGER start mode={n.mode} watch_dir={n.files.root} "
          f"personas={len(n.personas)} ack_min={args.ack_min} poll={args.poll}s", flush=True)
    while True:
        n.tick()
        if args.once:
            return 0
        time.sleep(args.poll)


if __name__ == "__main__":
    sys.exit(main())
