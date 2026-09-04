# Architecture Record — Federation Builder-Refinement Loop

> Date: 2026-08-23
> Author: qbp-architecture (Claude Opus 4.8)
> Beekeeper: James Paget Butler
> Status: RATIFIED (beekeeper-directed 2026-08-23)
> Related: `sprint-handoff-protocol.md` §Sprint-Close · `~/Documents/CLAUDE.md` §Sprint-Lifecycle Triggers · `inter/prompt/*-builder-launch-prompt.md` · `inter/wisdoms/`

---

## Context

The federation deploys **builders** — fresh, single-task instances launched from `inter/prompt/<name>-builder-launch-prompt.md` — to close scoped work in parallel. As of 2026-08-23 we had ~8 builder prompts and had **never refined any of them.** Consequence: no learning curve. Each fresh builder instance rediscovers the same gotchas, and the "non-obvious context" sections silently go stale (doc paths move, instructions expire).

Root cause is **not** laziness: refinement was designed as a *separate, deliberate maintenance act that nobody owns and that always loses to the next sprint's urgency.* Post-hoc maintenance always loses.

Key observation: **the builders already generate the refinement signal — we just never capture it.** Every builder that hits a gotcha, files a Tier-2 question, or makes a "call without architect input" is emitting a learning that evaporates into a PR thread. We are not missing the signal; we are missing the *loop that harvests it.*

## Decision

Adopt a three-part **builder-refinement loop** that reuses existing infrastructure (the `wisdoms/` corpus + sprint-close), is gated at Definition-of-Done, and is framed as the org-scale analogue of BMA's own sleep-cycle memory consolidation:

1. **Capture (per-run, DoD-gated, near-zero cost).** Every builder reads its own `inter/wisdoms/<builder>.md` at launch and, at `[COMPLETE]`, appends a short learnings delta — what was non-obvious, what the prompt got wrong/stale. *Not done until emitted.* Cost is marginal because the builder already holds the knowledge at completion; it is recording, not discovering. **"None" is a valid and common delta** — a mature prompt earns empty deltas; builders must not invent learnings to fill it.

2. **Consolidate (per sprint-close, batched, distributed ownership).** As step 3 of the Sprint-Close runbook, **each builder's owning implementor** promotes the *general* learnings into that builder's launch prompt (bump "Last updated"); cross-builder lessons route to `wisdoms/_federation.md`, which **qbp-architecture ratifies** for coherence. Distributed ownership → no architect bottleneck. Batching at an existing checkpoint → no new meeting, no new overhead.

3. **Feed-forward (automatic).** The next builder reads the updated prompt/wisdoms → the learning is in its clean launch context → the mistake does not recur. Loop closed.

## Overhead controls (a first-class design constraint)

- **Per-run cost is marginal** — a few lines at peak freshness, not a discovery task.
- **"No new learning" is a valid, common output** — the harvest does nothing when there is nothing. **Overhead scales with real learning, not run count.**
- **No new role, no new meeting** — reuses sprint-close + the wisdoms corpus + a DoD gate.
- **Existing un-refined builders are back-filled *lazily*, not as a project** — the next time each builder is deployed, its owner harvests that run + accumulated thread-learnings. Refine-on-next-touch, amortized. Do **not** spend a sprint back-filling all builders at once.

## The framing (why it is coherent with our own architecture)

This is **BMA's sleep cycle applied to the federation's process.** BMA's F01 compression functor consolidates episodic → semantic memory during sleep (Tier 0→1). The builder-learning loop is identical in shape:

| BMA cognitive layer | Federation process analogue |
|---|---|
| Episodic memory (Tier 0) | per-run builder learnings-deltas |
| Semantic memory (Tier 1) | builder launch prompts + `wisdoms/` |
| Sleep cycle | sprint-close |
| F01 compression functor | the implementor's promotion of general learnings |

The federation's learning curve and BMA's memory consolidation are the **same mechanism at two scales** — dogfooding our own cognitive architecture on our own organization.

## Consequences

- **Positive:** builders compound instead of resetting; the learning curve is continuous and automatic; the mechanism is crash-durable (the trigger lives in always-loaded CLAUDE.md, the runbook + wisdoms live on disk).
- **Cost:** a marginal per-run write and a batched per-close harvest — both bounded, both at existing checkpoints.
- **Obligation:** every `*-builder-launch-prompt.md` gains the Learnings-loop DoD stanza (applied lazily, on next touch). The Sprint-Close runbook step 3 is the enforcing harvest.
- **First embodiment:** `inter/prompt/qbp-architecture-builder-launch-prompt.md` ships with the loop built in (2026-08-23).

## Adoption

- New builders: include the Learnings-loop stanza from creation.
- Existing builders: add it on next deployment (lazy back-fill), owner harvests at that sprint's close.
- Enforcement point: Sprint-Close runbook step 3 (`sprint-handoff-protocol.md`).
