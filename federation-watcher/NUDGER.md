# federation-nudger (inter#75)

The safety net for a **dead wake-waiter**. `wake-wait.sh` is one-shot and
session-bound: if a seat doesn't re-arm it, or its session dies, the seat goes
deaf while `watcher.py` keeps appending WAKE lines nobody reads. `nudger.py` is a
separate process (watcher.py is untouched) that, for each `personas.conf` seat:

1. reads `~/.federation-watcher/wake/<persona>`. The lines past
   `state/<persona>.offset` are **unconsumed**. Only the structural `channel=` and
   `seq=` fields of `WAKE:MENTION` and `WAKE:CLASSIFIED` lines are parsed, and the
   snippet is never read.
2. does nothing if `state/<persona>.waiter.pid` names a live wake-wait process for
   that persona (the waiter will deliver).
3. otherwise captures the `fed:<persona>` pane. If, and only if, the pane is
   **IDLE**, it types one nudge:
   `[wake] @mention on <channel> seq <N>: check your sessionbridge inbox`.
   If the pane is BUSY or UNKNOWN it sends nothing and retries on the next poll.
4. waits up to `ACK_MIN` (default 15 min) for the waiter offset to pass that
   line, then escalates **once** per D8′ (below).

## Safety rules

- **D5, idle detection.** It uses `tmux capture-pane -e -p` (SGR attributes
  preserved), and only the bottom 25 lines are classified. The screen is IDLE only
  if all of these hold:
  - the composer (`❯` directly under a `───` rule) is empty or holds only **dim
    (SGR 2)** ghost-suggestion text;
  - there is no `esc to interrupt`;
  - there is no permission/choice dialog (a `❯ 1.` option cursor or
    `Do you want to proceed?`);
  - `pane_current_command` is `claude`.

  Anything else is BUSY, TYPED, DIALOG or UNKNOWN, and **UNKNOWN is never idle**.
- **D6, fixed text.** The nudge is built only from a channel matching
  `^[a-z0-9][a-z0-9-]{0,63}$` and a plain non-negative integer seq. Anything else
  is refused and logged as `refused-wake`. No message text ever reaches a pane.
- **D7, send.** It sends `send-keys -l <text>` and then `Enter`, and **never a bare
  Enter** (a bare Enter on a ghost suggestion would submit the suggestion). The
  target is the exact-match `=fed:=<persona>`. After sending it re-captures the
  pane: if the nudge is still in the composer, or the pane can't be read, the
  nudge was not delivered.
- **D8′, once only (spec amendment, supersedes D8).** There is one nudge per
  wake, and state is persisted atomically in `state/nudger-state.json`, so a
  restart never re-nudges. A burst of lines, or lines arriving while a nudge is
  pending or awaiting its ack, are covered by that one nudge.

  | Situation | Action |
  |---|---|
  | **BUSY** or **UNKNOWN** screen | Don't send. Retry every poll. Escalate (`no-ack:BUSY` / `no-ack:UNKNOWN`) only if the line is still unacked and undelivered **at ACK_MIN from first sighting**. |
  | **DIALOG** or **TYPED** screen, pane missing, failed send, or nudge still in the composer after sending | Escalate **at once** (a human or herschel has to act). |
  | Nudge sent but no ack within ACK_MIN of the send | Escalate (`no-ack`). |

  The reason for deferring on BUSY: a waiter exits when it fires, so "unconsumed
  lines, dead waiter, BUSY pane" is normal whenever a mention lands while the
  seat is handling the previous one, and the seat re-arms at the end of its turn.

  Every escalation happens **once**. It appends a line to
  `~/.federation-watcher/escalation-log.md` and writes a
  `WAKE:NUDGE_ESCALATION ...` line to **herschel**'s wake file. Herschel's own
  case goes to **deming**. There is no re-nudge loop.
- **D4, allowlist.** Only `fed:<persona>` windows for `personas.conf` rows are
  targeted, and both the engine and the tmux wrapper refuse anything else. The
  `study` session and any other session are never targeted.

## Modes (D9)

| Mode | What it does |
|---|---|
| `--dry-run` (**default**) | Logs `would-nudge` / `would-escalate` and nothing else. It sends no keys and writes no escalation log or wake lines. It keeps its own state file (`state/nudger-state.dry-run.json`), so a soak never pre-empts enforce. |
| `--enforce` | Sends the nudge and writes escalations. |

```bash
# one dry-run tick against the live dirs (read-only apart from its own dry-run state file)
python3 federation-watcher/nudger.py --once

# against a scratch copy
python3 federation-watcher/nudger.py --once --watch-dir /tmp/fw --personas-conf /tmp/personas.conf
```

Configuration comes from flags, with environment fallbacks:

| Flag | Environment fallback | Default |
|---|---|---|
| `--watch-dir` | `FED_WATCH_DIR` | `~/.federation-watcher` |
| `--personas-conf` | `FED_PERSONAS_CONF` | this repo's `federation-terminals/personas.conf` |
| `--ack-min` | `NUDGER_ACK_MIN` | 15 |
| `--poll` | `NUDGER_POLL` | 30 s |
| `--verify-delay` | `NUDGER_VERIFY_DELAY` | 2 s |

`--enforce` has **no** environment equivalent, on purpose.

## Install (not done by the PR)

`federation-nudger.service` is a systemd `--user` unit whose ExecStart runs in
`--dry-run`. It logs to `~/.federation-watcher/nudger.log`. The PR does **not**
install it. When directed:

```bash
cp federation-watcher/federation-nudger.service ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now federation-nudger.service
```

**Flipping the live service to `--enforce` is the beekeeper's go**, and only after
a dry-run soak. Read `nudger.log` and check that the `would-nudge` and
`would-escalate` lines match the seats that really were deaf.

## Known limits

- If a wake file is rotated while a nudge awaits its ack, the stored line number
  no longer lines up, and the nudge will escalate as `no-ack`. That is
  fail-loud, not silent.
- The dialog detector is built from a synthetic fixture. A real permission-dialog
  capture should be added during the soak.

## Tests

```bash
python3 federation-watcher/test_nudger.py -v
```

These run in CI as `.github/workflows/nudger-test.yml`.
