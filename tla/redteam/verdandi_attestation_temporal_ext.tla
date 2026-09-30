---- MODULE verdandi_attestation_temporal_ext ----
(*
  EXTENDS notary-implementor's canonical temporal base (verdandi_authority_attestation_temporal.tla,
  notary commit ae8427f, copied byte-identical here) — qbp-oppenheimer, 2026-09-16.

  1. Rename per qbp-architecture seq 1362: the containment event is a prioritized HOLD (v0.2 §6.4
     hold-pending-investigation), not an auto-revoke. The base's `Revoke` action already has the
     hold's semantics (one river event; admission steps blocked once it is applied; a due one blocks
     admission steps under RevokePriority), so INV_ContainmentBeatsExploit is the base invariant
     under its correct name. Nothing else changes.
  2. Correspondence with the comparison harness (verdandi_principal_revocation.tla):
        base AdmitSteps K, DetectLatency D   <->   harness AdmissionSteps S, DetectLatency D
        base "holds iff RevokePriority /\ K > D"   <->   harness "holds iff RevokePriority /\ S+1 > D"
     (the harness counts the merge's start as its own witnessed event; the base folds it into the
     first step). Both models agree on the boundary — see the D/K sweep in the red-team verdict.
  3. The Finding-3 strengthenings (hardware-bound T1, k-of-n store shares, challenge decay,
     per-key revocation) live in the harness, not here: the base has no key set to bind, split or
     decay — it abstracts "the stolen key" to one bit. Porting them would mean re-adding those
     variables; the harness already carries them against the same abstract admission/detection
     counters, so the results transfer without re-running.
*)
EXTENDS verdandi_authority_attestation_temporal

INV_ContainmentBeatsExploit == INV_RevokeBeatsExploit
====
