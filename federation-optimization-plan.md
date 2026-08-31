# Federation Optimization Plan

> Owner: **deming** (orchestration-layer enabler — delivery-lead + scrum-master + devops)
> Seated: 2026-08-19 · Tracking issue: inter#80 · Status: **LIVE**
> Layer split: **@herschel** drives sprint/review cadence *inside* a repo/sprint; **deming** works the *cross-session / infrastructure / federation-orchestration* layer.

---

## Why this exists

The federation carries **operational** friction that is separate from any persona's domain work — session & pane lifecycle, permissions, auth, environment reliability. It is nobody's domain job to fix, so it accumulates. Today's cold-boot after a host crash was a ~20-minute babysitting job (trust prompts, approval stalls, dead sessions, broken Gemini auth). This plan is the standing backlog for removing that friction and optimizing how the machinery runs.

## Operating model (how deming works)

A PDCA loop — **Observe → Measure → Remove → Verify**:
1. **Observe** the federation running; watch where personas stall on non-domain work.
2. **Measure** the friction (how often, how much time, what blocks).
3. **Remove** it — smallest safe change; security-sensitive changes (permissions, trust, auth) are surfaced to the beekeeper, never done silently.
4. **Verify** with before/after evidence; record it here.

Deming **enables**, it does not command: no domain decisions, no persona work. It unblocks the personas who do.

## Definition of "done" for an optimization
- The friction is measurably reduced (before/after stated).
- The change is safe and reversible (backups / excludes for anything destructive).
- It is recorded here as the federation standard, not a one-off.
- Any security-sensitive step was beekeeper-approved.

---

## Backlog (prioritized — updates from the member poll + observation)

| # | Optimization | Problem | Status | Effort |
|---|---|---|---|---|
| 1 | **Permission allowlist** | personas stall indefinitely on `gh`/`git`/shell approval prompts | ✅ shipped 2026-08-19 | S |
| 2 | **Pre-trust persona dirs** | every launch blocks at "trust this folder?" | ✅ shipped 2026-08-19 | S |
| 3 | **Host power-failure reliability** | box hard-dies at idle; kills sessions + uncommitted work; gates the 72h close | ⛔ open (bma-systema#250) | L / hardware |
| 4 | **Shared `.tmux.conf`** | `escape-time` 500ms makes programmatic control flaky; no titles, small history | ▶ ready (inter#77 / PR #79) | S |
| 5 | **Durable per-persona logging** | federation state read by squinting at 11 tiny panes | ◻ planned | M |
| 6 | **Launch resilience** | manual post-launch health-sweep; dead pins drop to shell; daemons need manual restart | ◻ planned | M |
| 7 | **Under-used tooling** | leverage left on the table (@claude action, LSP, pre-commit/gitleaks, CI) | 🔍 evaluating | M |

---

## Detail

### ✅ 1. Permission allowlist — SHIPPED
**Problem:** personas block waiting on tool approvals (cleared **6** for the architect in one ratification). Left alone, a persona stalls forever.
**Fix:** a curated, safety-conscious allowlist merged into 8 under-provisioned dirs' `.claude/settings.local.json` — generous on safe reads + authorized writes (commit, issue/pr comment/create), **excluding** `push`/`merge`/`close`/`rm`/`reset --hard` so those keep prompting (honors the confirm-first hard gates).
**Evidence:** `inter` 2→74 allows; 7 dirs 0→72; JSON valid ×8; `.bak` kept. Effect on each pane's next launch.
**Residual:** variable-expansion shell loops (`for n in …; do gh …`) still prompt — they can't be statically verified. Personas can run reads as single commands to hit the allowlist.

### ✅ 2. Pre-trust persona dirs — SHIPPED
**Problem:** 9 panes stuck at "trust this folder?" at cold-boot; `cmd=claude` ≠ ready.
**Fix:** set `projects[<dir>].hasTrustDialogAccepted = true` for all 11 persona dirs in `~/.claude.json` (atomic write + backup, to survive concurrent session writes).
**Evidence:** all 11 trusted, independently re-verified, JSON valid.
**Combined with #1:** the next cold-boot is **hands-free** — no trust prompts, no read-approval stalls.

### ⛔ 3. Host power-failure reliability (bma-systema#250)
**Problem:** the Crawl box hard-dies at idle (chronic power-domain fault) — it killed the architect *and* edda sessions during this very session, and threatens uncommitted work. It also **gates the Sprint 3 close** (the 72h continuous-op gate CV-12.1/12.2 can't reliably pass).
**Fix:** UPS + storage upgrade (#250, beekeeper/purchase) + crash-safety habits (personas auto-commit WIP; launch script auto-restarts daemons). **This is the single highest-value reliability item** — most other reliability work is moot until the box stops dying.

### ▶ 4. Shared `.tmux.conf` — READY
**Problem:** no config → `escape-time 500ms` makes programmatic `Escape` flaky; small scrollback; no pane titles. Made driving panes fragile all session.
**Fix:** ship the `.tmux.conf` documented in the tmux guide (`escape-time 0`, `history-limit 100000`, `pane-border-status`, `aggressive-resize`). See inter#77 / PR #79 §7.

### ◻ 5. Durable per-persona logging
**Problem:** I read federation state by capture-pane-sweeping 11 tiny panes — fragile, and off-screen content isn't in the buffer.
**Fix:** `pipe-pane` each persona to an append-only logfile at launch → durable, greppable transcripts + a cheap federation activity feed (could feed BMA-BADASS). "Grep the logs" replaces "sweep and squint."

### ◻ 6. Launch resilience
**Problem:** launch-federation.sh reports "✓ built" while panes are silently stuck (trust prompts, dead-pin drops-to-shell); daemons need manual restart after each crash; the health-sweep is manual.
**Fix:** post-launch auto-heal (confirm trust / restart dead panes / re-arm monitors); daemon auto-restart; crash-safe auto-commit. Builds on the auto-refresh watcher already shipped.

### 🔍 7. Under-used tooling
Evaluate and, where they pay off, adopt: the **`@claude` GitHub Action** (now live on `inter` per #78 — could offload mechanical PR work); **LSP** cross-file nav for the Go/Lean repos; **pre-commit hooks + gitleaks** (there's already `gitleaks-federation.md`); **CI** coverage gaps. Each evaluated against real friction, not adopted speculatively.

---

## Member input
Optimization poll open at **live-test seq=707** — each persona asked for their single biggest operational friction. Priorities in the table above update as responses land (most personas were re-launching from the ~2-month dormancy at poll time; responses arrive as they sign on).

## Next actions
1. Ship **#4** (`.tmux.conf`) — quick, low-risk.
2. Fold member poll responses into the priority order.
3. Elevate **#3** (#250) with the beekeeper — it gates Sprint 3 close.
4. Prototype **#5** (`pipe-pane` logging) as the observability foundation.
