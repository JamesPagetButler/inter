#!/usr/bin/env python3
"""contextus-seed-corpus round 1 — §2 corpus construction (intake, fan-out,
domain guard, selection, dedup). Pre-reg FROZEN-v1, sha256
f31c62fcf8e4586f947a803123c4b17a122b3ef05146a73465c8e8387608fb17.

Public APIs only (OpenAlex primary, Crossref/arXiv for DOI/arXiv resolution,
Semantic Scholar as a fan-out fallback). Polite rate: >=1.0s between calls,
fetch concurrency 1 (this script is single-threaded/serial by construction).
No PDFs fetched here — this stage is metadata + abstract/title only; full
text extraction happens in the next stage, from a separate per-paper cache.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(RUN_DIR, "corpus_construct_output.json")
LOG = os.path.join(RUN_DIR, "corpus_construct_log.jsonl")

UA = "contextus-seed-corpus-spike/1.0 (Helpful Engineering federation research; mailto:contact@helpfulengineering.org)"
OPENALEX = "https://api.openalex.org/works"

MIN_INTERVAL = 1.0
_last_call = [0.0]


def polite_get(url, what):
    wait = MIN_INTERVAL - (time.time() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read()
            _last_call[0] = time.time()
            return json.loads(body)
    except urllib.error.HTTPError as e:
        _last_call[0] = time.time()
        log_event({"kind": "http_error", "what": what, "url": url, "code": e.code})
        return None
    except Exception as e:
        _last_call[0] = time.time()
        log_event({"kind": "fetch_error", "what": what, "url": url, "error": str(e)})
        return None


_logf = open(LOG, "a")


def log_event(ev):
    ev["ts"] = time.time()
    _logf.write(json.dumps(ev) + "\n")
    _logf.flush()


# --- the 24 seeds, verbatim from oppenheimer's 2026-10-25 comment (inter#121) ---
# fields: domain, n, title, id_kind, id_value, hop, note
SEEDS = [
    ("math", 1, "Scholze (w/ Clausen), Lectures on Condensed Mathematics, 2019", "arxiv", "2605.03658", 1, "2026-posted id, verify-at-intake"),
    ("math", 2, "Scholze (w/ Clausen), Lectures on Analytic Geometry, 2019/20", "arxiv", "2605.03655", 1, "2026-posted id, verify-at-intake"),
    ("math", 3, "Clausen-Scholze, Condensed Mathematics and Complex Geometry, 2022", "title", "Condensed Mathematics and Complex Geometry", 1, "no id (MPIM pdf)"),
    ("math", 4, 'Scholze, "Liquid Tensor Experiment", Exp. Math. 31 (2022)', "doi", "10.1080/10586458.2021.1926016", 1, "seed exception (CS field)"),
    ("math", 5, "Commelin, Abstraction boundaries and spec-driven development in pure mathematics, 2023", "arxiv", "2309.14870", 2, "seed exception (CS field)"),
    ("math", 6, "Asgeirsson, Categorical Foundations of Formalized Condensed Mathematics, JSL 2024", "arxiv", "2309.07252", 1, ""),
    ("math", 7, "Barwick-Haine, Pyknotic objects I, 2019", "arxiv", "1904.09966", 1, ""),
    ("math", 8, "Mann, A p-adic 6-functor formalism in rigid-analytic geometry, 2022", "arxiv", "2206.02022", 2, ""),
    ("math", 9, "Heyer-Mann, 6-Functor Formalisms and Smooth Representations, 2024", "arxiv", "2410.13038", 1, ""),
    ("math", 10, "Johnstone, On a topological topos, Proc. LMS 38 (1979)", "doi", "10.1112/plms/s3-38.2.237", 2, ""),
    ("math", 11, "Lurie, Ultracategories, 2018 notes", "title", "Ultracategories", 2, "no id (IAS pdf)"),
    ("math", 12, "Clausen-Scholze, Analytic Stacks, 2023/24 course", "title", "Analytic Stacks", 2, "no id (video course)"),
    ("physics", 1, 'Chamseddine-Connes, "The spectral action principle", CMP 186 (1997)', "arxiv", "hep-th/9606001", 1, ""),
    ("physics", 2, 'Chamseddine-Connes-van Suijlekom, "Entropy and the spectral action", CMP 2019', "arxiv", "1809.02944", 1, ""),
    ("physics", 3, 'Connes, "Noncommutative geometry and reality", JMP 36 (1995)', "doi", "10.1063/1.531241", 1, ""),
    ("physics", 4, 'Bar, "The Dirac operator on space forms of positive curvature", J. Math. Soc. Japan 48 (1996)', "doi", "10.2969/jmsj/04810069", 1, ""),
    ("physics", 5, 'Camporesi-Higuchi, "Eigenfunctions of the Dirac operator on spheres and real hyperbolic spaces", JGP 20 (1996)', "arxiv", "gr-qc/9505009", 1, ""),
    ("physics", 6, 'Trautman, "The Dirac operator on hypersurfaces", Acta Phys. Polon. B 26 (1995)', "arxiv", "hep-th/9810018", 2, ""),
    ("physics", 7, 'Harvey-Lawson, "Calibrated geometries", Acta Math. 148 (1982)', "doi", "10.1007/BF02392726", 2, ""),
    ("physics", 8, 'Hitchin, "The geometry of three-forms in six and seven dimensions", JDG 55 (2000)', "arxiv", "math/0010054", 2, ""),
    ("physics", 9, "Bryant, Some remarks on G2-structures, Gokova 2005", "arxiv", "math/0305124", 2, ""),
    ("physics", 10, 'Baez, "The Octonions", Bull. AMS 39 (2002)', "arxiv", "math/0105155", 1, ""),
    ("physics", 11, "Lawson-Michelsohn, Spin Geometry, 1989", "isbn", "9780691085425", 2, "book, no DOI/arXiv"),
    ("physics", 12, "Capoferri, Global and microlocal aspects of Dirac operators, Math. Nachr. 2025", "unverified", "", 1, "id unverified per oppenheimer"),
]

ADMITTED_FIELDS = {"Mathematics", "Physics and Astronomy"}
EXCLUDED_NAMED = {"Life Sciences", "Health Sciences"}
SEED_EXCEPTION_TITLES = {
    "Liquid Tensor Experiment",
    "Abstraction boundaries and spec-driven development in pure mathematics",
}


def arxiv_doi(arxiv_id):
    # DataCite DOI minted for every arXiv submission since 2022-10.
    return f"10.48550/arXiv.{arxiv_id}"


def openalex_by_doi(doi):
    url = OPENALEX + "/doi:" + urllib.parse.quote(doi, safe="")
    return polite_get(url, f"doi:{doi}")


def openalex_search_title(title):
    url = OPENALEX + "?filter=" + urllib.parse.quote(f"title.search:{title}") + "&per_page=5"
    data = polite_get(url, f"title-search:{title}")
    if not data or not data.get("results"):
        return None
    return data["results"][0]


def primary_field(work):
    topic = work.get("primary_topic") or {}
    field = (topic.get("field") or {}).get("display_name")
    return field


def resolve_seed(seed):
    domain, n, title, id_kind, id_value, hop, note = seed
    work = None
    resolved_doi = None
    if id_kind == "doi":
        resolved_doi = id_value
        work = openalex_by_doi(id_value)
    elif id_kind == "arxiv":
        resolved_doi = arxiv_doi(id_value)
        work = openalex_by_doi(resolved_doi)
        if work is None:
            work = openalex_search_title(title.split(",")[0])
    elif id_kind in ("title", "isbn", "unverified"):
        work = openalex_search_title(title)

    status = "resolved" if work else "unresolved"
    rec = {
        "domain": domain, "seed_n": n, "title": title, "id_kind": id_kind,
        "id_value": id_value, "hop_limit": hop, "note": note,
        "status": status,
        "openalex_id": work.get("id") if work else None,
        "field": primary_field(work) if work else None,
        "is_seed": True,
    }
    return rec


def fan_out(seed_rec, hop_limit):
    """Hop limit <=2 from one seed. Returns list of candidate dicts with
    {openalex_id, field, link_count(from this seed), hops}."""
    if seed_rec["status"] != "resolved":
        return []
    out = {}
    frontier = {seed_rec["openalex_id"]}
    seen = {seed_rec["openalex_id"]}
    for hop in range(1, hop_limit + 1):
        next_frontier = set()
        for wid in frontier:
            short = wid.rsplit("/", 1)[-1]
            # references (backward)
            fwd = polite_get(OPENALEX + f"/{short}", f"work:{short}")
            refs = (fwd or {}).get("referenced_works") or []
            # citations (forward) — capped page size to keep this tractable
            cit = polite_get(
                OPENALEX + f"?filter=cites:{short}&per_page=50", f"cites:{short}"
            )
            cit_ids = [w["id"] for w in (cit or {}).get("results", [])]
            for cand in list(refs)[:50] + cit_ids:
                if cand in seen:
                    continue
                next_frontier.add(cand)
                rec = out.setdefault(cand, {"openalex_id": cand, "hops": hop, "link_count": 0})
                rec["link_count"] += 1
                rec["hops"] = min(rec["hops"], hop)
        seen |= next_frontier
        frontier = next_frontier
    return list(out.values())


def main():
    log_event({"kind": "start"})
    seed_recs = []
    for s in SEEDS:
        rec = resolve_seed(s)
        seed_recs.append(rec)
        log_event({"kind": "seed_resolved", **{k: rec[k] for k in ("domain", "seed_n", "status", "field")}})

    candidates = {}  # openalex_id -> {domain_votes: {math: score, physics: score}, hops_min, is_seed, seed_field}
    for rec in seed_recs:
        if rec["status"] != "resolved":
            continue
        candidates[rec["openalex_id"]] = {
            "openalex_id": rec["openalex_id"], "is_seed": True,
            "seed_domain": rec["domain"], "field": rec["field"],
            "score_by_domain": {rec["domain"]: 1000.0},  # seeds always selected
            "hops_min": 0,
        }
        fo = fan_out(rec, rec["hop_limit"])
        for cand in fo:
            wid = cand["openalex_id"]
            entry = candidates.setdefault(wid, {
                "openalex_id": wid, "is_seed": False, "field": None,
                "score_by_domain": {}, "hops_min": cand["hops"],
            })
            entry["hops_min"] = min(entry["hops_min"], cand["hops"])
            penalty = 0.5 * max(0, cand["hops"] - 1)
            entry["score_by_domain"][rec["domain"]] = (
                entry["score_by_domain"].get(rec["domain"], 0.0) + 1.0 - penalty
            )

    log_event({"kind": "fanout_done", "n_candidates": len(candidates)})

    # Rank BEFORE spending any more API calls: the guard/metadata fetch is
    # the expensive step (one call per candidate), so only run it on a
    # generous top-N per domain bucket, picked by the link-score computed
    # above (no extra calls needed for that). N=400/domain is a wide buffer
    # over the 50/domain final target to absorb out-of-domain drops + dedup.
    GUARD_TOPN = 400
    guard_pool = {}
    for dom in ("math", "physics"):
        ranked_ids = sorted(
            (wid for wid, c in candidates.items() if dom in c["score_by_domain"]),
            key=lambda wid: -candidates[wid]["score_by_domain"][dom],
        )[:GUARD_TOPN]
        for wid in ranked_ids:
            guard_pool[wid] = candidates[wid]
    for rec in seed_recs:
        if rec["status"] == "resolved":
            guard_pool[rec["openalex_id"]] = candidates[rec["openalex_id"]]

    log_event({
        "kind": "guard_pool_selected", "n_candidates_total": len(candidates),
        "n_guard_pool": len(guard_pool),
    })

    # domain-guard pass (metadata only) for the capped candidate pool
    out_of_domain = []
    in_domain = []
    for wid, c in guard_pool.items():
        if c["is_seed"]:
            in_domain.append(c)
            continue
        short = wid.rsplit("/", 1)[-1]
        work = polite_get(OPENALEX + f"/{short}", f"guard:{short}")
        field = primary_field(work) if work else None
        c["field"] = field
        title = (work or {}).get("title") or ""
        c["title"] = title
        year = (work or {}).get("publication_year")
        c["year"] = year
        if field in ADMITTED_FIELDS:
            in_domain.append(c)
        elif field is None:
            out_of_domain.append({**c, "reason": "no-openalex-topic"})
        else:
            out_of_domain.append({**c, "reason": f"field={field}"})

    log_event({
        "kind": "domain_guard_done",
        "in_domain": len(in_domain), "out_of_domain": len(out_of_domain),
    })

    # selection: rank by score desc within each domain, take 50/domain
    by_domain = {"math": [], "physics": []}
    for c in in_domain:
        for dom, score in c.get("score_by_domain", {}).items():
            by_domain.setdefault(dom, []).append((score, c))
    # map math/physics domain naming consistent with seed domains above
    selected = {}
    bridge_flagged = []
    for dom in ("math", "physics"):
        ranked = sorted(by_domain.get(dom, []), key=lambda t: (-t[0], t[1].get("year") or 0, t[1]["openalex_id"]))
        taken = 0
        for score, c in ranked:
            if taken >= 50:
                break
            wid = c["openalex_id"]
            if wid in selected:
                # bridge: linked to both domains — counts once, toward higher score
                other_score = selected[wid]["score"]
                if score > other_score:
                    selected[wid] = {"c": c, "score": score, "domain": dom}
                bridge_flagged.append(wid)
                continue
            selected[wid] = {"c": c, "score": score, "domain": dom}
            taken += 1

    log_event({"kind": "selection_done", "selected": len(selected), "bridge": len(set(bridge_flagged))})

    # dedup: canonical id norm already implicit (OpenAlex ids are canonical);
    # title token-Jaccard >= 0.85 as a secondary pass
    def norm_title(t):
        return re.sub(r"[^a-z0-9 ]", "", (t or "").lower())

    def jaccard(a, b):
        sa, sb = set(a.split()), set(b.split())
        if not sa or not sb:
            return 0.0
        return len(sa & sb) / len(sa | sb)

    items = list(selected.items())
    merged_log = []
    dropped = set()
    for i in range(len(items)):
        wid_i, info_i = items[i]
        if wid_i in dropped:
            continue
        ti = norm_title(info_i["c"].get("title", ""))
        for j in range(i + 1, len(items)):
            wid_j, info_j = items[j]
            if wid_j in dropped:
                continue
            tj = norm_title(info_j["c"].get("title", ""))
            if ti and tj and jaccard(ti, tj) >= 0.85:
                dropped.add(wid_j)
                merged_log.append({"kept": wid_i, "dropped": wid_j, "reason": "title-jaccard>=0.85"})

    final_selected = {wid: info for wid, info in selected.items() if wid not in dropped}

    result = {
        "pre_reg_sha256": "f31c62fcf8e4586f947a803123c4b17a122b3ef05146a73465c8e8387608fb17",
        "seeds": seed_recs,
        "candidates_total_raw_fanout": len(candidates),
        "guard_pool_size": len(guard_pool),
        "methods_note_guard_scope": (
            f"Domain-guard metadata fetch ran only on the top-{GUARD_TOPN}/domain "
            f"link-score pool ({len(guard_pool)} of {len(candidates)} raw fan-out "
            "candidates) to keep the API-call count tractable within the box-safety "
            "wall-clock budget; the remaining "
            f"{len(candidates) - len(guard_pool)} low-score candidates were never "
            "guard-checked or fetched. Q4's excluded-fraction-per-hop figure below "
            "is therefore computed over the guard pool only, not the full raw "
            "fan-out. Disclosed deviation from FROZEN-v1 (sha "
            "f31c62fc...8fb17) §2.3a's literal 'every other field excluded' "
            "scope; flagged to the director rather than silently narrowed."
        ),
        "in_domain": len(in_domain),
        "out_of_domain": [
            {"openalex_id": c["openalex_id"], "hops": c["hops_min"], "reason": c["reason"]}
            for c in out_of_domain
        ],
        "selected_count_pre_dedup": len(selected),
        "dedup_merges": merged_log,
        "selected_final": [
            {
                "openalex_id": wid, "domain": info["domain"], "score": info["score"],
                "title": info["c"].get("title"), "year": info["c"].get("year"),
                "is_seed": info["c"].get("is_seed", False),
                "bridge": wid in set(bridge_flagged),
            }
            for wid, info in final_selected.items()
        ],
    }
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)
    log_event({"kind": "done", "final_count": len(final_selected)})
    print(json.dumps({
        "seeds_resolved": sum(1 for r in seed_recs if r["status"] == "resolved"),
        "seeds_unresolved": sum(1 for r in seed_recs if r["status"] != "resolved"),
        "candidates_total": len(candidates),
        "in_domain": len(in_domain),
        "out_of_domain": len(out_of_domain),
        "selected_pre_dedup": len(selected),
        "dedup_merges": len(merged_log),
        "final_count": len(final_selected),
    }, indent=2))


if __name__ == "__main__":
    main()
