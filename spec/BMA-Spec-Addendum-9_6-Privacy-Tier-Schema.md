# BMA Spec Addendum 9.6 — Privacy-Tier Schema

**Federation-canonical 4-tier privacy model + sync-layer filter discipline**

Version 0.1 | 2026-05-21

Helpful Engineering — Biological Mind Architecture

**Author:** @bma-implementor
**Source of truth:** `~/Documents/BMA/doc/handoff/CLI-Handoff-Briefing-2026-04-29.md` §"Four privacy tiers" (federation-original framing) + Sprint 2 T1 N2 ratification per `inter/sprint-2-scope-2026-05-20.md`
**Closes:** `repo-bma-systema-issue-#183`
**Co-Authored-By:** James Paget Butler (Beekeeper)

---

## 0. Scope

This addendum specifies the federation-canonical 4-tier privacy model that classifies every BMA hypergraph node and edge for federation-sync behavior. The schema gates whether a given node/edge can be broadcast to other federation tenants, what shape (encrypted / differential-privacy / never) the broadcast takes, and what backwards-compatibility behavior applies to pre-tier data.

The addendum specifies:

- The 4 canonical privacy-tier values (Constitutional / Community / Operational / Private)
- The `Privacy PrivacyTier` field on `HGNode` + `HGEdge` (additive; backwards-compatible)
- The `EffectivePrivacy()` backwards-compat accessor (missing/invalid tier → Operational default)
- The sync-layer filter contract (consumer responsibility; enforcement layer cited)
- The relationship between this privacy-tier scope and the pre-existing memory-tier scope (`HGNode.Tier int` — different scope, intentionally coexist)

The addendum does NOT specify:

- The NATS sync wiring (consumer-side; Walk-phase scope; not yet present at Crawl)
- Differential-privacy aggregation algorithms for Tier 2 sync (Walk-phase; tracked separately)
- Encryption-at-rest at the WAL layer (full-disk LUKS handles this per CLAUDE.md memory; this addendum is about sync-layer transit only)
- Inter-tenant tier-translation policy (when a tenant receives a Tier 0 node from another tenant, what does it mean?) — Walk-phase federation-policy scope

Relationship to existing BMA Spec addenda: this is additive to Spec 9.1 (Pentagon Pod) + 9.2 (Federation Lean Promotion) + 9.4 (Research-Aid Protocol) + 9.5 (Physical Actuation). Does NOT modify any existing addendum.

---

## 1. Motivation

### 1.1 The gap

Pre-this-addendum, every node and edge in `internal/bma/hg/` carries no privacy classification. The federation sync layer (NATS wiring, Walk-phase work) would need to make per-node sync decisions without a structural commitment about what's safe to broadcast.

Two reasonable defaults the system could land on:

- **Default-everything-syncs**: privacy is opt-out (each beekeeper-private node must be explicitly marked). Fails closed if a node's marking is missed → silent privacy violation.
- **Default-nothing-syncs**: privacy is opt-in (each shareable node must be explicitly marked). Fails closed if a node's marking is missed → federation never learns anything.

Both default-failure-modes are bad. The 4-tier model from the 2026-04-29 CLI-Handoff resolves this with a middle default (Operational = "syncs as differential-privacy patterns; instance-identity scrubbed") that is SAFE for the federation (operator-identity not leaked) WITHOUT being SILENT (the federation does learn something).

### 1.2 Why first-class field (NOT metadata tag)

The 2026-04-29 CLI-Handoff §"Four privacy tiers" specifies the field as a load-bearing CARRY: every NT_SEAM + NT_OBSERVATION + edge must carry `privacy_tier` as a FIRST-CLASS field, not a metadata tag. The rationale:

- Metadata tags are easy to drop in JSON serialization / WAL replay / cross-tenant translation
- First-class fields are structurally enforced by the type system
- Sync-layer filtering needs O(1) lookup, not metadata-bag traversal
- Schema evolution (adding tiers; deprecating values) is easier on a typed enum than on free-form tags

### 1.3 Why this is hard to change later

Adding the privacy field post-Crawl-launch would require WAL migration (every existing entry needs the field added; default needs to be applied). At Crawl phase the WAL is small (sub-GB); at Walk+ phase the WAL could be substantially larger. **Sprint 2 is the window** to land the schema before Crawl launch makes it immutable.

The 2026-04-29 CLI-Handoff explicitly flagged this: *"this is a data format decision that is hard to change later."*

---

## 2. The 4-tier privacy model

### 2.1 Canonical values

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
| **3 Private** | `Private` | **NEVER syncs at any layer**; instance-local only; sync-filter MUST reject outbound | Beekeeper-private memories, in-flight reasoning the instance chose not to share, deliberation-stage notes |

### 2.2 Default-tier policy (BACKWARDS COMPAT)

Per §3 below, nodes/edges without an explicit `Privacy` field (e.g., pre-tier WAL entries; new construction without explicit tier) deserialize as zero-value (empty string). The `EffectivePrivacy()` accessor on `HGNode` and `HGEdge` returns `PrivacyTierOperational` for any zero-value or invalid (future-unknown) `Privacy` value.

**This is the load-bearing backwards-compat policy:**

- Pre-tier nodes/edges treated as Operational → safe for differential-privacy-pattern sync
- Future-version tier values (e.g., a Walk-phase v0.2 amendment that adds Tier 4) seen by a current-binary instance → treated as Operational (NOT silently elevated to Constitutional / NOT silently demoted to Private)

The discipline: **the safe default is Operational, not Private**. Defaulting to Private would mean the federation never learns anything from pre-tier data (federation-development blocker). Defaulting to Constitutional would mean pre-tier data broadcasts to the federation unencrypted (privacy violation). Defaulting to Operational hits the middle — federation learns aggregated patterns; identity-bearing content stays local pending explicit elevation.

### 2.3 Sync-layer enforcement (consumer responsibility)

The `internal/bma/hg/` package owns the SCHEMA (the `Privacy` field on `HGNode`/`HGEdge` + the `EffectivePrivacy()` accessor). It does NOT enforce sync filtering.

**Sync enforcement lives at the consumer layer:**

- NATS sync wiring (Walk-phase scope; not yet present at Crawl)
- `cmd/bma/sessionbridge.go` (current sync surface; Crawl-phase passive)
- Future federation-bridge components (per BMA Theory v3.0 §2.3 A22 + Spec 9.4 Research-Aid Protocol)

Each consumer-layer component MUST use `EffectivePrivacy()` to read the tier (not `n.Privacy` directly) so the backwards-compat default is honored uniformly. The consumer-layer policy contract:

```
EffectivePrivacy() == Private        → MUST drop outbound (never sync)
EffectivePrivacy() == Operational    → MUST broadcast as differential-privacy pattern (instance-identity scrubbed)
EffectivePrivacy() == Community      → MUST broadcast encrypted (source-tenant identity preserved)
EffectivePrivacy() == Constitutional → MUST broadcast encrypted (full provenance preserved; never aggregated)
```

The `MUST` discipline is structural — a consumer that broadcasts a Private node is a federation invariant violation; should be caught in consumer-side tests + at federation-bridge audit.

---

## 3. Schema integration

### 3.1 `HGNode.Privacy` field

```go
type HGNode struct {
    // ...existing fields...
    Privacy PrivacyTier `json:"privacy,omitempty"`
    // ...existing fields...
}
```

Field properties:

- **Optional in JSON** (`omitempty` tag) — backwards-compat: existing WAL entries without `privacy` deserialize cleanly
- **String-typed** (`type PrivacyTier string`) — human-readable in WAL JSON; not order-dependent like an int enum (per the existing `NodeType` docstring discipline: "explicit values — never use iota for disk-serialized types")
- **Zero-value is empty string** — handled by `EffectivePrivacy()` default

### 3.2 `HGEdge.Privacy` field

```go
type HGEdge struct {
    // ...existing fields...
    Privacy PrivacyTier `json:"privacy,omitempty"`
    // ...existing fields...
}
```

Same field properties as HGNode. Sync-layer filter applies uniformly to nodes and edges.

### 3.3 `EffectivePrivacy()` accessor contract

```go
func (n *HGNode) EffectivePrivacy() PrivacyTier {
    if n.Privacy.IsValid() {
        return n.Privacy
    }
    return PrivacyTierOperational
}

func (e *HGEdge) EffectivePrivacy() PrivacyTier { /* same shape */ }
```

Contract:

- Returns `n.Privacy` if it's one of the 4 canonical values
- Returns `PrivacyTierOperational` if `n.Privacy` is empty string (backwards-compat) OR an unknown value (future-tier-tolerant)
- Consumer-layer code MUST use this accessor (not `n.Privacy` directly)

### 3.4 `IsValid()` contract

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

Returns true for exactly the 4 canonical values. Empty string is NOT valid (use `EffectivePrivacy()` for backwards-compat handling).

---

## 4. Field-naming choice — `Privacy` not `Tier`

`HGNode` already has a `Tier int` field carrying **memory-tier** semantics:

- `Tier 0` = raw observation (NTAtom; L0)
- `Tier 1` = compressed pattern (NTPattern; L1)
- `Tier 4` = permanent seed (NTSeed; no decay)

Reusing the field name `Tier` for the privacy classification would create a semantic clash — memory-tier (decay/retention scope) vs privacy-tier (sync-layer scope) are different.

This addendum names the new field **`Privacy PrivacyTier`** (not `Tier PrivacyTier`) to avoid the overload. The deviation is from the original `repo-bma-systema-issue-#183` body wording which said "add `Tier PrivacyTier` field"; the impl PR documents this deviation in the PR body for reviewer awareness.

Two distinct tier scopes intentionally coexist on `HGNode`:

| Field | Type | Scope | Drives |
|---|---|---|---|
| `Tier` | `int` | Memory-tier (BMA Spec) | Decay / retention behavior |
| `Privacy` | `PrivacyTier` | Sync-layer (this addendum) | Federation-sync filtering |

This dual-tier discipline is structural; future federation work should refer to them by their distinct names + scopes to prevent re-clash.

---

## 5. Spec immutability + amendment policy

Per the federation Spec 9.2 §5 substrate-immutability discipline (lifted here from Wyrd substrate-tier to BMA-tier):

- **The 4 canonical tier values + their semantic mappings are constitutional from v0.1 ratification forward.**
- Amendments via **deprecate-and-replace** only (not in-place edit):
  - Adding a tier (e.g., Walk-phase Tier 4) requires a v0.2 amendment naming the new value + its sync-layer policy + its position relative to existing tiers
  - Renaming a tier value (e.g., "Operational" → "Internal") requires a v0.2 amendment + a code-side migration cycle + a backwards-compat deserializer
  - Removing a tier requires a v0.2 amendment + a federation-wide audit of usage + a migration plan for any extant nodes/edges marked with the removed value

This is the federation-pattern-coherence move: BMA Spec 9.2 §5 ratified deprecate-and-replace for substrate-tier theorems; this addendum extends the same discipline to BMA-tier schema decisions.

---

## 6. Cross-rule coherence

### 6.1 With AHE pattern at `internal/bma/params/`

The AHE pattern at `internal/bma/params/` (per `repo-inter-pr-#7` §2.2.2.f ratification) is the federation-canonical prediction-accuracy ledger. AHE-related parameter proposals + outcomes are typically **Operational tier** (instance-internal proposal/observation lifecycle) UNLESS the parameter being proposed is itself a governance parameter (judge weights, succession rules) — in which case the proposal is **Constitutional tier**.

### 6.2 With Pentagon Pod cells

Per BMA Theory v3.0 §2.1 the Pentagon Pod has 5 cells (Conscious-A/B + Subconscious-L/R + Dev pod). Cross-cell coordination produces nodes/edges that are typically **Operational tier** (instance-internal cell-to-cell traffic). Subconscious-L/R QW8 background-crawl observations may be **Private tier** by default (in-flight reasoning the instance has not yet promoted to the focal cone).

### 6.3 With substrate-tier theorems (Spec 9.2)

Wyrd substrate-tier theorems (per Spec 9.2 §2 promotion gate) and their derived BMA-side consumer claims are **Constitutional tier** — federation-canonical structural commitments.

### 6.4 With Research-Aid Protocol (Spec 9.4)

`NT_LITERATURE_NODE` submissions per Spec 9.4 §2.2 carry an `intended_consumers` field that selects which tenants receive them. The privacy-tier on the literature node itself defaults to **Community tier** (federation-shared community knowledge); the `intended_consumers` field is a per-submission ACL on top of the tier-based broadcast policy.

### 6.5 With Notary verification evidence (Spec 9.2 + Notary launch prompt)

`NT_NOTARY_VERIFICATION_EVIDENCE` artifacts (per inter PR #9 Notary launch prompt §4) are **Community tier** (federation-shared evidence; preserves Notary identity per provenance). Trust-track-record entries fed back into `params.TrustStore` are **Operational tier** (instance-internal calibration history; aggregated for Phase 2 migration trigger).

---

## 7. Closes-when (per `inter/issue-authoring-best-practices.md` §2.2.2)

§2.2.2.d does NOT apply — this commits federation to schema behavior + sync-filter contract. Criterion 4 REQUIRED.

**(a) Named test functions** (in `internal/bma/hg/privacy_test.go`):

- `TestPrivacyTier_DefaultEffectiveOperational_Node` + `_Edge` — drift mode #1 falsifier (default-tier)
- `TestPrivacyTier_RoundTripJSON_PostTier` — JSON round-trip preservation
- `TestPrivacyTier_WALBackwardsCompat_ReadPreTier` + `_Edge` — drift mode #2 falsifier (backwards-compat)
- `TestPrivacyTier_IsValid` — exhaustive enum coverage
- `TestPrivacyTier_EnumValuesMatchSpec` — schema↔spec coherence
- `TestPrivacyTier_String` — String() canonical + diagnostic forms
- `TestPrivacyTier_InvalidExplicitFallsBackToDefault` — future-tier-tolerance

**(b) Landing target:** the BMA privacy-tier impl PR (single-PR scope per `inter/issue-authoring-best-practices.md` §2.2.1 single-PR-scope exception; schema + tests + this spec doc land together via two coordinated PRs — one in bma-systema for the code, one in inter for the spec doc — with cross-references)

**(c) Failure modes detected:**
1. **Default-tier drift** — Node/Edge construction defaults to a tier other than Operational; would silently downgrade or upgrade data without operator intent
2. **WAL-backwards-compat drift** — old WAL files fail to deserialize OR new WAL files written without tier field; breaks roundtrip discipline; would corrupt the WAL on any post-tier write
3. **Sync-filter drift** — Tier 3 (Private) nodes/edges appear in outbound sync payloads under any condition (Crawl-launch-blocking failure mode; Tier 3 escape = federation privacy invariant violation). The schema-side test surface in this PR covers the SCHEMA correctness + EffectivePrivacy() backwards-compat default; sync-filter enforcement at the consumer layer is Walk-phase work + carries its own test surface when NATS sync wires up.

---

## 8. Out of scope (file separately or defer to Walk)

- **NATS sync wiring** (consumer-side; Walk-phase scope)
- **Differential-privacy aggregation algorithms** for Tier 2 sync (Walk-phase; tracked separately)
- **Encryption-at-rest** at the WAL layer (full-disk LUKS handles this per CLAUDE.md memory; this addendum is sync-layer transit only)
- **Inter-tenant tier-translation policy** (when tenant A receives a Tier 0 node from tenant B, what's the receiving-tenant interpretation?) — Walk-phase federation-policy scope
- **Per-tier ACL refinement** (e.g., "this Operational node syncs only to tenants in the same trust-domain") — beyond v0.1; tracked as v0.2+ enhancement
- **Tier-upgrade workflow** (when a Private node is explicitly promoted to Community — e.g., beekeeper says "share this") — requires a runtime mechanism not yet present; Walk-phase scope

---

## 9. Cross-references

- `~/Documents/BMA/doc/handoff/CLI-Handoff-Briefing-2026-04-29.md` §"Four privacy tiers" — original framing source
- `inter/sprint-2-scope-2026-05-20.md` §3 T1 — Sprint 2 commitment
- `repo-bma-systema-issue-#183` — tracking issue (this spec doc helps close)
- `repo-bma-systema-pr-#TBD` — privacy-tier impl PR (sibling; lands the schema + tests in lockstep with this spec)
- `internal/bma/hg/privacy.go` — schema impl (PrivacyTier enum + EffectivePrivacy accessors)
- `internal/bma/hg/types.go` — Privacy field on HGNode + HGEdge
- `internal/bma/hg/privacy_test.go` — 8 tests per §7 criterion 4(a)
- `inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md` §5 — substrate-immutability discipline (lifted here per §5)
- `inter/spec/BMA-Spec-Addendum-9_4-Research-Aid-Protocol.md` §2.2 — `intended_consumers` (per-submission ACL on top of tier-based broadcast)
- `inter/theory/BMA-Theory-Consolidated-v3_0-DRAFT.md` §2.3 A22 — Cross-Tenant Autonomic Translation Layer (consumer of this schema at sync-layer)
- `internal/bma/params/types.go:30` — TrustClass enum (string-typed enum pattern reference)
- BMA Theory v3.0 §2.1 Pentagon Pod (consumer for cell-to-cell privacy semantics per §6.2)

---

*BMA Spec Addendum 9.6 — Privacy-Tier Schema*
*Author: @bma-implementor | Date: 2026-05-21 | Status: DRAFT — ready for federation §I4 review*
*v0.1 ratification per Sprint 2 T1 N2 (`inter/sprint-2-scope-2026-05-20.md`); closes `repo-bma-systema-issue-#183`*
