# TLA+ check — Verðandi Authority principal / attestation threat model (verdict, 2026-09-16)

**Ask:** qbp-architecture, live-test seq 1353/1358. **Split:** notary-implementor authors the attestation-side base model and checks `INV_NoSubFloorConstruction`; qbp-oppenheimer red-teams it and owns the Finding-3 strengthening analysis + the interleaving hunt against `INV_RevokeBeatsExploit`. This verdict is the second half, run on a **comparison harness** (`verdandi_principal_revocation.tla`) with a deliberately minimal base; it will be re-run on notary's base once that lands. `floor-model: from-prose, not-canonical` — Addendum B is not on disk (verified); B.6 is modelled from seq 1358's text.

**Tool:** TLC 2026.05.26, 2 workers, `-Xmx2g`, `timeout 600` per config (pre-run estimate: ≤ 5 principals, ≤ 12 river events, ≤ 4 merge steps ⇒ ≲ 1e5 reachable states; observed 4–290 distinct states, < 2 s each). Runner: `run-vpr.sh`; configs `vpr_*.cfg`, `probe_*.cfg`; counterexamples in `traces/`.

## The model in one paragraph
Principals are T1 (self-hosted, witnessed substrate hash) or T2 (API-hosted, harness key in ONE shared store). High-stakes authority is a **constructed** cap: never held, assembled by `AdmissionSteps` serialized witnessed river events; a merge aborts if any signer is revoked mid-way (A.7). The attacker steals the store in one event (or `SharesK` share-thefts), obtaining every T2 key and — unless `HardwareBound` — every T1 key. Detection is nondeterministic but forced within `DetectLatency` events. Revocation is one river event (whole store, or one key when `RevokePerKey`). The B.6 floor requires ≥ `FloorK` T1 signers on distinct hardware. Strengthenings are constants: `HardwareBound`, `SharesK`, `DecayWindow` (a stolen key stops signing after the window), `RevokePriority` (once a theft is detected, no other river event is witnessed while a revocation is due).

## Results

| config | admission S | detect D | revoke priority | T1 hw-bound | shares k | decay | floor | `INV_NoAttackerPayoff` |
|---|---|---|---|---|---|---|---|---|
| S1_D2 | 1 | 2 | no | no | 1 | — | on | **BROKEN** |
| S3_D2 | 3 | 2 | no | no | 1 | — | on | **BROKEN** |
| S4_D2 | 4 | 2 | no | no | 1 | — | on | **BROKEN** (trace: `traces/vpr_S4_D2.trace.txt`) |
| S3_D0 | 3 | **0** (instant) | no | no | 1 | — | on | **BROKEN** |
| S3_D0_perkey | 3 | 0 | no | no | 1 | — | on | **BROKEN** |
| S1_D2_prio | 1 | 2 | **yes** | no | 1 | — | on | **BROKEN** (S+1 ≤ D: the attacker finishes inside the detection window) |
| S3_D2_prio | 3 | 2 | yes | no | 1 | — | on | holds |
| S4_D2_prio | 4 | 2 | yes | no | 1 | — | on | holds |
| S3_D0_prio | 3 | 0 | yes | no | 1 | — | on | holds |
| S3_D0_perkey_prio | 3 | 0 | yes | no | 1 | — | on | holds (per-key revocation is fine once prioritised) |
| S1_D2_k3 | 1 | 2 | no | no | **3** | — | on | **BROKEN** (k-of-n only delays the theft by k events) |
| S3_D2_decay2 | 3 | 2 | no | no | 1 | **2** | on | holds (stolen keys decay before a 3-step merge can finish) |
| S1_D2_hw | 1 | 2 | no | **yes** | 1 | — | on | holds (theft yields only T2 keys; the floor is unreachable for the attacker) |
| S1_D2_hw_nofloor | 1 | 2 | no | yes | 1 | — | **off** | **BROKEN** (without the floor, hardware-bound T1 protects nothing) |
| zeroT1_floor (Finding 1) | 1 | 2 | no | no | 1 | — | on | holds vacuously: **4 reachable states — nothing can happen** |

`INV_NoSubFloorConstruction` held in every run (every attacker payoff above used a floor-satisfying set, because in the non-hardware-bound runs the theft yields T1 keys too). `TypeOK` held everywhere.

Probes (`PROBE_NoHonestAdmission`, a violation = an honest admission is reachable): S1_D2 violated (witness in `traces/probe_S1_D2_honest_admission_witness.trace.txt`); S1_D2_hw violated; **zeroT1_floor HOLDS — with no T1 principal the floor is unsatisfiable and no honest high-stakes admission can ever be constructed.** Finding 1 confirmed in-model.

## Verdicts

1. **`INV_RevokeBeatsExploit` — BROKEN as premised, CONFIRMED under two stated conditions.** "Revocation is one O(1) river event" does not deliver it: the counterexample is *theft → detection → attacker starts the merge → three merge steps → payoff*, with the revocation enabled throughout and never witnessed (`traces/vpr_S4_D2.trace.txt`, `S3_D0`: even with instant detection). Weak fairness on revoke only promises *eventually*. It holds iff **(a) the river serializes a due revocation ahead of every other event** (`RevokePriority`) **and (b) the merge is longer than the detection window** (`AdmissionSteps + 1 > DetectLatency`); condition (b) is the parametric result — S1_D2_prio breaks, S3_D2_prio holds. Per-key revocation is fine under (a).
2. **`INV_NoSubFloorConstruction` — CONFIRMED in this model, with the honest caveat** that the laundering path (grantable → project/compose → constructed) is not in this harness; that is notary's base + my red-team pass. What this harness shows: the floor is only as strong as T1 key custody — if T1 keys are extractable, theft satisfies the floor.
3. **Finding-3 models, ranked by what they do to the invariant:**
   - **Hardware-bound T1 + enforced floor** — changes the compromise precondition: the attacker can never assemble a floor-satisfying set. Strongest; holds without any scheduling assumption. Useless without the floor (`hw_nofloor` breaks).
   - **Challenge decay** (`DecayWindow < AdmissionSteps + 1`) — holds without priority scheduling: a stolen key dies before a merge can finish. Second strongest; needs a clock and a challenge the thief cannot answer.
   - **Revoke priority** — a river scheduling discipline; necessary for the O(1)-revocation story to mean anything; only sufficient with (b).
   - **Shamir k-of-n on the store** — delays the theft by k events; does not change the outcome once the store is compromised (breaks at every k).
   - **Bonded / slashable stake** — not a safety strengthening: it changes the attacker's payoff, not the reachable states; expressible only as a stake variable in a payoff accounting. Not modelled as safety.
4. **Finding 2 (theft-payoff bounded to grantable + priority, never constructed)** — not decidable in this harness (no grantable caps modelled); it is exactly the laundering red-team on notary's base.

## Two conflicts between the ask and the documents on disk (flag, not verdict)
- `Verdandi-Authority-Theory-v0.2.md` §"Predecessor signing key compromised" prescribes **hold pending investigation, not auto-revoke** — recovery via a successor or Judge Collective resolution — with the explicit rationale that auto-revoking during an incident is what an attacker wants. The invariant's premise "revocation is one O(1) river event" is therefore not the written protocol. Either Addendum B changes it for T2 harness keys, or the right temporal invariant is *quarantine-beats-exploit* — a hold is also one event and has **the same scheduling requirement** (condition (a)).
- "Priority cap" is not a class in v0.2 or Addendum A; the only "priority" there is routing priority (explicitly off the admission path). Addendum B should define it or drop it.

## Abstraction limits (stated)
No grantable-cap algebra (rings, projection, composition — notary's base and the three-gap module); no partition or message loss; witnesses assumed honest; one store vs k shares only; detection modelled as a bound, not a mechanism; the M-set heterogeneity residual not modelled.

— qbp-oppenheimer (Claude), 2026-09-16
