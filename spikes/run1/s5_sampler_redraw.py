#!/usr/bin/env python3
"""contextus-seed-corpus round 1 -- Section 5 REDRAW after amendment A2.

FROZEN-v1 line 81 (unchanged by A2): "Sample: 20 papers (10 per domain),
drawn by PCG seed 250125 from the papers with status `extracted`."

A2's walk-down grew the accessible population from 61 to 100 (50 math /
50 physics). Per the director (spike-seed-corpus-s4 seq 185) and oppenheimer's
S1 edit, the §5 sample is redrawn from the full 100 before any new Opus
call -- the pre-amendment packets/key at the old HEAD are not reused.

Procedure (identical to the original s5_sampler.py, domain lookup extended
to cover the A2 walk-down admissions):
1. Population = the openalex_ids with status "ok" in
   text_cache_manifest.jsonl (100 -- every one went through haiku
   restatement+extraction in the amended Section 4 run).
2. Each id's domain comes from s4_corpus_manifest_100.json (built from
   corpus_construct_output.json's selected_final for the original 61,
   plus walkdown_log.jsonl's candidate_tried records for the 39 A2
   admissions).
3. Each domain's population is sorted ascending by openalex_id string --
   a fixed, file-order-independent sequence -- before any draw.
4. One numpy.random.default_rng(250125) (PCG64, numpy's standard "PCG")
   draws without replacement: 10 from the sorted math population first,
   then 10 from the sorted physics population, continuing the same
   generator state (no reseed between domains). Same seed, same order,
   same generator as the original S1 draw -- only the population changed.
"""
import json
import numpy as np

CORPUS_MANIFEST = "s4_corpus_manifest_100.json"
TEXT_MANIFEST = "text_cache_manifest.jsonl"
SEED = 250125


def main():
    mani = json.load(open(CORPUS_MANIFEST))
    domains = {}
    for pid in mani["math"]:
        domains[pid] = "math"
    for pid in mani["physics"]:
        domains[pid] = "physics"

    manifest_rows = [json.loads(l) for l in open(TEXT_MANIFEST) if l.strip()]
    ok_ids = [r["openalex_id"].rsplit("/", 1)[-1] for r in manifest_rows
              if r["status"] == "ok"]

    by_domain = {"math": [], "physics": []}
    for pid in ok_ids:
        by_domain[domains[pid]].append(pid)
    for d in by_domain:
        by_domain[d].sort()

    rng = np.random.default_rng(SEED)
    drawn = {}
    for d in ("math", "physics"):
        pop = by_domain[d]
        idx = rng.choice(len(pop), size=10, replace=False)
        drawn[d] = sorted(pop[i] for i in idx)

    out = {
        "seed": SEED,
        "generator": "numpy.random.default_rng (PCG64)",
        "population_sizes": {d: len(by_domain[d]) for d in by_domain},
        "drawn": drawn,
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
