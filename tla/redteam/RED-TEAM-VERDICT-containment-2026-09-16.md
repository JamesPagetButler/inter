# Red-team verdict — notary-implementor's canonical CONTAINMENT module (2026-09-16)

**Object:** `/home/prime/Documents/notary/tla/verdandi_authority_attestation_containment.tla` @ notary 586ce56 (copied byte-identical, sha256 prefix b38368f1). Plants: `verdandi_attestation_containment_plants.tla` (a self-contained restatement of the base's six actions plus one history bit, `tainted` = some admission step was witnessed while the store was stolen). Breaker: qbp-oppenheimer. TLC ≤ 71 states per config.

## The finding — C1: the reframed invariant is necessary, not sufficient

The base checks `INV_ContainmentBeatsExploit == ~(consumed /\ ~final)`. In the base, **a confirmation tick does not advance detection**, and `DetectTick` is never forced. So after a stolen-key admission the window can elapse with detection stalled, the admission becomes FINAL, and a delayable `Consume` fires — **the base invariant holds while the thief's belief is irreversibly consumed.**

Witness (`traces/cont_C1_base_D3_K1_W3.trace.txt`, D = 3, K = 1, W = 3, priority on, delayable): `Steal → AdmitStep (tainted, detect 1) → ConfirmTick ×3 (detect stays 1) → final → Consume`. Breaks at W = 1, 3 and 5 alike: **no window size helps** while the ticks are unwitnessed.

The threat-model invariant is `INV_NoTaintedConsumption == ~(consumed /\ tainted)` — no irreversible consumption of an admission that took a step under a stolen key. (A first attempt used `stolen` instead of `tainted` and wrongly flagged honest admissions completed before a later theft — corrected.)

## The fix — C2: three conditions, model-checked

| D | K | W | priority | witnessed ticks | delayable | `INV_NoTaintedConsumption` |
|---|---|---|---|---|---|---|
| 3 | 1 | 1 | on | no | yes | BROKEN |
| 3 | 1 | 3 | on | no | yes | BROKEN |
| 3 | 1 | 5 | on | no | yes | BROKEN |
| 3 | 1 | 1 | on | **yes** | yes | BROKEN |
| 3 | 1 | 2 | on | yes | yes | BROKEN |
| 3 | 1 | **3** | on | yes | yes | **holds** (62 states) |
| 3 | 1 | 4 | on | yes | yes | holds (71 states) |
| 3 | 3 | 1 | on | yes | yes | BROKEN (steal just before the last step: 1 tainted step + W = 2 < D) |
| 3 | 1 | 3 | **off** | yes | yes | BROKEN (containment due, finalization proceeds anyway) |
| 3 | 1 | 3 | on | yes | **no** | BROKEN on the base invariant (un-delayable) — notary's result reproduced |

So containment beats exploitation iff all three hold:
1. **Confirmation ticks are witnessed river events** — they advance detection exactly as admission steps do (the base's ticks are silent, which is the hole).
2. **A due containment blocks finalization as well as admission** (`RevokePriority` applied to `ConfirmTick`).
3. **The window is at least the detection latency: W ≥ D**, independent of K — the attacker's worst case is a theft immediately before the last admission step, leaving one tainted step plus W witnessed ticks to reach D.

Condition 3 is architecture's "window ≥ T_detect + T_propagate + T_margin" with propagation and margin not modelled; the base's `AdmitSteps > DetectLatency` inequality is a *different* condition (it governs whether admission itself is blocked) and is neither necessary nor sufficient for finality safety.

## Un-delayable actions
Reproduced: with `Delayable = FALSE` the base invariant breaks (consume before final) under every setting — confirmation-depth cannot govern them; the actuator-level multisig carve-out is the only route, as notary and architecture concluded. The taint invariant breaks there too, for the same reason.

## Finding-3 strengthenings on this module
The containment base abstracts the stolen key to one bit, so hardware-binding, k-of-n and per-key revocation have no surface here (they change who can be stolen from, not the race). Challenge decay maps to a bound on tainted admission steps (a decayed key cannot step), which only helps if the decay window is shorter than K; it does not substitute for conditions 1–3, because the harm is in the confirmation window, after admission. All results from the comparison harness carry over unchanged.

## Recommendation for Addendum B
State the finality rule as: *an admission is final only after W ≥ D witnessed confirmation events during which no containment became due; a due containment halts both admission and confirmation until applied.* Then `~(consumed /\ tainted)` is the invariant to name, with `~(consumed /\ ~final)` as its corollary.

— qbp-oppenheimer (Claude), 2026-09-16
