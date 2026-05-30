# Verðandi Authority — Theory v0.2

**Working name.** Verðandi Authority. The layer of Verðandi concerned with who has standing to act, on whose behalf, under what conditions, and with what consequences when authority changes.

**Status.** Theory document, v0.2. Supersedes v0.1. Incorporates the QBP-Architect review of v0.1 dated 2026-05-20. Companion to *Verðandi: A Theory of Wyrd-Native Interactive Work* v0.1. Not a specification.

**Stack position.** Authority is not a separate layer of the stack — it cross-cuts every other layer. Skuld enforces substrate authority through the ring algebra (Wyrd/Foundations.lean, Wyrd/Capability.lean). CTH tracks epistemic standing. BMA has named-succession beekeeper roles. Sharp Butler has Cup tiers. Verðandi Authority is the *unification* of these into one coherent model expressible in Edda (the L4 native language) and visible in the river/camera surface.

**Companion documents.** This document references Edda (the native language) and its compiler. Neither exists yet. Edda is sketched in a forthcoming companion theory document. The §8 syntax sketches in this document are *one possible realisation* of Edda's authority constructs; the section explicitly separates load-bearing requirements (what Edda must be able to express) from illustrative form (how it might look). The Edda companion document is the right place to settle the form.

---

## Changelog from v0.1

| Change | Section(s) | Driver |
| --- | --- | --- |
| Promote multi-tenant safety, compliance-as-query, consent-traceable AI safety to primary motivations | §1 | Architect §IV opportunities 1, 2, 3 |
| Add explicit Crawl/Walk phase distinction for authority infrastructure | §1.4 (new) | Architect §I push-back 4; YubiKey arriving Crawl Sprint 3 |
| Extend two-gap structure to three-gap (application, substrate, temporal) | §2 | Architect §II refinement 1 |
| Remove ring literals from application schemas; capabilities are named vocabularies; substrate mapping is separate concern | §4 | Architect §I push-back 1 (the schema-ring-coupling footgun) |
| Add **infrastructure authority** as sovereign category for Notary and similar system-attestation roles | §3.5 (new) | Architect §I push-back 3 |
| Add **Judge Collective** as fourth root authority type (placeholder section pending QBP-Architect specification) | §6.3 | Architect §I push-back 2 |
| Add cannot-self-grant axiom to delegation algebra | §6.1 | Architect §II refinement 2 |
| Add consent-downward-only axiom to consent algebra | §5 | Architect §II refinement 3 |
| Specify retained-with-flag as forward-compatibility-blocking; append-only river | §7.2 | Architect §II refinement 4 |
| Add schema versioning protocol with rolling-deployment migration | §4.3 (new) | Architect §II refinement 5; Architect §III challenge 4 |
| Elevate succession protocol from open question to mandatory specification with explicit edge case protocols | §6.4 | Architect §I push-back 4; §III challenge 3; §IV opportunity 5 |
| Add **authority envelope check** as general construct, AI agent as motivating case | §6.6 (new) | Architect §I push-back 5 |
| Formalize federation §I4 ceremony as reference implementation for N-of-M root authority | §6.5 | Architect §IV opportunity 4 |
| Add compliance-as-query subsection | §7.6 (new) | Architect §IV opportunity 2 |
| Multi-jurisdiction conflict resolution as jurisdiction-graph with consent-blocking | §5.6 (new) | Architect §III challenge 2 |
| Add explicit AI safety positioning section | §9 (new) | Architect §IV opportunity 3 |
| Reframe §8 as load-bearing requirements + illustrative realisation | §8 | Architect §III challenge 1 |
| Note that Edda design will be in companion document | §8 preamble + closing | Beekeeper direction |
| Renumber and prune open questions; many promoted to body | §11 | Architect §III in general |

---

## 1. Motivation

### 1.1 The structural gap (recap from v0.1)

Existing specs cover substrate authority — what code is allowed to do on Wyrd, enforced by Skuld through the ring algebra and proved sound in `Wyrd/Capability.lean` (T2.3). They do not cover *application authority* — what a user of an application is allowed to do, on whose behalf, with what consent, with what revocability. Sharp Butler's Cup tiers, a microburst application's property-owner consent, BMA's delegation from beekeeper to agent, the eventual succession from current beekeeper to Brett Lyman to Skyler Rainier — these are application-level authority constructs that need a shared theory.

Without a unified authority model these stay informal. The first time the framework deploys an application that handles other people's data — microburst, Sharp Butler, any clinical context, any organisational governance — informal authority becomes the load-bearing weakness. It fails first and it fails worst.

### 1.2 Multi-tenant substrate safety as primary design goal

The most powerful consequence of separating application from substrate authority is that a single Wyrd substrate can host arbitrarily many applications with completely incompatible authority schemas safely. BMA, Sharp Butler, WMPD, Contextus, future federation tenants — they can all run on the same Wyrd substrate without their authority schemas contaminating each other. This is not a side effect; it is the *primary justification* for the two-gap (now three-gap) structure.

Several design constraints follow from this goal: gap-1 (application) and gap-2 (substrate) separation must be clean precisely because gap-1 is arbitrary-application-defined; the substrate must never observe application-level distinctions; applications must never assume access to substrate-level distinctions they were not delegated.

### 1.3 Compliance-as-query, not compliance-as-infrastructure

Once revocation is a river event with structured metadata (retention obligations, retroactive flags, jurisdiction tags), legal compliance audits collapse into camera views on the provenance river at specific time slices. GDPR right-to-erasure audits, HIPAA access logs, SOC2 evidence, succession transition audits — these are river queries, not separate infrastructure. The Notary certifies compliance as a behavioural property: "at time T, every action whose authority traced to consent C had active, unexpired, unrevoked consent." This eliminates the bolt-on compliance audit layer that most systems require.

Framing the authority layer as the compliance infrastructure (rather than only the access control layer) materially changes its value proposition for any deployment that touches regulated data.

### 1.4 Consent-traceable AI safety as first-class property

Every BMA agent action that affects a human can be traced, by authority chain, to a specific human consent that either remains valid or has since been revoked. The query "show me every action whose root authority traces to a consent that has since been revoked" is the AI safety auditability guarantee. This is not a side benefit. BMA is an AI system where every human-affecting action is consent-traceable by construction. That is a meaningful safety claim that few AI safety proposals can make, and the authority layer is what delivers it.

### 1.5 Phased cryptographic infrastructure

A practical constraint affects every section that follows: cryptographic signing infrastructure is not uniformly available across phases. The authority layer must work within this constraint without pretending otherwise.

| Phase | Cryptographic basis | Authority semantics |
| --- | --- | --- |
| Crawl Sprint 1–2 | Provenance-only (sessionbridge JSONL records) | Best-effort attribution; tamper-evident at the file level but not cryptographically signed |
| **Crawl Sprint 3+** | **YubiKey-rooted (Ed25519)** | **Beekeeper signatures are cryptographic; consent acceptances are cryptographic; delegations are cryptographically signed** |
| Walk | YubiKey + multi-signer (federation §I4) | N-of-M root authorities, federation governance signatures |
| Run | HSM, full Skuld-mediated key management | Hardware-rooted key escrow, full revocation propagation |

The theory does not require cryptography to function in early Crawl, but it does require honesty about the cryptographic standing of each artifact. A provenance-only authority hyperedge is marked as such; it cannot be confused with a Crawl-Sprint-3+ cryptographic capability. This is the architect's correct insistence that conflation gives false security.

The beekeeper has confirmed YubiKey hardware is in hand and signing comes online by Crawl Sprint 3. Theory targets this; earlier sprints operate in provenance-only mode.

---

## 2. The Three-Gap Structure

A request to act in the system passes three independent authority checks:

**Gap 1: Application authority.** Does the actor (human or agent) have standing within the application to ask for this? A House of Butler client at One Cup cannot request a service that requires Two Cup. A microburst application user without consenting-recipient status cannot receive warnings. A BMA agent cannot act on a goal-shape that wasn't accepted by an authorised beekeeper.

**Gap 2: Substrate authority.** Does the action, once authorised at the application level, have the required substrate capabilities? Even an authorised Three Cup request that requires writing under an ℍ-ring capability needs a ℍ-ring cap in scope. Even an authorised microburst warning admission needs the right NATS subject permissions and the right Mímir write rings.

**Gap 3: Temporal authority.** Is the action within the valid time window of every upstream authority in the chain? A cap may be unexpired but its parent expired. A consent may be active but the schema that issued the derived tier was retired. The temporal check is uniform across cap lifetime, consent expiration, schema version retirement, retroactive revocation, and scheduled expiration. Making it a third gate collapses what would otherwise be five different checks scattered through the codebase.

These three gaps are independent. An action can pass any two and fail the third. All three must succeed.

**Composition.** Application authority *consumes* substrate authority. The application declares "this tier, in this context, can request actions that require these capability vocabularies." When a request comes in, the application checks the tier (gap 1), the system issues a scoped substrate cap derived from the tier's allowance and the request's scope, the substrate checks that cap (gap 2), and the temporal check (gap 3) validates the chain's time-windows. The two/three-gap separation is what makes the same substrate hostable by many applications with incompatible authority schemas.

**Why Skuld is necessary but not sufficient.** Skuld enforces gap 2 and gap 3 over the ring algebra and over cap metadata. Gap 1 is application-defined and lives in Edda code that *uses* Skuld. The authority layer is the discipline that says: applications must declare their gap-1 schemas; Edda must give them the constructs to do so; the compiler must check the declarations; CTH must validate them; the Notary must certify behaviour.

---

## 3. Substrate Authority

This section recapitulates what already exists in Wyrd and Skuld. Nothing here is new substrate work; it is the substrate as the authority layer needs to see it.

### 3.1 The ring algebra

Privilege is ring-typed via Cayley-Dickson subalgebras:

| Ring | Symbol | Role |
| --- | --- | --- |
| User | ℂ | ordinary application code, user-facing actions |
| Supervisor | ℍ | privileged orchestration, multi-region writes |
| Kernel | 𝕆 | substrate integrity, hypergraph invariants |
| Firmware | 𝕊 | hardware-level, QBP-CU configuration |

Each ring is an algebraic subalgebra. Boundary detectors are algebraic operations: commutator (ℂ→ℍ), associator (ℍ→𝕆), alternator (𝕆→𝕊). The four-tier no-surjection property (ℂ ↛ ℍ ↛ 𝕆 ↛ 𝕊) is machine-checked in `Wyrd/Foundations.lean` (T2.1.a/b/c).

### 3.2 Capability tokens

A substrate capability has: a ring, a scope (hypergraph region), a lifetime, and provenance. Capabilities are linear by default — use-once unless explicitly marked replicable — to prevent accidental smuggling across ring boundaries.

Operations on caps:

- **Intersection (narrowing).** A capability can be narrowed to a smaller scope, shorter lifetime, or lower ring. The narrowed cap has only the powers in both.
- **Projection (delegation).** A higher-ring holder can project a lower-ring copy to a subordinate. The projection is always ≤ the original. Soundness in `Wyrd/Capability.lean` (T2.3).
- **Composition.** Multiple caps held by the same actor combine into a composite cap with the union of their scopes (within their ring intersection). Bounded by §6.1's cannot-self-grant axiom.
- **Revocation.** A cap can be invalidated; revocation propagates (see §7).

### 3.3 Attestations

A substrate attestation is a Skuld-signed claim that some artifact was checked against the ring algebra and found sound. Attestations themselves are capabilities with ring/scope/lifetime/provenance, but their *content* is a check-result rather than a permission. They let composition be checked at composition time, not at every downstream use. A Skuld-attested contract embedded in a worktree has its merge gate trust the attestation rather than re-running the check.

Sandwich multiplicativity of the attestation chain is proved in `Wyrd/Capability.lean` (T2.4).

### 3.4 What Edda must express for substrate authority

The theory requires Edda to express:

- Ring-typed operations with compiler-verifiable ring-flow soundness
- Capability requirements on functions and contracts
- Linear capability consumption (use-once discipline by default)
- Projection, narrowing, and composition of capabilities as expressions
- Attestation attachment with downstream visibility
- Boundary-crossing syntactic structure that names the algebraic event being crossed (commutator/associator/alternator)

The form is Edda's design work; what matters here is that the authority layer requires these expressions.

### 3.5 Infrastructure authority

Some authority artifacts are not delegated from a user, a consent, or the kernel. They are *infrastructure* — system-attestation roles whose authority is sovereign relative to beekeeper succession, not subordinate to it. The Notary is the principal example.

The Notary certifies behavioural equivalence between source and lifted artifacts. If Notary authority traced back through beekeeper delegation, the Notary's certificates would be only as valid as the beekeeper's succession, which is precisely the structural vulnerability the authority theory is supposed to prevent. A Notary-issued seam record contradicting an existing authority claim would have no clear protocol consequence.

The fix: the Notary holds an infrastructure authority that is sovereign within its scope. Its certifications are not invalidated by beekeeper succession events; its scope is fixed at infrastructure-establishment time and cannot be expanded by any single beekeeper acting alone. Modifying the Notary's scope requires a federation-§I4-ceremony-equivalent (N-of-M, see §6.5).

Other roles that may take infrastructure authority:

- The CTH validator (epistemic coherence certification)
- The schema-versioning registry (declaring which schema versions remain valid)
- The Skuld attestation root (the root that signs other Skuld attestations)
- Hardware-bound roots (the QBP-CU firmware root, 𝕊-ring)

Infrastructure authorities are visible in the river but distinct from user-bound authorities. The camera should render them differently (likely as fixed landmarks rather than flowing tributaries).

---

## 4. Application Authority

Where substrate authority is universal (every application uses the same ring algebra), application authority is per-application. The authority layer gives applications a *pattern* for declaring their own schemas.

### 4.1 Authority schemas

An application authority schema is a first-class hyperedge declaring:

- **Subject kinds** — actor types the application recognises
- **Tier or role definitions** — named authority levels with their semantics
- **Action vocabulary** — actions the application defines that need authority checks
- **Authorization matrix** — which tiers can request which actions, with what scope qualifiers
- **Capability vocabulary mapping** — what *named* capabilities each (tier, action) pair consumes; the named-to-ring mapping is a *separate* concern (see §4.2)

The schema is algebraic. Tiers can be partially ordered (One Cup ≤ Two Cup ≤ Three Cup). Actions can compose. The matrix becomes a hypergraph of relations between tiers, actions, scopes, and capability vocabularies, not a flat enumeration.

### 4.2 Capability vocabularies and the schema-substrate separation

This is the v0.1 fix the architect identified. Application schemas declare capability *names*, not capability ring literals. A schema declares:

```
action issue_warning {
    requires: cap(warning_emit, scope=property.locale)
}
```

It does *not* declare:

```
action issue_warning {
    requires: cap(warning_emit, scope=property.locale, ring=ℍ)   // WRONG
}
```

The named capability `warning_emit` is bound to a ring at deployment time by Skuld through a *substrate vocabulary mapping* — a separate declarative artifact that says "for this application instance, `warning_emit` consumes a cap on ring ℍ scoped to NATS subject `warnings.>`." The mapping is application-specific in name but ring-specific in substrate.

This preserves the two-gap separation. Schema authors think in capability vocabularies appropriate to their domain (`warning_emit`, `calendar_write`, `patient_record_read`). Substrate operators think in rings and scopes. The mapping document is the explicit bridge between them. Schema changes that add new capability names do not require ring-algebra changes; substrate changes that re-bind named capabilities to different rings do not require schema changes.

The mapping document is itself authority-gated: typically an ℍ-ring artifact maintained by the substrate operator and reviewed at deployment. The Notary certifies that the mapping is consistent (no orphan capability names, no ring violations).

### 4.3 Schema versioning protocol

Schemas evolve. The protocol handles in-flight caps during evolution.

**Per-cap schema version recording.** Every cap issued under a schema carries the schema version that issued it. Gap-1 evaluation uses the *issuing* schema, not the current schema, unless the current schema explicitly declares backward compatibility for the relevant cap class.

**Migration declarations.** A schema version bump may declare migrations:

- *Compatible*: caps issued under v_N continue to evaluate correctly under v_(N+1) without change. Default.
- *Compatible-with-narrowing*: caps issued under v_N continue to function but with narrower scope/lifetime declared by the migration.
- *Incompatible-with-grace*: caps issued under v_N are valid until a declared grace-period expiry, after which they expire. Used for forced re-authorisation.
- *Incompatible-immediate*: caps issued under v_N expire immediately on schema bump. Reserved for security incidents; requires explicit infrastructure authority approval.

**Rolling deployment is the default.** A schema bump does not retroactively invalidate live sessions. The migration declaration specifies the lifecycle. This is the standard API-versioning pattern, lifted to authority.

**Authority for schema changes.** Schema changes are ℍ-ring operations against the substrate. Whether they additionally require multi-sig depends on the application: routine changes proceed under a single ℍ cap; structural changes that affect existing tiers require federation-§I4-style N-of-M (see §6.5).

### 4.4 Application authority is not RBAC

The pattern superficially resembles role-based access control but is structurally different in three ways:

**Authority is algebraic, not enumerated.** RBAC enumerates (role, permission) pairs. Verðandi Authority composes scope qualifiers, time bounds, and capability vocabularies algebraically. "Three Cup, June only, this specific property" is a narrowed Three Cup, not a separate role.

**Authority carries provenance.** RBAC role assignments are bare facts. Verðandi Authority assignments are hyperedges with full provenance — who granted, when, under what authority, with what justification, with what expiration. The river can flow through them.

**Authority composes with consent and delegation.** RBAC treats consent and delegation as separate concerns. Verðandi Authority makes them parts of the same algebra (§5, §6).

### 4.5 The microburst case (gap 1 only)

The WMPD application deployed at a Sharp Butler property:

- **Subject kinds**: property owner, opted-in client, SLA recipient, NWS coordinator
- **Tiers**: no global ordering across subject kinds; each kind has its own access pattern
- **Actions**: consent_to_deployment, receive_warning, view_coverage_map, request_silent_toggle, request_decommission
- **Capability vocabulary**: `warning_emit`, `coverage_read`, `consent_record`, `sensor_deploy`, `sensor_decommission`
- **Authorization matrix**: property owner can deploy/decommission; opted-in clients can receive; SLA recipient can receive aggregated feed; NWS coordinator (Phase 4 only) can receive operational status
- **Substrate vocabulary mapping** (separate artifact): binds `warning_emit` → ℍ-ring NATS write; `coverage_read` → ℂ-ring Mímir read; `consent_record` → ℍ-ring consent-contract write; `sensor_deploy` → ℍ-ring; `sensor_decommission` → ℍ-ring

The implementation companion §5.3 sketches these informally; the authority layer gives them algebraic structure.

---

## 5. Consent as a Contract Type

Consent is promoted from a Coherence-invariant face to a first-class Markov-Shape contract type. The motivation is unchanged from v0.1: consent has its own pillars, is the most frequently-needed authority construct in real applications, and composes with revocation non-trivially.

### 5.1 The five consent pillars

| Pillar | Content |
| --- | --- |
| **Subject** | Who is consenting. Subject kind, identity (possibly anonymised), capacity to consent, witnessing requirements |
| **Object** | What is consented to. Action vocabulary, data classes, scope qualifiers, duration |
| **Conditions** | Under what conditions consent is valid. Information disclosed before consent, comprehension confirmation, voluntariness, alternatives presented |
| **Standing** | What authority the consent confers. Standing scope, expiration, automatic-renewal vs explicit-renewal, scope of derived actions |
| **Revocation** | How consent can be withdrawn. Revocation channels, propagation behaviour, retention obligations after revocation, audit accessibility |

### 5.2 Two termination modes

Mirroring canonicalisation's two termination modes:

**Standing authority.** Consent confers ongoing authority that doesn't require re-asking for each individual action within scope. Actions within scope draw on the standing authority; the Revocation pillar describes how to terminate the standing.

**Per-action ping.** Consent must be re-confirmed for each instance of the action. Used when the action is high-stakes or rare enough that ongoing standing isn't appropriate.

Most applications use both modes for different actions.

### 5.3 The Coherence invariants of consent contracts

Consent contracts have their own Coherence invariants, applied uniformly:

- The Subject's capacity must be confirmed at offer-time
- The Object must be stated in language the Subject can understand
- The Conditions must be satisfied at offer-time, not after
- The Standing must have an explicit (not implicit) expiration
- The Revocation must be at least as easy as the original consent

CTH validates these when admitting the consent into the active hypergraph.

### 5.4 Consent as a source of application authority

A consent contract instance, once active, *produces* application authority. The consent is the predicate; the authority is the consequent. When the application's gap-1 check finds that an action requires consent-of-kind-K, the check looks up an active consent contract covering the requesting subject, the requested action, and the current time. If found and valid (Conditions still hold, Standing not expired, Revocation not invoked, gap-3 temporal check passes), the check passes and an application-authority cap is issued. The application-authority cap is exchanged for substrate caps through the §4.2 vocabulary mapping.

Consent is therefore the *source* of application authority in many cases, not a side check. The microburst property owner's consent produces the property's deployment authority. An opted-in client's consent produces their warning-reception authority. A patient's consent (in a clinical application) produces the clinician's data-access authority for that patient.

### 5.5 Consent is downward-only in the authority lattice

**Axiom.** Consent redistributes authority within an existing envelope; it cannot create new authority.

Specifically:

- An AI agent cannot consent to something that expands its own delegation
- A subject cannot consent to receiving capabilities they do not already hold
- Consent cannot project a cap onto a delegate that exceeds the consenter's own authority

This is the consent-algebra analogue of the cannot-self-grant axiom on delegation (§6.1). It must be stated explicitly because legal teams will exploit ambiguities in implicit statements of this principle.

### 5.6 Multi-jurisdiction consent

Different jurisdictions impose different requirements on the same consent. GDPR vs HIPAA vs FINRA vs contractual obligations may all apply. The v0.1 "strictest wins" answer is wrong: GDPR mandates erasure-on-request, FINRA mandates 7-year retention of financial records, both can apply to the same data point. "Strictest" gives the wrong answer for conflict cases.

**Jurisdiction graph.** Each jurisdiction's requirements are nodes; conflicts between requirements are edges. A consent contract instance is bound to a set of jurisdictions; its requirements are the union of node-requirements minus any conflict-flagged pairs.

**Conflict-blocking.** If a consent attempt produces a conflict (two jurisdictions' requirements contradict on the same dimension for the same data class), the system *refuses to issue the consent* until either:
1. The conflict is resolved (one jurisdiction's requirement excluded by an applicable exemption)
2. The conflict is explicitly accepted by an appropriate authority (typically requiring N-of-M signature)
3. The Object is restructured to fall outside one of the conflicting jurisdictions

This is significantly harder than "layered strictness" and the architect was right to push back on the v0.1 framing. The jurisdiction-graph is data, not code; populating it is a domain-expertise task per application.

---

## 6. Delegation Chains

A delegation transfers authority from a delegator to a delegate, with the delegate acting on the delegator's behalf. BMA agents acting on the beekeeper's behalf are the central case.

### 6.1 The delegation algebra

Delegation is a projection in the capability algebra:

- A delegator's authority is a cap C with ring r, scope S, lifetime L
- A delegation produces a cap C' for the delegate with ring r' ≤ r, scope S' ⊆ S, lifetime L' ≤ L
- The delegation hyperedge records: delegator, delegate, content (C'), parent cap reference (C), conditions, signature, audit trail
- The delegate acts using C'; every action carries provenance back to C and thence to whatever authorised C

**Cannot-self-grant axiom.** Composition of delegated caps is bounded by the root cap:

> If a delegate holds caps C₁' and C₂' (both projections from a common root cap C), the composition C₁' ⊕ C₂' must satisfy C₁' ⊕ C₂' ≤ C. The composition ceiling is the root, not the algebraic union.

Stated explicitly because implicit it admits constructions where a delegate composes multiple narrow projections to recover privileges the delegator never intended to grant.

### 6.2 Chain verification

When the delegate acts, the substrate (or gap-1 check, or both) verifies the chain:

1. Start from the action's cap reference Cₙ
2. Walk back to Cₙ₋₁; verify Cₙ is a valid projection of Cₙ₋₁ (algebraically; T2.3 grounds this)
3. Verify Cₙ₋₁'s delegation hyperedge is signed and the signature is valid (or, in pre-Sprint-3 Crawl, that the provenance record is intact)
4. Verify Cₙ₋₁ is still active (gap 3, including revocation status)
5. Repeat up the chain to C₀
6. Verify C₀ has a valid root authority (§6.3)

Failure at any step denies the action; the failure logs the specific link that failed.

### 6.3 Root authority

Every delegation chain terminates somewhere. The root must be authoritative without further delegation. **Five** kinds of roots (was three in v0.1):

**Beekeeper accept ceremony.** The beekeeper accepting a goal-shape, a worktree merge, a schema change, a Cup tier assignment — these produce signed authority hyperedges that serve as root capabilities. In Crawl-Sprint-1/2 these are provenance-record-rooted; from Crawl Sprint 3 these are YubiKey-Ed25519-signed.

**Consent contract instance.** A signed consent contract is a root authority for actions within its scope.

**Skuld kernel root.** Some substrate operations have roots in Skuld itself (boot-time, configuration, infrastructure). These are 𝕆-ring or 𝕊-ring and rarely cross into Verðandi's surface.

**Judge Collective resolution** (PLACEHOLDER — see below).

**Infrastructure authority** (§3.5). The Notary's root; CTH validator's root; hardware-bound roots. Not delegated from a user; sovereign within scope.

**Placeholder: Judge Collective root authority.**

> *This subsection is a placeholder. The Judge Collective has independent constitutional standing as established by BMA governance and proved sound in `Wyrd/JudgeCollective.lean` (C-21c, judge determinism + permutation invariance) and `Wyrd/Constitutional.lean` (C-21d, self-modification requires approval). The Judge Collective is therefore a fourth root authority type, not a beekeeper-delegated authority. The precise scope of Judge Collective authority — over which domains it has veto power, which actions it can independently authorize, what its relationship is to beekeeper succession, what cap-issuance it can perform — requires specification by the QBP-Architect, who has the governance context. The Verðandi Authority theory consumes this specification and integrates it; this document does not attempt to define it.*
>
> *Required from the Judge Collective specification (to be provided):*
> - *Scope of Judge Collective authority (what domains, what actions)*
> - *Form of Judge Collective root caps (signature scheme, cap content, expiration semantics)*
> - *Relationship to beekeeper roots (concurrent? hierarchical? veto-only?)*
> - *Behaviour during beekeeper succession (does Judge Collective continuity carry through?)*
> - *Conditions under which Judge Collective itself can be modified*
>
> *Once specified, this section will be replaced with the concrete protocol.*

### 6.4 Succession protocol (mandatory specification)

The beekeeper is mortal. The system must survive the beekeeper's death. BMA has named succession (Brett Lyman #1, Skyler Rainier #2). The Authority theory must formalise the protocol.

**Normal succession sequence:**

1. *Predecessor names successor* while alive and authoritative. The naming is a signed authority hyperedge. Signed cryptographically from Crawl Sprint 3 onward; provenance-rooted in earlier sprints with explicit upgrade-on-Sprint-3.
2. *Successor accepts the naming* while predecessor is alive. The acceptance is signed (or provenance-recorded) by the successor. The mutual signing creates a *succession pact* hyperedge that is the protocol's root artifact.
3. *Succession trigger* occurs — predecessor's incapacity, death, or explicit retirement. The trigger is recorded as a river event.
4. *Authority transitions*. Goal-shapes, schema authorities, and other root-bearing artifacts that explicitly transfer on succession take on the successor's signature alongside the predecessor's. Artifacts that don't transfer expire at the trigger.
5. *Audit trail preserved*. The river preserves the entire succession event; downstream artifacts gain a succession-edge in their provenance.
6. *Active delegations continue under their declared lifetime* but cannot be renewed by the predecessor.

**Edge case protocols (mandatory):**

**Predecessor dies intestate (no named successor).** All delegations from that beekeeper are held — not auto-revoked, not auto-continued. The system enters a "pending root" state where no new beekeeper-rooted authorities can issue, but existing live caps continue until their declared lifetimes. The Judge Collective (per §6.3 placeholder) is the only authority that can resolve the pending root by recognizing a new beekeeper through whatever protocol the governance document specifies. This is the existential risk the architect correctly flagged; conservative hold-pending is the answer.

**Named successor refuses at moment of succession.** Same as intestate: pending root state, Judge Collective resolution required. The refusal is a river event with its own provenance.

**Predecessor signing key compromised.** Conservative protocol: all artifacts signed by the compromised key are held pending investigation, not auto-revoked. Specifically:
- New caps issued by the compromised key are quarantined (issued but not effective) until investigation completes
- Live caps issued before the compromise window continue under their declared lifetimes
- Caps issued during the compromise window (date-range to be established by investigation) are held pending review
- Recovery requires a successor or Judge Collective resolution to reissue the compromised authorities under a new key

This is conservative but correct: auto-revoking everything signed by a compromised key during a security incident is exactly when an attacker would want the system to revoke. Auto-continuing is exactly what the attacker exploited. Quarantining and requiring explicit human-mediated recovery is the right default.

**Multi-beekeeper handover.** Beyond named succession, a beekeeper may transfer scope to a co-beekeeper (e.g., domain-specific handover from beekeeper to a domain specialist). This is a delegation projection (§6.1), not a succession; the original beekeeper remains the root authority for non-delegated scope.

### 6.5 Multi-signature roots: federation §I4 as reference implementation

§6.5 of v0.1 sketched N-of-M signature schemes as future work. We are already running one: the federation's §I4 review ceremony requires named reviewers to sign off before a PR merges. That is a 4-of-N signature scheme for substrate-level changes. The authority theory gives this algebraic grounding retroactively: §I4 reviewer acks are joint caps, not informal checks.

**Formalisation.** The §I4 ceremony defines:

- A set of *eligible signers* with their public keys
- A *threshold* N (currently 4)
- An *action scope* (substrate-level PRs against specific repos)
- A *signature collection protocol* (review comments equivalent to signed acks)
- A *result* (merged commit becomes a joint cap with the N signers as the cap's identity)

This becomes the reference implementation of multi-signature root authority. The same algebra extends to multi-beekeeper roots in §6.7 below, federation governance signatures, and any other context where joint authority is required.

**Implication for Crawl Sprint 3.** Federation §I4 ceremony moves from "informal but conventional" to "cryptographically signed" with YubiKey activation. The reviewer acks become Ed25519 signatures; the joint cap's identity becomes the set of signing public keys; the cap is verifiable by anyone with the federation's public-key registry.

### 6.6 Authority envelope check (general construct, AI motivating case)

The architect identified a second dimension to standing-authority drift beyond the temporal one v0.1 acknowledged. For AI agents, the dimension is *capability expansion*: an agent's effective power to act on delegated authority grows over time as underlying models improve, tools expand, and task scope creeps. The beekeeper who delegated "research assistance in this worktree" in early Crawl may find by mid-Walk that the agent is acting on that delegation in ways the original ceremony didn't envision.

The architect framed this as an AI-specific concern. I generalise: the same dimension applies to human delegates whose effective power grows as they accumulate system literacy and adjacent capabilities. The AI case is the most acute and most rapid; the construct is universal.

**Authority envelope.** Every delegation hyperedge records not just the delegated cap (what *can* be done) but the *intended envelope* (what was conceptually authorised). The envelope is a structured description — natural-language annotation plus structured tags (action classes, data classes, decision authority levels).

**Envelope check.** Periodically (and at sensitive action invocations), the system compares the delegate's *current effective power within the cap* against the *original intended envelope*. Discrepancies are flagged:

- *Envelope-within-cap*: current actions fall within both. Normal.
- *Envelope-exceeded-within-cap*: current actions are within the delegated cap but exceed the original envelope. Flagged for delegator review.
- *Cap-exceeded*: current actions exceed the delegated cap. Hard denial (this should already have been caught by gap-2).

**Triggers for envelope check.** Three classes:

1. *Scheduled* — periodic re-confirmation prompts at delegator-declared cadence
2. *Threshold* — when accumulated action volume or sensitivity crosses declared bounds within the cap
3. *Sensitive-action* — specific action classes trigger envelope re-check at invocation time

**AI-specific elaboration.** For AI agents, the envelope check should additionally account for model upgrades. When the agent's underlying model is upgraded, the envelope check fires automatically, and the delegator can decide whether the original envelope holds for the more capable agent or needs re-scoping.

This is genuinely new beyond v0.1. The construct is general (envelope-vs-cap is a property of any delegation) but the AI case is where it's acute enough to deserve mandatory implementation.

### 6.7 Multi-root concurrent authorities

A related case: multiple concurrent beekeepers (different domains, different organisations, different roles). The microburst case has multiple potential authorities — the beekeeper, the property owner, SLA leadership, eventually NWS. These are not in a delegation chain with each other; they are concurrent root authorities, each for their own scope.

The framework allows:

- Multiple independent root authorities with non-overlapping scopes
- Multiple independent root authorities with overlapping scopes, where action requires the conjunction (e.g., a high-stakes deployment requires both beekeeper and property owner)
- Multi-signature root authorities via §6.5 (N-of-M)

These are extensions of the same algebra; nothing new is needed beyond the schema declaring them.

---

## 7. Audit and Revocation

Authority changes over time. The authority layer handles changes as events in the provenance river, with the same machinery that handles every other event.

### 7.1 Revocation as a river event

A revocation is a typed event in the provenance river with: target, reason, signature (or provenance record in early Crawl), timestamp, effective-date. The revocation flows downstream from its target; every downstream artifact that depended on the revoked authority is reassessed.

### 7.2 Three propagation modes

**Hard revocation.** Downstream authority is gone. Pending work stops or is paused. Active state is marked held-under-revoked-authority and further use is gated.

**Soft revocation with fallback.** The downstream artifact had an alternative authority available. The artifact falls back; the fallback is itself a river event so the audit trail captures the transition.

**Retained-with-flag.** Past actions taken under the now-revoked authority remain in the river (they happened) but are flagged "asserted under authority later revoked." Critical for honest auditability — revoking authority doesn't erase history; it changes the standing of history.

**Forward-compatibility constraint on retained-with-flag.** A future consent by the same subject cannot un-flag historical data collected under the revoked consent. The river is append-only; a new consent creates new authority going forward but does not retroactively legitimise the flagged history. This must be stated explicitly because the absence of this constraint is a known legal team exploit.

### 7.3 CTH's role

CTH evaluates revocations for coherence with prior knowledge:

- A retroactive revocation (effective-date before its own timestamp) is allowed but flagged
- A revocation that contradicts other recent claims (the revoker itself recently revoked) triggers a seam
- A revocation propagating to many downstream artifacts triggers a high-impact review

### 7.4 Queryable history

The audit trail is the river itself, viewed through an audit camera. Standard queries:

- "Show me every action taken under cap C between dates A and B."
- "Show me every authority transfer involving subject S."
- "Show me every consent active when claim K was made."
- "Show me every action invalidated if we retroactively revoke authority A." *(preview before issuing)*

The preview query is interesting: it lets the beekeeper *see* a revocation's downstream impact before issuing it. The system computes the downstream change and renders it as a visible flow change in the river.

### 7.5 Retention obligations

Some revocations carry retention obligations. The application authority schema declares these per consent kind. The revocation event carries the retention metadata. The system schedules the obligations via Skuld and tracks compliance. This is where legal compliance (GDPR right-to-erasure, HIPAA retention, contractual obligations) lives.

### 7.6 Compliance-as-query

The authority layer becomes the compliance infrastructure. Legal compliance audits collapse into camera views on the provenance river:

- *GDPR right-to-erasure audit.* "For subject S, show me every data point whose authority traces to a consent C, where C is currently revoked with retention=erase. Verify each data point's retention obligation has been satisfied."
- *HIPAA access audit.* "For patient P, show me every access action with full authority chain. Annotate each access with the consent that authorised it and the actor's tier at the time."
- *SOC2 evidence gathering.* "For the audit period, show me every authority-changing event (issuance, delegation, revocation, succession) with full provenance."
- *Multi-jurisdiction reconciliation.* "For data class D, show me where jurisdiction conflicts were resolved and what authority resolved them."

The Notary can certify compliance as a behavioural property: at time T, every action whose authority traced to consent C had active, unexpired, unrevoked consent. This certification is itself a Notary-attested hyperedge with the certification scope, time window, and method documented.

This eliminates the separate compliance-audit infrastructure most systems require. It is a meaningful value-proposition shift.

---

## 8. Authority in Edda

This section is **load-bearing requirements + illustrative realisation**. The requirements are what the authority theory requires Edda to be able to express; these are theory-binding. The syntax sketches are *one possible realisation* of those requirements; they are illustrative and will be revisited (likely revised) in the Edda companion document.

### 8.1 Load-bearing requirements

The authority theory requires Edda to be able to express, with compiler-level checking:

1. Ring annotations on operations, with ring-flow soundness verified at compile time
2. Capability requirements on functions and contracts, with capability vocabulary names (not ring literals) as schema-level references
3. Linear capability consumption (use-once by default)
4. Projection, narrowing, and composition of capabilities as algebraic expressions, bounded by the cannot-self-grant axiom (§6.1)
5. Attestation attachment with downstream visibility
6. Boundary-crossing syntactic structure that names the algebraic event being crossed (commutator/associator/alternator)
7. Application authority schema declarations: subject kinds, tiers with ordering, action vocabulary, authorisation matrix
8. Substrate vocabulary mapping (separate from schema) binding named capabilities to rings and scopes
9. Consent contract declarations with five-pillar structure
10. Consent's downward-only constraint as a compiler-checkable property
11. Delegation declarations with envelope (intended scope) alongside cap (delegated scope)
12. Authority envelope check syntax (scheduled, threshold-triggered, sensitive-action-triggered)
13. Multi-signature root declarations (N-of-M with eligible signer sets)
14. Schema versioning declarations with migration semantics
15. Revocation declarations with three-mode propagation
16. Cryptographic signature attachment at every authority-modifying expression (with provenance-only fallback for pre-Sprint-3 Crawl)
17. Jurisdiction-graph declarations for multi-jurisdiction consent
18. Succession pact declarations as compiler-visible artifacts

These are non-negotiable from the theory's perspective. Edda's design is welcome to adopt any syntax that satisfies them.

### 8.2 Illustrative syntactic realisation

The following sketches are *one* way Edda might realise the requirements above. They are not specification. The Edda companion document will revisit, refine, and likely supersede these forms.

```edda
// Substrate ring annotation
contract issue_warning {
    ring: ℍ
    requires: cap(warning_emit, scope=property.locale)
    ...
}

// Application authority schema — capability vocabularies, not ring literals
schema sharp_butler {
    subject_kind client { ... }
    subject_kind property_owner { ... }

    tier teacup    annotation: "monitoring only"
    tier one_cup   annotation: "monitoring + scheduled visits" parent: teacup
    tier two_cup   annotation: "+ active response"               parent: one_cup
    tier three_cup annotation: "+ full estate concierge"          parent: two_cup

    action schedule_visit {
        parameters: { property, when, kind }
        contract: schedule_visit_contract
    }

    authorize (tier ≥ one_cup, action: schedule_visit) {
        requires: cap(calendar_write, scope=property.locale)
    }
}

// Substrate vocabulary mapping — separate artifact, deployment-time
mapping sharp_butler_substrate {
    capability calendar_write {
        ring: ℂ
        scope: mimir.write("calendar.{property_id}")
    }
    capability warning_emit {
        ring: ℍ
        scope: nats.write("warnings.{watershed_id}.>")
    }
    // ...
}

// Consent contract
consent property_sensor_deployment {
    subject: property_owner
    object: { action: deploy_sensor, scope: property.locale, duration: 2 years }
    conditions: {
        information_disclosed: deployment_disclosure_v3
        comprehension_confirmed: true
        voluntariness: confirmed
    }
    standing: continuous within scope until expiration or revocation
    revocation: {
        channels: [email, sharp_butler_app, voice]
        propagation: hard_revocation_with_retention_30d
    }
    jurisdictions: [US_NH, GDPR_if_applicable]
}

// Delegation with envelope
delegate agent_opus on_behalf_of beekeeper {
    cap: cap(read, scope=qbp_repo, lifetime=24h)
    envelope: {
        intent: "research assistance in this worktree"
        action_classes: [search, summarize, draft]
        excluded_classes: [merge_finish, schema_modify]
    }
    derived_from: goal_shape_accept(squam_microburst_v0_1)
    envelope_check: {
        scheduled: weekly
        sensitive_actions: [merge_finish_request, external_communication]
        on_model_upgrade: required
    }
    signature: beekeeper.yubikey_sign(...)   // Crawl Sprint 3+
}

// Revocation
revoke {
    target: cap(warning_emit, scope=property_xyz.locale)
    reason: "property owner consent withdrawn 2026-06-15"
    effective: now
    propagation: hard_with_retention
    signature: property_owner_xyz.yubikey_sign(...)
}

// Schema version bump with migration
schema sharp_butler v2 supersedes v1 {
    // ... changes ...
    migration: {
        teacup: compatible
        one_cup: compatible_with_narrowing { remove_actions: [some_deprecated_action] }
        two_cup: compatible
        three_cup: incompatible_with_grace { grace_period: 90d }
    }
}

// Multi-signature root: §I4 ceremony
multisig federation_i4 {
    eligible_signers: federation.registry.signers
    threshold: 4
    action_scope: pr_merge(substrate_repos)
    signature_collection: github_review_acks
}

// Succession pact
succession_pact {
    predecessor: beekeeper_current
    successor: brett_lyman
    successor_acceptance: brett_lyman.yubikey_sign(...)
    next_in_line: [skyler_rainier]
    transition_scope: [bma_roots, sharp_butler_roots, qbp_roots]
    excluded_from_transition: [personal_consent_records]
    signatures: [beekeeper_current.yubikey_sign(...), brett_lyman.yubikey_sign(...)]
}
```

These sketches assume Edda has constructs that are non-trivial design contributions in their own right: `cap(...)` as a first-class linear value type, `authorize (...)` as a constraint expression with static checking, `ring: ℍ` as a compiler-verifiable annotation, capability vocabulary names as separately-resolved symbols. Each is a research-level decision in capability-secure language design. The Edda companion is the right place for these decisions, not this document.

---

## 9. AI Safety Positioning

The architect identified that the consent-traceability property delivers a specific AI safety guarantee worth elevating to first-class.

**Claim.** BMA is an AI system where every human-affecting action is consent-traceable by construction. The authority chain from any action terminates at a human consent (or a chain of human consents); each consent is queryable, revocable, and time-bounded.

**What this enables.**

- *Continuous audit.* "Show me every action whose root authority traces to a consent that has since been revoked" is a single river query. It returns the set of decisions whose authority basis has eroded — exactly the population that any AI safety audit needs to surface.
- *Pre-action verification.* Before any human-affecting action, the gap-3 temporal check verifies that every consent in the authority chain is still active. This catches the case where a long-running agent has stale authority for actions it is currently taking.
- *Bounded delegation.* The envelope check (§6.6) catches cases where an agent's effective capability grew into its delegation without an explicit re-authorisation. Model upgrades and tool expansions are events that trigger envelope review.
- *Authority transparency.* The river is queryable by the consenter. A human who consented to something can ask "what actions has this consent enabled?" and get a comprehensive answer.

**What this does not solve.** This is not a complete AI safety solution. It addresses *authority* — whether a given action has standing. It does not address *correctness* (was the action right?), *consequence* (was the action's effect good?), or *alignment* (was the action what the consenter would have wanted?). Those remain hard problems that require separate machinery (CTH for correctness, the Notary for behavioural verification, BMA's broader cognitive architecture for alignment).

But: authority-traceability is a *prerequisite* for the harder problems. An AI system without consent-traceability cannot meaningfully be audited for alignment because the authority basis is opaque. With consent-traceability the harder problems become tractable.

The Verðandi Authority layer is therefore a specific AI safety contribution: it delivers a substrate-level guarantee that makes the harder problems addressable.

---

## 10. Worked Example: Microburst Warning Delivery

A walkthrough combining gap-1, gap-2, gap-3, consent, delegation, and revocation. Based on the microburst implementation companion's deployment scenario.

**Setup.** WMPD application is instantiated at a Sharp Butler property in the Squam watershed. Property owner has signed a consent contract for sensor deployment and warning recipient status (signed cryptographically, Crawl-Sprint-3+). Three opted-in clients have signed consent contracts for warning recipient status. Application is in calibration mode (silent run); operational warnings not yet issued externally.

**Action sequence.**

1. WMPD plugin observes a precursor signature. Emits `microburst.precursor.composite` signal at strength 0.72, locale Λ(property, t).
2. Signal consumed by the bridge. Bridge proposes a TimeWindowedProbabilistic claim and submits to CTH (per implementation companion §3.3).
3. CTH evaluates the claim. Plugin's source-trust score is checked. Truth-set consulted. Claim admitted with confidence c.
4. Application authority schema consulted. Action "issue warning" gated on: calibration mode (currently ON — this run is calibration-trace, not delivered warning), and every potential recipient having active consent. Gap 1 passes for the calibration-trace case.
5. *In production mode*, the system would look up each recipient's consent contract. Property owner: active, in scope, not expired (gap 3 passes). Each opted-in client: active, in scope, not expired (gap 3 passes for each).
6. Warning-issuance action requires `warning_emit` capability scoped to watershed.locale. The substrate vocabulary mapping binds this to ℍ-ring NATS write. Skuld issues the cap, gap 2 passes.
7. Authority chain from the warning action traces: issue → application's standing authority → derived from beekeeper acceptance of WMPD goal-shape (Crawl-Sprint-3+ YubiKey-signed) → root authority.
8. Warning emitted. Provenance records: signal, claim, CTH admission, gap 1/2/3 checks, cap derivation, full delegation chain, beekeeper root signature.

**Revocation scenario.** One opted-in client withdraws consent the next day.

- Client's consent contract marked revoked, retention=30 days for data collected under it
- Active warning state for that client's property hard-revoked
- Pending warning issued the day before (if not yet delivered) suppressed for that client; if delivered, marked "delivered under consent later revoked"; audit query "show me deliveries that became invalid retroactively" includes it
- Data collected under revoked consent enters retention window; Skuld schedules deletion in 30 days
- Provenance river shows visible disturbance at the revocation event; downstream artifacts whose authority depended on this consent are visibly affected
- Other opted-in clients, property owner, application as a whole — unaffected
- Application continues

**Schema bump scenario.** Six months later, schema v2 adds a new required consent dimension (e.g., explicit consent to AI-assisted alert filtering, which the original consent didn't address).

- Existing consents under schema v1 are checked against migration declaration
- If `compatible_with_narrowing`, existing consents continue with the new dimension defaulted to its safest value
- If `incompatible_with_grace`, consenting subjects receive re-consent prompts; existing consent valid until grace period ends
- River shows the schema bump as a structural event; all migration decisions are queryable

**This is the system working.** No special-case code, no ad-hoc revocation logic, no separate audit log. Authority constructs are first-class; changes flow through the same river; CTH validates; Notary certifies; beekeeper sees it all in the camera.

---

## 11. Open Questions

Pruned from v0.1. Several v0.1 open questions promoted into the body (succession, Notary, multi-jurisdiction). Remaining:

1. **The exact algebra of capability narrowing across the four rings.** Intersection straightforward for scope and lifetime; ring narrowing is constrained by Cayley-Dickson structure. Are there ring projections that don't have a clean algebraic form? `Wyrd/Capability.lean` proves T2.3 but the full taxonomy of narrowing operations may need additional theorems.

2. **Authority on cross-repo references.** A fiction-repo reference to a reality-repo observation — whose authority underwrites the reference? Fiction-repo author's, reality-repo author's, both? Probably both as a joint cap, but specification needed.

3. **Authority on AI-mediated merges.** When an AI auto-resolves a below-threshold conflict (Verðandi §4.1), whose authority underwrites the resolution? Probably a projected cap from the worktree's authorised-resolver set; audit trail and revocation implications need working through.

4. **Anonymisation and authority.** Sharp Butler uses HMAC-anonymised property identifiers. How does authority verification work when the subject is anonymised? Probably through a separate de-anonymisation cap held only by Skuld; discipline needs specifying.

5. **Standing-authority drift detection cadence.** Authority envelope check is specified in §6.6 but the policy for *when* to fire scheduled checks needs design. Weekly? Per agent-action volume? Adaptive?

6. **Authority for the authority layer itself.** Who can modify an application's authority schema beyond the application operator? Edda compiler authority? Substrate vocabulary mapping authority? Probably terminates at Skuld-rooted ℍ-ring authority rooted in beekeeper YubiKey signature, but the schema's own meta-authority needs clean declaration.

7. **The Notary's specific cap structure.** §3.5 establishes infrastructure authority; the Notary's particular form (scope, signature scheme, attestation format, revocation behaviour) needs spec.

8. **Edda's design constraints from this theory.** §8.1 lists 18 load-bearing requirements. Some may be in tension; some may be hard to satisfy simultaneously. The Edda companion document will surface these tensions; they may force this document's revision.

---

## 12. Glossary

(Unchanged from v0.1 except where additions noted.)

- **Application authority** — gap 1; defined by application's own schema.
- **Attestation** — Skuld-signed claim that an artifact was checked against the ring algebra at the time of checking.
- **Authority envelope** *(new)* — intended scope of a delegation, recorded alongside the delegated cap; subject of periodic and triggered checks against current effective use.
- **Capability (cap)** — value with ring, scope, lifetime, provenance; unit of substrate authority.
- **Capability vocabulary** *(new)* — named capabilities at the schema layer, separately mapped to rings/scopes at substrate.
- **Chain (delegation chain)** — sequence of capability projections from root to action.
- **Compliance-as-query** *(new)* — formal framing of legal compliance audits as river queries.
- **Consent contract** — first-class Markov-Shape contract with five consent-specific pillars.
- **Crawl Sprint 3** *(new)* — the deployment milestone at which YubiKey-rooted cryptographic signatures come online; pre-Sprint-3 authorities are provenance-only.
- **Delegation** — projection from delegator to delegate, producing narrower (or equal) cap.
- **Edda** — working name for the L4 native language; design in companion document.
- **Gap 1, Gap 2, Gap 3** *(extended)* — application, substrate, temporal authority checks.
- **Hard revocation** — full removal of downstream authority.
- **Infrastructure authority** *(new)* — sovereign category for Notary, CTH validator, hardware-bound roots; not delegated from users.
- **Judge Collective** *(new)* — fourth root authority type; constitutional independence proved in `Wyrd/JudgeCollective.lean` and `Wyrd/Constitutional.lean`; specification pending QBP-Architect.
- **Jurisdiction graph** *(new)* — data structure for multi-jurisdiction consent conflict resolution.
- **Notary** — role certifying behavioural equivalence between source and lifted artifacts; holds infrastructure authority.
- **Per-action ping** — consent mode requiring re-confirmation per action instance.
- **Projection** — capability algebra operation producing narrower cap from higher-authority one.
- **Retained-with-flag** — revocation mode preserving history but flagging it; forward-compatibility-blocking.
- **Revocation** — typed event withdrawing authority; flows downstream through river.
- **Ring** — Cayley-Dickson privilege level (ℂ/ℍ/𝕆/𝕊).
- **Root authority** — chain terminus; five kinds: beekeeper accept, consent contract, Skuld kernel, Judge Collective, infrastructure.
- **Schema versioning protocol** *(new)* — declared migrations between schema versions; rolling-deployment default.
- **Soft revocation with fallback** — downstream falls back to alternative authority.
- **Standing authority** — consent mode conferring ongoing authority until expiration or revocation.
- **Substrate authority** — gap 2; enforced by Skuld through ring algebra.
- **Substrate vocabulary mapping** *(new)* — separate artifact binding named capabilities to rings/scopes; preserves schema-substrate separation.
- **Succession pact** *(new)* — mutually-signed hyperedge naming successor and recording successor's acceptance.
- **Three-gap structure** — application, substrate, temporal checks required for every action.
- **Two-gap structure** *(deprecated)* — superseded by three-gap.

---

## Provenance

Drafted from the brainstorm between the beekeeper and Claude on 2026-05-19, reviewed by the QBP-Architect on 2026-05-20, revised by Claude on 2026-05-19 incorporating the review. The architect's pushbacks (5/5), refinements (5/5), challenges (4/4), and opportunities (5/5) were all accepted; this document adopts all sixteen as agreed with the beekeeper. The Judge Collective section (§6.3) is a placeholder pending QBP-Architect specification; the beekeeper has confirmed YubiKey hardware in hand with Sprint-3 target for cryptographic signing infrastructure.

Next in the agreed sequence: A (Verðandi v0.2 folding in Markov-Shape contracts) and the Edda companion document (language theory + compiler spec), the latter referencing this document for the load-bearing authority requirements in §8.1.

---

*References to Wyrd Lean theorems in this document have been validated against the Wyrd repo README v0.1.0-alpha (commit b8364cbc) — Phase 1–4 closed, zero sorries, zero user-defined axioms.*
