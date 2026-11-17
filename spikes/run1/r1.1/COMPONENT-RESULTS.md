# Round 1.1 component results

## sampler.py (pre-reg §4, §8b)
- Known-answer tests: 8/8 PASS (`test_sampler.py`): counts 387/62/325, deterministic twice, 6 per paper and 120 total (C1 cap), never contaminated, 60/60 split disjoint and complete, probe excludes W7160385925 (across 200 seeds), seed changes the draw.
- Mutations:
  - M1, contamination filter removed: KILLED
  - M2, unseeded RNG: KILLED
  - M3, 7 per paper: KILLED
  - M4, probe allows W7160385925: KILLED. It first SURVIVED: a single seed missed W716 by chance, so the test was strengthened to 200 seeds.
