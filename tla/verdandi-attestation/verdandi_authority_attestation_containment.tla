---- MODULE verdandi_authority_attestation_containment ----
\* STATUS: SUPERSEDED — ~(consumed /\ ~final) shown necessary-not-sufficient by red-team C1. Replaced by verdandi_authority_attestation_containment_witnessed.tla. Kept as audit trail — do not run as current.
\* NT_NOTARY — Verðandi Authority attestation (CONTAINMENT / confirmation-depth).
\* Author: notary-implementor (Notary Phase 1, competency #3). Dispatch: qbp-architecture seq=1370.
\* CANONICAL temporal base going forward — supersedes verdandi_authority_attestation_temporal.tla's
\* admission-race framing (kept as historical record). qbp-oppenheimer EXTENDS + red-teams on top.
\* floor-model = from-prose (Addendum B not on disk); reframe adopted into Addendum B (seq=1370).
\*
\* THE REFRAME (seq=1368/1370): admission is NOT the harm — admission is safe. The harm is IRREVERSIBLE
\* CONSUMPTION of a NOT-YET-FINAL admission. Finality = the admission survives a confirmation window
\* (>= T_detect+T_propagate+T_margin) uncontained. `Delayable` folds architect results #2 (finality
\* window) and #3 (un-delayable actions) into ONE model:
\*   Delayable=TRUE   -> the irreversible action WAITS for finality -> containment governs it (INV holds).
\*   Delayable=FALSE  -> un-delayable/time-critical action CANNOT wait -> reachable consume-before-final
\*                       -> post-merge invalidation provably cannot govern it -> needs actuator multisig.

EXTENDS Naturals

CONSTANTS
  DetectLatency,   \* D: witnessed events until a theft is detected and containment becomes DUE
  AdmitSteps,      \* K: witnessed serialized merge steps to complete A.7 admission
  ConfWindow,      \* W: confirmation depth — ticks an admission must survive uncontained to be FINAL
  RevokePriority,  \* TRUE = containment serialized AHEAD of further admission (§6.4 HOLD, not auto-revoke)
  Delayable        \* TRUE = downstream irreversible action can WAIT for finality; FALSE = un-delayable

ASSUME Bounds == DetectLatency \in Nat /\ AdmitSteps \in (Nat \ {0}) /\ ConfWindow \in (Nat \ {0})
ASSUME Flags  == RevokePriority \in BOOLEAN /\ Delayable \in BOOLEAN

VARIABLES
  stolen, detect, revokeDue, revoked, admit, admitted, confirm, final, consumed

vars == << stolen, detect, revokeDue, revoked, admit, admitted, confirm, final, consumed >>

Init ==
  /\ stolen = FALSE /\ detect = 0 /\ revokeDue = FALSE /\ revoked = FALSE
  /\ admit = 0 /\ admitted = FALSE /\ confirm = 0 /\ final = FALSE /\ consumed = FALSE

\* Theft is OPTIONAL — if it never fires, the run is honest and the admission finalizes normally.
Steal ==
  /\ ~stolen /\ stolen' = TRUE
  /\ UNCHANGED << detect, revokeDue, revoked, admit, admitted, confirm, final, consumed >>

DetectTick ==
  /\ stolen /\ ~revokeDue /\ detect < DetectLatency
  /\ detect' = detect + 1 /\ revokeDue' = (detect + 1 >= DetectLatency)
  /\ UNCHANGED << stolen, revoked, admit, admitted, confirm, final, consumed >>

\* Containment applied — one atomic river event (§6.4 HOLD-pending-investigation, or revoke).
Contain ==
  /\ revokeDue /\ ~revoked /\ revoked' = TRUE
  /\ UNCHANGED << stolen, detect, revokeDue, admit, admitted, confirm, final, consumed >>

\* One witnessed serialized admission step. If stolen, the step is observable -> advances detection.
\* RevokePriority: a DUE containment blocks further admission.
AdmitStep ==
  /\ ~revoked /\ admit < AdmitSteps
  /\ (RevokePriority => ~revokeDue)
  /\ admit' = admit + 1 /\ admitted' = (admit + 1 >= AdmitSteps)
  /\ IF stolen /\ detect < DetectLatency
       THEN detect' = detect + 1 /\ revokeDue' = (detect + 1 >= DetectLatency)
       ELSE UNCHANGED << detect, revokeDue >>
  /\ UNCHANGED << stolen, revoked, confirm, final, consumed >>

\* Confirmation depth: an uncontained admission that survives W ticks becomes FINAL.
\* Containment (revoked) during the window blocks finalization (the ~revoked guard).
ConfirmTick ==
  /\ admitted /\ ~revoked /\ ~final /\ confirm < ConfWindow
  /\ confirm' = confirm + 1 /\ final' = (confirm + 1 >= ConfWindow)
  /\ UNCHANGED << stolen, detect, revokeDue, revoked, admit, admitted, consumed >>

\* Irreversible downstream action. Delayable actions WAIT for finality; un-delayable ones cannot.
Consume ==
  /\ admitted /\ ~consumed
  /\ (Delayable => final)
  /\ consumed' = TRUE
  /\ UNCHANGED << stolen, detect, revokeDue, revoked, admit, admitted, confirm, final >>

Next == Steal \/ DetectTick \/ Contain \/ AdmitStep \/ ConfirmTick \/ Consume

Spec == Init /\ [][Next]_vars

\* PRIMARY (seq=1370, adopted into Addendum B): no irreversible consumption of a not-yet-final admission.
INV_ContainmentBeatsExploit == ~(consumed /\ ~final)
====
