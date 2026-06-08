---
name: knowledge-maturation
scope: federation-wide (the engine that grows wisdoms & skills)
type: meta-wisdom
maintained-by: qbp-architecture; verified-by: notary-implementor
refined: 2026-06-04 (beekeeper: "how does a learning develop from experience into a skill then a wisdom")
---

# The Antifragility Engine — Experience → Skill → Wisdom

> Antifragility is not surviving stress; it is **converting each stress into durable,
> increasingly-general capability.** The conversion runs on this ladder. Failures and
> surprises are the feedstock — the more the system is stressed, the faster it climbs.

## The three rungs (axis = breadth of applicability)
1. **Experience** — a raw finding, usually from a failure, near-miss, or surprise. Single
   instance, not yet reusable. *Captured* in the process-breakdown ledger or as a note.
   *e.g.* "log-session.sh grabbed the wrong transcript in a shared cwd."
2. **Skill** — an experience crystallized into repeatable know-how for **one specific tool**.
   Lives on that tool's skill doc (`inter/skills/<tool>.md`). *e.g.* "check a transcript's
   mtime age before trusting it as live — a live session is seconds old."
3. **Wisdom** — the *same shape* of lesson seen across **≥2 tools/contexts**, stripped of
   tool-specifics into a broadly-applicable principle (`inter/wisdoms/`). *e.g.* the mtime
   race + the roster-write race + the worktree-share incident → "one writer per resource"
   and "determinism is cheap; non-determinism is a latent bug."

## Promotion triggers (the engine's rules)
- **Experience → Skill:** the lesson is *actionable* and *tool-bound*. Crystallize it onto
  the tool's skill doc. (And per skill-before-blind-use, the skill must exist before reuse.)
- **Skill → Wisdom:** the lesson *recurs across ≥2 tools or contexts*. Generalize it. Breadth
  is the promotion axis — a wisdom is a skill-pattern that went cross-tool. (Same axis as the
  federation-wide vs persona-local scope rule.)
- **Verification gate:** notary V&V before a promotion lands — no false wisdom, no skill that
  doesn't hold. A promotion is a claim; claims get verified.

## It runs both ways
A wisdom that stops holding under new evidence is **revised or demoted**. Antifragile means
revisable, not dogmatic — the ladder is bidirectional, governed by evidence.

## Already in embryo
`inter/process-breakdowns.md` → "rules surfaced" → best-practices *is* experience→rule. This
engine formalizes and extends it: it adds the **skill** rung (tool-local know-how), the
**cross-tool generalization** trigger (skill→wisdom), and the **notary verification** gate.
Worked example, one cycle: notary's roster V&V surfaced "existence ≠ correctness ≠ liveness"
(experience) → folded into `inter/skills/verification.md` (skill) → candidate wisdom once a
second tool shows the same conflation.
