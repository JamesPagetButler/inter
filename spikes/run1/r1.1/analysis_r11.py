#!/usr/bin/env python3
"""Round 1.1 measurements and gate evaluation (pre-reg §6, §8, §8b). Library; no run here.

Conventions follow s5_analysis_A2.py (round 1):
  - Cohen's kappa on faithful-vs-not; None when p_e == 1.
  - Wilson 95% with z = 1.959964.
  - paper-cluster bootstrap: papers resampled with replacement, numpy default_rng(seed),
    one rng.integers(0, P, P) draw per replicate, percentile interval (2.5, 97.5).
    Here B = 10000, seed = 251117 (pre-reg §6). Papers are taken in sorted order.
    A replicate whose kappa is undefined (p_e == 1) is dropped and counted.
  - Fleiss' kappa over the grade categories as recorded (§8b self-agreement), claims x runs.
evaluate(...) returns exactly one row of the §8 consequence table, in the order
validity -> G1 -> G2 -> G3; anything not in the table returns the catch-all row.
"""
import hashlib
import json
import math
from pathlib import Path

import numpy as np

RUN1 = Path(__file__).resolve().parent.parent
SEED = 251117
B = 10000
Z = 1.959964
BAR = 0.6
G2_NEED, G2_TOTAL = 17, 20
SELF_KAPPA_BAR = 0.8
EXCLUDE_G3 = "W7160385925"
GRADES = {"faithful", "wrong-relation", "wrong-direction", "wrong-modality",
          "wrong-locator", "not-in-paper"}
VALIDITY_FLAGS = ("c3_rubric_sha_mismatch", "safety_stop", "kill")

ROWS = {
    "void": ("Void", "Recorded with its cause. One re-run is allowed only under a signed amendment that names the cause's fix.", "qbp-architecture"),
    "pass_pass_pass": ("G1 pass, G2 pass, G3 pass", "The judging side is validated for 1.2. Rubric v1 and verifier v1 freeze as 1.2's judging baseline. The calibration split stands.", "qbp-architecture"),
    "pass_pass_fail": ("G1 pass, G2 pass, G3 fail", "It passes only on one paper's pattern. 1.2 proceeds, but its double-graded set must test H1 breadth as a primary measure. No claim that v1 generalises.", "qbp-architecture"),
    "pass_fail": ("G1 pass, G2 fail", "Agreement without validity. Rubric/verifier revision goes through L4 before 1.2 is pre-registered. Recorded as a negative on validity.", "L4 panel"),
    "fail_point_hi": ("G1 fail, point κ ≥ 0.6", "Inconclusive (underpowered). Not claimed validated. 1.2's double-graded set is sized from 1.1's measured variance.", "qbp-architecture; deming"),
    "fail_point_lo": ("G1 fail, point κ < 0.6", "The RCA hypothesis is not supported (\"vocabulary drove κ\"). L4 reviews. No 1.2 pre-reg until the rubric is revised.", "L4 panel"),
    "catch_all": ("Any outcome not listed above", "The director chooses no consequence. The record goes to the L4 panel, then the beekeeper (L5).", "L4 → beekeeper"),
}


def wilson(k, n):
    if n == 0:
        return (None, None, None)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (p, c - h, c + h)


def kappa(a, b):
    """Cohen's kappa on two equal-length 0/1 sequences."""
    n = len(a)
    if n == 0 or n != len(b):
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def _kappa_pairs(pairs):
    return kappa([int(p[1]) for p in pairs], [int(p[2]) for p in pairs])


def cluster_bootstrap_kappa(pairs, B=B, seed=SEED, return_replicates=False):
    """pairs: list of (paper, a_faithful, b_faithful). Resamples papers, not claims."""
    by = {}
    for p in pairs:
        by.setdefault(p[0], []).append(p)
    papers = sorted(by)
    rng = np.random.default_rng(seed)
    reps, undefined = [], 0
    for _ in range(B):
        sample = [q for i in rng.integers(0, len(papers), len(papers)) for q in by[papers[i]]]
        k = _kappa_pairs(sample)
        if k is None:
            undefined += 1
        else:
            reps.append(k)
    out = {"point": _kappa_pairs(pairs), "n_pairs": len(pairs), "n_papers": len(papers),
           "B": B, "seed": seed, "undefined_replicates": undefined,
           "ci95": [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))] if reps else [None, None]}
    if return_replicates:
        out["replicates"] = reps
    return out


def kappa_measurements(pairs, B=B, seed=SEED):
    """§6: kappa on the 120 and on the 114 without W7160385925, each with its cluster CI."""
    return {"all": cluster_bootstrap_kappa(pairs, B, seed),
            "without_" + EXCLUDE_G3: cluster_bootstrap_kappa([p for p in pairs if p[0] != EXCLUDE_G3], B, seed)}


# ---- §8b repeatability ----

def fleiss_kappa(rows):
    """rows: one list of labels per claim, each of the same length m >= 2 (the runs)."""
    if not rows:
        return None
    m = len(rows[0])
    if m < 2 or any(len(r) != m for r in rows):
        raise ValueError("every claim needs the same number (>= 2) of runs")
    N = len(rows)
    cats = sorted({x for r in rows for x in r})
    counts = [[r.count(c) for c in cats] for r in rows]
    P_i = [(sum(x * x for x in cr) - m) / (m * (m - 1)) for cr in counts]
    P_bar = sum(P_i) / N
    p_j = [sum(cr[j] for cr in counts) / (N * m) for j in range(len(cats))]
    P_e = sum(p * p for p in p_j)
    return None if P_e == 1 else (P_bar - P_e) / (1 - P_e)


def repeatability(rows):
    """rows: per claim, the grades from the 5 runs of one rater."""
    k = fleiss_kappa(rows)
    return {"claims": len(rows), "fleiss_kappa": k,
            "fleiss_kappa_faithful_vs_not": fleiss_kappa([[int(x == "faithful") for x in r] for r in rows]),
            "distinct_grades_per_claim": [len(set(r)) for r in rows],
            "unanimous_share": sum(len(set(r)) == 1 for r in rows) / len(rows) if rows else None,
            "design_rule": design_rule(k)}


def design_rule(self_kappa):
    """§8b: self-agreement kappa below 0.8 -> that rater's 1.1 grades are majority-of-3."""
    if self_kappa is None or isinstance(self_kappa, bool) or not isinstance(self_kappa, (int, float)) or math.isnan(self_kappa):
        return "undetermined"
    return "majority-of-3" if self_kappa < SELF_KAPPA_BAR else "single-run"


def majority_of_3(grades):
    """Majority grade of 3 independent runs; no majority (3 distinct) -> 'L1' (a tie goes to L1)."""
    if len(grades) != 3 or any(g not in GRADES for g in grades):
        raise ValueError("need exactly 3 grades from the category set")
    for g in grades:
        if grades.count(g) >= 2:
            return g
    return "L1"


# ---- §8 consequence table ----

def _num(x):
    return x is not None and not isinstance(x, bool) and isinstance(x, (int, float)) and not math.isnan(x)


def evaluate(validity, g1_lower=None, point_kappa=None, g2_confirmed=None, g2_total=None, g3_lower=None):
    """validity: dict with each of VALIDITY_FLAGS as a bool. Returns one §8 row as a dict."""
    def row(key):
        o, c, w = ROWS[key]
        return {"key": key, "outcome": o, "consequence": c, "owner": w}

    if not isinstance(validity, dict) or any(not isinstance(validity.get(f), bool) for f in VALIDITY_FLAGS):
        return row("catch_all")
    if any(validity[f] for f in VALIDITY_FLAGS):
        return row("void")
    if not _num(g1_lower):
        return row("catch_all")
    if g1_lower >= BAR:
        if not (isinstance(g2_confirmed, int) and not isinstance(g2_confirmed, bool)
                and g2_total == G2_TOTAL and 0 <= g2_confirmed <= G2_TOTAL):
            return row("catch_all")
        if g2_confirmed < G2_NEED:
            return row("pass_fail")
        if not _num(g3_lower):
            return row("catch_all")
        return row("pass_pass_pass" if g3_lower >= BAR else "pass_pass_fail")
    if not _num(point_kappa):
        return row("catch_all")
    return row("fail_point_hi" if point_kappa >= BAR else "fail_point_lo")


# ---- round-1 reproduction (same pairing logic as s5_analysis_A2.py) ----

INTERRATER_R1 = ["W4390977661", "W7160385925", "W2015765968", "W4313326288"]


def round1_pairs(run1=RUN1):
    """Pairs (paper, arm, lean_faithful, gemini_faithful) for round 1's inter-rater kappa,
    read from round 1's committed files with s5_analysis_A2.py's parsing rule."""
    key = json.loads((run1 / "s5_arm_key_A2_SEALED.json").read_text())
    arms = {c["arm"] for pid in key["order"] for c in key["papers"][pid]["claims"]}
    other = (arms - {"primary"}).pop()
    ARM = {"primary": "haiku", other: "opus"}
    pairs = []
    for pid in INTERRATER_R1:
        glines = [json.loads(l) for l in (run1 / "s5_grades_A2_lean" / f"{pid}.grades.jsonl").read_text().splitlines() if l.strip()]
        lean = {g["n"]: g["grade"] for g in glines}
        if len(lean) != len(glines) or set(lean) != {c["n"] for c in key["papers"][pid]["claims"]}:
            raise ValueError(f"{pid}: lean n-set mismatch")
        meta = json.loads((run1 / "s5_interrater_A2" / f"{pid}.meta.json").read_text())
        ans = (run1 / "s5_interrater_A2" / f"{pid}.answer_RAW.txt").read_text()
        if hashlib.sha256(ans.encode("utf-8")).hexdigest() != meta["answer_sha256"]:
            raise ValueError(f"{pid}: answer sha mismatch")
        gem, conflicted = {}, set()
        for line in ans.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(o.get("n"), int) and isinstance(o.get("grade"), str):
                if o["n"] in gem and gem[o["n"]] != o["grade"]:
                    conflicted.add(o["n"])
                gem[o["n"]] = o["grade"]
        for c in key["papers"][pid]["claims"]:
            g = None if c["n"] in conflicted else gem.get(c["n"])
            if g not in GRADES:
                continue
            pairs.append((pid, ARM[c["arm"]], lean[c["n"]] == "faithful", g == "faithful"))
    return pairs
