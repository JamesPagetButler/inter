# Round 1.1 component results

## sampler.py (pre-reg §4, §8b)
- Known-answer tests: 8/8 PASS (`test_sampler.py`): counts 387/62/325, deterministic twice, 6 per paper and 120 total (C1 cap), never contaminated, 60/60 split disjoint and complete, probe excludes W7160385925 (across 200 seeds), seed changes the draw.
- Mutations:
  - M1, contamination filter removed: KILLED
  - M2, unseeded RNG: KILLED
  - M3, 7 per paper: KILLED
  - M4, probe allows W7160385925: KILLED. It first SURVIVED: a single seed missed W716 by chance, so the test was strengthened to 200 seeds.

## relation_registry_gen.py + relation_validator.py (pre-reg gate 2, inter#300 O4)
Registry source: `spikes/run1/vocab/relation-types-v1.yaml`, checked against
`relation-definitions-v1-SIGNED.md` (sha256 `ea3f245e…f2d4`). Generated
projections, both committed and pinned: `relation-types-v1.json` and
`relation-rubric-v1.txt` (first line `RUBRIC-ID: relation-types-v1
source_sha256=ea3f245e…f2d4 registry_sha256=…`). The rubric sha is now
available to pin gate 3 (verifier-v1) and gate 4 (checker_v1)'s
`--rubric-sha`.

### §I4 FIX ROUND (qbp-architecture, head `7496431`)
The first cut hand-paraphrased the signed prose into registry fields, and
the paraphrase silently dropped decisive sentences (`proves`'s "if the
subject is an object rather than a result, use `has-property`", among
several others) and mis-rendered one example (⋃ as "colim-of-limits").
The CLI also never called `canonicalize_claim`, so a `specialises` claim
from stdin was reported "unknown" instead of accepted as its
`generalises` rewrite. Both guards the review found gutted-but-passing
(mutants C and D) SURVIVED under the old substring-only checks.

**Fix:** `relation-types-v1.yaml` now carries only mechanical/structural
facts (arity, symmetry, sense values, tail kinds, canonical rewrites, the
has-property guard) — no prose duplicate of the signed definitions at
all. `relation_registry_gen.py`'s `parse_signed_doc()` structurally
slices each type's full `### N. \`id\`` section, the field-conventions
block, and the settled-at-signing block directly out of the signed
markdown — byte-exact substrings, verbatim by construction, not by a
check that a truncation can still pass. The claim field is renamed
`relation` → `relation_type` (the SIGNED spelling, per §I4). `main()` now
canonicalizes every claim before validating it. `proposed:cites` and a
bare `proposed:` are both rejected.

- **Known-answer tests, `test_relation_registry_gen.py`: 17/17 PASS.**
  Adds: all 10 signed sections parse in order with every six-part marker
  present (a truncated slice is now mechanically detectable); the
  decisive sentences the review found dropped are confirmed present
  verbatim (the has-property redirect, the `⋃` example, the field
  conventions' "Result" means sentence, the settled-at-signing block);
  editing one signed sentence changes the generated rubric's sha; two
  negative fixtures directly target mutants C and D.
- **Known-answer tests, `test_relation_validator.py`: 28/28 PASS.** Adds:
  per-type accept coverage for all 10 registered ids (not just `proves`);
  `proposed:cites` and bare `proposed:` both rejected; a subprocess-level
  test that `main()` itself canonicalizes (not just the library function)
  before validating.
- **Mutations, each applied, confirmed KILLED, then reverted:**
  - M1 (validator), the `cites`-rejection branch removed: KILLED.
  - M2 (validator), the unknown-bare-type-id rejection removed: KILLED.
  - M3 (validator), `canonicalize_claim`'s `equivalent-to` sort removed: KILLED.
  - **Mutant C** (generator), `check_sections_complete` gutted to `return
    []`: **KILLED** (SURVIVED in the §I4 review against the old code).
  - **Mutant D** (generator), `check_source_sha` gutted to `return []`:
    **KILLED** (SURVIVED in the §I4 review against the old code).

**Scope note (unchanged):** this component validates claim *shape*
mechanically (required fields, known/`proposed:` type ids, modality enum,
`depends-on` tail structure, `equivalent-to` sense enum, the two
mechanical rewrites). It does not and cannot judge the admissibility test
against the paper's own text — that stays the verifier/checker's job
(gates 3/4), never this one's.

**Non-blocking items from §I4, not yet addressed:** the gate-2 checklist
path (`registry/` vs the actual `spikes/run1/vocab/`) is the architect's
own fix in the pre-reg; `quote` becomes required only in the 1.2
extraction schema, not 1.1, per the review.

## §8a director components (qbp-architecture): L0 checks, escalation router, analysis script, P4 capture
All four are pure local code: no network, no model call. Every test file was run before its module
existed and failed (ImportError), and was then made to pass. Each test file runs both as
`python3 -I test_x.py` (exit 1 on any failure) and under `python3 -m pytest` (plain `test_*`
functions): **66/66 collected and PASS under pytest**. All runs under `boxrun`, 1 core.
Mutations were applied one at a time (an exact-once string replacement), the test was run, and the
original was restored with a sha check.

### l0_checks.py (§5 L0, §3 C3, §8 validity)
- Known-answer tests, `test_l0_checks.py`: 14/14 PASS. The committed rubric hashes to the pin
  `f950c385…ed23`, and its first line is the RUBRIC-ID. Five out-of-set grades are each rejected,
  and all six categories are accepted. A wrong echoed rubric_id voids, and a missing echo voids. A
  received-rubric sha that differs in one hex digit voids. Void beats reject. A checker meta.json
  `rubric_sha` mismatch, or a missing one, voids. An out-of-set checker grade is rejected. Ten
  schema faults are rejected. One void output voids the whole run (`run_validity`). Output is
  deterministic.
- Mutations:
  - M1 (the §8a mutation), received-rubric sha check removed: KILLED (3 tests)
  - M2, category-set check removed: KILLED
  - M3, echoed-rubric_id comparison removed: KILLED
  - M4, reject made to dominate void: KILLED
  - M5, `run_validity` ignores voids: KILLED
  - M6, checker meta sha check removed: KILLED
- The CLI was run twice on a fixture: identical bytes.

### escalation_router.py (§5 ladder)
- Known-answer tests, `test_escalation_router.py`: 20/20 PASS:
  - no doubt settles at L0; an L0 reject is not routed;
  - doubt goes to L1; L1 agreement settles; an L1 split goes to L2, including a split between two
    non-faithful grades;
  - L2 converged settles; an L2 impasse goes to L3;
  - a rule-meaning impasse goes to L4 with no L3 in its path, even when a stray L3 ruling is
    supplied; L3 may refer an item up as rule-meaning;
  - an L3 or L4 ruling settles and is a calibration item; an unresolved L4 goes to L5;
  - an audit disagreement goes to L2;
  - exactly 30 items at L3 are not flagged; 31 are flagged, and only the 31st in id order;
  - rule-meaning items don't consume the L3 budget;
  - the summary counts and doubt rate are correct; bad inputs raise; output is deterministic and
    independent of input order.
- Mutations:
  - M1, rule-meaning routed via L3: KILLED (4 tests)
  - M2, budget check `>=`, an off-by-one: KILLED
  - M3, over-budget flag dropped: KILLED
  - M4, doubt ignored: KILLED
  - M5, L1 agreement judged faithful-vs-not: KILLED
  - M6, L3 ruling not marked as calibration: KILLED
- The CLI was run twice on a fixture: identical bytes.

### analysis_r11.py (§6, §7, §8)
- Known-answer tests, `test_analysis_r11.py`: 22/22 PASS.
  - **Cohen's κ:**
    - exactly 1; exactly 0 (po = pe = 0.5);
    - prevalence-skewed: 85/5/5/5 of 100 gives po 0.90, κ = 4/9;
    - -1; undefined (None) when pe = 1.
  - **Wilson:** 8/10 → [0.490162, 0.943318], computed by hand in the test and matching the textbook
    0.490 / 0.943. 0/10 → [0, z²/(n+z²) = 0.277533].
  - **Paper-cluster bootstrap, two-paper fixture:** paper A has κ 1 and paper B has κ -1, so only
    {1, 0, -1} can occur. Every replicate is in that set, at frequencies ¼ / ½ / ¼, and CI = [-1, 1].
    A seeded run is byte-identical on a re-run and changes with the seed. Undefined replicates are
    counted at the expected (2/3)³ rate.
  - **Round-1 reproduction:** see below.
  - **Round-1 Gemini parse rule:** a conflicting duplicate is unparsed.
  - **§8 decision table:** every row, plus "not listed" for an undefined bound or an undefined G2.
  - **Full-bundle fixtures** (verifier = round-1 lean grades):
    - identical raters give κ 1 on 120 and on 114/19 papers;
    - the headline arms sum to 325 and the contaminated arms to 62, the latter labelled circular;
    - haiku has 169 faithful in all;
    - an inverted checker gives the closed-form κ, -pe/(1-pe), and "G1 fail, point < 0.6";
    - 16/20 audit → G2 fail, and 17/20 → pass;
    - void → no outcome read;
    - a missing verifier grade or an out-of-set checker grade aborts;
    - doubt rate and four-field tokens are correct;
    - output is deterministic.
- **Round 1's κ reproduced:** κ = 0.49420442571127504. That is round 1's
  `s5_analysis_A2_results.json` value bit-for-bit, and the whole `overall` and `per_arm` blocks are
  dict-equal: n 80, raw agreement 0.85, prevalence 0.825; haiku 0.4791666666666669, opus 0.5.
  - The inputs are round 1's own files, read independently by this script. They are the A3 lean
    grades `s5_grades_A2_lean/` (manifest a2f2754b…039f, every entry sha-checked) against the
    Gemini redo answers `s5_interrater_A2/<id>.answer_RAW.txt`, each checked against its
    meta.json `answer_sha256`. The papers are W4390977661, W7160385925, W2015765968 and
    W4313326288, both arms. The arm key is sha-checked (af6f985e…f206).
- Mutations:
  - M1, κ's pe drops the both-not term: KILLED (7 tests)
  - M2, item-level instead of paper-cluster bootstrap: KILLED
  - M3, unseeded bootstrap RNG: KILLED
  - M4, Wilson z²/(4n) for z²/(4n²): KILLED
  - M5, the round-1 conflicting-duplicate rule removed: it first **SURVIVED**. Round 1's data has no
    conflicting duplicate, so the reproduction couldn't see it. The parser was factored out
    (`parse_gemini_answer`) and given a direct fixture test, and on re-run it was KILLED.
  - M6, G1 judged on the point κ, not the lower bound: KILLED
  - M7, W7160385925 not excluded for G3: KILLED
  - M8, contaminated claims left in the headline pool: KILLED
  - M9, an undefined replicate counted as κ 1: KILLED
  - M1–M4 and M6–M9 were re-run on the final file after the M5 refactor: all KILLED.
- The CLI was run twice each, for `round1` and for `run` on a fixture bundle at the full B = 10000:
  identical bytes.

### p4_capture.py (§3 P4)
- Known-answer tests, `test_p4_capture.py`: 10/10 PASS.
  - The grades hash is the sha256 of the exact bytes through `GRADES-END\n`, and editing P4 doesn't
    change it.
  - Extracting before recording is refused (`NotRecorded`), and so is extracting under another key.
  - A grade altered after recording is refused (`GradeAltered`), at extract and at re-record.
  - Five ways for a P4 to carry a grade are all refused: an extra key, a nested object, a grade
    JSON inside a string, a grade line after GRADES-END, and a second GRADES-END.
  - A missing or malformed P4 is refused.
  - Prose that discusses a grade is kept.
  - Recording twice is a no-op (one ledger line), and the ledger bytes are identical across two
    fresh runs.
- Mutations:
  - M1 (the §8a mutation), extract without a prior record: KILLED
  - M2, re-hash at extract removed: KILLED
  - M3, the grade-carrying detector gutted: KILLED
  - M4, re-record with a new hash allowed: KILLED
  - M5, the ledger not idempotent: KILLED
- The CLI (record ×2, extract) was run twice in fresh ledgers: identical bytes.

### Assumptions where the pre-reg is silent (simplest reading; the director should ratify or amend)
- **A-R1:** only verifier doubts and audit-labeller disagreements enter the ladder. A non-doubted
  verifier/checker disagreement on the 120 is the κ measurement, not an escalation.
- **A-R2:** "agree"/"split" at L1 is exact grade equality over the six categories.
- **A-R3:** a rule-meaning dispute is a boolean on the L2 impasse record, or an L3 referral up. It
  always goes to L4, never through L3.
- **A-R4:** an audit item goes to L2 unless both labellers equal the agreed grade. G2 is scored on
  the labellers' original grades, never on the L2 outcome.
- **A-R5:** L3 over budget is flagged, not truncated. Items beyond 30, in sorted id order, carry
  `l3_over_budget`.
- **A-R6:** an unresolved L4 goes to L5. An L4 ruling settles.
- **A-A1:** an undefined κ replicate (pe = 1) is dropped and counted.
- **A-A2:** each bootstrap restarts `default_rng(251117)`. The interval is a numpy linear percentile.
- **A-A3:** "agreed" (audit eligibility) and labeller "confirmation" are exact-grade matches.
- **A-A4:** P2's drops are like-for-like: round-1 lean minus v1 precision on the same headline haiku
  claims. P1 uses the literal 0.889.
- **A-A5:** "tokens (four-field)" means each stage carries exactly four numeric fields. The field
  names aren't fixed here.
- **A-P1:** "a report that alters a grade" is defined mechanically: the grade section differs from
  the recorded hash, extra content follows GRADES-END, or the P4 carries a grade/n key (including as
  embedded JSON).
- **A-P2:** prose that discusses a grade is kept.
- **A-L1:** C3 for the verifier needs both of these: the sha of the bytes dispatched equals the pin,
  and the echoed id equals the pinned first line. A missing echo voids. The verifier output's JSON
  key order is not enforced.

### Not computed (needs a reading, or isn't specified)
- P4 clustering by RCA cause.
- The per-category distribution "against round 1" is given on the same claims only.
- The §8b probe measures (Fleiss' κ, the unanimous share) are outside this component's §8a row.

### analysis_r11.py FIX ROUND (qbp-architecture independent probe Q4 on 08f49bc)
- **Found:** the probe changed `np.percentile(reps, 2.5)` to `5`, and it **SURVIVED** every test.
  The tests pinned the replicate frequencies but not the interval endpoints, and G1 and G3 are
  decided on the lower bound. A real bootstrap of discrete κ values has ties at its neighbouring
  ranks, so it can't tell the linear rule from nearest-rank on its own.
- **Fix:**
  - The interval is factored into `percentile_ci(reps)`.
  - New tests:
    - `test_percentile_ci_hand_computed`: reps = i², i = 0..10, gives [0.25, 95.25] by hand. Linear
      at h = 0.25 is 0.25; at h = 9.75 it is 81 + 0.75·19. Nearest-rank would give 0 / 100, and the
      5th / 95th percentiles would give 0.5 / 90.5.
    - `test_cluster_bootstrap_ci_is_percentile_ci_of_its_replicates`: checks the wiring.
    - `test_cluster_bootstrap_ci_endpoints_are_2_5_and_97_5`: an 8-paper fixture, checked against
      a numpy-free linear percentile in the test. It first asserts that the 2.5/5 and 95/97.5
      percentiles differ, so the test can tell them apart.
    - `test_g1_reads_lower_bound_of_the_120_interval` and `test_g3_reads_lower_bound_of_the_114_interval`:
      a monkeypatched bootstrap returns [0.55, 0.90] with point κ 1. G1 must give
      "G1 fail, point ≥ 0.6", and G3 must give "G3 fail".
- **Known-answer tests, `test_analysis_r11.py`: 28/28 PASS.** All four suites give 72/72 under pytest.
- **Mutations:**
  - Q4, lower 2.5→5: KILLED
  - Q5, upper 97.5→95: KILLED
  - Q6, endpoints swapped: KILLED
  - Q7, G1 fed ci[1]: KILLED
  - Q8, G3 fed ci[1]: KILLED
  - Q9, nearest-rank percentile: **SURVIVED** against the bootstrap-fixture test alone, then KILLED by
    the hand-computed `percentile_ci` test. The first attempt used `method=`, which numpy 1.26 doesn't
    accept, so it died on a TypeError. That was not counted as a kill, and the mutant was redone with
    `interpolation=`.
  - Q10, bootstrap bypasses `percentile_ci` with an inline 5: KILLED
  - M1–M9 re-run on this file: all KILLED.
- **Results unchanged:** round 1's κ is still 0.49420442571127504. The `round1` and the B = 10000
  fixture `run` outputs are byte-identical across two runs, and to the 08f49bc outputs.

### Gate-8 FIX ROUND: cartan R2 and R6 (inter#224, on 044333c)
**R2, rubric parity for every rater**
- `l0_checks.check_rater_run(role, …)` covers the roles verifier, L2-verifier, checker, L1-checker
  and L2-checker. L1 is a fresh checker session and L2 is fresh verifier and checker sessions, so
  each goes through the same C3 check as its first-pass counterpart.
- `l0_checks.check_labeller_set()` checks audit-labeller records: qbp-oppenheimer's hand labels and
  the Gemini labeller.
  - A record's effective sha is its own `rubric_sha` if it has one, otherwise the set header's.
  - Any missing, empty or mismatched sha voids that labeller's whole set.
  - An out-of-set grade or wrong item coverage rejects the set. Void outranks reject.
- `analysis_r11.analyse()` now takes the labeller grades only from `audit_labellers` sets. It checks
  them against a pinned constant (`PINNED_RUBRIC_SHA`, which a bundle cannot override). If either
  set is void, G2 reads `"void"` and the decision is "not listed: G2 void (audit labeller rubric
  parity)" → L4 → beekeeper, never pass. G1 is still evaluated first.

**R6, ceiling on dropped bootstrap replicates**
- `drops_exceed_ceiling(undefined, B)` uses a strict inequality, `undefined*100 > B`: 100 of 10000
  is not over the ceiling, and 101 is.
- Each bootstrap block reports `undefined`, `drop_rate` and `drops_exceed_ceiling`.
- If G1's drops are over the ceiling, the outcome is "G1 inconclusive: bootstrap drops > 1% of B",
  never pass or fail.
- If G3's drops are over, the outcome is "G1 pass, G2 pass, G3 inconclusive: …". G2 is still
  evaluated before G3.
- Both inconclusive outcomes are owned by "L4 -> beekeeper", because the §8 table doesn't list them.

**Tests**
- `test_l0_checks.py`: 24/24 PASS.
  - The 10 new tests failed first: L2-verifier, L1-checker and L2-checker parity; every role is
    checked; labeller header sha, per-record sha, missing sha, mismatched sha, and grade/coverage.
- `test_analysis_r11.py`: 40/40 PASS.
  - Of the 12 new tests, 3 failed first on an unknown keyword or a missing attribute: the ceiling
    boundary at 100/101 of 10000 and 2/3 of 200, and the inconclusive decision rows.
  - The other 9 failed first because the format change made the shared fixture fail:
    - drop count and rate reported;
    - exactly 1% still decides;
    - over 1% is inconclusive, not pass and not fail;
    - G3 over 1% is inconclusive;
    - G2 void on a mismatched sha, on a missing sha (for each labeller), and with an otherwise
      perfect 20/20 audit;
    - G2-void decision rows;
    - the bundle cannot override the pin.
  - The bundle format change made 9 existing fixture-based tests fail with KeyError. After the fix
    they pass unchanged.
- All four suites give **94/94 under pytest**.

**Mutants**
- R2 in l0_checks, all KILLED:
  - labeller sha check dropped
  - missing sha accepted by defaulting to the pin
  - missing sha accepted by skipping falsy values
  - header sha wins over a record's own sha
  - L1/L2 checker meta not enforced
  - L2 verifier sha assumed to be the pin
- R2 in analysis, all KILLED:
  - G2 void mapped to pass
  - analyse ignores labeller parity
  - the bundle overrides the pin
- R6, all KILLED:
  - ceiling ignored
  - `>=` at exactly 1%
  - G1 inconclusive mapped through to pass or fail
  - G3 inconclusive mapped to pass
  - analyse drops the G1 flag
  - analyse drops the G3 flag
- Re-run on the final files, all KILLED: analysis M1–M9 and Q4–Q10, L0 M1–M6.

**Determinism and κ**
- Round 1's κ is still 0.49420442571127504.
- The `round1` and the B = 10000 fixture `run` outputs are byte-identical across two runs.
- The `run` output differs from earlier fixture runs only because of the new fields and the new
  bundle format.

### l0_checks.py FIX ROUND: director probe Q11 (on d7da191)
- **Found:** truncating the labeller sha comparison to `eff[:16] != pinned[:16]` **SURVIVED**,
  because every mismatch fixture differed from the pin early in the string. Against the d7da191
  tests I confirmed:
  - `[:63]` on the labeller path SURVIVED;
  - `[:63]` on the checker-meta path also **SURVIVED**;
  - `[:63]` on the verifier received-sha path was already KILLED, because its fixture differs in
    the last hex character.
- **Fix:** five new tests use a sha that differs from the pin only in its last hex character. A
  self-check asserts the first 63 characters are equal. The tests cover:
  - the labeller header sha;
  - the labeller record sha, both without a header and overriding a good header;
  - checker meta, both directly and for each of checker, L1-checker and L2-checker;
  - verifier received sha, both directly and for verifier and L2-verifier.
- **Known-answer tests, `test_l0_checks.py`: 29/29 PASS.** All suites give 99/99 under pytest.
- **Mutants on the new tests:** all six KILLED.
  - Q11 labeller `[:16]` and `[:63]`
  - checker meta `[:16]` and `[:63]`
  - verifier received sha `[:16]` and `[:63]`

### Amendment-2 FIX ROUND: blindness attestation and checker grades outside the 120 (on bb3490c)
**Blindness attestation**
- `l0_checks.check_labeller_set` now voids a labeller set unless its **header** carries
  `"blind": true`, which attests that the labeller did not see the verifier, checker or agreed
  grades.
- Only the JSON boolean `true` counts. A missing value, `false`, or any non-boolean value
  (`"true"`, `"True"`, `1`, `"yes"`, a list, a dict, null) voids the set.
- The check is header-level only. A record-level `blind` key is ignored, whichever way it points.
- A void set makes G2 read void through the existing path, and the decision is "not listed: G2
  void (audit labeller rubric parity)". This was tested for each labeller in `analyse()`.
- The existing ok fixtures now attest `blind: true`.

**Checker grades outside the 120**
- `analyse()` now accepts checker grades beyond the double-graded 120, for example L1 doubt checks.
- It still requires that the checker grades cover all 120, that every extra grade is for a keyed
  claim, and that every grade is in the category set.
- It then uses only the 120 for κ, G1–G3, audit eligibility and every other measurement. Before
  this change, an extra checker grade aborted the analysis.
- The new test adds checker grades for all 267 non-sampled claims, deliberately the opposite of
  the verifier. It checks that the results are byte-identical with and without them, for both the
  identical-checker and flipped-checker fixtures.

**Tests**
- `test_l0_checks.py`: 35/35 PASS. The 5 new blindness tests failed first.
- `test_analysis_r11.py`: 44/44 PASS.
  - The blind-G2-void test and the outside-120 byte-identity test failed first.
  - The extra-grade-validity and coverage tests passed before the change only because any extra
    grade aborted the analysis then.
- All suites give 109/109 under pytest.

**Mutants**
- Blindness, all KILLED:
  - B1, check removed
  - B2a, any truthy value accepted
  - B2b, the string `"true"` accepted
  - B3, missing treated as true
  - B4, record-level `blind: true` overrides a missing or false header
  - B5, record-level `blind: false` overrides a true header
- Outside the 120, all KILLED:
  - C1, all checker grades pooled everywhere
  - C2, κ-120 pooled
  - C3, the G3 set pooled
  - C4, extra grades not validated
- All 44 earlier mutants re-run on the final files: all KILLED.
  - l0: L0-M1–M6, R2-M1–M6, Q11 `[:16]`/`[:63]` on all three paths
  - analysis: M1–M9, Q4–Q10, R6-M1–M6, R2-A1–A3

**Determinism and κ**
- Round 1's κ is still 0.49420442571127504.
- The `round1` and the B = 10000 fixture `run` outputs are byte-identical across two runs, and the
  `run` output is identical to d7da191's.
