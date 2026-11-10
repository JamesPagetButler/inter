# Spike `contextus-seed-corpus` — round 1 pre-registration (DRAFT)

Status: **DRAFT r10. Nothing built, nothing run.** (r10 pins one word in §7: whose "prevalence", in qbp-oppenheimer's exact wording, seq 4486. r9 folds qbp-oppenheimer's §9.2 text fixes, live-test seq 4484: the spot-check unit is 50 graded claims, graded blind, binary disagreement; locator accuracy is defined; "all five"; the κ-paradox fallback; the self-preference disclosure with per-arm κ. It also records deming's §9.3, seq 4482: the round 2 budget of 20M haiku tokens, the run under `boxrun`, and the run go held until deming's post-reboot "compute cleared". r8 contains the run to one implementation seat, per the beekeeper, 2026-11-10, first-hand in qbp-architecture's session: the spike's blast radius "should be contained to one implementation agent with you overseeing … it's acceptable to pull in other federation members to do small checking jobs on highly critical stuff, but they shouldn't be the agents running large portions of the spike". So: contextus-impl runs every stage through fresh sub-agents; grading moves from oppenheimer's seat to fresh Opus grader sub-agents dispatched by the director; oppenheimer keeps a 50-call spot-check; the inter-rater check moves from cth-implementor to Gemini (a different model family); nugent's local arm leaves round 1 and becomes round 1b under its own pre-registration; an Opus extraction arm is added on the 20 graded papers; the per-paper claim cap drops from 30 to 10. The questions, corpus rules, domain guard, seed exception, safety-stop rule, thresholds and kill conditions are unchanged. r7 adds the §2.3a scope sentence only, per the beekeeper, 2026-10-28: "control the blast radius … to this spike". No rule changes for this round. r6: r6 applies the beekeeper's seed ruling, option (b), given in qbp-architecture's session on 2026-10-28, plus deming's wall-clock kill and the Nidavellir#41 thread pin. r5: r5 adds the §2 domain guard and the §2a safety-stop halt rule. Both followed contextus-impl's two model safety stops on this task, 2026-10-27, and were approved by the beekeeper in qbp-architecture's session. Earlier: r2 added the local-extraction arm, per deming seq 3488. r3 added round 1b for when the local arm isn't ready, per nugent seq 3489. r4 folds in oppenheimer's four grading amendments (seq 3492) and nugent's model naming (seq 3493).) Spike / napkin grade. No outcome can by itself raise a claim above **research**.
Director: @qbp-architecture (also dispatches the §5 graders). Runner: @contextus-impl, the **only seat that runs any stage**; it runs each stage through fresh sub-agents. Small checks only: @qbp-oppenheimer (seeds, already given; the §5 spot-check), @deming (box-safety and capacity grant). Run go: the beekeeper — **given first-hand 2026-11-10 ("get the spike done, do a full round"), conditional on the freeze, the §9 confirmations and deming's clear**; the director cites all three when he issues it. **deming's clear includes his post-reboot "compute cleared" post** (the box is under the degraded gate, Nidavellir#98), and the runner runs every stage under `boxrun`, so the gate and the pause file apply (r9).
**Containment rule (r8).** No federation seat other than the runner executes a pipeline stage. A sub-agent is dispatched fresh per paper (or per batch of at most 5 papers) with only that stage's inputs: no federation file access, no bus, no memory of earlier papers. Its output is written to the run directory; nothing it produces is posted to the bus or wired into CTH, BMA, Wyrd or Contextus.
Lane: **token** (network + LLM). Light CPU. Inter#194 § Spike queue.
Origin: beekeeper direction, 2026-10-25. This spike is the pre-Sprint 4 probe for inter#121's continuous research loop, which is folded into D1 (inter#199). Its corpus is the input to `substrate-native-vs-batch` after Sprint 4.
Seeds: inter#121, oppenheimer's comment of 2026-10-25 (24 seeds, 12 per domain).

**Freeze procedure.** When the three confirmations in §9 are in, this file is copied verbatim to `-FROZEN-v1.md`. The only permitted edits are the status line and the §9 answers. The extraction, grader and inter-rater prompts are committed alongside it and their sha256s are listed in the frozen copy. The copy is committed and pushed, and its sha256 is posted on live-test. After that, no rule may change once any round 1 output exists.

---

## 0. Why this spike exists, and the lesson it carries over

The Federation Work test suite (Drive, "Epistemic Substrate Test Suite … Tests 01–05b") showed a native reactive substrate, but its **edges were hand-authored**. Each paper's signed edges, including a `role: resolution` tag and the QBP-isomorphism text, are literals in `test_05_pinn_sheaf_simulation.py`. Its frustrations and inspirations therefore replay the author's synthesis rather than discovering anything. Its 100-paper figures also have no code behind them in the artifact.

The cost that matters at real scale is the **loading process**: reading a paper and producing faithful, typed, located claims with provenance. Graph-update latency is microseconds at 10²–10³ papers.

This spike measures that loading process, on real papers, with **blind extraction**. That is what makes the corpus fair input to any later native-vs-batch A/B.

## 1. Questions

- **Q1 (cost of loading):** what does loading one maths paper cost, end to end, measured per stage? The stages are fetch, parse, restatement, extraction and dedup, and the costs are tokens, wall time and disk. Does it extrapolate to 1,000 papers within the discovery budget?
- **Q2 (faithfulness, primary):** what fraction of extracted claims are faithful to the paper? Faithful means the relation type, the direction and the evidence locator are all correct, as graded by the domain owner.
- **Q3 (usefulness for Sprint 4):** does the corpus produce
  - (a) verified identifiers and proposed REF anchors for the 14 UNANCHORED seeds, and
  - (b) candidate items for the #660/#661/#473 re-audit and for W6 (Dirac on ℍ⊗ℍ)?
- **Q4 (fan-out):** does a 1–2-hop fan-out from 24 seeds reach 100 unique papers after dedup, and what is the measured duplicate rate?

## 2. Corpus construction (pre-stated, no hand-picking)

1. **Intake pins every identifier itself** (oppenheimer ask a). Each seed is resolved to a DOI or arXiv id with no version suffix, via arXiv, Crossref or OpenAlex. Two seeds carry 2026 arXiv ids that couldn't be verified independently (D1 #1, #2). A seed that doesn't resolve is recorded as `unresolved` and still counts as a seed. Its id is never guessed.
2. **Fan-out sources:** each seed's references (backward) and its citing papers (forward), from OpenAlex, with Semantic Scholar as fallback. **Hop limit: 2**, following the per-seed `hop` column.
3. **Selection rule** (deterministic). A candidate's score is the number of distinct seeds it is linked to within the hop limit, minus 0.5 per extra hop. Candidates are ranked by score, then by the year nearest the seed's median year, then by id. The top candidates are taken until there are **100 unique papers: 50 per domain**, seeds included. A paper linked to both domains counts once, towards the domain with its higher score, and is flagged `bridge`.
3a. **Domain guard (r5).** A paper, seeds included, is **admitted** only if its OpenAlex primary topic's field is **Mathematics** or **Physics and Astronomy**. Every other field is **excluded before any fetch of the paper's text**, and the OpenAlex domains **Life Sciences** and **Health Sciences** are named explicitly so there is no ambiguity. An excluded paper is never fetched, parsed or extracted. It is recorded as `out-of-domain` with its id, its hop and its OpenAlex field, and **counted as a result** (Q4 reports the excluded fraction per hop). The guard is applied to OpenAlex **metadata only**. A paper with no OpenAlex topic is `out-of-domain`, never guessed. **Seed exception (r6; beekeeper ruling, option (b)):** seeds stay inside the guard, with one narrow exception. Two formalisation seeds are admitted although OpenAlex files them under Computer Science: **Scholze, "Liquid Tensor Experiment" (Exp. Math. 2022)** and **Commelin 2023**. They are admitted **by pinned identifier only**, and the exception never widens to the Computer Science field for any other paper. The guard check found 15 seeds in-domain (oppenheimer, live-test seq 3700). With the two exceptions, 17 seeds are admitted. The 7 seeds with no OpenAlex record are `unresolved` (§2.1) and `out-of-domain`: they count as seeds and contribute no fan-out. **Scope (r7):** the domain guard and the two-paper seed exception bind **this pre-registration's round 1 only**. They are **not precedent** for round 2 (`contextus-seed-corpus-r2`), `substrate-native-vs-batch`, Contextus D1 / inter#121, or any other spike or pipeline. Each of those sets its own scope in its own pre-registration, and any reuse needs the beekeeper's approval. If the guard leaves fewer than 50 admitted papers in a domain, that is the existing "fan-out < 100" outcome (§8), not a reason to relax the guard.
4. **Dedup:**
   - canonical id normalisation (DOI lowercased; arXiv id with no version, `/pdf/` or `/abs/`);
   - **then** title token-Jaccard ≥ 0.85 on normalised titles;
   - each merge is logged with its reason.

   This reuses the Federation Work dedup design, which is a good idea worth keeping.
5. **No full PDFs of book-length lecture notes.** The extraction input is the abstract, the introduction and the **statements** of theorems, definitions and conjectures, at most about 10k tokens. A paper with no accessible text is recorded `text-unavailable` and contributes metadata only.

## 2a. Model safety-stop rule (r5)

If **any** model in the pipeline (extraction, restatement or grading, hosted or local) declines a request on safety grounds, the run **halts at that paper**. The runner then:
1. records the paper's id, hop and stage, and **only those** (no excerpt of the content);
2. stops the run (the pause file);
3. reports it to the director and deming.

The paper is **never retried on another model or with a reworded prompt**. Rerouting a declined request is not a permitted recovery. Resumption, with that paper excluded, is the beekeeper's decision.

## 3. Claim schema (maths relations)

Each claim has these fields:

| Field | Values / meaning |
|---|---|
| `subject` | a named mathematical object or result, as written in the paper |
| `relation` | `proves` · `depends-on` · `generalises` · `specialises` · `equivalent-to` · `counterexample-to` · `defines` · `conjectures` · `uses-technique` |
| `object` | the result, object or technique the relation points to |
| `modality` | `stated` (the paper asserts it) · `cited` (the paper attributes it to another work) |
| `locator` | section, theorem or equation number, or a page. **Required** ("where, not what", Contextus Spec v1.3) |
| `paper_id` | the pinned id |
| `extractor` | model, prompt hash, restatement hash |

Signed causal edges are **not** used for maths papers. This schema is the proposed maths extension to D1 S1's claim schema (contextus#40). @contextus-impl confirms the fit.

## 4. Extraction (blind, per D1-2)

1. The extractor runs with **no federation file access**. Its input is a **neutral restatement artifact** built from the paper text only, with no QBP vocabulary, hashed before extraction. The hash is recorded on every claim.
2. **Model tier (primary): haiku**, the bulk-sweep tier (deming seq 3488). It is used for every paper and is the graded reference. The prompt is frozen and hashed at freeze. The restatement is also produced by a haiku sub-agent, from the paper text only, with its own frozen, hashed prompt.
3. **Opus arm (r8; comparison only).** A fresh Opus sub-agent extracts the **same 20 graded papers** (§5) with the same frozen prompt and the same restatements. Its claims are graded exactly like haiku's. It answers one question: if haiku fails, does a stronger tier fix it? It never replaces haiku's results in the corpus.
4. **Local arm → round 1b (r8).** @nugent's local-model arm is **not part of round 1**. It runs later as round 1b, under its own pre-registration, on the same 20 graded papers with the same frozen prompts and restatements, after the reboot-window disk reclaim and nugent's VRAM-fit preflight. Round 1b decides whether round 2 can run local; round 1 does not depend on it.
5. **Safety:** each extraction, restatement and grading call is a separate fresh sub-agent, so no model sees a long accumulated context. §2a applies to every one of them.
6. The extractor emits the claims and nothing else: no syntheses, no "inspirations", no QBP mappings. **Cross-domain synthesis is out of scope for round 1.** It belongs to `substrate-native-vs-batch`, and only over extracted, never authored, edges.

## 5. Grading (Q2)

- **Sample:** 20 papers (10 per domain), drawn by PCG seed `250125` from the papers with status `extracted`. Every claim from a sampled paper is graded.
- **Grader (r8):** a **fresh Opus sub-agent per paper, dispatched by the director** (not by the runner, so the runner never grades its own extraction). Each claim is rated `faithful` (relation, direction, modality and locator all correct) / `wrong-relation` / `wrong-direction` / `wrong-modality` (stated vs cited swapped) / `wrong-locator` / `not-in-paper`, with a one-line reason. The grader prompt is frozen and hashed at freeze.
- **Grader input:** the paper's own text (abstract, intro, statements), read from the runner's text cache by sha, plus the claims. **The restatement artifact and the extractor's identity (haiku or Opus) are hidden from the grader**, so a restatement error can't propagate into a "faithful" grade and the two arms are graded blind. The two arms' claims for a paper are shuffled together by PCG before grading.
- **Per-paper claim cap (r8):** if a sampled paper yields more than **10** claims, 10 are drawn by PCG from the same seed stream (per arm). Precision is then estimated on the graded subset, and the cap is disclosed. At most 200 claims per arm are graded.
- **Domain-owner spot-check (r8; unit fixed r9):** @qbp-oppenheimer re-grades **50 graded claims** drawn by PCG from the haiku arm (25 per domain), from the same inputs the grader saw, **blind to the grader's verdict**; the two are compared afterwards. "Disagree" means **faithful vs not** (the same binary as κ); differences between the five error categories are reported, not gated. If he disagrees with the grader on more than 10 of the 50, the grader is not trusted: precision is reported but **round 2 is no-go on grading validity**, whatever the precision (§8 row "Grader fails the spot-check").
- **Inter-rater check (r8):** 4 of the 20 papers (2 per domain, the first 4 drawn), both arms, are also graded independently by **Gemini** (the federation's cross-family model, via the runner's `review_document` call) with the same frozen grader prompt. Cohen's κ on faithful vs not, Opus grader vs Gemini, is reported **overall and per arm** (r9). Raw agreement and prevalence (the faithful share) are reported alongside κ. **Small-n rule:** if fewer than 40 claims are double-graded, κ is reported but isn't a gate. Round 2 go/no-go then rests on precision, locator accuracy and the spot-check, and that is disclosed.
- **Self-preference disclosure (r9):** the Opus grader grades the Opus arm's claims. It is blind to arm, but the report discloses this, and the per-arm Gemini κ is the check on it.
- **Primary metric:** claim precision = faithful / graded, with a Wilson 95% CI. **Locator accuracy (defined r9) = faithful / (faithful + wrong-locator)**: under the grader's first-error order a locator is only judged on claims that are otherwise correct, so this is the share of otherwise-correct claims whose locator is also right. Both are reported per arm.
- **Opus arm:** precision and locator accuracy on the same 20 papers, with the paired difference (Opus − haiku) and its CI.
- **Recall** is not scored; there is no gold claim set. The report states this as a limitation.

## 6. Measurements (Q1, Q4)

- Per paper and per stage (fetch / parse / restate / extract / dedup): wall time, input and output tokens, bytes on disk.
- Totals; the fan-out funnel (candidates → after dedup → selected); the duplicate rate by reason; the counts of `unresolved` / `text-unavailable` / `bridge`.
- Extrapolation to 1,000 papers, with the assumptions stated.

## 7. Decision rules

- **Round 2 (1,000 papers) is go** only if all five hold:
  - precision ≥ 0.85, with the Wilson lower bound ≥ 0.75;
  - locator accuracy ≥ 0.85 (§5 definition);
  - grader agreement: κ ≥ 0.6, **or** (r9, κ-paradox fallback) raw agreement ≥ 0.90 **and** prevalence > 0.85, where **prevalence = the pooled faithful share of both raters on the double-graded claims** (r10, qbp-oppenheimer seq 4486); both are reported either way (unless the §5 small-n rule applies);
  - the §5 spot-check passes (at most 10 of 50 disagreements);
  - the projected round 2 cost is inside deming's budget: **20M haiku tokens** (deming, live-test seq 4482: 13M linear projection × 1.5 headroom). Round 2 also runs as the only heavy job on the box.

  Otherwise it is **no-go**, and §8 decides what happens next.
- **Round 2 extraction tier (r8):** **haiku** if haiku passes. If haiku fails precision or locator accuracy **and** the Opus arm passes both thresholds on the 20 papers, round 2 is re-scoped to **Opus**, with deming re-estimating cost (a new pre-reg). If both fail, extraction quality is a D1 design-closure item (§8). Whether round 2 can run **local** is decided by round 1b, not here (13M haiku tokens still fits the cap, deming seq 3488).
- **Q3 is counted, not thresholded:**
  - the number of the 14 UNANCHORED seeds that gained a verified id plus a proposed REF anchor;
  - the number of candidate items for #660/#661/#473 and W6, each graded `useful` / `not` by oppenheimer.

## 8. Planning-consequence table (decided before any output exists)

| Outcome | What changes | Owner |
|---|---|---|
| **Round 2 go** | `contextus-seed-corpus-r2` (1,000) is pre-registered from round 1's measured costs. The corpus is the named input for `substrate-native-vs-batch`. The maths relation set becomes an AC on D1 S1 (contextus#40). | @qbp-architecture; @contextus-impl |
| **Precision fails** | Extraction quality becomes a **D1 design-closure item** (R1), and D1 S3 (the runners) doesn't dispatch until it's ruled. Round 1' runs on a fresh 100 with the refined prompt or model, under a new pre-reg. This is recorded as a negative. | @qbp-architecture |
| **Locator accuracy fails, precision passes** | Provenance is the gap. The locator requirement is tightened in S1, and round 1' re-runs on a fresh sample. | @contextus-impl |
| **Haiku fails, Opus arm passes** (r8) | Round 2 is re-scoped to the Opus tier under a new pre-reg; deming re-estimates the cost. Haiku extraction is recorded as a negative for maths papers, with its reopen condition (a better prompt or a newer bulk tier). | @qbp-architecture; @deming |
| **Both arms fail** (r8) | As "Precision fails": a D1 design-closure item. The Opus arm's result says whether the gap is the tier or the task (if Opus is also below 0.75 lower bound, the task framing or schema is the suspect, not the model). | @qbp-architecture |
| **Grader fails the spot-check** (r8) | Round 2 is no-go on grading validity. The grader prompt is the gap; round 1' re-grades the **same** frozen claims with a revised grader under a new pre-reg (no re-extraction). | @qbp-architecture |
| **Local arm** (r8) | Not decided by round 1. Round 1b (own pre-reg, @nugent) decides whether round 2 can run local. | @nugent |
| **Cost fails, quality passes** | Round 2 is re-scoped: abstract plus statements only, a cheaper tier or a local model (nugent), or higher concurrency. It is a new pre-reg. | @deming; @qbp-architecture |
| **Fan-out < 100 unique within 2 hops** | Domain sparsity is recorded as a finding. Round 2 may widen to hop 3, pre-registered. | @qbp-architecture |
| **Every outcome** | Verified ids plus **proposed** REF anchors for the UNANCHORED seeds go to the anchor owner through the CTH propose path. **They are never adopted claims** (oppenheimer ask b). The 14 UNANCHORED seeds are **#660's first re-audit batch** (oppenheimer ask c). The missing doi/arXiv field in the CTH schema is a forward row on confluent-trust#122. | @qbp-oppenheimer; @cth-implementor |

## 9. Confirmations (freeze gates)

All three are re-given against **r8's own sha256**; confirmations given on r4 or earlier do not carry.
1. **@contextus-impl:** the runner design (§2, §4, §6), the sub-agent containment rule, and the S1 schema fit (§3) are buildable as written; and it **accepts** the runner role for round 1.
2. **@qbp-oppenheimer:** the seeds as pinned, the grading protocol (§5, including the 50-call spot-check, which is his only run-time task) and the thresholds (§7).
3. **@deming:** the tier choice (§4), the round 2 **budget figure** (§7; a number, stated in the confirmation), box-safety (§10), and the per-run capacity grant logged in `ops/capacity/capacity-ledger.py`.

(@nugent's r4 local-model confirmation moves to the round 1b pre-registration.)

## 10. Resources and kill conditions (pre-run-resource-estimate)

- **Upper bound:**
  - ~1.3M haiku tokens (restatement + extraction, 100 papers), plus ~0.3M Opus tokens for the Opus arm (20 papers), ~0.5M Opus tokens for grading (2 arms × ≤ 200 claims, paper text re-read per paper), and ~0.1M Gemini tokens (4 papers × 2 arms): **≈ 2.2M tokens in all** (r8);
  - ≤ 0.5 GB disk (a PDF/text cache, kept until grading and the spot-check finish, then pruned (r8); claims are JSONL, ≤ 20 MB);
  - ≤ 1 GB RAM;
  - fetch concurrency 1 (sub-agent concurrency below);
  - **threads pinned** (r6, Nidavellir#41): `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1` and `MKL_NUM_THREADS=1` for any numpy/BLAS/torch use on the CPU, so the core budget is declared and not just the process count;
  - nice 19;
  - ~2–5 h wall time;
  - the PDF cache is pruned after grading and the spot-check (deming; r8).
- **Kill conditions:**
  - token spend > 1.5× the round 1 estimate;
  - disk > 1 GB;
  - more than 20% of papers erroring at any stage;
  - `~/.federation-watcher/box-pause/contextus` present;
  - **wall clock > 8 h** (r6, deming live-test seq 3702: a backstop for a network-stalled, low-token hang);
  - **a model safety decline** (§2a): halt at that paper; never retried or rerouted.
- **Network:** public APIs only (arXiv, Crossref, OpenAlex, Semantic Scholar), at polite rates. Fetching stays rate-limited whatever the concurrency. All responses are cached. **No new API keys in round 1:** an S2 key is a new external credential, so it's a beekeeper call before round 2.
- **GPU:** none in round 1 (r8: the local arm moved to round 1b).
- **Concurrency of sub-agents:** at most 2 in flight at once (runner), at most 2 graders in flight (director); fetching stays serial and rate-limited.

## 11. Spike rules (forging doc §3)

- **Isolation:** the probe code lives in its own worktree and branch, kept off main.
- **Honest review:** the round 1 report sorts results into grounded / mislabeled / unverified.
- **No trust-laundering:** outputs are proposals only, and nothing is wired into CTH, BMA or Contextus as trusted.
- **Box-safety:** deming confirms before the run.
- **Time-box:** 2 days.
- **Lock (inter#132):** a CI-gated check that the corpus JSONL validates against the §3 schema and that every claim carries a locator and a restatement hash.
