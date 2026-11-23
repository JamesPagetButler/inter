# Relation vocabulary for extracted claims

**Status: v1, design-proposal (napkin).** The design surface is inter#300. This is the shared vocabulary that the extractor, every grader and the hypergraph use for claims extracted from papers (`subject` / `relation_type` / `object` / `modality` / `locator`). It exists because round 1 of the seed-corpus spike left every relation undefined, and that was the main cause of grader disagreement (inter#300, RCA H1).

## Versions

| Version | Role | Status |
|---|---|---|
| **v1** (`v1/`) | baseline for round 1.1 of the seed-corpus spike | 10 definitions signed by qbp-oppenheimer (rev 3, 2026-11-17) |
| v2 | baseline for round 2: v1 refined from the round 1.1 report | not yet written |

**How versions are made** (beekeeper direction, 2026-11-23). Each version is fixed before the round that uses it, and that round runs against its pinned shas. The next version is refined from that round's final report, through fix rounds on this PR, and becomes the baseline for the next round. A version is never edited in place once a round has run on it. A refinement is a new `vN/` directory, and the change log below says what changed and which round's evidence drove it.

## v1 files (copied byte for byte from inter `abce440`, branch `contextus-impl/seed-corpus-r11-gate2`)

| File | What it is | sha256 |
|---|---|---|
| `relation-definitions-v1-SIGNED.md` | **The source of truth.** Six-part definitions (meaning, kinds, direction, admissibility test, examples plus a near-miss, boundary) for the 10 relation types | `ea3f245e3794afbf11c2759459a44aab3a52ab90b49716f80f3ddd9420e0f2d4` |
| `relation-types-v1.yaml` | Mechanical facts only: arity, symmetry, sense values, tail kinds, canonical rewrites, the has-property guard. It holds no prose copy of the definitions | `edc8fd5fcd35d254c716c1f094503727ca4306b50d974884d3bc67eb578e8d13` |
| `relation-types-v1.json` | Generated canonical projection of the registry | `f0e2ca9d71b13516bc8ca3ab8f68a41ac8831accc06a5b215ad6b55573f4ad89` |
| `relation-rubric-v1.txt` | Generated rubric given to every rater. Each signed section is sliced byte-exact from the signed doc | `f950c385c016e8c0b23b6e8e8941d0448fcb049a31eb7fa404f3ed7f1b4eed23` |

The YAML's `source_file` names the spike-branch path, because that is where the generator ran. The shas above are what a round pins.

**The 10 types:** `proves`, `has-property`, `defines`, `depends-on` (n-ary), `generalises` (`specialises` is rewritten to it), `equivalent-to`, `subobject-of`, `counterexample-to`, `conjectures`, `uses-technique`. **Modality is never a relation:** `cites` is rejected.

**What stays on the spike branch** (spike rule 1): the generator, the validator and their tests. They are spike code. These files are their output, plus the signed source. The §I4 on gate 2 is inter#300 issuecomment-7108287804.

## Known open items (to be decided by round 1.1 data, not guessed)
- The has-property "dumping ground" threshold (~30%) is a review flag only, never a gate (settled-at-signing ii).
- `quote` becomes a required field in the round 1.2 extraction schema, not in 1.1.
- An external-declaration object kind (a Mathlib name plus a commit pin) for `equivalent-to` / `specialises`, raised on inter#300 for inter#317. This is a D1 question for edda-implementor.
- Physics relations (`predicts`, `constrains`, `measures`) are inter#300 Q2 and not yet in the vocabulary.

## Change log
- **v1** (2026-11-17, signed). Starts from round 1's nine relations. It adds `has-property` and `subobject-of`, removes `cites` (a modality), and turns the six RCA rules (R-defines, R-proves, R-depends-on, R-vocab, R-locator, R-specialises) into admissibility tests. Evidence: the round-1 RCA, `spikes/run1/rca/RCA-SUMMARY.md` at inter `d13cd9c`.
