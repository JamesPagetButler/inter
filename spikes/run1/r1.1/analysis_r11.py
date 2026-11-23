#!/usr/bin/env python3
"""Round 1.1 analysis (pre-reg §6 measurements, §7 predictions, §8 decision rules). Run under boxrun.

Committed before any 1.1 rating exists. Method choices are fixed here:
  - kappa: Cohen's kappa on faithful-vs-not, the round-1 formula (s5_analysis_A2.py kappa()):
      po = agreement share; pe = pa*pb + (1-pa)*(1-pb); kappa = (po - pe)/(1 - pe); undefined (None)
      when pe == 1 or n == 0.
  - paper-cluster bootstrap: resample the papers with replacement (as many as there are), pool
    their pairs, recompute kappa; B = 10000; numpy default_rng(251117) (PCG64); percentile interval
    (2.5, 97.5) with numpy's default (linear) percentile. A replicate whose kappa is undefined is
    dropped and counted (assumption A-A1). Each bootstrap starts its own default_rng(251117)
    (assumption A-A2), so the 120 and the without-W7160385925 intervals do not depend on run order.
  - Wilson 95%, z = 1.959964 (round 1's constant).
  - G1: lower bound of the 120's interval >= 0.6. G3: the same on the 114 without W7160385925.
  - G2: >= 17 of exactly 20 audit items confirmed by both labellers (labeller grade == agreed grade,
    exact category; assumption A-A3). Audit items must be double-graded items where verifier grade ==
    checker grade == agreed_grade (exact; A-A3).
  - Decision: §8 table, evaluated validity -> G1 -> G2 -> G3; anything unlisted (e.g. an undefined
    bound) is "not listed" -> L4 -> beekeeper. The director picks no consequence.

Inputs (`run` bundle JSON, after L0):
  verifier: {paper: {n: {"grade": g, "doubt": bool}}}  -- all 387 keyed claims
  checker:  {paper: {n: g}}                             -- exactly the double-graded 120
  double_graded: [[paper, n], ...]                      -- must equal sampler.draw()'s committed draw
  audit: [{"paper","n","agreed_grade","labeller_a","labeller_b"}]   (20)
  validity: {"void": bool, "cause": str}
  routing_summary: escalation_router.route_all()["summary"]  (optional, passed through)
  tokens: {stage: {four numeric fields}}                       (optional)
Arm, domain and the contaminated split come from the committed round-1 files via sampler.load_inputs.

CLI:  analysis_r11.py round1            -> reproduce round 1's inter-rater kappa from round 1's inputs
      analysis_r11.py run <bundle.json> -> the §6 measurements + §8 decision
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sampler  # noqa: E402

RUN1 = HERE.parent
SEED = 251117
B = 10000
Z = 1.959964
GRADES = ("faithful", "wrong-relation", "wrong-direction", "wrong-modality", "wrong-locator", "not-in-paper")
W716 = "W7160385925"
BAR = 0.6
ROUND1_HAIKU_PRECISION = 0.889          # §7 P1, as stated
CONTAMINATED_LABEL = "circular: the rules were written while reading these"

# Round 1 provenance (s5_analysis_A2.py EXPECT)
R1_INTERRATER = ["W4390977661", "W7160385925", "W2015765968", "W4313326288"]
R1_EXPECT = {
    "s5_grades_A2_lean_sha256_manifest.txt": "a2f2754bd760d2e1a24b67f79ad05561bf128bd1192f41512ee952b99a8d039f",
    "s5_arm_key_A2_SEALED.json": "af6f985e2c6f5e7994718f00a1a2f8aeddcd32915e51b3de58455778c8acf206",
}


def must(cond, msg):
    if not cond:
        raise SystemExit(f"ABORT: {msg}")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------- statistics ----------------

def kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def kblock(pairs):
    a = [int(x[0]) for x in pairs]
    b = [int(x[1]) for x in pairs]
    n = len(pairs)
    return {"double_graded": n, "kappa": kappa(a, b),
            "raw_agreement": (sum(x == y for x, y in zip(a, b)) / n) if n else None,
            "prevalence": ((sum(a) + sum(b)) / (2 * n)) if n else None}


def wilson(k, n):
    if n == 0:
        return (None, None, None)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def percentile_ci(reps):
    """Percentile 95% interval: numpy's default (linear) percentile at 2.5 and 97.5; None if empty."""
    if not reps:
        return None
    return [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))]


def cluster_bootstrap_kappa(pairs_by_paper, B=B, seed=SEED):
    papers = sorted(pairs_by_paper)
    rng = np.random.default_rng(seed)
    reps, undefined = [], 0
    for _ in range(B):
        pool = []
        for i in rng.integers(0, len(papers), len(papers)):
            pool += pairs_by_paper[papers[i]]
        k = kappa([int(x[0]) for x in pool], [int(x[1]) for x in pool])
        if k is None:
            undefined += 1
        else:
            reps.append(float(k))
    ci = percentile_ci(reps)
    return {"B": B, "seed": seed, "undefined": undefined, "ci95": ci, "replicates": reps}


# ---------------- round 1 reproduction ----------------

def _jsonl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def _round1_rows(run1):
    for rel, h in R1_EXPECT.items():
        must(sha(run1 / rel) == h, f"sha mismatch: {rel}")
    for line in (run1 / "s5_grades_A2_lean_sha256_manifest.txt").read_text().splitlines():
        if line.strip():
            h, rel = line.split(maxsplit=1)
            rel = rel.strip()
            p = (run1 / rel) if (run1 / rel).exists() else (run1.parent.parent / rel)
            must(sha(p) == h, f"manifest mismatch: {rel}")
    key = json.loads((run1 / "s5_arm_key_A2_SEALED.json").read_text())
    arms = {c["arm"] for pid in key["order"] for c in key["papers"][pid]["claims"]}
    must("primary" in arms and len(arms) == 2, arms)
    ARM = {"primary": "haiku", (arms - {"primary"}).pop(): "opus"}
    rows = []
    for pid in key["order"]:
        paper = key["papers"][pid]
        g = {x["n"]: x["grade"] for x in _jsonl(run1 / "s5_grades_A2_lean" / f"{pid}.grades.jsonl")}
        must(set(g) == {c["n"] for c in paper["claims"]}, f"{pid}: lean n-set")
        for c in paper["claims"]:
            rows.append({"paper": pid, "domain": paper["domain"], "n": c["n"], "arm": ARM[c["arm"]], "grade": g[c["n"]]})
    return rows


def parse_gemini_answer(ans):
    """Round 1's frozen Gemini parsing rule (s5_analysis_A2.py): every line that parses as a JSON
    object with int "n" and str "grade" is taken; the same n twice with the same grade counts once,
    with different grades it is unparsed (None), never last-one-wins."""
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
    return {n: (None if n in conflicted else g) for n, g in gem.items()}


def reproduce_round1(run1=RUN1):
    """Round 1's inter-rater kappa from round 1's own inputs: the A3 lean grades vs the Gemini redo
    answers (s5_interrater_A2/<id>.answer_RAW.txt, sha-checked against meta.json) on the 4
    inter-rater papers, both arms, with round 1's frozen Gemini parsing rule."""
    run1 = Path(run1)
    rows = _round1_rows(run1)
    gdir = run1 / "s5_interrater_A2"
    pairs, unparsed = [], 0
    for pid in R1_INTERRATER:
        meta = json.loads((gdir / f"{pid}.meta.json").read_text())
        ans = (gdir / f"{pid}.answer_RAW.txt").read_text()
        must(hashlib.sha256(ans.encode("utf-8")).hexdigest() == meta["answer_sha256"], pid)
        gem = parse_gemini_answer(ans)
        for r in (r for r in rows if r["paper"] == pid):
            g = gem.get(r["n"])
            if g not in GRADES:
                unparsed += 1
                continue
            pairs.append((r["arm"], r["grade"] == "faithful", g == "faithful"))
    return {"overall": kblock([(x[1], x[2]) for x in pairs]), "unparsed": unparsed,
            "per_arm": {a: kblock([(x[1], x[2]) for x in pairs if x[0] == a]) for a in ("haiku", "opus")},
            "inputs": {"lean_grades": "s5_grades_A2_lean/ (manifest a2f2754b…039f)",
                       "gemini": "s5_interrater_A2/<id>.answer_RAW.txt (meta answer_sha256 checked)",
                       "papers": R1_INTERRATER}}


# ---------------- §8 decision ----------------

def decide(void, g1_lb, g1_point, g2_pass, g3_lb):
    def out(o, owner):
        return {"outcome": o, "owner": owner, "inputs": {"void": void, "g1_lower_bound": g1_lb, "g1_point": g1_point,
                                                         "g2_pass": g2_pass, "g3_lower_bound": g3_lb}}
    if void:
        return out("void", "qbp-architecture")
    if g1_lb is None or g1_point is None:
        return out("not listed", "L4 -> beekeeper")
    if g1_lb >= BAR:
        if g2_pass is None:
            return out("not listed", "L4 -> beekeeper")
        if not g2_pass:
            return out("G1 pass, G2 fail", "L4 panel")
        if g3_lb is None:
            return out("not listed", "L4 -> beekeeper")
        return out("G1 pass, G2 pass, G3 pass" if g3_lb >= BAR else "G1 pass, G2 pass, G3 fail", "qbp-architecture")
    if g1_point >= BAR:
        return out("G1 fail, point kappa >= 0.6", "qbp-architecture; deming")
    return out("G1 fail, point kappa < 0.6", "L4 panel")


# ---------------- §6 analysis ----------------

def _stats(grades):
    f = sum(g == "faithful" for g in grades)
    p, lo, hi = wilson(f, len(grades))
    return {"graded": len(grades), "faithful": f, "precision": p, "wilson95": [lo, hi],
            "grade_counts": {g: sum(x == g for x in grades) for g in GRADES}}


def _precision_block(claims, rows, ver, lean):
    out = {"arms": {}, "by_domain": {}, "round1_same_claims": {}}
    for arm in ("haiku", "opus"):
        cs = [c for c in claims if rows[c]["arm"] == arm]
        out["arms"][arm] = _stats([ver[c]["grade"] for c in cs])
        out["round1_same_claims"][arm] = _stats([lean[c] for c in cs])
        for d in ("math", "physics"):
            out["by_domain"].setdefault(d, {})[arm] = _stats([ver[c]["grade"] for c in cs if rows[c]["domain"] == d])
    return out


def _kappa_with_ci(dg, ver, chk, B, seed):
    by = {}
    for c in dg:
        by.setdefault(c[0], []).append((ver[c]["grade"] == "faithful", chk[c] == "faithful"))
    blk = kblock([x for p in sorted(by) for x in by[p]])
    bs = cluster_bootstrap_kappa(by, B=B, seed=seed)
    bs.pop("replicates")
    blk.update({"papers": len(by), "bootstrap": bs})
    return blk


def analyse(bundle, run1=RUN1, B=B, seed=SEED):
    run1 = Path(run1)
    validity = bundle.get("validity", {"void": False, "cause": ""})
    if validity.get("void"):
        return {"validity": validity, "decision": decide(True, None, None, None, None)}
    rows = {(r["paper"], r["n"]): r for r in _round1_rows(run1)}
    lean = {c: r["grade"] for c, r in rows.items()}
    claims, cont = sampler.load_inputs(run1)
    must(set(claims) == set(rows) and len(rows) == 387, "keyed claim set")
    ver = {(p, int(n)): v for p, d in bundle["verifier"].items() for n, v in d.items()}
    must(set(ver) == set(rows), "verifier grades must cover exactly the 387 keyed claims")
    for c, v in ver.items():
        must(v.get("grade") in GRADES and isinstance(v.get("doubt"), bool), f"verifier {c}: {v}")
    dg = sorted((p, int(n)) for p, n in bundle["double_graded"])
    must(dg == sampler.draw(claims, cont, seed=SEED)["double_graded"], "double_graded != the committed §4 draw")
    chk = {(p, int(n)): g for p, d in bundle["checker"].items() for n, g in d.items()}
    must(set(chk) == set(dg), "checker grades must cover exactly the double-graded set")
    must(all(g in GRADES for g in chk.values()), "checker grade outside the category set")

    res = {"validity": validity}
    res["kappa_120"] = _kappa_with_ci(dg, ver, chk, B, seed)
    dg_x = [c for c in dg if c[0] != W716]
    res["kappa_without_W7160385925"] = _kappa_with_ci(dg_x, ver, chk, B, seed)

    audit = bundle.get("audit") or []
    conf = 0
    for a in audit:
        c = (a["paper"], int(a["n"]))
        must(c in chk and ver[c]["grade"] == chk[c] == a["agreed_grade"], f"audit item {c} is not an agreed item")
        must(c not in cont, f"audit item {c} is contaminated")
        conf += a["labeller_a"] == a["agreed_grade"] and a["labeller_b"] == a["agreed_grade"]
    must(len({(a["paper"], int(a["n"])) for a in audit}) == len(audit), "duplicate audit item")
    res["audit"] = {"n": len(audit), "confirmed_by_both": conf, "share": (conf / len(audit)) if audit else None,
                    "g2_pass": (conf >= 17) if len(audit) == 20 else None}

    head = sorted(c for c in rows if c not in cont)
    contam = sorted(c for c in rows if c in cont)
    res["precision_headline"] = _precision_block(head, rows, ver, lean)
    res["contaminated_62"] = _precision_block(contam, rows, ver, lean)
    res["contaminated_62"]["label"] = CONTAMINATED_LABEL

    hk = res["precision_headline"]
    pooled_v1 = hk["arms"]["haiku"]["precision"]
    pooled_drop = hk["round1_same_claims"]["haiku"]["precision"] - pooled_v1
    wc = [c for c in head if c[0] == W716 and rows[c]["arm"] == "haiku"]
    w_v1 = _stats([ver[c]["grade"] for c in wc])["precision"]
    w_r1 = _stats([lean[c] for c in wc])["precision"]
    res["predictions"] = {
        "P1": {"haiku_headline_precision_v1": pooled_v1, "threshold": ROUND1_HAIKU_PRECISION,
               "holds": pooled_v1 < ROUND1_HAIKU_PRECISION},
        "P2": {"pooled_drop": pooled_drop, "W7160385925_haiku_headline_n": len(wc),
               "W7160385925_drop": (w_r1 - w_v1) if wc else None,
               "holds": ((w_r1 - w_v1) > pooled_drop) if wc else None,
               "basis": "round-1 lean minus v1 precision on the same headline haiku claims"}}

    doubted = sum(v["doubt"] for v in ver.values())
    tokens = {}
    for stage, t in sorted((bundle.get("tokens") or {}).items()):
        must(len(t) == 4 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in t.values()),
             f"tokens[{stage}] must have exactly four numeric fields")
        tokens[stage] = dict(t, total=sum(t.values()))
    res["load"] = {"verifier_graded": len(ver), "doubted": doubted, "doubt_rate": doubted / len(ver),
                   "doubt_rate_planning": 0.15, "routing": bundle.get("routing_summary"), "tokens": tokens,
                   "p4_clusters_by_rca_cause": "not computed: clustering P4 text by RCA cause is a reading, not code"}

    k = res["kappa_120"]
    g1_lb = k["bootstrap"]["ci95"][0] if k["bootstrap"]["ci95"] else None
    kx = res["kappa_without_W7160385925"]
    g3_lb = kx["bootstrap"]["ci95"][0] if kx["bootstrap"]["ci95"] else None
    res["decision"] = decide(False, g1_lb, k["kappa"], res["audit"]["g2_pass"], g3_lb)
    return res


def main(argv):
    if len(argv) >= 2 and argv[1] == "round1":
        sys.stdout.write(json.dumps(reproduce_round1(), indent=1, sort_keys=True) + "\n")
        return 0
    if len(argv) >= 3 and argv[1] == "run":
        b = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
        sys.stdout.write(json.dumps(analyse(b), indent=1, sort_keys=True) + "\n")
        return 0
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
