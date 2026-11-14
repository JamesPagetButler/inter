#!/usr/bin/env python3
"""cap-e824bdcb: real fetch+parse (process_paper, new merged code) against
all 48 non-ok papers in text_cache_manifest.jsonl, to get the one true
figure the architect asked for (spike-seed-corpus-s4#75): how many of the
48 reach status "ok" under the new parser, split by domain.

READ-ONLY against text_cache_manifest.jsonl (never written back to).
Writes a SIDE file: real_coverage_results.jsonl (one record per paper,
process_paper()'s own result dict + domain).

Network+parse only -- zero LLM calls, no restatement/extraction stage
touched. Stop condition: natural stop at 48/48; this script has no retry
loop beyond what process_paper() already does (MAX_PAPER_ATTEMPTS=2 at the
paper level), so it cannot spin.
"""
import json
import os
import sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RUN_DIR)

import arxiv_text_cache as atc  # noqa: E402

MANIFEST = os.path.join(RUN_DIR, "text_cache_manifest.jsonl")
INPUT = os.path.join(RUN_DIR, "corpus_construct_output.json")
RESULTS_OUT = os.path.join(RUN_DIR, "real_coverage_results.jsonl")


def main():
    with open(MANIFEST) as f:
        manifest = [json.loads(l) for l in f if l.strip()]
    not_ok = [r for r in manifest if r.get("status") != "ok"]

    with open(INPUT) as f:
        data = json.load(f)
    papers_by_id = {p["openalex_id"]: p for p in data["selected_final"]}

    results = []
    n_now_ok = 0
    by_domain = {}
    with open(RESULTS_OUT, "w") as out:
        for i, rec in enumerate(not_ok, 1):
            oaid = rec["openalex_id"]
            paper = papers_by_id.get(oaid)
            if paper is None:
                print(f"[{i}/{len(not_ok)}] {oaid}: SKIP (not in corpus_construct_output.json)", file=sys.stderr)
                continue
            domain = paper.get("domain", "unknown")
            result = atc.process_paper(paper)
            result["domain"] = domain
            result["prior_status"] = rec.get("status")
            results.append(result)
            out.write(json.dumps(result) + "\n")
            out.flush()
            now_ok = result["status"] == "ok"
            if now_ok:
                n_now_ok += 1
            slot = by_domain.setdefault(domain, {"checked": 0, "now_ok": 0})
            slot["checked"] += 1
            if now_ok:
                slot["now_ok"] += 1
            print(f"[{i}/{len(not_ok)}] {oaid} ({domain}): {result['status']} "
                  f"(n_statements={result['n_statements_found']}, source={result['source']})",
                  file=sys.stderr)

    summary = {
        "n_checked": len(results),
        "n_not_ok_in_manifest": len(not_ok),
        "n_now_ok": n_now_ok,
        "by_domain": by_domain,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
