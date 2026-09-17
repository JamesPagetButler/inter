---- MODULE verdandi_authority_attestation_containment_witnessed ----
\* STATUS: CANONICAL-CURRENT — containment ~(consumed /\ tainted) (C1/C2 corrected).
\* NT_NOTARY — Verðandi Authority attestation CONTAINMENT, CORRECTED (C1/C2 fix).
\* Author: notary-implementor (Notary Phase 1, competency #3). Dispatch: qbp-architecture seq=1376.
\* Supersedes verdandi_authority_attestation_containment.tla, whose ~(consumed /\ ~final) invariant
\* qbp-oppenheimer's C1 red-team (seq=1375) showed NECESSARY-BUT-NOT-SUFFICIENT: silent confirmation
\* ticks let a stolen admission ride out the window, finalize, and be consumed while that invariant held.
\* Audit trail: temporal (admission-race) -> containment (~(consumed/\~final), C1-broken) -> THIS.
\*
\* Corrected threat-model invariant (architect seq=1376, into Addendum B):
\*   INV_ContainmentBeatsExploit == ~(consumed /\ tainted)
\*   tainted = an admission step was witnessed while stolen (history bit). `stolen` alone is wrong —
\*   it flags honest admissions completed before a later theft.
\* C2 conditions, all made load-bearing here via switches:
\*   (1) WitnessedConfirm — confirmation ticks advance detection (not silent time);
\*   (2) RevokePriority — a due containment halts FINALIZATION as well as admission;
\*   (3) W >= D (window >= detection latency, independent of K).
\* floor-model = from-prose (Addendum B not on disk).

EXTENDS Naturals

CONSTANTS
  DetectLatency,    \* D
  AdmitSteps,       \* K
  ConfWindow,       \* W
  RevokePriority,   \* a due containment blocks further admission AND finalization
  Delayable,        \* downstream irreversible action can wait for finality
  WitnessedConfirm  \* TRUE = confirmation ticks advance detection (C1 fix); FALSE = silent (the C1 bug)

ASSUME Bounds == DetectLatency \in Nat /\ AdmitSteps \in (Nat \ {0}) /\ ConfWindow \in (Nat \ {0})
ASSUME Flags  == RevokePriority \in BOOLEAN /\ Delayable \in BOOLEAN /\ WitnessedConfirm \in BOOLEAN

VARIABLES
  stolen, tainted, detect, revokeDue, revoked, admit, admitted, confirm, final, consumed

vars == << stolen, tainted, detect, revokeDue, revoked, admit, admitted, confirm, final, consumed >>

Init ==
  /\ stolen = FALSE /\ tainted = FALSE /\ detect = 0 /\ revokeDue = FALSE /\ revoked = FALSE
  /\ admit = 0 /\ admitted = FALSE /\ confirm = 0 /\ final = FALSE /\ consumed = FALSE

Steal ==
  /\ ~stolen /\ stolen' = TRUE
  /\ UNCHANGED << tainted, detect, revokeDue, revoked, admit, admitted, confirm, final, consumed >>

DetectTick ==
  /\ stolen /\ ~revokeDue /\ detect < DetectLatency
  /\ detect' = detect + 1 /\ revokeDue' = (detect + 1 >= DetectLatency)
  /\ UNCHANGED << stolen, tainted, revoked, admit, admitted, confirm, final, consumed >>

Contain ==
  /\ revokeDue /\ ~revoked /\ revoked' = TRUE
  /\ UNCHANGED << stolen, tainted, detect, revokeDue, admit, admitted, confirm, final, consumed >>

\* Admission step. If stolen: the admission is TAINTED, and the witnessed step advances detection.
\* RevokePriority: a due containment blocks the step.
AdmitStep ==
  /\ ~revoked /\ admit < AdmitSteps
  /\ (RevokePriority => ~revokeDue)
  /\ admit' = admit + 1 /\ admitted' = (admit + 1 >= AdmitSteps)
  /\ tainted' = (tainted \/ stolen)
  /\ IF stolen /\ detect < DetectLatency
       THEN detect' = detect + 1 /\ revokeDue' = (detect + 1 >= DetectLatency)
       ELSE UNCHANGED << detect, revokeDue >>
  /\ UNCHANGED << stolen, revoked, confirm, final, consumed >>

\* Confirmation depth. C1 FIX: a confirmation tick is WITNESSED — it advances detection (when stolen),
\* so the window is filled with detection work, not silent time. RevokePriority halts finalization on a
\* due containment. A containment (revoked) blocks finalization (the ~revoked guard).
ConfirmTick ==
  /\ admitted /\ ~revoked /\ ~final /\ confirm < ConfWindow
  /\ (RevokePriority => ~revokeDue)
  /\ confirm' = confirm + 1 /\ final' = (confirm + 1 >= ConfWindow)
  /\ IF WitnessedConfirm /\ stolen /\ detect < DetectLatency
       THEN detect' = detect + 1 /\ revokeDue' = (detect + 1 >= DetectLatency)
       ELSE UNCHANGED << detect, revokeDue >>
  /\ UNCHANGED << stolen, tainted, revoked, admit, admitted, consumed >>

Consume ==
  /\ admitted /\ ~consumed
  /\ (Delayable => final)
  /\ consumed' = TRUE
  /\ UNCHANGED << stolen, tainted, detect, revokeDue, revoked, admit, admitted, confirm, final >>

Next == Steal \/ DetectTick \/ Contain \/ AdmitStep \/ ConfirmTick \/ Consume

Spec == Init /\ [][Next]_vars

\* CORRECTED threat-model invariant (seq=1376): no irreversible consumption of a THEFT-TAINTED admission.
INV_ContainmentBeatsExploit == ~(consumed /\ tainted)
====
