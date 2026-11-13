# The decision boundary — what the beekeeper rules, and what a conversation derives or leaves open

> Federation standing process. **Beekeeper-directed, 2026-09-11.** Companion to `conversation-modus-operandi.md` §10b; ledger-side enforcement tracked in **QBP#654**.
> Origin ruling (beekeeper): *"We work from axioms, the fewer the better, anchored to experimentally proven facts; we change an axiom only when we have proven we must."* Added after the AXIOM-2 arc (QBP#648/#649/QBP#652) drifted into asking the beekeeper to **choose** physics the axioms under-determine (the P2 vs P2′ request), which he rightly rejected.

---

## The one rule

**The beekeeper rules scope, priority and process. He never rules a physical truth.**

A physical truth is settled by the axioms plus experiment, or it is left open with a kill condition. It is never settled by beekeeper fiat — because a ruling cannot make an under-determined fact true, it can only hide that it was under-determined.

## The four buckets

Every conversation output — and every claim a PR asks the federation to accept — lands in exactly one:

| # | Bucket | Meaning | Ledger reflection |
|---|---|---|---|
| 1 | **Proved** | derived from the axioms, or a theorem | a root with a forcing `PROOF`/`MEAS` anchor, or a `derived_from` chain to roots |
| 2 | **Forced** | fixed by a *prior ruling or an existing ledger rule* — not a fresh choice | `decision_state: ruled`, or a chain to a ruled/proved root |
| 3 | **Open — with a kill** | undetermined by axioms + evidence; stated with the precise datum/experiment/proof that would settle it | `decision_state: open` + `kill_condition` |
| 4 | **Wrong — and withdrawn** | refuted and retracted, named | `superseded_statement` / removed, or `retired` (axiom-level), with provenance |

**Grounded is not forced.** A chain that terminates at an `inputs[]` record (an instrument or free-input leaf) is *grounded* — it resolves — not *forced*: it counts as bucket 1/2 only as far as its inputs are themselves forced. A free input's evidential weight stays with its own tag (beekeeper ruling on QBP#805: `MEAS-alpha → INST-f0` resolves, but INST-f0 is a SELECTED free input, QBP#479).

Only buckets 1, 2 and 4 are *settled*. Bucket 3 is *open* — a valuable artifact (it names the open problem and exactly what would close it), but not a decision.

**One kill per open *question*.** A root with several independent open questions carries one `kill_condition` entry per question (a list), each naming its own precise missing piece — a single question is a one-element list. Bundling questions into one kill fails the "precise missing piece" test. (First applied: AXIOM-1, two questions — process and selection-clause scope — QBP#659.)

**The kill is required; the discharge is optional.** Each open question must state its **kill** (the falsifier that settles it). A **discharge** (a derivation closing it the other way) is stated only where one exists — its absence is honest, not a gap: a question whose only closure is a constitutional change on a fired kill (an axiom-under-determined clause *range* is a constitutional statement, not a theorem) is falsifiable but not verifiable-by-stipulation. A stipulation offered as a discharge is a choice dressed as a derivation — forbidden. (AXIOM-1 Q2, QBP#659.)

**The kill must be a genuine falsifier, not the claim's own negation.** For a root, the kill names an external observation or proof that forces the change; "prove this false" names no precise missing piece. A root whose *only* kill is its own negation is an adopted postulate without an independent falsifier — recorded as exactly that, not as a falsifiable open root. A real falsifier that cannot fire *today* is still a valid bucket-3, recorded OPEN-not-a-pass and tracked as burn-down (QBP#658). (v0.7 bundle: META-2's physical falsifier vs POST-hosting's self-negation, QBP#652.)

**Declare the quantifier — a ∀-claim is not closed by an ∃-proof.** A kill/negative claim must say whether it is *specific* (this construction fails, ∃) or *general* (all constructions fail, ∀). Proving one instance dead is *evidence* toward the general, never *closure*: the general stays OPEN, the specific cited. This blocks two failures at once — a napkin result treated as a proof, and a specific result treated as a general kill. (First caught: the condensed-sets kill — QBP#660; the general theorem that would earn it is QBP#661.)

## What this forbids

- **A bucket-3 result phrased as a beekeeper request.** An open question goes to the beekeeper as an **Impasse Record with its kill condition** (MO §10), never as "please choose." Asking the beekeeper to pick among axiom-under-determined options is the failure the P2/P2′ episode is the exemplar of.
- **A ruling used where a derivation was owed.** If a claim is *decidable from the axioms*, it must be **derived (bucket 1/2), not ruled.** Ruling a decidable claim launders a provable/refutable fact into an unappealable decree.
- **A "forced" claim (bucket 2) with no citable forcer.** Agreement that something is "forced" is not proof that it is (MO §8). A bucket-2 claim must **cite the specific prior ruling or ledger rule that forces it**, verifiable. Absent that, it is bucket 3 (open), not bucket 2.

## The pre-question and the gate

**Every PR that requests a beekeeper ruling must first answer, in the PR: "Is this decidable from the axioms?"**

- **Yes** → it is bucket 1/2; withdraw the request and derive it (or cite the forcer).
- **No, and it is open** → it is bucket 3; withdraw the request and file the Impasse Record + kill condition.
- **It is a genuine scope / priority / process choice** → it is a legitimate beekeeper decision; the request stands.

**The §7 confirmer rejects a ruling-request that is decidable-or-honestly-open.** The confirmer's job here is not to answer the physics — it is to check that the *right kind of thing* is being asked of the beekeeper.

## One invariant, two faces

This process rule (the conversation side) and the ledger's root discipline (the data side) enforce a single invariant:

> *A root is forced (carries a forcing anchor) or killed-and-open (carries a kill condition). A conversation's output is proved, forced, open-with-a-kill, or wrong-and-withdrawn. The beekeeper decides only scope, priority and process.*

The two speak one vocabulary: a ledger **root-with-forcing-anchor** = a bucket-1/2 settled item; a schema **`kill_condition` + `decision_state: open`** = a bucket-3 Impasse Record. So the ledger CI (root gate, chain-to-root audit, schema — QBP#654) and the Conversation MO are not five separate mechanisms; they are one invariant checked on both sides.

---

*Beekeeper-directed, 2026-09-11. Ratified alongside MO Rev. 3 by the beekeeper's merge (inter#296).*
