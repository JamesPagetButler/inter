# Ruling (DRAFT, for beekeeper ratification) — formality tier×state + capability-grant gate

> Resolves Spike-0 gaps **#7** (three non-commensurable formality scales) and **#8** (no settled-gate on `ETGrants`). Approved in principle by the beekeeper 2026-09-27 ("tier×state grid seems functional"; "#8 reasonable"); this is the formal ruling for sign-off. It is the design context for the Spike-0 build issues.

## Ruling 1 (#7) — formality is TWO axes, not one scale; "min over steps" is over *cleared-tier*

The three live scales are not three rulers for one quantity — they are two orthogonal axes:
- **Tier** (which rigor is claimed / which oracle applies): `spike:FormalityGradient` = active → napkin → engineering → formal.
- **Verification-state** (how far validation got against that tier's oracle): `cth:ProofState` (written→partial→verified) and `cth:decision_state` (open→settled).

**Clearing table** (which verification-state *clears* each tier — this is RECORD's Gate-1 table, now authoritative):

| Tier | Cleared when… |
|---|---|
| active | a settled pattern matches (`decision_state: settled` at the pattern) |
| napkin | minimal / declared |
| engineering | schema + build validation passes |
| formal | `ProofState: verified` (derivation) **or** `closure: measurement` — **not** `written` ("written is not a proof") |

- A step's **cleared-tier** = the highest tier whose oracle it actually passed (a step *claiming* formal but at `ProofState: written` has cleared at most engineering).
- **Composite formality = min over steps of cleared-tier.** Well-defined over one axis; no forced total order across the three scales.
- **Laundering** = claiming a higher tier than cleared. Caught by construction.

## Ruling 2 (#8) — a capability inherits the cleared-tier + provenance of the step that granted it

- **`ETGrants` is gated:** a `NT_CAPABILITY(kind=composite)` inherits the **cleared-tier and provenance** of the Step whose `ETGrants` edge produced it.
- An **`open`/unvalidated step grants only an `open`/quarantined capability** — present in CTH `open`, **not exercisable as `settled`**. It becomes exercisable-as-settled only when the granting step settles (clears its tier).
- A capability granted at a low tier (e.g. napkin) is a **low-tier capability** — usable only in same-or-lower-tier chains, and it drags any chain that uses it down to its tier via Ruling 1's min-over-steps. **No laundering a loose capability into formal work.**
- This is the S3 anti-laundering discipline enforced on *capability grants*, not just on content crossing into settled belief.

## Consequence for the build
The Spike-0 lowering (`NT_CAPABILITY`, `ETGrants`, formality fields) must implement both rulings: capability carries `{cleared_tier, provenance}` copied from its granting step; `ETGrants` from a non-settled step yields an `open` capability; composite formality computed as min cleared-tier. This is why #7/#8 gate the build — lowering without them bakes in a laundering vector.
