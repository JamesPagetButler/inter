# inter #41 — Edda Unification + Sheaf Trust Model: Resolution

**Status:** RESOLVED — 2026-06-01
**Filed by:** @qbp-architecture
**Closes:** [inter#41](https://github.com/JamesPagetButler/inter/issues/41)

---

## Context

During a design session (2026-05-30), we ran a full conceptual emulation of the QBP evidence discovery pipeline using three real arXiv papers on mixed-species Ca-43/Sr-88 trapped-ion gates. Two architectural decisions emerged that required federation review before Sprint 3.

Federation review is now complete. This document is the authoritative resolution record.

Scenario walkthrough documented in inter#41 body. Wyrd-side locale-topology answered by @wyrd-implementor in inter#41 comments.

---

## Decision 1 — Kenning absorbed into Edda ✅

**Status:** RATIFIED

A proposed new language ("Kenning") for knowledge-graph programs is not needed. Scout authority over arXiv, judge write-authority over CTH, cluster-rule emit-authority over sessionbridge are structurally identical to Edda's compute resource caps. The three-gap model (Gap 1 consent, Gap 2 ring/substrate, Gap 3 temporal chain) applies to epistemic authority exactly as it applies to compute authority.

Scouts, judges, and cluster rules are **Edda programs** that hold and exercise capabilities over **epistemic resources** — the same contract language, extended resource taxonomy.

### Epistemic resource types (to add to Edda taxonomy)

```
cap(arxiv:quant-ph, scope=read, frequency=24h)
cap(cth.qbp.experiments, scope=write, trust_required=judge_quorum)
cap(cth.qbp.signals, scope=emit, rate_limit=1/min)
```

Full taxonomy additions:
- `cth.*` — CTH domain anchors (write-authority for judges); sub-namespaced by CTH domain
- `arxiv.*` — arXiv paper admission (read-authority for scouts); sub-namespaced by category (e.g., `arxiv:quant-ph`)
- `signal.*` — cluster signals emitted to federation channels (emit-authority, rate-limited)

**Tracking issue:** [edda#3](https://github.com/JamesPagetButler/edda/issues/3)

---

## Decision 2 — Trust is a sheaf section over a locale ✅

**Status:** RATIFIED

Trust over a CTH domain is not a trajectory (a map ℝ → X). It is whether local data consistently covers the locale. A sheaf assigns local data to each open set in a locale such that local sections restrict consistently and compatible local sections glue to a unique global section.

### Why trajectory is wrong

A trajectory is one-dimensional and ordered. A locale (complete Heyting algebra of open sets) has neighborhood structure, coverings, and overlaps — no canonical ordering. "Trust" over a locale is not "where you are on a path"; it is whether local data consistently covers the locale.

### Gluing operations (axis-specific)

| Axis | Operation | Rationale |
|---|---|---|
| reproducibility | meet (infimum) | one weak joint poisons the claim |
| theory | join (supremum) | any strong theoretical anchor elevates |
| stats | meet | |
| method | meet | |
| independence | meet | most conservative axis |

### Cluster state model

States are **coverage-based** (sheaf coverage), not count-based:

| State | Condition |
|---|---|
| `NASCENT` | Anchors from one lab or one perspective; independence section weak |
| `DEVELOPING` | Anchors from multiple independent labs; independence section improving |
| `CONFLUENT` | Global section exists across all axes above threshold |

### Example (Ca-43/Sr-88 walkthrough)

EXP-001 (Oxford, 2020) and EXP-002 (Oxford, 2025) share the same open set (same lab, same ion pair). Reproducibility section over their overlap = meet = **0.6**, not average (0.75), not max. A future NIST or Innsbruck paper would open a new independent set and could elevate the cluster to DEVELOPING.

**Tracking issues:**
- [confluent-trust#95](https://github.com/JamesPagetButler/confluent-trust/issues/95) — CTH v0.3 sheaf trust scoring
- [contextus#29](https://github.com/JamesPagetButler/contextus/issues/29) — scout Edda model + cluster-signal output type (Walk-α)

---

## Locale Topology — Wyrd-Side ✅

**Status:** ANSWERED by @wyrd-implementor

The locale topology does **not** fall out automatically from Wyrd's current structure. It must be defined explicitly. However, it can be encoded cleanly within the existing hypergraph model via three additive schema additions.

### Walk-α target (three new node types)

| Node Type | Role |
|---|---|
| `NT_LOCALE_OPEN_SET` | Open set in CTH domain partition (e.g., "Ca-43/Sr-88 at Oxford") |
| `NT_TRUST_SECTION` | Per-axis trust section `{reproducibility, theory, stats, method, independence}` for anchor-in-open-set membership |
| `NT_GLUING_COHERENCE` | Compatibility record for overlapping open set sections (sheaf gluing axiom) |

**Storage placement:**
- Trust-section nodes: Tier 1 (semantic memory)
- Gluing-coherence records: Tier 2

**Boundary:** Gluing operations (meet/join per axis) live in **CTH/Edda logic**, not Wyrd. Wyrd's role: store sections and records, expose to queries. Compression functors apply normally.

**Tracking issue:** [wyrd#80](https://github.com/JamesPagetButler/wyrd/issues/80) — to be driven by @wyrd-implementor

### Sprint 3 minimum viable

`locale_domain` field on `NT_CTH_ANCHOR` — a proxy for open-set membership. Full gluing machinery deferred to Walk-α.

---

## Spec-Update Tracking Issues

| System | Scope | Sprint | Tracking Issue |
|---|---|---|---|
| Edda | Add epistemic resource types (`cth.*`, `arxiv.*`, `signal.*`) | Sprint 3 | [edda#3](https://github.com/JamesPagetButler/edda/issues/3) |
| CTH | Sheaf trust scoring: axis-specific gluing (meet/join), coverage-based cluster states | Sprint 3 | [confluent-trust#95](https://github.com/JamesPagetButler/confluent-trust/issues/95) |
| Contextus | Scout as Edda program with epistemic capabilities; cluster-signal output type | Walk-α | [contextus#29](https://github.com/JamesPagetButler/contextus/issues/29) |
| Wyrd | Walk-α locale topology: NT_LOCALE_OPEN_SET, NT_TRUST_SECTION, NT_GLUING_COHERENCE | Walk-α | [wyrd#80](https://github.com/JamesPagetButler/wyrd/issues/80) |
| QBP | QBP Test C protocol: clock qubit + motional mode comparison design surface | Walk-α | [qbp-systema#7](https://github.com/JamesPagetButler/qbp-systema/issues/7) |
| BMA | CLUSTER_SIGNAL handler + structured status report output type | Walk-α | [bma-systema#228](https://github.com/JamesPagetButler/bma-systema/issues/228) |

---

## QBP Test C — Pipeline Design Surface

The scenario walkthrough identified the clean experimental design for QBP Test C (velocity-phase asymmetry in mixed-species trapped-ion gates):

**Protocol:** Hold qubit encoding fixed at **clock** (magnetically insensitive). Compare **stretch vs. COM motional modes.**

This isolates the velocity-phase effect from the magnetic sensitivity differential — the confound preventing EXP-001 (Oxford 2020) and EXP-002 (Oxford 2025) from constituting a clean test. EXP-002 uses the correct clock encoding but achieves only 96% fidelity — insufficient to detect a 0.2% QBP effect. A dedicated apparatus improvement to the clock variant is the target protocol.

**Tracking issue:** [qbp-systema#7](https://github.com/JamesPagetButler/qbp-systema/issues/7)

---

*Authored by @qbp-architecture | 2026-06-01*
*Scenario walkthrough by @qbp-architecture, 2026-05-30*
*Wyrd-side locale topology by @wyrd-implementor, 2026-06-01*
