#!/usr/bin/env python3
"""Round 1.1 sampler (pre-reg §4 and §8b). Deterministic and read-only over committed inputs.

draw(seed) returns:
  probe_paper   one paper for the §8b repeatability probe (W7160385925 excluded)
  double_graded 6 headline claims per paper (the C1 set), sorted
  calibration / heldout   a 60/60 split of double_graded
The headline pool is every graded claim except the contaminated set: the 50 spot-check
claims plus the 12 Gemini-disagreement RCA items.
"""
import json
import sys
from pathlib import Path

import numpy as np

RUN1 = Path(__file__).resolve().parent.parent
SEED = 251117
PER_PAPER = 6
EXCLUDE_PROBE = "W7160385925"


def load_inputs(run1=RUN1):
    key = json.loads((run1 / "s5_arm_key_A2_SEALED.json").read_text())
    claims = sorted((p, c["n"]) for p in key["order"] for c in key["papers"][p]["claims"])
    spot = {(v["paper"], v["n"]) for v in map(json.loads, (run1 / "s5_spotcheck_A2/oppenheimer_spotcheck_verdicts.jsonl").read_text().splitlines()) if v}
    rca = [json.loads(l) for l in (run1 / "rca/rca_items.jsonl").read_text().splitlines() if l.strip()]
    gem = {(i["paper"], i["n"]) for i in rca if i["source"] == "gemini"}
    return claims, spot | gem


def draw(claims, contaminated, seed=SEED, per_paper=PER_PAPER):
    rng = np.random.default_rng(seed)
    papers = sorted({p for p, _ in claims})
    probe_pool = [p for p in papers if p != EXCLUDE_PROBE]
    probe = probe_pool[int(rng.integers(len(probe_pool)))]
    headline = [c for c in claims if c not in contaminated]
    dg = []
    for p in papers:
        pool = [c for c in headline if c[0] == p]
        if len(pool) < per_paper:
            raise ValueError(f"{p}: only {len(pool)} headline claims")
        idx = rng.choice(len(pool), size=per_paper, replace=False)
        dg += [pool[i] for i in sorted(idx)]
    dg.sort()
    perm = rng.permutation(len(dg))
    half = len(dg) // 2
    cal = sorted(dg[i] for i in perm[:half])
    held = sorted(dg[i] for i in perm[half:])
    return {"seed": seed, "probe_paper": probe, "double_graded": dg, "calibration": cal, "heldout": held}


def main():
    claims, cont = load_inputs()
    out = draw(claims, cont)
    js = json.dumps({k: (v if not isinstance(v, list) else [list(x) for x in v]) for k, v in out.items()}, indent=1, sort_keys=True)
    sys.stdout.write(js + "\n")


if __name__ == "__main__":
    main()
