#!/usr/bin/env python3
"""contextus-seed-corpus round 1 -- §5 analysis (A2 redraw, A3 lean grades).

Committed BEFORE the sealed arm key is opened and before any comparison is
run. Every method choice below is fixed here, not after seeing data.

Inputs (each asserted against its committed sha256; any mismatch aborts):
  - lean grades of record: s5_grades_A2_lean/*.grades.jsonl
      (manifest s5_grades_A2_lean_sha256_manifest.txt, sha256 a2f2754b...039f)
  - sealed arm key: s5_arm_key_A2_SEALED.json (sha256 af6f985e...cf206)
  - packets: s5_grading_packets_A2/ (manifest 45455851...727b8)
  - spot-check: s5_spotcheck_A2/oppenheimer_spotcheck_verdicts.jsonl
      (sha256 98d5feaf...01dc) + its draw (038ba417...8101)
  - Gemini inter-rater: s5_interrater_A2/<id>.answer_RAW.txt, each checked
      against its meta.json answer_sha256 (the redo run; the VOID run is
      never read).
The two heavy general-purpose grades (8f587d2) are never read (A3 ruling 1).

Metrics (FROZEN-v1 §5, §7):
  - precision per arm = faithful / graded, Wilson 95% CI (z = 1.959964).
  - locator accuracy per arm = faithful / (faithful + wrong-locator).
  - paired difference (Opus - haiku) in precision: point estimate on the
    pooled claims; 95% CI by a paper-cluster bootstrap (resample the 20
    papers with replacement, recompute each arm's pooled precision on the
    resampled papers, take the difference), B = 10000, generator
    numpy default_rng(250125), percentile interval (2.5, 97.5).
  - Cohen's kappa on faithful-vs-not, Opus lean grader vs Gemini, on the 4
    inter-rater papers, both arms: overall and per arm, with raw agreement
    and prevalence = pooled faithful share of both raters on the
    double-graded claims. Small-n rule: if fewer than 40 claims are
    double-graded, kappa is reported but is not a gate. Gate: kappa >= 0.6,
    or (raw agreement >= 0.90 and prevalence > 0.85).
  - spot-check: disagreement = faithful-vs-not differs between
    oppenheimer's verdict and the lean grade for the same (paper, n).
    Pass iff disagreements <= 10 of 50.
  - every metric is also reported per domain (reported, not gated).

Gemini parsing rule (fixed now): from answer_RAW.txt, every line that
parses as a JSON object with integer "n" and string "grade" is taken
(markdown fences and other lines ignored). A claim n missing from Gemini's
output, or a grade outside the six frozen grades, is counted as
`unparsed` and excluded from kappa; the count is reported.

Run under boxrun (deming, seq 226): 1 core, thread-pinned.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

RUN1 = Path(__file__).parent
SEED = 250125
B = 10000
Z = 1.959964
GRADES = {"faithful", "wrong-relation", "wrong-direction", "wrong-modality",
          "wrong-locator", "not-in-paper"}
INTERRATER = ["W4390977661", "W7160385925", "W2015765968", "W4313326288"]

EXPECT = {
    "s5_grades_A2_lean_sha256_manifest.txt":
        "a2f2754bd760d2e1a24b67f79ad05561bf128bd1192f41512ee952b99a8d039f",
    "s5_arm_key_A2_SEALED.json":
        "af6f985e2c6f5e7994718f00a1a2f8aeddcd32915e51b3de58455778c8acf206",
    "s5_grading_packets_A2_sha256_manifest.txt":
        "45455851b8f36f27ecb9aed4a7661c1d48d05825170659f49b91d9f7bec727b8",
    "s5_spotcheck_A2/oppenheimer_spotcheck_verdicts.jsonl":
        "98d5feaf3d70eae66dc58cf6659803c1d5e670bb7844e8be1ff57afdd16601dc",
    "s5_spotcheck_A2/s5_spotcheck_draw.json":
        "038ba41723c9c3d3f25dd41cfd8f2eb7c26229c1becb268ac57a3c669f468101",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_manifest(manifest: Path):
    for line in manifest.read_text().splitlines():
        if not line.strip():
            continue
        h, rel = line.split(maxsplit=1)
        rel = rel.strip()
        p = (RUN1 / rel) if (RUN1 / rel).exists() else (RUN1.parent.parent / rel)
        assert sha(p) == h, f"manifest mismatch: {rel}"


def wilson(k, n):
    if n == 0:
        return (None, None, None)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return (p, c - h, c + h)


def kappa(a, b):
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def load_jsonl(p):
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def main():
    for rel, h in EXPECT.items():
        assert sha(RUN1 / rel) == h, f"sha mismatch: {rel}"
    check_manifest(RUN1 / "s5_grades_A2_lean_sha256_manifest.txt")
    check_manifest(RUN1 / "s5_grading_packets_A2_sha256_manifest.txt")

    key = json.load(open(RUN1 / "s5_arm_key_A2_SEALED.json"))
    arm_values = {c["arm"] for pid in key["order"] for c in key["papers"][pid]["claims"]}
    assert "primary" in arm_values and len(arm_values) == 2, arm_values
    other = (arm_values - {"primary"}).pop()
    ARM = {"primary": "haiku", other: "opus"}

    # rows: one per graded claim
    rows = []
    for pid in key["order"]:
        paper = key["papers"][pid]
        grades = {g["n"]: g["grade"] for g in
                  load_jsonl(RUN1 / "s5_grades_A2_lean" / f"{pid}.grades.jsonl")}
        for c in paper["claims"]:
            g = grades[c["n"]]
            assert g in GRADES, (pid, c["n"], g)
            rows.append({"paper": pid, "domain": paper["domain"], "n": c["n"],
                         "arm": ARM[c["arm"]], "grade": g})
    assert {r["paper"] for r in rows} == set(key["order"]) and len(key["order"]) == 20

    def arm_stats(sub):
        f = sum(r["grade"] == "faithful" for r in sub)
        wl = sum(r["grade"] == "wrong-locator" for r in sub)
        p, lo, hi = wilson(f, len(sub))
        return {"graded": len(sub), "faithful": f, "precision": p,
                "wilson95": [lo, hi], "wrong_locator": wl,
                "locator_accuracy": (f / (f + wl)) if (f + wl) else None,
                "grade_counts": {g: sum(r["grade"] == g for r in sub) for g in sorted(GRADES)}}

    out = {"arms": {}, "by_domain": {}}
    for arm in ("haiku", "opus"):
        out["arms"][arm] = arm_stats([r for r in rows if r["arm"] == arm])
        for d in ("math", "physics"):
            out["by_domain"].setdefault(d, {})[arm] = arm_stats(
                [r for r in rows if r["arm"] == arm and r["domain"] == d])

    # paired difference, paper-cluster bootstrap
    papers = list(key["order"])
    per = {pid: {a: [0, 0] for a in ("haiku", "opus")} for pid in papers}
    for r in rows:
        per[r["paper"]][r["arm"]][0] += r["grade"] == "faithful"
        per[r["paper"]][r["arm"]][1] += 1
    def diff(sample):
        fo = sum(per[p]["opus"][0] for p in sample); no = sum(per[p]["opus"][1] for p in sample)
        fh = sum(per[p]["haiku"][0] for p in sample); nh = sum(per[p]["haiku"][1] for p in sample)
        return fo / no - fh / nh
    rng = np.random.default_rng(SEED)
    boots = [diff([papers[i] for i in rng.integers(0, len(papers), len(papers))]) for _ in range(B)]
    out["paired_difference_opus_minus_haiku"] = {
        "estimate": diff(papers),
        "ci95_paper_cluster_bootstrap": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
        "B": B, "seed": SEED}

    # spot-check
    lean = {(r["paper"], r["n"]): r for r in rows}
    sc = load_jsonl(RUN1 / "s5_spotcheck_A2" / "oppenheimer_spotcheck_verdicts.jsonl")
    dis, sc_rows = 0, []
    for v in sc:
        r = lean[(v["paper"], v["n"])]
        assert r["arm"] == "haiku", (v["paper"], v["n"])
        d = (v["grade"] == "faithful") != (r["grade"] == "faithful")
        dis += d
        sc_rows.append({"paper": v["paper"], "n": v["n"], "domain": v["domain"],
                        "oppenheimer": v["grade"], "lean_grader": r["grade"], "disagree": d})
    out["spot_check"] = {"n": len(sc), "disagreements": dis, "pass": dis <= 10,
                         "category_differences": sum(s["oppenheimer"] != s["lean_grader"] for s in sc_rows),
                         "rows": sc_rows}

    # Gemini inter-rater
    gdir = RUN1 / "s5_interrater_A2"
    pairs, unparsed = [], 0
    for pid in INTERRATER:
        meta = json.load(open(gdir / f"{pid}.meta.json"))
        ans_p = gdir / f"{pid}.answer_RAW.txt"
        assert hashlib.sha256(ans_p.read_text().encode("utf-8")).hexdigest() == meta["answer_sha256"], pid
        gem = {}
        for line in ans_p.read_text().splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(o.get("n"), int) and isinstance(o.get("grade"), str):
                gem[o["n"]] = o["grade"]
        for r in [r for r in rows if r["paper"] == pid]:
            g = gem.get(r["n"])
            if g not in GRADES:
                unparsed += 1
                continue
            pairs.append((r["arm"], r["grade"] == "faithful", g == "faithful"))
    def kblock(ps):
        a = [int(x[1]) for x in ps]; b = [int(x[2]) for x in ps]
        n = len(ps)
        return {"double_graded": n, "kappa": kappa(a, b),
                "raw_agreement": (sum(x == y for x, y in zip(a, b)) / n) if n else None,
                "prevalence": ((sum(a) + sum(b)) / (2 * n)) if n else None}
    ir = {"overall": kblock(pairs), "unparsed": unparsed,
          "per_arm": {arm: kblock([p for p in pairs if p[0] == arm]) for arm in ("haiku", "opus")}}
    o = ir["overall"]
    ir["small_n_rule_applies"] = o["double_graded"] < 40
    ir["gate_pass"] = (None if ir["small_n_rule_applies"] else
                       bool((o["kappa"] is not None and o["kappa"] >= 0.6) or
                            (o["raw_agreement"] >= 0.90 and o["prevalence"] > 0.85)))
    out["inter_rater"] = ir

    # §7 quality gates per arm (cost gate is assessed in the report, not here)
    for arm in ("haiku", "opus"):
        s = out["arms"][arm]
        s["gate_precision"] = bool(s["precision"] >= 0.85 and s["wilson95"][0] >= 0.75)
        s["gate_locator"] = bool(s["locator_accuracy"] is not None and s["locator_accuracy"] >= 0.85)

    res = RUN1 / "s5_analysis_A2_results.json"
    res.write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "spot_check"} |
                     {"spot_check": {k: v for k, v in out["spot_check"].items() if k != "rows"}}, indent=2))
    print("results sha256", sha(res), file=sys.stderr)


if __name__ == "__main__":
    main()
