# Round 1.1 component results

## sampler.py (pre-reg §4, §8b)
- Known-answer tests: 8/8 PASS (`test_sampler.py`): counts 387/62/325, deterministic twice, 6 per paper and 120 total (C1 cap), never contaminated, 60/60 split disjoint and complete, probe excludes W7160385925 (across 200 seeds), seed changes the draw.
- Mutations:
  - M1, contamination filter removed: KILLED
  - M2, unseeded RNG: KILLED
  - M3, 7 per paper: KILLED
  - M4, probe allows W7160385925: KILLED. It first SURVIVED: a single seed missed W716 by chance, so the test was strengthened to 200 seeds.

## capture.py (pre-reg §3, §5 L0; §8a "L0 checks", "P4 capture")
- Two phases. `capture_grades` hashes the exact bytes before the single exact `GRADES-END` line, then validates the grades and the rubric_id echo; the text after the marker is not parsed. `capture_p4` refuses a record without that hash (or whose grades block changed), rejects any grade-like JSON after the marker (`P4AltersGradeError`), then parses exactly one `{"p4": {...}}` line with the five verifier-v1 fields. `check_rubric_parity` raises `RunVoid` on any mismatch (C3). Every violation raises; nothing is repaired.
- Known-answer tests: 19/19 PASS (`test_capture.py`): valid response passes with a stable sha; sha = sha256 of the exact pre-marker bytes; sha independent of P4 and changes with the grades; grades hashed before P4 is parsed (phase 1 succeeds on a garbage P4, phase 2 refuses a missing or altered hash); missing n; extra n; duplicate n; out-of-order n; bad grade; doubt=true with empty reason; doubt=false with a reason; doubt not a bool; empty reason; wrong rubric_id; a grade line after GRADES-END (incl. nested) rejected as a P4 alteration; missing or altered marker; two markers; P4 missing, malformed or doubled; parity mismatch, None and an empty record are all VOID.
- Mutations:
  - CM1, parity check removed: KILLED
  - CM2, n-set check removed: KILLED
  - CM3, grade-like scan after the marker removed: KILLED
  - CM4, extra lines after the marker accepted (grades after the marker pass): KILLED
  - CM5, duplicate-n check removed: KILLED
  - CM6, rubric_id echo check removed: KILLED
  - CM7, doubt_reason "iff" weakened to "if": KILLED
  - CM8, sha taken over the whole response (P4 included): KILLED
- No first-survivors.

## router.py (pre-reg §5; §8a "Escalation router")
- Pure `route(item)` over the ladder: not doubted → settled at L0; doubt → L1; L1 same grade → settled; split → L2; converged → settled; impasse → L3, but a rule-meaning dispute → L4, skipping L3; L3 ruling → settled; L4 ruling → settled, impasse → L5; L5 ruling → settled. Undefined states raise `RouterError`. `route_round` counts the items whose path reaches L3 and sets `l3_over_budget` when the count is > 30.
- Known-answer tests: 15/15 PASS (`test_router.py`): every §5 transition; L1 agreement is on the exact grade; the rule-meaning skip (an L3 record on a rule-meaning item is rejected); L4 and L5; fail-closed on undefined states; the L3 flag is false at 30 and true at 31; items settled at L3 count against the budget and L4 skips do not; per-layer counts.
- Mutations:
  - RM1, rule-meaning dispute routed to L3: KILLED
  - RM2, L3 budget flag dropped: KILLED
  - RM3, budget off by one (flag at 30): KILLED
  - RM4, non-doubted items sent to L1: KILLED
  - RM5, L1 split settles at the verifier grade: KILLED
  - RM6, L1 agreement on faithful-vs-not instead of the exact grade: KILLED
- No first-survivors.

## analysis_r11.py (pre-reg §6, §8, §8b; §8a "Analysis script")
- Cohen κ (faithful vs not); Wilson (z = 1.959964); paper-cluster bootstrap (B = 10000, seed 251117, `default_rng`, one `integers(0, P, P)` draw per replicate over sorted papers, percentiles 2.5 / 97.5; undefined replicates are dropped and counted); κ without W7160385925; Fleiss κ over the grade categories as recorded (faithful-vs-not also reported); unanimous share; the §8b design rule; majority-of-3 (3 distinct → L1); `evaluate()` returning one §8 row (validity → G1 → G2 → G3, else the catch-all); `round1_pairs()` with s5_analysis_A2.py's pairing rule.
- Known-answer tests: 28/28 PASS (`test_analysis_r11.py`): κ = 1 for perfect agreement, 0 for an independent table, 4/9 for a prevalence-skewed table (hand arithmetic in a comment), undefined at p_e = 1; Wilson 169/190 → [0.8369463492139949, 0.9265642065471013]; round 1's κ = 0.494 recomputed from round 1's files (80 pairs; equal to the committed 0.49420442571127504, per arm too); bootstrap constants, deterministic, changes with the seed, resamples papers (replicates ⊂ {-1, 0, 1} on a two-paper fixture), same rng convention as round 1, CI = the 2.5 / 97.5 percentiles, perfect-agreement CI [1, 1], the without-W716 subset; Fleiss 67/112, -0.2 and 8/33 (hand arithmetic in comments), perfect = 1, a single category undefined; repeatability summary and design rule at 0.8 / 0.7999 / None; majority-of-3; every §8 row reachable, ≥ at each boundary, void precedence for each flag, catch-all for missing, NaN or wrong-total inputs, and row text equal to the pre-reg table.
- Mutations:
  - AM1, G1 on point κ instead of the lower bound: KILLED
  - AM2, void ignored: KILLED
  - AM3, void evaluated after the G1-missing check: KILLED
  - AM4, bootstrap resamples claims, not papers: KILLED
  - AM5, G2 threshold 16 of 20: KILLED
  - AM6, Fleiss P_e as uniform 1/k: KILLED
  - AM7, Wilson z = 1.96: KILLED
  - AM8, missing G3 read as a G3 fail (catch-all bypassed): KILLED
  - AM9, percentile interval 5 / 95 instead of 2.5 / 97.5: KILLED. It first SURVIVED: no test pinned the percentile levels, so `test_bootstrap_ci_is_2_5_and_97_5_percentiles` was added (checked against the replicates and a hand linear-interpolation percentile).
  - AM10, Cohen p_e drops the both-not term: KILLED
- Method: each mutant is a single string edit on a copy of `r1.1/` in a temporary `run1/_mut_<id>/` directory, run with `python3 -I -B test_<component>.py` (non-zero exit = KILLED); the copies and the driver were deleted after the run.

## Foreman verification (qbp-architecture), builder commit 6889eed58dd2b014934d9c8cf7bfc4e16e71ad0e
- **Integrity:** harness `--verify` OK before and after. The commit was read by object id in the foreman's own worktree. It descends from ca3ca43 and only **adds** files; COMPONENT-RESULTS.md is append-only.
- **Re-run through the harness at that oid:** sampler 8/8, capture 19/19, router 15/15, analysis 28/28 PASS.
- **Independent foreman probes** (each paired with a passing control):
  - F1: G2 needs 18 → KILLED
  - F2: doubt accepts any type → KILLED
  - F3: bar 0.5 → KILLED
  - F4: seed changed → KILLED
- **Method lesson:** a same-size mutant written in the same second as its restore can make Python reuse stale `__pycache__` bytecode. That produced a false control FAIL until the run used `-B` and cleared the cache. Mutation runs should use `python3 -I -B` in fresh directories.
## router.py, revision 2 (pre-reg §5 r4)
- Changes: an L2 impasse now carries `disputes`, one label from each L2 party. Two equal labels are used as they are, and **disagreeing labels resolve to `rule-meaning`** (skip L3 → L4). A missing, unknown, single or extra label still raises. **L3 `undecided` on an `application` dispute now routes to L4** (the path keeps L3, so it still counts against the L3 budget). Every other L3 outcome still raises. A rule-meaning item with any L3 record still raises.
- Known-answer tests: 19/19 PASS (`test_router.py`). The 15 earlier tests were updated to the two-label form. Four tests are new: disagreeing labels (both orders) → L4, with an L3 record rejected; missing or bad labels raise (incl. the old single-label form); L3 undecided → L4, then L4 ruled → settled and L4 impasse → L5, and it counts toward the budget at 31; the other L3 paths are unchanged.
- Mutations (`__pycache__` cleared per mutant copy, run with `python3 -I -B`):
  - RM1–RM6, re-run on the revised router: all KILLED
  - RN1, label disagreement resolved as application: KILLED
  - RN2, label disagreement resolved as the first label: KILLED
  - RN3, L3 undecided still raises: KILLED
  - RN4, missing or unknown label accepted: KILLED
  - RN5, a single label accepted: KILLED
  - RN6, L3 undecided settles at the verifier grade: KILLED
- No first-survivors.

## Foreman verification (qbp-architecture), builder commit 52d024cd0ff0bdeb0a6b1337683e4fa203c3daee (router rev 2)
- **Integrity:** harness `--verify` OK. The commit was read by oid; its parent is 6889eed. The diff covers router.py, test_router.py, and an append to this log.
- **Re-run through the harness at that oid:** sampler 8/8, capture 19/19, router 19/19, analysis 28/28 PASS.
- **Foreman probes** (each with a passing control):
  - F5: L3 budget 35 → KILLED
  - F6: over-budget uses `>=` → KILLED
- **Integrated** by cherry-pick (this log had appends on both sides; both kept).
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

## Gate 2 (contextus-impl), §I4 APPROVE by qbp-architecture at abce440a91dceae36eec3aff31804c091d98d422
- `relation-types-v1.yaml` edc8fd5fcd35d254c716c1f094503727ca4306b50d974884d3bc67eb578e8d13
- `relation-types-v1.json` f0e2ca9d71b13516bc8ca3ab8f68a41ac8831accc06a5b215ad6b55573f4ad89
- **`relation-rubric-v1.txt` f950c385c016e8c0b23b6e8e8941d0448fcb049a31eb7fa404f3ed7f1b4eed23** (the pinned rubric for round 1.1)
- **Tests:** registry 18/18, validator 28/28.
- **Reviewer mutants:**
  - deleting one signed sentence (×2): KILLED
  - one word altered: KILLED
  - guard C: KILLED
  - guard D: KILLED
- **Director spot-checks against the committed rubric:** the `proves`→`has-property` sentence, the "Result" definition, the ⋃ example and the sub-object rule are each present exactly once; `main()` canonicalises.
