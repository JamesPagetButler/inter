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
