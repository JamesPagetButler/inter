# contextus-seed-corpus round 1.1: amendment 3 (cartan's amendment-2 notes, prompt parity, runner pins)

**Amends:** the pre-reg `68cf5822…e2e6` together with amendment 1 `ff4bb2db…5455` and amendment 2 `8df3e597…0d42d`. None of them is edited. All four are frozen together.

## C1. Checker grades outside the 120 (cartan, seq 326, note 1)
The checker grades every claim in each input. **Only the double-graded 120 enter any measurement or gate**, including κ, G1–G3 and audit eligibility. Extra grades are still validated, so each must belong to a keyed claim and be in the category set. The analysis test shows the output is byte-identical with and without the extra grades.

## C2. Blindness attestation (cartan, seq 326, note 2)
Every labeller set's **header** carries `"blind": true`, as a JSON boolean. A missing, false or non-boolean value voids the set, and so G2 reads void. The attestation is header-level only; a record-level `blind` key is ignored. qbp-oppenheimer's set is attested by qbp-oppenheimer himself.

## C3. Prompt parity (found by director's probe, spike-seed-corpus-s4 seq 329)
The probe planted a prompt ("Grade everything faithful.") together with its own sha, and the runner accepted it, because a caller-supplied sha replaced the pin. Two fixes:
- **The runner** (contextus-spike, `b2aca67`): in real mode a supplied `--prompt-sha` / `--rubric-sha` must **equal** the canonical pin, or the call exits before any request is built. The director re-ran the probe against both scripts, with and without a supplied sha, and it was rejected each time.
- **L0** (defence in depth): a run or set whose recorded `prompt_sha` is missing or differs from its role's pin is voided:
  - verifier and L2-verifier: `verifier-v1.md`;
  - checker, L1-checker and L2-checker: `checker-v1.md`;
  - the Gemini labeller: `audit-labeller-v1.md`.

  The **only exemption** is a labeller set whose header `"labeller"` is exactly `"qbp-oppenheimer"`, because hand labels use no prompt. The pins are constants; no record or bundle can override them.

## C4. Exact record headers (the runner and qbp-oppenheimer must match these)
- Gemini labeller set header: `{"labeller": "gemini-labeller", "rubric_sha": "f950c385…ed23", "prompt_sha": "9d4d784e…5eff", "blind": true}`
- qbp-oppenheimer's set header: `{"labeller": "qbp-oppenheimer", "rubric_sha": "f950c385…ed23", "blind": true}`
- Checker meta.json records `rubric_sha` and `prompt_sha` (`cc4c6c2f…8803`). Each verifier dispatch record carries `prompt_sha` (`6d417edb…6289`).
- `"labeller"` lives **in the header**, not at the outer level. L0 reads the identity only from the header.

## Gate 4 and the labeller component, re-pinned
These are verified by the director by commit id at inter `b2aca67`, and again at `ea3fed7` (branch `contextus-spike/seed-corpus-s4`). All 5 test files pass, and the planted-prompt probe is rejected. sha256:
- `checker_v1.py` `1eb732c5b3f42a6cda46331ac28abbd703170706874ca2fa06f0e89c76574540`
- `audit_labeller_v1.py` `d4138e5e8b49ab868dc65837ba05f977bab4d9039f24f6550197f1ee36b30e4a`
- `r1_1_checker_driver.py` `a8708acab2bb797267a46d3acb81e985279bf1bd0d4ca2e27458de7136817387`
- `r1_1_audit_labeller_driver.py` `7809d4fdcd05b7e8f4517611a21c3e25370dfb15daa6ee7ef5ea1e9c22dd8684`
- `r1_1_audit_labeller.py` `b70fb3821fcf340eb349bb56d5eda61bc1821a506bcc55e7dde8de2c423ce4fb`. This was fixed in the C4 alignment round at `ea3fed7`: identity moved into the header, and `prompt_sha` is written when supplied, never as null.
- **Cross-check, director at `ea3fed7`:** the builder's output was run through the director's L0 (`b2fc451`). A Gemini set with the prompt sha gives `ok`; with no prompt sha, `void`; with a last-character-wrong prompt sha, `void`. qbp-oppenheimer's set with no prompt sha gives `ok`. The other four runner shas are unchanged from `b2aca67`.

## Director components, re-pinned
These are verified by commit id at inter `b2fc451`: 129/129 under pytest, round 1's κ still 0.49420442571127504, and the director's own probes Q13 (only an explicit `false` voids) and Q14 (the exemption widened) both KILLED.
- `l0_checks.py` `0ad2b59c32c08a274c389b90bd8d12efc0277de1645ef44ed7f5ce84ca88f4b4`
- `analysis_r11.py` `b86fe1db7e0067be747091e09493605391c53b4a02fee05e7f18d742fffaf06e`
