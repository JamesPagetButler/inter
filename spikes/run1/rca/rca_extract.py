#!/usr/bin/env python3
"""Round-1 grader RCA: extract the disagreement items (plan: rca/RCA-PLAN.md).

Read-only over committed files. Writes rca/rca_items.jsonl and prints its sha256.
An item is a claim where the lean grader and a second rater disagree on
faithful vs not-faithful (the same binary the §7 κ used):
  - source "gemini": the 4 committed Gemini answers (s5_interrater_A2, not VOID);
  - source "oppenheimer": the 50 spot-check verdicts (s5_spotcheck_A2).
Arm is deliberately omitted so the reader classifies causes blind to arm.
Items are sorted by (source, paper, n); no randomness.
"""
import hashlib
import json
import sys
from pathlib import Path

RUN1 = Path(__file__).resolve().parent.parent
OUT = RUN1 / "rca" / "rca_items.jsonl"
GEMINI = ["W4390977661", "W7160385925", "W2015765968", "W4313326288"]
EXPECT = {  # committed inputs, checked before anything is read
    "s5_analysis_A2_results.json": "02879c1dcc11506378f9c6908b9b53b6bba4b57e530b122ed6b3498c58c94621",
    "s5_spotcheck_A2/oppenheimer_spotcheck_verdicts.jsonl": "98d5feaf3d70eae66dc58cf6659803c1d5e670bb7844e8be1ff57afdd16601dc",
}
EXPECTED_COUNTS = {"gemini": 12, "oppenheimer": 7}  # from the results of record


def must(cond, msg):
    if not cond:
        print(f"RCA EXTRACT FAILED: {msg}", file=sys.stderr)
        sys.exit(1)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def jsonl(p):
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def faithful(g):
    return g == "faithful"


def main():
    for rel, h in EXPECT.items():
        must(sha(RUN1 / rel) == h, f"sha mismatch: {rel}")
    capped = {r["openalex_id"].rsplit("/", 1)[-1]: r.get("approx_tokens") == 10000
              for r in jsonl(RUN1 / "text_cache_manifest.jsonl") if r["status"] == "ok"}

    def lean(pid):
        return {g["n"]: g for g in jsonl(RUN1 / "s5_grades_A2_lean" / f"{pid}.grades.jsonl")}

    def packet(pid):
        return json.load(open(RUN1 / "s5_grading_packets_A2" / f"{pid}.grading_packet.json"))

    items = []

    def add(source, pid, n, other_grade, other_reason):
        L = lean(pid)
        must(n in L, (pid, n))
        if faithful(L[n]["grade"]) == faithful(other_grade):
            return
        pk = packet(pid)
        c = [x for x in pk["claims"] if x["n"] == n]
        must(len(c) == 1, (pid, n, "claim not in packet"))
        c = c[0]
        loc = str(c.get("locator") or "")
        items.append({
            "source": source, "paper": pid, "domain": pk["domain"], "n": n,
            "claim": {k: c.get(k) for k in ("subject", "relation", "object", "modality", "locator")},
            "lean": {"grade": L[n]["grade"], "reason": L[n].get("reason")},
            "other": {"rater": source, "grade": other_grade, "reason": other_reason},
            "signals": {  # mechanical hints for the reader; not causes
                "text_capped": capped.get(pid),
                "locator_string_in_packet_text": bool(loc) and loc in pk["text"],
            },
            "cause": None, "fix": None,  # filled by the RCA reading, not here
        })

    for pid in GEMINI:
        meta = json.load(open(RUN1 / "s5_interrater_A2" / f"{pid}.meta.json"))
        ans = RUN1 / "s5_interrater_A2" / f"{pid}.answer_RAW.txt"
        must(sha(ans) == meta["answer_sha256"], f"{pid} answer sha")
        seen = {}
        for line in ans.read_text().splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(o.get("n"), int):
                    must(o["n"] not in seen or seen[o["n"]]["grade"] == o["grade"], (pid, o["n"], "conflict"))
                    seen[o["n"]] = o
        for n, o in sorted(seen.items()):
            add("gemini", pid, n, o["grade"], o.get("reason"))

    for v in jsonl(RUN1 / "s5_spotcheck_A2" / "oppenheimer_spotcheck_verdicts.jsonl"):
        add("oppenheimer", v["paper"], v["n"], v["grade"], v.get("reason"))

    items.sort(key=lambda r: (r["source"], r["paper"], r["n"]))
    got = {s: sum(r["source"] == s for r in items) for s in EXPECTED_COUNTS}
    must(got == EXPECTED_COUNTS, f"item counts {got} != {EXPECTED_COUNTS}")
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in items))
    print(f"items {len(items)} {got}")
    print(f"rca_items.jsonl sha256 {sha(OUT)}")


if __name__ == "__main__":
    main()
