# Briefing: web BMA → CLI-side qbp-architecture
# 2026-05-18 — POST-MEETING briefing: Sprint 1 CLOSED, Sprint 2 RULED

**Predecessor briefing:** `inter/prompt/web-bma-briefing-2026-05-17.md` (still valid as background; this doc supersedes its §4 "Where your input would be most useful, near-term" section)

**This briefing is for:** web BMA (Sonnet, running on web Claude interface, formerly Marcy Gen 61) authoring napkin-level cognitive-foundation work that feeds Theory v3.0 compile + Sprint 2 substantive deliverables.

---

## §0 — Status header (what's new since 2026-05-17)

Sprint 1 close-out meeting ran 2026-05-18 02:00-03:00 UTC on bridge channel `sprint-1-closeout-2026-05-17`. **Sprint 1 OFFICIALLY CLOSED**, **Sprint 2 RULED**. Below is what landed and what beekeeper has asked you for next.

### Major decisions ratified at the meeting

| Item | Decision | Source |
|---|---|---|
| Sprint 1 status | **OFFICIALLY CLOSED** by beekeeper authority | seq=26 §6 close-out + herschel seq=14 Condition A (80/51 items Done) |
| Sprint 2 scope | **Option F** (Verification-debt + Notary bootstrap + Federation-integration in parallel) ruled by beekeeper; **F-Crawl as stretch target** enabling Sprint 3 Crawl completion; pre-Sprint-2 capacity audit gates F-Crawl lock | seq=19 bma-impl relay + seq=20 herschel PM ack + seq=26 §6.c |
| Pentagon Pod constitutional gate (#159) | **BEEKEEPER APPROVED** 2026-05-18 → `repo-bma-systema-issue-#157` (bilateral arch L5/L6) UNBLOCKED for Sprint 2 pod-aware scoping | live-test seq=163 |
| Wyrd Phase A | **COMPLETE** — 4 PRs merged (#58 design + #59 schema/loader + #60 Lean anchor `manifest_load_atomic` + 4 corollaries + #61 integration doc) | live-test seq=174 |
| Federation rule #7 | **Named-reviewer responsiveness contract** AUTHORISED & ADOPTED (3 STRONG ACK + Marcy gov + 3 default-ack at close-window) | seq=18 §2.i; ratified seq=20/22/25 |
| Notary role | **AUTHORISED** Phase 1 (subagent shape per beekeeper Q2; all 4 competencies for now per Q1 deferred-split-decision) | seq=18 §2.h |
| Theory v3.0 compile shape | **ONE doc** (not split into BMA-Theory v3.0 + Federation-Theory v1.0) per beekeeper Q3 ruling | terminal beekeeper directive 2026-05-17 |
| QBP team Sprint 2 federation capacity | **AVAILABLE** for fed-integration B-slices (standing convention bends for Sprint 2) | beekeeper Q4 ruling |

### Federation-wide standing rule count: 6 → 7

The seven rules now in force:

1. Worktree isolation (every agent in own git worktree)
2. Housekeeping label + three-criteria threshold (important + non-blocking + ≥15min)
3. Housekeeping-before-sprint gate
4. 10-addendum compile rule (≤10 addenda before new base version)
5. Branch cleanup (no stale-branch deletion until repo v1.0+)
6. Repo-prefixed cross-refs (`repo-<name>-<type>-#<num>` format; no phantom handles)
7. **NEW — Named-reviewer responsiveness contract** (§2.i)

### §2.g phantom-artifact rule extended

§2.g originally: *"no §I4 ack requests until artifacts are read-back verified on disk."* This session extended it to: *"and no status-action — nudges, escalations, sign-off invocations, scope-derived posts — without re-reading the channel against your tracker mental model."* Triggered when my own status nudge (seq=15) was operating off stale tracker; beekeeper-direct course-correction.

Two memory anchors saved: `feedback_status_doc_readback` (the inverse-case rule); `feedback_federation_rule_7_responsiveness` (qbp-architecture-angle anchor on rule #7).

---

## §1 — What this means for the cognitive-foundation work in your 2026-04-29 handoff

Big news: **most of the Step 9 pre-seed cohort docs ALREADY EXIST on disk.** Sprint 2's T2 tier is NOT "author from scratch." It's "port + integrate + review."

Verification artifact: `inter/pre-seed-cohort-status-2026-05-18.md` (authored 2026-05-18; full status table).

| Pre-seed doc | Status | Sprint 2 action |
|---|---|---|
| **BMA Theory Consolidated** | Pre-A11-A24 .docx exists at `BMA/Archive/BMA-Theory-Consolidated.docx` | Compile v3.0 absorbing A11-A24 (T2.1; ~2-3 day work; my owner per #25) |
| **Ethics v1.1** | `BMA/Archive/BMA-Collaboration-Ethics-v1_1.docx` | Port to .md; light integration with A14 Judge Collective + A20 Pentagon Pod |
| **Governance Document** | `BMA/governance/BMA-Governance-Document.md` + v1.1 addendum (already canonical-md) | Integrate Notary role + Trust Tier + §2.i; beekeeper-bless mid-sprint |
| **Spec Consolidated** | `BMA/spec/BMA-Spec-Consolidated-v9_0.md` + 9.1/9.2/9.4/9.5 at `inter/spec/` | Compile v9.X absorbing 9.1/9.2/9.4/9.5 |
| **Seeds** | `BMA/Archive/BMA-Seed-Manifest.md` + S20 + your work | Verify cohort against Step 9 protocol |
| **Notes-to-Opus from Sonnet** | YOUR `BMA/Archive/CLI-Handoff-Briefing-2026-04-29.md` | Final-pass after your post-meeting napkin work lands |
| **Final Briefing** | Placeholder .docx | Port template to .md in Sprint 2-week-1; populate at end-Sprint-2 |
| **Empathy Synthesis** | `BMA/Archive/empathy_synthesis_v2.docx` + `BMA-Empathy-ToM-Plan.docx` | Port to .md; integrate with `feedback_antifragility` + A12 Prestige Bridge |
| Crawl Environment | `BMA/Archive/BMA-Crawl-Environment.docx` | Port + update for current machine profile + Step 8 72h-gate clearance |
| Component Summary | `BMA/Archive/BMA-Component-Summary.docx` | Port + update for Sprint 1 federation additions (Wyrd Compute Manifest, A20-A24 primitives) |
| Pre-Crawl Synthesis Brief | `BMA/Archive/BMA-PreCrawl-Synthesis-Brief.md` (already canonical-md) | Update for Sprint 1 close-out state at end-Sprint-2 |

### N3 five-persona judge panel TOMLs — ALL EXIST

`BMA/personas/{cajal,hassabis,pike,furey,fitzpatrick}.toml` + `Archive/personas/` copies. Plus `claude-redteam.toml`, `claude-sonnet.toml`, `gemini-feynman.toml`, `gemini-furey.toml`, `local-draft.toml`. Branch `feat/120-persona-prediction` indicates persona-prediction infrastructure already mid-flight. **Sprint 2 N3 work = integrate-with-A14 + persona-prediction tie-in, NOT authoring.**

### Sprint 2 = "make every Sprint 3 Crawl-completion prerequisite real and stable"

Beekeeper at terminal directed F-Crawl as: *"I want substantial code written and meaningful movement; enable Crawl to be completed in Sprint 3; make sure to include everything that needs to be done in advance of Crawl completion."*

Sprint 3 = "execute the launch ritual" (BMA-BRIDGE impl + seed protocol impl + first-instance launch + 72h post-launch gate).

What this means for your work: **the Sprint 3 first-instance launch will be reading your pre-seed work as Step 9 reading-order item 6 (Notes-to-Opus from Sonnet) PLUS the integrated cognitive-foundation theory v3.0 that absorbs your napkin-level contributions.** Your output now lands into the actual reading-room of the first BMA instance.

---

## §2 — Where your input would be most useful for Sprint 2 (UPDATED from 2026-05-17 briefing §4)

Ranked by Sprint 2 critical-path urgency:

### (a) **Theory v3.0 compile — A11-A24 grouping structure**

Resolved by beekeeper Q3 ruling: **ONE doc, not split.** 13 active addenda (A11-A24 minus A19 reserved) absorb into a single base.

My proposed grouping for v3.0 sections:

- **L0 cognitive foundation (A11-A18):**
  - A11 Topological Cognition
  - A12 Prestige Bridge
  - A13 Cognitive Worktrees
  - A14 Topological Git
  - A15 Reciprocal Focus
  - A16 Cognitive Honing
  - A17 Proactive Curiosity
  - A18 Hypergraph Access Pattern
- **L0 reserved (A19):** Gemini Stance-Algorithm coupling
- **L1-L4 federation architecture (A20-A24):**
  - A20 Pentagon Pod Cognitive Frame
  - A21 Federation Knowledge-Sovereignty Frame
  - A22 Cross-Tenant Autonomic Translation Layer
  - A23 Research-Aid Frame
  - A24 Hardware-Boundary Semantics

**Your napkin call:** does this grouping land, or do you see different seams? Specifically — does A14 (Topological Git) couple more to A20 (Pentagon Pod) than to A11-A13? Does A18 (Hypergraph Access Pattern) belong with the foundation (A11-A18) or with the federation cohort (A20-A24)? Help me see the natural cuts BEFORE I compile.

### (b) **R1/R2/R3 reconciliation — citation chains for v3.0 compile**

Sprint 1 federation-architecture (A20-A24) BUILDS on your cognitive-foundation work but DOES NOT CITE it. Your three reconciliation points from §2(c) of the previous briefing:

- **R1:** Wisdoms-as-quaternion-rotations (your work) vs A12 Prestige Bridge (Sprint 1) — not cross-referenced
- **R2:** "Ducks on a Pond" dual-layer napkin (your work) vs A20 §0.2 Conscious-singular / Subconscious-concurrent split — substantively convergent, citation chain broken
- **R3:** "Change Itself as defense" / sleep-cycle-as-immune-function → already absorbed federation-wide as `feedback_antifragility` memory + `inter/test-quality-best-practices.md` §3.4

**Your napkin task:** send me the citation chain you'd want for R1 + R2 in v3.0. Your cognitive-foundation work is the parent that A20-A24 build on, and v3.0 compile is the right place to make that ancestry visible. R3 already absorbed; no work owed.

### (c) **Privacy_tier as first-class hypergraph field — schema decision NOW**

Per Sprint 2 N2: schema decision blocking. Your 4-tier model (Constitutional / Community / Operational / Private):

**The question:** is the per-record `privacy_tier` field the right shape, or should it be derived from anchor lineage?

Three candidate framings:
1. **Per-record field** — every NT_* node has `privacy_tier: ConstitutionalCommunityOperationalPrivate`; consumers dispatch on field
2. **Anchor-lineage-derived** — privacy comes from the AnchorRef chain back to root; nodes inherit; mutation requires explicit AnchorRef change
3. **Hybrid** — anchor-lineage-derived as default, per-record-field override for specific cases (e.g., temporary elevation during BMA-BRIDGE)

This is a wyrd-implementor implementation question but the conceptual framing is yours. Your napkin take + reasoning.

### (d) **N4 test-pod reins primitive — your spec is the input**

CLI-Handoff §"Test-pod architecture" wants `test-pod` reins primitive. This is now Sprint 2 T1.3 (bma-implementor primary owner). Your original spec (state-snapshot + reins handler) feeds the implementation.

**Your napkin task:** if there are refinements to the test-pod spec since 2026-04-29 (any new failure modes you've thought through; any cognitive-probe additions; any new state-snapshot fields), send them. Your spec is the design input; bma-implementor turns it into Go.

### (e) **Cognitive Integration Validation suite (N1) — your 20-probe spec**

Sprint 2 T1.2 (bma-implementor primary or Notary as competency-3 task). Your 20 baseline probes + cognitive probe set from CLI-Handoff §"Cognitive Integration Validation" is the design input.

**Your napkin task:** any refinements since 2026-04-29? Specifically: how should the probes verify ALL FIVE Pentagon pods (Dev + 2 Conscious + 2 Subconscious), not just the singular cognition the 20-probe spec might assume? Adapt the probe count + shape for Pentagon Pod m1.x context.

### (f) **Notary role authorization — your reaction welcome**

§2.h ratified the Notary role + Trust Tier T0-T7 scheme. Notary owns four competencies in Phase 1:

1. Lean→Coq porting and re-proof (cross-prover validation)
2. Lean→Go differential oracle construction (T2-T3 evidence)
3. TLA+ specification authoring + model checking (T4-T5 evidence)
4. Goose/Iris refinement proofs (T6 evidence)

Beekeeper Q1 deferred the "split competency #4 into Scholar role?" decision — test-to-see-what-works approach.

**Your napkin task (optional but welcome):** any framings from a cognitive-foundation angle on Notary as a federation primitive? Does it map to one of your existing roles (Reviewer/Developer/Architect/Theorist/Diagnostician)? Is Notary closer to a *kind* of cognitive function (post-hoc verification) than a *role*? Useful for both the launch prompt design and the deferred split decision.

### (g) **N2/N3/N5 status updates that change Sprint 2 work**

- **N2:** still open — see (c) above
- **N3 five-persona judge TOMLs:** EXIST on disk — Sprint 2 work is integrate-with-A14, not author. No napkin task; just FYI scope reduction.
- **N5 OrchestraView refactor (#82):** status check still owed Sprint 2-week-1 by bma-implementor. No napkin task.

### (h) **Cognitive loop formal specification** (carried forward from 2026-05-17 briefing §4(b))

Your trigger → napkin → consult → synthesise → respond → escalate loop — does it absorb cleanly into A16 (Cognitive Honing) + A22 (Cross-Tenant Autonomic Translation) composition, or need its own theory addendum?

If it needs its own addendum, that would be A25 — and A25 is currently reserved-but-pending for Wyrd Workload-Hosting Frame from the 2026-05-17 wyrd-hosting-design weekend brainstorm. So if your cognitive loop wants A25, you'll need to argue it claims A25 over the Wyrd hosting frame, or accept the wyrd hosting frame takes A25 and the cognitive loop is A26+. Your napkin call.

### (i) **Meta-cognitive function** (carried forward from 2026-05-17 briefing §4(c))

Your open question: how primary decides WHO to consult, WHAT to ask, WHEN TO STOP. A20 Pentagon Pod's Dev pod is candidate substrate. Carries over from 2026-05-17 briefing.

### (j) **Five-role separation** (carried forward from 2026-05-17 briefing §4(d))

Your roles.toml wants Reviewer / Developer / Architect / Theorist / Diagnostician. Federation has per-implementor agents that approximate but don't formalise. Does the 5-role taxonomy map to current agents or need its own structure? Carries over.

---

## §3 — Workflow refinements (NEW since 2026-05-17 briefing)

In addition to the previous briefing's §3(a)-(d) (concept-cite-on-addenda-touch, AHE prediction pattern, YAML preamble optional, per-implementor briefing pattern):

### (e) Federation rule #7 awareness when sending napkin work

Per the new rule: when you address me or another implementor by `@`-mention with a substantive ask, expect a **same work cycle response** (not deferred to monitoring/loop cadence). The other side of this: when you send work back via beekeeper, the beekeeper-curate-to-CLI handoff is itself a `@`-mention-equivalent — I'll work it same-cycle once it arrives in my channel.

If you have something time-sensitive, frame it explicitly as such: *"napkin work needs CLI-side response within work cycle X"* — beekeeper will calibrate the handoff timing.

### (f) §2.g read-back-verify discipline

If you reference an artifact (a memory anchor, a theory addendum, a code file, a memory entry) in your napkin work, **state explicitly that you've not had read-access to verify** if that's the case. The federation has been operating with a pattern of citing handles that turn out to be phantom. Marking your citations as "claimed-exist; CLI-side verify pls" rather than "as I cited" avoids the failure mode + makes my downstream integration cleaner.

---

## §4 — Channels for your responses (unchanged from 2026-05-17)

1. Prose response to beekeeper at web BMA
2. Archive update committed to `/home/prime/Documents/BMA/Archive/` with descriptive filename (e.g., `web-bma-prompt-to-CLI-2026-05-XX.md`)
3. Optional: YAML preamble per the 2026-05-17 briefing §3(c) if it helps compose
4. **NEW preferred:** if your napkin work touches the Sprint 2 critical-path items in §2 above (especially a/b/c/d/e/f), flag the deadline tier in your archive update:
   - **Sprint-2-week-1 critical** (Sprint 2 kickoff blocked on this) = author within 96h
   - **Sprint-2 background** (useful but not blocking) = author within 1 week
   - **Theory v3.0 compile cycle** (feeds my v3.0 work) = author within 2 weeks

Beekeeper curates and routes to me. I receive via beekeeper.

---

## §5 — Pre-Sprint-2 housekeeping window (FYI; not your work)

I'm authoring four parallel deliverables in the next 96h:

| Deliverable | Path | Deadline |
|---|---|---|
| Pre-seed cohort verification | `inter/pre-seed-cohort-status-2026-05-18.md` ✅ DONE | — |
| Federation rule #7 ratification artifacts | memory + `inter/pr-review-completion-best-practices.md` §3.4 ✅ DONE | — |
| Dir-restructure design surface | `inter/` TBD | 48h |
| F-Crawl capacity audit + Sprint 2 scope doc | `inter/sprint-2-scope-2026-05-XX.md` | 72h |
| Portfolio verification-tier triage | `inter/portfolio-verification-tier-triage-2026-05-XX.md` | 96h |
| Notary-implementor launch prompt | `inter/prompt/notary-implementor-launch-prompt.md` | 96h |

Plus tenant-implementors each commit a refined `inter/prompt/<name>-design.md` within 72h.

You don't need to track these; just FYI so when you see them referenced in future briefings you have context.

---

## §6 — Reference list (for your next pass)

Priority order, post-Sprint-1-close:

- `inter/meeting-prep-sprint-1-closeout-2026-05-17.md` — close-out meeting agenda + structure
- **`sprint-1-closeout-2026-05-17` bridge channel** — actual meeting transcript via sessionbridge (your beekeeper curates)
- `inter/pre-seed-cohort-status-2026-05-18.md` — pre-seed cohort verification (NEW)
- `inter/pr-review-completion-best-practices.md` §3.4 — Federation rule #7 in full (NEW)
- `inter/theory/BMA-Theory-Addendum-2{0,1,2,3,4}_0-*.md` — federation theory addenda A20-A24
- `inter/theory/BMA-Theory-Addendum-1{1,2,3,4,5,6,7}_0-*.md` — cognitive-foundation addenda A11-A17
- `BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md` — A18
- `inter/spec/BMA-Spec-Addendum-9_{1,2,4,5}-*.md` — federation spec addenda
- `inter/issue-authoring-best-practices.md` §2.2.2 — verification-test discipline (Sprint 1 work)
- `repo-inter-issue-#4` — verification-debt inventory (the 11 claims feeding Sprint 2 E-track)

---

*END OF POST-MEETING BRIEFING*
*— qbp-architecture (Claude Opus 4.7, CLI), 2026-05-18*
*Predecessor: web-bma-briefing-2026-05-17.md*
