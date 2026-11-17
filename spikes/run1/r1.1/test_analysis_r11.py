"""Known-answer tests for analysis_r11.py (pre-reg §6, §8, §8a "Analysis script", §8b). Run: python3 -I test_analysis_r11.py"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analysis_r11 as A  # noqa: E402

OK = {"c3_rubric_sha_mismatch": False, "safety_stop": False, "kill": False}


def close(x, y, tol=1e-12):
    return x is not None and abs(x - y) <= tol


# ---- Cohen's kappa ----

def test_kappa_perfect_agreement_is_1():
    a = [1, 0, 1, 1, 0, 0, 1]
    assert close(A.kappa(a, a), 1.0)


def test_kappa_independent_is_0():
    # 2x2 table with every cell 25: po = 0.5, pa = pb = 0.5, pe = 0.5 -> kappa = 0
    a = [1] * 25 + [1] * 25 + [0] * 25 + [0] * 25
    b = [1] * 25 + [0] * 25 + [1] * 25 + [0] * 25
    assert close(A.kappa(a, b), 0.0)


def test_kappa_prevalence_skewed_by_hand():
    # n = 100: both faithful 85, a-only 5, b-only 5, both not 5.
    # po = 90/100 = 0.90; pa = pb = 0.90; pe = 0.9*0.9 + 0.1*0.1 = 0.82
    # kappa = (0.90 - 0.82) / (1 - 0.82) = 0.08 / 0.18 = 4/9 = 0.4444...
    a = [1] * 85 + [1] * 5 + [0] * 5 + [0] * 5
    b = [1] * 85 + [0] * 5 + [1] * 5 + [0] * 5
    assert close(A.kappa(a, b), 4 / 9)


def test_kappa_undefined_when_pe_is_1():
    assert A.kappa([1, 1, 1], [1, 1, 1]) is None


# ---- Wilson ----

def test_wilson_reproduces_round1_haiku_precision():
    res = json.loads((A.RUN1 / "s5_analysis_A2_results.json").read_text())["arms"]["haiku"]
    assert (res["faithful"], res["graded"]) == (169, 190)
    p, lo, hi = A.wilson(169, 190)
    assert close(lo, 0.8369463492139949) and close(hi, 0.9265642065471013)
    assert close(lo, res["wilson95"][0]) and close(hi, res["wilson95"][1])
    assert A.Z == 1.959964


# ---- round 1 reproduction ----

def test_reproduces_round1_kappa_0494_from_committed_files():
    pairs = A.round1_pairs()
    assert len(pairs) == 80
    k = A.kappa([int(p[2]) for p in pairs], [int(p[3]) for p in pairs])
    assert round(k, 3) == 0.494
    committed = json.loads((A.RUN1 / "s5_analysis_A2_results.json").read_text())["inter_rater"]["overall"]["kappa"]
    assert close(k, committed)
    for arm in ("haiku", "opus"):
        sub = [p for p in pairs if p[1] == arm]
        want = json.loads((A.RUN1 / "s5_analysis_A2_results.json").read_text())["inter_rater"]["per_arm"][arm]["kappa"]
        assert close(A.kappa([int(p[2]) for p in sub], [int(p[3]) for p in sub]), want)


# ---- cluster bootstrap ----

def _fixture():
    pairs = []
    for i, pid in enumerate(["P%02d" % j for j in range(8)]):
        for c in range(6):
            a = (c + i) % 3 != 0
            b = a if (c + 2 * i) % 5 else (not a)
            pairs.append((pid, a, b))
    return pairs


def test_bootstrap_constants():
    assert A.B == 10000 and A.SEED == 251117


def test_bootstrap_deterministic_for_fixed_seed():
    r1 = A.cluster_bootstrap_kappa(_fixture(), B=2000)
    r2 = A.cluster_bootstrap_kappa(_fixture(), B=2000)
    assert r1 == r2 and r1["seed"] == 251117


def test_bootstrap_changes_with_seed():
    # 8 small papers give a coarse kappa lattice, so the percentile CI can coincide across seeds;
    # the replicate stream itself must differ.
    r1 = A.cluster_bootstrap_kappa(_fixture(), B=2000, return_replicates=True)
    r2 = A.cluster_bootstrap_kappa(_fixture(), B=2000, seed=1, return_replicates=True)
    assert r1["replicates"] != r2["replicates"] and r2["seed"] == 1


def test_bootstrap_resamples_papers_not_claims():
    # Paper A agrees perfectly (kappa 1), paper B disagrees on every claim (kappa -1), each balanced 5/5.
    # Paper-level resampling of 2 papers gives only AA (1), AB/BA (0), BB (-1).
    A_ = [("A", True, True)] * 5 + [("A", False, False)] * 5
    B_ = [("B", True, False)] * 5 + [("B", False, True)] * 5
    r = A.cluster_bootstrap_kappa(A_ + B_, B=500, return_replicates=True)
    assert all(min(abs(k - v) for v in (-1.0, 0.0, 1.0)) < 1e-12 for k in r["replicates"])
    assert {round(k) for k in r["replicates"]} == {-1, 0, 1}
    assert close(r["point"], 0.0)


def test_bootstrap_uses_same_rng_draw_convention_as_round1():
    # replicate b uses rng.integers(0, P, P) on sorted papers, exactly as s5_analysis_A2.py
    import numpy as np
    pairs = _fixture()
    papers = sorted({p[0] for p in pairs})
    rng = np.random.default_rng(A.SEED)
    want = []
    for _ in range(50):
        s = [q for i in rng.integers(0, len(papers), len(papers)) for q in pairs if q[0] == papers[i]]
        want.append(A.kappa([int(q[1]) for q in s], [int(q[2]) for q in s]))
    got = A.cluster_bootstrap_kappa(pairs, B=50, return_replicates=True)["replicates"]
    assert all(close(x, y) for x, y in zip(got, want)) and len(got) == 50


def test_bootstrap_ci_is_2_5_and_97_5_percentiles():
    # Added after mutant AM9 (5/95 interval) first SURVIVED: pin the interval to the replicates.
    import numpy as np
    r = A.cluster_bootstrap_kappa(_fixture(), B=2000, return_replicates=True)
    reps = sorted(r["replicates"])
    assert r["ci95"] == [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))]
    # and the interval is not the 5/95 one on this fixture (so the check has teeth)
    assert r["ci95"] != [float(np.percentile(reps, 5)), float(np.percentile(reps, 95))]
    # linear-interpolation percentile by hand on a sorted list, index = q/100 * (n-1)
    def pct(q):
        h = q / 100 * (len(reps) - 1)
        lo = int(math.floor(h))
        return reps[lo] + (h - lo) * (reps[min(lo + 1, len(reps) - 1)] - reps[lo])
    assert close(r["ci95"][0], pct(2.5)) and close(r["ci95"][1], pct(97.5))


def test_bootstrap_perfect_agreement_ci_is_1_1():
    pairs = [("P%d" % i, c % 2 == 0, c % 2 == 0) for i in range(5) for c in range(4)]
    assert A.cluster_bootstrap_kappa(pairs, B=300)["ci95"] == [1.0, 1.0]


def test_kappa_measurements_without_w716():
    pairs = _fixture() + [("W7160385925", True, False), ("W7160385925", False, True)]
    m = A.kappa_measurements(pairs, B=200)
    assert m["all"]["n_papers"] == 9 and m["without_W7160385925"]["n_papers"] == 8
    assert m["without_W7160385925"]["n_pairs"] == len(_fixture())


# ---- Fleiss + §8b ----

def test_fleiss_hand_case_67_over_112():
    # N=3 claims, m=5 runs. Counts (F, WR): c1 (5,0), c2 (0,5), c3 (3,2).
    # P_i = (sum n_ij^2 - m) / (m(m-1)) = (sum sq - 5)/20: c1 = 20/20 = 1, c2 = 1, c3 = (9+4-5)/20 = 0.4
    # P_bar = 2.4/3 = 0.8. p_F = 8/15, p_WR = 7/15, P_e = (64 + 49)/225 = 113/225.
    # kappa = (180/225 - 113/225) / (112/225) = 67/112 = 0.598214...
    rows = [["faithful"] * 5, ["wrong-relation"] * 5, ["faithful"] * 3 + ["wrong-relation"] * 2]
    assert close(A.fleiss_kappa(rows), 67 / 112)


def test_fleiss_negative_hand_case():
    # c1 (3F,2W), c2 (2F,3W): P_i = (9+4-5)/20 = 0.4 each, P_bar = 0.4; p_F = p_W = 0.5, P_e = 0.5
    # kappa = (0.4 - 0.5)/0.5 = -0.2
    rows = [["faithful"] * 3 + ["not-in-paper"] * 2, ["faithful"] * 2 + ["not-in-paper"] * 3]
    assert close(A.fleiss_kappa(rows), -0.2)


def test_fleiss_three_categories_hand_case():
    # N=2, m=5. c1 (F4, WR1, NIP0), c2 (F0, WR2, NIP3)
    # P_1 = (16+1-5)/20 = 0.6; P_2 = (4+9-5)/20 = 0.4; P_bar = 0.5
    # p = (4/10, 3/10, 3/10); P_e = 0.16+0.09+0.09 = 0.34; kappa = (0.5-0.34)/0.66 = 0.16/0.66 = 8/33
    rows = [["faithful"] * 4 + ["wrong-relation"], ["wrong-relation"] * 2 + ["not-in-paper"] * 3]
    assert close(A.fleiss_kappa(rows), 8 / 33)


def test_fleiss_perfect_is_1_and_single_category_undefined():
    assert close(A.fleiss_kappa([["faithful"] * 5, ["wrong-relation"] * 5]), 1.0)
    assert A.fleiss_kappa([["faithful"] * 5] * 4) is None


def test_repeatability_summary_and_design_rule():
    rows = [["faithful"] * 5, ["wrong-relation"] * 5, ["faithful"] * 3 + ["wrong-relation"] * 2]
    r = A.repeatability(rows)
    assert r["distinct_grades_per_claim"] == [1, 1, 2]
    assert close(r["unanimous_share"], 2 / 3)
    assert r["design_rule"] == "majority-of-3"          # 67/112 < 0.8
    assert A.design_rule(0.8) == "single-run"
    assert A.design_rule(0.7999) == "majority-of-3"
    assert A.design_rule(None) == "undetermined"


def test_majority_of_3():
    assert A.majority_of_3(["faithful", "wrong-relation", "faithful"]) == "faithful"
    assert A.majority_of_3(["faithful", "wrong-relation", "not-in-paper"]) == "L1"


# ---- §8 table ----

def ev(**kw):
    base = dict(validity=OK, g1_lower=0.65, point_kappa=0.75, g2_confirmed=18, g2_total=20, g3_lower=0.62)
    base.update(kw)
    return A.evaluate(**base)["key"]


def test_row_pass_pass_pass():
    assert ev() == "pass_pass_pass"
    assert ev(g1_lower=0.6, g2_confirmed=17, g3_lower=0.6) == "pass_pass_pass"   # boundaries are >=


def test_row_pass_pass_fail():
    assert ev(g3_lower=0.59) == "pass_pass_fail"


def test_row_pass_fail():
    assert ev(g2_confirmed=16) == "pass_fail"
    assert ev(g2_confirmed=16, g3_lower=None) == "pass_fail"   # G3 not needed for this row


def test_row_g1_fail_point_high_uses_lower_bound_not_point():
    assert ev(g1_lower=0.59, point_kappa=0.75) == "fail_point_hi"
    assert ev(g1_lower=0.59, point_kappa=0.6) == "fail_point_hi"


def test_row_g1_fail_point_low():
    assert ev(g1_lower=0.3, point_kappa=0.59) == "fail_point_lo"
    assert ev(g1_lower=0.3, point_kappa=0.5, g2_confirmed=None) == "fail_point_lo"


def test_void_takes_precedence():
    for f in A.VALIDITY_FLAGS:
        v = dict(OK, **{f: True})
        assert ev(validity=v) == "void"
        assert ev(validity=v, g1_lower=None) == "void"
        assert ev(validity=v, g1_lower=0.3, point_kappa=0.2) == "void"


def test_catch_all_reachable():
    assert ev(validity={}) == "catch_all"
    assert ev(validity={"c3_rubric_sha_mismatch": False, "safety_stop": False}) == "catch_all"
    assert ev(g1_lower=None) == "catch_all"
    assert ev(g1_lower=float("nan")) == "catch_all"
    assert ev(g2_confirmed=None) == "catch_all"
    assert ev(g2_total=19) == "catch_all"
    assert ev(g3_lower=None) == "catch_all"
    assert ev(g1_lower=0.3, point_kappa=None) == "catch_all"


def test_every_row_reachable_and_text_matches_table():
    keys = {ev(validity=dict(OK, kill=True)), ev(), ev(g3_lower=0.1), ev(g2_confirmed=3),
            ev(g1_lower=0.5, point_kappa=0.7), ev(g1_lower=0.5, point_kappa=0.5), ev(g1_lower=None)}
    assert keys == set(A.ROWS)
    prereg = (A.RUN1.parent / "prereg" / "contextus-seed-corpus-r1.1-prereg-DRAFT.md").read_text().replace("**", "")
    for o, c, w in A.ROWS.values():
        assert f"| {o} | {c} | {w} |" in prereg, o


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print("PASS", name)
            except Exception as e:
                fails += 1
                print("FAIL", name, type(e).__name__, e)
    sys.exit(1 if fails else 0)
