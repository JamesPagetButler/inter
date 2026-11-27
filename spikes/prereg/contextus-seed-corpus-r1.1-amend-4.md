# contextus-seed-corpus round 1.1: amendment 4 (gate-0b probe outcome, token units and stops, fence rule, runner re-pin)

**Amends:** the pre-reg `68cf5822…e2e6` together with amendment 1 `ff4bb2db…5455`, amendment 2 `8df3e597…0d42d` and amendment 3 `5937d1e3…f2bf`. None of them is edited. All five are frozen together.

**Disclosure for the beekeeper (cartan, gate 8, seq 349):** the Gemini unit correction (D3) was **found after the probe**. It is what makes the 1.1 run fit under the **unchanged** 1.65M Gemini kill line. **Under the pre-registered four-field unit, the worst case was 2.33M, over the line**; under the corrected unit it is 1.45M. Both sums are recorded for every call, so the old unit can still be computed.

**Why now:** the §8b repeatability probe (gate 0b) ran inside the base grant on 2026-11-27. The probe is there to find exactly these issues before the 1.1 run. Every change below comes from committed probe data, and each section names its source. **No outcome threshold (κ line, G1–G3, the 0.8 design rule, the kill lines) moves.**

## D1. Gate 0b outcome (pre-reg §8b, applied)
- Verifier v1: 5 fresh runs on W7168273025. Raw outputs at inter `d5ec623`, analysis at `32ddcc6`. **Fleiss' κ 0.932**, 19/20 unanimous.
- Checker v1: 5 fresh runs. Raw outputs at inter `3577576` (contextus-spike), analysis at `a09fe02`. **Fleiss' κ 0.882** on de-fenced copies (see D4), 18/20 unanimous.
- Both are ≥ 0.8. By the pre-stated rule, **the 1.1 grades are single runs for both raters**, and majority-of-3 is not triggered. No top-up request.
- Probe code: `r1.1/probe_r11.py` `d025402b696b1191bc098f5bdd500d461dfc1d675c55639de518e89ad4900351`, with `test_probe_r11.py` `62ebdbf1c7f4890c5d3abac6579ba280eea5e54f3d0dc9370a9684af9d9e898c`. Known-answer controls: Wikipedia's Fleiss example gives 0.2099 against 0.210. Mutants KILLED 3/3.

## D2. Verifier stop and the Opus line (A3 re-set per §10; deming, seq 346)
- All 5 probe runs exceeded the 65k per-verifier stop: 79,534 / 80,171 / 83,005 / 82,838 / 82,709, in the four-field unit. Each run is 2 API calls. 22,752 of each total is the first call's cached context, read again by the second call.
- **The new per-run stop is 95k, and it is hard:** a run that reaches it aborts that paper, which is recorded and never retried.
- **The Opus kill line stays at 2.25M** (1.5 × the 1.5M base) and is **enforced cumulatively**. No new paper starts if cumulative Opus spend + 95k > 2.25M; the shortfall is recorded, with no partial-paper overrun. **A checkpoint at paper 10:** if cumulative run spend, excluding the probe, is over 0.90M, pause and post a re-cost before paper 11.
- The Opus unit stays four-field (A-A5): the Anthropic input fields are disjoint.

## D3. Gemini unit correction (A-A5; deming, seq 348)
- **Primary source** (Gemini API reference, `UsageMetadata` under `GenerateContentResponse`, https://aistudio.google.com/api-reference/generate-content#Resource:GenerateContentResponse, redirected from https://ai.google.dev/api/generate-content, retrieved 2026-11-27):
  - `promptTokenCount`: "Number of tokens in the prompt. When `cached_content` is set, this is still the total effective prompt size meaning this includes the number of tokens in the cached content."
  - `cachedContentTokenCount`: "Number of tokens in the cached part of the prompt (the cached content)".
  - `totalTokenCount`: "Total token count for the generation request (prompt + tool-use prompt + thoughts + response candidates)". There is no cached term.
- **Corroboration from the committed probe** (inter `3577576`):
  - `prompt_token_count` is 16,209 on all 5 runs, both when `cached_content_token_count` is missing (runs 0–1) and when it is 14,158 (runs 2–4).
  - The API's own `total_token_count` equals prompt + thoughts + candidates exactly on all 5 calls (21,361 / 22,430 / 21,186 / 22,107 / 21,458; tool-use prompt 0). The four-field sum is 14,158 higher on each cached call.
  - So on Gemini the cached count is a subset of the prompt count, and the four-field sum counted those tokens twice.
- **The Gemini unit becomes three-field:** `prompt_token_count + thoughts_token_count + candidates_token_count`. `cached_content_token_count` is recorded per call but not summed. **Both sums, four-field and three-field, are reported in the record for every call.**
- Worst case for the 1.1 run (≤ 60 calls × the probe maximum, plus the probe): **1.45M three-field** (2.33M under the old four-field sum).
- **The Gemini kill line stays at 1.65M** (1.5 × the 1.1M base), enforced cumulatively as in D2: no new call if cumulative + the per-call worst case > 1.65M, plus a checkpoint at paper 10 against the pro-rata base.

## D4. Fenced answers (finding F-0b-1, director, seq 344)
- 3 of the 5 checker answers (run_index 1–3) were wrapped in ```` ```json ```` … ```` ``` ````. The frozen shared parser `parse_grade_lines` rejects them: the opening fence is "not JSON", and the closing fence is "content after GRADES-END".
- **Rule:** before parsing, if the first non-blank line is exactly ```` ```json ```` or ```` ``` ```` **and** the last non-blank line is exactly ```` ``` ````, drop exactly those two lines. Nothing else is normalised. A fence at one end only, any other language tag, a fence inside the grade block, or text before the opening fence is still rejected. Each de-fenced answer is flagged (`defenced: true`), and the count is reported.
- The rule lives in the shared parser, so it applies to the checker and the audit labeller alike (amendment 2 B1: one parser).
- Fence lines are matched after trimming surrounding whitespace (`.strip()`). That is the only leniency.
- Implemented by contextus-spike at inter `7de7151` (seq 352). The director verified it by commit id: the 3 real fenced probe answers parse to the same grades as their de-fenced copies; the 5 rejection shapes are refused with the guard's own reason; and the both-ends mutant is KILLED. `parse_grade_lines` now returns `(grades, defenced)`, and every caller is updated. The final pins are in **Runner re-pin** below.

## D5. Checker driver re-pin (live-fire finding, contextus-spike, seq 343)
- On the first live call, `execute_plan()` spawned the checker with `sys.executable`, which lacks `google-genai`. The fix at `7d775dc` points it at the Gemini MCP venv's own interpreter (run with `-I`), with a loud guard if that interpreter is missing. The director read the diff: it changes the interpreter only, and the command arguments are unchanged. `checker_v1.py` is unchanged (`1eb732c5…4540`).
- Folding in D6 found the **same interpreter bug in the audit-labeller driver**. It is fixed at `70907e3` by reusing the checker driver's interpreter and guard functions, not reimplementing them.

## D6. Cumulative Gemini token guard (runner; director seq 350, 351, 355, 357)
- Before building each request, the checker and labeller drivers call one shared `check_gemini_token_budget`. If the cumulative three-field spend + 25k per-call worst case > the budget (default **1.65M**), the driver stops with a named SystemExit.
- **Scope is all of round 1.1:** the guard sums every Gemini meta under `spikes/run1/s5_r1.1_*/` (probe, checker, L1, labeller), and a run directory outside that root is refused. Probe metas written before the guard existed are counted from their `usage_metadata`. A meta that declares a non-Gemini `rater` (the Opus verifier's, `opus-verifier-v1`) is skipped. A meta with no `rater` and no Gemini usage is rejected loudly.
- Verified by the director at `4448e85`, with the director's own verifier metas (inter `d0bdf96`) in place. Cumulative spend over the real root: **three-field 108,542, four-field 151,016**, which equals the probe. All 5 runner suites pass under boxrun. Mutants KILLED: zeroed spend, scope back to a single dir, and ignoring every meta that has a rater.
- Every Gemini meta records the 4 usage fields and both sums (`usage`, `usage_sums`).
- **The Opus guard (D2)** is enforced by the director on verifier dispatches, from each run's recorded four-field usage.

## Runner re-pin (supersedes amendment 3's runner pins)
Verified by the director by commit id at inter `4448e85` (branch `contextus-spike/seed-corpus-s4`). sha256:
- `checker_v1.py` `5f2997e15f2e87ab6f36d386197994b3b61e6ebaa09b5a996cc7e736290d0eb5` (was `1eb732c5…4540`; request and hash construction unchanged)
- `audit_labeller_v1.py` `44ea1e312c27d21a4073c679e3b8e0c4dcfaee3b8cdeb089590f72bdd63040d0` (was `d4138e5e…0e4a`)
- `r1_1_checker_driver.py` `16eb82f667b898b818c9f373b35076fe224066994d94e2b4e4073de288e95c5b` (was `a8708aca…7387`)
- `r1_1_audit_labeller_driver.py` `e2eb8a916310f9eb577d50ef911c3893f02374bd331270601462d464df2c982a` (was `7809d4fd…8684`)
- `r1_1_audit_labeller.py` `b70fb3821fcf340eb349bb56d5eda61bc1821a506bcc55e7dde8de2c423ce4fb` (unchanged)
- Tests: `checker_v1_test.py` `323c5e81…bcad`, `r1_1_checker_driver_test.py` `2e2d8c4c…8b23`, `r1_1_audit_labeller_driver_test.py` `e7e63db3…094e`.
- Director's probe record: `s5_r1.1_probe/verifier/SHA256SUMS` at inter `d0bdf96`, sha `2deb5ab4…9074` (metas tagged with `rater`; the raw `.out` files are unchanged from `d5ec623`).

## Sign-offs required before freeze
Director (qbp-architecture); cartan (gate-8 re-check, including the D3 unit text); deming (gate 7: D2/D3 and box safety unchanged); contextus-impl (registry owner: confirms the rubric and registry are untouched).
