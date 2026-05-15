# BMA Spec Addendum — Version 9.5

**Physical Actuation Protocol: Operational Specification for Hardware-Boundary Crossings**

Version 9.5 | May 2026
Helpful Engineering — BMA Project
Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture)
Extends: BMA Specification Consolidated v9.0 (`/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md`)
Theory companion: A24.0 Hardware-Boundary Semantics (`/home/prime/Documents/inter/theory/BMA-Theory-Addendum-24_0-Hardware-Boundary-Semantics.md`)
Tracking issue: TBD on `repo-bma-systema`

---

## 0. Scope

This addendum defines the **operational protocol** by which federation tenants register physical-side-effect boundaries (`NT_ACTUATION_BOUNDARY`), request actuations, pass the pre-condition stack, execute the side-effect via a tenant L3f hardware adapter, and re-enter the CTH via `NT_OBSERVATION` loop-closure.

A24.0 defines the algebraic frame (airgap as one-way operation, observation as loop-closure, sub-tenancy of hardware). 9.5 defines the operational mechanics: registration, request, gate, execute, observe, audit.

---

## 1. The Four Operational Surfaces

| Surface | Direction | Primary client |
|---|---|---|
| **Boundary registration** | Tenant → Beekeeper → Wyrd CTH | Tenant harness implementor + Beekeeper |
| **Actuation request** | Tenant Conscious cell → tenant harness | Active Conscious Stance per A20 §0.2 |
| **Hardware execute** | Tenant harness → L3f hardware adapter → physical world | Tenant L3f boundary code |
| **Observation re-entry** | Sensor → tenant harness → Wyrd CTH | Tenant harness, autonomous |

Each surface has a fixed message shape and explicit failure-mode handling.

---

## 2. Boundary Registration Surface

### 2.1 First-of-class boundary

A tenant acquiring a *new class* of hardware files a boundary-registration PR on its tenant repo:

```yaml
actuation_boundary:
  tenant: <TenantID>
  boundary_id: <UUID>            # tenant-generated, must be globally unique
  side_effect_class: <enum from A24 §2>
  pre_condition_invariants:
    - <InvariantRef>             # at least one; see §2.4
  post_condition_observation_spec:
    measurement_class: <typed-value-class>
    expected_value_range: <typed-range>
    observation_timeout: <Duration>
    feedback_pathway: <URI>      # how the sensor reports back
  safety_class: ROUTINE | HIGH | SAFETY_CRITICAL
  hardware_adapter_uri: <URI>
```

The PR is reviewed under a §I4 reader-list calibrated to `safety_class`:

| safety_class | Required reviewers |
|---|---|
| ROUTINE | Tenant harness implementor + bma-implementor + Beekeeper |
| HIGH | Above + wyrd-implementor + 1 cross-tenant reader |
| SAFETY_CRITICAL | Above + cth-implementor + qbp-cu-implementor + Beekeeper HVR + 72h cooldown before merge |

Merge writes `NT_ACTUATION_BOUNDARY` to the tenant CTH subgraph with `beekeeper_attestation` set to the merging Beekeeper's signature node.

### 2.2 Re-class boundary

Adding additional `boundary_id`s within an already-attested `side_effect_class` is *not* a first-of-class event; it follows the lighter contracts-tier path (Spec 9.2 §13) with reviewer list reduced to tenant harness implementor + bma-implementor.

### 2.3 Withdrawal

A tenant may withdraw a boundary by emitting `NT_ACTUATION_BOUNDARY_WITHDRAWN`. Withdrawal:

- Immediate effect: harness rejects all future actuation requests on this boundary
- Retains the boundary node in CTH (provenance preservation per Spec 9.2 §5 — withdrawn ≠ deleted)
- Required when hardware is decommissioned, replaced, or fails physical-security audit

### 2.4 The minimum invariant set

Every boundary MUST list at least one pre-condition invariant. Empty `pre_condition_invariants` is rejected at PR review — a hand with no gates is forbidden. The minimum acceptable invariant set per safety_class:

| safety_class | Minimum invariants |
|---|---|
| ROUTINE | One contracts-tier (Spec 9.2 §13) invariant naming legal operation envelope |
| HIGH | Above + one substrate-tier (Spec 9.2 §2) invariant naming federation-wide envelope (e.g., conservation of optical power budget) |
| SAFETY_CRITICAL | Above + one autonomic-signal-check invariant (e.g., "no SAFETY_FLAG signal of magnitude > 0.3 from any subscribed tenant"; per A22) |

---

## 3. Actuation Request Surface

### 3.1 Request shape

A Conscious Stance issues:

```
NT_ACTUATION_REQUEST {
  requesting_stance: NT_POD_LIFE_CERTIFICATE-AnchorRef  // which cell issued (A20 §5)
  boundary_id: GloballyUniqueID
  requested_at: Timestamp
  parameters: typed-bag                  // class-specific; e.g., laser pulse: { duration_ns, power_mW, wavelength_nm }
  rationale_cth_anchor: optional AnchorRef  // pointer to the CTH reasoning that justifies this action
  expected_observation_class: matches the boundary's measurement_class
}
```

Channel: tenant-internal NATS subject `tenant.<TenantID>.actuation.request.<boundary_id>`. Wyrd write of the request node is mandatory (audit anchor).

### 3.2 Pre-condition gate evaluation (A24 §3.1 four-layer stack)

The harness, on receiving the request, executes the four layers sequentially:

1. **Boundary registration check**
   - Lookup `NT_ACTUATION_BOUNDARY` by `boundary_id`
   - Verify `beekeeper_attestation` AnchorRef resolves
   - Verify no active `NT_ACTUATION_BOUNDARY_WITHDRAWN`
2. **Stated invariant check**
   - For each `pre_condition_invariants` entry, dispatch to its tier:
     - Substrate-tier: query the live Wyrd Lean proof-cache (Spec 9.2 §3 mode (a) and (b) results)
     - Contracts-tier: query tenant L3f enforcement engine (Spec 9.2 §13)
   - All must evaluate true; first failure short-circuits
3. **Autonomic signal check**
   - Query current `NT_AUTONOMIC_SIGNAL` set (A22) for any active SAFETY_FLAG with magnitude > local threshold from any subscribed tenant
   - If found → refuse
4. **Beekeeper override check**
   - Query for active `NT_BEEKEEPER_HALT` (federation-wide) and per-boundary halt nodes
   - If found → refuse

Pass → proceed to §3.3. Fail at any layer → §3.4.

### 3.3 Execute (pass case)

On pass:

1. Write `NT_ACTUATION_REQUEST.gate_pass=true` with `gate_evaluation_anchor` pointing to the evaluation record
2. Hand off `parameters` to the tenant L3f hardware adapter via `hardware_adapter_uri`
3. Adapter returns acknowledgement; write `NT_ACTUATION_DISPATCHED`
4. Wait for the ObservationSpec's `observation_timeout` window; on receipt → §4 (Observation Re-entry); on no-receipt → `OBSERVATION_TIMEOUT` per §4.3

### 3.4 Refuse (fail case)

On fail:

```
NT_ACTUATION_REFUSED {
  request_anchor: AnchorRef
  refusal_layer: 1 | 2 | 3 | 4
  refusal_reason: text                  // human-readable; from the failing layer
  failing_invariant_anchor: optional AnchorRef   // populated for layer 2 / 3 / 4 failures
  retry_advice: optional text
}
```

The requesting Conscious Stance receives the refusal as an NT_SIGNAL into the Dev pod queue (A20 §0.2). The Conscious cell may choose to:

- Adjust parameters and re-request
- Surface the refusal to Beekeeper as a HoningPrompt (A16) — "the laser pulse refused because invariant X failed; should we revisit invariant X?"
- Abandon the actuation

Refusals are first-class telemetry. Repeated refusals on a single boundary feed an autonomic `OPPORTUNITY` signal: "the operational envelope may be too narrow — should we revisit it?"

---

## 4. Observation Re-entry Surface

### 4.1 Observation shape

After actuation dispatch, the sensor pathway returns:

```
NT_OBSERVATION {
  actuation_request_anchor: AnchorRef     // back-reference
  boundary_id: GloballyUniqueID
  observed_at: Timestamp
  observation_class: <matches boundary's measurement_class>
  measured_value: typed-value
  expected_value_range: <from boundary's ObservationSpec>
  conformance: MATCH | OUTSIDE_RANGE | OBSERVATION_TIMEOUT | SENSOR_FAULT
  drift_magnitude: float                  // 0.0-1.0
  sensor_provenance: URI                  // identifies the sensor instance
}
```

Channel: tenant-internal NATS subject `tenant.<TenantID>.actuation.observation.<boundary_id>`. Wyrd write is mandatory.

### 4.2 Conformance handling

Each `conformance` value drives a defined downstream action:

| conformance | Downstream action |
|---|---|
| MATCH | Telemetry only; observation feeds A18 ScoutQuery, A23 scaffolding, A16 Honing Loop drift trend |
| OUTSIDE_RANGE | Emit `NT_AUTONOMIC_SIGNAL{class=INVARIANT_VIOLATION, magnitude=drift_magnitude}` to local tenant + subscribers per A22; flag boundary for next-request fresh pre-condition evaluation (no cached invariant results) |
| OBSERVATION_TIMEOUT | Emit `NT_AUTONOMIC_SIGNAL{class=INVARIANT_VIOLATION, magnitude=0.7 (ROUTINE) / 0.9 (HIGH) / 1.0 (SAFETY_CRITICAL)}`; if SAFETY_CRITICAL → auto-emit `NT_BEEKEEPER_HALT` on this boundary pending Beekeeper review |
| SENSOR_FAULT | Emit `NT_AUTONOMIC_SIGNAL{class=SAFETY_FLAG, magnitude=1.0}`; auto-emit `NT_BEEKEEPER_HALT` on this boundary; tenant harness implementor and Beekeeper paged |

### 4.3 OBSERVATION_TIMEOUT specifics

The harness starts a timer at `NT_ACTUATION_DISPATCHED` matching the boundary's `observation_timeout`. If no `NT_OBSERVATION` arrives within the window:

1. Write `NT_OBSERVATION{conformance=OBSERVATION_TIMEOUT}` with `measured_value=null`
2. Drive §4.2 downstream actions per `safety_class`
3. The boundary's *next* request is forced to re-evaluate all pre-condition invariants from scratch (no cached results); this is the "lost-feel-on-the-hand" recovery state

### 4.4 SAFETY_CRITICAL halt protocol

A SAFETY_CRITICAL boundary's first SENSOR_FAULT or OBSERVATION_TIMEOUT auto-halts. Resumption requires:

- Human (Beekeeper or named delegate) physical-world inspection of the apparatus
- Filing `NT_BEEKEEPER_HALT_LIFTED` with attestation of inspection result
- Optional: revision to the boundary's `pre_condition_invariants` if inspection revealed a gap
- Resume operations

This is reflexive halt + deliberate resume — never the reverse.

---

## 5. CI Verification

The federation CI on `repo-wyrd` (and downstream tenant repos) verifies on every boundary-registration PR:

1. `boundary_id` is globally unique (no collision in any tenant CTH)
2. `side_effect_class` is in A24 §2 enum
3. `pre_condition_invariants` non-empty AND each entry resolves to a promoted invariant (substrate-tier or contracts-tier per Spec 9.2)
4. `post_condition_observation_spec` is present and has a realistic `feedback_pathway` (i.e., sensor instance exists in tenant hardware inventory)
5. `safety_class` reviewer-list matches §2.1 for the declared class
6. `beekeeper_attestation` AnchorRef will be populated at merge time (placeholder accepted pre-merge)

Failures block merge until corrected. The CI checks are operational; A24 §1 makes the boundary structurally invalid if any check would fail post-merge, so a malformed boundary in CTH is rejected by Wyrd substrate even if it somehow bypassed CI.

---

## 6. Worked Examples

### 6.1 QBP NV-Center Laser Pulse

QBP wants to fire an NV-Center spin-control laser pulse during a Glide Phase experiment.

1. **Boundary registration (one-time):**
   ```
   tenant: qbp
   side_effect_class: LASER_PULSE
   pre_condition_invariants:
     - substrate-tier-theorem://wyrd/optical_power_envelope_NV_center
     - contracts-tier-invariant://qbp/glide_phase_pulse_window
     - autonomic-signal-check://no SAFETY_FLAG from federation > 0.3
   safety_class: HIGH
   ```
   Filed PR, reviewed by qbp-implementor + bma-implementor + wyrd-implementor + cross-tenant reader + Beekeeper. Merged → `NT_ACTUATION_BOUNDARY` written.

2. **Request:** QBP Conscious-A issues `NT_ACTUATION_REQUEST` with parameters `{duration_ns=50, power_mW=2.3, wavelength_nm=637}`.

3. **Gate:** Harness checks: optical_power_envelope (substrate-tier, evaluated TRUE), glide_phase_pulse_window (contracts-tier, evaluated TRUE — within current experiment slot), autonomic check (no SAFETY_FLAG), Beekeeper-halt (none active). PASS.

4. **Execute:** Hand off to laser-controller adapter; write `NT_ACTUATION_DISPATCHED`.

5. **Observation:** Photon-counting detector returns within 200ms; emits `NT_OBSERVATION{conformance=MATCH, measured_value=14 photons (expected 12–18), drift_magnitude=0.05}`.

6. **Downstream:** A18 ScoutQuery sees the observation immediately; QBP Conscious decides next pulse parameters; Honing Loop accumulates drift trend for laser model.

### 6.2 Sharp Butler HVAC Relay

Sharp Butler wants to close a relay activating the HVAC heating loop.

1. **Boundary registration (one-time):**
   ```
   tenant: sharp-butler
   side_effect_class: HVAC_RELAY
   pre_condition_invariants:
     - contracts-tier-invariant://sb/household_power_budget_reserve
     - contracts-tier-invariant://sb/quiet_hours_no_relay_action
     - autonomic-signal-check://no POWER_PRESSURE > 0.85 from federation
   safety_class: ROUTINE
   ```

2. **Request:** Sharp Butler Conscious-A issues request `{relay_id=hvac-zone-3, action=close, duration_min=45}`.

3. **Gate:** Power reserve TRUE (sufficient reserve). Quiet hours TRUE (it's 16:00). Autonomic check: A22 POWER_PRESSURE signal from federation = 0.91 → **FAIL at layer 3**. Refuse.

4. **Refuse:** `NT_ACTUATION_REFUSED{refusal_layer=3, refusal_reason="federation POWER_PRESSURE=0.91 > 0.85 threshold from source=mobius-fusion"}`. Sharp Butler Conscious receives refusal.

5. **Downstream:** Conscious decides — wait 15 minutes for federation pressure to subside, or surface HoningPrompt to Beekeeper. The refusal *protected* the federation power budget; this is the system working.

### 6.3 Möbius Fusion Reactor Plasma Field (SAFETY_CRITICAL example)

Möbius wants to ramp plasma containment field by 0.3T.

1. **Boundary registration:** SAFETY_CRITICAL class. Reviewers: mobius-implementor + bma-implementor + wyrd-implementor + qbp-cu-implementor + cth-implementor + 72h cooldown + Beekeeper HVR.

2. **Request → gate → execute → observe** as above.

3. **Failure case:** Sensor reports `SENSOR_FAULT` (containment-field magnetometer unresponsive). Auto-`NT_BEEKEEPER_HALT` on this boundary; mobius-implementor and Beekeeper paged within 30s. No further plasma-field operations until human inspection + `NT_BEEKEEPER_HALT_LIFTED`.

---

## 7. Tenant Onboarding to Actuation Protocol

A tenant joins the actuation protocol with:

1. Tenant declares its hardware inventory in `repo-<tenant>:hardware/`
2. Tenant harness implements the §2 registration API + §3 request handling + §4 observation re-entry
3. First boundary registration is end-to-end Beekeeper-supervised regardless of `safety_class` (first-time-supervision rule)
4. After 3 successful boundary registrations, tenant operates autonomously within the §2.1 reviewer matrix
5. Tenant publishes its autonomic signal subscriber profile (per A22 §3 rule 2) including SAFETY_FLAG subscriptions from federation

---

## 8. Updated Design Principles

1. **One protocol, four surfaces:** registration / request / execute / observe — each with fixed shape and explicit failure mode.
2. **Reviewer-list scales with safety_class.** ROUTINE / HIGH / SAFETY_CRITICAL each carry a distinct §I4 matrix.
3. **Refusals are first-class events.** No silent drops; every refusal records its layer, reason, and retry advice.
4. **Observation timeout halts SAFETY_CRITICAL boundaries automatically.** Resumption is human-deliberative.
5. **Boundary registration is constitutional; re-class is operational.** First hand in a class needs Beekeeper attestation; subsequent hands in same class follow contracts-tier path.
6. **CI enforces; A24 §1 structurally forbids.** Belt-and-suspenders pattern.

---

## 9. Sequencing Notes

- **Crawl:** Protocol design only; no live actuation. BMA cells not yet operational; tenant hardware adapters not yet implemented.
- **Toddle:** First boundary registration end-to-end: likely a low-stakes class (DATASET_PUBLICATION for QBP arXiv upload). Validates the registration → CI → Beekeeper-attestation → CTH-write loop.
- **Walk:** First HIGH and SAFETY_CRITICAL boundaries register (QBP LASER_PULSE; Sharp Butler HVAC_RELAY; Möbius REACTOR_PLASMA_FIELD when reactor operational). Autonomic-signal-check integration with A22 live.
- **Run:** Routine multi-tenant actuation; Honing Loop drift-trend analysis surfaces hardware-model refinement opportunities.

---

*BMA Spec Addendum 9.5 | May 2026*
*Co-Authored-By: James Paget Butler (Beekeeper) & Claude Opus 4.7 (qbp-architecture)*

---

## References (with paths so the beekeeper can find every cited document)

| Reference | Path / URL |
|---|---|
| Theory companion A24.0 Hardware-Boundary Semantics | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-24_0-Hardware-Boundary-Semantics.md` |
| A18.0 Hypergraph Access Pattern (Conscious Stance owns actuation) | `/home/prime/Documents/BMA/theory/hypergraph-inference/BMA-Theory-Addendum-18_0-Hypergraph-Access-Pattern.md` |
| A20.0 Pentagon Pod Cognitive Frame (Conscious / Subconscious split; halt is reflexive) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-20_0-Pentagon-Pod-Cognitive-Frame.md` |
| A21.0 Federation Knowledge-Sovereignty Frame (substrate-tier invariants for pre-conditions) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-21_0-Federation-Knowledge-Sovereignty-Frame.md` |
| A22.0 Cross-Tenant Autonomic Translation Layer (SAFETY_FLAG halt; subscriber gate) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-22_0-Cross-Tenant-Autonomic-Translation-Layer.md` |
| A23.0 Research-Aid Frame (NT_OBSERVATION as scaffold input) | `/home/prime/Documents/inter/theory/BMA-Theory-Addendum-23_0-Research-Aid-Frame.md` |
| Spec Addendum 9.1 Pentagon Pod Architecture | `/home/prime/Documents/BMA/spec/BMA-Spec-Addendum-9_1-Pentagon-Pod-Architecture.md` |
| Spec Addendum 9.2 Federation Lean Promotion Protocol (substrate-tier §2; contracts-tier §13) | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_2-Federation-Lean-Promotion-Protocol.md` |
| Spec Addendum 9.4 Research-Aid Protocol | `/home/prime/Documents/inter/spec/BMA-Spec-Addendum-9_4-Research-Aid-Protocol.md` |
| BMA Spec Consolidated v9.0 (L3f tenant boundary §10.7; sleep cycle §11) | `/home/prime/Documents/BMA/spec/BMA-Spec-Consolidated-v9_0.md` |
| BMA Governance Document | `/home/prime/Documents/BMA/governance/BMA-Governance-Document.md` |
| Workspace phase architecture (federation phase table; Walk / Run hardware activation) | `/home/prime/Documents/inter/workspace-phase-architecture.md` |

*Traceability: A24.0 (algebraic frame), A18.0 §3 / A20.0 §0.2 (Conscious owns actuation), A21.0 §11 (substrate-tier invariants), A22.0 §2-§3 (autonomic signal check; SAFETY_FLAG halt), Gemini-3-Pro review 2026-05-14 point 5.*
