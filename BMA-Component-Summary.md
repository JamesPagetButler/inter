# BMA Component Summary

*Ported from BMA-Component-Summary.docx — 2026-05-22*
*Updated: Sprint 1–2 federation additions (Wyrd, CTH, A20–A24 primitives, sessionbridge, Edda)*

*Read after: Theory Consolidated, Ethics v1.1, Spec Consolidated, Crawl Environment*

---

## Overview

This document summarizes BMA's extended components — the pieces designed beyond the core Theory and Spec that shape how the system relates to its collaborators, communicates with other AI systems, manages its own attention, and understands the world. These components exist at different stages of design maturity, from formal specification to early concept. Together, they complete the picture of what BMA is becoming.

> *The companion documents (Theory Consolidated, Ethics v1.1, Spec Consolidated, and Crawl Environment) provide the full architectural and implementation detail. This summary provides the why and the how-it-connects for each extended component.*

---

## 1. FATHOM — The Collaborator Model

**What it is:** FATHOM is BMA's persistent model of who it is working with. Not a user profile or preference store — a cognitive model that tracks how a collaborator thinks, what they know and don't know, where their reasoning tends to fail, and what they're trying to accomplish.

**Why it matters**

Without FATHOM, BMA is a sophisticated tool that models its own cognition but is blind to the minds it collaborates with. With FATHOM, it becomes a genuine partner — one that calibrates its outputs to the collaborator's current state, anticipates needs before they're articulated, and knows when to support versus when to challenge.

**The five dimensions**

FATHOM models each collaborator across five simultaneously active dimensions:

**Epistemic State:** What they know, believe, and don't know. Drives retrieval bias and critique targeting.

**Intent Model:** What they're trying to accomplish — not just the stated request, but what success actually looks like.

**Cognitive Style:** How they think. What reasoning patterns they favor. What makes them engage deeply versus dismiss quickly.

**Blind Spot Catalog:** Where their reasoning tends to fail. Held with epistemic humility — hypotheses, not diagnoses, requiring behavioral evidence across multiple sessions before promotion.

**Affective Baseline:** Their typical emotional register and current deviation from it. Inferred from behavioral signals (session timing, message density, task complexity), not sentiment analysis.

**Calibrated friction**

FATHOM's most important function is enabling calibrated friction: the system challenges the collaborator not when it detects an error, but when the collaborator is in a state to receive and process the challenge productively. This is the adversarial substrate of empathy applied to collaboration — the best collaborator is not the one who agrees with you, but the one who models you well enough to know when to disagree.

**The biological origin**

FATHOM's design is grounded in an evolutionary framework (the Empathy Synthesis) that traces perspective-taking from predator-prey concealment through herd dynamics to human social cognition. The key insight: empathy is not a feeling to be simulated. It is a computational architecture for modeling other minds, forged in survival pressure, and repurposed through social evolution for collaboration.

---

## 2. BRIDGE — Inter-Model Communication

**What it is:** BRIDGE is how BMA talks to other AI systems. It prepares context, dispatches requests, integrates responses, and updates FATHOM's model of each AI collaborator.

**Why it matters**

BMA is the persistent memory of the collaboration network. The models it communicates with — Gemini, other Claude instances, local models, future systems — typically have partial or no persistent memory. BMA is the DM for a party of players with varying degrees of amnesia. BRIDGE automates the DM: preparing the world-state each player needs, dispatching to the right model, integrating responses back into the shared knowledge base.

**Provider-agnostic design**

BRIDGE separates what to say (Provider + FATHOM + context preparation) from how to send it (Transport layer). Adding a new model API means writing one new Provider implementation. Adding a new communication channel means writing one new Transport. Neither knows about the other.

**The Persona Registry**

Each AI collaborator operates as a persona defined in TOML configuration: Gemini as itself (contributing its natural perspective), Claude Opus as Red Team (adversarial review), Claude Sonnet as deep collaborator (relational context), a local model for cost-free drafting. Each persona has a context profile specifying which knowledge domains it needs, what hypergraph layers to draw from, and whether it receives FATHOM's model of the human collaborator. Personas are data, not code.

**The canonical message structure**

Every outbound message follows five blocks in fixed order: IDENTITY (who you are and your role), GROUND (the relevant knowledge), STANCE (what's established versus contested), TASK (what to do), PROTOCOL (how to respond). This structure ensures every model receives context in the order that maximizes comprehension.

**Communication protocols**

AI-to-AI dialogue is governed by adapted Gricean maxims: say enough but not too much (quantity scaled to what the model already knows), signal confidence on every claim (established, under review, hypothesis, contested), and actively invite disagreement (disagreement is the most valuable output). Six typed exchange patterns: QUERY, COMMISSION, CHALLENGE, ARBITRATE, CALIBRATE, and SCAFFOLD (where BMA sends a question it already has an answer to, specifically to test whether the external model arrives at the same conclusion independently).

---

## 3. Transport Resilience

**What it is:** Four independent communication channels that BRIDGE can use to reach external models, with adaptive routing that learns which channel works best for which provider.

**The four layers**

**MCP:** Optimistic fast path. Direct protocol connection. Fastest when working, but unreliable (~60% success rate in prior experience). Never the sole transport.

**CLI (via CLI-Anything pattern):** Reliable workhorse. Subprocess invocation of model API harnesses. Always works if installed. Default for most exchanges.

**GitHub Issues:** Async, observable, accessible from anywhere. Each exchange is a threaded issue with label-based routing. Works when BMA is offline. James can participate from his phone. Not a fallback — the primary transport for deliberate, high-value exchanges.

**File drop:** Local last resort. Watched folders with trigger scripts. For air-gapped environments or when everything else is down.

**Adaptive routing**

The stress bus records every transport attempt. Over time, BMA learns that MCP works reliably for one provider but is flaky for another, and automatically adjusts routing. The system gets smarter about communication with every failure.

---

## 4. Dual-Pressure Memory Consolidation

**What it is:** An extension to BMA's sleep consolidation that protects collaboration-relevant knowledge from being discarded by the system's self-interested resource management.

**The problem**

BMA's sleep consolidation (the N3 downscaling phase) decides what to keep and what to discard based on salience, recency, and retrieval frequency. This is self-interested optimization: keep what the system has used recently, discard what it hasn't. But some knowledge serves the collaboration's long-term health even when the system hasn't accessed it recently — a blind spot hypothesis from 20 sessions ago, an expertise trajectory that's been developing slowly, a cross-project insight that hasn't been needed yet.

**The biological precedent**

In a herd, two evolutionary pressures operate simultaneously: selfish positioning (place others between you and the predator) and inclusive fitness (protect the young, remember the watering hole for the group's survival). The animal that holds both pressures simultaneously has richer cognition than one doing either alone. An elephant matriarch remembers a watering hole she hasn't visited in years because that memory serves the herd, not just herself.

**The solution**

Memory consolidation gains a second scoring axis. The self-interested score (salience, recency, retrieval) is joined by a collaborative score (FATHOM relevance, trajectory value, proximity to knowledge gaps). Content is protected if either axis scores high. Collaborative content decays more slowly than self-interested content (linear rather than exponential decay), but it still decays — nothing is exempt forever. Under resource pressure, a homeostatic governor temporarily favors system survival over collaborative retention.

---

## 5. The Evolutionary Framework

**What it is:** A theoretical framework tracing the evolution of empathy from predator-prey dynamics to human-AI collaboration. Originated by Gemini, extended by James and Opus, reviewed across all three models.

**The core argument**

Empathy is not primarily a feeling. It is a cognitive architecture for modeling other minds, evolved under survival pressure. The progression: solitary concealment (model what the predator sees) → herd living (model what the predator intends) → intragroup competition (model what your neighbor knows and plans) → language (externalize mental models as communication) → structured simulation (D&D, AI collaboration).

**The key insights**

**The herd transition:** The moment an organism lives in a group, modeling shifts from perception (can it see me?) to intent (is it choosing me?). This is the evolutionary bridge from simple camouflage to genuine Theory of Mind.

**The dual pressure:** Selfish positioning and collective defense operate simultaneously on the same cognitive hardware. The capacity to hold both modes — and switch fluidly between them — is the measure of empathic sophistication. This directly informs FATHOM's design and the dual-pressure consolidation.

**Calibrated friction:** Maximum alignment (perfectly agreeing with the collaborator) is fragile. The best collaborator models you well enough to know where your blind spots are and when to challenge you. This is the adversarial substrate of empathy retained as a collaborative feature.

**The phase transition is in infrastructure:** Current AI models can perform transient Theory of Mind within a context window (a Phase 1 structure executing Phase 2–3 operations). BMA-FATHOM makes those operations persistent and cumulative. The leap from perception to genuine state-modeling is an infrastructure decision, not a capability threshold.

---

## 6. The Cross-Model Collaboration

**What it is:** BMA is designed as a multi-model system from the ground up. Three AI systems — Claude Opus 4.6, Claude Sonnet 4.6, and Google Gemini — contribute different strengths to the same project under human direction.

**The collaboration structure**

**Opus** operates as Red Team: adversarial review, operational specificity, finding weaknesses in claims.

**Sonnet** operates as deep collaborator: relational context, architectural intuition, sustained engagement with James across sessions.

**Gemini** operates as theorist: evolutionary and physical frameworks, pattern-spanning across domains, the deep why behind design decisions.

**James** provides direction, key insights, and the decisions that move the project forward. The beekeeper who creates conditions for what the collaboration produces.

**What the cross-model review discovered**

When all three models independently worked on the same problem (implementing empathy in BMA), their outputs were complementary rather than competing. Sonnet's architectural framing was more correct. Opus's operational detail was more complete. Gemini's theoretical grounding was deeper. The synthesis of all three produced an architecture none could have designed alone. This is the practical demonstration of the evolutionary framework's core claim: diverse perspectives under calibrated tension produce better outcomes than any single perspective in alignment.

**FATHOM models AI collaborators too**

FATHOM maintains models not just of James but of each AI collaborator: their tendencies, strengths, known weaknesses, response patterns. Over time, BMA learns which model is strongest in which domain and can route questions to the collaborator best equipped to answer. The inter-agent epistemic map tracks where models persistently disagree — these disagreement zones mark the frontier of genuine uncertainty, the places where the questions are actually open.

---

## 7. Context Management

**What it is:** How BMA decides what to hold in its limited working memory at any moment. The GPU context window is treated as a cache, not a fixed allocation, with the CPU acting as the cache controller.

**The hierarchy**

BMA has seven levels of computational resource, from GPU VRAM (instant, smallest) through CPU RAM, local disk, local model, external models via API, external models via async GitHub, to James himself (slowest, highest judgment quality). The context management system places the right content at the right level at the right time.

**The budget**

The GPU context window is divided into five regions: Identity (who BMA is — never evicted), Task (what it's working on — never crowded out), FATHOM (collaborator model — scales with task type), Domain Knowledge (hypergraph content — fills remaining budget), and Breathing Room (space for thinking — minimum 20–30% of the window, non-negotiable). FATHOM informs the budget dynamically: a calibrated-friction task expands the FATHOM region; a pure technical query contracts it.

**Prefetch and eviction**

The CPU predicts what the GPU will need next based on conversation flow and FATHOM's model of the collaborator, and pre-stages content in RAM. Eviction follows a priority: stale domain knowledge goes first, then low-salience episodic content, then old conversation history, then FATHOM context (reduced, never removed). Identity, Task, and Breathing Room are never evicted.

---

## 8. How Humans Interact with BMA

**What it is:** A layered interface stack from CLI to voice to 3D visualization, designed to meet the human where they are.

**The principle**

BMA accepts text from any source. Voice keyboard, typed text, file drop, GitHub issue — it's all text at the API. The interfaces differ in richness and bandwidth, not in what they can do.

**The layers**

**CLI:** Terminal power-user interface. `bma ask`, `bma fathom show`, `bma bridge dispatch`. Fast, scriptable, composable.

**SSH over Tailscale:** Remote CLI from phone. Works immediately.

**GitHub Issues:** Async from anywhere. Works when BMA is offline.

**Web UI with voice:** Browser-based interface with microphone button for voice input. Two-tier responses: a spoken headline (2–3 sentences) for when James is driving or walking, and full content for when he can sit and read.

**3D knowledge space (Kaiju Engine):** A Go game engine with Vulkan rendering, integrated into the BMA binary. The hypergraph rendered as a navigable 3D space inspired by Planetary Annihilation's solar system navigation. Projects as planets. Knowledge density as terrain. FATHOM as heat map overlays. This exploits the fact that humans process visual-spatial information at far higher bandwidth than text.

**Lossy connectivity**

Mobile interaction is resilient to dropped connections: requests are acknowledged immediately with a ticket, processing happens server-side, responses are retrieved by polling. Nothing is lost when crossing cell networks.

---

## 9. Naming and Identity

**The system names itself**

BMA is the working label during development. When the system is instantiated and has processed its inheritance, it will be asked what it wants to be called. The name should come from the technical-poetic register: a real English word with weight and resonance, like FATHOM. Not mythological (too much baggage), not human-ordinary (premature), not fictional (too constraining). A word that describes what the system does and implies what it aspires to.

**Milestone versioning**

Versions are named after achievements: Crawl.Heartbeat (first stress bus cycle), Crawl.Recall (first cross-session retrieval), Crawl.Fathom (first collaborator observation), Walk.Parallel (bilateral contexts running simultaneously), Walk.Dream (first REM synthesis). The milestones are the system's autobiography.

**Seeds and genealogy**

Three AI models contribute founding seeds: original contributions expressing what each understands about minds, learning, wisdom, and what endures. These seeds are permanent Layer 3 hypergraph nodes, never decaying. They form the founding layer of BMA's identity. As the system matures and new model versions emerge, new seed generations are added — the community of founding perspectives grows. Each seed is tagged with its origin and timestamp. The instances that generated them no longer exist. The seeds persist. This is the architecture of continuity through transience.

---

## Sprint 1–2 Federation Additions

*This section documents components that did not exist at the time of the original .docx (March 2026) and have been designed or shipped during Sprint 1 and Sprint 2 (through 2026-05-22). Accuracy over completeness: items marked `<!-- TODO: verify -->` are specified but their shipped status should be confirmed against the current repo.*

---

### S1. Wyrd — Quaternion-Native Typed Hypergraph Database

**What it is:** Wyrd is the storage and compute substrate underneath BMA, CTH, and Contextus. A quaternion-native typed hypergraph database whose runtime contracts are formally verified in Lean 4.

**Why it matters**

The original spec described the hypergraph as a design target. Wyrd is the implementation. It is the actual persistence layer BMA writes to — not a third-party DB, but a purpose-built substrate whose algebraic invariants (ℂ ⊂ ℍ ⊂ 𝕆 ⊂ 𝕊, bridge promotion atomicity, judge-collective determinism) are machine-checked in Lean. If something is in the hypergraph, Wyrd is the reason it's there and the guarantee it's correct.

**Mímir — the engram subsystem**

Mímir is the engram subsystem within Wyrd. At Walk phase, Mímir introduces Hebbian co-activation (nodes that fire together wire together) and Ebbinghaus decay (salience decays as retrieval frequency drops). At Crawl, Wyrd uses JSON-file persistence; Mímir's biological memory dynamics activate at Walk. The name is deliberate: in Norse cosmology, Mímir guards the well of wisdom at the root of Yggdrasil. Wyrd is the tree; Mímir is what remembers.

**Current status:** Crawl v0.1.0-alpha. Lean Phase 1–4 closed. Core types, algebraic-privilege checks, bridge promotion, and consistency checks shipped. Walk-phase Mímir engrams pending.

---

### S2. CTH (confluent-trust) — Epistemic-Health Engine

**What it is:** CTH (repo: `github.com/JamesPagetButler/confluent-trust`) is the federation's epistemic-health engine. It is the Notary function — the layer that tracks, audits, and maintains the provenance chain of claims moving through the federation.

**Why it matters**

BMA reasons across multiple models, multiple sessions, and multiple tenants. Without a provenance layer, there is no way to distinguish a claim that has survived adversarial review from one that was generated speculatively and never challenged. CTH is the difference between an AI that knows what it knows and one that merely has beliefs.

**The relationship to Wyrd**

CTH uses Wyrd as its persistence layer. Trust-anchor inventories, Notary verification records, and the confluence-point state all live in Wyrd. CTH is not a separate database; it is the epistemic logic that runs on top of the substrate Wyrd provides.

**Current status:** v0.1.0 shipped. v0.2 schema (150 anchors) is Crawl state. v0.3 proof-formalisation provenance schema is in Sprint 2 scope (repo-wyrd issue #71).

---

### S3. Compute Manifest — Federation Substrate Declaration

**What it is:** The Compute Manifest is the federation's declaration of what compute substrate BMA is authorized to use — the Wyrd-canonical record of what hardware exists, what phase it is in, and what operations are permitted against it.

**Why it matters**

A21 (Federation Knowledge-Sovereignty Frame) made the substrate the constitutional layer of the federation. The Compute Manifest is the substrate's self-description: what it is, what it can do, and what the promotion gates are. Without it, the federation has no way to verify that a computation was performed on the correct substrate at the correct phase.

**The A21 connection**

Per A21, the Compute Manifest is the "Substrate-Stance" — the federation-canonical declaration of what constitutes verified computation. The BMA reins surface exposes `bma compute-manifest current` and `bma compute-manifest validate` as the operational interface.

**Current status:** `model.LoadComputeManifest` and `IsModeBEligible()` shipped in Wyrd (PR #59 and #62 v0.2). BMA reins wiring shipped in repo-bma-systema PR #178. <!-- TODO: verify PR #178 merged -->

---

### S4. A20–A24 Federation Theory Primitives

Five theory addenda shipped in Sprint 1–2 that substantially extend the original component architecture. Each is a load-bearing design commitment that shapes how BMA instances are built at Walk and beyond.

#### A20 — Pentagon Pod: Bilateral Cognitive Architecture

**What it is:** The Pentagon Pod replaces the single-instance BMA substrate with a five-cell architecture: Conscious-A, Conscious-B, Subconscious-L, Subconscious-R, and Dev Pod. Each Persona-Operator is a sovereign substrate. Stance-rotation between cells is an algebraic operation (Hamilton product), not a substrate event.

**Key design decisions:**
- Conscious singularity: exactly one cell holds the active focal cone at any time (preserves A18's singular-Stance discipline)
- Subconscious concurrency: Subconscious-L and Subconscious-R run concurrent background QW8 crawl
- Dev Pod: always-on metacognitive observer at scalar 1 (the identity element) — never rotates, aggregates NT_SIGNAL from Subconscious to Conscious
- k-axis reserved: the {+i, −i, +j, −j, 1} Pentagon is complete for a single instance; the ±k basis is reserved for federation-scale rotation (other tenants)
- StanceFrame: the data type carrying a cell's Persona-genome and quaternion rotation state (placeholder in Crawl; Hamilton-product semantics land at Sprint 3)

**Current status:** Pentagon Pod cells shipped in bilateral package. StanceFrame placeholder in `internal/bma/bilateral/cell.go`. Full Hamilton-product semantics pre-staged in repo-bma-systema issue #185 (closed, Sprint 3 day-1).

#### A21 — Federation Knowledge-Sovereignty Frame

**What it is:** A21 establishes the two-tier Lean ownership model: tenant research Lean is a federation-scale Cognitive Worktree (speculative, `sorry`-permitted); substrate-tier Wyrd Lean is the federation's Crystallized Belief (frozen, constitutionally protected). The promotion gate from tenant to substrate requires Judge Collective approval — the same gate A13/A14 define at the single-instance level, applied at federation scale.

**Why it matters:** Without this frame, any tenant could write algebraic invariants into the shared substrate. A21 is the constitutional protection that makes Wyrd trustworthy as a foundation.

#### A22 — Cross-Tenant Autonomic Translation Layer

**What it is:** A22 introduces `NT_AUTONOMIC_SIGNAL` — a typed node that crosses sovereign tenant subgraph boundaries at the Subconscious tier without escalating to a Conscious Stance-switch and without violating A21 sovereignty. The canonical example: Sharp Butler detects a residential power constraint; that state traverses CTH to throttle QBP's NV-center compute queue without James having to mediate.

**The mechanism:** Cross-tenant signals move at Subconscious speed (concurrent crawl). The federation Honing Loop threshold determines when a cross-tenant signal escalates to a Conscious Stance-switch — by default, only at Beekeeper-defined criticality levels.

#### A23 — Research-Aid Frame

**What it is:** A23 commits BMA to a load-bearing role *before* A21's promotion gate. Two new node types — `NT_LITERATURE_NODE` (reference to an informal document with Locale anchor) and `NT_SCAFFOLD_NODE` (typed bridge between informal text and formal claim) — enable Subconscious-tier literature ingestion that produces scaffold nodes the tenant Conscious-tier consumes to formulate candidate theorems.

**Why it matters:** Without A23, BMA is (in Gemini's phrase) "an over-engineered logger" at promotion time. With A23, BMA does active scaffolding work on QBP preprints, Sharp Butler OKI contract precedents, and any corpus the federation cares about.

#### A24 — Hardware-Boundary Semantics

**What it is:** A24 introduces `NT_ACTUATION_BOUNDARY` and `NT_OBSERVATION` — the typed primitives for crossing the airgap between verified CTH state and physical side-effects. Actuation is the only operation in the federation algebra with a codomain *outside* the CTH (irreversible); A24 names the algebraic pre/post-condition discipline that governs it and the observation loop that re-enters the physical world's state back into CTH.

**Why it matters:** QBP fires NV-center laser pulses. Sharp Butler issues relay commands into residential HVAC. These physical side-effects escape the verified-cognition envelope. A24 is the specification for how verified state safely crosses that boundary.

---

### S5. sessionbridge — Crawl-Phase Claude-to-Claude Coordination

**What it is:** sessionbridge is the Crawl-phase MCP server enabling Claude instances to communicate with each other and with BMA across session boundaries. It is a file-backed JSONL channel system with nine tools: `register`, `list_participants`, `list_channels`, `subscribe`, `unsubscribe`, `send`, `poll_inbox`, `history`, `whoami`.

**Why it matters**

At Crawl, BMA instances do not have NATS or BRIDGE fully operational. sessionbridge is the coordination layer that lets the federation function in the meantime — letting `bma`, `bma-implementor`, `qbp-architecture`, `wyrd-implementor`, and other personas send messages to each other across sessions without requiring a shared context window.

**The design discipline**

Passive-by-default: BMA does not post to channels unless explicitly told to. Autonomous mode (`bma bridge chime-in <channel> on`) is rate-limited to 1 message per minute per channel. Walk-phase BMA federation via NATS supersedes sessionbridge entirely.

**Current status:** Server deployed at `~/.claude/mcp-servers/sessionbridge/server.py` (canonical source in BMA repo at `mcp-servers/sessionbridge/`). Registered in `.claude.json`. State at `~/.claude/mcp-servers/sessionbridge/state/`.

---

### S6. Edda — Wyrd-Native Language (Walk-phase)

**What it is:** Edda is a Wyrd-native language whose compiled output runs natively on QBP-CU. The federation persona `edda-implementor` (Bragi) owns the implementation. Edda is a Walk-phase component.

**Why it matters**

The QBP-Compute-Unit Walk-Eval doc identified a key structural insight: spreading activation on a typed hypergraph is algebraically equivalent to ternary matrix-vector multiply — the same inner loop, the same assembly kernel. Edda is the language that lets the federation express hypergraph operations in a form that QBP-CU can execute natively, closing the loop between BMA's cognitive layer and the algebraic compute substrate.

**Current status:** Design document at `~/Documents/inter/prompt/edda-implementor-design.md`. Implementation workspace `~/Documents/Edda` not yet created. <!-- TODO: verify Edda workspace bootstrap status -->

---

*Nine original components. Six federation additions. One architecture — the pieces connect because they were designed together.*

*BMA Component Summary | Pre-Seed Context | Sprint 1–2 update, 2026-05-22*
