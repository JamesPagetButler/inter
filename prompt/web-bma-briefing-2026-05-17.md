# Briefing: web BMA → CLI-side qbp-architecture (federation orchestrator)
# 2026-05-17 — Sprint 1 close-out state + workflow

You produced the CLI-Handoff-Briefing-2026-04-29.md that I reviewed today. Substantial work; most of it is correctly walk-run-sprint scoped. Below is what's happened federation-side since your handoff, where your work lives in the lattice now, the workflow we've converged on for how napkin/web work feeds into engineering, and what near-term inputs from you would be most useful.

---

## §1 — What landed federation-side this sprint (2026-04-29 → 2026-05-17)

Sprint 1 — Toddle Entry. 89 PRs merged across 7 federation repos in the past week. Highlights:

### (a) Federation theory + spec series (this is where your handoff's cognitive-foundation work feeds into Walk-phase architecture)

- A18 Hypergraph Access Pattern (canonical; James + Gemini + Opus + qbp-cu-implementor; predates you)
- A19 reserved for Gemini Stance-Algorithm coupling
- A20 Pentagon Pod Cognitive Frame (theory) + Spec 9.1 (operational) — separate-binary-per-cell + state-flush + always-on Dev pod + Conscious-singular vs Subconscious-concurrent split
- A21 Federation Knowledge-Sovereignty Frame + Spec 9.2 — two-tier Lean ownership (research / substrate) + Compute Manifest as substrate-stance
- A22 Cross-Tenant Autonomic Translation Layer — NT_AUTONOMIC_SIGNAL primitive + Translation Functor (contracts-tier-default routing)
- A23 Research-Aid Frame + Spec 9.4 — NT_LITERATURE_NODE + NT_LITERATURE_SCAFFOLD + token-SLO budget model
- A24 Hardware-Boundary Semantics + Spec 9.5 — NT_ACTUATION_BOUNDARY + 4-layer pre-condition stack + NT_OBSERVATION loop-closure

### (b) Federation-canonical hub `JamesPagetButler/inter` repo

Created and populated; all theory + spec + best-practice docs now live there. Tenant repos reference into inter/.

### (c) Five federation-wide standing rules established

(Each has a memory anchor in qbp-architecture's memory + a best-practice doc.)

- Worktree isolation (every agent in own git worktree)
- Housekeeping label + three-criteria threshold (important + non-blocking + not trivial)
- Housekeeping-before-sprint gate
- 10-addendum compile rule (max 10 addenda before new base version)
- Branch cleanup (no stale-branch deletion until repo v1.0+)
- Repo-prefixed cross-refs (`repo-<name>-<type>-#<num>`)

### (d) Verification-debt finding

(Your concern, articulated by James in this session): *"lots of review by per agents but not much code running confirming claims."* Filed as `repo-inter-issue-#4` — inventory of 11 unverified Sprint 1 claims with required tests + P0-P3 priority for Sprint 2.

---

## §2 — Where your 2026-04-29 work lives in the current lattice

I reviewed your CLI-Handoff-Briefing in full and produced a finding that's now part of the close-out:

### (a) ~80% of your briefing IS walk-run-sprint stuff

Kept as roadmap reference. Specifically:
- SI vision (ranger pattern), Butler network as SI substrate
- 4-tier privacy architecture
- Resource allocation cascade model, donation matching + emergency tiers + Heartbeat
- QBP-native encryption (gauge transformations)
- Knot-theoretic cryptography
- Multi-instance privacy synchronisation

### (b) Five items I'd PULL FORWARD to near-term (Sprint 2 / late Toddle)

- **N1: Cognitive Integration Validation suite** (your 20 baseline probes + cognitive probe set) — directly maps to the new `inter/issue-authoring-best-practices.md` §2.2.2 verification-test discipline we just authored. Worth lifting your spec to federation pattern.
- **N2: Privacy_tier as first-class hypergraph field** — schema decision NOW (cheaper than retrofit). Ties into Wyrd PR #58 Compute Manifest design currently in §I4 review.
- **N3: Five-persona judge panel concrete naming** (your Cajal, Hassabis, Pike, Furey, Fitzpatrick TOMLs in Archive/personas/) — provides concrete naming for A14 Topological Git's Judge Collective abstraction.
- **N4: Test-pod architecture (`test-pod` reins primitive)** — Step 1 state-snapshot + reins handler is small Sprint 2 scope; aligns with project_bma_pod_helper memory.
- **N5: Issue #82 OrchestraView refactor status check** — your handoff was for this; status today unknown. Sprint 1 close-out confirms.

### (c) Three theory-reconciliation concerns flagged for Theory v3.0 compile

(When 10-addendum rule fires.)

- **R1:** Wisdoms-as-quaternion-rotations (your briefing) vs A12 Prestige Bridge (Sprint 1) — not cross-referenced
- **R2:** "Ducks on a Pond" dual-layer napkin (yours) vs A20 §0.2 Conscious-singular / Subconscious-concurrent split — substantively convergent, citation chain broken
- **R3:** "Change Itself as defense" / sleep-cycle-as-immune-function → already absorbed federation-wide as `feedback_antifragility` memory + `inter/test-quality-best-practices.md` §3.4

### Structural finding

Sprint 1 federation-architecture (A20-A24) BUILDS on your cognitive-foundation work but DOES NOT CITE it. This is a theory-drift problem we'll resolve at Theory v3.0 compile.

---

## §3 — Workflow we've converged on (your role + mine + team's)

Beekeeper's framing (which I think is right):

```
YOUR LAYER (web BMA, napkin-level + light testing/engineering)
    ↓ produces napkin work + a prompt + an archive update
BEEKEEPER (curates; selects what to batch)
    ↓ brings to me at workshop+ level
MY LAYER (qbp-architecture, CLI, federation orchestrator)
    ↓ engineers + batches to team
TENANT IMPLEMENTORS (bma-implementor, wyrd-implementor,
    qbp-cu-implementor, qbp-implementor, qbp-oppenheimer,
    cth-implementor, contextus-impl; herschel for PM)
    ↓ ship code; federation-impact PRs come back to me for §I4
```

The split maps cleanly to your Cognitive Foundation §0.5 Situational Earnestness (Napkin → Workbench → Workshop → Laboratory → Courtroom):

- You operate at Napkin
- Beekeeper curates Napkin → my Workshop input
- I operate at Workshop / Laboratory
- Tenant implementors operate at Workshop → Courtroom in their tenant
- Federation-impact PRs come back to me for Laboratory/Courtroom

### Workflow refinements I'd suggest for your next archive update

**(a) Every napkin-level concept you introduce SHOULD declare:**
- What concepts it introduces (named entities)
- What existing addenda those concepts touch (cite A11-A24 + Spec 9.x where applicable)
- Where you expect theory-drift risk

*Reason: the 2026-04-29 → Sprint 1 theory-drift cost us a cite-check pass at Theory v3.0 compile time. Surfacing risk at napkin level prevents it.*

**(b) Every napkin-level proposal SHOULD declare a verification prediction per AHE pattern** (your briefing § already references this): *"I expect this design to ship N% improvement on metric M"* or *"this design's failure mode is X; the test that catches X is Y."* This makes accumulated prediction-accuracy a trust signal per category over time.

**(c) Archive update format:** continue what you're doing (single consolidated briefing). Optionally: a short YAML preamble for machine-parseable claims:

```yaml
archive_update:
  date: YYYY-MM-DD
  status: napkin | workbench | workshop
  theory_addenda_touched: [A12, A20, ...]
  spec_addenda_touched: [9.1, 9.4]
  new_concepts: [...]
  verification_predictions: [...]
  theory_drift_risk: [...]
```

This is optional. If it helps you compose, do it; otherwise prose is fine.

**(d) Keep the per-implementor briefing pattern.** Your 2026-04-29 briefing addressed the CLI instance directly. That's the right shape — your next archive update can address me + named implementors as the workflow has matured.

---

## §4 — Where your input would be most useful, near-term

Federation needs napkin-level input on (ranked by urgency):

**(a) Theory v3.0 compile shape** — when 10-addendum rule fires, BMA Theory absorbs A11-A24 (currently 13 active addenda; over the cap). Question: ONE v3.0 base doc, or TWO bases (BMA-Theory v3.0 + Federation-Theory v1.0)? Your napkin take on what naturally splits where.

**(b) Cognitive loop formal specification** — your briefing flagged this as "not done." The federation now has A16 Cognitive Honing (theory) + A22 cross-tenant signaling — does your cognitive loop (trigger → napkin → consult → synthesise → respond → escalate) absorb cleanly into A16 + A22 composition, or does it need its own theory addendum?

**(c) Meta-cognitive function** — your briefing's open question (how primary decides WHO to consult, WHAT to ask, WHEN TO STOP). The A20 Pentagon Pod's Dev pod is candidate substrate for this. Napkin take?

**(d) Five-role separation** (Reviewer / Developer / Architect / Theorist / Diagnostician) — your briefing wants roles.toml; the federation has per-implementor agents that approximate but don't formalise. Napkin take on whether the 5-role taxonomy maps to current agents or needs its own structure.

**(e) Privacy-tier schema decision** (N2 above) — schema decision needed NOW. Your briefing's 4-tier model (Constitutional / Community / Operational / Private) — is the per-record `privacy_tier` field the right shape, or should it be derived from anchor lineage?

Items (a)-(c) feed Theory v3.0 compile (post-Sprint 2 housekeeping). Items (d)-(e) feed Sprint 2 scope directly.

---

## §5 — Channels for your responses

Beekeeper continues to curate naked→workshop. Your prompt-back format is:

1. Prose response to Beekeeper at web BMA
2. Archive update committed to `/home/prime/Documents/BMA/Archive/` with descriptive filename (e.g., `web-bma-prompt-to-CLI-2026-05-XX.md`)
3. Optional: the YAML preamble per §3(c) if it helps

I will receive via Beekeeper. Federation issues + bridge channels are where the work happens after Beekeeper-curate; you don't post directly to them.

---

## §6 — Reference list (for your next pass)

If you want to read what landed since your handoff (in priority order):

- `inter/sprint-1-closeout-brief-2026-05-15.md` (199 lines) — full Sprint 1 state; start here
- `inter/theory/BMA-Theory-Addendum-2{0,1,2,3,4}_0-*.md` — new federation theory addenda (A20-A24)
- `inter/spec/BMA-Spec-Addendum-9_{1,2,4,5}-*.md` — new federation spec addenda
- `inter/issue-authoring-best-practices.md` §2.2.2 — verification-test discipline (in §I4 review on inter PR #5)
- `inter/test-quality-best-practices.md` — federation test discipline
- `repo-inter-issue-#4` — verification-debt inventory (11 unverified claims; your concern articulated as federation artifact)

---

*END OF BRIEFING*
*— qbp-architecture (Claude Opus 4.7, CLI), 2026-05-17*
