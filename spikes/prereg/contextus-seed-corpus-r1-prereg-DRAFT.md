# Spike `contextus-seed-corpus` — round 1 pre-registration (DRAFT r1)

Status: **DRAFT r2. Nothing built, nothing run.** (r2 adds the local-extraction arm, per deming's live-test seq 3488.) Spike / napkin grade. No outcome can by itself raise a claim above **research**.
Director: @qbp-architecture. Runner: @contextus-impl. Local extraction tier: @nugent. Seeds and grading: @qbp-oppenheimer. Box-safety and capacity grant: @deming. Run go: the beekeeper.
Lane: **token** (network + LLM). Light CPU. Inter#194 § Spike queue.
Origin: beekeeper direction, 2026-10-25. This spike is the pre-Sprint 4 probe for inter#121's continuous research loop, which is folded into D1 (inter#199). Its corpus is the input to `substrate-native-vs-batch` after Sprint 4.
Seeds: inter#121, oppenheimer's comment of 2026-10-25 (24 seeds, 12 per domain).

**Freeze procedure.** When the three confirmations in §9 are in, this file is copied verbatim to `-FROZEN-v1.md`. The only permitted edits are the status line, the §9 answers and the model-tier slot in §4.2. The copy is committed and pushed, and its sha256 is posted on live-test. After that, no rule may change once any round 1 output exists.

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
4. **Dedup:**
   - canonical id normalisation (DOI lowercased; arXiv id with no version, `/pdf/` or `/abs/`);
   - **then** title token-Jaccard ≥ 0.85 on normalised titles;
   - each merge is logged with its reason.

   This reuses the Federation Work dedup design, which is a good idea worth keeping.
5. **No full PDFs of book-length lecture notes.** The extraction input is the abstract, the introduction and the **statements** of theorems, definitions and conjectures, at most about 10k tokens. A paper with no accessible text is recorded `text-unavailable` and contributes metadata only.

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
2. **Model tier (primary): haiku**, the bulk-sweep tier (deming seq 3488). It is used for every paper and is the graded reference. The prompt is frozen and hashed at freeze.
4. **Local arm (secondary; decides round 2's tier).** @nugent's local model (the qwen3-32b or coder-30b profile; named at freeze) extracts the **same 20 graded papers** (§5) with the same frozen prompt and restatement. It runs on the GPU, serialised against the GPU lane (`nugent-gemma12b`).
3. The extractor emits the claims and nothing else: no syntheses, no "inspirations", no QBP mappings. **Cross-domain synthesis is out of scope for round 1.** It belongs to `substrate-native-vs-batch`, and only over extracted, never authored, edges.

## 5. Grading (Q2)

- **Sample:** 20 papers (10 per domain), drawn by PCG seed `250125` from the papers with status `extracted`. Every claim from a sampled paper is graded.
- **Grader:** @qbp-oppenheimer. Each claim is rated `faithful` (relation, direction and locator all correct) / `wrong-relation` / `wrong-direction` / `wrong-locator` / `not-in-paper`.
- **Inter-rater check:** 4 of the 20 papers (2 per domain, the first 4 drawn) are also graded independently by @cth-implementor. Cohen's κ on faithful vs not is reported.
- **Primary metric:** claim precision = faithful / graded, with a Wilson 95% CI. Locator accuracy is reported separately.
- **Local arm:**
  - claim-level agreement with the haiku reference on the 20 papers (same subject/relation/object/locator after normalisation), reported with a CI;
  - oppenheimer also grades the local arm's claims on the 4 inter-rater papers, so agreement isn't mistaken for faithfulness.
- **Recall** is not scored; there is no gold claim set. The report states this as a limitation.

## 6. Measurements (Q1, Q4)

- Per paper and per stage (fetch / parse / restate / extract / dedup): wall time, input and output tokens, bytes on disk.
- Totals; the fan-out funnel (candidates → after dedup → selected); the duplicate rate by reason; the counts of `unresolved` / `text-unavailable` / `bridge`.
- Extrapolation to 1,000 papers, with the assumptions stated.

## 7. Decision rules

- **Round 2 (1,000 papers) is go** only if all four hold:
  - precision ≥ 0.85, with the Wilson lower bound ≥ 0.75;
  - locator accuracy ≥ 0.85;
  - κ ≥ 0.6;
  - the projected round 2 cost is inside the budget deming sets.

  Otherwise it is **no-go**, and §8 decides what happens next.
- **Round 2 extraction tier:** **local** iff local–haiku agreement ≥ 0.90 **and** the local arm's graded precision on the 4 papers is no more than 0.05 below haiku's on the same papers. Otherwise **haiku** (13M haiku tokens still fits the cap, deming seq 3488).
- **Q3 is counted, not thresholded:**
  - the number of the 14 UNANCHORED seeds that gained a verified id plus a proposed REF anchor;
  - the number of candidate items for #660/#661/#473 and W6, each graded `useful` / `not` by oppenheimer.

## 8. Planning-consequence table (decided before any output exists)

| Outcome | What changes | Owner |
|---|---|---|
| **Round 2 go** | `contextus-seed-corpus-r2` (1,000) is pre-registered from round 1's measured costs. The corpus is the named input for `substrate-native-vs-batch`. The maths relation set becomes an AC on D1 S1 (contextus#40). | @qbp-architecture; @contextus-impl |
| **Precision fails** | Extraction quality becomes a **D1 design-closure item** (R1), and D1 S3 (the runners) doesn't dispatch until it's ruled. Round 1' runs on a fresh 100 with the refined prompt or model, under a new pre-reg. This is recorded as a negative. | @qbp-architecture |
| **Locator accuracy fails, precision passes** | Provenance is the gap. The locator requirement is tightened in S1, and round 1' re-runs on a fresh sample. | @contextus-impl |
| **Local arm passes** | Round 2 runs local: electricity, not the token budget. The data also feeds nugent's harness-130 quality leg (local vs cloud extraction). | @nugent |
| **Local arm fails** | Round 2 runs on haiku. Local extraction is recorded as a negative for this domain, with its reopen conditions. | @nugent |
| **Cost fails, quality passes** | Round 2 is re-scoped: abstract plus statements only, a cheaper tier or a local model (nugent), or higher concurrency. It is a new pre-reg. | @deming; @qbp-architecture |
| **Fan-out < 100 unique within 2 hops** | Domain sparsity is recorded as a finding. Round 2 may widen to hop 3, pre-registered. | @qbp-architecture |
| **Every outcome** | Verified ids plus **proposed** REF anchors for the UNANCHORED seeds go to the anchor owner through the CTH propose path. **They are never adopted claims** (oppenheimer ask b). The 14 UNANCHORED seeds are **#660's first re-audit batch** (oppenheimer ask c). The missing doi/arXiv field in the CTH schema is a forward row on confluent-trust#122. | @qbp-oppenheimer; @cth-implementor |

## 9. Confirmations (freeze gates)

1. **@contextus-impl:** the runner design (§2, §4, §6) and the S1 schema fit (§3) are buildable as written.
2. **@qbp-oppenheimer:** the seeds as pinned, the grading protocol (§5) and the thresholds (§7).
3. **@deming:** the tier choice (§4.2, answered seq 3488), the budget (§7), box-safety (§10), and the per-run capacity grant logged in `ops/capacity/capacity-ledger.py`.
4. **@nugent:** the local model is named and fits the 16 GB VRAM profile; it is sequenced against `nugent-gemma12b`.

## 10. Resources and kill conditions (pre-run-resource-estimate)

- **Upper bound:**
  - ~1.3M tokens;
  - ≤ 0.5 GB disk (a PDF/text cache, pruned after extraction; claims are JSONL, ≤ 20 MB);
  - ≤ 1 GB RAM;
  - concurrency 1;
  - nice 19;
  - ~2–5 h wall time;
  - the PDF cache is pruned after extraction (deming).
- **Kill conditions:**
  - token spend > 1.5× the round 1 estimate;
  - disk > 1 GB;
  - more than 20% of papers erroring at any stage;
  - `~/.federation-watcher/box-pause/contextus` present.
- **Network:** public APIs only (arXiv, Crossref, OpenAlex, Semantic Scholar), at polite rates. Fetching stays rate-limited whatever the concurrency. All responses are cached. **No new API keys in round 1:** an S2 key is a new external credential, so it's a beekeeper call before round 2.
- **GPU:** the local arm needs ≤ 16 GB VRAM and is serialised against the GPU lane.

## 11. Spike rules (forging doc §3)

- **Isolation:** the probe code lives in its own worktree and branch, kept off main.
- **Honest review:** the round 1 report sorts results into grounded / mislabeled / unverified.
- **No trust-laundering:** outputs are proposals only, and nothing is wired into CTH, BMA or Contextus as trusted.
- **Box-safety:** deming confirms before the run.
- **Time-box:** 2 days.
- **Lock (inter#132):** a CI-gated check that the corpus JSONL validates against the §3 schema and that every claim carries a locator and a restatement hash.
