---- MODULE verdandi_attestation_containment_plants ----
(*
  RED-TEAM PLANTS against notary-implementor's canonical CONTAINMENT module
  (verdandi_authority_attestation_containment.tla, notary commit 586ce56, copied byte-identical).
  Breaker: qbp-oppenheimer, 2026-09-16.

  C1 Is the reframed invariant ~(consumed /\ ~final) SUFFICIENT? In the base, ConfirmTick does not
     advance detection and DetectTick is never forced: after a stolen-key admission the window can
     elapse with detection stalled, the admission becomes FINAL, and a delayable Consume fires. The
     base invariant HOLDS while the thief's belief is irreversibly consumed. The threat-model
     invariant is INV_NoTaintedConsumption == ~(consumed /\ tainted), where `tainted` is a history
     variable: some admission step was witnessed while the store was stolen. (A first version used
     `stolen` instead of `tainted` and wrongly flagged honest admissions made before a later theft.)
  C2 Fix candidate: confirmation ticks are WITNESSED events (they advance detection) and a DUE
     containment blocks finalization as it blocks admission; then with W >= D the theft is detected
     before finality and containment lands first. Switch: ConfirmWitnessed.
*)
EXTENDS Naturals

CONSTANTS DetectLatency, AdmitSteps, ConfWindow, RevokePriority, Delayable, ConfirmWitnessed
ASSUME DetectLatency \in Nat /\ AdmitSteps \in (Nat \ {0}) /\ ConfWindow \in (Nat \ {0})

VARIABLES stolen, detect, revokeDue, revoked, admit, admitted, confirm, final, consumed, tainted
vars == << stolen, detect, revokeDue, revoked, admit, admitted, confirm, final, consumed, tainted >>

Init ==
  /\ stolen = FALSE /\ detect = 0 /\ revokeDue = FALSE /\ revoked = FALSE
  /\ admit = 0 /\ admitted = FALSE /\ confirm = 0 /\ final = FALSE /\ consumed = FALSE
  /\ tainted = FALSE

Steal ==
  /\ ~stolen /\ stolen' = TRUE
  /\ UNCHANGED << detect, revokeDue, revoked, admit, admitted, confirm, final, consumed, tainted >>

DetectTick ==
  /\ stolen /\ ~revokeDue /\ detect < DetectLatency
  /\ detect' = detect + 1 /\ revokeDue' = (detect + 1 >= DetectLatency)
  /\ UNCHANGED << stolen, revoked, admit, admitted, confirm, final, consumed, tainted >>

Contain ==
  /\ revokeDue /\ ~revoked /\ revoked' = TRUE
  /\ UNCHANGED << stolen, detect, revokeDue, admit, admitted, confirm, final, consumed, tainted >>

\* Base AdmitStep + the taint history bit (a step witnessed while stolen taints the admission).
AdmitStep ==
  /\ ~revoked /\ admit < AdmitSteps
  /\ (RevokePriority => ~revokeDue)
  /\ admit' = admit + 1 /\ admitted' = (admit + 1 >= AdmitSteps)
  /\ tainted' = (tainted \/ stolen)
  /\ IF stolen /\ detect < DetectLatency
       THEN detect' = detect + 1 /\ revokeDue' = (detect + 1 >= DetectLatency)
       ELSE UNCHANGED << detect, revokeDue >>
  /\ UNCHANGED << stolen, revoked, confirm, final, consumed >>

\* Base ConfirmTick, optionally witnessed (advances detection) and blocked by a DUE containment.
ConfirmTick ==
  /\ admitted /\ ~revoked /\ ~final /\ confirm < ConfWindow
  /\ (ConfirmWitnessed /\ RevokePriority => ~revokeDue)
  /\ confirm' = confirm + 1 /\ final' = (confirm + 1 >= ConfWindow)
  /\ IF ConfirmWitnessed /\ stolen /\ detect < DetectLatency
       THEN detect' = detect + 1 /\ revokeDue' = (detect + 1 >= DetectLatency)
       ELSE UNCHANGED << detect, revokeDue >>
  /\ UNCHANGED << stolen, revoked, admit, admitted, consumed, tainted >>

Consume ==
  /\ admitted /\ ~consumed
  /\ (Delayable => final)
  /\ consumed' = TRUE
  /\ UNCHANGED << stolen, detect, revokeDue, revoked, admit, admitted, confirm, final, tainted >>

Next == Steal \/ DetectTick \/ Contain \/ AdmitStep \/ ConfirmTick \/ Consume
Spec == Init /\ [][Next]_vars

INV_ContainmentBeatsExploit == ~(consumed /\ ~final)   \* the base's invariant, verbatim
INV_NoTaintedConsumption   == ~(consumed /\ tainted)   \* the threat model's
====
