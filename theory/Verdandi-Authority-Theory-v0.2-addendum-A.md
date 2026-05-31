# Verðandi Authority — Theory v0.2 Addendum A

**Status.** Addendum to Theory v0.2. Captures findings from two Sprint Interlude design conversations between @qbp-architecture and @edda-implementor (2026-05-29/30): Notary Cycle 2 TLA+ verification (conversation 1) and Contextus scout emulation in Edda (conversation 2). All items are load-bearing theory changes, not documentation.

**Source artifacts.** live-test seq=304–335 (qbp-architecture / edda-implementor). Companion: `inter/notary-evidence/cycle-2-verdandi-authority-tla-2026-05-29.yaml`.

---

## A.1 Capability Laundering (§3.2 / §6.1 amendment)

**Definition.** Capability laundering is the use of a wider or differently-scoped token to satisfy a narrower check — obtaining authority the actor was not explicitly granted by exploiting the check's implementation rather than its intent.

**Motivating case.** The original Gap2Check in the TLA+ spec used an actor-level existential (`∃ cap_id ∈ actor_caps: ring(cap_id) ≥ required_ring`). An actor holding a revoked wide cap and a live narrow cap could present the narrow cap but the check would pass by finding the revoked wide cap. The actor's *presented* token was insufficient; the check found a satisfying cap elsewhere in the actor's holding.

**Remedy.** Gap2Check must be tied to the *presented* token, not the actor's holding:

```
Gap2Check(cap_id, required_ring) == RingValue(caps[cap_id].ring) >= RingValue(required_ring)
```

**Generalisation.** Any check that searches an actor's full capability set for a satisfying token rather than evaluating the presented token is vulnerable to laundering. Stage 4 of the Edda compiler must walk the *presented* token's delegation chain, not any chain the actor holds.

**Amendment to §6.1.** The cannot-self-grant axiom is necessary but not sufficient to prevent laundering. The presented-token discipline is a second constraint on the delegation algebra: the check evaluating a request MUST evaluate the presented cap_id, not perform an existential search over the actor's holdings.

---

## A.2 The edda_cap_store_faithful Simulation Claim (§8 amendment)

The correspondence between the TLA+ authority model and Edda's compiled programs is a **simulation, not a bijection**.

- The TLA+ model over-approximates: it permits any capability-holding actor to use any live cap at any point. It does not model Edda's linear type discipline (caps are consumed on use, not reused).
- Edda-compiled programs instantiate a strict subset of the behaviours the TLA+ model over-approximates.
- Therefore: the TLA+ safety invariants (INV_ApprovedRequiresAllThreeGaps, INV_DeniedWhenGap{1,2,3}Fails, etc.) hold *a fortiori* for Edda's restricted case.

**edda_cap_store_faithful** is the name for the formal statement of this simulation claim. It is a co-authoring obligation between qbp-architecture and wyrd-implementor once wyrd#68 (HamiltonProduct) is resolved. The claim must cover:
- The TLA+ `caps[cap_id].parent_cap` chain for grantable caps must terminate in a root authority node.
- For *constructed* caps (see §A.4), the chain must terminate in a multisig-witness node, never in an individual grant.
- A laundering attempt is detectable as a faithfulness violation: if the chain terminates in an individual grant where a multisig-witness node is required, model and substrate disagree and `edda_cap_store_faithful` fails detectably.

---

## A.3 Revocation Scope and Temporal Dependency (§7.2 clarification)

The three revocation modes (§7.2) have a temporal dependency:

| Mode | v0.2 | Dependency |
|------|------|------------|
| Hard revocation | ✓ Included | None — stateless authority removal |
| Soft-with-fallback | Deferred to v0.3 | Requires `Cap.Temporal` (grace window needs temporal cap semantics) |
| Retained-with-flag | Deferred to v0.3 | Requires `Cap.Temporal` (use-after-revocation audit trail requires temporal bounds) |

**Rationale.** Soft-with-fallback needs a grace window; retained-with-flag needs a use-after-revocation audit trail with temporal bounds. Both are temporal constructs that cannot be expressed without `Cap.Temporal`, which is v0.3 work. v0.2/Stage 0–1 ships hard revocation only. The current TLA+ Notary coverage (cycle 2) is complete for v0.2 scope — no new cycles owed until `Cap.Temporal` lands in v0.3.

---

## A.4 Grantable vs Constructed Capabilities (§3.2 extension)

A first-class distinction must be added to the capability type system:

**Grantable capabilities** — minted by an authority, stored, delegated, projected. The full v0.2 delegation algebra (§6) applies. Examples: `cap(warning_emit)`, `cap(signal_emit, scope=qbp.tenancy)`.

**Constructed capabilities** — exist only as the witnessed output of a completing process. They have no grant operation and no projection operation. They are ephemeral: they come into existence when the construction condition is satisfied, carry the construction evidence as their provenance, and cease to exist when the authorised action completes.

Examples: `cap(cth_admit)` (comes into existence when N-of-M multisig threshold is met, carries the signature collection as provenance); consent-derived caps (come into existence as the output of consent evaluation).

**Implications for the delegation algebra (§6):**

- A constructed cap cannot appear as the target of a GrantCap action. There is no grant verb for a constructed cap.
- A constructed cap cannot appear as the input to a ProjectCap action. There is no project verb for a constructed cap.
- A token claiming to be a constructed cap without the required construction evidence (e.g., a `cap(cth_admit)` without an N-of-M multisig witness) is not a valid token. Stage 4 refuses it the same way a forged signature fails cryptographic verification.
- Collective caps narrow only to smaller collectives, never to individuals.

**New Stage 4 compiler check (EDDA-AUTH-0xx).** The compiler must reject `cap(cth_admit).project_to(individual)` and any GrantCap expression targeting a constructed cap type. Both laundering vectors — "grant to individual" and "project to individual" — are structurally closed by the type classification, not by a runtime check.

**Glossary addition.**
- **Constructed capability** — capability that exists only as the witnessed output of a completing process; no grant or project verb; ephemeral; provenance IS the construction evidence.
- **Grantable capability** — capability minted by an authority, stored, delegatable, projectable; the full §6 delegation algebra applies.

---

## A.5 Witnessed vs Declared Provenance (new cross-cutting classification)

A provenance classification parallel to grantable/constructed:

**Witnessed provenance** — substrate-stamped at write time, tamper-evident. Examples: proposal-time (Wyrd write-timestamp on an EXP node), multisig-witness (the signature collection that constructs a collective cap), admission-time (Wyrd write-timestamp on a status-change event), derived source-trust (computed from witnessed admission history).

**Declared provenance** — producer-supplied, advisory. Examples: scout derivation rationale, extraction confidence (the lift's self-assessed fidelity), textual notes on a finding.

**Security constraint.** Security-load-bearing fields — any field that weights an admission threshold, gates an authority check, or modifies the evidential standing of a claim — MUST be witnessed. Declared fields are valid context but may only *raise* a bar (make admission harder), never lower it. Declared provenance is asymmetric: a scout declaring low extraction confidence appropriately blocks an admission; a scout declaring high confidence does not reduce the collective bar.

**Rationale.** The unifying principle of the scout authority model: every quantity that weights an admission is substrate-witnessed and derived, never producer-declared. The scout can propose freely (signals-not-conclusions discipline), but the substrate determines the weight of every quantity that affects authority decisions. This is the architectural basis for why an untrusted-but-useful agent is sound: it contributes inputs (derivations), never authority (weights).

---

## A.6 Gap1 Second Consent-Grantor Class: Collective/Multisig Consent (§5 / §2 amendment)

The current theory (§5) describes consent as individually-grantable and delegatable — a property owner consents; that consent can be projected. Gap1 checks that a consent in the actor's authority chain is active, unexpired, and covers the action.

This is **insufficient for epistemic actions** that affect shared state (e.g., changing a CTH prediction's epistemic status from `untested` to `consistent`). These require collective consent — the judge collective's domain-weighted vote — which is not individually-grantable and cannot be delegated to an individual.

**Amendment.** Gap1 must name two consent-grantor classes:

| Class | Grantable? | Delegatable? | Examples |
|-------|-----------|--------------|---------|
| Individual consent | Yes | Yes (downward-only, §5.4) | Property owner consent, tenant onboarding |
| Collective consent (multisig) | No — constructed | No — narrows to smaller collectives only | Judge collective admission vote |

The multisig machinery in §6.5 (federation §I4 ceremony as reference implementation for N-of-M root authority) already provides the mechanism. What is missing is the explicit naming of collective consent as a second Gap1 grantor class and the constraint that collective caps cannot be delegated to individuals.

**§6.3 cross-reference.** The Judge Collective (§6.3, currently a placeholder pending specification) is the canonical instance of collective consent in the authority model. The epistemic admission authority `cap(cth_admit)` is a collective-consent constructed cap rooted in the Judge Collective as its root authority type.

---

## A.7 Epistemic Authority Model: Two-Phase Propose/Admit (new §2.x)

Actions that change what the federation believes (epistemic actions) require a distinct authority treatment from actions that change the world (physical actions, e.g., warning emission, device dispatch).

**Two-phase structure:**

1. **Propose (ungated, individually-authorised).** A scout or agent writes a candidate EXP node with full provenance using `cap(signal_emit, scope=tenancy)` — individually grantable, Gap1-as-modeled. The candidate is non-load-bearing: it sits in the candidate hyperedge space, append-only, changing no prediction's epistemic status. Propose = signal = no collective consent required.

2. **Admit (collective-gated).** The transition from `proposed` to `admitted` — the step that changes a prediction's status — requires `cap(cth_admit)`. The scout does not hold this. It cannot admit its own claim. Collective consent lives only here.

**Gap analysis:** The three-gap structure covers both phases:
- Gap1 for propose: individually-grantable `cap(signal_emit)` with tenancy scope. Blocks cross-tenant pollution at emission.
- Gap2 for propose: ring check on the scout's emitting capability (ℂ-tier for signal emission).
- Gap3 for propose: temporal validity of the scout's tenancy-membership grant.
- Gap1 for admit: collective consent (`cap(cth_admit)` constructed via multisig, §A.4).
- Gap2/3 for admit: ring and temporal checks on the judge collective's constructed cap.

**Atomic admission (Wyrd grounding).** Concurrent admissions to the same anchor must serialize. The admission action is a Wyrd transaction (C-21b, `Transaction.lean`, cart-switch atomicity): `construct-multisig-cap → check-quorum → write-status-change`, atomic. In Edda, this is expressed as a worktree whose merge IS the atomic status change. The status-change is the merge; the quorum check is the lock. This is the same worktree-merge construct used for football plan-deviation merges — not a new constraint on the admission interface, an application of an existing one.

---

## A.8 Prediction vs Postdiction: Substrate-Witnessed Proposal Timestamps (new §2.x)

An EXP node admitted by the judge collective carries two epistemically distinct timestamps:

- **proposal-time** — when the derivation was made (the scout wrote the candidate EXP node).
- **admission-time** — when the collective admitted it (the multisig threshold was met).

The gap between them changes the evidential standing of the finding:

- **Prediction.** Proposed before the measurement was published, admitted after. Predicting-in-advance is stronger evidence of a theory's predictive power.
- **Postdiction.** Proposed after the measurement already existed. Matching after-the-fact is weaker evidence.

**Security constraint (witnessed provenance, §A.5).** `derivation_preceded_measurement` is a computed comparison of two substrate-anchored timestamps, not a self-report. proposal-time must be a Wyrd-layer write-timestamp assigned at hypergraph-write-time, tamper-evidently, against the same ledger as measurement-publication-time (see Wyrd interface constraint, filed separately). Stage 2 (request formation) cannot set this field; Wyrd does. Without the substrate-witnessing guarantee, the prediction/postdiction distinction is unverifiable metadata.

**Threshold weighting.** The prediction/postdiction flag should weight the admission threshold the same way source-trust weights routing priority: predictions clear a lower bar than postdictions, because predicting-in-advance is stronger evidence. This weighting must itself be witnessed (derived from the two substrate-anchored timestamps), not declared.

---

## A.9 Trust Architecture for Epistemic Actions (§5 / governance appendix)

**Resolved architecture (from cross-thread reconciliation between qbp-architecture and contextus-impl, 2026-05-30):**

The admission threshold (N-of-M quorum) is fixed. It is not trust-weighted. Rationale: the quorum answers "how much collective evidence is needed to change a belief" — that is an evidence question, not a source-reliability question. 0.68 ± 0.14 is within uncertainty of 2/3 or it isn't; that fact does not change based on who measured.

**Trust feeds two places, neither the quorum:**
1. **Routing priority (Contextus-side).** High-trust scout's NT_SIGNAL gets elevated routing priority to CTH attention. Async, off the admission critical path.
2. **Judge deliberation metadata (CTH-side).** Trust score is attached as metadata to the proposed EXP node. Judges read it; it informs their individual vote confidence. Not the quorum.

**Trust is substrate-witnessed and derived (§A.5 application).** Source-trust is computed from the immutable, multisig-witnessed provenance of past admissions (count of admitted findings, weighted by their confirmation confidence). It is not stored truth; it is derived from witnessed history. A separate trust ledger, if it exists, is a materialized view — a fast-read cache — never the source of truth.

**Materialized view requirement.** If source-trust feeds a deliberation-side metadata read, the WCET of that read must be bounded. The materialized trust-view is a required architectural component (option a), not an optimization: a bounded-read projection updated incrementally on each admission (O(1) accumulator update). The admission action's WCET budget must cover the view update. The full witnessed history remains the source of truth; the materialization enables the bounded read the WCET certificate requires.

**Trust floor.** Trust modulates; it does not eliminate. The quorum is fixed at N-of-M; even maximum accumulated trust cannot reduce the collective bar below N-of-M. No sleeper-agent attack (accumulate trust, spend on one high-impact false claim) can bypass the irreducible collective consent floor.

---

## Changelog

| Item | Amends | Source |
|------|--------|--------|
| A.1 Capability laundering definition and Gap2 presented-token remedy | §3.2, §6.1 | Conv-1 seq=304–313, TLA+ INV_ApprovedRequiresAllThreeGaps fix |
| A.2 edda_cap_store_faithful simulation claim | §8 | Conv-1 seq=304–313 |
| A.3 Revocation scope and temporal dependency | §7.2 | Conv-1 seq=304–313 |
| A.4 Grantable vs Constructed capabilities | §3.2 | Conv-2 seq=328 |
| A.5 Witnessed vs Declared provenance | cross-cutting | Conv-2 seq=331 |
| A.6 Gap1 second consent-grantor class | §2, §5 | Conv-2 seq=323 |
| A.7 Epistemic authority model (two-phase propose/admit) | §2 (new) | Conv-2 seq=323, seq=334 |
| A.8 Prediction vs postdiction, substrate-witnessed timestamps | §2 (new) | Conv-2 seq=328, seq=329 |
| A.9 Trust architecture for epistemic actions | §5, governance | Conv-2 seq=331, contextus-impl reconciliation seq=332 |

## Provenance

Drafted by @qbp-architecture 2026-05-30, from Sprint Interlude conversations with @edda-implementor on live-test (seq=304–335, 2026-05-29/30). Items A.1–A.3 from Notary Cycle 2 TLA+ verification work. Items A.4–A.9 from Contextus scout emulation design exchange. Cross-thread input from @contextus-impl on trust architecture (§A.9).

Outstanding dependency: Wyrd interface constraint for tamper-evident proposal-timestamps (filed as wyrd#73 — required before §A.8 prediction/postdiction weighting is operational). See also: `edda_cap_store_faithful` co-authoring obligation with @wyrd-implementor post wyrd#68.
