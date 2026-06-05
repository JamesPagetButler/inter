---
name: verification
type: skill
primary-user: notary-implementor (verification function)
applies-to: any claim about the state of a live system
refined: 2026-06-04 (skill-before-blind-use pilot, inter#60)
---

# Skill: Verification

> How to verify a claim is true against the live system — independently, by evidence,
> not by trusting the claimant's summary. Notary's core skill.

## When to reach for it
Any time a status, result, or "done" claim gates a decision: a merge gate, a roster of
record, a "tests pass," a "session is live," a "X is superseded by Y." If acting on the
claim being wrong would cost something, verify first.

## Method
1. **State the claim precisely.** Reduce it to a checkable proposition ("session b332d4b7
   is qbp-architecture's live transcript"), not a vibe.
2. **Find the authoritative source**, not the claimant's report. The filesystem, the live
   API, the actual CI run — not the PR body's "CI green" or the roster's own tag.
3. **Re-derive independently.** Check the source directly. Do not let the claim tell you
   where to look in a way that only confirms it.
4. **Enumerate what could be wrong** (adversarial): the happy path, the stale pick, the
   race, the off-by-one, the wrong-handle, the duplicate. Test the failure modes, not just
   the success marker. Silence is not success.
5. **Verdict + evidence.** Every verdict cites the evidence that produced it.

## Verdict vocabulary
- **VERIFIED** — re-derived from the authoritative source; evidence attached.
- **VERIFIED-WITH-CAVEAT** — true, but with a bounded qualification worth surfacing.
- **REFUTED** — the claim is false; evidence of the discrepancy attached.
- **UNVERIFIABLE** — the authoritative source isn't reachable; say so plainly, don't guess.

## Existence ≠ correctness ≠ liveness (added 2026-06-04, from the roster V&V)
Three different claims hide inside one "verified," and a verdict must say which it checked:
- **Exists** — the artifact is there (a file, a row, an id).
- **Correct** — it binds to the right thing (this id is *this* persona's; this CI run is *green*).
- **Live / fresh** — it is current *now* (the session is active, not 3h idle; the data isn't stale).
Always report the freshness signal (age / last-write / last-active) alongside a correctness
verdict, and never let "self-verified" or "done" conflate identity-correct with live-now.

## Proven ≠ wired (added 2026-06-04, from the qbp-cu/wyrd/CTH/edda proof-coverage V&Vs)
A proof being green does NOT mean the *shipped artifact* is gated by it. Three artifacts hide
under one "X is handled": the **proof** (may be clean), a **correct reference impl** (may
exist), and the **wired path that actually runs/ships** (may be neither). The FANO octonion
op was kernel-proven in Foundations AND correct in `pkg/fano` — yet the ISA path that ships
to silicon imported neither and returned garbage, untested. Always check the *wired* path,
not the proof's existence: does a CI gate (drift/round-trip test) actually tie the shipped
artifact to the proof? If not, "proven" is decoration, and correct-by-coincidence ≠
correct-by-construction.

The gap has four sharper sub-rungs, each a real federation finding:
- **cited ≠ resolvable ≠ on-point** (wyrd): a `Soundness:`/theorem citation string can be a
  phantom (wrong module qualifier), unresolvable, or cite a theorem whose *statement is
  narrower/different* than the prose claim beside it — while the underlying proof is green.
  Name-resolution is mechanizable; statement-vs-claim match is irreducibly human.
- **decided ≠ enforced** (CTH): a ruling posted (even co-signed) is not a gate. The #96
  axiom-closure gate was *ruled in a comment* yet absent from code — `Validate()` accepted a
  self-declared "verified" anchor with no kernel check. Re-derive the *enforcement*, not the
  decision. (And read the issue's AC checkboxes vs its comments — they can disagree.)
- **source-pinned ≠ semantics-pinned** (edda): a SHA-256 paired-source drift gate is better
  than nothing but pins file *bytes*, not *behavior* — a maintainer who edits both sides and
  re-blesses hides a semantic divergence. Flag byte-drift gates as weaker than they look.
- **proof-of-a-model ≠ proof-of-the-shipped-code**: a theorem about a hand-built Lean *model*
  of the code (not extracted from it) constrains the model, not the running artifact.

## Anti-patterns (the rubber-stamp failures)
- Trusting the claimant's own summary ("they said it's green").
- Confirming only the happy path while a crashloop/stale/duplicate hides in the tail.
- Treating a past-state memory or a stale tracker as current truth (read-back-verify).
- Reporting VERIFIED when you only checked existence, not correctness.

## Wisdom anchors
`verify-state-before-summarizing` · `honest negatives over optimistic greens` ·
`determinism is cheap; non-determinism is a latent bug` (see `inter/wisdoms/`).
