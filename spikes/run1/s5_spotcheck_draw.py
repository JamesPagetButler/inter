#!/usr/bin/env python3
"""contextus-seed-corpus round 1 -- Section 5 domain-owner spot-check draw.

FROZEN-v1 §5 line 85: "@qbp-oppenheimer re-grades 50 graded claims drawn by
PCG from the haiku arm (25 per domain), from the same inputs the grader saw,
blind to the grader's verdict." Director's go, sessionbridge
spike-seed-corpus-s4 seq 228/230, matching oppenheimer's conditions at
seq 227(3)(a): a fresh default_rng(250125) (seq 196 already ruled a new
seed after freeze is a rule change -- this stays on the one frozen seed),
population = the haiku (primary) arm's packet claims across the 20 graded
papers, sorted by (domain, paper_id, packet claim n), drawing 25 per domain,
math then physics, in one continuous pass, no reseed.

This reads the sealed arm key (s5_arm_key_A2_SEALED.json) only to find which
packet claim numbers are primary-arm, per paper. It never opens or tallies
any grade file, and its output carries no arm label and no verdict -- only
(paper_id, packet claim n) pairs, so the drawn claims can be looked up in
the (already-blind) grading packets without anyone seeing which arm they
came from or what the grader said about them.
"""
import json
from pathlib import Path

import numpy as np

SEED = 250125
RUN1 = Path(__file__).parent
ARM_KEY_PATH = RUN1 / "s5_arm_key_A2_SEALED.json"
OUT_PATH = RUN1 / "s5_spotcheck_draw.json"


def main():
    arm_key = json.load(open(ARM_KEY_PATH))

    # population[domain] = sorted list of (paper_id, n) for primary-arm claims
    population = {"math": [], "physics": []}
    for pid in arm_key["order"]:
        paper = arm_key["papers"][pid]
        domain = paper["domain"]
        for c in paper["claims"]:
            if c["arm"] == "primary":
                population[domain].append((pid, c["n"]))

    for domain in ("math", "physics"):
        population[domain].sort(key=lambda pair: (pair[0], pair[1]))

    rng = np.random.default_rng(SEED)

    drawn = {}
    for domain in ("math", "physics"):  # one continuous pass, no reseed
        pool = population[domain]
        idx = sorted(rng.choice(len(pool), size=25, replace=False).tolist())
        drawn[domain] = [list(pool[i]) for i in idx]

    out = {
        "seed": SEED,
        "generator": "numpy.random.default_rng (PCG64)",
        "population_sizes": {d: len(population[d]) for d in population},
        "drawn": drawn,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"wrote {sum(len(v) for v in drawn.values())} draws to {OUT_PATH}")


if __name__ == "__main__":
    main()
