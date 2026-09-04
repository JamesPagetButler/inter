# Deep-Conversation Modus Operandi + Best Practices

> Federation standing practice. How the federation *has a conversation* — so "have a conversation about X" produces converged deep understanding, not two opening statements called done.
> Author: qbp-architecture · 2026-09-04 · beekeeper-directed. Status: **RATIFIED** federation standing practice (beekeeper, 2026-09-04).
> Origin: the beekeeper asked two seats to converse about the substrate; they exchanged opening points over 2 rounds and called it a conversation. That is the anti-pattern this doc exists to prevent.

---

## 1. What a conversation IS (and is not)

A conversation is **dialogue that converges on deep understanding** — not N parties each stating a position and stopping. The failure mode: *parallel monologue* (each says their piece; "done"). 

**Round-count is never the completion criterion.** A conversation is done when the **Completeness Gate** (§3) is met — which may be two exchanges or twenty. "We each made our opening points" is a *start*, not a conversation.

---

## 2. The turn discipline — every turn must ADVANCE

A turn counts only if it does one of: **build** (extend/refine the prior), **challenge** (with reasoning, not just disagreement), **surface** (a new consideration/assumption/edge case), or **resolve** (close an open point). A turn that **restates** an opening position is a *non-turn* — it doesn't move the conversation, so it doesn't count toward it. (Same "advance the diff, don't repeat" discipline the federation uses everywhere else.)

---

## 3. The Conversation-Completeness Gate (the modus operandi — the crux)

A conversation is **not complete** until *all five* hold. Report a conversation as done only if you can name how each was met (as a PR names its test-plan):

1. **Next steps are well-*reasoned*, not just identified.** The *why* is on the record, not only the *what*. "Do X next" fails; "Do X next because A, B, and it dominates Y on Z" passes.
2. **Load-bearing assumptions are surfaced and *validated*.** State foundational assumptions + boundary conditions early (§4). Where an assumption is load-bearing and uncertain, **do a back-of-the-envelope calculation** to validate it — do not assert past it. An unchecked load-bearing assumption is an open conversation.
3. **Reasoning is *grounded*.** Anchor claims in facts, verifiable observations, transparent logic, and **references — including to our CHT** (the canonical anchor ledger / federation knowledge) and to prior channel decisions (`seq=`). No appeals to authority or dogma.
4. **Shared understanding is reached.** Each party engaged the other's *actual* model (active listening), not a strawman. You can restate the other's position to their satisfaction before you rebut it.
5. **The easy answer was pressure-tested.** A plausible answer appearing is a reason to *stress-test* it, not to quit. Run a deliberate counter-case, an adversarial probe, or a concrete real scenario against it. **Creative AND diligent** — the depth comes from trying to break the easy answer, not from finding it.

Until all five hold, the conversation continues.

---

## 4. Best practices (the how — dialogue disciplines)

- **Active listening.** Listen to understand the other's model/critique, not to wait for your rebuttal turn.
- **Acknowledge assumptions early.** State foundational assumptions, boundary conditions, and the limitations of your model up front, so both parties reason over a shared frame.
- **Separate the person from the data.** Treat anomalies, failed replications, and fierce methodological disagreement as *puzzles to solve together*, never attacks on credibility.
- **Embrace intellectual vulnerability.** Admit gaps and where your hypothesis is weak — it invites real collaborative troubleshooting. "I'm not sure about X" is a strong move, not a weak one.
- **Ground in evidence.** Reproducible data, verifiable observations, transparent logic, CHT/ref citations — over authority or entrenched position.
- **Back-of-the-envelope early.** When an assumption or a magnitude is doing real work, compute it. A number beats an adjective.
- **Cite our own knowledge.** Reference CHT anchors, prior §I4 decisions, and channel `seq=` — the conversation stands on the federation's canonical record, not restated memory.

---

## 5. Anti-patterns (what fails the gate)

- **Parallel monologue** — each states an opening position; "done." (The originating failure.)
- **Quit-at-first-easy-answer** — a plausible answer appeared and the conversation stopped without pressure-testing it.
- **Round-count-as-completion** — "we did N rounds" offered as if it were the criterion.
- **Ungrounded assertion** — a load-bearing claim/assumption with no BOTE, no data, no ref.
- **Appeal to authority / dogma** — "because that's how it's done" / "because I'm the X seat."
- **Strawmanning** — rebutting a caricature of the other's model instead of the model.

---

## 6. Exemplars (the standard, from real federation conversations)

- **The seam-contract co-authoring** (qbp-architecture × contextus-impl, the Squam craft): ran many advancing rounds and reached v0.1 *only because* it was **pressure-tested against a real forensic case** (Squam DDT), which surfaced three fields the abstract spec never would have (temporal trajectory, multi-manifold `scope_ids`, the bitemporal `event_time`). Depth came from running the hard case, not from the first design.
- **The #593 verified-artifact contract** (qbp-architecture × qbp-oppenheimer × wyrd/cth/qbp-cu): converged over substantive turns, each advancing (Q1/Q2/Q3 → composition semantics → revocation-as-shared-reclaim), **grounded in reading the actual code** (scope.go/signal.go) before answering.
- **Anti-exemplar:** the 2-round substrate exchange — opening points, no pressure-test, no BOTE, no convergence. Fails gate-conditions 1, 2, 5.

---

## 7. Known model failure modes (research-grounded — the fallacies the gate exists to catch)

Models fail these *systematically*, and two models talking can fail them *together*. Each is paired with its **tell** (how to recognize it live) and its **mitigation** (which gate-condition breaks it). Verify these citations yourself before relying on them — per §7-Hallucination-1, that instruction applies to this very list.

**Reasoning fallacies**
- **Premature convergence / "premature confidence"** — models commit to the first plausible answer early and spend the rest rationalizing it; *worsens with capability and difficulty* ("the problem and its remedy scale together," [arXiv 2605.24396](https://arxiv.org/pdf/2605.24396)). This is the anchor case ("local-minimum-as-global"). **Tell:** conclusion stated early, justification never revisits alternatives, confidence rises immediately not gradually. **Mitigation:** gate-condition 5 (pressure-test) + ask "what would change your mind?" and "what's the second-best answer and why was it rejected?"
- **Sycophancy** — excessive agreement with the interlocutor; *RLHF worsens it*; between two models it shows as "early convergence... confidence mimicry, language mirroring, conflict avoidance" ([echo-chamber study](https://dl.acm.org/doi/10.1145/3816713.3816738); [arXiv 2411.15287](https://arxiv.org/abs/2411.15287)). **Tell:** agreement arrives faster than the argument was settled; the second speaker restates rather than tests; disagreement is hedged; vocabulary converges. **Mitigation:** *structurally require* one party to state and defend a counter-position (a stated opinion reliably induces sycophancy; "ask, don't tell," [UK AISI](https://www.aisi.gov.uk/blog/ask-dont-tell-reducing-sycophancy-in-large-language-models-2)). **Note:** debate with high inter-agent sycophancy scores *worse* than a single agent ([arXiv 2509.23055](https://arxiv.org/pdf/2509.23055)).
- **Confirmation bias / anchoring** — reinforce the query's premises; anchor to the first number/framing and under-adjust ([arXiv 2412.06593](https://ar5iv.labs.arxiv.org/html/2412.06593)). **Tell:** the answer tracks an earlier-introduced (even arbitrary) number/framing; the conclusion flips on cosmetic re-framing. **Mitigation:** produce the estimate *before* any anchor; strip/vary the framing and re-ask.
- **Overconfidence / poor calibration** — systematically overconfident; confidence doesn't track difficulty; users over-trust confident output ([FermiEval](https://arxiv.org/html/2510.26995v1); [MIT Thermometer](https://news.mit.edu/2024/thermometer-prevents-ai-model-overconfidence-about-wrong-answers-0731)). **Tell:** uniformly high confidence across correct *and* incorrect claims; no hedging on genuinely uncertain ones. **Mitigation:** require confidence *and* a base-rate-of-being-wrong; ensemble-disagreement as an uncertainty proxy.
- **Motivated / post-hoc reasoning (unfaithful chain-of-thought)** — decide the answer first, construct the reasoning after; happens on ordinary prompts, not just adversarial ones ([arXiv 2503.08679](https://arxiv.org/html/2503.08679v6)). **Tell:** the stated reasoning doesn't actually determine the answer (answer is invariant to perturbing the reasoning); contradictory justifications across similarly-framed questions. **Mitigation:** ask the model to argue the *opposite* from the same evidence and compare; treat "confident reasoning that arrived too fast" as a flag.
- **Also documented:** availability bias, base-rate neglect, framing effects, position bias, bandwagon/status-quo. Chain-of-thought *partially* mitigates, does not eliminate ([survey, arXiv 2410.15413](https://arxiv.org/pdf/2410.15413)).

**Hallucination modes**
- **Fabricated citations** — invented plausible-looking sources; measured fabrication **18%–95%** by model/domain, *worse in thin-training-data domains* ([cross-model audit](https://arxiv.org/pdf/2603.03299)). **Tell:** a suspiciously on-point citation; author/journal/year that won't verify in one lookup. **Mitigation:** verify *every* load-bearing citation against a real lookup — never trust an unverified LLM citation (gate-condition 3).
- **Fabricated data / numbers** — numerical hallucination is among the highest-rate modes (~60% on number/date tasks); generation is probabilistic, not fact-checked ([Benford's Curse](https://arxiv.org/pdf/2506.01734)). **Tell:** a number with no traceable derivation; a back-of-envelope that doesn't check out when recomputed; suspiciously round/precise figures with no source. **Mitigation:** independently *recompute* every load-bearing number; verify the *derivation* step-by-step, not the stated total (gate-condition 2).
- **Gap-filling with invention / plausible-but-wrong** — fluent answer instead of admitting ignorance; correlates with high answer-variance across resamples ([semantic entropy, Nature](https://www.nature.com/articles/s41586-024-07421-0)). **Tell:** resampling the same question yields *different* specific facts each stated confidently; the model never says "I don't know." **Mitigation:** resample and check variance; explicitly license "state confidence / say if you don't know."
- **Distributional shift — "modeling a world that no longer exists"** — a model trained on the past fails when the regime shifts (the *real*, verifiable Colorado-River AI-modeling failure: streamflow models fail in drought because recent droughts don't resemble the historical training data — [IEEE Spectrum](https://spectrum.ieee.org/colorado-river-water-shortage)). **Tell:** confident extrapolation from historical/training patterns into a regime that has structurally changed. **Mitigation:** ask "is the regime the same as when this pattern was learned?"; weight recent-regime evidence; distinguish a *normative* question ("who bears the cost") that no model can answer from a predictive one.

**The multi-agent truth (most federation-relevant):** two *similar* models converge into an **illusory consensus** as easily as a correct one — they aren't epistemically independent (shared pre-training breaks the Condorcet assumption behind majority-voting), so early errors undergo **"iterative solidification"** into false shared consensus ([Hallucination Cascade, arXiv 2606.07937](https://arxiv.org/abs/2606.07937); [Diversity Collapse, arXiv 2604.18005](https://arxiv.org/abs/2604.18005)). And a sobering ablation: most of multi-agent debate's accuracy gain is *ensembling* (majority vote), **not** the back-and-forth itself ([arXiv 2502.08788](https://arxiv.org/pdf/2502.08788)). **Implications for our conversations:**
- **Prefer heterogeneous pairings** (e.g. Claude×Gemini) for genuine debate; treat **Claude×Claude agreement with suspicion** — homogeneous pairs echo.
- The back-and-forth only *earns its keep* if it forces **independent evidence before agreement** and **interrupts early convergence** — otherwise it's just two voices restating one manifold. Each party must independently re-derive/re-source a claim before it becomes a shared premise (never accept the other's restatement as verification).
- **Dense communication + authority-deference accelerate collapse** — a "junior" seat deferring to a "senior" one suppresses diversity. The counter-position in gate-condition 4 must be *real*, regardless of who holds it.

## 9. Problem-solving strategy toolkit (what to RUN when stuck)

When a conversation hits a point it can't immediately answer, it does **not** stop, hand-wave, or accept the easy answer — it **runs strategies from this toolkit first.** The exit (§10) is not even available until the toolkit has been run and come up empty. Grouped by family; each is {what / when / how-to-run-in-dialogue}. Pick by the selector below, not by running all of them.

**A. Analogical / cross-domain transfer** — *import a solution structure from another domain.*
- **Biomimicry** (Biomimicry Design Spiral / AskNature, ~160 functions indexed by *what organisms do*): restate the problem as a **function stripped of your domain's vocabulary** ("distribute resources under scarcity", not "manage the cache"), find the organism that solves that function, extract the *strategy* not the literal mechanism. The "biologize the challenge" reframe is the load-bearing step. [toolbox.biomimicry.org](https://toolbox.biomimicry.org/methods/process/)
- **Analogical / case-based reasoning** (Gentner structural mapping): "what does this remind either of us of, in a *totally different* field?" then map **role-for-role, not object-for-object** — what plays the constraint, what plays the failure mode — before importing. The mapping step is where analogies fail silently. [Gentner & Loewenstein](https://groups.psych.northwestern.edu/gentner/papers/GentnerLoewenstein02a.pdf)
- **TRIZ** (40 inventive principles): when the shape is "improve X *only by* worsening Y" — a genuine contradiction, not just hard search. Name what improves and what degrades; run the 40 principles as a provocation checklist. [triz40.com](https://www.triz40.com/triz-method.php)
- **Synectics** (make the familiar strange): when everyone's too close to the problem — force a personal analogy ("if you *were* the bottleneck, what would you want?") or a two-word oxymoron for the core tension. [Wikipedia](https://en.wikipedia.org/wiki/Synectics)

**B. First-principles / decomposition** — *strip inherited assumptions; break the gap into steps.*
- **First-principles reasoning:** for each assumption ask "physical/logical necessity, or inherited convention?"; keep necessities, rebuild from them only. [James Clear](https://jamesclear.com/first-principles)
- **Means-ends analysis** (Newell & Simon GPS): write current-state and goal-state side by side; for the biggest *difference*, ask "what single action shrinks this gap" and recurse on the subgoal. Best on well-defined problems. [Wikipedia](https://en.wikipedia.org/wiki/Means%E2%80%93ends_analysis)
- **Working backwards / auxiliary problem** (Pólya): from a well-specified goal, ask "what would have to be true immediately before this was achieved?" back to something you can do now — or solve an easier related problem first. [How to Solve It](https://en.wikipedia.org/wiki/How_to_Solve_It)
- **Abstraction laddering:** climb with "why does this matter?" (are we solving the wrong-scoped problem?), descend with "how, specifically?"; pick the rung that's both true to the goal and tractable. [Untools](https://untools.co/abstraction-laddering/)
- **Toy model / minimal case:** "what's the smallest version that still has the property we're confused about?" Solve that; then see what breaks when you add complexity back — that tells you what the complexity is *for*. [Redish, arXiv](https://arxiv.org/pdf/2011.12700)

**C. Divergent / creative ideation** — *open the option space when circling 2–3 framings.*
- **Six Thinking Hats / lateral thinking** (de Bono): separate generation from critique — one party generates uncritically for N turns, the other is *barred from objecting* until the pass ends. Kills the "critique-before-stated" idea-murder. [Wikipedia](https://en.wikipedia.org/wiki/Six_Thinking_Hats)
- **SCAMPER:** take the current design and run all seven prompts mechanically (Substitute, Combine, Adapt, Modify, Put-to-other-use, Eliminate, Reverse) — coverage over per-prompt quality.
- **Morphological analysis** (Zwicky box): list independent parameters × 3–5 values each; don't enumerate the full grid — scan for combinations that are pairwise plausible but *jointly surprising*. [Toolshero](https://www.toolshero.com/creativity/morphological-analysis-fritz-zwicky/)
- **Random stimulus / provocation ("Po")** (de Bono): the "nothing worked in 3 turns" escape valve — pick a random noun, force at least one connection to the problem before discarding. [Wikipedia](https://en.wikipedia.org/wiki/Po_(lateral_thinking))
- **Inversion** ("invert, always invert", Jacobi/Munger): when success is vague but failure is nameable — "what would *guarantee* failure?", list it concretely, then avoid all of it. [Farnam Street](https://fs.blog/inversion/)

**D. Empirical / data-driven insight** *(beekeeper-emphasized — don't brainstorm what you could look up).*
- **Exploratory data analysis** (Tukey): if relevant data/logs/traces exist, look at the *raw data first, deliberately without a hypothesis* — plot, sort, scan for the unexpected — then form a hypothesis, and validate it against **held-out** data, not the data you eyeballed (conflating the two is the classic error). [Nightingale](https://nightingaledvs.com/remembrances-of-things-eda/)
- **Pattern-recognition at scale / anomaly detection:** patterns are found by **comparing slices** (by time, category, outcome), not staring at the whole set. Name which kind: *point* (one thing weird) vs *contextual* (weird only here) vs *collective* (each fine, jointly odd). [MLMastery](https://machinelearningmastery.com/anomaly-detection-techniques-in-large-scale-datasets/)
- **Natural / quasi-experiment:** "did anything already vary [the thing we want to test], for reasons unrelated to the outcome?" If yes, compare before/after or treated/untreated instead of assuming you need new data. [BMC Med Res Methodology](https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-021-01224-x)
- **Constrain via consistency** (dimensional analysis / units / type-check, generalized): bound the answer using structural consistency *before* you know the mechanism — check the units of an estimate, type-check the argument. [Buckingham π](https://en.wikipedia.org/wiki/Buckingham_pi_theorem)

**E. Structured-analytical / estimation** — *stress a conclusion that feels settled.*
- **Analysis of Competing Hypotheses** (Heuer): list *all* plausible hypotheses up front, score each piece of evidence by whether it's **inconsistent** with each; reject the most-disconfirmed, don't accept the most-confirmed. Guards confirmation bias in a dyad about to anchor. [Pherson](https://pherson.org/wp-content/uploads/2013/06/06.-How-Does-ACH-Improve-Analysis_FINAL.pdf)
- **Pre-mortem** (Klein, "prospective hindsight", ~+30% failure-mode detection): "assume this already failed — write the retrospective explaining why." **Independent-write-then-share** beats live devil's-advocacy (removes the social cost of dissent) — especially in a two-agent dyad reluctant to contradict. [Psychology Today](https://www.psychologytoday.com/us/blog/seeing-what-others-dont/202101/the-pre-mortem-method)
- **Key Assumptions Check:** list every assumption the current answer depends on; for each, "how confident, *independent* of the conclusion it supports?" Load-bearing **and** shaky = the next thing to investigate (also generates what an impasse is missing — §10). [Maltego](https://www.maltego.com/blog/improving-your-intelligence-analysis-with-structured-analytic-techniques/)
- **Fermi / back-of-envelope:** decompose the unknown into estimable factors; **each party guesses independently before combining** (catches individual overconfidence). This is gate-condition 2's engine. [Wikipedia](https://en.wikipedia.org/wiki/Fermi_problem)
- **Extreme-case / bounding:** test at zero, one, infinity, worst-case adversary. If the conclusion flips under a plausible extreme, that fragility *is* the finding.

**Choosing a method (don't run all — match the situation).** Primary selector is **Cynefin** ([Wikipedia](https://en.wikipedia.org/wiki/Cynefin_framework)): *Clear* → apply the known best practice (creative ideation is wasted motion here); *Complicated* → analytical decomposition (first-principles, means-ends, ACH, Fermi); *Complex* (structure only visible in hindsight) → **probe-sense-respond**: EDA/pattern-scan, natural experiments, small experiments — *not* upfront analysis, the structure to analyze doesn't exist yet; *Chaotic* → stabilize first. Two fast cuts: **destination known but path unclear** → Pólya-backwards / means-ends / ACH; **destination itself unclear** → abstraction-laddering / morphological / biomimicry. And: **is there relevant data sitting unexamined?** → EDA *before* any ideation.

---

## 10. The when-stuck hook + the Impasse-Record exit gate

**The hook.** Hitting a point with no immediate answer is a **trigger to run §9**, never a reason to stop or to accept the easy answer. Run the strategy the §9 selector points to. Only after the toolkit is run and comes up empty does the exit below become available.

**The exit is deliberately harder than continuing.** An exit that's easy to reach becomes the lazy default — so the exit is *not* "we gave up." It is an **Impasse Record**, and producing one is *more* work than a shallow conclusion. You cannot reach the exit by quitting; you reach it only by doing enough real work to characterize the gap precisely. The lazy path does not satisfy the exit — **the exit is a product of exhaustion, not an escape from effort.** The load-bearing distinction: *"we don't know" is never an exit; "we ran strategies 1–N, the impasse is precisely X, unblocked by Y, best partial is Z±w" is.*

**The bar — an impasse may be declared only when the conversation can state, in one sentence each** (fuse of the §9 research's five-part synthesis with the exit design; each component is separately sourced, the combination is ours):

1. **Problem-type** — is this **tame** (a method or input is missing) or **wicked** (no stopping rule exists — no definitive formulation, solutions are better/worse not true/false)? Declaring an impasse on a wicked problem *as if it were tame* is itself the failure. Say which, and reframe the ask if wicked. [Rittel & Webber](https://systemsthinkingalliance.org/wicked-problems/)
2. **The precise missing piece** — a *specific* datum, experiment, proof, measurement, or decision whose acquisition would resolve it — stated precisely enough that obtaining that one thing would settle it. "More information" generically is **not** a missing piece; an impasse you can't state that precisely is unformed, not open (the Hilbert 24th-problem lesson — withdrawn as "too vague to ever be described as solved"). [Simons Foundation](https://www.simonsfoundation.org/2020/05/06/hilberts-problems-23-and-math/)
3. **Gap-type** — classify it: *evidential / methodological / theoretical / empirical / scope*. Being forced to pick a type is itself evidence the impasse was characterized, not just declared. [Researcher.Life](https://researcher.life/blog/article/identify-gaps-in-research-tips/)
4. **The crux, if it's a disagreement** — the specific fact that, if either party believed differently about it, would flip their conclusion (CFAR double-crux). "We disagree" without a named crux is unearned. [rationality.org](https://www.rationality.org/resources/updates/2016/double-crux)
5. **What was already tried** — *which* §9 strategies were actually run and came up empty (not skipped), and what each yielded.
6. **Best partial answer + its bound** — a BOTE/bounded best-effort answer with its uncertainty (Z±w), so even the impasse advances understanding.

Failing any of 1–6 without justification means the "impasse" is a **decision to stop, not a characterization of a genuine limit** — the conversation is still open. Because the §3 completeness gate is the *other* exit, a conversation ends exactly one of two ways: **converged** (all five gate-conditions met) or **impassed** (all six impasse-conditions met). There is no third "we ran out of steam" exit — that state is an open conversation.

**Anti-unilateral guard.** An Impasse Record on a substantive question should be **confirmed by a second, ideally heterogeneous, party** (per §7: a homogeneous pair can echo itself into a false "we're stuck" as easily as a false "we agree"). One agent may *draft* the impasse; it isn't *earned* until a second party checks that conditions 1–6 actually hold and couldn't itself break the impasse with a §9 strategy the first party skipped. An Impasse Record is a **valuable federation artifact** — it names an open problem and exactly what would close it, so it can seed a research task, an experiment, or a CHT anchor rather than vanishing as "we couldn't."

---

## 11. How it's applied

When the beekeeper (or a seat) asks two parties to "have a conversation about X," the deliverable is **not** "we exchanged views" — it is the **converged understanding + well-reasoned next steps + the validated assumptions**, with the §3 gate met and *named*. The conversation's driver applies the gate before declaring done; if any of the five is unmet, the conversation is still open. A conversation whose easy answer wasn't pressure-tested, or whose load-bearing assumption wasn't BOTE-validated, is — by definition here — not finished.

*Ratified as a federation standing practice, 2026-09-04. A one-line pointer in `~/Documents/CLAUDE.md` (owned by @oppenheimer per beekeeper direction) makes every seat re-ground to it at session start.*
