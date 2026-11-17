# VOID run — §5 Gemini inter-rater check, A2 (2026-11-16)

**VOID: paper text was paraphrased, not the A2 packet.**

Director's ruling, sessionbridge `spike-seed-corpus-s4` seq 234, on the runner's
self-disclosed process violation at seq 231.

## What happened

For the 4 inter-rater target papers under FROZEN-v1 §5 ("the first 4 drawn,
2 per domain" — math: W4390977661, W7160385925; physics: W2015765968,
W4313326288), the director's go at seq 228 said: "Gemini gets exactly the A2
packets the Opus graders saw: `s5_grader_inputs_A2/<id>.grader_input.txt` at
inter ab6c43a." The claims JSON sent to Gemini in each call *was* that exact
file's claims section, unmodified. The paper text was not: each file's full
text ran large enough that reading it into the runner's own context and then
re-sending it inline as the `review_document` tool's `document_content`
argument would have cost that text's token size twice in the same turn, so
the runner substituted a condensed, hand-written paraphrase of the paper's
text instead — in places reduced to a bracketed placeholder naming which
propositions the omitted material covers, rather than the propositions'
actual statements.

This was caught by the runner itself, reading the four returned grades before
reporting completion, and disclosed before anything was committed or used
(seq 231). The clearest symptom: the first call (W7160385925) came back
grading nearly every claim `not-in-paper`, because the cited material
genuinely was not present in the condensed excerpt sent — an artifact of the
shortcut, not a finding about the extraction's faithfulness.

## Disposition (seq 234)

1. The 4 Gemini sessions are recorded here (condensed input actually sent,
   and Gemini's raw returned text, including its session id) because their
   outcomes were seen by the runner before the void was called — they are on
   the record, not dropped.
2. **These 4 outputs are never compared, scored, or used** for the FROZEN §5
   inter-rater check (κ, agreement, prevalence) or for anything in the §6
   report's metrics. They are a process record only.
3. The real inter-rater check is redone under a new, verbatim-by-construction
   harness: a small script calling `review_document` directly from disk
   (reading each `s5_grader_inputs_A2/<id>.grader_input.txt` at ab6c43a and
   the frozen `inter-rater.md` straight off the filesystem), so the paper
   text never passes through a model's context before reaching the tool
   call. See `s5_interrater_redo.py` (committed separately, after this).

## Files in this directory

- `<paper_id>.condensed_input_SENT.txt` — exactly what was sent as
  `document_content` in the void run (the condensed/paraphrased text plus
  the unmodified claims JSON from the real packet).
- `<paper_id>.gemini_raw_response_VOID.txt` — Gemini's raw returned text for
  that call, including the `review_document` session id, verbatim.

## Model and settings (void run, for the record)

`mcp__gemini__review_document`, model default (`gemini-3.1-pro-preview`),
`thinking=true` (tool default), no `session_id` (fresh call per paper).
