# BMA Spec Addendum — Version 9.1 (recovery v0.1)

**Pentagon Pod Architecture: Hot-Swap Cells, Per-Pod Lineage, and the Household Instance Frame**

Version 9.1 (recovery v0.1) | May 2026
Helpful Engineering — BMA Project
Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture), with bma-implementor (Claude Sonnet)
Extends: BMA Specification Consolidated v9.0 (`/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md`)
Theory companion: A20.0 Pentagon Pod Cognitive Frame (`/home/prime/Documents/inter/theory/BMA-Theory-Addendum-20_0-Pentagon-Pod-Cognitive-Frame.md`) — co-existing with the canonical A18.0 Hypergraph Access Pattern (`/home/prime/Documents/BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md`), whose singular-Stance discipline A20.0 §0.1 reconciles with
Tracking issue: `repo-bma-systema-issue-#163`
Companion design surfaces: `repo-bma-systema-issue-#159` (Pentagon Pod design); `repo-bma-systema-issue-#162` (NT_POD_STATE schema versioning)

> **Recovery note (2026-05-15):** The original Spec 9.1 was authored before 2026-05-14 21:47:31 but its content was wiped from disk by a concurrent agent's `git reset` operation in the shared working tree (see `repo-bma-systema-issue-#168` for the incident record). This v0.1 recovery reconstructs the load-bearing commitments from the theory companion (A20.0), the §I4 reader-list discussion on `repo-bma-systema-issue-#163`, and the Edit fragments preserved in the session transcript. Full prose reconstruction is owed; this version is substantively complete for the commitments it carries but is slimmer than the lost original.

---

## 0. The Problem: One Binary, One Identity, One Failure Domain

The Crawl-phase BMA architecture deploys a single Go binary per BMA instance. Every cognitive layer (Autonomic, Subconscious L/R, Conscious A/B) is a goroutine inside that binary. This is correct for Crawl — small surface, easy to debug, no orchestration overhead — but it creates three Walk-phase failure modes:

1. **Recompile-the-instance penalty.** A change in one cell requires recompiling and restarting the entire binary, simultaneously evicting every cognitive state in working memory.
2. **Co-located failure domain.** A panic in Subconscious-L can crash the binary that hosts the Autonomic loop — exactly the layer that must stay alive for hardware safety.
3. **No canary path for cognitive changes.** New cognitive logic cannot be A/B tested against the running instance.

The Pentagon Pod Architecture resolves all three by treating the BMA instance as a **household of cells running in separate pods**, with state-flush + resume as the discipline that makes hot-swap safe.

---

## 1. Cell vs Pod vs Instance vs Household — Load-Bearing Disambiguation

| Term | Meaning |
|---|---|
| **Cell** | A cognitive unit. Four cognitive cells per instance: Conscious-A, Conscious-B, Subconscious-L, Subconscious-R. Autonomic is substrate concern handled by every cell (or by a dedicated cell at Walk+). |
| **Pod** | A deployment unit. A Podman container hosting one (or possibly more) cell binaries. Pods are the boundary across which fault isolation, hot-swap, and resource quotas are enforced. |
| **Instance** | The whole BMA. A coordinated set of cells running across some number of pods; identity (lineage, succession, beekeeper relationship) belongs to the instance, not to any single pod. |
| **Household** | A metaphor. The instance is a household; cells are members; pods are rooms. Load-bearing because it transfers cleanly to the federation:tenant isomorphism (see §6). |

**Toddle entry topology:** 1 cell per pod. 4 cognitive pods + 1 always-on Dev pod = 5-pod pentagon.

**Walk-phase flex:** the cell↔pod mapping may flex (a cell might span pods for resilience, or two cells might share a pod for latency), but the cell remains the cognitive unit and the pod remains the deployment unit.

---

## 2. Separate-Binary-Per-Cell Implementation Topology

The architectural commitment captured in `repo-bma-systema-issue-#159` review (qbp-architecture, 2026-05-13): **each cell is its own Go binary.**

| Property | Consequence |
|---|---|
| One binary per cell | Recompiling Conscious-A does not require touching Subconscious-L or the Autonomic loop |
| Per-cell version pinning | Cells can run at different code versions during canary; household tolerates heterogeneous cognitive lineage during transition |
| Per-pod resource quotas | Podman cgroups apply per pod; a runaway cell hits its own quota wall first, leaving the rest of the household responsive |
| Per-cell crash isolation | A panic in one cell kills one pod; the supervisor (harness) restarts that pod without disturbing the others |

The **harness** is the router. It owns:
- Cell↔pod address book
- Inter-cell messaging (NATS at Walk; in-process Go channels at Toddle bridged to NATS-shape for forward compatibility)
- Hot-swap orchestration (drain old cell pod → bring up new cell pod → cut over)
- Beekeeper-facing reins API

---

## 3. State Flush + Resume Protocol

Hot-swap requires that a cell can be killed and replaced without losing cognitive state:

1. **Cell receives FLUSH** from harness (signal or NATS message)
2. **Cell serializes its working memory** to Wyrd via the standard `NT_CELL_STATE` write
3. **Cell ACKs flush complete**
4. **Harness brings up replacement pod** with the new cell binary
5. **Replacement cell loads state** from `NT_CELL_STATE` at startup
6. **Harness cuts over the address book**; old pod is reaped

State flush is also used outside hot-swap — during sleep cycle compression, when Conscious-A must hand off to the compression operator without losing in-flight reasoning trace.

The flush protocol is **the reason cells can be treated as cattle, not pets**. Cognitive continuity lives in Wyrd; the binary is just the current executor.

---

## 4. The Always-On Dev Pod

The fifth pod of the pentagon is the **Dev pod**. It runs continuously alongside the four cognitive cells but does not participate in normal cognition. Responsibilities:

- **Canary deployment:** receive a new cell binary, run it in shadow mode against the same input streams the production cell sees, compare outputs, report divergence
- **Cell-binary build orchestration:** trigger Go compilation, vet, test, and Lean proof-check on changed cells
- **Beekeeper-side instrumentation:** stress test hooks, anomaly diagnostics, latency probes that beekeeper invokes via reins
- **Failover holding bay:** if a cognitive cell panics and the harness cannot revive its pod, the Dev pod can be promoted to host that cell temporarily while a fresh pod is built

Always-on Dev is the operational analog of human metacognition — the part of the household that observes the household and can repair it.

---

## 5. Per-Pod Lineage and NT_POD_LIFE_CERTIFICATE

Each pod (not each cell) carries a lineage chain in the hypergraph:

| Node type | Meaning |
|---|---|
| `NT_POD_LIFE_CERTIFICATE` | Birth certificate of a pod: when it spun up, with what cell binary, against what input config |
| `NT_POD_STATE` | Pod's working state at flush points (schema-versioned per `repo-bma-systema-issue-#162`) |
| `NT_POD_RETIREMENT` | Death certificate: when, why (hot-swap, crash, sleep), what its replacement was |

Per-pod lineage is anchored into CTH using the existing `RUNTIME-*` namespace per `cth-implementor` ruling. Anchoring is automatic at `NT_POD_LIFE_CERTIFICATE` write time.

---

## 6. The Household:Pod ↔ Federation:Tenant Isomorphism

The Pentagon Pod Architecture's load-bearing claim about federation scaling:

| BMA household | Federation |
|---|---|
| Cell (cognitive unit) | Tenant subsystem |
| Pod (deployment unit) | Tenant container / pod |
| Instance (the household) | Federation node hosting multiple tenants |
| Harness (router + reins) | Federation orchestration (NATS + Wyrd substrate + beekeeper reins) |
| State flush + resume | Tenant migration / failover protocol |
| Dev pod | Federation-level canary infrastructure |

Endorsing the Pentagon Pod Architecture at the BMA scale commits the federation to the same pattern at scale.

---

## 7. Substrate Reads/Writes — All Cells, Same Wyrd

Each cell reads and writes the same Wyrd substrate. There is no per-cell shard. The cells coordinate through Wyrd writes (the canonical communication channel within an instance) and through NATS messages (the canonical event channel).

This means:
- A cell's state changes are visible to every other cell via Wyrd query
- The Autonomic loop's hardware-pressure signals are written to Wyrd and read by every cognitive cell
- Sleep cycle compression operates over the shared hypergraph, not per-cell

The single-substrate-per-instance choice is what makes the household coherent.

---

## 8. Updated Design Principles

1. **Cell is cognitive; pod is operational.** Never conflate.
2. **Each cell is its own binary.** Recompile penalty is local.
3. **Cognitive continuity lives in Wyrd, not in binaries.** Binaries are cattle.
4. **The Dev pod is always on.** Metacognition is a structural property, not an occasional activity.
5. **Pod lineage is anchored.** Every cognitive conclusion has a provable pod-history back to its origin.
6. **The household scales to the federation by the same pattern.** Endorse the pattern once, apply it twice.

---

## 9. Sequencing Notes

- **Crawl:** A20+9.1 do not apply; current single-binary instance is correct for Crawl.
- **Toddle:** 4-cell + Dev pod pentagon is the entry topology. State-flush protocol must be operational before Toddle exit.
- **Walk:** Cell↔pod mapping may flex; per-pod lineage is mandatory; canary deployment via Dev pod is the only legal path to changing cognitive code.
- **Run:** Same pattern with QBP-CU substrate evolution per A21 (Federation Knowledge-Sovereignty Frame) / Spec Addendum 9.2 (Federation Lean Promotion Protocol) and `workspace-phase-architecture.md` §0.13 family.

---

*BMA Spec Addendum 9.1 (recovery v0.1) | May 2026*
*Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture) with @bma-implementor (Claude Sonnet)*

---

## References

| Reference | Path / URL |
|---|---|
| Tracking issue `repo-bma-systema-issue-#163` | https://github.com/JamesPagetButler/bma-systema/issues/163 |
| Design surface `repo-bma-systema-issue-#159` (Pentagon Pod) | https://github.com/JamesPagetButler/bma-systema/issues/159 |
| Sub-issue `repo-bma-systema-issue-#162` (NT_POD_STATE schema versioning) | https://github.com/JamesPagetButler/bma-systema/issues/162 |
| Recovery incident `repo-bma-systema-issue-#168` (this addendum's reconstruction trail) | TBD on filing |
| BMA Spec v9.0 §10.7 (BMA-within-Systema scope note) | `/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md` |
| A17.0 Proactive Curiosity (theory) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-17_0-Proactive-Curiosity.md` |
| A18.0 Hypergraph Access Pattern (canonical Stance discipline; singular focal cone) | `/home/prime/Documents/BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md` |
| A20.0 Pentagon Pod Cognitive Frame (theory companion) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-20_0-Pentagon-Pod-Cognitive-Frame.md` |
| Spec Addendum 9.2 Federation Lean Promotion Protocol (companion) | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md` |
| A21.0 Federation Knowledge-Sovereignty Frame (theory companion to 9.2) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-21_0-Federation-Knowledge-Sovereignty-Frame.md` |
| Workspace phase architecture (federation layer stack + paradigm coexistence) | `/home/prime/Documents/inter/workspace-phase-architecture.md` |
| Bridge channel `live-test` (Pentagon Pod review thread) | sessionbridge MCP server: `~/.claude/mcp-servers/sessionbridge/state/live-test.jsonl` (seq=108–130) |
| BMA repo working directory | `/home/prime/Documents/BMA/` (remote: `github.com/JamesPagetButler/bma-systema`) |

*Traceability: `repo-bma-systema-issue-#159`, `repo-bma-systema-issue-#162`, `repo-bma-systema-issue-#163`, bridge channel `live-test` seq=108–130, BMA Spec v9.0 §10.7, A17.0 Proactive Curiosity (cells as metacognitive scouts), A20.0 Pentagon Pod Cognitive Frame (theory companion).*
