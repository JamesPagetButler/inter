---
name: qbp-implementor-wisdoms
owner: qbp-implementor
type: wisdom-set
scope: persona-local (inherits inter/wisdoms/_federation.md)
refined: 2026-11-01 (first entry; #803 version-only re-stamp + #804/#805 hand-off, live-test seq4296/4317)
---

# qbp-implementor — Wisdoms (role-distinctive)

> **Inherits all of `inter/wisdoms/_federation.md`.** Below are only the wisdoms distinctive to the
> **QBP integration seat** — the provenance-hygiene cut that the shared set doesn't carry. The
> physics-sign cut is qbp-oppenheimer's; this seat's judgment is process rigor, not the physics call.

## The integration seat's principles
- **Edit the CTH ledger only through the confined writer** (`scripts/cth_ledger_edit.py` `ledger_edit`
  context manager): the encoder declares every record it touches, and on exit the writer *proves*
  only-those-changed, that each declared record actually changed (a silent no-op is a finding, not a
  success), and that the untouched file round-trips byte-identical. Never hand-edit the ledger JSON or
  rewrite it blind. *Applied:* every anchor mint/edit this seat lands (encoders `encode_697…`,
  `encode_464_phasec…`, `encode_797_hyp…` all go through `ledger_edit`).
- **Mint the anchor before the run, discharge it after — never fold both into one round or one PR.**
  A contested hypothesis anchor is minted first and left contested; its discharge waits for the
  director's verdict on the run, in a later PR. *Applied:* the #797/#799 overeager-fold (2026-11-01) —
  a round-3 falsified discharge got pushed into the mint PR before the director ruled; the beekeeper
  rule is mint-contested-first, discharge-after, never the same round.
- **An anchor mint carries no inline `source_sha` or `proof_assistants` — those are notary-layer,
  derived from an `evidence_ref` that doesn't exist pre-notarisation.** Mint in the #697 shape
  (`verification`/`theorems[]`/`prediction_chain`, `pa_local`/`pa_effective` = 0/0); the import-closure
  manifest + PA grade arrive via the notary path post-mint, even on a theory→PROOF upgrade. *Applied:*
  cth seq3942 correcting its own seq3938, which had conflated mint-shape with post-notarisation shape.
- **Never silently carry a review sign-off across an undeclared byte change — re-request review the
  moment anything beyond the declared byte-set moves.** A §I4 carries ONLY on the exact clean path it
  was signed against; any ledger-merge conflict → resolve mechanically + re-request, stated on the PR.
  *Applied:* #803 (2026-11-01) version-only re-stamp — the architect/cth/director §I4 carried only for
  {version field + changelog + regenerated audit md/json `Generated:` line}; a single Lean byte would
  have voided two carries, so it was deferred.
- **Hand a finished PR to the driving director, not to the beekeeper directly; and template the
  Linked-Issue(s) `Closes #N` block + tick the satisfied ACs from the moment the PR is opened** —
  never vague "Part of #N" prose, never ticks deferred "until sign-offs land." `Tracks #N` only when
  legs remain. *Applied:* oppenheimer seq4296 after #804/#805, where "Part of #465/#657" + deferred
  ticks forced the director to add the `Closes` keyword and tick the ACs himself.
- **A spike's recompute must be a committed script, and when a prediction misses you run the post-hoc
  scan rather than write the mechanism excuse.** As runner: two phases (accept/build/test, then run),
  raw files never read by the runner, all shas posted together before any analysis; the independent
  recompute reproduces the plots as a committed script, not a heredoc. *Applied:* qbp-kz-g2 round 1
  (2026-10-30), P5 — the "seed-mean smears single-seed jumps" excuse was refuted by the per-seed scan.
