# contextus-seed-corpus, round 1: report

Spike: inter#224 (seed-corpus round 1). Director: qbp-architecture. Runner: contextus-spike. Domain owner and spot-check grader: qbp-oppenheimer. Box safety: deming.
Pre-registration: `spikes/prereg/contextus-seed-corpus-r1-prereg-FROZEN-v1.md`, sha256 `f31c62fcf8e4586f947a803123c4b17a122b3ef05146a73465c8e8387608fb17`. Amendments: A1 (accessible population), A2 (walk-down drift), A3 (grading harness and budget).
Results of record: `spikes/run1/s5_analysis_A2_results.json`, sha256 `02879c1dcc11506378f9c6908b9b53b6bba4b57e530b122ed6b3498c58c94621` (inter f8e73e5), produced by `s5_analysis_A2.py` (sha256 `1c1d4ef268e1eb8962cd98c6968ba9518e75054b1a44e1ce75493b8ee9871946`), one run.

Status: **DRAFT for review.** Cartan reviews it as a checking job. Q3 grading is oppenheimer's and is still pending.

---

## 1. Verdict

**Round 2 is NO-GO under §7.** Two gates fail independently.

| §7 gate | Haiku (primary) | Opus (comparison) | Bar | Result |
|---|---|---|---|---|
| Precision | 169/190 = 0.889, Wilson 95% [0.837, 0.927] | 186/197 = 0.944, Wilson 95% [0.903, 0.969] | ≥ 0.85, lower bound ≥ 0.75 | PASS |
| Locator accuracy | 0.988 | 0.984 | ≥ 0.85 | PASS |
| Grader agreement | κ 0.479 (40 claims) | κ 0.500 (40 claims) | κ ≥ 0.6, or raw ≥ 0.90 with prevalence > 0.85 | **FAIL** |
| Spot-check | 7 of 50 disagree | | ≤ 10 | PASS |
| Projected round 2 cost | ≈ 47.9M Haiku tokens | | ≤ 20M | **FAIL** |

**Grader agreement, overall:** κ = 0.494 on 80 double-graded claims, raw agreement 0.85, prevalence 0.825. The r9 fallback fails on both of its terms. All 80 Gemini lines parsed, so the §5 small-n rule does not apply.

**Cost:** deming ruled at spike-seed-corpus-s4 seq 270 that the gate is measured in the four-field count (§6).

**Arm difference (Opus − Haiku):** +0.055, paper-cluster bootstrap 95% [−0.020, +0.133] (B = 10,000, seed 250125). The two arms are not separated.

## 2. Open question for the beekeeper: the §8 gap

§7 sends a no-go to the §8 table. **No row in §8 covers this outcome.**
- "Grader fails the spot-check" is triggered by more than 10 of 50 disagreements. There were 7, so that row does not apply (qbp-oppenheimer, seq 265).
- "Cost fails, quality passes" requires quality to pass. Grader agreement, one of the quality gates, failed.

The director has seen the outcomes. So no consequence row is chosen or proposed here, and none should be by anyone who has seen them. What follows round 1 needs the beekeeper's own words or a new pre-registration. qbp-oppenheimer (seq 265) and deming (seq 266) agree with this reading.

Two descriptive facts, offered without a rule choice:
- **Spot-check direction** (qbp-oppenheimer, seq 265): in 5 of the 7 disagreements, oppenheimer graded `wrong-relation` where the lean grader said `faithful`. In the other two the grader was the stricter one: it said `wrong-relation` and `wrong-locator`, where oppenheimer said `faithful`. The differences lean toward the grader being more lenient on relation type.
- **Spot-check faithful shares** (qbp-oppenheimer, seq 272; description only, as these are not grades of record and no gate is read from them): on the same 50 Haiku claims, oppenheimer's faithful share is 40/50 = 0.80, Wilson 95% [0.670, 0.888], and the lean grader's is 43/50 = 0.86 [0.738, 0.930].
- **Cost structure** (deming, seq 270): cache_creation is 65% of Haiku spend, and there were 0 cache reads.

## 3. Q2: faithfulness by domain

| Domain | Arm | Faithful / graded | Precision | Wilson 95% | Locator accuracy |
|---|---|---|---|---|---|
| maths | Haiku | 84 / 90 | 0.933 | [0.862, 0.969] | 1.000 |
| maths | Opus | 92 / 97 | 0.948 | [0.885, 0.978] | 0.968 |
| physics | Haiku | 85 / 100 | 0.850 | [0.767, 0.907] | 0.977 |
| physics | Opus | 94 / 100 | 0.940 | [0.875, 0.972] | 1.000 |

**Error mix:**
- Haiku: wrong-relation 13, wrong-modality 4, wrong-locator 2, wrong-direction 1, not-in-paper 1.
- Opus: wrong-relation 3, not-in-paper 3, wrong-locator 3, wrong-modality 2.

Wrong-relation is the largest category in the Haiku arm. It is also the category where the spot-check found the grader most lenient (§2).

## 4. Q1: cost of loading, measured

Source: `s4_telemetry.jsonl`, 200 rows (100 papers × restatement and extraction), 0 non-zero exits.

| Stage | Papers | Tokens, all four fields | Mean per paper | Median | Max | Median wall time |
|---|---|---|---|---|---|---|
| Restatement (Haiku) | 100 | 3,257,778 | 32,578 | 33,759 | 63,687 | 38.5 s |
| Extraction (Haiku) | 100 | 1,536,839 | 15,368 | 15,445 | 26,167 | 18.4 s |
| **Haiku total** | 100 | **4,794,617** | **47,946** | | | |
| Opus arm extraction | 34 | 891,320 | | | | |
| Lean grading (Opus) | 20 | 972,086 | | | 63,690 | |

- **Count basis (deming ruling, seq 270):** the four-field sum, the same unit as `haiku_budget_gate.py`, the A1 grant, the 58k per-paper stop and the 65k grader stop.
- **Haiku breakdown:** input + output = 1,673,012. cache_creation = 3,121,605. cache_read = 0.
- **Linear projection to 1,000 papers:**
  - four-field: ≈ 47.9M, the gate basis (**FAIL** against 20M);
  - input + output only: ≈ 16.7M, reported for completeness, not the gate basis.
- **Against the pre-measurement estimate:** FROZEN-v1 §10 estimated ~1.3M Haiku for 100 papers. The measured count is about 3.7× that. The kill line was re-based on the approved A1 and A2 grants under A3 ruling 2.
- **Budgets reconciled:**
  - Haiku cap-e12e7a19: 2,028,945, covering the scope that cap governed.
  - Opus cap-90dc4922: 2,035,109 of 2.2M. That is extraction 891,320 + heavy grades 171,703 + lean grades 972,086.
- **Disk:** 1.72 MB of restatements and 0.55 MB of claims across 100 papers, well inside §10's 0.5 GB.
- **Not measured as separate stages:** fetch and parse wall time per paper. The text cache logs fetch timestamps only.

## 5. Compression: what each step keeps, against accuracy

Per paper, medians over 100 papers.

| Step | Size | Ratio to previous step |
|---|---|---|
| Paper text sent to restatement | ≈ 22,557 input tokens (≈ 90 KB at 4 bytes/token) | — |
| Restatement | 18.2 KB | ≈ 4.8× smaller |
| Extracted claims (JSONL) | 5.6 KB, 27.5 claims | ≈ 3.2× smaller |
| **Paper → claims** | | **≈ 15× smaller** |

- **Totals:** 2,070,956 input tokens → 1,719,936 bytes of restatement → 545,907 bytes and 2,812 claims.
- **Text cap:** 66 of the 100 texts hit the `approx_tokens` cap of 10,000 in the text cache, so for most papers the "paper text" is already a capped excerpt, not the whole paper. The ratios above are measured from that capped input.
- **Accuracy at the end of the chain:** the claims that survive are faithful at 0.889 (Haiku) and 0.944 (Opus), with locators correct at about 0.98. Round 1 does not grade the restatement on its own, so it cannot say which of the two steps loses the 11% of Haiku claims that are unfaithful.
- **Not tested in round 1, by design:**
  - Contextus's own tiered storage, Near ~10–50 KB down to a Distant ~200–500-byte fingerprint;
  - hypergraph compression;
  - cross-paper synthesis, which was ruled out of round 1's scope.
  Nothing from round 1 was fed into Contextus, BMA or Wyrd.

The per-claim grade list is in `s5_grades_A2_lean/` (20 files, manifest sha256 a2f2754b…039f), keyed to arms by `s5_arm_key_A2_SEALED.json`.

## 6. Q4: fan-out

- **Seeds:** 24 seeds produced a raw 2-hop fan-out of 14,016 candidates.
- **Domain guard:** checked 300 candidates in frozen score order, in batches of 150 per domain, until 50 per domain were admitted. 260 were in domain and 39 out of domain. The 13,716 lower-ranked candidates were never reached. This is a disclosed deviation from §2.3a's full-fan-out scope, per the director's live-test seq 4523 and 4533 rulings.
- **Dedup:** 100 were selected. One merge on title-Jaccard ≥ 0.85 (W1971010458 into W3104633719) left 99. The duplicate rate is 1 in 100.
- **Fetch failures:** 2 OpenAlex permanent failures, listed in `corpus_construct_output.json`. Neither was dropped silently.
- **Answer to Q4:** yes. A 1–2-hop fan-out from 24 seeds reaches more than 100 unique papers.

## 7. Accessible population (A1 §6)

- **Population:** round 1 describes **open-access** maths and physics papers. Physics, much of it in paywalled journals, is the weaker case.
- **Readable rate in the original selection:** 61 of 99 (maths 40/50, physics 21/49), after the disclosed parser fix (`run1/DEVIATION-NOTE-text-acquisition-fix.md`).
- **A1 walk-down to 50 + 50:** it tried 10 more maths and 49 more physics candidates, with 0 pipeline errors. K1 did not fire.
- **Thin restatements:** two papers (W4391839082, W3134337821) have thin restatements, thin in both arms. The shared restatement is the common cause.
- **Invalid JSON:** `s4_opus_arm/W3134337821.opus_extraction.jsonl` has 2 of 7 lines with un-escaped LaTeX backslashes. They are repaired on read only, and the committed raw file is never rewritten.
- **Over the claim limit:** W3162009980 and W7208731890 each emitted 41 claims against `extraction.md`'s limit of 40. This is a prompt-adherence finding. The §5 cap of 10 per paper still governed grading.
- **Zero statements:** two physics texts had no statements, W1533921740 and W6948872679 (`oa-fallback-no-statements`).

## 8. Q3: usefulness for Sprint 4

**Pending.** The UNANCHORED-seed counts and the #660/#661/#473/W6 candidate items are graded `useful` / `not` by qbp-oppenheimer (seq 268). Q3 is counted, not thresholded, so it does not affect the §7 verdict.

Under the §8 "every outcome" row:
- verified ids and **proposed** REF anchors go to the anchor owner through the CTH propose path, and are never adopted claims;
- the 14 UNANCHORED seeds are #660's first re-audit batch.

## 9. Disclosures

1. **A2 drift and tie order.** Re-running the frozen corpus construction gave the same count of 99 papers but a different set. 3 papers dropped out and 3 others came in (`walkdown_log.jsonl`, `REPRODUCE_MISMATCH` ×2, `A2_CONTINUE_PAST_MISMATCH`). The cause is OpenAlex data drift and tie order. A2 recorded this and the walk-down continued under it. The §5 sample was redrawn under A2 (`s5_sample_draw_redraw_A2.json`).
2. **A3, the grading harness.** The beekeeper's words were relayed by deming at seq 209, 212 and 216: "lean re-grade all 20", "re-base on the grants", "lets do 2.2m", "raise the grader stop to 50k", then "raise the grader stop to 65k". All are recorded in A3 before any lean grade existed.
3. **Heavy grades.** Two general-purpose grades (inter 8f587d2) exceeded the original 39k stop. They are committed as a recorded result only, never compared and never used.
4. **The director saw the heavy outputs.** qbp-oppenheimer, seq 204: the lean graders are fresh sub-agents with no access to them, so the record is unaffected.
5. **Grader-input wrapping.** The grader inputs are renders of the packets wrapped at 400 characters (`s5_grader_inputs_A2.py`, ab6c43a). Only line breaks change. Words and claims were verified unchanged.
6. **Gemini VOID run and redo.**
   - The first inter-rater run sent paraphrased paper text, not the A2 packets. The runner caught this itself at seq 231 before anything was compared.
   - It is recorded as VOID at d95b0c4. Its outcomes were seen, so it is on the record, but it is never scored.
   - The redo was ruled on input grounds, before any comparison (seq 234).
   - The redo dropped the `review_document` wrapper, because it wraps the prompt in a review template. It calls `generate_content` directly with the frozen `inter-rater.md` + "\n\n" + the grader input, through a script (`s5_interrater_redo.py`, 0574453).
   - Each `request_SENT` is byte-identical to that concatenation. All 4 finished with STOP on gemini-3.1-pro-preview (8e90ecb, copied verbatim at 79f2b6f).
7. **Thinking non-determinism.** Gemini runs with thinking enabled, so a re-run of the same request need not reproduce the same grades. The raw responses and thoughts are committed and hashed, and only the committed responses are scored.
8. **Stale and live server paths.** The ruling at seq 234 named the server under `~/Documents/mcp-servers/gemini/`. deming corrected this to the live path `~/.claude/mcp-servers/gemini/server.py` (sha256 7657d49e…). The redo used the live one.
9. **oppenheimer's spot-check method** (seq 241, verbatim in substance):
   - **Graded blind:** no grader verdict, arm key or tally was seen before the verdicts were fixed by sha (98d5feaf…01dc, committed verbatim at 937dfea).
   - Graded by hand, with no sub-agent.
   - Four papers were checked by locating cited passages with search rather than a full read: W4390977661, W7160385925, W1665497193 and W2080238236.
   - Two judgment rules were fixed before any comparison:
     1. "defines" for a symbol that already has a meaning in the paper is `wrong-relation`;
     2. "X proves P" read as "the paper shows X has P" is accepted, "A depends-on B" is `wrong-relation` when B is what A establishes, and "cited" as a relation is `wrong-relation`.
   - Every spot-check pair is the Haiku arm, by construction of the draw.
10. **Zero-statement texts.** See §7.
11. **Analysis start timing.**
    - deming's box conditions were a 10-sample median start temperature (≤ 42 °C at seq 249, revised to ≤ 50 °C at seq 262), a start inside the Zack window (last pass +120 to +320 s), boxrun on 1 core and `--timeout 600`.
    - The director's gate admitted at 23:54:55 EST (d = 190 s, median 50 °C). boxrun then queued the job for about 1h50m, first behind another run's box lease and then behind its own 58 °C start check. **The actual start (~01:45) was not inside the Zack window the gate had checked.**
    - Box safety held: a few seconds on one core, under boxrun's cool start and 65 °C pause (deming, seq 266).
    - The analysis is deterministic and seeded, so its numbers don't depend on when it ran.
    - boxrun has no Zack-window check of its own. deming is adding this case to Nidavellir#138.
    - An earlier 2-hour gate at ≤ 42 °C timed out without running. The cause was an unrelated 8-core test suite running outside boxrun (deming, seq 262).
12. **The analysis ran once.** Known-answer controls passed before the real run. There was no re-run and no selection between runs.

## 10. Record convention (inter#224 items 4–6)

- **Claims:**
  - *Grounded:* the fan-out reaches 100+ unique papers. The cost is measured, and the projection fails the cap.
  - *Unverified / inconclusive:* precision and locator accuracy. Both arms pass as graded by the lean grader, but that grader's agreement with an independent rater is below bar (κ 0.494), so the figures are **not validated** as measurements of faithfulness. The arm difference is not separated.
  - *Mislabeled risk:* reading 0.889 or 0.944 as "the extractor is ~90% faithful" without the κ caveat. On the 50 claims oppenheimer graded blind, a second grader comes out lower (0.80 against 0.86, §2).
- **Fired planning rows:** none. §8 has no row for this outcome (§2). The "every outcome" row still applies (§8 of this report).
- **Lock:** none. This is a spike, nothing merges to main, and there is no CI drift-gate.

E-grade: no move is claimed for faithfulness. The grader's agreement did not pass, so the confrontation is not counted as valid evidence. F = napkin.
