# tmux — Driving & Session-Management Best Practices (Federation)

> Scope: how to launch, drive, and read the federation's long-running interactive
> agent sessions in tmux — programmatically (`send-keys`/`capture-pane`) and by
> hand. Grounded in authoritative tmux practice + hard-won lessons from operating
> the `fed` session. Companion to `launch-federation.sh` and the
> `project-federation-launch-gotchas` memory.
>
> **Verified against tmux 3.2a** (the Crawl box). tmux flags vary across versions
> (e.g. `capture-pane -N` changed meaning; `paste-buffer` trailing-newline behavior
> is version-sensitive) — when in doubt, check the **local** `man tmux`, don't trust
> a web snippet. Closes: JamesPagetButler/inter#77.

---

## 0. TL;DR — the commands you actually use

```bash
tmux has-session -t fed 2>/dev/null && echo up || echo down     # existence gate

# true state of every pane (id, cwd, running command) — NOT just "is claude up"
for p in $(tmux list-panes -t fed -F '#{pane_id}'); do
  printf '%s %-24s %s\n' "$p" "$(tmux display -p -t $p '#{pane_current_path}')" \
                              "$(tmux display -p -t $p '#{pane_current_command}')"
done

tmux capture-pane -p -t %10                 # read current screen
tmux capture-pane -p -t %10 -J -S -80       # + join wrapped lines + 80 lines history

# read a TUI menu too tall for a tiled pane: zoom, wait for redraw, capture, un-zoom
tmux resize-pane -Z -t %10; sleep 0.5; tmux capture-pane -p -t %10; tmux resize-pane -Z -t %10

tmux send-keys -t %10 'make build' Enter    # short command: text + Enter as a SEPARATE key
tmux send-keys -t %10 Down Enter            # navigate a menu
tmux send-keys -t %10 Escape                # cancel/dismiss

tmux attach -t fed          # interactive only (needs a real TTY); detach with Ctrl-b d
```

**The one rule that prevents most mistakes:** `pane_current_command == claude` does **not**
mean the session is ready for input — it may be at a trust/permission prompt or a menu.
**Always `capture-pane` and confirm the on-screen state before you `send-keys`.**

---

## 1. Session / window / pane model & targeting

- **Model:** a tmux **server** holds **sessions** → **windows** → **panes**. The server
  outlives the terminal that started it.
- **Every object has a stable id** — session `$N`, window `@N`, pane `%N` — assigned once
  and **permanent for the object's life**, even across renames/moves/layout changes.
  *Indices* (`fed:0.1`) renumber when panes are added/killed. **Always target by id.** [tao]
- **Create detached** (the scriptable default; `-d` = don't attach). Capture the id at
  birth with `-P -F`: [man7][obra]
  ```bash
  pane0=$(tmux new-session  -d -s fed -n federation -c ~/Documents/inter -P -F '#{pane_id}')
  pane1=$(tmux new-window   -d -t fed -n wyrd -c ~/Documents/Wyrd        -P -F '#{pane_id}')
  pane2=$(tmux split-window -d -t fed -h -c ~/Documents/BMA              -P -F '#{pane_id}')
  #                                        -h left/right · -v top/bottom · -l 40% size
  ```
- **Targeting (`-t`)** accepts `session:window.pane`, an id (`%10`, `@2`, `$1`), or special
  tokens `{last} {next} {top} {bottom} {left} {right}`. Prefer ids. [man7][tao]
- **Query one object** (fresh server round-trip each call — ideal for state that moves):
  ```bash
  tmux display-message -p -t %10 '#{pane_current_command}'
  tmux list-panes -t fed -F '#{pane_id} #{pane_index} #{pane_title} #{pane_current_command} #{pane_dead}'
  ```
  Useful fields: `#{pane_id} #{pane_current_path} #{pane_current_command} #{pane_pid}
  #{pane_title} #{pane_width} #{pane_height} #{pane_dead} #{alternate_on}
  #{window_zoomed_flag}`. `#{alternate_on}` is a coarse "a full-screen TUI is drawing"
  signal (1 = alt-screen active). [tao][man7]
- **Titles** (persona labels in the pane border):
  ```bash
  tmux select-pane -t %10 -T edda-implementor
  tmux set -t fed pane-border-status top; tmux set -t fed pane-border-format ' #T '
  ```

## 2. Layouts & the tiny-pane render problem

- **Apply a layout:** `tmux select-layout -t fed tiled` (also `even-horizontal`,
  `even-vertical`, `main-vertical`, `main-horizontal`). [man7]
- **THE fundamental problem:** a TUI only draws **what fits in its viewport**. A `tiled`
  layout of ~11 panes makes each pane tiny (≈40×15), so a prompt/menu taller than the pane
  is **partially rendered** — and the off-screen part is **not in the capture buffer**,
  because the app never drew it. `capture-pane -S -N` will *not* recover it; only a bigger
  pane will. [libtmux][obra]
- **A second, sneaky cause of truncation:** a **detached** session with no attached client
  defaults to a small virtual size (~80×24), so even a "full window" TUI is clipped. Set
  the size at creation: [man7]
  ```bash
  tmux new-session -d -s fed -x 250 -y 60 ...
  ```
- **Fix at read time — zoom, wait, capture, un-zoom** (`-Z` is a *toggle*; pair the calls):
  ```bash
  tmux resize-pane -Z -t %10; sleep 0.5
  tmux capture-pane -p -t %10
  tmux resize-pane -Z -t %10
  ```
  Or resize absolutely: `tmux resize-pane -t %10 -x 200 -y 50`.
- **Windows-per-agent beats tiled panes for *driving*.** With one window per persona, each
  TUI renders at full window size, so menus/prompts are always in-buffer and capture is
  reliable. Tiled panes are for *human* at-a-glance monitoring, not for scripted capture.
  **Recommended hybrid:** drive against per-persona windows; keep an optional tiled
  "dashboard" window of read-only `pipe-pane` mirrors for the human. `launch-federation.sh`
  supports `LAYOUT=windows` for exactly this.

## 3. Sending input — `send-keys`

- **Key-names vs literal — the #1 automation footgun:** [man7][libtmux]
  - `send-keys -t %10 'ls' Enter` — args are parsed as **key names** (`Enter`, `C-c`,
    `Escape`, `Tab`, `Up`…). Normal way to type a command and run it.
  - `send-keys -t %10 -l 'literal text'` — **`-l` = literal**, every character sent as-is,
    no key-name interpretation. Use for arbitrary payloads that may contain key-like words.
- **Send `Enter` as its own key** — never embed `\n` in the text; `'cmd\n'` is unreliable:
  ```bash
  tmux send-keys -t %10 -l "$payload"; tmux send-keys -t %10 Enter
  ```
- **Multiline payloads to an Enter-submit TUI need `paste-buffer`, not `send-keys`.** Every
  embedded newline in a `send-keys` payload is delivered as a *separate Enter keypress*, so
  an Enter-submit prompt fires on the first line and mis-handles the rest. [pi2376][paste4098]
  The reliable pattern uses **bracketed paste** so the app sees one paste, not typed Enters:
  ```bash
  printf '%s' "$multiline" > /tmp/payload.txt
  tmux load-buffer -b agentbuf /tmp/payload.txt
  tmux paste-buffer -t %10 -b agentbuf -p -d     # -p bracketed paste · -d delete buffer after
  # confirm the whole payload rendered (capture-match) BEFORE the single submit:
  tmux send-keys -t %10 Enter
  ```
  (`paste-buffer` trailing-newline behavior is version-sensitive — verify on 3.2a against
  your target TUI, then standardize.) For **single-line** payloads (most reins prompts),
  `send-keys -l "$(cat file)"` + a separate `Enter` is fine — that's what the federation
  onboarding recipe (§9) uses.
- **Special keys:** `Enter`(=`C-m`) `Escape` `Tab` `BSpace` `Space` `C-c` `C-d`
  `Up`/`Down`/`Left`/`Right` `Home`/`End`/`PageUp`/`PageDown`. Menus = arrows + `Enter`:
  ```bash
  tmux send-keys -t %0 Down Enter          # pick 2nd option
  tmux send-keys -t %0 Right               # next tab in a multi-question prompt
  tmux send-keys -N 20 -t %0 Down          # repeat count: Down ×20 (paging)
  ```
- **One writer per pane.** Concurrent `send-keys` to the same pane interleave keystrokes —
  serialize input per persona.

## 4. Reading output — `capture-pane`

- **Current screen → stdout:** `tmux capture-pane -p -t %10`. [man7]
- **History range:** `-S` start / `-E` end line (0 = first visible; negatives reach into
  history; `-` = the extreme):
  ```bash
  tmux capture-pane -p -t %10 -S -500        # 500 lines back + screen
  tmux capture-pane -p -t %10 -S -           # entire history
  ```
- **`-J` — join wrapped lines + preserve trailing spaces** (verified in 3.2a). Essential
  when a long prompt wraps across the narrow pane rows:
  ```bash
  tmux capture-pane -p -J -t %10
  ```
- **`-e`** keeps ANSI colour/attributes (usually omit for clean text). **`-b name`** +
  `save-buffer -b name file` captures into a named buffer for later dump.
- **`-S` cannot recover an alt-screen TUI's internal scrollback.** History holds the
  scrolling-region (pre-TUI shell) text, not a full-screen app's off-viewport content — so
  deep `-S` won't reveal a menu that never fit. **Enlarge the pane instead** (§2). [libtmux]
- **Continuous logging (`pipe-pane`)** — durable, greppable transcript independent of the
  volatile screen; lets the driver poll files instead of hammering `capture-pane`:
  ```bash
  tmux pipe-pane -t %10 -o 'cat >> ~/logs/edda.pane.log'   # -o toggle-safe; no cmd = OFF
  ```
  Raw pipe keeps ANSI; strip downstream: `sed 's/\x1b\[[0-9;]*m//g'`.

## 5. Driving interactive TUIs reliably

These apps **redraw asynchronously** — a keystroke is accepted by the PTY instantly but the
*visual result* appears only after the app's next render. `send-keys` returning 0 tells you
nothing about the UI. [obra][libtmux]

- **Poll until a marker, don't fixed-sleep.** Fixed sleeps either waste time or fire early;
  across 11 panes they compound. Busy-wait on what actually printed:
  ```bash
  wait_for() {  # $1=pane  $2=needle  $3=timeout_s
    local end=$(( $(date +%s) + ${3:-10} ))
    while (( $(date +%s) < end )); do
      tmux capture-pane -p -t "$1" | grep -qF "$2" && return 0
      sleep 0.1
    done
    return 1
  }
  wait_for %10 '❯' 15 && tmux send-keys -t %10 'go' Enter
  ```
- **Detect state before sending.** Match a known ready marker (input glyph `❯`, a numbered
  menu, a trust prompt) before typing. Scan for `error|failed|panic|Traceback` rather than
  trusting an exit status you don't have for a live TUI. [libtmux]
- **First-run prompts block silently.** A fresh agent may sit at *"trust this folder?"* while
  `pane_current_command` already reads `claude`, and a small pane hides it below the fold.
  Zoom → capture → match the prompt → send the accept key (`Enter`/`y`) → re-capture to
  confirm it cleared. Only *then* send the task input.
- **A dead `--resume <id>` drops to a shell.** If a resumed id has no transcript, the app
  prints "No conversation found" and exits to `bash` (`pane_current_command` → `bash`).
  Detect it, `send-keys <pane> 'claude' Enter`, and fix the stale id upstream.
- **No-TTY constraint.** A driver without a controlling TTY (cron/CI/systemd/`!`-prefix
  one-shot) **cannot** do interactive `read` — it hits EOF. tmux is the fix: the *server*
  owns a real PTY per pane, so the TUIs get a proper terminal even though the orchestrator
  has none. Always talk **through** `send-keys`/`capture-pane`, never to a raw pipe.
- **Idempotency & races.** Guard creation with `has-session`; store `%id` at birth; one
  writer per pane; confirm a payload is fully on screen (capture-match) before the final
  `Enter`; insert a capture-confirm between dependent keystrokes that trigger a redraw.

## 6. Persistence — detach / attach

The tmux **server** is a background process holding all sessions/PTYs; a client is just a
view. Closing the launching terminal detaches the client — **the sessions keep running**.
That's why the federation lives in tmux. [man7][tao]

```bash
tmux has-session -t fed 2>/dev/null; echo $?   # 0 exists · nonzero not (the idempotency gate)
tmux attach -t fed            # attach a human view (needs a real TTY)
tmux attach -d -t fed         # attach and detach other clients (single-viewer)
tmux switch-client -t fed     # from inside another tmux session
# detach: Ctrl-b d
tmux kill-session -t fed      # kill one session (+ its processes)
tmux kill-server              # nuke everything (careful)
```
`tmux attach` from a non-TTY tool errors *"open terminal failed: not a terminal"* — attaching
is a **human-terminal** action; have the operator run it (or use the `!` prefix in their own
session). A detached session's small default size truncates TUIs — set `-x/-y` at creation (§2).

## 7. `.tmux.conf` essentials (for scripted driving)

```tmux
set -sg escape-time 0        # CRITICAL: default 500ms swallows/merges a programmatic Escape
                             # and slows menu nav. (On a SLOW/REMOTE link use 10, not 0 — a
                             # split Alt/Meta byte stream can misfire at 0.)  [esc]
set -g  history-limit 100000 # default ~2000; raise so capture-pane -S reaches far back
set -g  base-index 1
setw -g pane-base-index 1
setw -g aggressive-resize on # size each window to the largest attached client (TUIs get full size)
set -g  pane-border-status top
set -g  pane-border-format ' #{pane_index} #T [#{pane_current_command}] '
set -g  mouse on             # human convenience; irrelevant to send-keys drivers
```
Apply live: `tmux source-file ~/.tmux.conf` (or set at runtime, e.g.
`tmux set-option -g escape-time 0`). `escape-time 0` is the single most important setting for
reliable programmatic `Escape`.

## 8. Gotchas & anti-patterns

| Anti-pattern | Reality / fix |
|---|---|
| `pane_current_command == claude` ⇒ "ready" | May be at a trust/permission prompt or menu. **Capture and check the on-screen state.** [obra] |
| Partial menu in capture ⇒ "that's all there is" | Rest is off-screen, *not in the buffer*. **`resize-pane -Z`, wait, re-capture.** [libtmux] |
| Detached session, no `-x/-y` | Defaults to ~80×24 → every TUI truncated even "full window". Set size at creation. [man7] |
| `send-keys 'text\n'` to submit | Newlines = separate Enters. Send text, then a separate `Enter`. [obra] |
| Multiline `send-keys` to an Enter-submit prompt | Fires on line 1. Use `load-buffer`+`paste-buffer -p`, confirm, then one `Enter`. [pi2376] |
| Targeting by window/pane **index** | Indices renumber after splits/kills. **Use `%N`/`@N`/`$N` ids** captured via `-P -F`. [tao] |
| `send-keys Escape` flaky | `escape-time 500` swallows it. `set -sg escape-time 0` (10 on slow links). [esc] |
| Capture immediately after send | No redraw yet. **Poll-until-marker** (or `sleep`) between send and capture. [libtmux] |
| Fixed sleeps × 11 panes | Slow and still racy. Replace with per-pane capture-polling. [obra] |
| `tmux attach` from a script/agent | No TTY → error. Attaching is a human action. |
| Interactive `read -s` via a `!` one-shot | Non-TTY → EOF, writes nothing. Use a real terminal or an editor. |
| Two agent sessions sharing one worktree/cwd | `worktree-isolation` hard-gate violation → silent data loss. One worktree per session. |

## 9. Federation playbook (the `fed` session)

**Cold-boot / recover after a crash:**
```bash
cd ~/Documents/inter/federation-terminals && ./launch-federation.sh   # build + attach
./launch-federation.sh list       # preview persona→session mapping, build nothing
./launch-federation.sh kill       # tear down
LAYOUT=windows ./launch-federation.sh   # one full-size window per persona (best for driving)
```

**Post-launch health sweep** (do this every cold-boot — the "✓ built" line hides trust
prompts and dead-pin drops-to-shell; `cmd=claude` ≠ ready):
```bash
for p in $(tmux list-panes -t fed -F '#{pane_id}'); do
  echo "== $p $(tmux display -p -t $p '#{pane_current_path}') [$(tmux display -p -t $p '#{pane_current_command}')] =="
  tmux capture-pane -p -t $p | grep -v '^[[:space:]]*$' | tail -2
done
```
For any pane at a **trust prompt** → `tmux send-keys <pane> Enter`. For any pane that
**dropped to `bash`** (dead `--resume`) → `tmux send-keys <pane> 'claude' Enter`, then fix the
stale id in `personas.conf` and prune the roster row (`~/.federation-watcher/session-roster.tsv`).

**Brief a freshly-launched persona (reins pattern)** — write the onboarding prompt to a file
(no trailing newline), paste literally, submit:
```bash
tmux send-keys -t %10 -l "$(cat /tmp/edda-onboard.txt)"; tmux send-keys -t %10 Enter
```
(For a prompt with embedded newlines, use the `load-buffer`+`paste-buffer -p` route from §3.)

**Answer a multi-question agent prompt** (tabs across the top, options below): zoom to read
every tab, then `Right` to move between tabs / `Down`+`Enter` to pick, ending on the Submit tab.

See the `project-federation-launch-gotchas` memory for the incident that motivated this guide.

---

## Sources

- **[man7]** tmux(1) man page — https://man7.org/linux/man-pages/man1/tmux.1.html (cross-checked against local `man tmux`, 3.2a)
- **[wiki-gs]** tmux wiki · Getting Started — https://github.com/tmux/tmux/wiki/Getting-Started
- **[wiki-adv]** tmux wiki · Advanced Use — https://github.com/tmux/tmux/wiki/Advanced-Use
- **[tao]** Tao of tmux · Scripting & Panes — https://tao-of-tmux.readthedocs.io/en/latest/manuscript/10-scripting.html
- **[libtmux]** libtmux · Pane interaction (send/capture patterns) — https://libtmux.git-pull.com/topics/pane_interaction.html
- **[obra]** "Using tmux for interactive commands" — https://skillshunt.io/skills/obra/using-tmux-for-interactive-commands
- **[esc]** escape-time for programmatic Escape — https://jeffkreeftmeijer.com/tmux-escape-time/ · https://github.com/tmux/tmux/issues/2652
- **[paste4098]** paste-buffer / bracketed-paste newline behavior — https://github.com/orgs/tmux/discussions/4098
- **[pi2376]** multi-line paste submits on first newline — https://github.com/earendil-works/pi/issues/2376
