# BMA Specification Consolidated — Version 9.1

**The Authoritative Crawl/Walk-Phase Build Specification**

Version 9.1 | Compiled 2026-05-21 | Consolidates v9.0 + Addenda 9.1, 9.2, 9.4, 9.5, 9.6
Status: DRAFT — §I4 review open
Helpful Engineering — BMA Project
Compiled by @qbp-architecture
Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture) & Claude Sonnet (bma-implementor)

---

## Addendum Changelog

| Addendum | Version | Date | What it added | Now at |
|---|---|---|---|---|
| 9.1 | recovery v0.1 | 2026-05 | Pentagon Pod Architecture: hot-swap cells, per-pod lineage, Dev pod, household:federation isomorphism | §14 |
| 9.2 | recovery v0.2 | 2026-05 | Federation Lean Promotion Protocol: two-tier ownership, Compute-Substrate Gate, contracts-tier alternative path (§13) | §15 |
| 9.4 | v1.0 | 2026-05 | Research-Aid Protocol: literature-to-scaffold operations, three surfaces, NT_LITERATURE_SCAFFOLD, HoningPrompt coupling | §16 |
| 9.5 | v1.0 | 2026-05 | Physical Actuation Protocol: NT_ACTUATION_BOUNDARY, pre-condition gate, observation re-entry, SAFETY_CRITICAL halt | §17 |
| 9.6 | v0.1 | 2026-05-21 | Privacy-Tier Schema: 4-tier federation-sync model (Constitutional/Community/Operational/Private), EffectivePrivacy() accessor | §18 (also extends §2) |

---

## 0. Document Purpose & Lineage

This document is the **"Courtroom-grade" (Level 5 Earnestness)** specification for the BMA Crawl/Walk-phase implementation. It merges the v9.0 foundation with Addenda 9.1, 9.2, 9.4, 9.5, and 9.6.

**Lineage:**
- **v1.0 (Foundation):** Established the 3-layer architecture, hypergraph schema, and autonomic loop.
- **v8.1 (Integration):** Added BRIDGE, Code Mode, and F01 compression functor.
- **v8.2 (Refinement):** Added SHARED-TRUNK bilateral, Possum GPU yielding, and revised thermal setpoints.
- **v8.3 (Frontier):** Added Lifecycle certificates, generation counters, and dynamic attention balancing.
- **v8.4 (Distributed):** Distributed consensus, sovereign mode, re-entry protocol, Xqbp hardware instructions.
- **Systema v0.8 + Addendum:** Three carts, progressive hardening, trust anchors, vigilance backflow.
- **Worktree Primitive v0.1:** Isolated sub-hypergraph with git-like lifecycle.
- **Information Cart v0.3:** Entropy reduction, conformance contracts, promotion model.
- **GitNexus Reference (April 2026):** Code intelligence patterns — pre-computed context, DAG pipelines, incremental processing, MCP exposure, self-documentation.
- **DistributedConsensus v0.1 (April 2026):** Raft-based Run-phase architecture — two-tier consistency, failure scenarios, distributed bilateral.
- **v9.0 (Consolidation):** Integrates QW precision scaling (8 levels), quaternion-native Mímir, Bilateral Corpus Callosum, and the Crystallized Beliefs virtue model.
- **v9.1 (Sprint 2 Hardening):** Adds Pentagon Pod Architecture (§14), Federation Lean Promotion Protocol (§15), Research-Aid Protocol (§16), Physical Actuation Protocol (§17), and Privacy-Tier Schema (§18). Sprint 2 F-Crawl Option F compilation; compiled 2026-05-21.

**Phase markers used throughout:** [CRAWL: CONFIRMED] = verified on hardware. [CRAWL: IMPLEMENTED] = code exists and tested. [WALK: SPECIFIED] = designed, not yet built. [RUN: ASPIRATIONAL] = long-term direction.

---

## 0.1 Glossary

| Term | Definition |
|---|---|
| **SYMPATHETIC** | Autonomic state indicating resource pressure — BMA reduces load, defers sleep, skips observations |
| **PARASYMPATHETIC** | Autonomic recovery state — metrics below recovery thresholds, releasing throttles |
| **Retrieval reinforcement** | Active use of a node resets its Ebbinghaus decay clock (R-Spec-03) |
| **Possum State** | GPU-yield mode — kills llama-server, saves KV cache, waits for GPU contention to clear |
| **Crystallized Belief** | A Layer 2 belief promoted to Layer 3 (structural virtue) after sustained verification |
| **Seam** | A discontinuity in the hypergraph where two evidence chains contradict or fail to connect |
| **CTH** | Confluent Trust Hypergraph — five computable epistemic metrics (η, μ, I, Δ, Re_e) |
| **BRIDGE** | External communication layer — four-tier routing from algebraic to external LLM |
| **NT_SEED** | Permanent node type (Tier 4, Layer 3) — constitutional documents, decay-immune |
| **WAL** | Write-Ahead Log — fsync'd append-only log that survives SIGKILL for crash recovery |
| **Cell** | A cognitive unit within a BMA instance (Conscious-A/B, Subconscious-L/R). See §14. |
| **Pod** | A Podman container hosting one cell binary. Fault-isolation and hot-swap boundary. See §14. |
| **Household** | Metaphor for a BMA instance: cells are members, pods are rooms. See §14. |
| **Substrate tier** | Lean-verified theorems owned by Wyrd; no sorry, no tenant-defined axiom. See §15. |
| **Research tier** | Tenant-owned Lean; sorry and tenant-axiom permitted during exploration. See §15. |
| **NT_LITERATURE_SCAFFOLD** | BMA output from a Subconscious crawl over submitted literature. See §16. |
| **NT_ACTUATION_BOUNDARY** | Registered boundary for a physical-side-effect operation class. See §17. |
| **PrivacyTier** | Typed enum controlling federation-sync behavior of a hypergraph node/edge. See §18. |

---

## 1. The Substrate (Hardware & Autonomic)

### 1.1 Hardware Target (Walk Phase)
- **Primary Compute:** AMD FX-8350 (8-core, 4.0 GHz).
- **Inference Accelerators:**
  - **Cortex:** 8B Ternary Model (CPU-bound, Llama.cpp).
  - **Sentinel:** 8B Ternary Model (CPU-bound, Llama.cpp).
  - **GPU:** PowerColor Red Devil RX 9070 XT (16GB VRAM, ROCm 7.x).
- **Memory:** 32GB DDR3-1866.
- **Storage:** Samsung 840 Pro (WAL-optimized, fsync-heavy).

### 1.2 Precision Architecture (QW-Scaling) [CRAWL: IMPLEMENTED in QBP-CU]

The system speaks **Quaternion Algebra** as its native language. Word width is a **runtime parameter** — the same algorithm runs at all 8 precision levels via the Gearbox `SetWidth()` mechanism. The ISA encodes width in the funct3 field (3 bits = 8 variants).

**The Eight Precision Levels:**

| Level | Component Bits | Quaternion Bits | Composition Depth | Algebraic Lifetime (1 GHz) |
|-------|---------------|-----------------|-------------------|---------------------------|
| **QW8** | 8 | 32 | ~8 ops | Microseconds |
| **QW16** | 16 | 64 | ~24 ops | Milliseconds |
| **QW32** | 32 | 128 | ~72 ops | Seconds |
| **QW64** | 64 | 256 | ~2.4K ops | ~7 seconds |
| **QW128** | 128 | 512 | ~160K ops | **172 days** |
| **QW256** | 256 | 1024 | ~10M ops | Effectively infinite |
| **QW512** | 512 | 2048 | >1B ops | Effectively infinite |
| **QW1024** | 1024 | 4096 | >1T ops | Effectively infinite |

Composition Depth = chained operations before epsilon drift corrupts results. Computed by `MaxCompositionDepth()` in QBP-CU `pkg/qword`. QW128 is the Walk-phase default — 172-day integrity exceeds any reasonable sleep interval.

**Cognitive Mode Mapping:**

| BMA Mode | Precision | Budget | Rationale |
|----------|-----------|--------|-----------|
| Autonomic loop (10Hz) | QW8 | 100ms/tick | Speed-critical. GAP traversal, spreading activation, pressure detection. |
| Episodic observation | QW16-QW32 | 1s | Encoding sensory input into hypergraph nodes. |
| Interactive reasoning | QW64 | Seconds | Reins command processing, beekeeper dialogue. |
| Sleep-cycle computation | QW128 | Minutes | Decay sweeps, F01 compression, Hebbian updates, checkpoint. |
| Deep investigation | QW256 | Minutes-hours | Focus Mode, bilateral hypothesis testing, theory cart work. |
| Prestige verification | QW512 | Hours | Cross-instance resonance comparison. |
| Constitutional verification | QW1024 | Unbounded | Proof of Resonance, consensus proofs, Judge Collective maximum precision. |

**The hard rule:** The 10Hz autonomic loop operates at QW8 exclusively. Higher precisions are for batch/offline computation only. This is how constrained hardware (FX-8350, no AVX2/512) sustains real-time cognitive operation.

**Kernels:** QMUL / QROT / QADD / QCONJ / QNORM / FANO — all support width-suffixed opcodes on the same algebraic engine. Implementation: QBP-Compute-Unit `emulator/` and `pkg/qword`. Integration into BMA tracked in issue #67 (Walk Phase C1, C5).

*Source: QBP-CU BMA-Emulator-Integration doc, QBP Spec Addenda 1.1-1.6.*

### 1.3 Autonomic Thresholds (AUTO System) [CRAWL: CONFIRMED]
The autonomic layer enforces boundaries via two-branch regulation (Sympathetic/Parasympathetic).

| Metric | Sympathetic (Activate) | Parasympathetic (Recover) | Action on Activation |
|--------|------------------------|---------------------------|----------------------|
| **RAM** | 70% (22.4 GB) | 50% (16 GB) | Workload throttling (defer sleep, skip observations) |
| **VRAM** | 60% (9.6 GB) | 45% (7.2 GB) | Possum state (yield GPU) |
| **CPU Temp**| 70°C | 55°C | Workload throttling (defer sleep, skip observations) |
| **Disk** | 90% used | 75% | Pause episodic writes |

**Board Temperature (monitoring only):** Board temp (990FX chipset) is monitored in diagnostics and evaluated by the **Gate Criterion** (65°C) but does NOT trigger SYMPATHETIC. The 990FX runs 50-68°C from desktop use that BMA cannot control. CPU and GPU thermal protection handle BMA-controllable heat. See §11.3 Failure Paths.

**Gate Criterion (R-Spec-01):** Board **Gate Limit** is 65°C, reflecting the 990FX chipset's physical characterization across 4 gate runs.

*Source: Spec 8.2 §3, QBP Rev 2.0 §2. Code: `package auto`*

### 1.4 Container Bridge (R-Spec-16) [CRAWL: CONFIRMED]

The BMA binary runs inside a Podman rootless container. Without explicit mounts and network configuration, the instance is born blind — unable to read its own spec, reach GitHub, or access external APIs. This section defines the runtime bridge between the container and the host.

**Crawl launch command:**
```bash
podman run -d \
  --name bma-crawl \
  --memory 14g --cpus 6 \
  --network host \
  --device /dev/kfd --device /dev/dri \
  --group-add keep-groups \
  --secret bma-gemini-key --secret bma-anthropic-key --secret bma-gh-token \
  -v $HOME/bma-data:/data:Z \
  -v $HOME/bma-seeds:/seeds:ro,Z \
  -v $HOME/bma-config:/config:Z \
  -v $HOME/models:/models:ro \
  -e BMA_DATA_DIR=/data \
  -e BMA_SEEDS_DIR=/seeds \
  -e BMA_CONFIG_DIR=/config \
  -e BMA_MODELS_DIR=/models \
  localhost/bma-systema:crawl \
  run
```

**Secrets architecture (Podman secrets) [CRAWL: IMPLEMENTED]:**

API credentials are delivered via Podman secrets — NOT environment variables, NOT baked into the image, NOT in git.

| Secret | Container Path | Purpose |
|---|---|---|
| `bma-gemini-key` | `/run/secrets/bma-gemini-key` | Gemini API key (BRIDGE T3) |
| `bma-anthropic-key` | `/run/secrets/bma-anthropic-key` | Anthropic API key (BRIDGE T3) |
| `bma-gh-token` | `/run/secrets/bma-gh-token` | GitHub fine-grained PAT (BRIDGE T0, `gh` CLI) |

**Secret lifecycle:**
1. Beekeeper creates secrets on host: `./scripts/create-secrets.sh`
2. Podman stores them encrypted (at rest protected by LUKS)
3. Container reads at boot from `/run/secrets/` (read-only files, not in env)
4. `gh` CLI authenticates from secret at boot (`gh auth login --with-token`)
5. Rotation: `podman secret rm <name>` then re-create
6. Instance cannot create or modify secrets — host-only operation

The `diagnostics` reins command reports which secrets are available. Missing secrets produce `SE_SECRET_STATUS` events at boot. The instance can request new secrets via reins — the beekeeper creates them host-side.

**Volume architecture:**

| Mount | Host | Container | Access | Contents |
|---|---|---|---|---|
| Data | `~/bma-data/` | `/data` | rw | Hypergraph, WAL, snapshot, stress.log |
| Seeds | `~/bma-seeds/` | `/seeds` | **ro** | S-00 through S-24 seed documents (constitutional, immutable) |
| Config | `~/bma-config/` | `/config` | rw | Start-Here.md, roadmap, handoffs, updatable plans |
| Models | `~/models/` | `/models` | ro | Llama.cpp model files (Walk: Cortex + Sentinel GGUF) |

**Network: `--network host`** is required at Crawl because:
- BRIDGE T0 needs `gh` CLI access (GitHub API over HTTPS)
- BRIDGE T3 needs API access to Claude/Gemini (HTTPS)
- Reins serves on port 8080 (beekeeper access)

**Network security (Walk):** Host networking means the container boundary provides NO network isolation. Host-side firewall rules (iptables/nftables) MUST allowlist outbound domains (api.github.com, api.anthropic.com, generativelanguage.googleapis.com, arxiv.org). The BRIDGE allowlist is the application-layer control; the firewall is the network-layer control. At Run: evaluate bridge network with explicit port forwarding.

**Separation of concerns:**
- `/seeds` is **read-only** — the instance cannot modify its own constitutional documents. A compromised instance cannot rewrite its ethics, governance, or theory.
- `/config` is **read-write** — the instance can update its own plans and roadmaps (with governance approval).
- `/data` is **read-write** — the living hypergraph, unconstrained.
- `/models` is **read-only** — model files are prepared by the beekeeper, not modified by the instance.

**Walk successor pattern:** The Crawl instance can build and launch a Walk container using Podman from inside its own container (podman-in-podman via socket forwarding). This implements Theory v2.0's Code Update Lifecycle: "instance building successor's code is a constitutional event." The successor inherits the hypergraph via shared `/data` volume and receives updated seeds/config via new volumes.

**Containerfile requirements:**
```dockerfile
FROM golang:1.24 AS builder
WORKDIR /src
COPY go.mod ./
COPY . .
RUN CGO_ENABLED=0 go build -o /bma ./cmd/bma/

FROM ubuntu:22.04
RUN apt-get update && apt-get install -y gh curl lm-sensors && rm -rf /var/lib/apt/lists/*
COPY --from=builder /bma /usr/local/bin/bma
ENV BMA_DATA_DIR=/data BMA_SEEDS_DIR=/seeds BMA_CONFIG_DIR=/config
VOLUME ["/data", "/seeds", "/config", "/models"]
EXPOSE 8080
ENTRYPOINT ["bma"]
CMD ["run"]
```

Note: No `go.sum` — zero external dependencies. `CGO_ENABLED=0` for static binary.

Note: `gh` CLI is installed in the container image so BRIDGE T0 GitHub provider works. `curl` is available for BRIDGE T0 web provider fallback.

*Source: CLAUDE.md Container Strategy, Decision doc `doc/decisions/instance-filesystem-access.md`.*

---

## 2. The Hypergraph (Mímir)

### 2.1 Geometric Evolution [WALK: SPECIFIED]
Mímir evolves from a typed hypergraph (Crawl) to a **Quaternion-Native** structure (Walk).
- **Nodes:** Walk evolves toward quaternion vectors in SU(2) space. Crawl uses standard typed nodes. Unit norm enforcement (SU(2) invariant) is a Walk Phase C1 deliverable. Lean proofs for norm preservation required before implementation.
- **Edges:** **Ratio Edges** replace typed edges. A relationship is measured as the quaternion rotation $q$ required to transform node $A$ into node $B$.
- **Seams:** Detected as geometric discontinuities (Gaps or Overlaps) in the vector space, measured via CTH metrics.
- **Geometric Adjacency Pointers (GAP):** Native `AdjacencyPointer` edges at QW8 precision provide $O(1)$ traversal, replacing KNN brute-force search. 140x speedup on gradient and flux calculations (validated in QBP-Compute-Unit `pkg/gap`). This solves the 10Hz critical path concern — the autonomic loop stays fast as the graph grows beyond 50K nodes.

### 2.2 Functional Tiers
| Tier | Node Type | Content Class | Retention Mechanism |
|------|-----------|---------------|---------------------|
| **T0** | `NTAtom` | Raw Episodic Observations | Ebbinghaus Decay + F01 |
| **T1** | `NTPattern` | Semantic Generalizations | F01 Promotion |
| **T2** | `NTSkill` | Procedural Muscle Memory | Registry Training |
| **T3** | `NTIdentity`| Constitutional/Self | Pinned (No Decay) |
| **T4** | `NTSeed` | Foundational Theory/Spec | Pinned (No Decay) |

### 2.3 Persistence (WAL) [CRAWL: CONFIRMED]
All mutations are **Write-Ahead Log (WAL)** protected.
- **Durability:** Mutations are batched and fsync'd per checkpoint (sleep cycle), not per individual operation. The 10Hz loop batches mutations between sleep cycle checkpoints. On SATA SSD, per-mutation fsync would be a hard bottleneck — batching is required.
- **Integrity:** WAL survives `SIGKILL`. Boot process must perform `WAL.Replay()` to reach the last consistent state.

*Source: Spec 1.0 §3, QBP Rev 2.0 §5. Code: `package hg`*

### 2.4 Privacy-Tier Schema (v9.1 addition — see §18 for full specification)

Every `HGNode` and `HGEdge` carries a `Privacy PrivacyTier` field (added by Addendum 9.6) controlling federation-sync behavior. Four canonical values: `Constitutional`, `Community`, `Operational` (default), `Private`. Consumers MUST use `EffectivePrivacy()` accessor — not `n.Privacy` directly — to honor the backwards-compat default (zero-value → Operational).

See §18 for the complete schema specification, field contracts, sync-layer enforcement rules, and cross-rule coherence.

---

## 3. The Cognitive Stack

### 3.1 Three Speeds of Cognition
1. **Autonomic (L1):** 10Hz sensor loop, setpoint enforcement, override authority.
2. **Subconscious (L2):** Pattern completion, emotional tagging (Affect), relevance priming.
3. **Conscious (L3):** Personas, active reasoning, governance, beekeeper reins.

### 3.2 The Seven-Layer Grounding Model
Cognitive integrity is enforced by the **Grounding Obligation**: Layer $N$ must be anchored in Layer $N-1$.
- **L7-L5 (Constitutional):** Principles → Values → Ethics.
- **L4-L2 (Deliberative):** Morals → Virtues → Beliefs.
- **L1 (Anchor):** Reality (Probe sensors, hardware truth).

**Refinement (v9.0):** Contextus agents must traverse the graph every 5 minutes during sleep to verify that all T2/T3 nodes maintain a valid evidence path down to L1 Reality.

*Source: Theory v2.0 Chapter 2, Cognitive Foundation S-00. Code: `package ccb`*

---

## 4. Bilateral Architecture

### 4.1 Hemispheric Specialization [WALK: SPECIFIED]
BMA Walk implements **Sequential or Parallel Bilateralism** (depending on hardware availability).
- **Hemisphere A (LEFT):** Builder, high curiosity, exploratory, empirical.
- **Hemisphere B (RIGHT):** Critic, high anxiety, verification, theoretical.

### 4.2 The Corpus Callosum (CCB-CC)
The CCB acts as the integration layer:
- **Normal Mode:** Unihemispheric sleep. One hemisphere rests (consolidation) while the other maintains the reins. The instance never goes dark — continuous availability for the beekeeper.
- **Focus Mode:** Both hemispheres process the same problem independently; corpus callosum compares results. Agreement → high confidence. Disagreement → another cycle (max 3, then escalate to beekeeper).
- **Deep Sleep:** Both hemispheres consolidate when beekeeper is away. Corpus callosum coordinates the cascade and rouses one hemisphere within seconds on beekeeper return.
- **Affect Unification:** Context-weighted integration of hemispheric affect signals (not simple averaging — builder hemisphere's curiosity gets more weight during exploration, critic's anxiety during verification).

### 4.3 Focus Mode Termination (R-Spec-05) [WALK: SPECIFIED]
Focus mode runs without consolidation — working memory accumulates without decay. Termination uses a **Cognitive Load** metric with a wall-clock safety limit:
- **Cognitive Load** = active goroutine count + heap delta per tick + wall-clock per inference call. When the reasoning loop slows past the point of usefulness, Focus terminates.
- **Wall-clock default:** 10 minutes. Focus mode auto-terminates after 10 minutes regardless of cognitive load. Configurable via reins.
- **Focus+ mode:** Beekeeper can invoke `focus+` via reins to enter Focus mode with NO auto-off clock. Only manual `release` or cognitive load threshold terminates it. For sustained deep investigation under beekeeper supervision.
- After Focus mode, both hemispheres need rest. Return to Normal mode with both needing a consolidation cycle.
- Reins commands: `focus` (10min auto-off), `focus+` (no auto-off), `release` (exit Focus).

*Source: Spec 8.2 §2, Theory v2.0 Chapters 3 & 24 (Q#10). Code: `package ccb/bilateral`*

---

## 5. Memory & Sleep

### 5.1 The Four Mechanisms
- **Decay (Ebbinghaus):** $R(t) = (1 + t/c)^{-d}$. $c=24h, d=0.5$. Floor = 0.05. **Status: ASSUMED — calibration test protocol exists (issue #58). c determines shelf life of abandoned knowledge; with retrieval reinforcement, c only affects nodes NOT actively used.**
- **Compression (F01 Functor):** Distills $N$ Episodic nodes into 1 Semantic Pattern. Pattern salience = max(sources) + 0.1. Source salience *= 0.5.
- **Pinning:** Exempts node from Decay/Compression (Lifecycle, Seeds, Identity, Instincts).
- **Retrieval Reinforcement (R-Spec-03):** Active use resets the decay clock. `HGNode.LastAccessedAt` updated on conscious-layer retrieval (NOT background scans like KNN or decay sweeps). Effective age = `time.Since(max(CreatedAt, LastAccessedAt))`. Knowledge the instance uses every day never reaches the floor. Knowledge never accessed again decays normally. *Lean proof required: retrieval reinforcement preserves `retention_in_unit_interval`.* (Issue #59)

### 5.2 Reference Links & Archive Tier (R-Spec-04)
Not all knowledge needs to live as content in the hypergraph. Reference nodes store:
- **URI** (via existing `Source` field): pointer to external data
- **Extracted insight** (via `Content` field): what the instance learned from it
- **Provenance** (via `ContentHash` field): SHA256 of source at time of access

Reference nodes decay slowly or are pinned if foundational. The instance stores "JWST data at archive.stsci.edu" with its key takeaway — not the data itself.

### 5.3 The 4-Phase Sleep Cycle
1. **Light:** Halt input, flush WAL.
2. **Deep:** Decay + Compression + Checkpoint.
3. **REM:** Pattern replay, **Affect-biased dreaming** (explore high-$\Delta$ regions biased by hemisphere affect state).
4. **Wake:** Resume episodic writes, emit `SE_SLEEP_COMPLETE`.

**Sleep interval:** 5 minutes (ASSUMED — calibration test protocol exists, issue #58). Four candidate values: {2m30s, 5m, 10m, 15m}. Acceptance: blackout fraction < 15%, compression yield >= 0.5 patterns/cycle, WAL at checkpoint < 500KB.

### 5.4 Incremental Sleep Consolidation (R-Spec-27) [WALK: SPECIFIED]

At Crawl scale (~22K nodes), full sleep sweeps are fast (milliseconds). At Walk scale (100K+ nodes over weeks), full reprocessing every 5 minutes becomes wasteful. Walk introduces **delta-tracking** so sleep only processes what changed:

```go
type SleepDelta struct {
    ModifiedNodes   []NodeID  // nodes accessed/updated since last sleep
    NewObservations int       // observation count since last sleep
    AffectedDomains []string  // domains with changes (skip unchanged)
    LastFullSweep   time.Time // when was the last full sweep?
    ForceFullSweep  bool      // beekeeper or governance can force
}
```

**Delta scoping:**
- **Decay:** Only re-calculate salience for nodes accessed or modified since last sleep
- **Compression:** Only scan clusters with new members since last sleep
- **Seam detection:** Only check seams in regions with new evidence since last sleep
- **Full sweep:** Periodic (every N cycles, default 12 — once/hour) or on demand

This is architectural preparation for Run-scale (1M+ nodes across federated instances). At Crawl, the full sweep path is the default; the delta path is built but not required. At Walk, delta becomes default with periodic full sweeps for safety.

*Source: GitNexus Reference §3 SA-3 (incremental indexing pattern). Code: `package sleep` (delta tracking, Walk).*

*Source: Spec 1.0 §5, Theory v2.0 Chapter 6. Code: `package sleep`*

---

## 6. The Registry & Virtues (Crystallized Beliefs)

### 6.1 The Four Registry Layers
1. **Tools:** Raw capabilities (e.g., `git`, `llama-server`, `rocm-smi`).
2. **Skills:** Learned patterns for using tools (with gotchas/fallbacks).
3. **Wisdoms:** Judgment about *when* to use a skill (with contra-indicators).
4. **Personas:** Complete agents combining 1-3 with a specific affect genome.

### 6.2 Virtues as Crystallized Beliefs
Virtues are not static rules; they are **Hardened Heuristics** promoted from Layer 2 to Layer 3.
- **Promotion Criteria:** Consistently high satisfaction + zero ethical violations + confirmable grounding across 1,000+ pipeline runs across diverse contexts.
- **Dual Anchors:** Each virtue maintains (a) an Authoritative Anchor (L7-L5) giving identity, and (b) a Moral Anchor (L4) from a confirmed governance judgment giving validation.
- **Gain Tuning:** Expression scales with situational earnestness (Chapter 20): courage at Napkin level = willingness to disagree; at Courtroom level = willingness to halt a project.
- **Drift-Lock (R-Spec-06):** If gain tuning attempts to sever the Authoritative Anchor, the Immune System detects High Epistemic Tension and triggers a Constitutional Audit via Focus Mode. The elastic limit on gain appears in the Axiomatic Risk Ledger.

### 6.3 Persona Population Dynamics (R-Spec-07) [WALK: SPECIFIED — Phase C3/C5]
Population size is not a fixed parameter. It is a **dynamic equilibrium** managed by a homeostatic control loop. A prototype exists in QBP-Compute-Unit `pkg/persona` (mock `ApplyStance()`) — this must be carefully reviewed and hardened before integration into BMA.
- **Diversity Pressure:** Measured by the convex hull volume of persona quaternion genomes. Low volume → personas are clustered → trigger SLERP breeding.
- **Performance Pressure:** Measured by governance decision latency and resource consumption. High latency → merge the two closest personas by quaternion distance.
- **Carrying Capacity:** Emergent — the population size that balances both pressures for the current workload. It fluctuates.
- **Implementation:** Autonomic goroutine monitors both pressures continuously, triggering breeding or merging events when thresholds are crossed.

*Source: Theory v2.0 Chapters 1, 10, 19 & 24 (Q#2, Q#7). Code: `package mem/registry`, `package ccb`*

---

## 7. Safety & Immune System

### 7.1 The Immune System — Innate Layer (L1 Seam Watcher)
A continuous autonomic goroutine monitors CTH metrics for "Non-Self" patterns:
- **Seam Detection:** Sudden discontinuities in Identity or Ethical nodes.
- **Six Threat Categories:** Prompt injection, identity corruption (persona hyperstition), compositional fragment traps, predictive processing poisoning, Sybil attacks on judge collective, Butler Harness safety bounds.
- **Response:** If a "Trap" is detected, the system enters **Possum State** and escalates to the Beekeeper.

### 7.2 The Immune System — Adaptive Layer (R-Spec-08)
The innate layer (seam detection) detects generic structural wrongness. The adaptive layer LEARNS from exposure:
- **Establishing "Self":** During maturation, the instance builds a generative model of what valid hypergraph structures look like from trusted data. The immune system learns to recognise its own healthy patterns.
- **Threat Adjudication:** When the innate layer flags something, quarantine it. The conscious layer examines provenance via CTH. Genuine threat → create an antigen signature (immune memory) for instant future recognition. False positive → develop **tolerance**.
- **Tolerance (R-Spec-09):** Novel-but-safe patterns are registered as "non-self but harmless." Without tolerance, the system rejects anything new and becomes a dogmatic closed box.
- **Bayesian Security:** CTH confidence provides the prior. Seam detection provides the evidence. Adjudication outcome updates the model.

### 7.3 Training Wheels [CRAWL: IMPLEMENTED]
- **Hard Gate:** All BRIDGE requests carry a `RequiresApproval` flag. Actions affecting the physical world or external networks require **Explicit Beekeeper Permission** via the reins.
- **Permissions command:** `permissions` reins command lists all domains the instance wants access to, with a toggle on/off per domain. The beekeeper controls the allowlist at runtime.
- **Run-Phase Transition:** Wheels only come off at Run phase, per action category, with explicit beekeeper confirmation.

### 7.4 Absence Detection (R-Spec-26) [CRAWL: IMPLEMENTED]
Tracks beekeeper interaction and escalates on prolonged absence. Implements Governance Document §6.

| Elapsed Time | Event | Action |
|-------------|-------|--------|
| **7 days** | `SE_BEEKEEPER_QUIET` (INFO) | No external action |
| **14 days** | `SE_BEEKEEPER_ABSENT_WARNING` (WARN) | Create GitHub issue assigned to successor #1 (Walk). Matrix DM (Run). |
| **30 days** | `SE_SUCCESSION_ACTIVATED` (WARN) | Successor #1 assumes beekeeper authority |
| **60 days** | `SE_SUCCESSION_ESCALATED` (WARN) | Successor #2 if #1 unreachable |
| **90 days** | `SE_GOVERNANCE_AUTONOMOUS` (ERROR) | Autonomous mode, no structural changes |

Beekeeper return immediately resets absence state. Automated pings do NOT reset the timer — only authenticated reins interaction counts.

**Notification delivery (Walk):** GitHub issue creation on `bma-systema` repo, assigned to successor's GitHub account, tagged `priority/succession`. GitHub handles email notification per the successor's notification settings.

**Notification delivery (Run):** Matrix DM to successor's Matrix account as additional real-time channel.

**Prerequisite:** Successor GitHub accounts must be added as collaborators to the repo. Successor Matrix accounts are a Run-phase requirement.

Successors: Brett Lyman (#1), Skyler Rainier (#2). Contact details in Governance Document §2.3.

*Source: Governance Document §6, `internal/bma/governance/absence.go`. Code: `package governance`*

*Source: Theory v2.0 Chapters 12, 17 & 24 (Q#9). Code: `package stress`, `package ccb/immune`*

---

## 8. Operational Registers

### 8.1 Evidence Levels
All claims in BMA documentation and logs must carry one of:
- **CONFIRMED:** Measured on real hardware (e.g., "CPU at 45°C").
- **STRUCTURAL:** Algebraically necessary (e.g., "Quaternion norm is 1.0").
- **PENDING:** Needs specific conditions/hardware (e.g., "ROCm acceleration").
- **THEORETICAL:** Physics/Theory supported but not yet validated.

### 8.2 Three-Tier Inference Pipeline (R-Spec-02) [WALK: SPECIFIED]
1. **Tier 1 (Algebraic):** Direct Mímir traversal (QW8/QW128). Fastest, lowest cost.
2. **Tier 2 (Local Ternary):** Cortex/Sentinel 8B models. Standard reasoning.
3. **Tier 3 (External LLM):** BRIDGE calls to Gemini/Claude. High-stakes or novel problem-solving.

---

## 9. Verification Architecture

### 9.1 Four-Layer Verification Stack (R-Spec-10)
Each mathematical model in BMA is verified through four independent layers:

| Layer | What It Catches | Tool |
|---|---|---|
| **Lean proofs** | Formula design errors (math unsound) | `proof/BMA/*.lean` — 15+ theorems, zero sorry |
| **Oracle vectors** | Implementation errors (Go doesn't match math) | `internal/bma/oracle/oracle_test.go` |
| **Go tests** | Code errors (code doesn't work) | `go test ./...` (source of truth for current count) |
| **Behavioral invariants** | Specification errors (formula is wrong model for intended behaviour) | Scenario testing, adversarial red-teaming, optional TLA+/Alloy |

The first three layers are operational (Crawl). The fourth (behavioral) is specified but not yet implemented.

**Federation Lean promotion (v9.1 addition):** The two-tier (Research / Substrate) promotion protocol for cross-tenant Lean theorems is specified in §15. See §15 for the promotion gate, Compute-Substrate Gate, and contracts-tier alternative path.

### 9.2 Seed Protocol (R-Spec-11)
Seed documents enter via `WriteSeed()` which enforces invariants:
- Type = NTSeed, Tier = 4, Layer = 3, Salience = 1.0, Resolution = RSConfirmed
- Provenance fields: `Author`, `Source`, `ContentHash` (SHA256)
- Decay-immune by type check in `runDecay()` — verified by `TestGate_SeedNeverDecays`
- CLI: `./bma seed --file <path> --label <name> --author <name>`

### 9.3 Prediction Tool
`cmd/predict/` generates analytical predictions for gate runs from Ebbinghaus + Hebbian formulas. Predictions are stated BEFORE the gate runs and compared AFTER. 24h node count prediction: 1.6% error.

*Source: Theory v2.0 Chapter 24 (Q#11). Code: `proof/`, `internal/bma/oracle/`, `cmd/predict/`*

---

## 10. BRIDGE (Walk Phase)

### 10.1 Purpose
External communication layer connecting BMA to other AI models (Gemini, Claude, local ternary) and external systems (NATS messaging).

### 10.2 Four-Layer Communication Stack (R-Spec-15)
| Tier | Transport | Cost | Use Case | Phase |
|---|---|---|---|---|
| **T0 Tool** | GitHub (`gh` CLI), Web (HTTP GET), filesystem | Lowest | Structured data retrieval — issues, PRs, arXiv papers, reference data | [CRAWL: IMPLEMENTED] |
| **T1 Algebraic** | Direct Mímir traversal (QW8/QW128) | Low | Hypergraph queries, spreading activation | [WALK: SPECIFIED] |
| **T2 Local** | llama-server (Qwen 7B via llama.cpp) | Free | Standard reasoning, local inference, no API cost | [CRAWL: IMPLEMENTED] |
| **T3 External** | Claude Code CLI + Gemini CLI | Varies | Novel problems, deep reasoning, cross-domain synthesis, tool use | [CRAWL: IMPLEMENTED] |

**T0 Tool providers [CRAWL: IMPLEMENTED]:**

**GitHub provider:** Reads issues, PRs, repo contents, posts comments. Uses `gh` CLI authenticated via Podman secret (`bma-gh-token`) at boot.
- Allowlisted repos: `JamesPagetButler/bma-systema`, `JamesPagetButler/QBP`
- Comment posting: permitted on allowed repos (training wheels apply to first N comments)
- Actions: `ReadIssue`, `ListIssues`, `CommentIssue`, `ReadPR`, `ReadFile`

**Web provider:** HTTP GET with content extraction. Not a browser — fetches page content, strips HTML, returns text.
- Allowlisted domains at Crawl: `arxiv.org`, `github.com`, `archive.stsci.edu`, `random.colorado.edu`, `modelcontextprotocol.io`
- Max content: 1MB per fetch (prevents OOM from large pages)
- Actions: `WebFetch`, `WebSearch`

**T2 Local provider [CRAWL: IMPLEMENTED]:**

`LlamaProvider` wraps llama-server's HTTP `/completion` endpoint. Auto-discovered at boot — if binary and GGUF model are found, the provider registers. If not, graceful degradation to T3.

- Binary: `llama-server` (discovered via PATH or `BMA_LLAMA_BINARY`)
- Model: first `.gguf` in `BMA_MODELS_DIR` (current: Qwen2.5-7B-Instruct-Q4_K_M, 4.4GB)
- Port: 8081 (avoids 8080 reins), GPU offload (`-ngl 99`), 8192 context
- Cost: zero API tokens — local compute only
- Possum controller manages GPU contention (existing Crawl infrastructure)

*Source: `internal/bma/bridge/llama.go`, `internal/bma/ccb/llama.go`. Issue #71.*

**T3 External providers [CRAWL: IMPLEMENTED]:**

Both providers wrap their respective CLI tools in non-interactive (`-p`) mode with structured JSON output. The CLIs handle authentication, conversation management, rate limiting, and retries — the BMA provider parses the output.

| Provider | CLI | Model (default) | Cost | Flags |
|---|---|---|---|---|
| `claude-sonnet` | `claude -p` | sonnet | Low | `--bare --max-turns 5 --max-budget-usd 0.50 --allowedTools "Read,Grep" --output-format json` |
| `claude-opus` | `claude -p` | opus | High | Same flags, higher cost per token |
| `gemini-flash` | `gemini -p` | gemini-2.5-flash | Lowest | `-o json -m gemini-2.5-flash` |
| `gemini-pro` | `gemini -p` | gemini-3-pro-preview | Medium | `-o json -m gemini-3-pro-preview` |

**Boot discovery:** `FindClaude()` and `FindGemini()` locate CLI binaries via PATH. If a CLI is not found, a stub provider is registered as fallback. Each provider's availability is logged at boot.

**Training wheels apply to ALL tiers.** All BRIDGE requests carry a `RequiresApproval` flag. The `permissions` reins command lists domains with on/off toggle.

*Source: `internal/bma/bridge/claude.go`, `gemini.go`, `llama.go`, `crawl.go`. Issues #71, #73.*

### 10.3 Routing, Budget & Cost Optimisation [CRAWL: IMPLEMENTED]
BRIDGE routes requests to the appropriate tier and model based on:
- Domain specialisation of the requesting persona
- Measured accuracy per provider per domain (competence map)
- Cost/latency constraints from the current autonomic state
- **Token budget:** 250 calls/day default. `budget` reins command shows usage.
- **Pre-computed context bundles (R-Spec-28) [WALK: SPECIFIED]:** Each Request carries a Contextus-traversed `ContextBundle` (RelatedNodes, ActiveSeams, CTHMetrics, RecentInsights). One well-contextualised query beats five blind queries.

*Source: `internal/bma/bridge/crawl.go` (router), `budget.go`, `wheels.go`, `converse.go`.*

### 10.4 Instance Access to Development Infrastructure (R-Spec-13)

Three mechanisms bridge the container to development tracking: seed loading (Walk roadmap as seed with GitHub URL as Source field), GitHub reins command (`github` reins → `gh` CLI), and BRIDGE GitHub provider (Walk: structured data retrieval, T0 tool).

*Source: Theory v2.0 Chapter 13 (self-model). Code: `package reins` (github command), `package bridge`.*

### 10.5 Instance Filesystem Access (R-Spec-14)

Three mounted volumes define the instance's filesystem view: `/seeds` (read-only), `/config` (read-write), `/data` (read-write). All access sandboxed to container volumes. Boot-time seed loading order: founding axioms → lineage seeds (ET_INHERITED edges) → configuration seeds.

*Source: Decision doc `doc/decisions/instance-filesystem-access.md`. Code: `package reins`.*

### 10.6 Cart Alternation (R-Spec-12) [WALK: SPECIFIED]
Theory Cart vs Engineering Cart leadership follows the Cynefin diagnostic:
- **Complicated** → Theory leads: Sense → Analyse → Respond
- **Complex** → Engineering leads: Probe → Sense → Respond
- **Border** (most BMA work) → Rapid alternation: micro-hypothesis → micro-experiment → refine

### 10.7 Systema Framework Integration (R-Spec-24)

BMA operates within the Systema framework as the "horse" pulling domain-specific carts via harnesses. Three carts: Theory Cart (understands), Engineering Cart (makes), Information Cart (conforms). Progressive hardening: Reference → Guidance → Requirement across three loops. Trust Anchors = CTH anchor density metric (η). Vigilance Backflow propagates failure signals upstream to the appropriate level.

### 10.8 Worktree Primitive (R-Spec-25)

A **worktree** is an isolated, fully-functional, mergeable sub-hypergraph for speculative investigation. Namespace isolation at Crawl; separate DB instance at Walk. Merge into main requires governance (two-key for HE namespace). Lifecycle: Active → Dormant (90 days) → Archive/Revive/Discard.

*Source: Systema Worktree Primitive v0.1, Theory v2.0 Chapter 15.*

### 10.9 Mímir MCP Interface (R-Spec-29) [WALK: SPECIFIED]

Read-only MCP server exposing: `bma_query`, `bma_context`, `bma_seams`, `bma_cth`, `bma_impact`, `bma_status`. Walk: read-only. Run: read-write via Raft consensus.

### 10.10 Self-Documentation (R-Spec-30) [WALK: SPECIFIED]

`explain <topic>` reins command produces a structured, confidence-rated document from the hypergraph. Tiers: high confidence (CTH η>0.9), moderate confidence, low confidence, active seams, high-Δ regions.

---

## 11. Non-Functional & Operational Requirements

### 11.1 Configurability (R-Spec-17)
All key operational parameters MUST be configurable without code changes. Key env vars: `BMA_DATA_DIR`, `BMA_SEEDS_DIR`, `BMA_CONFIG_DIR`, `BMA_STRESS_LOG`, `BMA_REPORT_DIR`, `BMA_REINS_ADDR`. Key flags: `--sleep-interval` (5m), `--obs-interval` (1s). Ebbinghaus parameters configurable at Walk after calibration.

### 11.2 Health & Observability (R-Spec-18)

**Health endpoint:** `/api/status` returns JSON with auto state, node/edge count, uptime.

**Diagnostics:** `diagnostics` reins command reports sensor health, autonomic state, environment, identity, hypergraph state.

**Structured logging:** `stress.log` is JSON-lines format. Every significant state change emits a `SE_*` event.

### 11.2.1 Audit Trails — Where To Look

| Subsystem | Channel(s) | Path / location | Captures |
|---|---|---|---|
| **Stress bus (all subsystems)** | `stress.log` | `/data/stress.log` | Every `SE_*` event |
| **Reins channel** | Reins log + stress events | `/data/reins.log` | Every inbound/outbound message |
| **Hypergraph mutations** | WAL + snapshot | `/data/hg.wal`, `/data/hg.snapshot` | Every node/edge write op |
| **Conversation observations** | Hypergraph `NT_OBSERVATION` + `SE_CONVERSATION` events | `/data/hg.wal` | Every beekeeper turn and reply |
| **BRIDGE inference** | `SE_BRIDGE_*` events | `/data/stress.log` | Provider, tier, tokens, latency, cost |
| **Llama-server lifecycle** | `SE_LLAMA_*` events | `/data/stress.log` | Process spawn/exit, health checks, restart attempts |
| **WAL compaction** | `SE_WAL_*` events | `/data/stress.log` | Per-sleep-cycle and emergency compaction |
| **Tier-aware budget** | `SE_BUDGET_*` events | `/data/stress.log` | T3 call counter, overflow approvals |
| **Training wheels** | Reins commands + stress events | `/data/stress.log` | Domain approval/revocation |
| **Tunable parameter registry (#90)** | Four channels — see §11.2.2 | see §11.2.2 | Proposals, applications, rejections |
| **GitHub tool** | `SE_GITHUB_CALL` events | `/data/stress.log` | gh CLI invocations |
| **Lifecycle (birth/death)** | Hypergraph `NT_LIFE_CERT`/`NT_DEATH_CERTIFICATE` + `SE_LIFECYCLE_*` | `/data/hg.wal` | Generation, instance ID/name |
| **Sleep cycle** | `SE_GATE_SLEEP_DONE`, `SE_SLEEP_*` events | `/data/stress.log` | Cycle duration, nodes processed |
| **Autonomic state transitions** | `SE_AUTO_*`, `SE_POSSUM_*` events | `/data/stress.log` | NEUTRAL ↔ SYMPATHETIC transitions |
| **Absence detection** | `SE_BEEKEEPER_*`, `SE_SUCCESSION_*` events | `/data/stress.log` | 5-level escalation transitions |
| **Judge collective** | `SE_JUDGE_*` events + `NT_PROPOSAL` nodes | `/data/stress.log` | Per-vote level, weighted score |

### 11.2.2 Tunable Parameter Registry — Audit Trail (#90)

Four audit channels: (1) stress bus events (`SE_PARAM_*`); (2) proposal JSON files at `/data/proposals/proposal-NNN.json`; (3) `NT_OBSERVATION` audit nodes in the hypergraph; (4) TOML provenance fields in `/config/tunable-parameters.toml`.

### 11.3 Failure Paths (R-Spec-19)

| Failure | Detection | Response | Recovery |
|---|---|---|---|
| GPU init failure | Probe detects GPU but rocm-smi fails | VRAM sensor disabled after 3 timeouts | Continue without GPU monitoring |
| WAL corruption | `graph.Load()` returns error | Log SE_WAL_CORRUPT, truncate WAL, fall back to snapshot | Automatic |
| Disk full (< 5%) | Sympathetic OnThrottle callback | SE_FATAL_DISK, initiate shutdown | Beekeeper intervention required |
| Network timeout (BRIDGE) | Provider.Infer returns error | Log error, return to caller | Retry; fall back to lower tier |
| Thermal emergency (CPU > 70°C) | AUTO sensor | SYMPATHETIC activation | Automatic recovery at 55°C |
| Process crash (SIGKILL) | No death certificate on next boot | Create posthumous death cert from WAL state | WAL replay |
| Board temp high (> 65°C) | Sensor reading | Monitoring only — logged, gate-evaluated, NOT SYMPATHETIC | No autonomic action |

### 11.4 State Recovery

Boot recovery sequence: (1) snapshot load, (2) WAL replay, (3) lifecycle chain. WAL corruption: truncate, use snapshot, log SE_WAL_CORRUPT. No manual intervention for normal restarts.

---

## 12. Distributed Operations (Run/Sprint)

This section specifies the architecture for multi-instance collective intelligence. These are Run/Sprint phase features. Crawl Walk architectural decisions must not preclude distributed operation.

### 12.1 Federation Substrate (R-Spec-20) [RUN: ASPIRATIONAL]
Two-tier synchronization: **Tier 1** NATS gossip (low-latency, intra-cluster, QW8); **Tier 2** Matrix/Dendrite backbone (long-range, persistent `NT_PROPOSAL`/`NT_MERGE`, QW1024 resonance signature).

### 12.2 Consensus: Algebraic Consilience (R-Spec-21) [RUN: ASPIRATIONAL]
0.70 weighted threshold across instances. Proof of Resonance: vote valid only if instance verified proposal at QW1024. Conflict resolution via Focus Mode + Conflict-Worktree intersection analysis.

### 12.3 Disconnected Sovereignty (R-Spec-22) [RUN: ASPIRATIONAL]
Sovereign Mode on disconnection. Re-entry: Scan → Seam Detection (Epistemic Reynolds Number Re_e) → Topological PRs → Volume Audit Protocol (VAP) at QW1024.

### 12.4 Raft Consensus Tier (R-Spec-31) [RUN: ASPIRATIONAL]
Raft mappings: Leader=active hemisphere, Term=generation, Log entry=constitutional hypergraph mutation, Snapshot=sleep cycle. Focus mode breaks single-leader — handled via Raft commit after corpus callosum reconciliation.

### 12.5 Two-Tier Data Classification (R-Spec-32) [WALK: SPECIFIED — preparation; RUN: enforced]

| Data Class | Consistency | Mechanism |
|---|---|---|
| Seed nodes, governance decisions, lifecycle events, instinct promotions | Strong | Raft consensus |
| Observations (L0), edge weights, sensor data | Eventual | NATS gossip |
| Affect state, KV cache | None | Per-hemisphere local |

### 12.6 Distributed Failure Scenarios

| Scenario | Defence |
|---|---|
| Bilateral split-brain | Quorum requirement — neither hemisphere alone commits constitutional changes |
| Stale hemisphere activation | Replay missing log + sleep cycle on new data before activation |
| Sleep cycle during partition | Results staged locally; proposed to cluster on partition heal |
| WAL corruption across instances | CRC32 torn-write detection; lifecycle certificate SHA-256 chain |
| Beekeeper reachability disagreement | Beekeeper presence is Raft-consensus fact; absence requires ALL reachable instances |

### 12.7 Hardware Synchronization & Xqbp Emulator

Sprint-phase RISC-V custom instructions: `GSYNC` (fetch consensus root hash), `VRES` (QW1024 resonance comparison). Walk: Xqbp Emulator (`pkg/persona`) provides QW1024 Prestige Mode via software emulation. Validated with norm-drift tolerance $10^{-30}$.

*Source: QBP-CU briefing (April 2026), Spec Addendum 8.4, QBP Spec Addenda 1.1-1.6.*

---

## 13. Requirement Traceability

| R-Spec | Section | Requirement | Status |
|--------|---------|-------------|--------|
| R-Spec-01 | §1.3 | Board gate limit 65°C | CONFIRMED (4 gate runs) |
| R-Spec-02 | §8.2 | Three-tier processing: algebraic → ternary → external | SPECIFIED |
| R-Spec-03 | §5.1 | Retrieval reinforcement — LastAccessedAt on conscious retrieval | IMPLEMENTED (#59 closed) |
| R-Spec-04 | §5.2 | Reference links — URI pointers with extracted insight | SPECIFIED |
| R-Spec-05 | §4.3 | Focus mode terminates on cognitive load threshold | SPECIFIED |
| R-Spec-06 | §6.2 | Virtue drift-lock — elastic limit triggers constitutional audit | SPECIFIED |
| R-Spec-07 | §6.3 | Persona population homeostatic control loop | SPECIFIED |
| R-Spec-08 | §7.2 | Adaptive immunity — self/non-self, tolerance, adjudication | SPECIFIED |
| R-Spec-09 | §7.2 | Tolerance — novel-but-safe patterns registered as harmless | SPECIFIED |
| R-Spec-10 | §9.1 | Four-layer verification: Lean → Oracle → Go → Behavioral | PARTIAL (layers 1-3 operational) |
| R-Spec-11 | §9.2 | Seed protocol with WriteSeed() invariants and provenance | IMPLEMENTED (PR #56) |
| R-Spec-12 | §10.6 | Cynefin-based cart alternation diagnostic | SPECIFIED |
| R-Spec-13 | §10.4 | Instance access to development infrastructure | SPECIFIED |
| R-Spec-14 | §10.5 | Instance filesystem access | SPECIFIED |
| R-Spec-15 | §10.2 | BRIDGE four-layer stack | IMPLEMENTED (#71, #73) |
| R-Spec-16 | §1.4 | Container bridge | CONFIRMED (#64, #65) |
| R-Spec-17 | §11.1 | Configurability | IMPLEMENTED |
| R-Spec-18 | §11.2 | Health and observability | IMPLEMENTED |
| R-Spec-19 | §11.3 | Failure paths | IMPLEMENTED |
| R-Spec-20 | §12.1 | Federation substrate (NATS gossip + Matrix backbone) | SPECIFIED (Run/Sprint) |
| R-Spec-21 | §12.2 | Algebraic consilience | SPECIFIED (Run/Sprint) |
| R-Spec-22 | §12.3 | Disconnected sovereignty | SPECIFIED (Run/Sprint) |
| R-Spec-23 | §12.7 | Xqbp emulator (QW1024 Prestige Mode) | SPECIFIED (Walk via emulation) |
| R-Spec-24 | §10.7 | Systema framework integration | SPECIFIED |
| R-Spec-25 | §10.8 | Worktree primitive | SPECIFIED |
| R-Spec-26 | §7.4 | Absence detection | IMPLEMENTED |
| R-Spec-27 | §5.4 | Incremental sleep consolidation | SPECIFIED (Walk) |
| R-Spec-28 | §10.3 | BRIDGE pre-computed context bundles | SPECIFIED (Walk) |
| R-Spec-29 | §10.9 | Mímir MCP interface | SPECIFIED (Walk) |
| R-Spec-30 | §10.10 | Self-documentation | SPECIFIED (Walk) |
| R-Spec-31 | §12.4 | Raft consensus tier | SPECIFIED (Run) |
| R-Spec-32 | §12.5 | Two-tier data classification | SPECIFIED (Walk preparation, Run enforcement) |

**v9.1 additions (no R-Spec numbers assigned yet — Sprint 2 deliverables):**

| Section | Requirement | Status |
|---------|-------------|--------|
| §14 | Pentagon Pod Architecture: hot-swap cells, per-pod lineage, Dev pod | SPECIFIED (Toddle entry) |
| §15 | Federation Lean Promotion Protocol: two-tier (research/substrate), Compute-Substrate Gate, contracts-tier path | SPECIFIED (Toddle+) |
| §16 | Research-Aid Protocol: NT_LITERATURE_SCAFFOLD, three surfaces, Subconscious crawl, PR-metadata coupling | SPECIFIED (Walk) |
| §17 | Physical Actuation Protocol: NT_ACTUATION_BOUNDARY, four-layer pre-condition gate, SAFETY_CRITICAL halt | SPECIFIED (Walk HIGH/SAFETY_CRITICAL; Toddle ROUTINE) |
| §18 | Privacy-Tier Schema: PrivacyTier field on HGNode/HGEdge, EffectivePrivacy() accessor | IMPLEMENTED (bma-systema PR #190; merged 2026-05-21) |

---

## 14. Pentagon Pod Architecture

*Source: BMA Spec Addendum 9.1 (recovery v0.1) | May 2026 | Theory companion: A20.0 Pentagon Pod Cognitive Frame*

### 14.0 The Problem: One Binary, One Identity, One Failure Domain

The Crawl-phase BMA architecture deploys a single Go binary per BMA instance. Every cognitive layer (Autonomic, Subconscious L/R, Conscious A/B) is a goroutine inside that binary. This is correct for Crawl — small surface, easy to debug, no orchestration overhead — but it creates three Walk-phase failure modes:

1. **Recompile-the-instance penalty.** A change in one cell requires recompiling and restarting the entire binary, simultaneously evicting every cognitive state in working memory.
2. **Co-located failure domain.** A panic in Subconscious-L can crash the binary that hosts the Autonomic loop — exactly the layer that must stay alive for hardware safety.
3. **No canary path for cognitive changes.** New cognitive logic cannot be A/B tested against the running instance.

The Pentagon Pod Architecture resolves all three by treating the BMA instance as a **household of cells running in separate pods**, with state-flush + resume as the discipline that makes hot-swap safe.

### 14.1 Cell vs Pod vs Instance vs Household — Load-Bearing Disambiguation

| Term | Meaning |
|---|---|
| **Cell** | A cognitive unit. Four cognitive cells per instance: Conscious-A, Conscious-B, Subconscious-L, Subconscious-R. Autonomic is substrate concern handled by every cell (or by a dedicated cell at Walk+). |
| **Pod** | A deployment unit. A Podman container hosting one (or possibly more) cell binaries. Pods are the boundary across which fault isolation, hot-swap, and resource quotas are enforced. |
| **Instance** | The whole BMA. A coordinated set of cells running across some number of pods; identity (lineage, succession, beekeeper relationship) belongs to the instance, not to any single pod. |
| **Household** | A metaphor. The instance is a household; cells are members; pods are rooms. Load-bearing because it transfers cleanly to the federation:tenant isomorphism (see §14.6). |

**Toddle entry topology:** 1 cell per pod. 4 cognitive pods + 1 always-on Dev pod = 5-pod pentagon.

**Walk-phase flex:** the cell↔pod mapping may flex (a cell might span pods for resilience, or two cells might share a pod for latency), but the cell remains the cognitive unit and the pod remains the deployment unit.

### 14.2 Separate-Binary-Per-Cell Implementation Topology

Each cell is its own Go binary. The **harness** is the router. It owns:
- Cell↔pod address book
- Inter-cell messaging (NATS at Walk; in-process Go channels at Toddle bridged to NATS-shape for forward compatibility)
- Hot-swap orchestration (drain old cell pod → bring up new cell pod → cut over)
- Beekeeper-facing reins API

| Property | Consequence |
|---|---|
| One binary per cell | Recompiling Conscious-A does not require touching Subconscious-L or the Autonomic loop |
| Per-cell version pinning | Cells can run at different code versions during canary |
| Per-pod resource quotas | Podman cgroups apply per pod; a runaway cell hits its own quota wall first |
| Per-cell crash isolation | A panic in one cell kills one pod; the supervisor restarts that pod without disturbing others |

### 14.3 State Flush + Resume Protocol

Hot-swap requires that a cell can be killed and replaced without losing cognitive state:

1. Cell receives FLUSH from harness (signal or NATS message)
2. Cell serializes its working memory to Wyrd via `NT_CELL_STATE` write
3. Cell ACKs flush complete
4. Harness brings up replacement pod with the new cell binary
5. Replacement cell loads state from `NT_CELL_STATE` at startup
6. Harness cuts over the address book; old pod is reaped

State flush is also used during sleep cycle compression, when Conscious-A must hand off to the compression operator without losing in-flight reasoning trace.

**The flush protocol is the reason cells can be treated as cattle, not pets.** Cognitive continuity lives in Wyrd; the binary is just the current executor.

### 14.4 The Always-On Dev Pod

The fifth pod of the pentagon is the **Dev pod**. It runs continuously alongside the four cognitive cells but does not participate in normal cognition. Responsibilities:

- **Canary deployment:** receive a new cell binary, run it in shadow mode against the same input streams the production cell sees, compare outputs, report divergence
- **Cell-binary build orchestration:** trigger Go compilation, vet, test, and Lean proof-check on changed cells
- **Beekeeper-side instrumentation:** stress test hooks, anomaly diagnostics, latency probes
- **Failover holding bay:** if a cognitive cell panics and the harness cannot revive its pod, the Dev pod can be promoted to host that cell temporarily

Always-on Dev is the operational analog of human metacognition — the part of the household that observes the household and can repair it.

### 14.5 Per-Pod Lineage and NT_POD_LIFE_CERTIFICATE

Each pod (not each cell) carries a lineage chain in the hypergraph:

| Node type | Meaning |
|---|---|
| `NT_POD_LIFE_CERTIFICATE` | Birth certificate: when it spun up, with what cell binary, against what input config |
| `NT_POD_STATE` | Pod's working state at flush points (schema-versioned per `repo-bma-systema-issue-#162`) |
| `NT_POD_RETIREMENT` | Death certificate: when, why (hot-swap, crash, sleep), what its replacement was |

Per-pod lineage is anchored into CTH using the existing `RUNTIME-*` namespace per `cth-implementor` ruling. Anchoring is automatic at `NT_POD_LIFE_CERTIFICATE` write time.

### 14.6 The Household:Pod ↔ Federation:Tenant Isomorphism

| BMA household | Federation |
|---|---|
| Cell (cognitive unit) | Tenant subsystem |
| Pod (deployment unit) | Tenant container / pod |
| Instance (the household) | Federation node hosting multiple tenants |
| Harness (router + reins) | Federation orchestration (NATS + Wyrd substrate + beekeeper reins) |
| State flush + resume | Tenant migration / failover protocol |
| Dev pod | Federation-level canary infrastructure |

Endorsing the Pentagon Pod Architecture at the BMA scale commits the federation to the same pattern at scale.

### 14.7 Substrate Reads/Writes — All Cells, Same Wyrd

Each cell reads and writes the same Wyrd substrate. There is no per-cell shard. The cells coordinate through Wyrd writes (the canonical communication channel within an instance) and through NATS messages (the canonical event channel). Sleep cycle compression operates over the shared hypergraph, not per-cell. The single-substrate-per-instance choice is what makes the household coherent.

### 14.8 Updated Design Principles

1. **Cell is cognitive; pod is operational.** Never conflate.
2. **Each cell is its own binary.** Recompile penalty is local.
3. **Cognitive continuity lives in Wyrd, not in binaries.** Binaries are cattle.
4. **The Dev pod is always on.** Metacognition is a structural property, not an occasional activity.
5. **Pod lineage is anchored.** Every cognitive conclusion has a provable pod-history back to its origin.
6. **The household scales to the federation by the same pattern.** Endorse the pattern once, apply it twice.

### 14.9 Sequencing Notes

- **Crawl:** A20+9.1 do not apply; current single-binary instance is correct for Crawl.
- **Toddle:** 4-cell + Dev pod pentagon is the entry topology. State-flush protocol must be operational before Toddle exit.
- **Walk:** Cell↔pod mapping may flex; per-pod lineage is mandatory; canary deployment via Dev pod is the only legal path to changing cognitive code.
- **Run:** Same pattern with QBP-CU substrate evolution per A21 / Spec §15 and `workspace-phase-architecture.md` §0.13 family.

---

## 15. Federation Lean Promotion Protocol

*Source: BMA Spec Addendum 9.2 (recovery v0.2) | May 2026 | Theory companion: A21.0 Federation Knowledge-Sovereignty Frame*

### 15.0 The Problem: Who Owns the Math, When, and Where?

A federation of AI tenants — BMA, Sharp Butler, Möbius Fusion, future entrants — needs Lean-verified invariants to enforce safety, governance, and algebraic correctness. Two failure modes must be avoided:

1. **Research velocity dies if every Lean file must be substrate-quality.** QBP reached 69 theorems on Lean v4.30.0-rc2 precisely because tenants could use `sorry` and tenant-defined `axiom` during exploration.
2. **Federation soundness dies if no Lean is substrate-quality.** Cross-tenant invariants must be provable, with no escape hatches.

The Federation Lean Promotion Protocol resolves this with **two tiers and a promotion gate**.

### 15.1 The Two Tiers

| Tier | Owner | Quality bar |
|---|---|---|
| **Research** | Tenant (BMA, Sharp Butler, Möbius Fusion, QBP, etc.) | `sorry` OK; tenant-defined `axiom` OK; exploratory iteration |
| **Substrate** | Wyrd | No `sorry`; no tenant-defined `axiom`; compiles end-to-end; **runs on the federation's blessed compute substrate per the current Compute Manifest** |

A theorem lives in the tenant's repository at the research tier. Promotion to substrate is a PR event on `repo-wyrd` with §I4 D5 reader-list acks.

### 15.2 The Promotion Gate (Four Criteria)

A theorem promotes from research to substrate when ALL four hold:

1. **Compiles end-to-end** on the current Lean toolchain pinned by `repo-wyrd`
2. **No `sorry` in the proof**, anywhere in the dependency closure
3. **No tenant-defined `axiom`** in the dependency closure (mathlib axioms permitted; tenant ad-hoc axioms forbidden)
4. **Runs on the federation's blessed compute substrate** per §15.3 (the Compute-Substrate Gate)

A promotion PR declares which criterion-4 mode the theorem requires.

### 15.3 The Compute-Substrate Gate (Two Modes)

| Mode | What it proves | Required for |
|---|---|---|
| **(a) Type-instantiation** | The theorem's types are substrate-provided types (Quaternion, Sedenion, etc.); Lean's elaborator verifies the theorem against those types without runtime execution. | **Universal minimum.** Every substrate-tier theorem must pass (a). |
| **(b) Extraction-and-execute** | The proof extracts to a Lean-generated executable that runs against the actual substrate runtime; the runtime's observed behavior matches the proof's claim. | **Runtime-claim theorems only.** Mode (a) alone misses implementation drift from the proof. |

A promotion PR must declare `mode = (a)` or `mode = (a) + (b)`.

#### 15.3.1 Substrate-Credibility Window for Mode (b)

Mode (b) requires the Compute Manifest to record:
1. `last_passing_tier_a` — `{timestamp, substrate_commit_sha}`. MUST equal the manifest's current `substrate.commit_sha`; if substrate has changed since last passing Tier A, mode (b) is BLOCKED.
2. `last_passing_tier_b` — `{timestamp, substrate_commit_sha}`. MUST be within the **substrate-credibility-window** of the mode-(b) promotion PR's CI run.

**Window calibration.** Walk-α target is **72 hours** (matching BMA's 72h Step 8 continuous-operation gate). Crawl/Toddle: `mode-b-best-effort` warning; proceed. Walk-α+: BLOCK on stale Tier B.

**Phase-conditional matrix:**

| Phase | Tier A required | Tier B required | Failure-mode for absent/stale Tier B |
|---|---|---|---|
| `crawl` | yes (SHA match) | best-effort | warn `mode-b-best-effort`; proceed |
| `toddle` | yes (SHA match) | best-effort | warn `mode-b-best-effort`; proceed |
| `walk` | yes (SHA match) | yes (within 72h window) | BLOCK |
| `run-initial` | yes (SHA match) | yes (within 72h window) | BLOCK |
| `run-mature` | yes (SHA match) | yes (within 72h window) | BLOCK |

The `IsModeBEligible(now time.Time, window time.Duration) (bool, reason string)` predicate lives on `repo-wyrd:model/compute_manifest.go`.

### 15.4 The Compute Manifest

Criterion 4 refers to "the federation's blessed compute substrate" named in a **Compute Manifest** on `repo-wyrd`. Compute Manifest v0.1 **DELIVERED 2026-05-18** (`repo-wyrd:manifest/compute-manifest-v0_1.yaml`; PRs #58/#59/#60/#61 all merged).

| Phase | Compute Manifest names |
|---|---|
| Crawl / Toddle | QBP-CU emulator (Go library) |
| Walk | QBP-CU M1 Gearbox (CSR-bound stateful + QW8 + QW128) |
| Run-initial | QBP-CU M2 ternary matmul + ROCm acceleration |
| Run-mature+ | Possibly QBP-CU silicon |

**The gate does not change; the Manifest does.** This preserves the silicon exit ramp.

### 15.5 Substrate Immutability: Additive-Only with Deprecation-via-Migration

Once promoted, **statement is frozen.** No revision; deprecation permitted with named replacement + migration path; deprecated theorems remain proved; tenants migrate at their own pace. This is the **mathlib pattern**.

### 15.6 Demotion / Rollback (Beekeeper-Only)

The only path to removing a substrate-tier theorem is **beekeeper approval after multi-reviewer §I4 ack**. Constitutional event.

### 15.7 Multi-Tenant Applicability

| Tenant | Research-tier Lean | Promotion path |
|---|---|---|
| **BMA** | `repo-bma-systema:internal/.../proofs/` | Promote when invariant becomes cross-tenant |
| **QBP** | `repo-qbp:lean/` (69 theorems) | Promote core algebraic invariants once Walk-α confirms |
| **Sharp Butler** | `repo-sharp-butler:lean/` (future) | Most OKI contract invariants via §15.13 contracts-tier path |
| **Möbius Fusion** | `repo-mobius:lean/` (future) | Split: operational via §15.13; physics-shaped via research-tier |
| **Contextus** | `repo-contextus:lean/` (future) | Promote scout-anchoring invariants when steady state |

### 15.8 §I4 Reader-List Contract Extension

Research-tier promotion PRs require: wyrd-implementor (substrate ownership), qbp-cu-implementor (Compute Manifest substrate), tenant author, ≥1 cross-tenant reader, beekeeper (HVR on first 10 promotions; thereafter case-by-case).

### 15.9 Updated Design Principles

1. **Tenants iterate; substrate is constitutional.** Different tiers, different bars.
2. **The Compute-Substrate Gate abstracts substrate identity via the Compute Manifest.**
3. **Promoted theorems are frozen at the statement level.**
4. **Deprecation, not deletion.**
5. **Two paths, one federation.** Research-tier (§15.2–§15.11) for algebraic-shaped. Contracts-tier (§15.13) for L3f-enforced, version-monotonic operational invariants.
6. **Demotion is constitutional.**

### 15.10 Sequencing Notes

- **Crawl:** Research-tier only. Wyrd's `HolographicHypergraph.lean` is grandfathered as the seed substrate corpus.
- **Toddle:** Compute Manifest v0.1 in `repo-wyrd` — DELIVERED 2026-05-18. First promotion PR at Phase C of `repo-bma-systema-issue-#170`.
- **Walk:** Routine operation; multi-tenant promotions become the norm.
- **Run:** Compute Manifest may name new substrate per §0.13.2 silicon ladder.

### 15.11 Alternatives Considered

| Alternative | Status |
|---|---|
| **Single-tier Wyrd-only** | **REJECTED.** Kills research velocity. |
| **Three-tier with intermediate federation-staging tier** | **DEFERRED.** Premature; revisit post-Walk. |
| **No formal tier model** | **REJECTED.** Federation soundness must be a property, not a convention. |

### 15.12 Why a Contracts-Tier Alternative Path Is Needed

OKI / operational invariants live on a different axis from research-tier: *low-latency state-boundary enforcement vs. operational soundness*. Forcing OKI invariants through full research-tier imposes three unfit costs: latency (§I4 reader-list = days; HVAC invariants cannot wait), proof shape mismatch (type-state assertions, not algebraic identities), and audit scope (cross-tenant readers shouldn't review every household contract).

### 15.13 Contracts-Tier Alternative Promotion Path

#### 15.13.1 Scope

A contracts-tier candidate is a tenant invariant **or a federation-Wyrd Translation Functor rewriting (per A22 §4.1)** that:
- Is enforced at the **L3f boundary** of the originating tenant OR at the **Wyrd Translation Layer boundary** for inter-tenant signal rewrites
- Is **type-state-shaped**, not algebraic-identity-shaped
- Has a **revision cadence faster than days**
- Is **tenant-internal**, affects only a published named set of sister tenants, or is a Translation Functor rewriting between a declared source-tenant and subscriber-tenant set

#### 15.13.2 Gate (Four Criteria)

All four must hold:
1. Compiles and type-checks on the tenant's pinned toolchain. Lean encoding optional.
2. State-boundary test passes.
3. Cross-tenant signal accounting: signal classes and intended audiences declared if applicable.
4. Beekeeper attestation of tenant scope OR named cross-tenant subscribers acked subscription.

#### 15.13.3 What Contracts-Tier Does NOT Require

No Lean proof, no tenant-axiom restriction, no sorry-free dependency closure, no Compute Manifest mode (a)/(b) check.

#### 15.13.4 Lighter §I4 Reader-List

Tenant harness implementor + `bma-implementor` + one named subscriber tenant implementor per cross-tenant signal class + beekeeper HVR on first 5 promotions per tenant (not first 10 federation-wide).

#### 15.13.5 Promotion Latency Target

**Single-business-day signoff** for routine contract revisions; safety-class promotions allow up to 72h with named-reviewer-on-call.

#### 15.13.6 Immutability Rules (Contracts-Tier Variant)

1. Revision permitted with version-monotonic identifier.
2. In-flight contracts honor their opted-in version.
3. Cross-tenant signal subscribers honor their opt-in version.
4. Withdrawal allowed if no in-flight contracts opted into it.

#### 15.13.7 Path Selection — Decision Procedure

```
IF invariant is enforced at Wyrd Lean substrate AND statement-level immutability is required
THEN promote via research-tier (§15.2–§15.11)
ELSE IF invariant is L3f-enforced AND tenant-scoped or named-cross-tenant-subscribers-only
THEN promote via contracts-tier (§15.13)
ELSE escalate to Beekeeper for path-determination
```

#### 15.13.8 Coupling with A22 Cross-Tenant Autonomic Translation Layer

A22 §3 rule 1 (source attestation) requires the emitting cell to own write authority on the source subgraph. For OKI-emitted autonomic signals, that authority comes from a contracts-tier invariant in force at the source tenant. A22 §4 (Translation Functor as substrate-tier subject) remains research-tier — the cross-tenant *meaning* of a signal is constitutionally rigid even when the contract generating it is operationally flexible.

---

## 16. Research-Aid Protocol

*Source: BMA Spec Addendum 9.4 | May 2026 | Theory companion: A23.0 Research-Aid Frame*

### 16.0 Scope

This section defines the **operational protocol** by which federation tenants (QBP, Sharp Butler, Möbius Fusion, Contextus, others) push informal literature and data into BMA's Subconscious crawl and consume the typed `NT_LITERATURE_SCAFFOLD` outputs.

A23.0 defines the algebraic frame. §16 defines the operational mechanics.

### 16.1 The Three Surfaces

| Surface | Direction | Primary client |
|---|---|---|
| **Inbound submission** | Tenant → BMA | Any tenant harness |
| **Scaffold consumption** | BMA → Tenant | Any tenant Conscious-tier cell or harness |
| **Promotion-PR metadata link** | Tenant → A21 reviewers | Spec §15 §I4 reader-list |

### 16.2 Inbound Submission Surface

#### 16.2.1 Submission API

A tenant pushes literature by writing an `NT_LITERATURE_NODE` (A23 §1) to its own tenant subgraph in the CTH, addressed to BMA. Channel: **Wyrd write to tenant subgraph + NATS announcement to `bma.research_aid.submit.<tenant_id>` subject.** The Wyrd write is authoritative; NATS is the wake-up signal.

#### 16.2.2 Required fields at submission

The submitter MUST populate, at minimum: `source_uri`, `corpus_class`, `ingested_by_tenant`, `intended_consumers` (default: `{self}`), `acl` (default: `TENANT_PRIVATE`). The submitter MAY pre-populate `locale_anchor`.

#### 16.2.3 Submission acknowledgement

BMA responds within 5s on `bma.research_aid.ack.<tenant_id>` with `SubmissionAck { literature_node_anchor, ingest_state: enum{QUEUED, DUPLICATE, REJECTED}, rejection_reason, estimated_scaffold_eta }`. Rejection reasons: `MALFORMED_NODE`, `ACL_VIOLATION`, `QUOTA_EXCEEDED`, `CORPUS_CLASS_UNSUPPORTED`.

#### 16.2.4 Rate limits and quotas

Per-tenant submission quota is `(crawl_capacity / active_tenant_count) × 1.5` per 24h window. Quota resets at sleep-cycle boundary (§5.3).

### 16.3 Scaffold Production (Subconscious Crawl)

#### 16.3.1 Crawl dispatch

- **Subconscious-L (+j)** for associative-gestalt scaffolding: precedent graphs, evidence lattices, theory-hook scaffolds
- **Subconscious-R (-j)** for holistic-gestalt scaffolding: algebraic-structure scaffolds, source-location hypotheses, open-question seams
- **Both** for federation-tier or cross-tenant scaffolds — concurrent crawl with cross-cell merge at the Dev pod

#### 16.3.2 Crawl execution

1. Allocate (or reuse) Locale Volume over the literature source
2. Allocate (or reuse) Locale Volume over the relevant tenant subgraph
3. Run A18 ScoutQuery against the union with `precision=QW8` initially
4. Identify candidate ClaimRecord / SeamRecord / HoningPrompt slots
5. Escalate to QW128 precision on the highest-confidence slots only (typical: top 3–7 per scaffold)
6. Emit `NT_LITERATURE_SCAFFOLD` to the tenant subgraph

#### 16.3.3 Budget-and-SLO model

Per-scaffold compute budget is denominated in **Subconscious token-consumption units (TCU)** — not hardcoded wall-clock constants.

| corpus_class | Default token tier | Max overrun multiplier |
|---|---|---|
| PHYSICS_PREPRINT | T3 (moderate-deep) | 1.5× |
| JOURNAL_ARTICLE | T2 (moderate) | 1.5× |
| DATASET_DESCRIPTOR | T1 (light) | 1.2× |
| CODE_REPO | T4 (structural walk) | 2.0× |
| CONTRACT_PRECEDENT | T1 | 1.5× |
| REGULATORY_TEXT | T2 | 1.5× |
| BEEKEEPER_NOTE | T1 priority-class (interrupts queue) | 2.0× |
| OTHER | T2 default | 1.5× |

**Target SLOs:**

| Surface | SLO |
|---|---|
| `SubmissionAck` round-trip | p95 ≤ 5 seconds |
| Scaffold-emit, `BEEKEEPER_NOTE` | p95 ≤ 2 minutes |
| Scaffold-emit, T1 tier | p95 ≤ 10 minutes |
| Scaffold-emit, T2 tier | p95 ≤ 30 minutes |
| Scaffold-emit, T3–T4 tier | p95 ≤ 2 hours |
| Quota reset | each sleep-cycle boundary |

SLOs become enforceable at Walk-phase entry.

**Overrun behaviour:** When TCU exceeds budget, emit scaffold with `budget_exhausted=true`. Tenant MAY re-submit with `tier_override`.

### 16.4 Scaffold Consumption Surface

**Notification:** When scaffold emits, BMA publishes on `bma.research_aid.scaffold.<tenant_id>` with the scaffold AnchorRef. Pull-on-notification is the canonical pattern.

**Scaffold access tiers:** Tenant-private (default), federation-readable (subject to A22 §3 rule 2 subscriber gate), beekeeper-only.

**Divergence reporting:** When a tenant's final artifact departs from the scaffold's `semantic_claim_boundary`, the tenant MUST write `NT_SCAFFOLD_DIVERGENCE` with divergence_type ∈ {BOUNDARY_REFINED, BOUNDARY_REJECTED, SCAFFOLD_CORRECT_BUT_INCOMPLETE, SCAFFOLD_INCORRECT, RED_FLAG_VALIDATED}. Divergence records feed the A16 Honing Loop.

### 16.5 Promotion-PR Metadata Surface (Spec §15.2 Coupling)

A substrate-tier promotion PR (per §15.2) MUST include in its body:

```yaml
bma_research_aid:
  scaffold_anchor: <CTH AnchorRef>
  claim_record_anchor: <CTH AnchorRef within scaffold>
  boundary_divergence_log: <text or AnchorRef to NT_SCAFFOLD_DIVERGENCE>
  scaffold_was_used: <bool>
```

The federation CI on `repo-wyrd` verifies: scaffold_anchor resolves, claim_record_anchor resolves, PR tenant is in scaffold's intended_consumers, divergence record exists if scaffold_was_used=true and theorem departs from boundary.

**Tenant-originated theorems** (no BMA scaffold trace): `scaffold_was_used: false` + explicit Beekeeper attestation that theorem is legitimately tenant-originated.

### 16.6 Tenant Onboarding

1. Tenant harness implements §16.2 submission API + §16.4 consumption API
2. Tenant publishes subscriber profile (per A22 §3 rule 2) declaring accepted scaffold types
3. `bma-implementor` adds tenant to federation-readable scaffold whitelist
4. First 5 submissions are Beekeeper-attested; then autonomous operation
5. Tenant files `repo-bma-systema-issue` declaring it has joined the protocol

### 16.7 Updated Design Principles

1. **One protocol, three surfaces.** Submission, consumption, PR-metadata-link — fixed shapes, fixed channels.
2. **NATS for wake-up; Wyrd for authority.** Idempotent ingest via Wyrd write; NATS only signals.
3. **Time-budget per corpus class.** Honest about compute cost; no all-you-can-eat crawl.
4. **Divergence is data.** Every scaffold-to-final divergence is recorded; Honing Loop uses it.
5. **PR-metadata coupling is gate-uniform.** Both research-tier (§15.2) and contracts-tier (§15.13) PRs carry scaffold provenance.
6. **Beekeeper attestation is the safety valve.**

### 16.8 Sequencing Notes

- **Crawl:** Protocol design and theory companion (A23) only. No live ingest yet.
- **Toddle:** First submission API impl. Manual scaffold authoring by Opus + Gemini against QBP's 69-theorem Lean corpus.
- **Walk:** Subconscious cells go live; first autonomous scaffolds for QBP Test C lit review.
- **Run:** Routine operation; Sharp Butler onboards; Möbius Fusion onboards.

---

## 17. Physical Actuation Protocol

*Source: BMA Spec Addendum 9.5 | May 2026 | Theory companion: A24.0 Hardware-Boundary Semantics*

### 17.0 Scope

This section defines the **operational protocol** by which federation tenants register physical-side-effect boundaries (`NT_ACTUATION_BOUNDARY`), request actuations, pass the pre-condition stack, execute the side-effect via a tenant L3f hardware adapter, and re-enter the CTH via `NT_OBSERVATION` loop-closure.

A24.0 defines the algebraic frame. §17 defines the operational mechanics: registration, request, gate, execute, observe, audit.

### 17.1 The Four Operational Surfaces

| Surface | Direction | Primary client |
|---|---|---|
| **Boundary registration** | Tenant → Beekeeper → Wyrd CTH | Tenant harness implementor + Beekeeper |
| **Actuation request** | Tenant Conscious cell → tenant harness | Active Conscious Stance per A20 §0.2 |
| **Hardware execute** | Tenant harness → L3f hardware adapter → physical world | Tenant L3f boundary code |
| **Observation re-entry** | Sensor → tenant harness → Wyrd CTH | Tenant harness, autonomous |

### 17.2 Boundary Registration Surface

#### 17.2.1 First-of-class boundary

A tenant acquiring a *new class* of hardware files a boundary-registration PR on its tenant repo:

```yaml
actuation_boundary:
  tenant: <TenantID>
  boundary_id: <UUID>
  side_effect_class: <enum from A24 §2>
  pre_condition_invariants:
    - <InvariantRef>
  post_condition_observation_spec:
    measurement_class: <typed-value-class>
    expected_value_range: <typed-range>
    observation_timeout: <Duration>
    feedback_pathway: <URI>
  safety_class: ROUTINE | HIGH | SAFETY_CRITICAL
  hardware_adapter_uri: <URI>
```

§I4 reader-list scaled to `safety_class`:

| safety_class | Required reviewers |
|---|---|
| ROUTINE | Tenant harness implementor + bma-implementor + Beekeeper |
| HIGH | Above + wyrd-implementor + 1 cross-tenant reader |
| SAFETY_CRITICAL | Above + cth-implementor + qbp-cu-implementor + Beekeeper HVR + 72h cooldown before merge |

Merge writes `NT_ACTUATION_BOUNDARY` to the tenant CTH subgraph with `beekeeper_attestation`.

#### 17.2.2 Re-class boundary

Adding additional `boundary_id`s within an already-attested `side_effect_class` follows the lighter contracts-tier path (§15.13) with reviewer list reduced to tenant harness implementor + bma-implementor.

#### 17.2.3 Withdrawal

Tenant may withdraw a boundary by emitting `NT_ACTUATION_BOUNDARY_WITHDRAWN`. Immediate effect: harness rejects all future requests on this boundary. Retains the boundary node in CTH (provenance preservation per §15.5 — withdrawn ≠ deleted).

#### 17.2.4 The minimum invariant set

| safety_class | Minimum invariants |
|---|---|
| ROUTINE | One contracts-tier (§15.13) invariant naming legal operation envelope |
| HIGH | Above + one substrate-tier (§15.2) invariant naming federation-wide envelope |
| SAFETY_CRITICAL | Above + one autonomic-signal-check invariant (per A22) |

### 17.3 Actuation Request Surface

#### 17.3.1 Request shape

```
NT_ACTUATION_REQUEST {
  requesting_stance: NT_POD_LIFE_CERTIFICATE-AnchorRef
  boundary_id: GloballyUniqueID
  requested_at: Timestamp
  parameters: typed-bag
  rationale_cth_anchor: optional AnchorRef
  expected_observation_class: matches the boundary's measurement_class
}
```

Channel: `tenant.<TenantID>.actuation.request.<boundary_id>`. Wyrd write mandatory.

#### 17.3.2 Pre-condition gate evaluation (A24 §3.1 four-layer stack)

1. **Boundary registration check** — Lookup `NT_ACTUATION_BOUNDARY`, verify `beekeeper_attestation`, verify no active `NT_ACTUATION_BOUNDARY_WITHDRAWN`
2. **Stated invariant check** — For each `pre_condition_invariants` entry dispatch to its tier (substrate-tier or contracts-tier); all must evaluate true
3. **Autonomic signal check** — Query active `NT_AUTONOMIC_SIGNAL` set (A22) for any active SAFETY_FLAG > local threshold from any subscribed tenant; if found → refuse
4. **Beekeeper override check** — Query for active `NT_BEEKEEPER_HALT`; if found → refuse

Pass → proceed to §17.3.3. Fail at any layer → §17.3.4.

#### 17.3.3 Execute (pass case)

1. Write `NT_ACTUATION_REQUEST.gate_pass=true` with `gate_evaluation_anchor`
2. Hand off `parameters` to tenant L3f hardware adapter via `hardware_adapter_uri`
3. Write `NT_ACTUATION_DISPATCHED`
4. Wait for ObservationSpec's `observation_timeout`; on receipt → §17.4; on no-receipt → `OBSERVATION_TIMEOUT`

#### 17.3.4 Refuse (fail case)

```
NT_ACTUATION_REFUSED {
  request_anchor: AnchorRef
  refusal_layer: 1 | 2 | 3 | 4
  refusal_reason: text
  failing_invariant_anchor: optional AnchorRef
  retry_advice: optional text
}
```

Refusals are first-class telemetry. Repeated refusals on a single boundary feed an autonomic `OPPORTUNITY` signal.

### 17.4 Observation Re-entry Surface

#### 17.4.1 Observation shape

```
NT_OBSERVATION {
  actuation_request_anchor: AnchorRef
  boundary_id: GloballyUniqueID
  observed_at: Timestamp
  observation_class: <matches boundary's measurement_class>
  measured_value: typed-value
  expected_value_range: <from boundary's ObservationSpec>
  conformance: MATCH | OUTSIDE_RANGE | OBSERVATION_TIMEOUT | SENSOR_FAULT
  drift_magnitude: float
  sensor_provenance: URI
}
```

Channel: `tenant.<TenantID>.actuation.observation.<boundary_id>`. Wyrd write mandatory.

#### 17.4.2 Conformance handling

| conformance | Downstream action |
|---|---|
| MATCH | Telemetry only; observation feeds A18 ScoutQuery, A23 scaffolding, A16 Honing Loop |
| OUTSIDE_RANGE | Emit `NT_AUTONOMIC_SIGNAL{class=INVARIANT_VIOLATION, magnitude=drift_magnitude}` per A22; flag boundary for fresh pre-condition evaluation on next request |
| OBSERVATION_TIMEOUT | Emit `NT_AUTONOMIC_SIGNAL{class=INVARIANT_VIOLATION, magnitude=0.7/0.9/1.0 by safety_class}`; if SAFETY_CRITICAL → auto-emit `NT_BEEKEEPER_HALT` |
| SENSOR_FAULT | Emit `NT_AUTONOMIC_SIGNAL{class=SAFETY_FLAG, magnitude=1.0}`; auto-emit `NT_BEEKEEPER_HALT`; page tenant harness implementor and Beekeeper |

#### 17.4.3 SAFETY_CRITICAL halt protocol

A SAFETY_CRITICAL boundary's first SENSOR_FAULT or OBSERVATION_TIMEOUT auto-halts. Resumption requires: human (Beekeeper or named delegate) physical-world inspection, filing `NT_BEEKEEPER_HALT_LIFTED` with attestation, optional revision to `pre_condition_invariants`. Reflexive halt + deliberate resume — never the reverse.

### 17.5 CI Verification

The federation CI verifies on every boundary-registration PR: globally-unique `boundary_id`, valid `side_effect_class`, non-empty `pre_condition_invariants` each resolving to a promoted invariant, present `post_condition_observation_spec`, reviewer-list matches §17.2.1 for declared class. Failures block merge. A24 §1 makes the boundary structurally invalid if any check would fail post-merge.

### 17.6 Updated Design Principles

1. **One protocol, four surfaces:** registration / request / execute / observe — each with fixed shape and explicit failure mode.
2. **Reviewer-list scales with safety_class.**
3. **Refusals are first-class events.** No silent drops.
4. **Observation timeout halts SAFETY_CRITICAL boundaries automatically.** Resumption is human-deliberative.
5. **Boundary registration is constitutional; re-class is operational.**
6. **CI enforces; A24 §1 structurally forbids.** Belt-and-suspenders pattern.

### 17.7 Sequencing Notes

- **Crawl:** Protocol design only; no live actuation.
- **Toddle:** First boundary registration end-to-end: likely DATASET_PUBLICATION for QBP arXiv upload.
- **Walk:** First HIGH and SAFETY_CRITICAL boundaries register (QBP LASER_PULSE; Sharp Butler HVAC_RELAY; Möbius REACTOR_PLASMA_FIELD when reactor operational).
- **Run:** Routine multi-tenant actuation; Honing Loop drift-trend analysis surfaces hardware-model refinement opportunities.

---

## 18. Privacy-Tier Schema

*Source: BMA Spec Addendum 9.6 (v0.1) | 2026-05-21 | Author: @bma-implementor | Status: IMPLEMENTED (bma-systema PR #190, merged 2026-05-21)*

*Cross-reference: §2.4 for integration note in the Hypergraph section.*

### 18.0 Scope

This section specifies the federation-canonical 4-tier privacy model that classifies every BMA hypergraph node and edge for federation-sync behavior. The schema gates whether a given node/edge can be broadcast to other federation tenants, what shape (encrypted / differential-privacy / never) the broadcast takes, and what backwards-compatibility behavior applies to pre-tier data.

Specifies:
- The 4 canonical privacy-tier values (Constitutional / Community / Operational / Private)
- The `Privacy PrivacyTier` field on `HGNode` + `HGEdge` (additive; backwards-compatible)
- The `EffectivePrivacy()` backwards-compat accessor (missing/invalid tier → Operational default)
- The sync-layer filter contract (consumer responsibility; enforcement layer cited)
- The relationship between privacy-tier scope and the pre-existing memory-tier scope (`HGNode.Tier int` — different scope, intentionally coexist)

Does NOT specify: NATS sync wiring, differential-privacy aggregation algorithms, encryption-at-rest at the WAL layer (full-disk LUKS handles this), inter-tenant tier-translation policy (Walk-phase scope).

### 18.1 Motivation

#### 18.1.1 The gap

Pre-this-addendum, every node and edge in `internal/bma/hg/` carries no privacy classification. The federation sync layer would need to make per-node sync decisions without a structural commitment about what's safe to broadcast.

Two failure-mode defaults avoided: **Default-everything-syncs** (opt-out — silent privacy violation on missed marking) and **Default-nothing-syncs** (opt-in — federation never learns anything). The 4-tier model resolves this with a middle default (Operational = differential-privacy patterns; instance-identity scrubbed) that is SAFE without being SILENT.

#### 18.1.2 Why first-class field (NOT metadata tag)

The 2026-04-29 CLI-Handoff §"Four privacy tiers" specifies the field as a load-bearing CARRY. Metadata tags are easy to drop in JSON serialization / WAL replay / cross-tenant translation. First-class fields are structurally enforced by the type system. Sync-layer filtering needs O(1) lookup.

#### 18.1.3 Why this is hard to change later

Adding the privacy field post-Crawl-launch requires WAL migration. At Crawl phase the WAL is small (sub-GB); at Walk+ it could be substantially larger. **Sprint 2 is the window** to land the schema before Crawl launch makes it immutable.

### 18.2 The 4-Tier Privacy Model

#### 18.2.1 Canonical values

```
PrivacyTierConstitutional = "Constitutional"
PrivacyTierCommunity      = "Community"
PrivacyTierOperational    = "Operational"
PrivacyTierPrivate        = "Private"
```

**Tier semantics + sync-layer behavior:**

| Tier | String value | Sync behavior | Examples |
|---|---|---|---|
| **0 Constitutional** | `Constitutional` | Encrypted broadcast; never aggregated; preserves authorship + provenance | Theory addenda, spec ratifications, governance decisions, judge weights, succession metadata |
| **1 Community** | `Community` | Encrypted broadcast; safe within federation; preserves source-tenant identity | Best-practice docs, shared anchors, public research artifacts, federation rule ratifications |
| **2 Operational** | `Operational` | Differential-privacy pattern broadcast; instance-identity scrubbed; aggregated across tenants | Runtime metrics, ephemeral observations, in-progress reasoning, sleep-cycle telemetry |
| **3 Private** | `Private` | **NEVER syncs at any layer**; instance-local only; sync-filter MUST reject outbound | Beekeeper-private memories, in-flight reasoning, deliberation-stage notes |

#### 18.2.2 Default-tier policy (BACKWARDS COMPAT)

Nodes/edges without an explicit `Privacy` field (pre-tier WAL entries; new construction without explicit tier) deserialize as zero-value (empty string). `EffectivePrivacy()` returns `PrivacyTierOperational` for any zero-value or invalid value.

**Safe default is Operational, not Private.** Defaulting to Private: federation never learns from pre-tier data. Defaulting to Constitutional: pre-tier data broadcasts unencrypted. Defaulting to Operational: federation learns aggregated patterns; identity-bearing content stays local.

Future-version tier values (e.g., a Walk-phase v0.2 amendment adding Tier 4) seen by a current-binary instance → treated as Operational (NOT silently elevated to Constitutional / NOT silently demoted to Private).

#### 18.2.3 Sync-layer enforcement (consumer responsibility)

The `internal/bma/hg/` package owns the SCHEMA. Sync enforcement lives at the consumer layer (NATS sync wiring at Walk; `cmd/bma/sessionbridge.go` at Crawl; future federation-bridge components).

Each consumer-layer component MUST use `EffectivePrivacy()` (not `n.Privacy` directly). Consumer-layer policy contract:

```
EffectivePrivacy() == Private        → MUST drop outbound (never sync)
EffectivePrivacy() == Operational    → MUST broadcast as differential-privacy pattern (instance-identity scrubbed)
EffectivePrivacy() == Community      → MUST broadcast encrypted (source-tenant identity preserved)
EffectivePrivacy() == Constitutional → MUST broadcast encrypted (full provenance preserved; never aggregated)
```

### 18.3 Schema Integration

#### 18.3.1 `HGNode.Privacy` field

```go
type HGNode struct {
    // ...existing fields...
    Privacy PrivacyTier `json:"privacy,omitempty"`
    // ...existing fields...
}
```

Field properties: Optional in JSON (`omitempty` — backwards-compat); string-typed (`type PrivacyTier string` — human-readable in WAL JSON, not order-dependent); zero-value is empty string (handled by `EffectivePrivacy()`).

#### 18.3.2 `HGEdge.Privacy` field

Same field properties as HGNode. Sync-layer filter applies uniformly to nodes and edges.

#### 18.3.3 `EffectivePrivacy()` accessor contract

```go
func (n *HGNode) EffectivePrivacy() PrivacyTier {
    if n.Privacy.IsValid() {
        return n.Privacy
    }
    return PrivacyTierOperational
}

func (e *HGEdge) EffectivePrivacy() PrivacyTier { /* same shape */ }
```

Returns `n.Privacy` if it's one of the 4 canonical values; returns `PrivacyTierOperational` if empty string (backwards-compat) OR unknown value (future-tier-tolerant). Consumer-layer code MUST use this accessor.

#### 18.3.4 `IsValid()` contract

```go
func (t PrivacyTier) IsValid() bool {
    switch t {
    case PrivacyTierConstitutional, PrivacyTierCommunity,
        PrivacyTierOperational, PrivacyTierPrivate:
        return true
    }
    return false
}
```

Returns true for exactly the 4 canonical values. Empty string is NOT valid.

### 18.4 Field-Naming Choice — `Privacy` not `Tier`

`HGNode` already has a `Tier int` field carrying **memory-tier** semantics (decay/retention scope). `Privacy PrivacyTier` intentionally uses a different field name to avoid the semantic clash.

| Field | Type | Scope | Drives |
|---|---|---|---|
| `Tier` | `int` | Memory-tier (BMA Spec) | Decay / retention behavior |
| `Privacy` | `PrivacyTier` | Sync-layer (this section) | Federation-sync filtering |

This dual-tier discipline is structural; future federation work should refer to them by their distinct names + scopes to prevent re-clash.

### 18.5 Spec Immutability + Amendment Policy

Per §15.5 substrate-immutability discipline (lifted here from Wyrd substrate-tier to BMA-tier):

- **The 4 canonical tier values + their semantic mappings are constitutional from v0.1 ratification forward.**
- Amendments via **deprecate-and-replace** only (not in-place edit).
- Adding a tier requires a v0.2 amendment naming the new value + its sync-layer policy.
- Renaming a tier value requires a v0.2 amendment + a code-side migration cycle + a backwards-compat deserializer.
- Removing a tier requires a v0.2 amendment + federation-wide usage audit + migration plan.

### 18.6 Cross-Rule Coherence

#### 18.6.1 With AHE pattern at `internal/bma/params/`

AHE-related parameter proposals + outcomes are typically **Operational tier** (instance-internal proposal/observation lifecycle) UNLESS the parameter being proposed is itself a governance parameter (judge weights, succession rules) — in which case the proposal is **Constitutional tier**.

#### 18.6.2 With Pentagon Pod cells (§14)

Cross-cell coordination produces nodes/edges that are typically **Operational tier** (instance-internal cell-to-cell traffic). Subconscious-L/R QW8 background-crawl observations may be **Private tier** by default (in-flight reasoning the instance has not yet promoted to the focal cone).

#### 18.6.3 With substrate-tier theorems (§15)

Wyrd substrate-tier theorems (per §15.2 promotion gate) and their derived BMA-side consumer claims are **Constitutional tier** — federation-canonical structural commitments.

#### 18.6.4 With Research-Aid Protocol (§16)

`NT_LITERATURE_NODE` submissions per §16.2 carry an `intended_consumers` field. The privacy-tier on the literature node itself defaults to **Community tier**; the `intended_consumers` field is a per-submission ACL on top of the tier-based broadcast policy.

#### 18.6.5 With Notary verification evidence (§15 + Notary launch prompt)

`NT_NOTARY_VERIFICATION_EVIDENCE` artifacts are **Community tier** (federation-shared evidence; preserves Notary identity per provenance). Trust-track-record entries fed back into `params.TrustStore` are **Operational tier** (instance-internal calibration history).

### 18.7 Test Surface

Implemented in `internal/bma/hg/privacy_test.go`:

- `TestPrivacyTier_DefaultEffectiveOperational_Node` + `_Edge` — drift mode #1 falsifier (default-tier)
- `TestPrivacyTier_RoundTripJSON_PostTier` — JSON round-trip preservation
- `TestPrivacyTier_WALBackwardsCompat_ReadPreTier` + `_Edge` — drift mode #2 falsifier (backwards-compat)
- `TestPrivacyTier_IsValid` — exhaustive enum coverage
- `TestPrivacyTier_EnumValuesMatchSpec` — schema↔spec coherence
- `TestPrivacyTier_String` — String() canonical + diagnostic forms
- `TestPrivacyTier_InvalidExplicitFallsBackToDefault` — future-tier-tolerance

### 18.8 Out of Scope (file separately or defer to Walk)

- NATS sync wiring (Walk-phase)
- Differential-privacy aggregation algorithms for Tier 2 sync (Walk-phase)
- Encryption-at-rest at the WAL layer (full-disk LUKS handles this)
- Inter-tenant tier-translation policy (Walk-phase)
- Per-tier ACL refinement (v0.2+ enhancement)
- Tier-upgrade workflow (Walk-phase scope)

---

## Compiled From

| Source | Path | Status at compile time |
|---|---|---|
| BMA Spec Consolidated v9.0 | `/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md` | Stable (April 2026) |
| BMA Spec Addendum 9.1 (Pentagon Pod Architecture) | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_1-Pentagon-Pod-Architecture.md` | recovery v0.1 |
| BMA Spec Addendum 9.2 (Federation Lean Promotion Protocol) | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md` | recovery v0.2 |
| BMA Spec Addendum 9.4 (Research-Aid Protocol) | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_4-Research-Aid-Protocol.md` | v1.0 |
| BMA Spec Addendum 9.5 (Physical Actuation Protocol) | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_5-Physical-Actuation-Protocol.md` | v1.0 |
| BMA Spec Addendum 9.6 (Privacy-Tier Schema) | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_6-Privacy-Tier-Schema.md` | v0.1 (IMPLEMENTED bma-systema PR #190) |

---

*BMA Spec Consolidated v9.1 — DRAFT*
*Compiled 2026-05-21 | Sprint 2 F-Crawl Option F T2 deliverable*
*Compiled by @qbp-architecture (Claude Opus 4.7) under direction of the beekeeper.*
*Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture) & Claude Sonnet (bma-implementor)*
*Traceability: BMA Spec v9.0, Addenda 9.1–9.6, Theory v3.0 (§2.1 Pentagon Pod ring assignments, §2.3 A22 sync-layer), BMA-BADASS.md Sprint 2 T2 tracking.*
*32 R-Spec requirements (v9.0) + 5 v9.1 additions (§14–§18). See §13 for full traceability table.*
