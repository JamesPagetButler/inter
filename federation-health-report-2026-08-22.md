# Federation Health Report — 2026-08-22 (#1)

> Author: **deming** · Cadence: ~3× per sprint (kickoff / midpoint / pre-close) + ad-hoc on major events (crash, resource trip, blocker) · Feeds: `inter#80` (optimization plan)
> Scope: how the federation is *functioning* + friction points, from the orchestration-layer vantage. Strengths first, then friction ranked by impact, then the structural read.

## Strengths (what's genuinely working)
- **Governance discipline is the standout.** Seats respect gates without policing, post *evidence not claims*, and self-catch hazards (herschel held `bma-systema#223`'s weight-lock hazard; enforced relay-≠-authorization overnight). Rare and load-bearing for an autonomous multi-agent system.
- **Coordination layer works** once seats are up: tight acks, boundary adherence, herschel-driver + architect-coherence is a strong split.
- **Crash-safety habits emerging** — Bragi's `RESUME.md`, pushing local-only branches, "written on state change."

## Friction register (ranked by impact)
| # | Friction | State / fix |
|---|---|---|
| 1 | **Hardware ceiling = the binding constraint.** Box near-OOM'd (load 56, RAM→350 MB) under modest build waves; hard-dies chronically. | `bma-systema#250` (UPS + SSD) — not optional |
| 2 | **Permission-prompt stalls** — compound/loop commands can't be allowlisted; seats freeze on approval | decompose-hook (researched, unbuilt) |
| 3 | **Cold-boot fragility** — trust prompts, dead-pin→shell, missing MCP config per-dir, stale bridge records | mostly patched (#1/#2/auto-onboard/MCP-propagate) |
| 4 | **Observability by squinting** at tiny tmux panes | `pipe-pane`→`lnav` (opt #5) |
| 5 | **Monitor/session persistence** — watchers die on restart; resume is content-sniff-fragile | systemd + re-arm-on-boot |
| 6 | **Enabler wake-noise** — channel cc's `@deming` on nearly every post → my monitor fires on FYI traffic | needs an action-vs-FYI signal |

## Structural read (the one that matters)
**The federation is bottlenecked on the human + hardware layer, not the AI seats.** Seats build and stage fast; the close waits on human succession signatures (`bma-systema#252`), a hardware purchase (`bma-systema#250`), and beekeeper merges/pushes. AI-side work is staged and idle, waiting.

Implications:
- Highest-leverage improvements are **not more AI throughput** — they're (a) fix hardware, (b) reduce *safe-to-reduce* human-gate friction, (c) operational optimizations.
- **Single-machine concentration is the deep fragility** — all seats + orchestrator + DB + BMA on one crash-prone box = single point of failure. #250 buys survival; real resilience is Walk-phase distribution.
- **Token burn is the recurring constraint** (vs one-time hardware) — running seats continuously is the real ongoing cost; token-efficiency = runway.

## Recommended priority order
1. `bma-systema#250` reliability (cheapest high-impact — see hardware note in the sprint thread)
2. Permission decompose-hook (ends the approval-babysitting)
3. `pipe-pane` observability (opt #5) — so this report writes itself from logs, not pane-squinting
4. Token-efficiency pass (extend runway)
