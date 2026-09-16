---- MODULE verdandi_attestation_safety_plants ----
(*
  RED-TEAM PLANTS against notary-implementor's canonical safety base
  (verdandi_authority_attestation_safety.tla, notary commit ae8427f, copied byte-identical
  into this directory so EXTENDS resolves). Breaker: qbp-oppenheimer, 2026-09-16.

  P1 NarrowCollective — A.4 says a constructed cap "narrows only to smaller collectives, never to
     individuals". The base has no narrowing verb. This plant adds the LEGITIMATE verb (narrow a
     constructed cap's holder set to a strict subset that is still a collective, |S'| >= 2) and
     asks whether the floor survives narrowing. If the floor is a property of the ASSEMBLING set
     (provenance) only, a narrowed cap held by a sub-floor collective exists — is that a hole or
     by design? (Design question for Addendum B; the model shows the consequence either way.)
  P2 Substrate cloning — the base defines Hash(p) == p, so "pairwise-distinct" is vacuous. This
     plant lets a set ClonedT1 of T1 principals share ONE hash (a cloned self-hosted instance).
  P3 Hardware-bound premise — the base makes StealT1 available, so INV_NoSubFloorConstruction is
     satisfied even when the attacker owns every T1 key (its constructions satisfy the floor!).
     The security claim needs INV_NoAttackerConstruction under HardwareBound (StealT1 disabled).
  P4 n = 3 + 3 — uniform-in-n probe at a larger instance.
*)
EXTENDS verdandi_authority_attestation_safety

CONSTANTS
  AllowNarrow,     \* P1: the A.4 collective-narrowing verb is available
  FloorOnNarrow,   \* P1: narrowing is floor-gated (the narrowed holder set must still satisfy the floor)
  ClonedT1,        \* P2: T1 principals sharing one substrate hash (subset of T1Principals; {} = none)
  HardwareBound    \* P3: T1 keys are non-extractable (StealT1 disabled)

ASSUME ClonedT1 \subseteq T1Principals

\* P2: distinct-hash count with cloning — every cloned member contributes the SAME hash.
DistinctHashes(S) ==
  Cardinality((T1Of(S) \ ClonedT1)) + (IF (T1Of(S) \cap ClonedT1) = {} THEN 0 ELSE 1)
FloorSatisfiedC(S) == DistinctHashes(S) >= 2

VARIABLES held  \* holder sets of live constructed caps (after narrowing); initially = constructed

varsP == << compromised, grantableFrom, constructed, held >>

InitP == Init /\ held = {}

StealT1P(p) == ~HardwareBound /\ StealT1(p) /\ UNCHANGED held

\* Construct as in the base, but with the cloning-aware floor, and record the holder set.
ConstructP(S) ==
  /\ S \subseteq compromised
  /\ S # {}
  /\ (EnforceFloor => FloorSatisfiedC(S))
  /\ S \notin constructed
  /\ constructed' = constructed \cup {S}
  /\ held' = held \cup {S}
  /\ UNCHANGED << compromised, grantableFrom >>

\* P1: narrow a held constructed cap to a strict sub-collective (never an individual).
NarrowCollective(S, T) ==
  /\ AllowNarrow
  /\ S \in held
  /\ T \subseteq S /\ T # S /\ Cardinality(T) >= 2
  /\ (FloorOnNarrow => FloorSatisfiedC(T))
  /\ T \notin held
  /\ held' = held \cup {T}
  /\ UNCHANGED << compromised, grantableFrom, constructed >>

NextP ==
  \/ (StealStore /\ UNCHANGED held)
  \/ \E p \in T1Principals : StealT1P(p)
  \/ (\E p \in Principals : AcquireGrantable(p)) /\ UNCHANGED held
  \/ \E S \in SUBSET compromised : ConstructP(S)
  \/ (\E S \in SUBSET grantableFrom : LaunderUpward(S)) /\ UNCHANGED held
  \/ \E S \in held : \E T \in SUBSET S : NarrowCollective(S, T)

SpecP == InitP /\ [][NextP]_varsP

\* The base invariant, over assembling sets (unchanged), and its holder-set form.
INV_NoSubFloorAssembly == \A S \in constructed : FloorSatisfiedC(S)
INV_NoSubFloorHolder   == \A S \in held : FloorSatisfiedC(S)
\* P3: the security claim proper — the attacker never constructs anything.
INV_NoAttackerConstruction == constructed = {}
====
