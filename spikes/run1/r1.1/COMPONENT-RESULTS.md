# Round 1.1 component results

## sampler.py (pre-reg §4, §8b)
- Known-answer tests: 8/8 PASS (`test_sampler.py`): counts 387/62/325, deterministic twice, 6 per paper and 120 total (C1 cap), never contaminated, 60/60 split disjoint and complete, probe excludes W7160385925 (across 200 seeds), seed changes the draw.
- Mutations:
  - M1, contamination filter removed: KILLED
  - M2, unseeded RNG: KILLED
  - M3, 7 per paper: KILLED
  - M4, probe allows W7160385925: KILLED. It first SURVIVED: a single seed missed W716 by chance, so the test was strengthened to 200 seeds.

## relation_registry_gen.py + relation_validator.py (pre-reg gate 2, inter#300 O4)
Registry source: `spikes/run1/vocab/relation-types-v1.yaml`, generated from and
checked against `relation-definitions-v1-SIGNED.md` (sha256 `ea3f245e…f2d4`).
Generated projections, both committed and pinned: `relation-types-v1.json`
(sha256 `7a2b2bba…c305`) and `relation-rubric-v1.txt` (sha256 `c2699513…d89b`,
first line `RUBRIC-ID: relation-types-v1 source_sha256=ea3f245e…f2d4
registry_sha256=0b789395…e12`). The rubric sha is now available to pin gate 3
(verifier-v1) and gate 4 (checker_v1)'s `--rubric-sha`.

- **Known-answer tests, `test_relation_registry_gen.py`: 10/10 PASS.** Exactly
  the 10 signed type ids in signed order; registry's claimed source sha
  matches the real signed file; schema-complete (no type missing a required
  field); `meaning`/`direction`/`admissibility_test`/`boundary` are all real
  substrings of the signed doc (not a second source of truth); JSON and
  rubric generation are each deterministic across two runs and match their
  pinned shas; the rubric's first line parses as `RUBRIC-ID: …`; `cites` is
  rejected, never listed as a type.
- **Known-answer tests, `test_relation_validator.py`: 16/16 PASS.** Accepts a
  plain registered type, a `proposed:<name>` placeholder, a well-formed
  n-ary `depends-on` tail, and an allowed `equivalent-to` sense. Rejects
  `cites`, an unregistered bare type id, an invalid modality, an empty
  `depends-on` tail, a tail member missing `kind`, a disallowed `sense`, and
  a claim missing a required field. `canonicalize_claim` rewrites
  `specialises(A,B)` to `generalises(B,A)` and stores `equivalent-to` in
  sorted canonical order, and leaves other claims untouched. The
  has-property guard does not trip at exactly 30% and does trip at 40%
  (review flag only, never a hard gate, per the signed doc's "Settled at
  signing" item (ii)).
- **Mutations, each applied, confirmed KILLED, then reverted:**
  - M1, the `cites`-rejection branch removed: KILLED.
  - M2, the unknown-bare-type-id rejection removed (silently accepts any
    string as a relation): KILLED.
  - M3, `canonicalize_claim`'s `equivalent-to` sort removed: KILLED.

**Scope note:** this component validates claim *shape* mechanically
(required fields, known/`proposed:` type ids, modality enum, `depends-on`
tail structure, `equivalent-to` sense enum, the two mechanical rewrites).
It does not and cannot judge the admissibility test against the paper's own
text — that stays the verifier/checker's job (gates 3/4), never this one's.
