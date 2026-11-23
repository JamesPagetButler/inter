#!/usr/bin/env python3
"""Round 1.1 escalation router (pre-reg §5, the inter#300 P3 ladder). Pure code, no model call.

The router does not grade. Given what each layer has returned so far for one item, it says where
the item now stands: settled (with the grade that settles it) or pending at a layer.

Ladder (§5):
  L0  code: schema, rubric sha, category set (l0_checks.py). An L0 reject is not routed.
  L1  a verifier doubt goes to the checker; two agreeing raters settle it.
  L2  an L1 split goes to fresh verifier + checker sessions: they converge, or produce an impasse record.
  L3  qbp-oppenheimer rules on L2 impasses. Budget <= 30 items.
  L4  panel (qbp-oppenheimer + qbp-architecture, cartan confirming). Rule-meaning disputes skip L3.
  L5  the beekeeper, batched.
Every L3 or L4 ruling is a calibration item (§5); it applies forward only and never re-scores 1.1.

Assumptions where §5 is silent (simplest reading; listed in COMPONENT-RESULTS.md):
  A-R1 Only verifier doubts and audit-labeller disagreements enter the ladder. A non-doubted
       verifier/checker disagreement on the double-graded 120 is the kappa measurement, not an
       escalation.
  A-R2 "Agree" / "split" is exact grade equality over the six categories, not faithful-vs-not.
  A-R3 "Rule-meaning dispute" is a boolean the L2 impasse record carries (rule_meaning: true);
       L3 may also refer an item up as rule_meaning. Either way it goes to L4 and never uses L3.
  A-R4 An audit item goes to L2 unless both labellers' grades equal the agreed grade; the L2
       positions are the two labellers' grades. G2 is scored on the labellers' original grades,
       never on the L2 outcome.
  A-R5 L3 over budget is flagged, not truncated: every item over 30 (in sorted id order) carries
       l3_over_budget = true and the summary sets l3_over_budget. What to do then is not the router's.
  A-R6 An unresolved L4 goes to L5 (pending). L4 ruling settles.

Item shape:
  {"id": [paper, n], "source": "verifier"|"audit", "l0": "ok"|"reject",
   "verifier": {"grade": g, "doubt": bool},
   "l1": {"grade": g} | None,
   "l2": {"outcome": "converged", "grade": g} | {"outcome": "impasse", "rule_meaning": bool} | None,
   "l3": {"outcome": "ruled", "grade": g} | {"outcome": "rule_meaning"} | None,
   "l4": {"outcome": "ruled", "grade": g} | {"outcome": "unresolved"} | None,
   "audit": {"agreed_grade": g, "labeller_a": g, "labeller_b": g}}   (source audit only)

CLI: escalation_router.py <items.json>  -> routes all, prints JSON (sorted keys).
"""
import json
import sys

L3_BUDGET = 30
LEVELS = ("L0", "L1", "L2", "L3", "L4", "L5", "audit")


def _res(item, path, status, at, grade=None, calibration=False, **extra):
    r = {"id": item.get("id"), "path": path, "status": status, "at": at, "grade": grade,
         "calibration_item": calibration, "l3_over_budget": False}
    r.update(extra)
    return r


def _from_l2(item, path, positions):
    l2, l3, l4 = item.get("l2"), item.get("l3"), item.get("l4")
    path = path + ["L2"]
    if l2 is None:
        return _res(item, path, "pending", "L2", positions=positions)
    if l2.get("outcome") == "converged":
        return _res(item, path, "settled", "L2", l2["grade"])
    if l2.get("outcome") != "impasse" or not isinstance(l2.get("rule_meaning"), bool):
        raise ValueError(f"bad L2 record: {l2!r}")
    if not l2["rule_meaning"]:
        path = path + ["L3"]
        if l3 is None:
            return _res(item, path, "pending", "L3")
        if l3.get("outcome") == "ruled":
            return _res(item, path, "settled", "L3", l3["grade"], calibration=True)
        if l3.get("outcome") != "rule_meaning":
            raise ValueError(f"bad L3 record: {l3!r}")
    # rule-meaning dispute: L4, never L3
    path = path + ["L4"]
    if l4 is None:
        return _res(item, path, "pending", "L4")
    if l4.get("outcome") == "ruled":
        return _res(item, path, "settled", "L4", l4["grade"], calibration=True)
    if l4.get("outcome") == "unresolved":
        return _res(item, path + ["L5"], "pending", "L5")
    raise ValueError(f"bad L4 record: {l4!r}")


def route(item):
    src = item.get("source")
    if src == "audit":
        a = item["audit"]
        if a["labeller_a"] == a["agreed_grade"] == a["labeller_b"]:
            return _res(item, ["audit"], "settled", "audit", a["agreed_grade"])
        return _from_l2(item, ["audit"], [a["labeller_a"], a["labeller_b"]])
    if src != "verifier":
        raise ValueError(f"unknown source: {src!r}")
    if item.get("l0") != "ok":
        return _res(item, ["L0"], "l0-reject", "L0")
    vg, doubt = item["verifier"]["grade"], item["verifier"]["doubt"]
    if not doubt:
        if any(item.get(k) is not None for k in ("l1", "l2", "l3", "l4")):
            raise ValueError("escalation records on a non-doubted item")
        return _res(item, ["L0"], "settled", "L0", vg)
    l1 = item.get("l1")
    if l1 is None:
        if any(item.get(k) is not None for k in ("l2", "l3", "l4")):
            raise ValueError("later-layer records without an L1 result")
        return _res(item, ["L0", "L1"], "pending", "L1")
    if l1["grade"] == vg:
        if any(item.get(k) is not None for k in ("l2", "l3", "l4")):
            raise ValueError("L2+ records on an L1-agreed item")
        return _res(item, ["L0", "L1"], "settled", "L1", vg)
    return _from_l2(item, ["L0", "L1"], [vg, l1["grade"]])


def route_all(items, l3_budget=L3_BUDGET):
    results = sorted((route(i) for i in items), key=lambda r: (str(r["id"][0]), r["id"][1]))
    reached = {lv: 0 for lv in LEVELS}
    n_l3 = 0
    for r in results:
        for lv in r["path"]:
            reached[lv] += 1
        if "L3" in r["path"]:
            n_l3 += 1
            if n_l3 > l3_budget:
                r["l3_over_budget"] = True
    ver = [i for i in items if i.get("source") == "verifier" and i.get("l0") == "ok"]
    doubted = sum(bool(i["verifier"]["doubt"]) for i in ver)
    summary = {"reached": reached, "l3_budget": l3_budget, "l3_over_budget": n_l3 > l3_budget,
               "verifier_items": len(ver), "doubted": doubted,
               "doubt_rate": (doubted / len(ver)) if ver else None,
               "settled": sum(r["status"] == "settled" for r in results),
               "pending": {lv: sum(r["status"] == "pending" and r["at"] == lv for r in results) for lv in LEVELS},
               "calibration_items": sum(r["calibration_item"] for r in results)}
    return {"results": results, "summary": summary}


def main(argv):
    items = json.loads(open(argv[1], encoding="utf-8").read())
    sys.stdout.write(json.dumps(route_all(items), sort_keys=True, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
