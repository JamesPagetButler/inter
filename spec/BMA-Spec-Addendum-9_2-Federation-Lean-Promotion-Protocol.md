# BMA Spec Addendum — Version 9.2 (recovery v0.1)

**Federation Lean Promotion Protocol: Two-Tier Ownership and the Compute-Substrate Gate**

Version 9.2 (recovery v0.1) | May 2026
Helpful Engineering — BMA Project
Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture), with bma-implementor (Claude Sonnet)
Extends: BMA Specification Consolidated v9.0 (`/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md`)
Theory companion: A21.0 Federation Knowledge-Sovereignty Frame (`/home/prime/Documents/inter/theory/BMA-Theory-Addendum-21_0-Federation-Knowledge-Sovereignty-Frame.md`)
Tracking issue: `repo-bma-systema-issue-#164`
Companion operational artifact: Compute Manifest v0.1 (to be authored in `repo-wyrd`)

> **Recovery note (2026-05-15):** The original Spec 9.2 was authored before 2026-05-14 21:47:31 but its content was wiped from disk by a concurrent agent's `git reset` operation in the shared working tree (see `repo-bma-systema-issue-#168` for the incident record). This v0.1 recovery reconstructs the load-bearing commitments from the theory companion (A21.0), the §I4 reader-list discussion on `repo-bma-systema-issue-#164` (including the #164 comment posting Spec 9.2 §12–§13 contracts-tier extension + A21 §11 amendment), and the Edit fragments preserved in the session transcript. Full prose reconstruction is owed; this version is substantively complete for the commitments it carries.

---

## 0. The Problem: Who Owns the Math, When, and Where?

A federation of AI tenants — BMA, Sharp Butler, Möbius Fusion, future entrants — needs Lean-verified invariants to enforce safety, governance, and algebraic correctness. Two failure modes must be avoided:

1. **Research velocity dies if every Lean file must be substrate-quality.** QBP reached 69 theorems on Lean v4.30.0-rc2 precisely because tenants could use `sorry` and tenant-defined `axiom` during exploration.
2. **Federation soundness dies if no Lean is substrate-quality.** Cross-tenant invariants must be provable, with no escape hatches.

The Federation Lean Promotion Protocol resolves this with **two tiers and a promotion gate**.

---

## 1. The Two Tiers

| Tier | Owner | Quality bar |
|---|---|---|
| **Research** | Tenant (BMA, Sharp Butler, Möbius Fusion, QBP, etc.) | `sorry` OK; tenant-defined `axiom` OK; exploratory iteration |
| **Substrate** | Wyrd | No `sorry`; no tenant-defined `axiom`; compiles end-to-end; **runs on the federation's blessed compute substrate per the current Compute Manifest** |

A theorem lives in the tenant's repository at the research tier. Promotion to substrate is a PR event on `repo-wyrd` with §I4 D5 reader-list acks.

---

## 2. The Promotion Gate (Four Criteria)

A theorem promotes from research to substrate when ALL four hold:

1. **Compiles end-to-end** on the current Lean toolchain pinned by `repo-wyrd`
2. **No `sorry` in the proof**, anywhere in the dependency closure
3. **No tenant-defined `axiom`** in the dependency closure (mathlib axioms permitted; tenant ad-hoc axioms forbidden)
4. **Runs on the federation's blessed compute substrate** per §3 (the Compute-Substrate Gate)

A promotion PR declares which criterion-4 mode the theorem requires.

---

## 3. The Compute-Substrate Gate (Two Modes)

| Mode | What it proves | Required for |
|---|---|---|
| **(a) Type-instantiation** | The theorem's types are substrate-provided types (Quaternion, Sedenion, etc.); Lean's elaborator verifies the theorem against those types without runtime execution. | **Universal minimum.** Every substrate-tier theorem must pass (a). |
| **(b) Extraction-and-execute** | The proof extracts to a Lean-generated executable that runs against the actual substrate runtime; the runtime's observed behavior matches the proof's claim. | **Runtime-claim theorems only.** Mode (a) alone misses implementation drift from the proof. |

A promotion PR must declare `mode = (a)` or `mode = (a) + (b)`.

---

## 4. The Compute Manifest: Abstracting Substrate Identity

Criterion 4 refers to "the federation's blessed compute substrate" rather than to QBP-CU specifically. The current substrate identity is named in a **Compute Manifest** — a Wyrd-owned operational document.

| Phase | Compute Manifest names |
|---|---|
| Crawl / Toddle | QBP-CU emulator (Go library) |
| Walk | QBP-CU M1 Gearbox (CSR-bound stateful + QW8 + QW128) |
| Run-initial | QBP-CU M2 ternary matmul + ROCm acceleration |
| Run-mature+ | Possibly QBP-CU silicon (per `workspace-phase-architecture.md` §0.13.2) |

**The gate does not change; the Manifest does.** This preserves the silicon exit ramp.

---

## 5. Substrate Immutability: Additive-Only with Deprecation-via-Migration

Substrate-tier theorems are constitutional. Once promoted, **statement is frozen.**

1. **No revision of a promoted theorem's statement.** File a new theorem; do not edit existing.
2. **Deprecation permitted** with named replacement + migration path.
3. **Deprecated theorems remain proved.** Downstream tenant proofs continue to verify.
4. **Tenants migrate at their own pace.** No forced lockstep.

This is the **mathlib pattern**.

---

## 6. Demotion / Rollback (Beekeeper-Only)

The only path to removing a substrate-tier theorem is **beekeeper approval after multi-reviewer §I4 ack**. Demotion is a constitutional event.

---

## 7. Alternatives Considered

| Alternative | Status |
|---|---|
| **Single-tier Wyrd-only** | **REJECTED.** Kills research velocity. |
| **Three-tier with intermediate federation-staging tier** | **DEFERRED.** Premature; revisit post-Walk. |
| **No formal tier model** | **REJECTED.** Federation soundness must be a property, not a convention. |

---

## 8. Multi-Tenant Applicability

| Tenant | Research-tier Lean | Promotion path |
|---|---|---|
| **BMA** | `repo-bma-systema:internal/.../proofs/` | Promote when invariant becomes cross-tenant (e.g., judge collective veto soundness) |
| **QBP** | `repo-qbp:lean/` (69 theorems) | Promote core algebraic invariants once Walk-α confirms framework value |
| **Sharp Butler** | `repo-sharp-butler:lean/` (future) | Most OKI contract invariants via §13 contracts-tier path |
| **Möbius Fusion** | `repo-mobius:lean/` (future) | Split: operational invariants via §13; physics-shaped theorems via research-tier |
| **Contextus** | `repo-contextus:lean/` (future) | Promote scout-anchoring invariants when steady state |

---

## 9. §I4 Reader-List Contract Extension

Research-tier promotion PRs require:
- **wyrd-implementor** — substrate ownership; criteria 1–3
- **qbp-cu-implementor** — Compute Manifest substrate; criterion 4
- **Tenant author** — originating tenant implementor
- **≥1 cross-tenant reader** — federation generality check
- **beekeeper** — final HVR pass on first 10 promotions; thereafter case-by-case

---

## 10. Updated Design Principles

1. **Tenants iterate; substrate is constitutional.** Different tiers, different bars.
2. **The Compute-Substrate Gate abstracts substrate identity via the Compute Manifest.** Criteria survive substrate evolution.
3. **Promoted theorems are frozen at the statement level.** Refinement is additive.
4. **Deprecation, not deletion.** Old proofs remain valid in perpetuity.
5. **Two paths, one federation.** Research-tier (§2–§11) for algebraic-shaped, statement-immutable invariants. Contracts-tier (§13) for L3f-enforced, version-monotonic operational invariants. Path selection is mechanical (§13.7).
6. **Demotion is constitutional.** Beekeeper-only; multi-reviewer §I4 ack. (Research-tier; contracts-tier uses withdrawal per §13.6 rule 4.)

---

## 11. Sequencing Notes

- **Crawl:** Research-tier only. Wyrd's `HolographicHypergraph.lean` is grandfathered as the seed substrate corpus.
- **Toddle:** Compute Manifest v0.1 authored in `repo-wyrd`; first promotion PR exercises the pattern.
- **Walk:** Routine operation; multi-tenant promotions become the norm.
- **Run:** Compute Manifest may name new substrate per §0.13.2 silicon ladder.

---

## 12. Why a Contracts-Tier Alternative Path Is Needed

Gemini-3-Pro's 2026-05-14 review surfaced a calibration mismatch: research-tier is calibrated for *research velocity vs. constitutional soundness*. Sharp Butler / OKI / Möbius operational contracts live on a different axis — *low-latency state-boundary enforcement vs. operational soundness*.

Forcing OKI invariants through full research-tier imposes three costs unfit for operational tenants:

1. **Latency.** §I4 reader-list + Beekeeper HVR on first 10 = days-to-weeks. An HVAC invariant on second-scale household state cannot wait.
2. **Proof shape mismatch.** OKI invariants are typically *type-state* assertions at L3f boundaries, not algebraic identities. Lean-substrate immutability is wrong rigidity for state-shaped invariants that revise with each contract version.
3. **Audit scope.** Cross-tenant readers should not be required to review *every* household-scope contract — only those whose semantics cross tenant boundaries.

A contracts-tier path is *parallel* to research-tier; an invariant that becomes genuinely cross-tenant graduates to research-tier.

---

## 13. Contracts-Tier Alternative Promotion Path

### 13.1 Scope

A contracts-tier candidate is a tenant invariant **or a federation-Wyrd Translation Functor rewriting (per A22 §4.1)** that:

- Is enforced at the **L3f boundary** of the originating tenant OR at the **Wyrd Translation Layer boundary** for inter-tenant signal rewrites — not at the Wyrd substrate Lean tier
- Is **type-state-shaped** (when-can-this-contract-fire / how-does-this-signal-rewrite), not algebraic-identity-shaped
- Has a **revision cadence faster than days** (operational contracts and Translation Functor rewrites update with each tenant or substrate version)
- Is **tenant-internal**, affects only a published named set of sister tenants, or is a Translation Functor rewriting between a declared source-tenant and subscriber-tenant set

### 13.2 Gate (Four Criteria)

A contracts-tier invariant promotes to **enforced-at-L3f** status when ALL four hold:

1. **Compiles and type-checks** on the tenant's pinned Go (or other native) toolchain. Lean encoding optional.
2. **State-boundary test passes:** an executable suite demonstrates the invariant cannot be violated by any sequence of legal contract operations within tenant scope.
3. **Cross-tenant signal accounting:** if the invariant generates `NT_AUTONOMIC_SIGNAL` events crossing tenant boundaries (A22), signal classes and intended audiences are declared.
4. **Beekeeper attestation of tenant scope** OR named cross-tenant subscribers acked subscription.

### 13.3 What Contracts-Tier Does NOT Require

- **No Lean proof.** Native enforcement (Go type state) sufficient.
- **No tenant-axiom restriction.** Contract languages routinely encode policy as axiom-shaped declarations.
- **No `sorry`-free dependency closure.** Test suite is the dependency closure.
- **No Compute Manifest mode (a)/(b) check.** L3f enforcement runs on tenant's deployment substrate.

### 13.4 Lighter §I4 Reader-List

Contracts-tier promotion PRs require:
- **Tenant harness implementor** — owns L3f enforcement
- **`bma-implementor`** — verifies integration with A22 autonomic signaling
- **One named subscriber tenant implementor per cross-tenant signal class declared** — verifies subscription willingness on receive side
- **Beekeeper** — HVR pass on **first 5 promotions per tenant** (not first 10 federation-wide), thereafter only for declared safety-class contracts (signal classes including SAFETY_FLAG or INVARIANT_VIOLATION per A22 §2)

### 13.5 Promotion Latency Target

Contracts-tier promotion targets **single-business-day signoff** for routine contract revisions; safety-class promotions allow up to 72h with named-reviewer-on-call.

### 13.6 Immutability Rules (Contracts-Tier Variant)

1. **Revision permitted** with version-monotonic identifier. A revision is a new contract version; previous remains valid for in-flight contract instances that opted into it.
2. **In-flight contracts honor their opted-in version.**
3. **Cross-tenant signal subscribers honor their opt-in version.** A21 substrate immutability for corresponding Translation Functor rewriting (A22 §4) constrains how cross-tenant *meaning* evolves.
4. **Withdrawal allowed** if no in-flight contracts opted into it.

### 13.7 Path Selection — Decision Procedure

```
IF invariant is enforced at Wyrd Lean substrate AND statement-level immutability is required
THEN promote via research-tier (§2–§11)
ELSE IF invariant is L3f-enforced AND tenant-scoped or named-cross-tenant-subscribers-only
THEN promote via contracts-tier (§13)
ELSE escalate to Beekeeper for path-determination
```

### 13.8 Coupling with A22 Cross-Tenant Autonomic Translation Layer

A22 §3 rule 1 (source attestation) requires the emitting cell to own write authority on the source subgraph. For OKI-emitted autonomic signals, that authority comes from a *contracts-tier* invariant in force at the source tenant; this section makes A22 §3 rule 1 enforceable for contracts-heavy tenants. A22 §4 (Translation Functor as substrate-tier subject) remains research-tier — the cross-tenant *meaning* of a signal is constitutionally rigid even when the contract generating it is operationally flexible.

---

*BMA Spec Addendum 9.2 (recovery v0.1) | May 2026*
*Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture) with @bma-implementor (Claude Sonnet)*

---

## References

| Reference | Path / URL |
|---|---|
| Tracking issue `repo-bma-systema-issue-#164` | https://github.com/JamesPagetButler/bma-systema/issues/164 |
| Companion issue `repo-bma-systema-issue-#162` | https://github.com/JamesPagetButler/bma-systema/issues/162 |
| Recovery incident `repo-bma-systema-issue-#168` | TBD on filing |
| Companion Spec Addendum 9.1 Pentagon Pod Architecture | `/home/prime/Documents/BMA/spec/BMA-Spec-Addendum-9_1-Pentagon-Pod-Architecture.md` |
| Theory companion A21.0 Federation Knowledge-Sovereignty Frame | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-21_0-Federation-Knowledge-Sovereignty-Frame.md` |
| Theory companion A20.0 Pentagon Pod Cognitive Frame | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-20_0-Pentagon-Pod-Cognitive-Frame.md` |
| Canonical A18.0 Hypergraph Access Pattern | `/home/prime/Documents/BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md` |
| A22.0 Cross-Tenant Autonomic Translation Layer (Translation Functor; §3 source-attestation) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-22_0-Cross-Tenant-Autonomic-Translation-Layer.md` |
| Workspace phase architecture (§0.13 family) | `/home/prime/Documents/inter/workspace-phase-architecture.md` |
| Bridge channel `live-test` | sessionbridge MCP: `~/.claude/mcp-servers/sessionbridge/state/live-test.jsonl` (seq=112–130) |
| Wyrd README | `/home/prime/Documents/Wyrd/README.md` |
| QBP-CU MANIFEST | `/home/prime/Documents/QBP-Compute-Unit/MANIFEST.md` |
| BMA repo working directory | `/home/prime/Documents/BMA/` (remote: `github.com/JamesPagetButler/bma-systema`) |
| Compute Manifest v0.1 companion artifact | **TBD** — to be authored at `~/Documents/Wyrd/<path TBD>` (wyrd-implementor decision) |

*Traceability: `repo-bma-systema-issue-#164`, `repo-bma-systema-issue-#162`, `workspace-phase-architecture.md` §0.13–§0.13.2, bridge channel `live-test` seq=112–130, Wyrd README phase table, A21.0 Federation Knowledge-Sovereignty Frame, A22.0 Cross-Tenant Autonomic Translation Layer (Translation Functor contracts-tier-default per §4.1), Gemini-3-Pro review 2026-05-14 points (2) and (4).*
