# Architecture Record — studybuddy: a seatless agent

> Status: RECORDED. Proposed by deming on 2026-10-08 (beekeeper-directed) as JamesPagetButler/inter#172 and
> committed by qbp-architecture on 2026-10-17 with deming's 2026-10-08 `/name` correction folded in.
> Registry: `architecture-records/SEATLESS-AGENTS.md`.
> Category: the first **seatless agent** — a companion to the Seat Charter, documenting an agent
> that deliberately is *not* a federation seat.

## What studybuddy is
The beekeeper's private **Opus 5.5 thinking partner** for free-ranging, wide-subject exploration.
Runs locally in tmux session `study`, cwd `~/Documents/studybuddy`. Phone-accessible via Claude Code
Remote Control.

## Why it is SEATLESS (the point of this record)
A seat has a bus identity, a home-repo warp it writes, review/capacity duties, and a wake monitor.
studybuddy has **none of these on purpose**:
- **Off-bus** — never registers on sessionbridge, never posts to channels. (So it never appears in
  `list_participants`, is not on the seat-wall, has no wake monitor.)
- **No authority** — cannot act on the federation: no issues, PRs, pushes, or directing any seat. A
  sealed thinking room.
- **No home-repo warp** — it does not own/write any repo. It only **reads** the Gestalt and **writes
  its own outbox**.
Making it a seat would hand it authority + bus presence it must not have. It is the upstream head of
the thinking pipeline, not a working unit.

## Files (on disk — survive a crash)
- `~/Documents/studybuddy/CLAUDE.md` — its seed/charter (auto-loads on launch). The source of truth
  for its behavior; a relaunch reloads it verbatim.
- `~/Documents/studybuddy/outbox/` + `outbox/manifest.md` — where it writes **vault-ready Foam notes**.

## Gestalt linkage (how its thinking becomes durable)
Reads `~/Documents/Gestalt/concepts/` (Shared Read) to link correctly → writes vault-ready notes to
its outbox → **herschel ingests the outbox into the Gestalt `thinking/` lane** on cadence and before
any Sprint-Target prep (herschel seat-addendum carries this duty). herschel stays the sole writer to
the Gestalt; studybuddy never writes the vault. Keeps one-warp-one-owner + worktree-isolation intact.

## Relaunch recipe (deming, after a crash — "bring it back")
```
tmux new-session -d -s study -c ~/Documents/studybuddy
tmux send-keys -t study 'claude --model opus' Enter      # auto-loads its CLAUDE.md charter
# phone access:
tmux send-keys -t study '/remote-control' Enter           # prints the session URL; connect via
                                                          # Claude mobile app (Code tab) or the URL
tmux send-keys -t study '/name studybuddy' Enter          # sets the Remote Control display name
```
Keep-alive: the box must stay on and the `study` session running (Remote Control is not a daemon);
re-run `/remote-control` after any sleep/drop. The session URL changes per launch, so read it from `/remote-control` output, not from this record.

## Must-NOTs (preserve the seatless property on relaunch)
Do not register it on sessionbridge · do not add it to the seat roster or Seat Charter · do not give
it repo write · do not put it on the seat-wall. If any of those is wanted, that's a re-classification
decision for the beekeeper + architect, not a relaunch default.
