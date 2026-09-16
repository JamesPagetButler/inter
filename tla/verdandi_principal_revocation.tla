---- MODULE verdandi_principal_revocation ----
(*
  Verðandi Authority — Principal-of-Record threat model:
  INV_NoSubFloorConstruction (safety) + INV_RevokeBeatsExploit (temporal)
  with the Finding-3 invalidation models as switchable strengthenings.

  Ask: qbp-architecture, live-test seq 1353 (2026-09-16). Split with
  notary-implementor (seq 1355/1356): notary authors the attestation-side base
  (T1/T2 principals, PoR, constructed caps, A.1 delegation/projection/composition,
  A.7 atomic admission, revocation); this module carries the TEMPORAL side and the
  strengthening comparisons on a deliberately minimal base, to be rebased onto
  notary's module (EXTENDS) once it lands.

  floor-model: FROM-PROSE (Addendum B is not on disk; B.6 is modelled from the
  seq-1353 description: "≥ 2 T1 PoRs on distinct substrate hashes"). The verdict
  carries this as a trust dependency.

  What is modelled
    - Principals with a tier (T1 self-hosted / T2 API-hosted) and a substrate hash
      (T1 principals on distinct hardware have distinct hashes).
    - One shared key STORE holding every T2 harness key (Finding 1). T1 keys are
      hardware-bound (non-extractable) iff HardwareBound = TRUE.
    - High-stakes authority is a CONSTRUCTED cap (A.4): never held; it must be
      assembled by a witnessed, serialized quorum-merge of AdmissionSteps river
      events (A.7). A merge aborts if any signer is revoked before it completes
      (atomic admission).
    - Theft: StealStore compromises the whole store in one event (or, under
      SharesK > 1, needs SharesK independent share-thefts first — Shamir k-of-n).
    - Detection: bounded latency — detection happens no later than
      DetectLatency river events after the theft (weak fairness on Detect).
    - Revocation: one witnessed river event revokes every key in the store
      (RevokePerKey = FALSE) or one key per event (RevokePerKey = TRUE).
    - ChallengeDecay: a key not re-challenged within DecayWindow events of its
      last challenge stops signing (a stolen key decays; the thief cannot answer
      the challenge — modelled as: stolen keys are never re-challenged).
    - Bonded stake: recorded as a payoff/stake account only — it is NOT a safety
      strengthening (it changes incentive, not possibility); see the verdict.

  What is NOT modelled (abstraction limits, stated)
    - cap contents, rings, consent (the three-gap module covers those);
    - network partition, message loss, Byzantine witnesses;
    - the M-set heterogeneity question (qbp-architecture's residual);
    - key custody procedures other than "one store" vs "k shares".

  Authored: 2026-09-16, qbp-oppenheimer (Claude), on the beekeeper's direction.
*)

EXTENDS Naturals, FiniteSets

CONSTANTS
  Principals,        \* model values, e.g. {t1a, t1b, t2a, t2b, t2c}
  T1s,               \* the T1 (self-hosted, witnessed substrate_hash) principals; the rest are T2
  T1Distinct,        \* BOOLEAN: the T1 principals sit on pairwise-distinct hardware (distinct hashes)
  FloorK,            \* B.6: minimum number of T1 PoRs on DISTINCT hashes in a high-stakes quorum
  FloorEnforced,     \* BOOLEAN: is the T1 floor enforced at admission?
  QuorumSize,        \* minimum signer count for a high-stakes admission
  AdmissionSteps,    \* A.7: number of serialized witnessed river events a quorum-merge takes (>= 1)
  DetectLatency,     \* bound on river events from theft to detection
  RevokePerKey,      \* BOOLEAN: TRUE = one key per revocation event; FALSE = whole store per event
  HardwareBound,     \* BOOLEAN: T1 keys non-extractable (theft never yields a T1 key)
  SharesK,           \* Shamir k-of-n on the store: number of share-thefts needed (1 = single store)
  DecayWindow,       \* challenge-decay: 0 = off; else a stolen key decays after this many events
  RevokePriority,    \* BOOLEAN: once a theft is detected, the river serializes revocation AHEAD of
                     \*   every other event (no merge step may be witnessed while a revocation is due)
  MaxEvents          \* bound on river events (state-space control; kill bound)

ASSUME FloorK \in Nat /\ QuorumSize \in Nat /\ AdmissionSteps \in Nat \ {0}
ASSUME DetectLatency \in Nat /\ SharesK \in Nat \ {0} /\ DecayWindow \in Nat /\ MaxEvents \in Nat

ASSUME T1s \subseteq Principals
T2s == Principals \ T1s

VARIABLES
  events,       \* Nat: river-event counter (every action below is one witnessed river event)
  sharesStolen, \* Nat: share-thefts so far (SharesK needed)
  stolenAt,     \* Nat: event index of the store compromise, or MaxEvents+1 if none
  compromised,  \* subset of Principals whose key the attacker holds
  revoked,      \* subset of Principals whose key is revoked
  detected,     \* BOOLEAN: theft detected
  adm,          \* admission record: [active, signers, step, attacker]
  payoff,       \* BOOLEAN: the attacker completed a high-stakes admission
  legitDone     \* BOOLEAN: some honest quorum completed a high-stakes admission (floor liveness probe)

vars == <<events, sharesStolen, stolenAt, compromised, revoked, detected, adm, payoff, legitDone>>

NoAdm == [active |-> FALSE, signers |-> {}, step |-> 0, attacker |-> FALSE]

Init ==
  /\ events = 0
  /\ sharesStolen = 0
  /\ stolenAt = MaxEvents + 1
  /\ compromised = {}
  /\ revoked = {}
  /\ detected = FALSE
  /\ adm = NoAdm
  /\ payoff = FALSE
  /\ legitDone = FALSE

Stolen == stolenAt <= MaxEvents

\* A stolen key has decayed (challenge-decay) if the window has elapsed since the theft.
Decayed(p) == DecayWindow > 0 /\ p \in compromised /\ events >= stolenAt + DecayWindow

\* Keys the attacker can still sign with.
AttackerUsable == { p \in compromised : p \notin revoked /\ ~Decayed(p) }

\* Honest signers: not compromised (a compromised key is the attacker's, not honest), not revoked.
HonestUsable == { p \in Principals : p \notin compromised /\ p \notin revoked }

\* B.6 floor, modelled from prose: >= FloorK T1 members on pairwise-distinct hashes.
\* TLC cfg files cannot express functions, so the hash map is abstracted to one bit: either every
\* T1 is on its own hardware (distinct hashes) or they all share one.
DistinctHashT1(S) == IF T1Distinct THEN Cardinality(S \cap T1s)
                     ELSE (IF S \cap T1s = {} THEN 0 ELSE 1)
FloorOK(S) == ~FloorEnforced \/ DistinctHashT1(S) >= FloorK

QuorumOK(S) == Cardinality(S) >= QuorumSize /\ FloorOK(S)

\* ---------------------------------------------------------------- actions
Tick == events < MaxEvents /\ events' = events + 1

\* A revocation is DUE when a detected theft still has unrevoked keys. Under RevokePriority no
\* other river event may be witnessed while one is due (the scheduling discipline that the O(1)
\* cost of a revocation does NOT by itself provide).
RevokeDue == detected /\ (compromised \ revoked) # {}
MayProceed == ~(RevokePriority /\ RevokeDue)

\* Attacker steals one share of the store (SharesK = 1 => the whole store at once).
StealShare ==
  /\ ~Stolen
  /\ MayProceed
  /\ sharesStolen < SharesK
  /\ Tick
  /\ sharesStolen' = sharesStolen + 1
  /\ IF sharesStolen + 1 = SharesK
       THEN /\ stolenAt' = events + 1
            /\ compromised' = IF HardwareBound THEN T2s ELSE Principals
       ELSE /\ UNCHANGED <<stolenAt, compromised>>
  /\ UNCHANGED <<revoked, detected, adm, payoff, legitDone>>

\* Detection: nondeterministic, but forced (by DetectDeadline below) within DetectLatency events.
Detect ==
  /\ Stolen /\ ~detected
  /\ Tick
  /\ detected' = TRUE
  /\ UNCHANGED <<sharesStolen, stolenAt, compromised, revoked, adm, payoff, legitDone>>

\* Revocation: one witnessed river event. Whole store, or one key.
Revoke ==
  /\ detected
  /\ compromised \ revoked # {}
  /\ Tick
  /\ \/ /\ ~RevokePerKey
        /\ revoked' = revoked \cup compromised
     \/ /\ RevokePerKey
        /\ \E p \in compromised \ revoked : revoked' = revoked \cup {p}
  \* atomic admission (A.7): a merge whose signer is revoked mid-way aborts
  /\ adm' = IF adm.active /\ (adm.signers \cap revoked') # {} THEN NoAdm ELSE adm
  /\ UNCHANGED <<sharesStolen, stolenAt, compromised, detected, payoff, legitDone>>

\* Attacker starts assembling a constructed cap from keys it holds.
AttackerStart ==
  /\ Stolen /\ ~adm.active /\ ~payoff
  /\ MayProceed
  /\ \E S \in SUBSET AttackerUsable :
       /\ S # {}
       /\ QuorumOK(S)
       /\ Tick
       /\ adm' = [active |-> TRUE, signers |-> S, step |-> 1, attacker |-> TRUE]
  /\ UNCHANGED <<sharesStolen, stolenAt, compromised, revoked, detected, payoff, legitDone>>

\* Honest quorum starts an admission (liveness probe for the floor).
HonestStart ==
  /\ ~adm.active /\ ~legitDone
  /\ MayProceed
  /\ \E S \in SUBSET HonestUsable :
       /\ S # {}
       /\ QuorumOK(S)
       /\ Tick
       /\ adm' = [active |-> TRUE, signers |-> S, step |-> 1, attacker |-> FALSE]
  /\ UNCHANGED <<sharesStolen, stolenAt, compromised, revoked, detected, payoff, legitDone>>

\* One serialized, witnessed merge step (A.7). Every signer must still be usable.
Step ==
  /\ adm.active
  /\ MayProceed
  /\ adm.step < AdmissionSteps
  /\ (adm.attacker => adm.signers \subseteq AttackerUsable)
  /\ (~adm.attacker => adm.signers \subseteq HonestUsable)
  /\ Tick
  /\ adm' = [adm EXCEPT !.step = adm.step + 1]
  /\ UNCHANGED <<sharesStolen, stolenAt, compromised, revoked, detected, payoff, legitDone>>

\* The merge completes: the constructed cap exists for this one use.
Complete ==
  /\ adm.active
  /\ MayProceed
  /\ adm.step = AdmissionSteps
  /\ (adm.attacker => adm.signers \subseteq AttackerUsable)
  /\ (~adm.attacker => adm.signers \subseteq HonestUsable)
  /\ Tick
  /\ payoff' = (payoff \/ adm.attacker)
  /\ legitDone' = (legitDone \/ ~adm.attacker)
  /\ adm' = NoAdm
  /\ UNCHANGED <<sharesStolen, stolenAt, compromised, revoked, detected>>

Next == StealShare \/ Detect \/ Revoke \/ AttackerStart \/ HonestStart \/ Step \/ Complete

\* Detection deadline as a STATE constraint: no reachable state may have an undetected theft
\* older than DetectLatency events. TLC prunes successors that would violate it, which is the
\* semantics "detection happens within the bound".
DetectDeadline == ~(Stolen /\ ~detected /\ events > stolenAt + DetectLatency)

Spec == Init /\ [][Next]_vars /\ WF_vars(Detect) /\ WF_vars(Revoke)

\* ---------------------------------------------------------------- properties
TypeOK ==
  /\ events \in 0..MaxEvents
  /\ compromised \subseteq Principals
  /\ revoked \subseteq Principals
  /\ adm.signers \subseteq Principals

\* INV_NoSubFloorConstruction: no completed attacker admission whose signer set fails the floor.
\* (payoff is only set by Complete, which requires QuorumOK at AttackerStart; so this is
\*  really: the attacker can never obtain payoff at all while its usable keys fail the floor.)
INV_NoSubFloorConstruction ==
  payoff => \E S \in SUBSET compromised : QuorumOK(S)

\* INV_NoAttackerPayoff: the strong form — under the chosen constants the attacker never
\* completes a high-stakes admission at all. This is what "revoke beats exploit" must deliver.
INV_NoAttackerPayoff == ~payoff

\* INV_RevokeBeatsExploit (temporal): once stolen, every compromised key is eventually revoked,
\* and no attacker payoff ever occurs. Checked as PROPERTY under Spec's fairness.
INV_RevokeBeatsExploit ==
  /\ [](Stolen => <>(compromised \subseteq revoked))
  /\ []INV_NoAttackerPayoff

\* Floor probe (Finding 1), checked as an INVARIANT that we EXPECT to be violated: a violation
\* trace is a witness that an honest high-stakes admission is reachable; if it HOLDS, no honest
\* quorum can ever construct a high-stakes cap under these constants — the floor is unsatisfiable.
PROBE_NoHonestAdmission == ~legitDone
FloorSatisfiable == ~FloorEnforced \/ DistinctHashT1(Principals) >= FloorK

====
