"""Known-answer tests for escalation_router.py (pre-reg §5, §8a).

Run: python3 -I test_escalation_router.py   or   python3 -m pytest -q test_escalation_router.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import escalation_router as er  # noqa: E402


def v(grade="faithful", doubt=False, **kw):
    d = {"id": ["P", 1], "source": "verifier", "l0": "ok", "verifier": {"grade": grade, "doubt": doubt}}
    d.update(kw)
    return d


def test_no_doubt_settles_at_l0_with_verifier_grade():
    r = er.route(v("wrong-relation"))
    assert r["status"] == "settled" and r["at"] == "L0" and r["grade"] == "wrong-relation"
    assert r["path"] == ["L0"] and not r["calibration_item"]


def test_l0_reject_is_not_routed():
    r = er.route(v(doubt=True, l0="reject"))
    assert r["status"] == "l0-reject" and r["path"] == ["L0"]


def test_doubt_goes_to_l1():
    r = er.route(v(doubt=True))
    assert r["status"] == "pending" and r["at"] == "L1" and r["path"] == ["L0", "L1"]


def test_l1_agreement_settles():
    r = er.route(v("wrong-direction", doubt=True, l1={"grade": "wrong-direction"}))
    assert r["status"] == "settled" and r["at"] == "L1" and r["grade"] == "wrong-direction"


def test_l1_split_goes_to_l2():
    r = er.route(v("faithful", doubt=True, l1={"grade": "wrong-relation"}))
    assert r["status"] == "pending" and r["at"] == "L2" and r["path"] == ["L0", "L1", "L2"]
    assert r["positions"] == ["faithful", "wrong-relation"]


def test_l1_split_on_non_faithful_category_still_splits():
    # Exact-grade agreement, not faithful-vs-not (assumption A-R2).
    r = er.route(v("wrong-relation", doubt=True, l1={"grade": "not-in-paper"}))
    assert r["at"] == "L2"


def test_l2_convergence_settles():
    r = er.route(v("faithful", doubt=True, l1={"grade": "wrong-relation"}, l2={"outcome": "converged", "grade": "wrong-relation"}))
    assert r["status"] == "settled" and r["at"] == "L2" and r["grade"] == "wrong-relation"
    assert not r["calibration_item"]


def test_l2_impasse_goes_to_l3():
    r = er.route(v(doubt=True, l1={"grade": "wrong-relation"}, l2={"outcome": "impasse", "rule_meaning": False}))
    assert r["status"] == "pending" and r["at"] == "L3" and r["path"] == ["L0", "L1", "L2", "L3"]


def test_rule_meaning_dispute_skips_l3_to_l4():
    r = er.route(v(doubt=True, l1={"grade": "wrong-relation"}, l2={"outcome": "impasse", "rule_meaning": True}))
    assert r["status"] == "pending" and r["at"] == "L4"
    assert "L3" not in r["path"] and r["path"] == ["L0", "L1", "L2", "L4"]


def test_rule_meaning_skips_l3_even_if_l3_ruling_supplied():
    # A stray L3 ruling must not be used for a rule-meaning dispute.
    r = er.route(v(doubt=True, l1={"grade": "wrong-relation"}, l2={"outcome": "impasse", "rule_meaning": True},
                   l3={"outcome": "ruled", "grade": "faithful"}))
    assert r["at"] == "L4" and r["status"] == "pending" and "L3" not in r["path"]


def test_l3_ruling_settles_and_is_calibration():
    r = er.route(v(doubt=True, l1={"grade": "wrong-relation"}, l2={"outcome": "impasse", "rule_meaning": False},
                   l3={"outcome": "ruled", "grade": "wrong-relation"}))
    assert r["status"] == "settled" and r["at"] == "L3" and r["grade"] == "wrong-relation" and r["calibration_item"]


def test_l3_can_refer_rule_meaning_to_l4():
    r = er.route(v(doubt=True, l1={"grade": "wrong-relation"}, l2={"outcome": "impasse", "rule_meaning": False},
                   l3={"outcome": "rule_meaning"}))
    assert r["at"] == "L4" and r["path"] == ["L0", "L1", "L2", "L3", "L4"]


def test_l4_ruling_and_l5():
    base = dict(doubt=True, l1={"grade": "wrong-relation"}, l2={"outcome": "impasse", "rule_meaning": True})
    r = er.route(v(**base, l4={"outcome": "ruled", "grade": "faithful"}))
    assert r["status"] == "settled" and r["at"] == "L4" and r["calibration_item"]
    r = er.route(v(**base, l4={"outcome": "unresolved"}))
    assert r["status"] == "pending" and r["at"] == "L5"


def test_audit_disagreement_goes_to_l2_agreement_does_not():
    a = {"id": ["P", 2], "source": "audit", "audit": {"agreed_grade": "faithful", "labeller_a": "faithful", "labeller_b": "faithful"}}
    assert er.route(a)["status"] == "settled" and er.route(a)["at"] == "audit"
    a["audit"]["labeller_b"] = "wrong-relation"
    r = er.route(a)
    assert r["at"] == "L2" and r["status"] == "pending"


def test_bad_inputs_raise():
    for bad in (v(l2={"outcome": "converged", "grade": "faithful"}),        # L2 without L1 split
                v(doubt=True, l1={"grade": "faithful"}, l2={"outcome": "maybe"}),
                {"id": ["P", 1], "source": "other"}):
        try:
            er.route(bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted {bad}")


def _l3_item(i):
    return v(doubt=True, l1={"grade": "wrong-relation"}, l2={"outcome": "impasse", "rule_meaning": False}, id=["P", i])


def test_l3_budget_exactly_30_not_flagged():
    s = er.route_all([_l3_item(i) for i in range(30)])
    assert s["summary"]["reached"]["L3"] == 30
    assert s["summary"]["l3_over_budget"] is False
    assert not any(r["l3_over_budget"] for r in s["results"])


def test_l3_over_budget_flagged():
    items = [_l3_item(i) for i in range(31)] + [v(id=["Q", 1])]
    s = er.route_all(items)
    assert s["summary"]["reached"]["L3"] == 31 and s["summary"]["l3_over_budget"] is True
    flagged = [r["id"] for r in s["results"] if r["l3_over_budget"]]
    assert flagged == [["P", 30]], flagged   # the 31st in id order


def test_rule_meaning_items_do_not_consume_l3_budget():
    items = [_l3_item(i) for i in range(30)] + [
        v(doubt=True, l1={"grade": "wrong-relation"}, l2={"outcome": "impasse", "rule_meaning": True}, id=["R", i]) for i in range(5)]
    s = er.route_all(items)
    assert s["summary"]["reached"]["L3"] == 30 and s["summary"]["reached"]["L4"] == 5
    assert s["summary"]["l3_over_budget"] is False


def test_summary_counts_and_doubt_rate():
    items = [v(id=["A", 1]), v(id=["A", 2], doubt=True), v(id=["A", 3], doubt=True, l1={"grade": "faithful"}),
             v(id=["A", 4], doubt=True, l1={"grade": "not-in-paper"})]
    s = er.route_all(items)["summary"]
    assert s["reached"] == {"L0": 4, "L1": 3, "L2": 1, "L3": 0, "L4": 0, "L5": 0, "audit": 0}
    assert s["verifier_items"] == 4 and s["doubted"] == 3 and s["doubt_rate"] == 0.75


def test_deterministic_and_order_independent():
    items = [_l3_item(i) for i in range(31)]
    a = json.dumps(er.route_all(items), sort_keys=True)
    b = json.dumps(er.route_all(list(reversed(items))), sort_keys=True)
    assert a == b


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except Exception as e:  # noqa: BLE001
                fails += 1
                print("FAIL", name, repr(e))
    sys.exit(1 if fails else 0)
