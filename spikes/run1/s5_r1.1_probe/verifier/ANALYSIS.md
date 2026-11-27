# §8b probe, verifier half: result

- Runs: 5 fresh corpus-verifier-v1 runs on W7168273025 (20 claims), identical dispatch bytes. Raw outputs committed first, at `d5ec623`.
- **Fleiss' κ across the 5 runs: 0.932.** That is ≥ 0.8, so by the pre-stated rule **the verifier's single runs stand.**
- Unanimous-claim share: 19/20 (0.95). One claim splits: claim 6, wrong-relation ×3 and faithful ×2. It is doubted in all 5 runs.
- Doubt-flag stability: claim 5 is doubted in 4 of 5 runs; claims 10 and 15 in 1 of 5 each; claim 6 in 5 of 5. The other 16 are never doubted.
- P4 friction: all 5 runs name the same two frictions: the "Theorem 1.1 (Corollary 5.2)" restatement and "defines" inside Proposition 4.7. Runs 2 and 3 also raise dropped hypotheses (claims 15 and 10).
- **Tokens per run, four-field sum: 79,534 / 80,171 / 83,005 / 82,838 / 82,709.** Each run is 2 API calls; 22,752 of each total is the first call's cached context, read again by the second call. **All 5 exceed the 65k per-verifier stop (A3).** Per §10, the stop is re-set by signed amendment before the 20-paper run.
- Code: `r1.1/probe_r11.py`, with `test_probe_r11.py` as the known-answer controls (the Wikipedia Fleiss example gives 0.2099 against 0.210; perfect agreement 1; undefined when only one category is used). Mutants KILLED 3/3: P_e formula, threshold, P_i denominator. Run under boxrun.
