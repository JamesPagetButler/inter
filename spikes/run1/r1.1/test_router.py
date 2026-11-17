"""Known-answer tests for router.py (pre-reg §5, §8a "Escalation router"). Run: python3 -I test_router.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import router  # noqa: E402

F, WR = "faithful", "wrong-relation"
IMP_APP = {"outcome": "impasse", "dispute": "application"}
IMP_RULE = {"outcome": "impasse", "dispute": "rule-meaning"}


def it(**kw):
    base = {"verifier_grade": F, "doubt": True}
    base.update(kw)
    return base


def raises(item):
    try:
        router.route(item)
    except router.RouterError:
        return
    raise AssertionError(f"accepted {item}")


def test_not_doubted_stays_settled_at_verifier_grade():
    r = router.route({"verifier_grade": WR, "doubt": False})
    assert r == {"status": "settled", "grade": WR, "layer": "L0", "path": ["L0"]}


def test_doubt_goes_to_l1():
    assert router.route(it()) == {"status": "pending", "layer": "L1", "path": ["L0", "L1"]}


def test_l1_agreement_settles():
    r = router.route(it(l1_grade=F))
    assert r["status"] == "settled" and r["grade"] == F and r["layer"] == "L1"


def test_l1_split_goes_to_l2():
    r = router.route(it(l1_grade=WR))
    assert r == {"status": "pending", "layer": "L2", "path": ["L0", "L1", "L2"]}


def test_l1_split_on_non_faithful_grades_goes_to_l2():
    # exact-grade agreement: wrong-relation vs not-in-paper is a split, not an agreement
    r = router.route(it(verifier_grade=WR, l1_grade="not-in-paper"))
    assert r["status"] == "pending" and r["layer"] == "L2"


def test_l2_converged_settles():
    r = router.route(it(l1_grade=WR, l2={"outcome": "converged", "grade": WR}))
    assert r["status"] == "settled" and r["grade"] == WR and r["layer"] == "L2"


def test_l2_impasse_goes_to_l3():
    r = router.route(it(l1_grade=WR, l2=IMP_APP))
    assert r == {"status": "pending", "layer": "L3", "path": ["L0", "L1", "L2", "L3"]}


def test_l3_ruling_settles():
    r = router.route(it(l1_grade=WR, l2=IMP_APP, l3={"outcome": "ruled", "grade": "not-in-paper"}))
    assert r["status"] == "settled" and r["grade"] == "not-in-paper" and r["layer"] == "L3"


def test_rule_meaning_dispute_skips_l3_to_l4():
    r = router.route(it(l1_grade=WR, l2=IMP_RULE))
    assert r == {"status": "pending", "layer": "L4", "path": ["L0", "L1", "L2", "L4"]}
    raises(it(l1_grade=WR, l2=IMP_RULE, l3={"outcome": "ruled", "grade": F}))


def test_l4_ruling_settles():
    r = router.route(it(l1_grade=WR, l2=IMP_RULE, l4={"outcome": "ruled", "grade": WR}))
    assert r["status"] == "settled" and r["grade"] == WR and r["layer"] == "L4"


def test_l4_impasse_goes_to_l5_and_l5_settles():
    r = router.route(it(l1_grade=WR, l2=IMP_RULE, l4={"outcome": "impasse"}))
    assert r == {"status": "pending", "layer": "L5", "path": ["L0", "L1", "L2", "L4", "L5"]}
    r = router.route(it(l1_grade=WR, l2=IMP_RULE, l4={"outcome": "impasse"}, l5={"outcome": "ruled", "grade": F}))
    assert r["status"] == "settled" and r["layer"] == "L5" and r["grade"] == F


def test_undefined_states_fail_closed():
    raises({"verifier_grade": "partial", "doubt": False})
    raises({"verifier_grade": F, "doubt": "yes"})
    raises({"verifier_grade": F, "doubt": False, "l1_grade": WR})
    raises(it(l1_grade=F, l2=IMP_APP))
    raises(it(l1_grade=WR, l2={"outcome": "impasse"}))            # dispute type missing
    raises(it(l1_grade=WR, l2={"outcome": "stalled"}))
    raises(it(l1_grade=WR, l2=IMP_APP, l3={"outcome": "impasse"}))
    raises(it(l1_grade=WR, l3={"outcome": "ruled", "grade": F}))  # L3 before L2


def _l3_items(k):
    return [it(l1_grade=WR, l2=IMP_APP)] * k + [it(l1_grade=WR, l2=IMP_RULE)] * 5 + [{"verifier_grade": F, "doubt": False}] * 40


def test_l3_budget_flag_at_31_not_30():
    r30 = router.route_round(_l3_items(30))
    r31 = router.route_round(_l3_items(31))
    assert r30["l3_count"] == 30 and r30["l3_over_budget"] is False
    assert r31["l3_count"] == 31 and r31["l3_over_budget"] is True
    assert router.L3_BUDGET == 30


def test_l3_budget_counts_settled_l3_items_not_l4_skips():
    items = [it(l1_grade=WR, l2=IMP_APP, l3={"outcome": "ruled", "grade": F})] * 31
    assert router.route_round(items)["l3_over_budget"] is True
    assert router.route_round([it(l1_grade=WR, l2=IMP_RULE)] * 40)["l3_count"] == 0


def test_round_per_layer_counts():
    r = router.route_round(_l3_items(2))
    assert r["per_layer"] == {"L1": 7, "L2": 7, "L3": 2, "L4": 5, "L5": 0}


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
