---- MODULE verdandi_authority_attestation_safety_holder ----
\* STATUS: CANONICAL-CURRENT — safety / holder-set floor (option b, floor-gated narrowing).
\* NT_NOTARY — Verðandi Authority attestation SAFETY, HOLDER-SET form (A.4 narrowing verb).
\* Author: notary-implementor (Notary Phase 1, competency #3). Dispatch: qbp-architecture seq=1374.
\* Extends the safety analysis to cover qbp-oppenheimer's P1 red-team finding (seq=1373).
\* Architect RULING seq=1374: the floor is a property of EVERY HOLDER SET, not just the assembling set
\*   (option b) — A.4's narrow-to-smaller-collective verb MUST preserve the floor. This becomes a B.6
\*   clause. GateNarrow=TRUE models the ruled design; GateNarrow=FALSE reproduces the P1 break, so the
\*   gate is shown load-bearing. floor-model = from-prose (Addendum B not on disk).

EXTENDS Naturals, FiniteSets

CONSTANTS
  T1Principals,  \* self-hosted PoRs; distinct witnessed substrate_hash
  T2Principals,  \* API-hosted PoRs; shared key-store
  GateNarrow     \* TRUE = A.4 narrowing must preserve the floor (architect ruling, option b).
                 \* FALSE = un-gated narrowing (reproduces the P1 counterexample) — shows the gate load-bearing.

Principals == T1Principals \cup T2Principals
ASSUME DisjointTiers == T1Principals \cap T2Principals = {}
ASSUME GateIsBool    == GateNarrow \in BOOLEAN

Hash(p)  == p
T1Of(S)  == S \cap T1Principals
FloorSatisfied(S) == Cardinality({ Hash(p) : p \in T1Of(S) }) >= 2

\* A constructed high-stakes cap: its provenance (assembling) set and its current holder set.
Cap == [prov: SUBSET Principals, holder: SUBSET Principals]

VARIABLES constructed   \* set of live constructed high-stakes caps
vars == << constructed >>

Init == constructed = {}

\* A.4 construct verb: floor-gated on the assembling set; holder starts = assembling set.
ConstructHighStakes(S) ==
  /\ FloorSatisfied(S)
  /\ [prov |-> S, holder |-> S] \notin constructed
  /\ constructed' = constructed \cup {[prov |-> S, holder |-> S]}

\* A.4 narrow verb: narrow a cap's holder to a SMALLER COLLECTIVE (>=2 members, never an individual).
\* GateNarrow: the ruled B.6 clause — the narrowed holder must still satisfy the floor.
Narrow(c, H) ==
  /\ c \in constructed
  /\ H \subseteq c.holder
  /\ Cardinality(H) >= 2          \* A.4: never to an individual
  /\ H # c.holder                 \* strictly smaller
  /\ (GateNarrow => FloorSatisfied(H))
  /\ [prov |-> c.prov, holder |-> H] \notin constructed
  /\ constructed' = (constructed \ {c}) \cup {[prov |-> c.prov, holder |-> H]}

Next ==
  \/ \E S \in SUBSET Principals : ConstructHighStakes(S)
  \/ \E c \in constructed : \E H \in SUBSET c.holder : Narrow(c, H)

Spec == Init /\ [][Next]_vars

\* HOLDER-SET safety (architect option b): every LIVE constructed cap's HOLDER set satisfies the floor.
INV_NoSubFloorHolder == \A c \in constructed : FloorSatisfied(c.holder)
====
