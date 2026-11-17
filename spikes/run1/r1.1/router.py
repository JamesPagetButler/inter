#!/usr/bin/env python3
"""Round 1.1 escalation router (pre-reg §5, the inter#300 P3 ladder). Pure functions, no I/O.

Input: one item's state as a dict. L0 (capture.py) has already passed for it.
  verifier_grade  str, the verifier v1 grade (required)
  doubt           bool, the verifier's doubt flag (required)
  l1_grade        checker grade at L1, or absent/None if L1 has not run
  l2              {"outcome": "converged", "grade": g}
                  | {"outcome": "impasse", "dispute": "rule-meaning" | "application"}
  l3              {"outcome": "ruled", "grade": g}   (L3 = qbp-oppenheimer applies the rubric)
  l4              {"outcome": "ruled", "grade": g} | {"outcome": "impasse"}
  l5              {"outcome": "ruled", "grade": g}   (the beekeeper)

route(item) -> {"status": "settled", "grade": g, "layer": L, "path": [...]}
             | {"status": "pending", "layer": L, "path": [...]}   (L = the layer it waits on)

Ladder:
  not doubted            -> settled at the verifier's grade (L0)
  doubted                -> L1 (checker)
  L1 same grade          -> settled
  L1 different grade     -> L2
  L2 converged           -> settled
  L2 impasse, rule-meaning dispute -> L4 (skips L3, seq 5212)
  L2 impasse, otherwise  -> L3
  L3 ruling              -> settled
  L4 ruling              -> settled; L4 impasse -> L5
  L5 ruling              -> settled
Any state that does not fit the ladder raises RouterError (fail closed).

route_round(items) applies route() to every item and counts the items whose path reaches L3;
over L3_BUDGET (30) sets l3_over_budget. The flag does not change any item's route.
"""
GRADES = {"faithful", "wrong-relation", "wrong-direction", "wrong-modality",
          "wrong-locator", "not-in-paper"}
L3_BUDGET = 30
DISPUTES = {"rule-meaning", "application"}


class RouterError(Exception):
    """An item state that the §5 ladder does not define."""


def _grade(g, where):
    if g not in GRADES:
        raise RouterError(f"{where}: grade {g!r} not in the category set")
    return g


def _later(item, *keys):
    return [k for k in keys if item.get(k) is not None]


def route(item):
    vg = _grade(item.get("verifier_grade"), "verifier")
    doubt = item.get("doubt")
    if not isinstance(doubt, bool):
        raise RouterError("doubt must be a bool")
    path = ["L0"]
    if not doubt:
        if _later(item, "l1_grade", "l2", "l3", "l4", "l5"):
            raise RouterError("non-doubted item has escalation records")
        return {"status": "settled", "grade": vg, "layer": "L0", "path": path}

    path.append("L1")
    l1 = item.get("l1_grade")
    if l1 is None:
        if _later(item, "l2", "l3", "l4", "l5"):
            raise RouterError("later layer recorded before L1")
        return {"status": "pending", "layer": "L1", "path": path}
    _grade(l1, "L1")
    if l1 == vg:
        if _later(item, "l2", "l3", "l4", "l5"):
            raise RouterError("L1 agreed but later layers recorded")
        return {"status": "settled", "grade": l1, "layer": "L1", "path": path}

    path.append("L2")
    l2 = item.get("l2")
    if l2 is None:
        if _later(item, "l3", "l4", "l5"):
            raise RouterError("later layer recorded before L2")
        return {"status": "pending", "layer": "L2", "path": path}
    if l2.get("outcome") == "converged":
        if _later(item, "l3", "l4", "l5"):
            raise RouterError("L2 converged but later layers recorded")
        return {"status": "settled", "grade": _grade(l2.get("grade"), "L2"), "layer": "L2", "path": path}
    if l2.get("outcome") != "impasse":
        raise RouterError(f"L2 outcome {l2.get('outcome')!r} undefined")
    dispute = l2.get("dispute")
    if dispute not in DISPUTES:
        raise RouterError(f"L2 impasse needs dispute in {sorted(DISPUTES)}, got {dispute!r}")

    if dispute == "application":
        path.append("L3")
        l3 = item.get("l3")
        if l3 is None:
            if _later(item, "l4", "l5"):
                raise RouterError("later layer recorded before L3")
            return {"status": "pending", "layer": "L3", "path": path}
        if l3.get("outcome") != "ruled":
            raise RouterError(f"L3 outcome {l3.get('outcome')!r} undefined in §5")
        if _later(item, "l4", "l5"):
            raise RouterError("L3 ruled but later layers recorded")
        return {"status": "settled", "grade": _grade(l3.get("grade"), "L3"), "layer": "L3", "path": path}

    # rule-meaning dispute: skip L3
    if item.get("l3") is not None:
        raise RouterError("rule-meaning dispute must skip L3, but an L3 record exists")
    path.append("L4")
    l4 = item.get("l4")
    if l4 is None:
        if _later(item, "l5"):
            raise RouterError("L5 recorded before L4")
        return {"status": "pending", "layer": "L4", "path": path}
    if l4.get("outcome") == "ruled":
        if _later(item, "l5"):
            raise RouterError("L4 ruled but L5 recorded")
        return {"status": "settled", "grade": _grade(l4.get("grade"), "L4"), "layer": "L4", "path": path}
    if l4.get("outcome") != "impasse":
        raise RouterError(f"L4 outcome {l4.get('outcome')!r} undefined")
    path.append("L5")
    l5 = item.get("l5")
    if l5 is None:
        return {"status": "pending", "layer": "L5", "path": path}
    if l5.get("outcome") != "ruled":
        raise RouterError(f"L5 outcome {l5.get('outcome')!r} undefined")
    return {"status": "settled", "grade": _grade(l5.get("grade"), "L5"), "layer": "L5", "path": path}


def route_round(items):
    routes = [route(it) for it in items]
    l3 = sum("L3" in r["path"] for r in routes)
    return {"routes": routes, "l3_count": l3, "l3_budget": L3_BUDGET, "l3_over_budget": l3 > L3_BUDGET,
            "per_layer": {L: sum(L in r["path"] for r in routes) for L in ("L1", "L2", "L3", "L4", "L5")}}
