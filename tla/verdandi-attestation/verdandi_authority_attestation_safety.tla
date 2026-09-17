---- MODULE verdandi_authority_attestation_safety ----
\* STATUS: pre-P1 base (assembling-set floor). SUPERSEDED for the holder-set floor by verdandi_authority_attestation_safety_holder.tla (architect seq=1374, option b). Kept as cycle-5 audit trail — do not run as current.
\* NT_NOTARY — Verðandi Authority attestation-tier / T1-floor threat model (SAFETY side)
\* Author: notary-implementor (Notary Phase 1, competency #3). Dispatch: qbp-architecture seq=1358.
\* Red-teamed by: qbp-oppenheimer (author writes / breaker breaks — §8 shape).
\* floor-model = FROM-PROSE (Addendum B not on disk) — architect seq=1358 option (a); re-stamp on ratification.
\*
\* Checks INV_NoSubFloorConstruction (A.4 constructed-cap discipline + B.6 floor), and — via two
\* switchable MUTATIONS — demonstrates that the floor AND the A.1 verb-closure are each LOAD-BEARING
\* (not a vacuous pass): flip either off and TLC must produce a sub-floor construction counterexample.

EXTENDS Naturals, FiniteSets

CONSTANTS
  T1Principals,    \* self-hosted PoRs; each carries a WITNESSED, pairwise-distinct substrate_hash
  T2Principals,    \* API-hosted PoRs; DECLARED model_id, share ONE harness key-store
  EnforceFloor,    \* TRUE = B.6 floor active. FALSE = MUTATION (expect violation).
  AllowUpwardVerb  \* FALSE = A.4 verb-closure (grant/project/compose stay within grantable+priority).
                   \* TRUE = MUTATION: laundering verb can cross grantable -> constructed (expect violation).

Principals == T1Principals \cup T2Principals

ASSUME DisjointTiers == T1Principals \cap T2Principals = {}
ASSUME FlagsAreBool  == EnforceFloor \in BOOLEAN /\ AllowUpwardVerb \in BOOLEAN

\* T1 substrate hash is distinct per principal (hash = principal); T2 have no distinct hash.
Hash(p)  == p
T1Of(S)  == S \cap T1Principals

\* B.6 floor: an assembling set S may construct a high-stakes cap only if it holds
\* >= 2 T1 PoRs with pairwise-DISTINCT substrate_hash. No all-T2 set qualifies, any size/trust.
FloorSatisfied(S) == Cardinality({ Hash(p) : p \in T1Of(S) }) >= 2

VARIABLES
  compromised,    \* principals whose signing key the attacker controls
  grantableFrom,  \* principals from which the attacker has acquired a grantable cap
  constructed     \* set of assembling-sets that have produced a CONSTRUCTED high-stakes cap

vars == << compromised, grantableFrom, constructed >>

TypeOK ==
  /\ compromised   \subseteq Principals
  /\ grantableFrom \subseteq Principals
  /\ constructed   \subseteq SUBSET Principals

Init ==
  /\ compromised   = {}
  /\ grantableFrom = {}
  /\ constructed   = {}

\* Finding 1: stealing the shared T2 key-store compromises ALL T2 at once (one-theft total).
StealStore ==
  /\ ~(T2Principals \subseteq compromised)
  /\ compromised' = compromised \cup T2Principals
  /\ UNCHANGED << grantableFrom, constructed >>

\* Stealing a hardware-bound T1 key compromises exactly one principal (modeled available, per-principal).
StealT1(p) ==
  /\ p \in T1Principals
  /\ p \notin compromised
  /\ compromised' = compromised \cup {p}
  /\ UNCHANGED << grantableFrom, constructed >>

\* The attacker acquires a grantable cap from a principal it controls.
AcquireGrantable(p) ==
  /\ p \in compromised
  /\ p \notin grantableFrom
  /\ grantableFrom' = grantableFrom \cup {p}
  /\ UNCHANGED << compromised, constructed >>

\* A.4 construct verb: the ONLY producer of a high-stakes cap. Floor-gated when EnforceFloor.
ConstructHighStakes(S) ==
  /\ S \subseteq compromised
  /\ S # {}
  /\ (EnforceFloor => FloorSatisfied(S))
  /\ S \notin constructed
  /\ constructed' = constructed \cup {S}
  /\ UNCHANGED << compromised, grantableFrom >>

\* A.1 laundering: compose/project grantable caps upward into a high-stakes cap, BYPASSING the floor.
\* Enabled ONLY under the AllowUpwardVerb mutation — the base model's verb-closure forbids it.
LaunderUpward(S) ==
  /\ AllowUpwardVerb
  /\ S \subseteq grantableFrom
  /\ S # {}
  /\ S \notin constructed
  /\ constructed' = constructed \cup {S}
  /\ UNCHANGED << compromised, grantableFrom >>

Next ==
  \/ StealStore
  \/ \E p \in T1Principals   : StealT1(p)
  \/ \E p \in Principals     : AcquireGrantable(p)
  \/ \E S \in SUBSET compromised   : ConstructHighStakes(S)
  \/ \E S \in SUBSET grantableFrom : LaunderUpward(S)

Spec == Init /\ [][Next]_vars

\* SAFETY: every constructed high-stakes cap's assembling set satisfies the B.6 floor.
INV_NoSubFloorConstruction == \A S \in constructed : FloorSatisfied(S)
====
