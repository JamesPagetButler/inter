"""Known-answer tests for analysis_r11.py (pre-reg §6, §8, §8a).

Run: python3 -I test_analysis_r11.py   or   python3 -m pytest -q test_analysis_r11.py
(under boxrun: numpy, 1 core)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analysis_r11 as an  # noqa: E402
import sampler  # noqa: E402

RUN1 = HERE.parent


# ---------- Cohen's kappa known answers ----------

def test_kappa_exactly_one():
    assert an.kappa([1, 1, 0, 0, 1], [1, 1, 0, 0, 1]) == 1.0


def test_kappa_exactly_zero():
    # po = 0.5, pa = pb = 0.5 -> pe = 0.5 -> kappa = 0 exactly.
    assert an.kappa([1, 1, 0, 0], [1, 0, 1, 0]) == 0.0


def test_kappa_prevalence_skewed():
    # 100 items: both-faithful 85, a-only 5, b-only 5, both-not 5.
    # po = 0.90; pa = pb = 0.90; pe = 0.81 + 0.01 = 0.82; kappa = 0.08 / 0.18 = 4/9.
    a = [1] * 85 + [1] * 5 + [0] * 5 + [0] * 5
    b = [1] * 85 + [0] * 5 + [1] * 5 + [0] * 5
    k = an.kappa(a, b)
    assert abs(k - 4 / 9) < 1e-12, k
    blk = an.kblock(list(zip(a, b)))
    assert blk["raw_agreement"] == 0.9 and blk["prevalence"] == 0.9


def test_kappa_perfect_disagreement_and_undefined():
    assert an.kappa([1, 0, 1, 0], [0, 1, 0, 1]) == -1.0
    assert an.kappa([1, 1, 1], [1, 1, 1]) is None   # pe == 1: undefined, never reported as 1
    assert an.kappa([], []) is None


# ---------- Wilson against a hand-computed reference ----------

def test_wilson_reference_8_of_10():
    # Hand computation, z = 1.959964, z^2 = 3.841459:
    #   centre = (0.8 + z^2/20) / (1 + z^2/10) = 0.992073 / 1.384146 = 0.716740
    #   half   = z * sqrt(0.8*0.2/10 + z^2/400) / 1.384146 = 1.959964 * 0.160011 / 1.384146 = 0.226578
    #   -> [0.490162, 0.943318]  (textbook Wilson 95% for 8/10: 0.490, 0.943)
    p, lo, hi = an.wilson(8, 10)
    assert p == 0.8
    assert abs(lo - 0.490162) < 1e-6 and abs(hi - 0.943318) < 1e-6, (lo, hi)


def test_wilson_reference_0_of_10():
    # k = 0: lower = 0, upper = z^2 / (n + z^2) = 3.841459 / 13.841459 = 0.277533.
    p, lo, hi = an.wilson(0, 10)
    assert p == 0.0 and abs(lo) < 1e-12 and abs(hi - 0.277533) < 1e-6


def test_wilson_n0():
    assert an.wilson(0, 0) == (None, None, None)


# ---------- paper-cluster bootstrap on a fixture ----------

def _two_paper_fixture():
    A = [(1, 1)] * 5 + [(0, 0)] * 5                     # kappa(A) = 1
    Bp = [(1, 0)] * 5 + [(0, 1)] * 5                    # kappa(B) = -1
    return {"A": A, "B": Bp}
    # resamples: AA -> 1, BB -> -1, AB/BA -> 0 (po 0.5, pa = pb = 0.5): only {1, 0, -1} can occur


def test_cluster_bootstrap_resamples_whole_papers():
    bs = an.cluster_bootstrap_kappa(_two_paper_fixture(), B=4000, seed=7)
    assert set(bs["replicates"]) <= {1.0, 0.0, -1.0}, set(bs["replicates"]) - {1.0, 0.0, -1.0}
    # P(AA) = P(BB) = 1/4, P(mixed) = 1/2
    f = {v: bs["replicates"].count(v) / 4000 for v in (1.0, 0.0, -1.0)}
    assert abs(f[1.0] - 0.25) < 0.03 and abs(f[-1.0] - 0.25) < 0.03 and abs(f[0.0] - 0.5) < 0.03, f
    assert bs["ci95"] == [-1.0, 1.0] and bs["undefined"] == 0


def test_cluster_bootstrap_seeded_deterministic():
    fx = {"P%d" % i: [(1, 1), (0, 0), (1, 0), (1, 1)][: 2 + i % 3] for i in range(6)}
    a = an.cluster_bootstrap_kappa(fx, B=500, seed=251117)
    b = an.cluster_bootstrap_kappa(fx, B=500, seed=251117)
    c = an.cluster_bootstrap_kappa(fx, B=500, seed=1)
    assert json.dumps(a) == json.dumps(b)
    assert a["replicates"] != c["replicates"]


def test_cluster_bootstrap_counts_undefined():
    # Every paper is all-faithful on both sides except one; a resample without it is undefined.
    fx = {"X": [(1, 1)] * 3, "Y": [(1, 1)] * 3, "Z": [(0, 0), (1, 1)]}
    bs = an.cluster_bootstrap_kappa(fx, B=2000, seed=3)
    # P(no Z in 3 draws) = (2/3)^3 = 0.296
    assert abs(bs["undefined"] / 2000 - 8 / 27) < 0.04, bs["undefined"]
    assert len(bs["replicates"]) == 2000 - bs["undefined"]


def _hand_linear_percentile(sorted_vals, q):
    # Independent of numpy: the "linear" (type 7) rule. h = (N-1) q/100; interpolate r[floor h] .. r[floor h + 1].
    h = (len(sorted_vals) - 1) * q / 100
    lo = int(h)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (h - lo) * (sorted_vals[hi] - sorted_vals[lo])


def _varied_fixture():
    # 8 papers with different agreement patterns, so the replicate distribution is spread out and
    # its 2.5/5 and 95/97.5 percentiles differ (checked below, so the test can discriminate them).
    pats = [(1, 1), (0, 0), (1, 0), (0, 1)]
    return {"P%d" % i: [pats[(i * j + j // 2) % 4] for j in range(3 + i)] for i in range(8)}


def test_cluster_bootstrap_ci_endpoints_are_2_5_and_97_5():
    bs = an.cluster_bootstrap_kappa(_varied_fixture(), B=2000, seed=251117)
    r = sorted(bs["replicates"])
    lo, hi = _hand_linear_percentile(r, 2.5), _hand_linear_percentile(r, 97.5)
    # the fixture must separate the neighbouring percentiles, or this test proves nothing
    assert lo != _hand_linear_percentile(r, 5) and hi != _hand_linear_percentile(r, 95)
    assert lo < hi
    assert abs(bs["ci95"][0] - lo) < 1e-12 and abs(bs["ci95"][1] - hi) < 1e-12, (bs["ci95"], lo, hi)


def test_hand_percentile_known_values():
    # 0..100 in steps of 1 -> the q-th percentile is exactly q; 5 values [0,1,2,3,10]: 97.5 -> h = 3.9 -> 3 + 0.9*7 = 9.3
    vals = [float(i) for i in range(101)]
    assert _hand_linear_percentile(vals, 2.5) == 2.5 and _hand_linear_percentile(vals, 97.5) == 97.5
    assert abs(_hand_linear_percentile([0.0, 1.0, 2.0, 3.0, 10.0], 97.5) - 9.3) < 1e-12


def test_percentile_ci_hand_computed():
    # reps = i^2, i = 0..10 (N = 11), linear rule h = (N-1) q/100 = q/10:
    #   2.5  -> h = 0.25 -> 0  + 0.25*(1-0)    = 0.25   (nearest would give 0, the 5th pct 0.5)
    #   97.5 -> h = 9.75 -> 81 + 0.75*(100-81) = 95.25  (nearest would give 100, the 95th pct 90.5)
    reps = [float(i * i) for i in range(11)]
    assert an.percentile_ci(reps) == [0.25, 95.25]
    assert an.percentile_ci(list(reversed(reps))) == [0.25, 95.25]   # order-free
    assert an.percentile_ci([]) is None


def test_cluster_bootstrap_ci_is_percentile_ci_of_its_replicates():
    bs = an.cluster_bootstrap_kappa(_varied_fixture(), B=500, seed=5)
    assert bs["ci95"] == an.percentile_ci(bs["replicates"])


def _with_fixed_bootstrap(ci_by_n, fn, undefined_by_n=None, fake_B=None):
    # Monkeypatch the bootstrap so the decision sees a known interval and drop count; restored afterwards.
    orig = an.cluster_bootstrap_kappa

    def fake(by, B=an.B, seed=an.SEED):
        n = sum(len(v) for v in by.values())
        und = (undefined_by_n or {}).get(n, 0)
        return {"B": fake_B or B, "seed": seed, "undefined": und, "ci95": list(ci_by_n[n]), "replicates": []}
    an.cluster_bootstrap_kappa = fake
    try:
        return fn()
    finally:
        an.cluster_bootstrap_kappa = orig


def test_g1_reads_lower_bound_of_the_120_interval():
    # point kappa 1, interval [0.55, 0.90]: G1 must FAIL on the lower bound (inconclusive row).
    r = _with_fixed_bootstrap({120: (0.55, 0.90), 114: (0.7, 0.95)}, lambda: an.analyse(_bundle(), RUN1, B=10))
    assert r["decision"]["inputs"]["g1_lower_bound"] == 0.55
    assert r["decision"]["outcome"] == "G1 fail, point kappa >= 0.6"


def test_g3_reads_lower_bound_of_the_114_interval():
    r = _with_fixed_bootstrap({120: (0.7, 0.95), 114: (0.55, 0.90)}, lambda: an.analyse(_bundle(), RUN1, B=10))
    assert r["decision"]["inputs"]["g3_lower_bound"] == 0.55
    assert r["decision"]["outcome"] == "G1 pass, G2 pass, G3 fail"


# ---------- R6 (cartan gate 8): ceiling on dropped bootstrap replicates ----------

def test_drop_ceiling_boundary_is_strictly_more_than_1pct():
    assert an.drops_exceed_ceiling(100, 10000) is False      # exactly 1%: not inconclusive
    assert an.drops_exceed_ceiling(101, 10000) is True
    assert an.drops_exceed_ceiling(0, 10000) is False
    assert an.drops_exceed_ceiling(2, 200) is False and an.drops_exceed_ceiling(3, 200) is True


def test_bootstrap_block_reports_drop_count_and_rate():
    r = _with_fixed_bootstrap({120: (0.7, 0.9), 114: (0.7, 0.9)}, lambda: an.analyse(_bundle(), RUN1, B=10000),
                              undefined_by_n={120: 101, 114: 7}, fake_B=10000)
    b = r["kappa_120"]["bootstrap"]
    assert b["undefined"] == 101 and b["drop_rate"] == 0.0101 and b["drops_exceed_ceiling"] is True
    b = r["kappa_without_W7160385925"]["bootstrap"]
    assert b["undefined"] == 7 and b["drop_rate"] == 0.0007 and b["drops_exceed_ceiling"] is False


def test_g1_exactly_1pct_drops_still_decides():
    r = _with_fixed_bootstrap({120: (0.7, 0.9), 114: (0.7, 0.9)}, lambda: an.analyse(_bundle(), RUN1, B=10000),
                              undefined_by_n={120: 100, 114: 100}, fake_B=10000)
    assert r["decision"]["outcome"] == "G1 pass, G2 pass, G3 pass"


def test_g1_over_1pct_drops_reads_inconclusive_not_pass():
    r = _with_fixed_bootstrap({120: (0.7, 0.9), 114: (0.7, 0.9)}, lambda: an.analyse(_bundle(), RUN1, B=10000),
                              undefined_by_n={120: 101}, fake_B=10000)
    assert r["decision"]["outcome"] == "G1 inconclusive: bootstrap drops > 1% of B"
    assert r["decision"]["inputs"]["g1_inconclusive"] is True


def test_g1_over_1pct_drops_reads_inconclusive_not_fail():
    r = _with_fixed_bootstrap({120: (0.3, 0.5), 114: (0.7, 0.9)}, lambda: an.analyse(_bundle(), RUN1, B=10000),
                              undefined_by_n={120: 500}, fake_B=10000)
    assert r["decision"]["outcome"] == "G1 inconclusive: bootstrap drops > 1% of B"


def test_g3_over_1pct_drops_reads_inconclusive():
    r = _with_fixed_bootstrap({120: (0.7, 0.9), 114: (0.7, 0.9)}, lambda: an.analyse(_bundle(), RUN1, B=10000),
                              undefined_by_n={114: 101}, fake_B=10000)
    assert r["decision"]["outcome"] == "G1 pass, G2 pass, G3 inconclusive: bootstrap drops > 1% of B"


def test_decide_inconclusive_rows():
    D = an.decide
    assert D(False, 0.7, 0.7, True, 0.9, g1_inconclusive=True)["outcome"] == "G1 inconclusive: bootstrap drops > 1% of B"
    assert D(False, 0.4, 0.4, True, 0.9, g1_inconclusive=True)["owner"] == "L4 -> beekeeper"
    assert D(False, 0.7, 0.7, True, 0.4, g3_inconclusive=True)["outcome"].endswith("G3 inconclusive: bootstrap drops > 1% of B")
    assert D(False, 0.7, 0.7, False, 0.9, g3_inconclusive=True)["outcome"] == "G1 pass, G2 fail"   # G2 before G3
    assert D(True, 0.7, 0.7, True, 0.9, g1_inconclusive=True)["outcome"] == "void"


# ---------- R2 (cartan gate 8): audit-labeller rubric parity -> G2 void ----------

def test_g2_void_when_a_labeller_sha_mismatches():
    r = an.analyse(_bundle(b_sha="9" * 64), RUN1, B=200)
    assert r["audit"]["g2_pass"] == "void"
    assert r["audit"]["labeller_parity"]["labeller_b"]["status"] == "void"
    assert r["decision"]["outcome"] == "not listed: G2 void (audit labeller rubric parity)"
    assert r["decision"]["owner"] == "L4 -> beekeeper"


def test_g2_void_when_a_labeller_sha_is_missing():
    r = an.analyse(_bundle(b_sha=None), RUN1, B=200)
    assert r["audit"]["g2_pass"] == "void" and r["decision"]["outcome"].startswith("not listed: G2 void")
    r = an.analyse(_bundle(a_sha=None), RUN1, B=200)   # qbp-oppenheimer's hand labels too
    assert r["audit"]["labeller_parity"]["labeller_a"]["status"] == "void" and r["audit"]["g2_pass"] == "void"


def test_g2_void_with_otherwise_perfect_audit_is_not_pass():
    r = an.analyse(_bundle(a_sha="8" * 64, audit_confirmed=20), RUN1, B=200)
    assert r["audit"]["confirmed_by_both"] == 20 and r["audit"]["g2_pass"] == "void"
    assert r["decision"]["outcome"] == "not listed: G2 void (audit labeller rubric parity)"


def test_decide_g2_void_rows():
    D = an.decide
    assert D(False, 0.7, 0.7, "void", 0.9)["outcome"] == "not listed: G2 void (audit labeller rubric parity)"
    assert D(False, 0.5, 0.5, "void", 0.9)["outcome"] == "G1 fail, point kappa < 0.6"   # G1 decides first


def test_bundle_cannot_override_the_pinned_rubric_sha():
    b = _bundle(a_sha="7" * 64, b_sha="7" * 64)
    b["pinned_rubric_sha"] = "7" * 64
    assert an.analyse(b, RUN1, B=50)["audit"]["g2_pass"] == "void"


# ---------- round 1 reproduction ----------

def test_reproduces_round1_kappa_0494():
    r = an.reproduce_round1(RUN1)
    o = r["overall"]
    assert o["double_graded"] == 80
    assert round(o["kappa"], 3) == 0.494
    assert abs(o["kappa"] - 0.49420442571127504) < 1e-12, o["kappa"]
    assert o["raw_agreement"] == 0.85 and o["prevalence"] == 0.825
    assert abs(r["per_arm"]["haiku"]["kappa"] - 0.4791666666666669) < 1e-12
    assert abs(r["per_arm"]["opus"]["kappa"] - 0.5) < 1e-12
    assert r["unparsed"] == 0


def test_gemini_parse_rule_conflicting_duplicate_is_unparsed():
    ans = "\n".join(["```json", '{"n": 1, "grade": "faithful"}', '{"n": 2, "grade": "faithful"}',
                      '{"n": 2, "grade": "wrong-relation"}', '{"n": 3, "grade": "not-in-paper"}',
                      '{"n": 3, "grade": "not-in-paper"}', '{"n": "4", "grade": "faithful"}', "not json {", "```"])
    assert an.parse_gemini_answer(ans) == {1: "faithful", 2: None, 3: "not-in-paper"}


def test_round1_reproduction_matches_committed_results_file():
    committed = json.loads((RUN1 / "s5_analysis_A2_results.json").read_text())["inter_rater"]
    r = an.reproduce_round1(RUN1)
    assert r["overall"] == committed["overall"]
    assert r["per_arm"] == committed["per_arm"]


# ---------- §8 decision table ----------

def test_decide_every_row():
    D = an.decide
    assert D(void=True, g1_lb=0.9, g1_point=0.9, g2_pass=True, g3_lb=0.9)["outcome"] == "void"
    assert D(False, 0.6, 0.7, True, 0.6)["outcome"] == "G1 pass, G2 pass, G3 pass"
    assert D(False, 0.6, 0.7, True, 0.59)["outcome"] == "G1 pass, G2 pass, G3 fail"
    assert D(False, 0.6, 0.7, False, 0.9)["outcome"] == "G1 pass, G2 fail"
    assert D(False, 0.59, 0.6, True, 0.9)["outcome"] == "G1 fail, point kappa >= 0.6"
    assert D(False, 0.59, 0.5999, True, 0.9)["outcome"] == "G1 fail, point kappa < 0.6"
    # Not listed -> L4 then beekeeper; the director picks nothing.
    assert D(False, None, 0.7, True, 0.9)["outcome"] == "not listed"
    assert D(False, 0.7, 0.7, None, 0.9)["outcome"] == "not listed"
    assert D(False, 0.7, 0.7, True, None)["outcome"] == "not listed"
    assert D(False, 0.7, 0.7, True, 0.9)["owner"] == "qbp-architecture"
    assert D(False, 0.7, 0.7, True, None)["owner"] == "L4 -> beekeeper"


# ---------- full §6 analysis on a fixture bundle ----------

def _lean():
    out = {}
    for p in json.loads((RUN1 / "s5_arm_key_A2_SEALED.json").read_text())["order"]:
        out[p] = {g["n"]: g["grade"] for g in map(json.loads, (RUN1 / "s5_grades_A2_lean" / f"{p}.grades.jsonl").read_text().splitlines()) if g}
    return out


PIN = "f950c385c016e8c0b23b6e8e8941d0448fcb049a31eb7fa404f3ed7f1b4eed23"


def _bundle(checker_flip=False, audit_confirmed=20, doubt_every=10, a_sha=PIN, b_sha=PIN):
    lean = _lean()
    claims, cont = sampler.load_inputs(RUN1)
    draw = sampler.draw(claims, cont)
    ver = {p: {str(n): {"grade": g, "doubt": (n % doubt_every == 0)} for n, g in d.items()} for p, d in lean.items()}
    flip = {"faithful": "wrong-relation"}
    chk = {}
    for p, n in draw["double_graded"]:
        g = lean[p][n]
        chk.setdefault(p, {})[str(n)] = (flip.get(g, "faithful") if checker_flip else g)
    items = draw["double_graded"][:20] if not checker_flip else []
    audit = [{"paper": p, "n": n, "agreed_grade": lean[p][n]} for p, n in items]
    labellers = {
        "labeller_a": {"labeller": "qbp-oppenheimer", "header": {"rubric_sha": a_sha},
                       "records": [{"paper": p, "n": n, "grade": lean[p][n]} for p, n in items]},
        "labeller_b": {"labeller": "gemini-labeller", "header": {"rubric_sha": b_sha} if b_sha is not None else {},
                       "records": [{"paper": p, "n": n, "grade": lean[p][n] if i < audit_confirmed else "not-in-paper"}
                                   for i, (p, n) in enumerate(items)]}}
    return {"verifier": ver, "checker": chk, "double_graded": [list(x) for x in draw["double_graded"]],
            "audit": audit, "audit_labellers": labellers, "validity": {"void": False, "cause": ""},
            "tokens": {"verifier": {"input": 10, "output": 2, "cache_read": 0, "cache_write": 0}}}


def test_analyse_fixture_identical_raters():
    r = an.analyse(_bundle(), RUN1, B=400)
    k = r["kappa_120"]
    assert k["double_graded"] == 120 and k["kappa"] == 1.0
    assert k["bootstrap"]["ci95"] == [1.0, 1.0]
    assert r["kappa_without_W7160385925"]["double_graded"] == 114
    assert r["kappa_without_W7160385925"]["papers"] == 19
    assert r["audit"]["n"] == 20 and r["audit"]["confirmed_by_both"] == 20 and r["audit"]["g2_pass"]
    assert r["decision"]["outcome"] == "G1 pass, G2 pass, G3 pass"


def test_analyse_precision_headline_and_contaminated_counts():
    r = an.analyse(_bundle(), RUN1, B=50)
    hp, cp = r["precision_headline"], r["contaminated_62"]
    assert hp["arms"]["haiku"]["graded"] + hp["arms"]["opus"]["graded"] == 325
    assert cp["arms"]["haiku"]["graded"] + cp["arms"]["opus"]["graded"] == 62
    assert cp["label"] == "circular: the rules were written while reading these"
    # verifier = round-1 lean grades, so v1 distribution == round-1 distribution on the same claims
    for arm in ("haiku", "opus"):
        assert hp["arms"][arm]["grade_counts"] == hp["round1_same_claims"][arm]["grade_counts"]
    # all 387: haiku 169/190 faithful in round 1 (s5_analysis_A2_results.json)
    tot = sum(x["arms"]["haiku"]["faithful"] for x in (hp, cp))
    assert tot == 169
    w = hp["arms"]["haiku"]
    assert w["wilson95"] == list(an.wilson(w["faithful"], w["graded"])[1:])
    assert set(hp["by_domain"]) == {"math", "physics"}


def test_analyse_flipped_checker_fails_g1():
    r = an.analyse(_bundle(checker_flip=True), RUN1, B=200)
    # Every pair disagrees (po = 0) with verifier faithful-share pa, checker share 1 - pa:
    # pe = 2 pa (1 - pa), kappa = -pe / (1 - pe)  (closed form, not -1 unless pa = 0.5).
    lean = _lean()
    dg = _bundle()["double_graded"]
    pa = sum(lean[p][n] == "faithful" for p, n in dg) / len(dg)
    pe = 2 * pa * (1 - pa)
    assert abs(r["kappa_120"]["kappa"] - (-pe / (1 - pe))) < 1e-12, (r["kappa_120"]["kappa"], pa)
    assert r["kappa_120"]["raw_agreement"] == 0.0
    assert r["decision"]["outcome"] == "G1 fail, point kappa < 0.6"


def test_analyse_audit_16_of_20_fails_g2():
    r = an.analyse(_bundle(audit_confirmed=16), RUN1, B=200)
    assert r["audit"]["confirmed_by_both"] == 16 and r["audit"]["g2_pass"] is False
    r = an.analyse(_bundle(audit_confirmed=17), RUN1, B=200)
    assert r["audit"]["g2_pass"] is True


def test_analyse_void_reads_no_outcome():
    b = _bundle()
    b["validity"] = {"void": True, "cause": "C3 rubric sha mismatch"}
    r = an.analyse(b, RUN1, B=50)
    assert r["decision"]["outcome"] == "void" and "kappa_120" not in r


def test_analyse_rejects_incomplete_inputs():
    b = _bundle()
    first = next(iter(b["verifier"]))
    b["verifier"][first].pop(next(iter(b["verifier"][first])))
    try:
        an.analyse(b, RUN1, B=10)
    except SystemExit:
        pass
    else:
        raise AssertionError("missing verifier grade accepted")
    b = _bundle()
    p = next(iter(b["checker"]))
    b["checker"][p][next(iter(b["checker"][p]))] = "maybe"
    try:
        an.analyse(b, RUN1, B=10)
    except SystemExit:
        pass
    else:
        raise AssertionError("out-of-set checker grade accepted")


def test_analyse_load_and_doubt_rate():
    r = an.analyse(_bundle(doubt_every=10), RUN1, B=10)
    ld = r["load"]
    n_doubt = sum(1 for p, d in _lean().items() for n in d if n % 10 == 0)
    assert ld["verifier_graded"] == 387 and ld["doubted"] == n_doubt
    assert abs(ld["doubt_rate"] - n_doubt / 387) < 1e-15
    assert ld["tokens"]["verifier"]["total"] == 12


def test_analyse_deterministic_bytes():
    a = json.dumps(an.analyse(_bundle(checker_flip=True), RUN1, B=300), sort_keys=True)
    b = json.dumps(an.analyse(_bundle(checker_flip=True), RUN1, B=300), sort_keys=True)
    assert a == b


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except (Exception, SystemExit) as e:  # noqa: BLE001  (must() raises SystemExit)
                fails += 1
                print("FAIL", name, repr(e))
    sys.exit(1 if fails else 0)
