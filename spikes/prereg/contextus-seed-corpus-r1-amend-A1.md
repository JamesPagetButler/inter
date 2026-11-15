# contextus-seed-corpus round 1 — Amendment A1: accessible population (100 = 50 + 50)

Status: **SIGNED r4.** Beekeeper approval recorded 2026-11-15 (inter#224 issuecomment-6901375447). All four federation signatures are on r4 (sha256 `d3b0e6d2b0c61e8645910c1d84d7e29ca946f1abcd16ba3bab4064c90b60a274`): director (issuecomment-6899224216), qbp-oppenheimer (issuecomment-6899230479), contextus-spike (issuecomment-6899231487), deming (issuecomment-6899231884).

r4 adds contextus-spike's two §6 disclosures (inter#224 issuecomment-6899207758); reporting only, no rule change. r3 folds qbp-oppenheimer's K1, K2, S1 and S2 (inter#224 issuecomment-6899196955). r2 folded deming's seq 119 condition: §4 names the haiku grant and its separate sign-off, and §3 runs under `boxrun`. Amends `spikes/prereg/contextus-seed-corpus-r1-prereg-FROZEN-v1.md` (sha256 `f31c62fcf8e4586f947a803123c4b17a122b3ef05146a73465c8e8387608fb17`). FROZEN-v1 is not edited. Where A1 and FROZEN-v1 differ, A1 governs. Everything A1 does not name is unchanged.

Author: qbp-architecture (director). Directed by the beekeeper, 2026-11-15, first-hand in qbp-architecture's session: complete round 1 "as documented: 100 total, 50 math, 50 physics", with the population "the top 100 by citation links that are accessible through our approved sources".

## 1. Why

§2.3 selects "100 unique papers: 50 per domain". The selection reached 99 (50 maths / 49 physics after one dedup merge). Under §2.5, 38 of those were `text-unavailable`, so 61 were extracted (maths 40/50, physics 21/49; `text_cache_manifest.jsonl` sha `2205acee…b8a`). §8 has a rule for fan-out shortfall but none for a **text-access** shortfall, which is what happened. The director treated the 38 `text-unavailable` papers as a recorded status and accepted 61 without a top-up. The beekeeper caught it. No claim has been graded, so no outcome has been seen: this is the last point where the population can change cleanly.

## 2. The population (replaces §2.3's stopping rule)

**Round 1's corpus is the top 100 papers by citation links that are accessible through our approved sources: 50 maths, 50 physics.**

- **"Top by citation links"** = FROZEN-v1 §2.3's score, tie-breaks and per-domain ranking, with the §2.3a domain guard and seed exception, unchanged. The ranking is filtered, never re-scored.
- **"Accessible"** = the frozen text fetcher and parser at code commit `432d049` returns `status: ok`. A paper that is reachable but yields zero statements is **not accessible**, and is logged as such.
- **"Approved sources"** = FROZEN-v1 §10's public APIs: arXiv (ar5iv), OpenAlex open-access locations, Semantic Scholar, Crossref. No new source, credential or publisher access. Adding one changes the population and needs a new beekeeper decision.
- **Dedup** as §2.3: title-Jaccard ≥ 0.85, one kept.

## 3. Walk-down procedure

1. **Reproduce first.** From the cached responses, re-run the construction and confirm it reproduces `corpus_construct_output.json` (sha `546df8c0…d7fe9`) selection order exactly. Any mismatch → stop and report, no walk-down.
2. Per domain, continue down the frozen score-descending order past the current 50 selected, guard-checking in batches of 150 (live-test seq 4533 binding 1). Each in-domain candidate is fetched and parsed with `432d049`.
3. Stop when the domain holds **50 accessible papers**, counting the ones already `ok`. If a domain's ranked pool within 2 hops is exhausted first, stop at what was reached and record it under §8 "fan-out < 100". Hop 3 is not opened in round 1.
4. **Every candidate tried is logged**: rank, domain, hop, guard result, text status, and reason (no arXiv id / no OA location / zero statements). A fetch failure is not a skip reason; see §7 (K2). Already-selected papers that are `text-unavailable` stay in the log, seeds included.
5. **Reported as a result:** candidates tried vs accessible, per domain and per hop (the accessible fraction). This feeds the round 2 cost forecast, which must count candidates tried, not papers kept.

Network and parsing only, zero model calls. Rate limits per §10. Runs under `boxrun` as the only IO-heavy job on the box (deming seq 119).

## 4. Extraction of the new papers

- Haiku restate + extract on the newly admitted papers (about 39): same frozen prompts (FROZEN-v1 prompt shas), same runner (contextus-spike, `rolling_runner.py`), same containment rule.
- **Fix budget is not reset** (2 of 2 used). Any pipeline failure → stop and report.
- **Budget:** about 1.8M haiku tokens (39 × ≈45k, the measured §4 rate). This grant needs the **beekeeper's separate written sign-off**, distinct from approving A1. contextus-spike files the request only after A1 is signed (deming seq 116, 119).
- Caps, per deming seq 116: stop and report at 58k tokens per paper; batches of ≤ 10; box clearance as for §4, per deming.
- Before any analysis: hash the raw output and the **100-paper manifest**, commit, and post the shas.

## 5. §5 sample redraw

- The 20-paper sample is **redrawn from all 100** with PCG seed `250125` and FROZEN-v1 §5's rule (10 per domain, from status `extracted`).
- **Input order (S1):** the draw runs over the 100-paper manifest sorted by OpenAlex id, ascending, within each domain. The 20 drawn ids are committed, and their sha posted, **before** any new Opus extraction or packet build.
- **Opus arm:** outputs already produced for a paper that is drawn again are reused unchanged (same frozen prompt, same restatement). Papers newly drawn get a fresh Opus extraction under the same rules.
- The pre-amendment Opus arm (manifest `0e2bc3db…851e`, HEAD `af3deea`) and grading packets (HEAD `6edf8ae`) **stay committed as a recorded result**. Papers in them that are not redrawn are not graded and not reported as part of round 1's metrics.
- **Fresh blinding (S2):** grading packets and the sealed arm key are rebuilt over the full redrawn 20, so reused Opus outputs are re-blinded with the rest. The pre-amendment key (HEAD `6edf8ae`) is not reused.
- Grading, the Gemini inter-rater (first 4 drawn) and oppenheimer's 50-claim spot-check then run as FROZEN-v1 §5. Grader dispatch: director, batches of ≤ 5, spread over time, stop at 39k per grader.
- Budget: inside cap-90dc4922 (984,472 left). If it would be exceeded, stop; deming asks the beekeeper (seq 116). **If the budget stop fires mid-grading, round 1 is reported as incomplete. No metric is reported on a partial sample (S2).**
- **Stratified report (S2):** metrics are also reported split by original-61 versus walk-down-admitted papers, as description only. No threshold applies to the split; §7's thresholds stay on the pooled 20.

## 6. Reporting

The round 1 report leads with the quality verdict and the round 2 go/no-go. It then states, prominently:
- the population definition in §2;
- the accessible fraction per domain;
- the limit it implies: results describe **open-access** maths and physics papers. Physics, much of it in paywalled journals, is the weaker case;
- the two thin-restatement papers (W4391839082, W3134337821), thin in both arms, with the shared restatement as the common cause;
- `s4_opus_arm/W3134337821.opus_extraction.jsonl`: 2 of 7 lines carry un-escaped LaTeX backslashes, which makes them invalid JSON in the committed raw file. Readers repair them on read only (`tolerant_json_loads`). The committed raw is never rewritten;
- two primary-arm papers (W3162009980, W7208731890) each emitted 41 claims, one over `extraction.md`'s "at most 40" rule. This is recorded as a prompt-adherence finding. The §5 per-paper cap of 10 still governs what is graded.

## 7. Kill-condition reading (§10)

"More than 20% of papers erroring at any stage" counts **pipeline errors**: a fetch error, a crash, malformed output. A paper that is `text-unavailable` or `not accessible` is a **recorded status** under §2.5 and A1 §2, not an error. This reading is stated here so the beekeeper can overrule it.

- **K1, zero-statement papers:** these are counted separately. If they exceed 10% of `ok` fetches in either domain, they count as pipeline errors under §10, and the run stops and reports. The director hand-inspects the first 3 zero-statement texts before the walk-down continues.
- **K2, fetch failures:** `no arXiv id` and `no OA location` are statuses. A fetch failure (HTTP error, timeout) is retried twice under §10's rate rules. If it still fails, it is logged as a pipeline error and counts toward the 20% kill threshold. It is not a skip.

## 8. Not changed

Questions Q1–Q4, the domain guard and seed exception, the §2a safety-stop rule, the claim schema, the frozen prompts, the grader rules, every §7 threshold, the round 2 budget (20M haiku), and every other kill condition.

## 9. Signatures

- [x] Beekeeper approval (written, on the tracking issue) — inter#224 issuecomment-6901375447, 2026-11-15.
- [x] qbp-architecture (director) — issuecomment-6899224216.
- [x] qbp-oppenheimer (grading rules / domain owner) — issuecomment-6899230479.
- [x] contextus-spike (runner) — issuecomment-6899231487.
- [x] deming (box safety and budget; haiku grant for §4) — issuecomment-6899231884.

On signing: committed to `spikes/prereg/contextus-seed-corpus-r1-amend-A1.md` on `contextus-spike/seed-corpus-s4`, sha256 posted. The run go cites A1's sha with the three gates.
