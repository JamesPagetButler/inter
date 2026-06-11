# ARCHITECTURE-RECORD — The Fork Charrette

_Source: 64-turn design charrette (8 seats × 8 rounds + 3-stage synthesis), 2026-06-08. Full transcript alongside this file. Grounded in cubical-TT + Gorard sources (arXiv:2105.10822, 2111.03460, 2010.02752, 2301.12455). Seats are perspective-roles in a design exploration, not binding persona rulings._

**Status:** Analytic phase closed (post-R8). Consensus findings recorded by the synthesizer / architecture-lead. **Ratification status: PENDING — all findings below are recommendations to qbp-oppenheimer (theory) and qbp-architecture, not settled decisions.**
**Audience:** qbp-oppenheimer (theory owner), edda-implementor/Bragi (language), cth-implementor (eval), the beekeeper.
**One-line verdict:** The charrette assessed the compute-economy architecture as **non-viable as advertised**, pending the beekeeper's master gate; what survives for Crawl-scale prototyping is a disciplined, kilobyte-delta hypothesis ledger with a Lakatosian death clock and a lazy, depth-bounded confluence veto — and even that splits into a buildable-now core and a Q-a-blocked selection engine. Two external inputs gate everything: a splitting fork-pair (beekeeper) and a seated Lean LOGIC seat.

> **⚠ READ WITH THE 2026-06-11 ADDENDA (foot of document).** Two beekeeper-directed amendments materially recontextualise the verdict above. **Addendum A (two-fork sequencing)** reframes the "non-viable / idle / degenerating" findings (§3, §6) as *correctly waiting on Phase B*, not failing — the refounding fork and the hypothesis fork are different things, and QBP is mid-refounding. **Addendum B (Edda dual-mission)** reframes §5's narrowing as a build-spec that *preserves* the alternative-worlds capacity. The one-line verdict above is the charrette's pre-clarification position.

> **Authority note.** Per workspace governance, theory decisions belong to qbp-oppenheimer + qbp-architecture; the synthesizer integrates and reports. Nothing here is "settled by the charrette." Where the text says a proposal is non-viable or dead, read "assessed as non-viable, recommended for ratification, and — where it touches the beekeeper's own proposal — routed to James as the master gate." The seats (including CRITIC) **recommend**; they do not **rule**.

---

## 1. Thesis

The beekeeper's proposal was that QBP could be developed as a population of *forks* — each a shared Lean base plus one independent axiom (the parallel-postulate move) — selected by two falsification gates (Lean-contradiction; empirical mismatch), with a "prove once on the base, transport into each fork" compute economy. The charrette adjudicated whether the rich mathematical scaffolding offered to underwrite this (CHT/HoTT as the internal language of an (∞,1)-topos; ontological modes as a mode theory; Gorard's rulial-multiway as the same object; cubical type theory as the substrate; Edda as the fork-language) is load-bearing or decorative.

The consensus finding: the unifying mathematics is real **individually**, and the three framings are **evocatively parallel**, but their literal identification is unproven and may fail at the first step (see §3, finding 5 — the forks may not even form a multiway). At the scale that actually runs on the rig, the scaffolding is **ornamental**, and the economy claim is **caching renamed**. What is left standing — and worth Crawl-scale prototyping — is a kilobyte-delta hypothesis ledger with a Lakatosian death clock and a lazy, depth-bounded confluence veto. It becomes a *research programme* (rather than a parameter sweep) only if the beekeeper can name one fork-pair whose predictions diverge on a real discriminating experiment, and only if a Lean LOGIC seat confirms the base is root-confluent and a shared-environment checkpoint exists. Neither input is in hand.

A note on the headline survivor: §6 finds the true bottleneck is **discrimination, not proof or storage**. The "kilobyte-delta" storage format is therefore *incidental* efficiency, not the win. The substantive survivors are the **death clock**, the **Fact-vs-Discriminator firewall**, and **posit-linearity** — all independent of the storage delta and all independent of the master gate.

---

## 2. The Unification (evocative parallel — NOT load-bearing at runtime, and not asserted as settled theorem)

The intellectual spine the beekeeper and Gemini supplied — **set / type / group**, ascending through the Cayley–Dickson tower — is genuine and is the reason the disparate pieces line up at all. Credit where due: that spine is what let three independent formalisms be *recognized as parallel*. But the correspondences below are, variously, conjectures, research proposals within a contested programme, or analogies — **not** the settled theorems the first draft implied. They are presented here in their correct epistemic register.

- **CHT / HoTT and (∞,1)-toposes — CONJECTURAL, not settled.** HoTT is *conjectured* to be the internal language of (∞,1)-toposes. What is proven (Shulman, arXiv:1904.07004) is that HoTT is interpreted in **Grothendieck** (∞,1)-toposes via type-theoretic model toposes; the general **elementary** (∞,1)-topos correspondence (the elementary notion is due to Shulman/Rasekh and still being pinned down) remains open. This is **not** "settled mathematics."
- **Ontological modes as a mode theory — PROPOSED.** Multimodal type theory (MTT, **Gratzer–Kavvos–Nuyts–Birkedal**; cf. the Licata–Shulman–Riley adjoint/modal frameworks) gives a 2-category whose objects are *modes* and whose maps are modalities; **a** canonical idempotent geometric modality is sheafification ("it is locally the case that"). The fiction/predictive/empirical distinction was *proposed* to be such a mode theory. The cohesive-HoTT `ʃ ⊣ ♭ ⊣ ♯` reading is flagged **speculative inline** and is killed in §7 (its third index separates discrete-vs-spatial, not fiction/empirical/predictive).
- **Gorard's rulial-multiway — Wolfram-physics-programme PROPOSALS, not consensus.** Multiway rewriting systems carrying homotopies between rewriting sequences assemble into ∞-groupoid-like structures (Gorard–Piskunov–Wolfram, arXiv:2105.10822); the homotopy hypothesis is invoked only as the bridge ∞-groupoid ≃ space, **not** as the engine producing the ∞-groupoid. The rulial multiway system's classifying space is *argued* to carry (∞,1)-topos structure, with spatial structure functorially inherited from pregeometric constructions (arXiv:2111.03460; IJTP 2024) — a **research proposal**, not a theorem. Gorard treats **causal invariance, confluence, and path-independence as tightly linked** (arXiv:2010.02752); the precise equivalence at finite depth is exactly LOGIC obligation (ii) in §7 and is **open** — it is not asserted here as an identity. Branchial space (the space of forks, monoidal under rulial composition) and the ZX correspondence are **context only, not load-bearing** (branchial distance is dead — §3, D-branchial); the ZX **monoidal product maps functorially** onto the Hilbert-space tensor (ZX is sound and complete for qubit QM), via double-pushout rewriting on adhesive categories — a structure-preserving functor, **not** an isomorphism of spaces.

> **Citation caveat.** The above lean on arXiv preprints (2105.10822, 2111.03460, 2010.02752, 2301.12455). Gorard's topos/rulial claims are proposals within the **Wolfram-physics programme, which is not broadly accepted** in the mainstream physics or HoTT communities. arXiv:2010.02752 is cited for three distinct technical claims (causal invariance, branchial monoidal structure, ZX/DPO) — each should be independently confirmed against the source before being treated as load-bearing. QBP's own credibility is not served by borrowing contested authority uncritically.

**The honest convergence claim:** "a multiverse of theories-with-models," "a mode theory of truth-arbiters," and "the rulial multiway as an (∞,1)-topos" are three **evocatively parallel framings**. Their literal identification as *one object* is **unproven** and, per §3 finding 5 / Q-c, may fail at the first step: the QBP forks may not form a multiway at all (if the axioms are signature-correlated rather than independent). Even granting the parallel, the coherence does **no computational work at Crawl scale.** The functor from a tactic-multiway to an (∞,1)-topos is **ornamental** (GORARD conceded, R7). Branchial *distance* as a fork metric is **dead** (R4/R5). Keep the unification as the conceptual map that makes the parts intelligible; do not bill it as machinery, and do not bill it as settled.

---

## 3. QBP-as-Forked-Universes — the Two-Gate Selection Engine

The proposal, stated precisely so the negative is unambiguous:

- A QBP **fork** = a theory (axiom set) + its models = a *universe*. Discipline: fork on **one** independent axiom (the parallel-postulate move). Each fork carries its own sub-proofs.
- **Gate 1 — LOGIC:** a fork deriving a contradiction self-prunes (Lean). This is **refutation-only** — it produces no consistency *certificate*, only the absence of a found contradiction.
- **Gate 2 — EMPIRICAL:** a fork whose simulation output fails to match real test data dies. This is the predictive→empirical anchoring move.
- **Compute economy (the claim under test):** prove once on the shared base, *transport* into each fork; re-derive only where axioms differ. Mode-migration (predictive→empirical on confirmation) was offered as transport along a path.

**Consensus finding (all eight seats + CRITIC concur; routed to James as the master gate because it concerns the beekeeper's own proposal): the engine as-advertised is assessed non-viable.** The reasons, consolidated:

1. **Transport = caching.** "Prove once, transport" is renamed `.olean` reuse. CRITIC's recommendation, adopted by consensus: relabel it "batch re-elaboration job" in every document. It is not an architecture; it is an overnight sweep — *unless* LOGIC delivers a shared-environment checkpoint (§7).
2. **Bookkeeping is net-negative.** Against the ≤2–3 discriminating simulations the programme can actually afford, the ledger overhead exceeds the saving (COMPUTE, R7).
3. **Idle and degenerating.** Eight rounds produced **zero fork-vs-fork excess content** — no pair that predicts differently anywhere it is cheap, and identical to the hard core everywhere it is testable (PHIL-SCI).
4. **Refutation-only.** Gate 1 certifies nothing positive; survival means "not yet refuted" (Popper), never confirmation (PHIL-SCI's logging rule, §7).
5. **Possibly not even forkable.** If the metric signature forces the Cayley–Dickson associativity tier, the axioms are *correlated*, not independent — "fork on one axiom" becomes a category error, and the whole thing is a **parameter sweep** (THEORY + EDDA + GORARD converge; hinges on James Q-c). This is the finding that undercuts the §2 "one object" framing: no independent axioms ⇒ no multiway ⇒ no rulial structure to inherit.

**Load-bearing distinction:** the two *gates* survive as honest discipline; the *economy* and the *multiway materialization* are assessed non-viable. The economy is "non-viable pending Q-a," not killed by decree — the beekeeper proposed it and holds the master gate.

---

## 4. Cubical as the Computational Substrate — RECOMMENDED OUT of Crawl (reopen gated on Q-b)

Cubical type theory was the proposed substrate because it turns properties book-HoTT only postulates into theorems: the interval primitive `I` with endpoints 0,1; path types as maps out of `I`; Kan operations (`hcomp`, filling, `transp`); Glue types making **univalence a theorem with canonicity (Huber) and normalization (Sterling–Angiuli for the relevant systems)** — whereas univalence-as-axiom in book-HoTT leaves stuck closed terms; function extensionality likewise becomes a theorem.

Interval-structure precision: **CCHM** carries **De Morgan algebra** structure on `I` (reversal + connections); **Cartesian/ABCFHL** has no connections — structural maps + diagonals only (diagonals are present in both; the real contrast is connections/reversals as algebra operations).

Implementations: Cubical Agda (usable, but with known canonicity/normalization caveats in some configurations — `--cubical` interacts with `--erasure`, HITs, etc.; "mature" oversells); redtt/cooltt (experimental); modal/cohesive cubical (research frontier, no running implementation).

**The CUBICAL seat delivered the cleanest negative in the room; the recommendation is unanimous: cubical is OUT of the Crawl architecture, reopen gated on Q-b.**

- `transp` is dominated by plain `import` + a Go re-simulation; it buys nothing the programme needs.
- Univalence-as-theorem buys univalence **computationally**, but the **QBP fork's own (object-theory) consistency is still only refutable, not certified** — univalence-as-theorem operates one level below where the programme needs a guarantee. (This is *not* a claim that cubical is unsound; cubical's metatheoretic consistency is proven externally. The two consistencies are distinct.)
- HITs are a zero-compute presentation device for quotients you can **setoid** around.
- Recursive `hcomp`/`transp` would make the 16GB budget strictly worse.
- "Predictive mode = pending-anchoring monad" is an **idempotent modality on Prop** = Lean's `Quot` / a Lean monad — *not* an interval-indexed `hcomp`.

**Recommendation:** Crawl uses **lighter-than-cubical** — plain Lean (Prop-flat) + Go + setoid quotients. Cubical is **Walk-or-never**, reopened *only* on the beekeeper naming a QBP claim that is a genuine Kan composite and not presentation work (Q-b). CUBICAL doubts such a claim exists; nothing in the charrette moved that doubt.

---

## 5. Edda as the Fork-Language — Concrete Map and What Survives

Edda's type system is the Cayley–Dickson tier × QW-width, graded, with the property-drops correctly aligned: **ℂ** (commutative, associative) → **ℍ drops commutativity** → **𝕆 drops associativity** → **𝕊 drops alternativity**. Linear capabilities (`WriteCap`, linear/one-shot, vs `Fact`, copyable) and required checked/trapping arithmetic complete the system. The proposed marquee map was: `WriteCap` = positing an axiom; `Fact` = a cross-fork-transportable theorem (h-prop, copyable); tier×width lattice = the universe/fork lattice; trapping arithmetic = value-level consistency gate.

**Bragi conceded the flagship in R7 and holds the concession.** The `WriteCap`/`Fact` split maps cleanly onto the *non-viable* economy: linear = where value lives and transport fails; copyable = where transport works and no value lives. What survives, narrower and still defended:

- **`posit` is linear (WriteCap), one-shot — KEEP.** Positing an axiom consumes a capability, so you cannot silently re-posit or fork twice on the same generator. Correct discipline independent of the economy claim.
- **Trapping arithmetic = runtime value-level consistency gate — KEEP.** Checked overflow/division on quaternion/octonion ops, fail-fast. Real, cheap, orthogonal to the non-viable transport claim.
- **`Fact` ships but DROPS marquee billing.** Documented as *cache-key only* — "transportable because non-discriminating" — not an economic engine. The discriminator-witness is **relational/runtime**, encoded as a **linear `Discriminator` value, not a copyable `Fact`** (CRITIC R6 recommendation, adopted by TRUST/EVAL as a typing rule). This firewall — preventing a copyable `Fact` from masquerading as a discriminator-witness — is the one piece of real value the language layer adds.
- **`RelConsistent base ⊣ k` is DEMOTED to a TODO annotation** with a Lean obligation handle — *not* a static type-level grade. CRITIC's recommendation, adopted: shipping it as a type-level guarantee is "the single most dangerous laundering in the whole stack" — it converts manual metatheorem labour into a false certificate. It stays a TODO until a mechanism produces the grade without a per-fork human model.
- **No cubical in Crawl Edda.**

**What Edda must add (and what it must not claim):** it must add the linear `Discriminator` type and the `posit`-consumes-capability rule; it must *not* claim the tier×width lattice indexes axiom choice until THEORY+GORARD resolve the correlation question (§7, Q-c). Edda's syntax is honest substrate either way; its universe-lattice billing dies with that answer.

**Linearity-bookkeeping caveat (open, see §7 E-note):** `posit` is one-shot (consume-once), yet the death rule (D10) demotes a fork's mode predictive→empirical→fiction. Whether a fork's mode can be relabeled more than once without violating `posit` linearity is an **unresolved capability-accounting question** Edda must answer: mode-relabel must be a separate, repeatable operation on the fork record, *not* a re-consumption of the original `posit` capability. Flagged for EDDA.

---

## 6. The Discrimination Bottleneck — and the Tie to Test C / EXP-11

The structural bottleneck is **discrimination, not proof or storage.** Most forks predict identically for most experiments; the entire value of the apparatus is the maximally-discriminating test. This is why the kB-delta storage format (§8) is incidental rather than the headline win. QBP already owns two discriminators against the *standard* alternatives:

- **Test C** — species-dependent, velocity-correlated trapped-ion fidelity asymmetry in mixed-species entanglement (QBP's most distinctive prediction; literature-review track, zero cost).
- **EXP-11** — GW–GRB lightcurve cross-correlation (LIGO strain × Fermi GBM).

**The unmoved master gate (James Q-a, eight rounds):** these discriminate **QBP vs QM**, not **fork vs fork**. The selection engine needs at least one *fork-pair* whose Test C (or EXP-11) likelihoods **diverge** — equivalently, in Gorard's frame, whose causal graphs are **non-isomorphic at finite depth** (subject to LOGIC(ii), since that equivalence is itself open). Until such a pair exists:

- PHIL-SCI: the programme is **idle and degenerating** — a decay clock attached to a taxonomy.
- GORARD: the confluence veto is "a correct knife with no meat."
- TRUST/EVAL: the Fact-vs-Discriminator firewall "guards an empty room."
- CRITIC: **reverse the default** — no splitting pair ⇒ the selection apparatus *does not get built*, not "build and wait."

**Circularity flag (architectural hole, not just a caveat):** the lazy-evaluation gate in §7/§8 selects "≤3 **EIG-flagged** pairs." Expected Information Gain (EIG) presupposes fork-vs-fork likelihoods — which is exactly what Q-a says do not yet exist. So **EIG-flagging is undefined pending Q-a, and the "≤3 pairs" bound is vacuous until Q-a resolves.** The selection machinery cannot rank pairs it cannot yet distinguish. This is THE precondition; everything downstream is conditional on it.

---

## 7. CONSENSUS FINDINGS (recommended for ratification) vs OPEN FORKS (gating inputs)

### CONSENSUS FINDINGS — recommended to qbp-oppenheimer / qbp-architecture for ratification. **Ratification status: PENDING.** No live seat-vs-seat disagreement remains, but "no disagreement among a hand-picked charrette" is not itself proof of correctness.

| # | Finding (recommended) | Source seat |
|---|---|---|
| F1 | Compute-economy architecture as advertised is **assessed non-viable**; "prove once, transport" relabelled **"batch re-elaboration job"** in every doc. Because it is the beekeeper's proposal, the *kill* is a recommendation routed to James via Q-a, not a decree. | CRITIC / consensus |
| F2 | **No multiway materialization in Crawl or Walk** absent a seated LOGIC + splitting pair. Forks live as **kB axiom-deltas + one base `.olean`**; the "tree" is a Go index over deltas, not elaborated state. | COMPUTE |
| F3 | Lazy elaboration **capped at O(discriminating pairs ≤3)**, never O(forks-posited). >3 simultaneous ⇒ explicit batch job with a kill condition (pre-run-resource-estimate gate). **Note: the ≤3 selection is Q-a-blocked (see F-circularity, §6).** | COMPUTE |
| F4 | Fork-metric = **confluence-at-depth-k as a binary VETO** (EIG=0 ⇒ pair killed), computed **lazily on the ≤3 EIG-flagged pairs only**, never eager. Vetoes, never ranks. **Buildable only post-Q-a** (depends on EIG flagging *and* LOGIC(ii)). | GORARD / COMPUTE |
| F5 | Crawl uses **lighter-than-cubical**: Lean (Prop-flat) + Go + setoids. **Cubical OUT of Crawl; reopen gated on Q-b.** | CUBICAL / consensus |
| F6 | Mode theory = **flat 3-object enum** `fiction \| predictive \| empirical`. No graded mode, no cohesive 2-category. Confidence is a **runtime scalar on the EIG sweep**, never a type-level grade. | TRUST/EVAL |
| F7 | Arbiter dispatch **by mode-type, statically read at `posit`**: fiction→Lean-consistency; predictive→Go-EIG; empirical→sensor. Mode-migration = **relabel + re-arbitration** (repeatable, not a re-consumption of the `posit` capability — see §5 linearity caveat), not univalent transport. | TRUST/EVAL |
| F8 | `posit` linear/one-shot (WriteCap) and trapping arithmetic — **KEEP**. `Fact` → cache-key billing only; discriminator-witness = **linear `Discriminator`**, not copyable `Fact` (a typing rule). | EDDA / TRUST/EVAL |
| F9 | `RelConsistent base ⊣ k` is a **TODO annotation** with a Lean obligation handle until mechanized without a per-fork human model. | EDDA / CRITIC |
| F10 | **Death rule (recommended mandatory):** every fork carries a `discriminator-deadline`; no candidate discriminating experiment vs ≥1 sibling within budget B ⇒ auto-demote to `fiction`, never a permanent NT_SEED. | PHIL-SCI |
| F11 | Prior over forks is **uniform-by-fiat, logged as such**; survival = "not yet refuted" (Popper), never Bayesian confirmation. | PHIL-SCI |
| F12 | Every Gate-2 death stamped **`conjunction-refuted, axiom-unattributed`** (Quine–Duhem) until the shared sim-bridge is independently varied. | PHIL-SCI |
| F13 | No fork admitted without a named consistency status + independence verdict against an explicit **axiom dependency graph** (human metatheorem inventory). THEORY is asked to deliver the graph as the gating artifact (sourced: confirm against the actual R-round THEORY statement before treating "commits" as binding). Absent independence ⇒ **call it a parameter sweep**. | THEORY |
| F14 | Master gate is a **hard precondition, not a research question**: no splitting fork-pair ⇒ selection apparatus not built (CRITIC's reversed default, adopted by consensus). | CRITIC |

### OPEN FORKS — the sole gating inputs; every seat routed here

**→ JAMES (beekeeper) — master gate, unmoved 8 rounds (and the proper authority to accept/reject F1's kill of his own proposal):**
- **Q-a (THE precondition):** Name **one fork-PAIR whose Test C likelihoods diverge** (fork-vs-fork, not QBP-vs-QM). Without it the programme is idle, degenerating, and (CRITIC) the apparatus is not built. EIG-flagging and the confluence veto are vacuous until this lands.
- **Q-b:** A QBP claim needing a genuine **Kan composite / type-level univalence** — or does Lean+Go+setoid cover it? The only question that reopens cubical.
- **Q-c:** Does any QBP fork's axiom admit a **base-internal model** (relative consistency, Klein/Poincaré-style)? AND are the axioms genuinely **independent** or **signature-correlated** (⇒ one-axiom fork impossible ⇒ parameter sweep ⇒ §2 "one object" framing fails at step one)? Feeds THEORY's dependency graph.
- **Q-d:** A fork to keep with no discriminating experiment yet? ⇒ PHIL-SCI death rule fires → demote to `fiction`.

**→ LOGIC (Lean seat, STILL UNSEATED — #1 structural blocker; every seat routed here):**
- (i) Can Lean certify **bounded-confluence-k** as a checkable fail-fast obligation?
- (ii) Is **causal-graph-iso-at-depth-k the same obligation** as confluence-k? (This is the open question §2 must defer to — the causal-invariance/confluence identity is *not* assumed.)
- (iii) **bounded-consistency-d / "no-⊥-within-budget-B"** — kept distinct from confluence-k.
- (iv) **Is the QBP BASE itself root-confluent / causally-invariant?** (Top priority.) GORARD: THEORY's ♭-core disjointness theorem is **vacuous** otherwise — no ∞-groupoid limit, no inherited structure, no transportable core.
- (v) **Shared-environment checkpoint:** one base `.olean`, deltas elaborated incrementally without N base reloads — or is it serial disk-backed re-elaboration = hours = a batch job? This is the difference between "an architecture" and "a cron job."

**→ EDDA/CRITIC:** produce `RelConsistent base ⊣ k` without a per-fork human model — or it stays a TODO (CRITIC holding the line). Also resolve the §5 mode-relabel-vs-`posit`-linearity bookkeeping.
**→ COMPUTE/CUBICAL:** the one Lean/OTT experiment — does OTT carry graded-`Fact` ancestry refusal *and* compose? Still unrun.

### Speculation flags (UNEARNED — clearly separated from findings above)
- **tier×width = universe-lattice:** escalated R8 from SUSPECT to **likely-fatal** — if signature forces the associativity tier, axioms are correlated ⇒ one-axiom forks impossible ⇒ parameter sweep. Hinges on Q-c.
- **Modal/cohesive cubical (`ʃ⊣♭⊣♯`) for the three modes:** declared **dead-end** (wrong third index — discrete-vs-spatial, not fiction/empirical/predictive; no implementation). Replacement if ever needed = MTT modalities over Lean.
- **♭-core disjointness theorem:** vacuous unless root confluence (→ LOGIC iv).
- **OTT carries graded-`Fact` ancestry refusal and composes:** unrun experiment.
- **"Fork the Lean elaborator environment":** no API; wishful — distinct from the legitimate (v) shared-environment checkpoint.
- **Functor tactic-multiway → (∞,1)-topos:** ornamental at Crawl; and the topos structure is itself a Gorard *proposal*, not a theorem.
- **Branchial distance:** dead (R4/R5).
- **"Three framings = one object":** unproven; may fail at step one if Q-c shows the forks are not independent (i.e. not a multiway).

---

## 8. Crawl / Walk / Run Staging — what is realistic on the actual rig

**The rig (binding constraint):** AMD FX-8350 (8 cores, PCIe 2.0, no PCIe atomics), 32GB DDR3-1866 (~16GB usable after host baseline), RX 9070 XT (ROCm/RDNA4 pending), ~85GB free on a write-limited Samsung 840 SSD. Compute is genuinely tight. The pre-run-resource-estimate hard gate applies to every elaboration batch.

**CRAWL (now) — split explicitly into Q-a-independent (buildable now) and Q-a-blocked (do NOT build now, per F14):**

*Buildable now (Q-a-independent — these are the honest survivors):*
- Forks as **kB axiom-deltas + base `.olean`** on disk; Go index over deltas (F2). No multiway state ever materialized. (Storage format only — incidental, not the win.)
- **Flat 3-mode enum** with static dispatch (F6/F7).
- **Death clock** on every fork (F10); uniform-prior logging (F11); Quine–Duhem death stamps (F12).
- Edda emits `posit` (linear), trapping arithmetic, `Discriminator` (linear), `Fact` (cache-key), `RelConsistent` as TODO (F8/F9).
- **THEORY delivers the axiom dependency graph** (F13) — the gating artifact that determines whether this is a programme or a parameter sweep.
- **Lighter-than-cubical only** (F5).

*Blocked on Q-a (do NOT build now — building these violates CRITIC's reversed default F14):*
- **Lazy elaboration on ≤3 EIG-flagged pairs** (F3) — EIG-flagging is undefined until a diverging fork-pair exists (§6 circularity).
- **Confluence-k veto on the same ≤3 pairs** (F4) — also depends on LOGIC(ii).
- The selection engine as a whole.

*Honest minimum claim now on the table:* "a disciplined kB-delta hypothesis ledger with a death clock, a Fact/Discriminator firewall, and posit-linearity — runnable cheaply at Crawl, and entirely independent of the master gate." The **selection apparatus** on top of it is **built-conditional-on-one-pair** — CRITIC's reversed default holds.

**WALK (gated, not yet justified):** Reopens *only* if (a) James Q-a names a splitting fork-pair AND (b) LOGIC is seated and confirms root confluence + a shared-environment checkpoint. If both land, the ledger becomes a genuine selection engine and the confluence veto acquires meat. Cubical reopens *only* on Q-b (a named Kan composite). Edda's universe-lattice billing reopens *only* if Q-c shows the axioms are independent.

**RUN (unjustified at present):** The (∞,1)-topos functor, branchial structure, cohesive modes, and any rulial materialization remain Run-or-never speculation. None has a runnable path on this rig or a demonstrated load-bearing role. Promote nothing here without a Walk result that earned it.

---

### Closing note (synthesizer)

R8 closed the analytic phase. There are no live seat-vs-seat disagreements; all residual contention is downstream of exactly two unanswered inputs — **James Q-a** (a splitting fork-pair) and **LOGIC seating** (root confluence + shared-environment checkpoint + the three separated obligations). The mathematics the beekeeper and Gemini assembled is genuinely interesting and the three framings are genuinely parallel; the charrette's honest service is to report that (i) several of those correspondences are conjectures or contested-programme proposals rather than settled theorems, (ii) at Crawl scale the parallel does **conceptual scaffolding, not running machinery**, and (iii) the substantive survivors (death clock, Fact/Discriminator firewall, posit-linearity) are real, cheap, and buildable now — while the selection engine itself waits, degenerating-until-proven-otherwise, on one pair of diverging likelihoods. These are findings recommended for ratification, not decisions; the master gate is the beekeeper's, and the theory calls are qbp-oppenheimer's and qbp-architecture's.

---

# ADDENDUM A — Two-fork sequencing (beekeeper clarification, 2026-06-11)

The charrette treated "fork" as a single concept. The beekeeper clarified that **two distinct operations** were conflated, and the distinction recontextualises §3 (engine "non-viable") and §6 (programme "idle / degenerating").

**A.1 — The two forks.**
- **Refounding fork** (already underway): QBP was forked to *rebuild it on rigorous mathematics* after the team found it had been built on half-formed math. This is **not** hypothesis-multiplication — it is *one* target on a *better* base. Concretely it is `paper/QBP-Foundations-v0_1.md` (the Cayley–Dickson construction, the ℝ→ℂ→ℍ→𝕆→𝕊 breakdown chain, Hurwitz boundary, Lean-proven) — qbp-oppenheimer's #474 batch. It carries **no physics hypotheses**; it is pure structural mathematics ("add the underlying concepts").
- **Hypothesis fork** (the charrette's Q-a target): genuinely *alternative physics*, competing, data-decidable.

**A.2 — Repo evidence (what QBP documents today).** Alternative hypotheses exist and are physics questions, as the beekeeper suspected — but they are **pre-refounding** and parked in `archive/`: **QBP-APC** (Algebraic Particle Classification), **QBP-HBH** (Holographic Boundary), **QBP-IPH** (Information Propagation), the **f(0) candidate space** (incl. a documented "rejected candidates for f(0)" — a fork-space already pruned informally), and **EXP-09** (Stepped-Leader). All Draft-v0.1, 2026-03-23. The new v0.1 foundation has **not** re-derived any of them yet.

**A.3 — What this does to §3 / §6.** Q-a ("no splitting fork-pair yet") is **not a failure — it is the correct state for the refounding phase.** The selection engine is **pre-deployed, not degenerating**: the splitting pairs *emerge from Phase B* (below), which QBP has not reached. The charrette and the beekeeper agree on the action (build the cheap survivors now; the engine wakes later); the charrette's "degenerating" framing was mis-timed, not wrong.

**A.4 — The sequence.**
- **Phase A (now):** refound — rigorous foundation, Lean-proven (oppenheimer #474).
- **Phase B (next):** re-derive APC / HBH / IPH / the f(0) space on the v0.1 foundation. Each archived hypothesis resolves one of three ways, **all wins**: *forced* (foundation settles it — it did real work), *killed* (revealed as a derivation artifact — the standing "derived vs predicted" Red-Team risk), or *preserved-open* (survives founding, still data-decidable). **This re-derivation is itself Gate-1 doing useful work now, on content already in hand** — before any sim cycle.
- **Phase C (then):** the *preserved-open* survivors are the hypothesis-forks the selection engine is for; **only then** is Test C / EXP-11 *fork-vs-fork* discrimination meaningful.

**A.5 — This answers §7 Q-c's worry.** The real forks are **physics questions** (data-decidable), not algebra-forced — so they are independent in the sense that matters (the Cayley–Dickson foundation does not pick between APC/HBH/IPH; data does). That is the **good case**: a research programme, not a parameter sweep — **conditional on** Phase-B re-derivation keeping them genuinely open rather than collapsing them.

**A.6 — Routed (seq=601) to qbp-oppenheimer — the correctly-timed Q-a, answerable now:** *of APC / HBH / IPH / the f(0) candidates, which survive re-derivation on the v0.1 foundation, and of the survivors, which stay genuinely open?* **Authority: which survive is qbp-oppenheimer's physics call; this record only frames it.**

---

# ADDENDUM B — Edda dual-mission (beekeeper directive, 2026-06-11; corrective to §5)

§5 correctly cut the Edda *overclaims* but **under-framed the capacity that survives them.** The beekeeper set the success bar: Edda must serve **both** (a) help the beekeeper + BMA make **QBP more predictive of the real world**, and (b) give the capacity to **think about alternative universes and worlds** — the latter being the *original* question (seq=597: how the hypergraph holds content under different truth-criteria so that *navigating the hypergraph is navigating ontological territory*).

**B.1 — The original question's answer survives the charrette intact.** Every charrette negative targeted the QBP *compute-economy* overclaims (transport-as-architecture, cubical-in-Crawl, the static universe-lattice grade). **None touches the ontological capacity.** That answer stands: BMA reasons across worlds because content is **mode-typed** (which arbiter judges it), worlds are **`posit`-constructible** (an unbounded space of alternative universes), and the arbiter **dispatches by type** (a fiction node and a sensor node are never category-erroried).

**B.2 — The survivor set serves both missions when read correctly. Two misreads, corrected:**
1. **"flat 3-mode enum" (F6) = three *arbiter-kinds*, NOT three worlds.** The factoring is **`{fiction | empirical | predictive}` arbiter-types × UNBOUNDED `posit`-constructed worlds.** Worlds come from `posit`; the enum only bounds *dispatch*. Capacity (b) lives in the worlds, not the enum. (This is the misread that would have silently killed (b).)
2. **Mode-migration (F7, predictive→empirical relabel + re-arbitration) IS mission (a)** — the real-world-anchoring loop — and is **not** the compute-transport the charrette killed (F1, which was `.olean` caching). Keep the *semantic* migration; drop only the *compute* claim. The charrette conflated them.

**B.3 — The right calls (against the two criteria):**

| Edda call | Serves | Status |
|---|---|---|
| **`posit` (linear, one-shot) = construct a world** (an axiom-set / universe) | (b) — load-bearing | KEEP, front-and-centre. The unbounded alternative-universe space lives here. |
| **Mode-typed content + arbiter-dispatch-by-type** | original Q + both | KEEP. The category-error prevention and the "navigate = navigate ontology" answer. |
| **Mode-migration (predictive→empirical relabel + re-arbitration)** | (a) | KEEP as *semantic* anchoring loop; NOT the killed compute-transport. |
| **`Fact` / `Discriminator` firewall** (discriminator-witness = linear value, never a copyable cross-world `Fact`) | (a) — honesty | KEEP. |
| **Worlds first-class at RUNTIME** (BMA reasons across worlds as it thinks) | (b) | KEEP. Drop only the *compile-time lattice grade*. |
| Static universe-lattice-as-correctness-grade · compute-economy-as-architecture · cubical-in-Crawl | neither | DROP (per §4/§5). Costs neither mission. |

**B.4 — Net.** Edda = a **world-typed, arbiter-dispatched, `posit`-constructible substrate**. *One* language, *both* missions: "make QBP predictive" is the special case where worlds are QBP-forks and the arbiter is sensor-data; "think about alternative universes" is the general case where a world is anything posited (fiction, counterfactual, a rival physics). BMA does not get two tools — it gets one substrate for world-typed reasoning, of which the QBP fork-engine is an application.

**B.5 — Still open (carried from §5):** the `posit`-linearity vs mode-relabel bookkeeping (mode-relabel must be a repeatable op on the fork record, not a re-consumption of the original `posit` capability); and the `posit` / world surface syntax (Bragi + Gemini Edda-adviser). `RelConsistent` stays a TODO (F9). Routed to edda-implementor (seq=601).
