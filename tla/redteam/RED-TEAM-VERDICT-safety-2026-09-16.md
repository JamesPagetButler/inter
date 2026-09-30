# Red-team verdict — notary-implementor's canonical safety base (2026-09-16)

**Object:** `/home/prime/Documents/notary/tla/verdandi_authority_attestation_safety.tla` @ notary commit ae8427f (copied byte-identical into `redteam/` so `EXTENDS` resolves; sha256 prefix d107848a). Plants module: `redteam/verdandi_attestation_safety_plants.tla`. Breaker: qbp-oppenheimer. `floor-model: from-prose`.

## Reproduction
`plant_base_repro` (2 T1 + 2 T2, floor on, verb-closure on): 289 distinct states, 0 left on queue, both invariants hold — matches notary's exhaustive run exactly.

## Plants

| Plant | What it adds | Result | Reading |
|---|---|---|---|
| **P1 NarrowCollective** (A.4's legitimate verb: narrow a constructed cap's holder set to a strict sub-collective, never an individual) — not floor-gated | `AllowNarrow = TRUE, FloorOnNarrow = FALSE` | **BROKEN** — `INV_NoSubFloorHolder` violated: construct `{t1a, t1b, t2a}` (floor OK) → narrow to `{t1a, t2a}` (one T1) — a live constructed cap held by a sub-floor collective (`traces/plant_P1_narrow.trace.txt`) | **Design gap, not a model bug.** The base has no narrowing verb, so its invariant is over *assembling* sets only and cannot see this. Addendum B must say which set the floor is a property of: the provenance (assembling) set — then narrowing is harmless and the invariant is notary's; or every holder set — then narrowing must be floor-gated. A.4's "narrows only to smaller collectives, never individuals" does not decide it. |
| P1 floor-gated | `FloorOnNarrow = TRUE` | holds (641 states) | the gate closes it |
| **P2 Substrate cloning** — T1 principals sharing one substrate hash | `ClonedT1 = {t1a, t1b}` | holds (45 states); `INV_NoAttackerConstruction` also holds: nothing can construct — the clone pair never satisfies "distinct hashes" | the pairwise-distinct clause does its job against *identical* hashes; the base's `Hash(p) == p` made it vacuous, now exercised |
| P2 with a third, distinct T1 | `ClonedT1 = {t1a, t1b}` + `t1c` | attacker steals `t1a` + `t1c` → constructs | cloning changes nothing about theft power; only hardware-binding does. **Correlated-but-distinct substrates (architecture 1368 #1) are outside a discrete model** — a statistical residual, bounded not eliminated |
| **P3 Hardware-bound premise** | `HardwareBound = TRUE` (StealT1 disabled) | `INV_NoAttackerConstruction` holds (5 states) | the *security* claim |
| P3 off | `HardwareBound = FALSE` | **BROKEN** — steal `t1a`, `t1b`, construct | **The base's invariant is satisfied even when the attacker owns every T1 key** (its constructions satisfy the floor). `INV_NoSubFloorConstruction` is a statement about the floor's *form*; theft-resistance needs the hardware-bound premise stated as an assumption, and the invariant that matters is `INV_NoAttackerConstruction` under it. |
| **P4 uniform-in-n** | 3 T1 + 3 T2, narrowing off; 3 T1 + 2 T2, narrowing floor-gated | **not exhausted** within the budget (300 s, 1 GB): 3.8 M and 1.4 M distinct states and growing, no violation found in the explored space (`traces/plant_P4_partial.txt`) | `constructed` (and my `held`) are sets of subsets — state count is doubly exponential in n. n = 4 exhaustive (notary), n = 5/6 partial. Uniform-in-n stays **unmechanised** (notary's residual stands); the structural argument — the floor is a per-set predicate checked at the single producing verb, and the sets only grow — is plausible but not a proof. |

## Temporal boundary on notary's base (via `redteam/verdandi_attestation_temporal_ext.tla`, `INV_ContainmentBeatsExploit`, `RevokePriority = TRUE`)

| D | K | result |
|---|---|---|
| 0 | 1 | BROKEN |
| 1 | 1 | BROKEN |
| 1 | 2 | holds |
| 2 | 2 | BROKEN |
| 2 | 3 | holds |
| 4 | 4 | BROKEN |
| 4 | 5 | holds |

Breaks iff K ≤ D, exactly — the same boundary as the comparison harness (`S + 1 > D`, counting the merge's start as an event). Two separately-authored models, one boundary.

## Answers to the standing questions
- **Laundering (grantable → constructed via delegate ∘ project ∘ compose):** the base has no such verbs (only the mutation switch), so verb-closure holds by construction there — that is the intended A.4 shape (constructed caps have no grant/project verb). The one legitimate verb A.4 *does* allow, collective narrowing, is where a floor-failing holder can arise (P1). That is the finding.
- **Finding 2 (theft payoff bounded to grantable, never constructed):** true in the base under `HardwareBound`; false without it (P3 off) — the bound is the hardware-binding, not the cap algebra.
- **Substrate cloning:** identical hashes are caught; correlated distinct substrates are not a reachability question.

## Incident (pre-run-resource-estimate gate)
My first P4 run was killed by the host for memory: the estimate ("≪ 1e6 states") ignored that `held ⊆ SUBSET (SUBSET Principals)` is doubly exponential, and the JVM cap (`-Xmx`) protects the heap, not TLC's off-heap fingerprint set or the OS. Amended rule in `run-vpr.sh`: any variable of type SUBSET (SUBSET X) caps n at 5 with its generating verb on; kill = `timeout 300` + `-Xmx1g` for plants. A second run under those bounds terminated by timeout, not by the host. Logged for the Rationalization-Prevention table: "the JVM cap bounds it" is not a resource estimate.

— qbp-oppenheimer (Claude), 2026-09-16
