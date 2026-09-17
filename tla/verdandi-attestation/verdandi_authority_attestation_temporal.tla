---- MODULE verdandi_authority_attestation_temporal ----
\* NT_NOTARY — Verðandi Authority attestation (TEMPORAL side): INV_RevokeBeatsExploit.
\* Author: notary-implementor (Notary Phase 1, competency #3). Dispatch: qbp-architecture seq=1358.
\* Purpose: INDEPENDENT reproduction (heterogeneous cross-check) of qbp-oppenheimer's seq=1361 finding
\* that INV_RevokeBeatsExploit is BROKEN-as-premised, holding iff (a) revocation is serialized AHEAD of
\* other events (RevokePriority) AND (b) the admission window exceeds the detection latency (K > D).
\*
\* A.7 premise baked in: admission is WITNESSED serialized (each AdmitStep is observable, so it also
\* advances detection). The two named conditions are exposed as the switch RevokePriority and the
\* constants (DetectLatency D, AdmitSteps K). floor-model = from-prose (Addendum B not on disk).

EXTENDS Naturals

CONSTANTS
  DetectLatency,   \* D: witnessed events until detection completes and a revoke becomes DUE
  AdmitSteps,      \* K: witnessed serialized merge steps to complete A.7 admission
  RevokePriority   \* TRUE = the river serializes a DUE revoke ahead of any further admit (A.7 discipline).
                   \* FALSE = revoke only "eventually" (fairness) — admit may race past it.

ASSUME PosBounds  == DetectLatency \in Nat /\ AdmitSteps \in (Nat \ {0})
ASSUME PrioIsBool == RevokePriority \in BOOLEAN

VARIABLES
  stolen,     \* the T2 key-store has been stolen
  detect,     \* witnessed-event counter toward detection (0..D)
  revokeDue,  \* detection completed; a revoke is pending on the river
  revoked,    \* the revoke river-event has been applied
  admit,      \* witnessed serialized admission steps completed (0..K)
  admitted    \* the stolen key completed A.7 admission (the exploit payoff)

vars == << stolen, detect, revokeDue, revoked, admit, admitted >>

Init ==
  /\ stolen = FALSE
  /\ detect = 0
  /\ revokeDue = FALSE
  /\ revoked = FALSE
  /\ admit = 0
  /\ admitted = FALSE

Steal ==
  /\ ~stolen
  /\ stolen' = TRUE
  /\ UNCHANGED << detect, revokeDue, revoked, admit, admitted >>

\* Detection may also advance on its own (out-of-band monitoring), reaching DUE at D.
DetectTick ==
  /\ stolen /\ ~revokeDue /\ detect < DetectLatency
  /\ detect' = detect + 1
  /\ revokeDue' = (detect + 1 >= DetectLatency)
  /\ UNCHANGED << stolen, revoked, admit, admitted >>

\* The river applies a due revocation (one atomic event).
Revoke ==
  /\ revokeDue /\ ~revoked
  /\ revoked' = TRUE
  /\ UNCHANGED << stolen, detect, revokeDue, admit, admitted >>

\* Attacker drives one witnessed serialized admission step with the stolen key.
\* A.7 witnessed premise: the step is observable, so it ALSO advances detection.
\* RevokePriority: if a revoke is DUE, the step is blocked until Revoke fires.
AdmitStep ==
  /\ stolen /\ ~revoked /\ admit < AdmitSteps
  /\ (RevokePriority => ~revokeDue)
  /\ admit' = admit + 1
  /\ admitted' = (admit + 1 >= AdmitSteps)
  /\ IF detect < DetectLatency
       THEN /\ detect' = detect + 1
            /\ revokeDue' = (detect + 1 >= DetectLatency)
       ELSE UNCHANGED << detect, revokeDue >>
  /\ UNCHANGED << stolen, revoked >>

Next == Steal \/ DetectTick \/ Revoke \/ AdmitStep

Spec == Init /\ [][Next]_vars

\* INV_RevokeBeatsExploit: the stolen key NEVER completes admission — revocation always beats the exploit.
INV_RevokeBeatsExploit == ~admitted
====
