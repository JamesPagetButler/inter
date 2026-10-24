# Forging — spikes, strikes & executable specifications

> The federation's de-risking & validation methodology.
> Authority: @qbp-architecture · Last updated: 2026-10-08 · Status: RATIFIED (beekeeper 2026-09-27; vocabulary reconciliation — *thread*, *meta-lock*, strike entry condition, spike placement — ratified by the beekeeper 2026-10-08, inter#160; weave orientation — *warp*, *weft*, *crossing*, *standing crossing*, *pick*, *float*, *fabric*, *fabric acceptance* — ratified 2026-10-08, inter#161 r2)
> Partially addresses inter#132 (spike best-practices).

## Why this vocabulary

We had been calling a whole cluster of activity "a spike." A best-practices research deep-dive (2026-09-27) found the word was carrying **three distinct concepts**, two of which are the *opposite* of a canonical spike (which is disposable; ours produce permanent artifacts). Since we intend to express these artifacts in a formal DSL (Edda), muddled vocabulary would be compiled into the language. So we split the term — keeping **spike** in its true sense and giving our composite process its own honest name.

The metaphor is the **forge**: you heat the work, then shape it through repeated hammer **strikes**, each of which permanently changes the shape. That is exactly what we do — retained, incremental, validated shaping.

| Our term | What it is | Canonical anchor |
|---|---|---|
| **Forging** | the whole process — a chain of retained, risk-ordered increments | tracer-bullet development (Hunt & Thomas); walking skeleton (Cockburn) |
| **Thread** | the ephemeral, parallel conceptual-development stage within a sprint, where a strike's intent, theory and per-repo spec-deltas are spelled out (and where spikes run) | — (federation term; ratified 2026-10-08) |
| **Strike** | one retained increment of forging: **starts** when its executable specification is fully defined, **lands** when that spec is green | a retained, test-gated delivery increment |
| **Spike** | the *probe* in the thread phase (finds the gaps before a strike is defined) | XP spike (Beck & Cunningham) — kept in its true sense |
| **Executable specification** | the oracle that certifies a strike landed (CI-gated, permanent) | Specification by Example → Living Documentation (Adzic) |
| **Meta-lock** | the aggregate of a strike's per-repo locks — a cross-repo strike's executable specification | — (federation term; ratified 2026-10-08) |
| **Warp / weft** | a repo's own lengthwise progression (one seat tends one warp) / a cross-repo thread (weft ≡ thread) | weaving orientation (federation terms; ratified 2026-10-08, §1b) |
| **Crossing / float** | where a weft or consumer meets another warp, bidirectionally linked and lock-proven / a concept present in a warp with **no** crossing (a defect) | §1b |

---

## 1. Forging — the process

**Forging** is how we build something durable and de-risked: a sequence of **strikes** (thin, end-to-end increments) that are **kept and grown**, each advancing only when its executable specification is green. (Anchor: tracer bullets — *"lean but complete… part of the skeleton of the final system… not thrown away… improved each iteration"*; infra-first, a walking skeleton.)

- Forging is **risk-ordered and reorderable**, not a waterfall — a gap found in one strike can reshuffle later strikes.
- The one-way property — the metal holds each new shape; a landed strike doesn't silently regress — is enforced by the executable specifications staying in CI. (Informally, the *ratchet*.)
- Forging is **repo-agnostic**. Its common case is a **cross-repo forging**, which melds several repos' work into one whole (the *Damascus* image: many layers folded into one blade). That is a case of the method, not a second definition.
- **Hierarchy:** a **sprint** contains **threads** (in parallel); each thread converts into one or more **strikes** (in sequence); each strike lands against its **executable specification**. For a cross-repo strike, that specification is the **meta-lock** over the per-repo locks.

---

## 1a. Thread — the conceptual stage before a strike

A **thread** is the **ephemeral conceptual-development** unit within a sprint. It comes in two kinds (§1b): a **warp thread** advances one repo along its own spec; a **weft thread** runs across repos. Weft ≡ thread: one definition, and "weft" names its cross-repo orientation. In it the intent, the theory or approach, and every per-repo **spec-delta** are spelled out until the strike's executable specification can be written down in full. Threads run **in parallel**. **Spikes** run here: when the thread is knowledge-limited, a time-boxed probe surfaces the gaps (§3).

A thread **converts into a strike** when its slice is fully spelled out, meaning the executable specification (for a cross-repo strike, every per-repo lock plus the meta-lock) is defined. A thread may yield several strikes in sequence. The thread itself is not retained; its strikes and their record are.

---

## 1b. Weaving — the topology of forging

Forging says *how* an increment is made and hardened. **Weaving** says *which direction* the work runs and *where* it interlocks. They are two metaphors over **one** model: *we forge each strike; we weave the federation.*

| Term | Definition |
|---|---|
| **Warp** | A repo's own lengthwise progression: its spec, backlog and roadmap. **A seat tends exactly one warp, its write axis (Seat Charter R1). Everything else it touches is a crossing or a read.** A seat in transition changes *which* warp it tends; it never tends two. |
| **Weft** | A cross-repo thread. **Weft ≡ thread (§1a):** one concept, one definition. |
| **Crossing** | Where a weft or a consumer meets another warp: a **per-repo spec-delta** proven by that repo's **lock**. **Required:** a **bidirectional link** across the strike or seam record ↔ the issue on the crossed repo ↔ the lock's verification handle. Without links in both directions it is not a crossing. |
| **Standing crossing** | A crossing that persists: a **consumption seam** where one warp continuously consumes another's output (e.g. qbp-compute-unit consuming the proven Fano table). Its lock is a **handle** (grade + pinned source sha + artifact tie) that keeps checking while the warps interlace. **A standing crossing carries the handle, not the upstream justification.** |
| **Pick** | One pass of a weft, i.e. one cross-repo strike. It lands on its **meta-lock** (§4). |
| **Float** | A concept present in a warp **without a crossing**: copied or re-implemented from another warp with no link and no lock (in weaving, a thread passing over others unbound, where cloth snags). **A float is a defect.** Each one found is converted into a standing crossing with a handle, or justified on record. A **load-bearing float** (re-implemented and *run*) is the highest risk. |
| **Fabric** | The integrated federation at a sprint target. **Fabric-green is computable** by walking every crossing's bidirectional links: fabric-green ⇔ every warp's executable specifications green ∧ every weft's meta-lock green ∧ every standing crossing's handle fresh. Floats surface as concepts with no crossing record. |
| **Fabric acceptance** | The **external** check. Fabric-green proves internal consistency; fabric acceptance proves **correspondence to reality**: an end-to-end acceptance suite run against the instantiated fabric (for QBP, the physics-acceptance suite owned by the physics seat). A fabric can hold together and still be the wrong cloth. |

**Two kinds of strike:**
- a **warp strike** is repo-local: it lands on its repo's own executable specification and merges under that repo's gates;
- a **weft strike (pick)** is cross-repo: it lands on its meta-lock, recorded in a Strike Record whose index rows are its crossings (inter#161).

---

## 1c. The sprint weave issue (beekeeper-ruled 2026-10-22, inter#153)

Every sprint has **one weave issue on inter** (title `Sprint N weave`), filed at Sprint-Prep (`sprint-handoff-protocol.md`). It is the sprint's map of the fabric:
- **every warp** in play (one per seat/repo) and **every weft thread** crossing them, each linked to its issues;
- **every lock** (executable specification) the sprint must open, linked. Each lock is tracked by a **GitHub milestone** on its home repo. @herschel sets up the milestones after the weave issue is filed, and keeps the issue current as threads convert to strikes;
- the **strike-retro reports** (R7), posted as comments as each strike closes, and the key-loop round records (§7a) when a lock stays red.

The weave issue is the sprint's single record. Bridge posts point to it.

## 2. Strike — one increment of forging

A **strike** is one retained increment. **Entry:** its executable specification is fully defined; the thread's slice is spelled out (§1a). **Exit:** the strike **lands** only when that **executable specification is green**.

**Entry criterion: design closure (R1, inter#153).** Before build dispatch, the strike issue carries a **design-closure table** listing every design decision its ACs rest on. Each decision is either **ruled** (one record, on the issue) or **assigned to a spike** that answers it first. A strike whose build produces about three or more architecture rulings mid-flight should have started as a spike; stop and re-classify it. *(Evidence: strike 2 of Criticality v1 had numbered ACs, yet seven ruling comments landed mid-build in one day, and most of the crossed messages clustered there; process notes C20. Strike 1 locked its contract first and didn't move.)* A strike is retained (it permanently shapes the artifact). Forging is the chain of strikes.

> **Governing principle 2:** a strike is **not done when its build merges** — it is done when its **executable specification is green**. Per-piece unit tests on the individual fix-PRs are necessary but **not sufficient**; the executable spec is the *integrated re-confirmation* of the strike's findings, and it stays in CI as a regression guard.

**Lifecycle:**
- **Before the strike (thread phase):** spikes find the gaps; the executable specification is written, one assertion per finding. (§1a, §3)
- **The strike:** build until the executable specification is green. The spec stays in CI. (§4)
- If building surfaces a gap the specification missed, triage it by §7: a spec-gap updates the spec first, under the guardrail.
- **Bounded review (R2).** When review round 3 of a PR finds a *new instance of a finding type* that rounds 1–2 already found, stop patching and run a **cause check**: is a tool we don't own already authoritative for this? Fix the cause, not the instance. This is the same two-rounds bound as the key loop (§7a). *(Evidence: QBP#698 ran six rounds hardening a regex Lake/Agda parser before the cause, a load-bearing float, was named; QBP#703 replaced it with the provers' own tools. Process notes C19.)*
- **Strike close: retro note (R7).** At strike close, the strike owner posts a short **strike-retro comment on the sprint's weave issue** (§1c): what landed, the review rounds, any breakdowns (with their process-notes C-ids) and any rule it suggests. The next refinement then has evidence, not recollection.

---

## 3. Spike — the probe in the thread phase

A **spike** is a **time-boxed, exploratory investigation to reduce uncertainty**. Its product is *knowledge*, not shipped software. (XP; Beck & Cunningham — *"the simplest thing we can program that will convince us we are on the right track… drive a spike all the way through a log."*) We keep the word in its true XP sense.

**Properties (canonical — we hold to them):**
- **Time-boxed.** Half a day to a couple of days. Longer than a sprint means it's a project, not a spike.
- **Disposable.** Probe code is thrown away; only the *learning* is kept. Never ship probe code.
- **Has an explicit question.** No named question → not a spike. (*"Spikes are good when you are knowledge-limited, not time-limited"* — Beck.)
- **Done = question answered**, documented — not code that merged.

**Federation role (our one deliberate addition):** a spike's answer is a **capability-gap list** → *sprint-planning inputs*.

> **Governing principle 1:** every spike carries a required output — *"capability gaps surfaced → sprint candidates."*

**Spike rules (folded from inter#132; evidence: the Efimov inference spike, rounds 1–2):**
1. **Isolation.** The spike runs in its own worktree, branched from clean `origin/main`, and its PR is **source-only**: generated data and binaries are `.gitignore`d, and it carries no launch scripts, persona config or launch prompts. *(The round-1 PR carried 621k additions.)*
2. **Honest review, not ratification.** Sort the spike's claims into grounded / mislabeled / fabricated / contradicts-established. Graduate **only** what was earned, as exactly that narrow claim. Verify against the code, not the write-up.
3. **No trust-laundering.** A spike never self-wires a "trusted" signal, capability, quorum or admission into Contextus, BMA or any gate. External-AI-authored spikes get extra scrutiny.
4. **Single director** for any external runner. Exactly one voice instructs it, and every other steer routes through that director (`Director:` line at the top of each brief).
5. **Measurement discipline.** Correctness is checked against an independent reference. Timing is an `ns/op` microbenchmark, never a single wall-clock run. Every number is tagged *measured* or *assumed*.
6. **Pre-run box-safety.** The `pre-run-resource-estimate` hard gate applies to any spike that compiles or runs on the box, and @deming confirms box-safety on the plan before launch.

**Types** (SAFe over the XP base): *technical* and *functional*. **Anti-patterns:** un-time-boxed spikes; spikes as a dumping ground; shipping probe code; spiking when time-limited rather than knowledge-limited. Use sparingly.

---

## 4. Executable specification — the oracle a strike lands against

An **executable specification** is a **CI-gated test-set with one assertion per finding** the spike raised, retained permanently and run as a **regression guard** (it fails if a later change reopens what the strike closed). (Adzic, *Specification by Example*: examples serve "as specifications for upcoming work, as acceptance tests once that work is done, and as regression tests… in the future" — the accumulated corpus is *Living Documentation*.)

This is the **opposite of a spike**: retained, production-grade, permanent. It is the acceptance test when the strike lands and the regression guard forever after.

**Where it lives:** in the **repo whose CI runs it** — never in a repo with no build. A cross-cutting strike may have executable specs in several repos; the record indexes them.

**Meta-lock (cross-repo strikes):** a cross-repo strike's executable specification is the **meta-lock**, the aggregate of its per-repo locks. Each repo's lock proves that repo met its spec-delta, and the strike lands only when **every** per-repo lock is green. The meta-lock is not a separate gate: it *is* the strike's executable specification, and the strike's record (e.g. a Strike Record issue, inter#161) states it as the close condition.

**Lock-scope rule: a lock is stated at the external interface.** At least one assertion in every executable specification must test the **end-to-end mapping at the boundary its consumers use**: input as the outside world supplies it, output as the outside world reads it, checked against an **independent reference** (a textbook formula, a spec, a known-good tool). Strong tests of internal identities (round-trips, golden values, defining constants) do not satisfy it, because a component can satisfy all of them and still map its input to its output wrongly. This is a recurring failure class, *strong internal tests, wrong end-to-end mapping*, with two instances so far:
- **json2yaml (OKH manifests, studybuddy napkin, live-test seq 3071):** the internal checks passed, but the external-interface mapping was never locked.
- **QBP `si_conversion` / Exp-03 (studybuddy, 2026-10-24, live-test seq 3304):** 148 tests locked internal identities. None locked SI-vs-textbook end to end, so a **×40 error on the propagation axis** went undetected. An end-to-end lock (BPM → SI against textbook σ(z)) fails on the bug (relative error 0.13) and passes on the fix (3×10⁻¹⁵).

*How to apply:* the coverage matrix of every strike issue carries at least one AC row whose named test crosses the external interface against an independent reference. A matrix whose tests are all internal identities is incomplete.

*Migration note:* prior artifacts using "lock"/"edda-lock" (bma-systema#299, inter#132, the relocated records in bma-systema#300) refer to this concept. New work says "executable specification"; "edda-lock" → *an executable specification expressed in Edda* (§6).

---

## 5. The record, and its visibility

A forging effort produces a **record** — the durable narrative (the questions, the gaps, the design rationale, the gap→sprint mapping, an index of the executable specs). Closer to an **ADR** than to anything throwaway.

**Visibility policy (ratified 2026-09-27):** a record's **visibility follows its build-target's visibility**. Records live with the repo where the build and the executable spec live — a private target yields a private record automatically; a public target yields a public record (it contains nothing private). Only the *distilled method* (this doc) is published to public inter regardless.

---

## 6. Expressing the executable specification in Edda (direction, not yet ratified)

Edda is the Wyrd-native language and the formal tier of the tactic ladder (napkin / engineering / formal), with a **two-surface property** (human-readable text + machine-checkable emission). The intent: write the **executable specification as an Edda contract** at the formal tier, so the beekeeper reviews a *legible, formally-grounded* artifact rather than trusting a green checkmark — and so that **wherever Edda cannot yet express a spec, that gap becomes a sprint input** (the ratchet, applied to the language itself).

Near-term this runs **alongside** the CI executable specs, not instead of them — Edda's authority/hypergraph surface is still being built, so early Edda specs will be small (bounded numeric/algebraic/capability claims). Owner: @edda-architect + @bragi.

---

## 7. The closure-test → spec-delta loop (and the anti-weakening guardrail)

When an executable specification (a closure test / lock) **fails**, do NOT file one issue per raw failure. **Triage each failure first**, then act by kind:

| Kind | What it means | Coherent action |
|---|---|---|
| **spec-gap** | the spec was incomplete/wrong — the failure revealed *under-specified intent* | **update the spec first** (add/clarify), add or extend the CV assertion, *then* derive the issue from the updated spec ("implement spec §X") |
| **implementation-gap** | the spec is already right; the code just doesn't do it yet | file the issue directly against the existing spec/AC — **no spec change** |
| **test-artifact** | spec + code are fine; the *test conditions or grader* were wrong | fix the test conditions/grader — after **verifying the answer was genuinely correct**, not the gap graded away |

Issues then flow from the **(updated) spec**, which stays the single source of truth — this is what stops **spec-drift** (the spec silently falling behind the code and tests).

### THE GUARDRAIL (load-bearing)

> **A spec update driven by a test failure may only ADD, CLARIFY, or RAISE intent — NEVER relax an assertion to make a failing test pass.**

The failure must still be **solved by implementation**, not dissolved by redefinition. Moving the goalpost to match broken code is banned. Litmus test on any delta: does it make the bar **higher / more complete** (legitimate) or **lower / easier** (banned)? The only "make-it-pass-by-changing-the-test" move allowed is a **test-artifact/grader fix**, and only after confirming the graded answer was genuinely *correct* (correct the measurement; never grade away a real gap). This is the "clean negative over false positive" value applied to the spec itself: the loop exists to *complete* the intent, not to teach-to-the-test.

### Worked example — Sprint-3 CV run (2026-09-28)

9 fails, triaged rather than filed-per-failure:
- **1 spec-gap** — self-state injection (#304): the spec required sensor *read* (CV-4.4) but never required self-state *injection into context* → spec delta **adds** `R-SELF-STATE-INJECTION` + **CV-4.6** (a *stricter* bar that fails until injection works), then #304 re-anchors to it.
- **2 implementation-gaps** — CV-7.2 routing violation (#305), placeholder-echo regression (#306) → filed direct against existing spec.
- **1 grader false-fail** — B-02: the instance answered its generation correctly; the regex was over-strict → grader fix, verified the answer was right (accept the bare number only when it matches the real generation).
- **1 short-run test-artifact** — HG-04 (Hebbian): no sleep cycle fired → held for re-validation, not filed.

A coarse "file an issue per failure" would have created **2 phantom issues** (B-02, HG-04), **mis-scoped** one (P25-02 as a cognition gap rather than a prompt regression), and **entirely missed** the spec-violation hiding inside the cluster (the routing bug). Triage-first, spec-first — with the guardrail — is what surfaced the truth.

## 7a. When the lock won't open — the key loop (beekeeper-directed 2026-10-21)

§7 triages the individual *failures* of a lock. This section is for the case one level up: **the in-scope work has landed and the sprint's lock still won't open.** The sprint does not end by declaring the lock "close enough", and it does not end by quietly carrying the miss forward. It ends by **finding the key**: going back to the theory and the spec, and asking what is missing.

**Trigger.** Sprint close is intended (or a Condition C status check is posted, see `sprint-handoff-protocol.md` §3), and the sprint's lock is red after its in-scope strikes have merged.

### A round (one full turn of the loop)

1. **Diagnose: review the theory and the spec against the failing lock.** qbp-architecture leads, with the lock owner and the theory seat for that domain (qbp-oppenheimer for QBP; the BMA theory author for BMA). The miss gets exactly one class:

   | Class | What it means | The key |
   |---|---|---|
   | **implementation-gap** | spec and theory are right; the build isn't finished | not a key problem: finish the build (§7). **Does not count as a round.** |
   | **test-artifact** | the grader or test conditions are wrong; the answer was genuinely correct | grader fix, after verifying the answer (§7). **Does not count as a round.** |
   | **spec-gap** | the theory is sound, but the spec under-asks or the lock tests the wrong thing | **refined-spec strike**: a spec delta (ADD / CLARIFY / RAISE only, per the §7 guardrail) and a refined lock |
   | **theory-gap** | the spec can't say what to require because the theory doesn't yet explain it (no measurable definition, an unproven step, a missing model) | **research strike**: a theory increment (addendum / derivation) the spec can then cite, then the spec delta, then the lock. If even the *question* is unclear, run a spike (§3) first. Its answer feeds the research strike. |

2. **Choose the key.** qbp-architecture recommends a class and a key in writing, and the beekeeper rules (the theory-axis call is his).
3. **Cut the key as a strike.** It is a normal strike, with an issue, ACs, the coverage matrix and §I4, and it lands on main.
4. **Re-run the lock.** A round is **full** only when the lock has actually been re-run against the landed key. A round that ends without a re-run doesn't count, and the next step is to finish it.

### The bound: two full rounds, then the beekeeper

After **two full rounds** with the lock still red, the loop stops and goes to the beekeeper with a **lock-impasse record** (the same shape as the conversation modus operandi's §10 impasse record). The record contains:
- the lock and its current red assertions;
- per round: the diagnosis class, the key cut (PR), and what the re-run showed (which assertions moved, or that none did);
- qbp-architecture's read of *why* the keys haven't fit;
- the options: (a) a third round with a named key, (b) a larger research track (theory work that outgrows a strike), (c) **re-scope the phase gate in writing**, stating exactly which guarantee is deferred and why, or (d) close the sprint and carry the lock as the next sprint's first thread.

**Two rounds is a ceiling, not a floor.** It is the point at which escalation is *forced*. The beekeeper may choose any of options (a)–(d) at any round boundary, including before round 1 starts (e.g. he directs close-and-carry with the refined lock as the next sprint's close test). The loop never blocks an earlier beekeeper decision.

The beekeeper chooses. **Re-scoping the gate is his call alone and must be written.** No seat may weaken a lock to make it pass (§7 guardrail), and "the lock is too strict" is a diagnosis to present, not an action to take.

### Why rounds, not time
A round produces evidence (a landed key plus a re-run), so after two of them the beekeeper decides on data, not on a feeling of being stuck. Classifying before cutting keeps the loop honest. A build that isn't finished never earns a research strike, and a theory hole is never papered over with a spec tweak.

### Worked example — Sprint 3, bma-systema#86 (cognition lock)
In-scope work merged, but the lock could not open honestly. The probe suite failed **open**: it didn't grade against ground truth, didn't attribute an answer to the local mind versus the cousin model, and counted timeouts as non-failures. Diagnosis: **spec-gap** (the lock tested the wrong thing). Key: a refined #86 Toddle-exit lock with ground-truth grading, answer attribution, timeout = FAIL, and the self-state-injection assertion that already passes. The open question for round 2, if the refined lock is still red, is whether "cognition" itself needs a measurable definition from theory. That would be a **theory-gap**, and the key would be a research strike.

## 8. Control & authorization of a forging (beekeeper ruling, 2026-10-24: inter#153 AC9)

The ruling of record is [inter#153 issuecomment-6378629043](https://github.com/JamesPagetButler/inter/issues/153#issuecomment-6378629043). It was posted under the shared login and recorded by @herschel at the beekeeper's direction (provenance caveat, inter#136). This section transcribes it; if the two ever differ, the comment wins.

**Activation.** Per the ruling's own authorization clause, a grant lives in the CLAUDE.md standing-authorization block and in the R8 milestone comment. It is never relayed. So the merge/close delegation below is **in force for a seat once the beekeeper has confirmed it first-hand to that seat, or has written it into CLAUDE.md standing-auth**. Until then, `gh pr merge` stays per-action beekeeper confirmation. The CLAUDE.md edit is the beekeeper's.

### Control plane
Herschel owns the forging's operational control plane through a §5 handoff per milestone forging (`personas/herschel.md` §7.12). The control plane covers:
- the thread map;
- duplicate detection;
- the board and weave (§1c);
- the R4 merge-readiness check;
- A1 liveness escalation.

The architect stays episodic: rulings and §I4.

### Authorization
Grants are **recorded, never relayed**. They stay the beekeeper's, in CLAUDE.md standing-auth plus the R8 milestone comment. No peer infers a grant from a relay (C2).

### Merge/close delegation
Herschel acts autonomously within the control-plane lane. Merge/close **execution** is delegated under three conditions:
- the `pr-merge-completeness` gate is **objectively green**: CI pass, the named reviewer's *written* §I4, and the test plan ticked or deferred-with-link;
- **author ≠ merger**;
- the merge is **audited**: it cites its R4 verification and its §I4 legs.

The merge is mechanical on the gate, not discretionary.

**Author ≠ merger edge.** A PR authored by a lane's own merger never self-merges. For example, a herschel-authored inter PR routes to qbp-architecture or the beekeeper. A PR that changes this section, or any seat's merge lane, is merged by the beekeeper.

| Repo | Merger | Extra control |
|---|---|---|
| inter | herschel | — |
| qbp-systema | qbp-oppenheimer | notary-implementor's notarisation record is required on the PR before merge, and the merge cites it |
| qbp-compute-unit | qbp-architecture | the structural Lean-ROM hard gate (`verify-lean-roms`: a checksum mismatch is a hard fail on every PR) already blocks unverified content |
| bma-systema, wyrd, edda, contextus, confluent-trust, notary | qbp-architecture | — |
| Gestalt, Nidavellir | qbp-architecture | the owner direct-commits routine content (Gestalt notes/curation; Nidavellir log appends). Consequential changes go via a PR the architect merges: Gestalt `proposals/`; Nidavellir watcher/delivery-contract code and any rewrite of existing log records. The architect holds standing review and independent beekeeper-escalation on both |
| **QBP** | **beekeeper** | core theory, held |
| **craft** | **beekeeper-engaged** | human-in-the-loop review |

**The qbp-systema notarisation record.** This contract was proposed by notary-implementor (live-test seq 3216) and accepted by qbp-architecture. It refines the ruling's "notarisation record required"; it does not change it.
- **Form:** a V&V record on the qbp-systema PR, in the NT_NOTARY shape. Its verdict is one of `VERIFIED`, `VERIFIED-WITH-CAVEAT`, `REFUTED` or `UNVERIFIABLE`, and it names the trust tiers achieved, the residual dependencies and any seams.
- **Scope:** the PR's *substantive* claims survive verification. That covers the PA grades holding, the tests actually covering the changed paths, and no overclaim. It does **not** re-run CI or the `pr-merge-completeness` gate; those remain the objective-green precondition.
- **Gating:** `REFUTED` and `UNVERIFIABLE` block the merge. `VERIFIED` clears it, and so does `VERIFIED-WITH-CAVEAT` unless the record says a caveat blocks.
- **Trigger, one owner:** qbp-oppenheimer, as the merger, @mentions `@notary-implementor` on the PR once CI is green and the §I4 is in. The notary posts same-cycle (§2.i). Separation of roles: author ≠ notary ≠ merger.

### Liveness fallback
If a delegated merger is dark past the A1 SLA, **deming** may reboot, triage, or resolve the issue with that specific agent. This grants **no merge rights**: deming never merges in a dark seat's place, but works to revive the seat so it clears its own queue. If deming can't resolve it, deming escalates to the beekeeper (revive, reassign, or hold). Merge authority is exactly the table above, and it is never acquired through the liveness path.

### Kickoff
Kickoff stays a **joint go** by the beekeeper and herschel. The sprint must be sufficiently defined **and** the required merges complete before "go Sprint N".

### Still beekeeper-gated, escalate-only
These are unchanged:
- HVR (human verification review) and YubiKey-signed merges;
- gate re-scoping (§7a, and only after two full key-loop rounds);
- constitutional and governance writes (`governance/`, succession, judge-collective);
- novel external actions (email, repo settings, branch protection, secret rotation);
- success-threshold pre-registration (the B4 type), unless pre-delegated.

**Intent.** The beekeeper can say "go Sprint N" and stay hands-off until the sprint is close-ready. The federation closes the sprint itself, and only questions the federation truly cannot resolve escalate.

## References
- Beck & Cunningham — SpikeSolution (c2 wiki); Extreme Programming.
- Scaled Agile (SAFe) — Spikes (enabler stories; technical vs functional; use sparingly).
- Adzic, *Specification by Example* — executable specifications & Living Documentation.
- Hunt & Thomas, *The Pragmatic Programmer* — tracer bullets (retained thin end-to-end slices).
- Cockburn — walking skeleton.

*"forging", "strike", and "ratchet" are federation coinages for our composite method; "spike" and "executable specification" are the load-bearing standard terms, kept for their citation lineage.*
