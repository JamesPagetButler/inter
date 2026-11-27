# §8b probe, checker half: result (director's analysis)

The raw runs were committed by contextus-spike at inter `3577576` (`spikes/run1/s5_r1.1_probe/checker/`, driver `7d775dc`) before any analysis. All 5 requests are byte-identical (request sha `eb27988b…076c`), finish_reason is STOP on all 5, and none was safety-blocked.

## Finding F-0b-1: 3 of the 5 answers are wrapped in a markdown code fence
Runs 1–3 (run_index 1, 2, 3) open with a ```` ```json ```` line and close with a ```` ``` ```` line after `GRADES-END`. The frozen shared parser `parse_grade_lines` (checker_v1.py) rejects all three: the opening fence is "not JSON", and the closing fence is "content after GRADES-END". At that rate, about 60% of the 1.1 checker calls would be void. **This needs a signed amendment (4) before the 1.1 run.** The proposed rule is mechanical: if the first non-blank line is exactly ```` ```json ```` or ```` ``` ```` and the last non-blank line is exactly ```` ``` ````, drop exactly those two lines before parsing. Nothing else is normalised, and the number of de-fenced answers is counted and reported.

## Self-agreement (computed on de-fenced copies; conditional on amendment 4)
- **Fleiss' κ across the 5 runs: 0.882.** That is ≥ 0.8, so by the pre-stated rule **the checker's single runs stand.**
- Unanimous-claim share: 18/20 (0.90). Claim 3 splits faithful ×4, wrong-modality ×1. Claim 6 splits wrong-relation ×4, faithful ×1.
- The checker output has no doubt flag, so doubt stability does not apply.
- Tokens per call (Gemini usage_metadata): prompt 16,209; thoughts 3,854–5,008; candidates 890–1,472; cached content missing on runs 0–1 and 14,158 on runs 2–4 (implicit caching).

## Gate 0b outcome (both halves)
Verifier κ 0.932 (`32ddcc6`) and checker κ 0.882: **single runs for both raters; majority-of-3 is not triggered.** No top-up request.
Open before freeze: amendment 4, covering the verifier stop (all 5 verifier runs exceeded 65k), the driver re-pin `ea3fed7`→`7d775dc`, and the fence rule F-0b-1.
