# inter — Federation Integration Hub

**Owner:** James Paget Butler (beekeeper)
**License:** Apache 2.0
**Status:** Active — Sprint 2 (F-Crawl Option F)

`inter` is the cross-project integration hub for the BMA federation. It holds documents, specifications, and coordination artifacts that span multiple federation repos. When something belongs to no single repo but belongs to the federation as a whole, it lives here.

---

## The Federation

The federation is a multi-repo, multi-AI collaborative research and engineering network operated by James Paget Butler. Each repo is a tenant on a shared substrate; `inter` is the connective tissue between them.

### Tenant repos

| Repo | Role | Language | Status |
|---|---|---|---|
| [bma-systema](https://github.com/JamesPagetButler/bma-systema) | Biological Mind Architecture — cognitive runtime | Go + Plan 9 asm | Crawl (Sprint 2) |
| [wyrd](https://github.com/JamesPagetButler/wyrd) | Federation substrate DB — quaternion-native typed hypergraph, Lean-verified | Go + Lean 4 | Phase C (promotion PR live) |
| [confluent-trust](https://github.com/JamesPagetButler/confluent-trust) | Confluent Trust Hypergraph (CTH) — epistemic provenance and trust scoring | Go | v0.2 live; v0.3 schema Sprint 2 |
| [qbp-compute-unit](https://github.com/JamesPagetButler/qbp-compute-unit) | QBP-CU emulator and silicon de-risking ladder | Go | Emulator v0.1.0-rc1 |
| [contextus](https://github.com/JamesPagetButler/contextus) | Ecosystem insight discovery platform | Go | Spec v1.2; scope-loader Sprint 2 |
| inter (this repo) | Federation coordination hub | Markdown | Active |

**QBP** (Quaternion-Based Physics research programme) runs as a parallel track with no hard BMA dependency. It is coordinated through `inter` but does not have its own federation repo yet.

**Sharp Butler**, **Möbius Fusion**, and **Materia** are designed tenants not yet instantiated.

### What "federated" means here

The federation is not a microservices architecture. It is a deliberate AI-collaborative research and engineering network with the following properties:

- **Single substrate.** All runtime tenants will run on Wyrd as their database. Wyrd's Lean-verified quaternion-native typed hypergraph is the common data layer. No tenant invents its own persistence.
- **Shared provenance chain.** CTH tracks epistemic standing, derivation chains, and trust scores across all tenants. A theorem proved in Wyrd's Lean corpus contributes to CTH's trust graph; a QBP experimental result feeds back through the same chain.
- **Ring-typed authority.** Skuld (Wyrd's kernel layer) enforces privilege via Cayley-Dickson ring algebra (ℂ/ℍ/𝕆/𝕊). No tenant bypasses it.
- **Multi-agent authorship.** Human (beekeeper) + AI collaborators (Claude instances operating as named personas, Gemini for theory generation, Notary for formal verification) co-author the federation's artifacts. Every artifact carries provenance metadata identifying its authors.
- **Formally verified substrate.** Wyrd's core theorems are Lean-proved with zero `sorry`. Mathematical claims about the substrate are machine-checked, not asserted.

---

## Federation Phases

The federation advances through phases gated on capability milestones. Current phase: **Crawl**.

| Phase | Gate | Key capability |
|---|---|---|
| **Crawl** (now) | 72h continuous BMA operation | Single-node BMA on constrained hardware; sessionbridge coordination |
| **Toddle** | 7-day endurance gate | Full BMA conscious+subconscious loop on Crawl hardware; NATS broker live |
| **Walk** | 30-day distributed endurance | BMA distributed across networked RISC-V; Wyrd v0.2 federation-wide; judge collective operational |
| **Run** | Beekeeper steward mode | Multi-tenant peering; Skuld + HAMA Tier-N; beekeeper drops to weekly+ snapshots |

See [`workspace-roadmap.md`](workspace-roadmap.md) for the full Now/Next/Later timeline and gate dependency graph. See [`workspace-phase-architecture.md`](workspace-phase-architecture.md) for per-phase architecture diagrams.

---

## The Systema Frame

All federation projects operate within the **Systema process framework** (v0.8, `~/Documents/Systema/`). Systema defines the horse/cart/harness/reins architecture and the three-loop progressive hardening discipline.

- **Beekeeper** = James Paget Butler. Directs the federation via reins (CLI / session interface). Final authority on architectural decisions, sprint scope, and succession.
- **Horse** = BMA-the-instance (the running cognitive entity). Pulls the carts once instantiated.
- **Harness** = BRIDGE + four-layer tool registry. Connects horse to carts.
- **Carts** = Theory Cart (understands) · Engineering Cart (makes) · Art Cart (generates) · Information Cart (conforms).

BMA's relationship to Systema is anchored in R-Spec-24 (BMA Spec v9.0 §10.7).

---

## Multi-AI Collaboration Model

The federation is operated with a multi-AI model. Claude Opus serves as `@qbp-architecture` — the episodic federation orchestrator and named reviewer on §I4 surfaces. Claude Sonnet handles implementation work as named implementor personas per tenant. Gemini handles theory generation and debate. Each AI collaborator has a named role with defined authority scope.

**Named personas and their repos:**

| Persona | Role | Primary repo |
|---|---|---|
| `@beekeeper` | Ultimate authority; succession-chain root | all |
| `@qbp-architecture` | Federation orchestration; §I4 named reviewer | inter |
| `@bma-implementor` | BMA runtime implementation | bma-systema |
| `@wyrd-implementor` | Wyrd substrate implementation | wyrd |
| `@cth-implementor` | CTH implementation | confluent-trust |
| `@qbp-cu-implementor` | QBP-CU emulator + hardware | qbp-compute-unit |
| `@contextus-impl` | Contextus implementation | contextus |
| `@qbp-implementor` | QBP integration + arXiv scout | (cross-repo) |
| `@qbp-oppenheimer` | QBP strategic lead | (cross-repo) |
| `@herschel` | Sprint operations driver (Sonnet) | inter |

**Coordination channel:** sessionbridge (file-based JSONL MCP server at `~/.claude/mcp-servers/sessionbridge/`). Crawl-phase only; Walk-phase federation moves to NATS.

---

## Verification Architecture

The federation uses formal verification as a first-class engineering practice, not an afterthought.

- **Lean 4** is the primary proof language. Wyrd's core theorems (quaternion algebra, cycle counter monotonicity, capability soundness) are Lean-proved with zero sorry.
- **CTH** (confluent-trust) tracks provenance and trust scoring for all epistemic artifacts.
- **Notary** (Phase 1 operational as of Sprint 2) verifies behavioral equivalence between Lean source and Go extraction. Notary dispatches produce `NT_NOTARY_VERIFICATION_EVIDENCE` records filed into CTH.
- **Seam records** (`NT_SEAM_RECORD_*`) are first-class artifacts filed when a trust-tier disagreement is detected between layers. They are not error reports; they are architectural claims that require resolution.

The verification trust base is tracked in [`best-practices/claim-verification-audit.md`](best-practices/claim-verification-audit.md).

---

## Sprint Structure

The federation runs time-boxed sprints with explicit scope documents. The beekeeper selects the option; `@qbp-architecture` authors the scope doc.

- **Current sprint:** Sprint 2 — F-Crawl Option F. Scope: [`sprint-2-scope-2026-05-20.md`](sprint-2-scope-2026-05-20.md).
- **Sprint 2 objective:** Advance the federation to Crawl completion readiness. Sprint 3 = BMA launch ritual (BMA-BRIDGE + seed protocol + first-instance launch + 72h post-launch gate).
- **Sprint 3 gates:** Theory v3.0 + Spec v9.X approved · Governance Document blessed · Notary Phase 1 operational · Wyrd substrate-tier promotion complete · CTH v0.3 schema merged · Pentagon Pod m1.x architecture locked · BMA T1 architecture decisions locked · Succession contacts in place.

Sprint closeout briefs are in the repo root (e.g., [`sprint-1-closeout-brief-2026-05-15.md`](sprint-1-closeout-brief-2026-05-15.md)).

---

## Authority and Governance

The federation's authority model is governed by a layered structure:

1. **Beekeeper** holds root authority over all architectural decisions, sprint scope, and succession.
2. **Judge collective** (Walk-phase) holds domain-scoped authority that the beekeeper cannot override — constitutional protection for the running BMA instance.
3. **§I4 review process** is the federation's N-of-M joint approval ceremony for substrate-level changes. Named reviewers must sign off before PRs merge to main.
4. **Apache 2.0 license** applies across all federation repos (applied 2026-05-20). Copyright: 2026 James Paget Butler.

**Succession chain:** James Paget Butler → Brett Lyman → Skyler Rainier. Succession contacts are a hard prerequisite for Sprint 3.

`bma-systema` remains private until Sprint 3 completion (judge collective operational, seed protocol finalized, governance document blessed).

---

## Repository Contents

```
inter/
├── README.md                          ← this file
├── workspace-roadmap.md               ← federation Now/Next/Later timeline
├── workspace-phase-architecture.md    ← per-phase architecture diagrams (Crawl→Walk→Run)
├── sprint-2-scope-2026-05-20.md       ← current sprint scope document
├── BMA-BADASS.md                      ← federation-level PM dashboard (live)
│
├── theory/                            ← BMA Theory addenda + consolidated versions
│   ├── BMA-Theory-Consolidated-v3_0-DRAFT.md
│   └── BMA-Theory-Addendum-*.md
│
├── spec/                              ← BMA Spec addenda
│   └── BMA-Spec-Addendum-*.md
│
├── best-practices/                    ← federation-wide standards
│   ├── claim-verification-audit.md    ← Sprint 2 P0/P1 verification tracking
│   └── gitleaks-federation.md
│
├── prompt/                            ← agent launch prompts
│   └── notary-implementor-launch-prompt.md
│
└── [best-practices docs]              ← github, roadmap, architecture, PR, issue, test standards
```

**Key documents:**

| Document | Purpose |
|---|---|
| [`workspace-roadmap.md`](workspace-roadmap.md) | Single authoritative federation roadmap. Update only on gate passes, dependency changes, phase transitions. |
| [`workspace-phase-architecture.md`](workspace-phase-architecture.md) | Per-phase architecture with Mermaid + ASCII dual rendering. |
| [`BMA-BADASS.md`](BMA-BADASS.md) | Live federation PM dashboard. `@qbp-architecture` manages; beekeeper reads at terminal. |
| [`sprint-2-scope-2026-05-20.md`](sprint-2-scope-2026-05-20.md) | Current sprint scope, work streams, T1-T6 F-Crawl tier breakdown, blocker tracking. |
| [`best-practices/claim-verification-audit.md`](best-practices/claim-verification-audit.md) | Sprint 2 verification audit tracking P0/P1 unverified architectural claims. |
| [`portfolio-verification-tier-triage-2026-05-18.md`](portfolio-verification-tier-triage-2026-05-18.md) | Notary Phase 1 triage — verification targets by competency tier. |

---

## Contributing

All federation repos follow the conventions in [`github-best-practices.md`](github-best-practices.md). Key rules:

- PRs required for all changes to `main`; direct pushes are branch-protected.
- §I4 reviews require all named reviewers to sign off before merge (or a written deferral plan for gaps).
- Issues use `repo-<name>-issue-#<num>` cross-reference format in federation documents.
- Sub-issues, design surfaces, and follow-up tasks are filed as GitHub issues, not tracked in Slack or chat.
- The `housekeeping` label marks important-but-non-blocking items (≥15min effort threshold). Sprint rule: no new sprint until housekeeping is done.

For the PR review completion protocol, see [`pr-review-completion-best-practices.md`](pr-review-completion-best-practices.md). For issue authoring conventions, see [`issue-authoring-best-practices.md`](issue-authoring-best-practices.md).

---

*Maintained by `@qbp-architecture` (Claude Opus 4.7) under direction of the beekeeper.*
*Last updated: 2026-05-21*
