# Forging — spikes, strikes & executable specifications

> The federation's de-risking & validation methodology.
> Authority: @qbp-architecture · Last updated: 2026-09-27 · Status: RATIFIED (beekeeper 2026-09-27)
> Partially addresses inter#132 (spike best-practices).

## Why this vocabulary

We had been calling a whole cluster of activity "a spike." A best-practices research deep-dive (2026-09-27) found the word was carrying **three distinct concepts**, two of which are the *opposite* of a canonical spike (which is disposable; ours produce permanent artifacts). Since we intend to express these artifacts in a formal DSL (Edda), muddled vocabulary would be compiled into the language. So we split the term — keeping **spike** in its true sense and giving our composite process its own honest name.

The metaphor is the **forge**: you heat the work, then shape it through repeated hammer **strikes**, each of which permanently changes the shape. That is exactly what we do — retained, incremental, validated shaping.

| Our term | What it is | Canonical anchor |
|---|---|---|
| **Forging** | the whole process — a chain of retained, risk-ordered increments | tracer-bullet development (Hunt & Thomas); walking skeleton (Cockburn) |
| **Strike** | one increment of forging (a spike → build → executable spec green) | a retained, test-gated delivery increment |
| **Spike** | the *probe* inside a strike (round-1, finds the gaps) | XP spike (Beck & Cunningham) — kept in its true sense |
| **Executable specification** | the oracle that certifies a strike landed (CI-gated, permanent) | Specification by Example → Living Documentation (Adzic) |

---

## 1. Forging — the process

**Forging** is how we build something durable and de-risked: a sequence of **strikes** (thin, end-to-end increments) that are **kept and grown**, each advancing only when its executable specification is green. (Anchor: tracer bullets — *"lean but complete… part of the skeleton of the final system… not thrown away… improved each iteration"*; infra-first, a walking skeleton.)

- Forging is **risk-ordered and reorderable**, not a waterfall — a gap found in one strike can reshuffle later strikes.
- The one-way property — the metal holds each new shape; a landed strike doesn't silently regress — is enforced by the executable specifications staying in CI. (Informally, the *ratchet*.)

---

## 2. Strike — one increment of forging

A **strike** is one increment: a **spike** surfaces the gaps → the increment is built → the strike **lands** only when its **executable specification is green**. A strike is retained (it permanently shapes the artifact). Forging is the chain of strikes.

> **Governing principle 2:** a strike is **not done when its build merges** — it is done when its **executable specification is green**. Per-piece unit tests on the individual fix-PRs are necessary but **not sufficient**; the executable spec is the *integrated re-confirmation* of the strike's findings, and it stays in CI as a regression guard.

**Two rounds within a strike:**
- **Round 1 = the spike (probe).** Finds the gaps. Disposable. (§3)
- **Round 2 = build + the executable specification.** One assertion per round-1 finding; confirm the gaps are closed; the spec stays in CI. (§4)

---

## 3. Spike — the probe inside a strike

A **spike** is a **time-boxed, exploratory investigation to reduce uncertainty**. Its product is *knowledge*, not shipped software. (XP; Beck & Cunningham — *"the simplest thing we can program that will convince us we are on the right track… drive a spike all the way through a log."*) We keep the word in its true XP sense.

**Properties (canonical — we hold to them):**
- **Time-boxed.** Half a day to a couple of days. Longer than a sprint means it's a project, not a spike.
- **Disposable.** Probe code is thrown away; only the *learning* is kept. Never ship probe code.
- **Has an explicit question.** No named question → not a spike. (*"Spikes are good when you are knowledge-limited, not time-limited"* — Beck.)
- **Done = question answered**, documented — not code that merged.

**Federation role (our one deliberate addition):** a spike's answer is a **capability-gap list** → *sprint-planning inputs*.

> **Governing principle 1:** every spike carries a required output — *"capability gaps surfaced → sprint candidates."*

**Types** (SAFe over the XP base): *technical* and *functional*. **Anti-patterns:** un-time-boxed spikes; spikes as a dumping ground; shipping probe code; spiking when time-limited rather than knowledge-limited. Use sparingly.

---

## 4. Executable specification — the oracle a strike lands against

An **executable specification** is a **CI-gated test-set with one assertion per finding** the spike raised, retained permanently and run as a **regression guard** (it fails if a later change reopens what the strike closed). (Adzic, *Specification by Example*: examples serve "as specifications for upcoming work, as acceptance tests once that work is done, and as regression tests… in the future" — the accumulated corpus is *Living Documentation*.)

This is the **opposite of a spike**: retained, production-grade, permanent. It is the acceptance test when the strike lands and the regression guard forever after.

**Where it lives:** in the **repo whose CI runs it** — never in a repo with no build. A cross-cutting strike may have executable specs in several repos; the record indexes them.

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

## References
- Beck & Cunningham — SpikeSolution (c2 wiki); Extreme Programming.
- Scaled Agile (SAFe) — Spikes (enabler stories; technical vs functional; use sparingly).
- Adzic, *Specification by Example* — executable specifications & Living Documentation.
- Hunt & Thomas, *The Pragmatic Programmer* — tracer bullets (retained thin end-to-end slices).
- Cockburn — walking skeleton.

*"forging", "strike", and "ratchet" are federation coinages for our composite method; "spike" and "executable specification" are the load-bearing standard terms, kept for their citation lineage.*
