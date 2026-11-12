# Addendum — studybuddy as a default launched seat (launched last)

> Status: RECORDED 2026-10-31 by qbp-architecture (inter#266).
> Amends: `architecture-records/2026-10-08-studybuddy-seatless-agent-RECORD.md`, for **launch only**.
> Source: beekeeper ruling, first-hand in deming's session, 2026-10-31 (relayed at live-test seq 4135,
> recorded on inter#266). The drain relationship is from herschel and deming on inter#266.

## What changes
- **studybuddy becomes a default startup seat with its own pane** in the federation's tmux session.
  Until now it was started by hand in its own `study` session.
- **It is launched last.** The roster row carries the flags `deferred,no-onboard`:
  - `launch-federation.sh` (the main launch) leaves it out, and `plan` shows it as `DEFERRED`;
  - after deming's post-launch health sweep is green, `launch-federation.sh start-deferred` starts it
    fresh (per inter#262), with its seat-map model, into the running session;
  - "last" means after **every** other seat, herschel included. The outbox's drainer is up before its
    producer, so nothing written at startup is missed.
- **Never a second instance.** `start-deferred` refuses if `claude` is already running in
  `~/Documents/studybuddy` in **any** tmux session (for example a hand-started `study` session).

## What does not change (the seatless properties still hold)
- **Off-bus.** It does not register on sessionbridge or post to channels. `no-onboard` means the
  launcher never sends it the bus boot prompt; its own `CLAUDE.md` drives it.
- **No authority, no home-repo warp.** It reads the Gestalt and writes its own outbox. herschel keeps
  draining `studybuddy/outbox` into Gestalt.
- A move on-bus would need a separate beekeeper ruling. Until then the outbox is the channel.

## Open, the beekeeper's call
- **Model.** inter#266 proposes **Sonnet 5** (napkin-scale study notes). The 2026-10-08 record describes
  studybuddy as the beekeeper's **Opus 5.5** thinking partner. The beekeeper confirms one. deming then
  adds the `seat-model-map.tsv` row in Nidavellir. Until that row exists, `plan` reports its model as
  MISSING and the pane starts on the account default.
