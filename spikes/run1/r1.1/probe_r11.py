#!/usr/bin/env python3
"""Round 1.1 §8b repeatability probe analysis (pre-reg §8b). Read-only over committed raw runs.

Per rater: distinct grades per claim, unanimous-claim share, Fleiss' kappa across the runs,
doubt-flag stability, per-run token spread (four-field sum), and the pre-stated design rule
(kappa < 0.8 -> majority of 3 for that rater).
"""
import json
import sys
from collections import Counter
from pathlib import Path

GRADES = ["faithful", "wrong-relation", "wrong-direction", "wrong-modality", "wrong-locator", "not-in-paper"]
THRESHOLD = 0.8


def fleiss_kappa(table):
    """table: list of per-subject category-count lists, each row summing to the same n."""
    N = len(table)
    n = sum(table[0])
    if N == 0 or n < 2 or any(sum(r) != n for r in table):
        raise ValueError("every subject needs the same number (>=2) of ratings")
    k = len(table[0])
    p = [sum(r[j] for r in table) / (N * n) for j in range(k)]
    P_i = [(sum(c * c for c in r) - n) / (n * (n - 1)) for r in table]
    P_bar = sum(P_i) / N
    P_e = sum(x * x for x in p)
    if P_e == 1.0:
        return None  # undefined: a single category used throughout
    return (P_bar - P_e) / (1 - P_e)


def parse_run(path):
    rows = {}
    for line in Path(path).read_text().splitlines():
        if line.strip() == "GRADES-END":
            break
        o = json.loads(line)
        if "n" in o:
            if o["n"] in rows or o["grade"] not in GRADES:
                raise ValueError(f"{path}: duplicate n or bad grade at n={o.get('n')}")
            rows[o["n"]] = o
    return rows


def analyse(runs, tokens=None):
    ns = sorted(runs[0])
    if any(sorted(r) != ns for r in runs):
        raise ValueError("runs cover different claim sets")
    table, per_claim = [], {}
    for n in ns:
        gs = [r[n]["grade"] for r in runs]
        ds = [bool(r[n]["doubt"]) for r in runs]
        c = Counter(gs)
        table.append([c[g] for g in GRADES])
        per_claim[n] = {"grades": gs, "distinct": len(c), "doubts": sum(ds)}
    kappa = fleiss_kappa(table)
    out = {
        "runs": len(runs),
        "claims": len(ns),
        "fleiss_kappa": kappa,
        "unanimous_share": sum(1 for v in per_claim.values() if v["distinct"] == 1) / len(ns),
        "disagreeing_claims": {n: v["grades"] for n, v in per_claim.items() if v["distinct"] > 1},
        "doubt_unstable_claims": {n: v["doubts"] for n, v in per_claim.items() if 0 < v["doubts"] < len(runs)},
        "doubt_always_claims": [n for n, v in per_claim.items() if v["doubts"] == len(runs)],
        "rule": None if kappa is None else ("single runs stand" if kappa >= THRESHOLD else "majority of 3"),
    }
    if tokens:
        out["tokens_per_run"] = tokens
        out["tokens_min_max"] = [min(tokens), max(tokens)]
    return out


def main(argv):
    d = Path(argv[1])
    paths = sorted(d.glob("run*.out"))
    runs = [parse_run(p) for p in paths]
    toks = []
    for p in paths:
        m = p.with_name(p.name.replace(".out", ".meta.json"))
        toks.append(json.loads(m.read_text())["sum_all"] if m.exists() else None)
    print(json.dumps(analyse(runs, toks if all(t is not None for t in toks) else None), indent=1, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
