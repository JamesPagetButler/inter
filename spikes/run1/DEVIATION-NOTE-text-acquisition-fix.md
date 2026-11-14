# Deviation note: text-acquisition parser fix (disclosed implementation fix, not a rule change)

Per qbp-architecture's ruling on `spike-seed-corpus-s4#82`: the equation-scanner
+ arXiv-search + OA-fallback parser fix (Builder A2, `8fa6290`/`432d049`) is a
**disclosed implementation fix** to how §2.5's frozen text inputs are
obtained, not a change to which papers are selected or any threshold. Made
before any extraction output existed. Approved with three conditions, all
satisfied below.

## What changed

`text_cache_manifest.jsonl` was regenerated once, in place, replacing the 48
rows that were `status: text-unavailable` under the original parser with the
real result of running the merged `process_paper()` (equation scanning +
arXiv title/author search + OA fallback) against those same 48 papers. The
51 rows that were already `status: ok` under the original parser were left
untouched (no re-fetch).

## The 51 → 61 shift

| | math | physics | total |
|---|---|---|---|
| original manifest (old parser) | 38/50 ok | 13/49 ok | 51/99 ok |
| regenerated manifest (new parser) | 40/50 ok | 21/49 ok | 61/99 ok |

Physics is the thin side (21/49), not math (40/50) — math and physics were
both misreported backwards in-session (seq 80/81) before this recount.

Of the 10 newly-recovered papers: 8 physics, 2 math. 6 of the 8 physics
recoveries came from the equation scanner finding hundreds of statements
(up to 281) where the old parser found zero. 2 of the 10 (both math) came
through the new OA-fallback path, not ar5iv.

Of the 38 still `text-unavailable`: 35/38 never resolved an arXiv id at all
(even with the title/author search fallback) — 22 of those also have no
usable OA location, 13 have an OA location but zero statements via the
generic scan. The remaining 3 resolved an arXiv id and fetched ar5iv
successfully but the parser found zero statements in the body. Zero of the
38 failed because the ar5iv fetch itself errored.

Full per-paper detail: `real_coverage_results.jsonl` (the 48 rows, as run
under `cap-e824bdcb`).

## Manifest shas (condition 1)

- Code commit: `432d049` (merge of Builder A2's `8fa6290` into
  `contextus-impl/seed-corpus-patternb`).
- Original manifest (old parser, 51 ok): `cfed430721ab770f6192a9cc7bc59aee635b385aa63490bf47da6760eaf32982`
- Regenerated manifest (new parser, 61 ok): `2205acee781747f0acdc9ca5606600fce1d514da37e6895e61b98048dc397b8a`

## §8 finding (unrelated to this fix, recorded by the architect on seq 82)

99 papers selected (math 50, physics 49), not 100 — the frozen §8
"fan-out < 100" outcome. Not a reason to relax the guard (§2.3a); recorded
as a finding, not a change.

## Condition 3

No further text-acquisition changes after §4 starts. This regeneration is
the last one before §4 resumes.
