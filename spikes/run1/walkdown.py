#!/usr/bin/env python3
"""A1 §3 walk-down.

Step 1 (reproduce): re-run corpus_construct.build_corpus() in full (same
seeds, same frozen fan-out/domain-guard logic) and confirm selected_final
matches the committed corpus_construct_output.json exactly, in order. Any
mismatch stops here -- no walk-down.

Step 2+ (walk-down): per domain, continue down the SAME frozen ranked
candidate list past the original admission cursor, in batches of 150,
guard-checking (reusing corpus_construct's own guard_one, so domain
classification is byte-identical to the already-accepted run) and then
text-fetching each newly admitted candidate with the frozen 432d049
fetcher (arxiv_text_cache.process_paper), until 50 ACCESSIBLE papers/
domain (admitted AND text status "ok"). Every candidate tried is logged
to walkdown_log.jsonl: rank-order position, domain, hop, guard result,
text status, reason.

K1 (qbp-architecture seq 5106/134): stops the whole walk-down the moment
3 true zero-statement candidates are found (page reached, parser found
nothing -- not a fetch/arxiv-id/OA-location failure), for the director's
hand-inspection before anything continues.

Network + parsing only, zero model calls. Runs under boxrun as the only
IO-heavy job on the box (A1 §3, deming seq 119/5109).
"""
import json
import os
import sys
import time

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RUN_DIR)
import corpus_construct as cc
import arxiv_text_cache as atc

EXISTING_OUT = os.path.join(RUN_DIR, "corpus_construct_output.json")
MANIFEST = os.path.join(RUN_DIR, "text_cache_manifest.jsonl")
WALKDOWN_LOG = os.path.join(RUN_DIR, "walkdown_log.jsonl")
WALKDOWN_STATE = os.path.join(RUN_DIR, "walkdown_state.json")
REPRODUCED_RANKED = os.path.join(RUN_DIR, "reproduced_ranked_candidates.json")
REPRODUCED_SELECTED = os.path.join(RUN_DIR, "reproduced_selected_final.json")
REPRODUCE_DIFF = os.path.join(RUN_DIR, "reproduce_diff.json")

TARGET_PER_DOMAIN = 50
BATCH = 150
ZERO_STOP = 3


class K1Stop(Exception):
    pass


def log_wd(ev):
    ev["ts"] = time.time()
    with open(WALKDOWN_LOG, "a") as f:
        f.write(json.dumps(ev) + "\n")
        f.flush()


def guard_with_retry(state, wid, attempts=3):
    """A1 §7 K2: a fetch failure is retried twice (3 attempts total) before
    it is logged as a pipeline error."""
    g = None
    for i in range(attempts):
        g = state["guard_one"](wid)
        if g["status"] != "fetch_failed":
            return g, i + 1
        del state["guarded"][wid]
    return g, attempts


def last_paper_status_reason(oaid):
    """arxiv_text_cache.process_paper() logs its own per-paper reason (not
    carried in the returned dict); read it back from the tail of its log
    rather than duplicate that logic here."""
    try:
        with open(atc.LOG, "rb") as f:
            lines = f.read().decode("utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return None
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("kind") == "paper_status" and ev.get("openalex_id") == oaid:
            return ev.get("reason")
    return None


def main():
    with open(EXISTING_OUT) as f:
        existing = json.load(f)
    existing_selected = existing["selected_final"]
    domain_of_existing = {c["openalex_id"]: c["domain"] for c in existing_selected}

    with open(MANIFEST) as f:
        manifest = [json.loads(l) for l in f if l.strip()]
    ok_ids = {r["openalex_id"] for r in manifest if r.get("status") == "ok"}
    accessible_count = {"math": 0, "physics": 0}
    for oaid, dom in domain_of_existing.items():
        if oaid in ok_ids:
            accessible_count[dom] += 1
    print(f"already-accessible: {accessible_count}", file=sys.stderr, flush=True)

    print("reproducing corpus construction (full fan-out re-run)...", file=sys.stderr, flush=True)
    state = cc.build_corpus()
    new_selected = state["result"]["selected_final"]

    # qbp-architecture seq 145 / qbp-oppenheimer seq 147: write the full
    # reproduced ranked candidate list per domain (with scores), the
    # reproduced selected_final, and the diff -- to disk, BEFORE the
    # stop-on-mismatch check, so a mismatch can be decided from evidence
    # without a re-fetch. Logging only, no rule change.
    ranked_with_scores = {
        dom: [
            {
                "openalex_id": wid,
                "score": state["candidates"][wid]["score_by_domain"].get(dom),
                "hops_min": state["candidates"][wid].get("hops_min"),
                "is_seed": state["candidates"][wid].get("is_seed", False),
            }
            for wid in state["ranked_ids_by_domain"][dom]
        ]
        for dom in ("math", "physics")
    }
    with open(REPRODUCED_RANKED, "w") as f:
        json.dump(ranked_with_scores, f, indent=2)
    with open(REPRODUCED_SELECTED, "w") as f:
        json.dump(new_selected, f, indent=2)

    old_tuples = [(c["openalex_id"], c["domain"]) for c in existing_selected]
    new_tuples = [(c["openalex_id"], c["domain"]) for c in new_selected]
    match = old_tuples == new_tuples
    diff = {
        "match": match,
        "old_count": len(old_tuples),
        "new_count": len(new_tuples),
        "old_only": [t for t in old_tuples if t not in set(new_tuples)],
        "new_only": [t for t in new_tuples if t not in set(old_tuples)],
        "first_order_divergence_index": next(
            (i for i, (a, b) in enumerate(zip(old_tuples, new_tuples)) if a != b), None
        ) if not match else None,
    }
    with open(REPRODUCE_DIFF, "w") as f:
        json.dump(diff, f, indent=2)

    if not match:
        log_wd({"kind": "REPRODUCE_MISMATCH", "old_count": len(old_tuples), "new_count": len(new_tuples)})
        print(json.dumps({"reproduce": "MISMATCH", "diff": diff}, indent=2))
        sys.exit(2)
    log_wd({"kind": "reproduce_ok", "n": len(old_tuples)})
    print(f"REPRODUCE: exact match, {len(old_tuples)} papers", file=sys.stderr, flush=True)

    zero_statement_found = []
    tried = {"math": 0, "physics": 0}
    newly_accessible = {"math": [], "physics": []}
    pipeline_errors = {"math": 0, "physics": 0}

    try:
        for dom in ("math", "physics"):
            ranked_ids = state["ranked_ids_by_domain"][dom]
            cursor = state["cursor_by_domain"][dom]
            while accessible_count[dom] < TARGET_PER_DOMAIN and cursor < len(ranked_ids):
                batch = ranked_ids[cursor:cursor + BATCH]
                cursor += BATCH
                for wid in batch:
                    if wid in domain_of_existing:
                        continue  # already tried as part of the original 99/100
                    if accessible_count[dom] >= TARGET_PER_DOMAIN:
                        break
                    tried[dom] += 1
                    g, n_attempts = guard_with_retry(state, wid)
                    hop = (state["candidates"].get(wid) or {}).get("hops_min")
                    entry = {
                        "kind": "candidate_tried", "domain": dom, "openalex_id": wid,
                        "hop": hop, "guard_status": g["status"], "guard_attempts": n_attempts,
                    }
                    if g["status"] == "fetch_failed":
                        entry["pipeline_error"] = True
                        pipeline_errors[dom] += 1
                        log_wd(entry)
                        continue
                    if g["status"] == "out_of_domain":
                        entry["reason"] = g.get("reason")
                        log_wd(entry)
                        continue
                    paper_rec = atc.process_paper({"openalex_id": wid})
                    with open(MANIFEST, "a") as mf:
                        mf.write(json.dumps(paper_rec) + "\n")
                    entry["text_status"] = paper_rec["status"]
                    entry["arxiv_id"] = paper_rec.get("arxiv_id")
                    entry["n_statements_found"] = paper_rec.get("n_statements_found")
                    if paper_rec["status"] == "ok":
                        accessible_count[dom] += 1
                        newly_accessible[dom].append(wid)
                        entry["reason"] = None
                    else:
                        reason = last_paper_status_reason(wid)
                        entry["reason"] = reason
                        if reason in ("no-statements-parsed", "oa-fallback-no-statements"):
                            zero_statement_found.append({
                                "openalex_id": wid, "domain": dom,
                                "arxiv_id": paper_rec.get("arxiv_id"), "reason": reason,
                            })
                    log_wd(entry)
                    if len(zero_statement_found) >= ZERO_STOP:
                        raise K1Stop()
                log_wd({
                    "kind": "batch_done", "domain": dom, "cursor": cursor,
                    "accessible_so_far": accessible_count[dom], "tried_so_far": tried[dom],
                })
    except K1Stop:
        pass

    summary = {
        "reproduce": "OK",
        "accessible_count": accessible_count,
        "tried": tried,
        "pipeline_errors": pipeline_errors,
        "newly_accessible": newly_accessible,
        "zero_statement_found": zero_statement_found,
        "stopped_early_for_K1": len(zero_statement_found) >= ZERO_STOP,
    }
    with open(WALKDOWN_STATE, "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
