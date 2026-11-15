#!/usr/bin/env python3
"""contextus-seed-corpus round 1 -- Section 5 sample draw.

FROZEN-v1 line 81: "Sample: 20 papers (10 per domain), drawn by PCG seed
250125 from the papers with status `extracted`."

Procedure (disclosed for reproducibility -- the spec names the seed and
the generator family but not a library call, so this is the one chosen):
1. Population = the openalex_ids with status "ok" in
   text_cache_manifest.jsonl (61; every one of them went through
   extraction in the Section 4 run -- "extracted" and "ok" coincide here).
2. Each id's domain comes from corpus_construct_output.json's
   selected_final (math 40, physics 21).
3. Each domain's population is sorted ascending by openalex_id string --
   a fixed, file-order-independent sequence -- before any draw.
4. One numpy.random.default_rng(250125) (PCG64, numpy's standard "PCG")
   draws without replacement: 10 from the sorted math population first,
   then 10 from the sorted physics population, continuing the same
   generator state (no reseed between domains).
"""
import json
import numpy as np

CORPUS = "corpus_construct_output.json"
MANIFEST = "text_cache_manifest.jsonl"
SEED = 250125


def main():
    corpus = json.load(open(CORPUS))
    domains = {p["openalex_id"].rsplit("/", 1)[-1]: p["domain"]
               for p in corpus["selected_final"]}

    manifest_rows = [json.loads(l) for l in open(MANIFEST) if l.strip()]
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
