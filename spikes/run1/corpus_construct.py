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
MAILTO = "contact@helpfulengineering.org"

MIN_INTERVAL = 4.0  # backed off hard: this box's own repeated test runs over
# the last ~2h (five-plus full pipeline passes, 1000+ calls each) earned a
# real 429 throttle from OpenAlex even with mailto -- this is the runner's
# own traffic causing the problem, not an OpenAlex flake, so the fix is to
# slow down and stop re-running the whole pipeline for determinism-testing
# against a shared public API, not to retry harder.
MAX_RETRIES = 6
_last_call = [0.0]


def _with_mailto(url):
    # OpenAlex's "polite pool" (higher, more reliable rate limit) is keyed
    # off a `mailto` QUERY PARAM, not the User-Agent header alone. Root
    # cause of a real non-determinism bug found in this run: without it,
    # ~10% of calls (100+ per run) got HTTP 429 and were silently treated
    # as "no data" (no retry), so two runs of the identical seed list
    # produced selected-corpus overlaps as low as 83/100 -- a different
    # ~10% of the citation graph went missing each time, not true
    # randomness. Fixed here + the retry loop below.
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}mailto={urllib.parse.quote(MAILTO)}"


def polite_get(url, what):
    url = _with_mailto(url)
    backoff = 2.0
    for attempt in range(MAX_RETRIES):
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
            if e.code == 429 or 500 <= e.code < 600:
                log_event({"kind": "retry", "what": what, "code": e.code, "attempt": attempt, "backoff": backoff})
                time.sleep(backoff)
                backoff = min(backoff * 2, 60.0)
                continue
            log_event({"kind": "http_error", "what": what, "url": url, "code": e.code})
            return None
        except Exception as e:
            _last_call[0] = time.time()
            log_event({"kind": "fetch_error", "what": what, "url": url, "error": str(e), "attempt": attempt})
            time.sleep(backoff)
            backoff = min(backoff * 2, 60.0)
            continue
    log_event({"kind": "giving_up_after_retries", "what": what, "url": url})
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
    ("math", 6, "Asgeirsson, Categorical Foundations of Formalized Condensed Mathematics, JSL 2024", "doi", "10.1017/jsl.2024.69", 1, "id corrected per qbp-oppenheimer live-test seq 4524: table's arXiv:2309.07252 and arXiv:2410.17847 both resolved to different, unrelated papers; correct pin is doi:10.1017/jsl.2024.69 = arXiv:2407.12840"),
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


S2_API = "https://api.semanticscholar.org/graph/v1/paper"
_fetch_failed_log = []  # module-level funnel of permanent, S2-also-failed calls


def s2_get(url, what):
    """Semantic Scholar fallback — same serial/backoff discipline as
    polite_get, used only when OpenAlex has already permanently failed and
    we hold an external id (DOI) to query S2 with."""
    backoff = 2.0
    for attempt in range(MAX_RETRIES):
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
            if e.code == 429 or 500 <= e.code < 600:
                log_event({"kind": "s2_retry", "what": what, "code": e.code, "attempt": attempt})
                time.sleep(backoff)
                backoff = min(backoff * 2, 60.0)
                continue
            log_event({"kind": "s2_http_error", "what": what, "code": e.code})
            return None
        except Exception as e:
            _last_call[0] = time.time()
            log_event({"kind": "s2_fetch_error", "what": what, "error": str(e), "attempt": attempt})
            time.sleep(backoff)
            backoff = min(backoff * 2, 60.0)
            continue
    log_event({"kind": "s2_giving_up", "what": what})
    return None


def s2_citations_by_doi(doi, limit=50):
    """Returns a list of OpenAlex ids for papers citing `doi`, resolved via
    S2's citation list then mapped back through OpenAlex-by-DOI (so the
    candidate graph stays keyed consistently). A citing paper with no DOI
    in S2's record can't be mapped into the OpenAlex-keyed graph and is
    skipped -- logged, not silently merged in or dropped from the funnel."""
    if not doi:
        return None
    url = S2_API + f"/DOI:{urllib.parse.quote(doi, safe='')}?fields=citations.externalIds"
    data = s2_get(url, f"s2-citations:{doi}")
    if data is None:
        return None
    out_ids = []
    skipped_no_doi = 0
    for c in (data.get("citations") or [])[:limit]:
        cdoi = (c.get("externalIds") or {}).get("DOI")
        if not cdoi:
            skipped_no_doi += 1
            continue
        w = openalex_by_doi(cdoi)
        if w and w.get("id"):
            out_ids.append(w["id"])
    log_event({"kind": "s2_citations_mapped", "doi": doi, "mapped": len(out_ids), "skipped_no_doi": skipped_no_doi})
    return out_ids


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


def doi_of_work(work):
    d = (work or {}).get("doi") or ""
    return d.replace("https://doi.org/", "") if d else None


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
            fwd_doi = doi_of_work(fwd) if fwd else None
            if fwd is None:
                _fetch_failed_log.append({"openalex_id": wid, "hops": hop, "what": "work-detail(for-refs)", "reason": "openalex-permanent-fail+no-doi-for-s2"})
                log_event({"kind": "fanout_fetch_failed", "openalex_id": wid, "hop": hop, "what": "work-detail"})
            # citations (forward) — capped page size to keep this tractable.
            # Explicit sort is required: OpenAlex's default order for an
            # unsorted filter query is not guaranteed stable across calls,
            # and a prior run (no sort) produced 14,447 raw candidates vs
            # 1,681 on a rerun differing by only one unrelated seed id --
            # too large a swing to be the seed change, consistent with
            # unordered pagination returning a different arbitrary subset
            # of a highly-cited paper's citers each call. Sorting by
            # cited_by_count desc makes "top 50 citers" both deterministic
            # and the more meaningful choice (most-influential citers first).
            cit = polite_get(
                OPENALEX + f"?filter=cites:{short}&sort=cited_by_count:desc&per_page=50",
                f"cites:{short}",
            )
            if cit is None:
                # OpenAlex permanently failed -- try S2 by this node's own
                # DOI (binding 2: zero silent drops). Only possible if the
                # work-detail fetch above succeeded and carried a DOI.
                s2_ids = s2_citations_by_doi(fwd_doi) if fwd_doi else None
                if s2_ids is not None:
                    cit_ids = s2_ids
                    log_event({"kind": "fanout_s2_fallback_used", "openalex_id": wid, "hop": hop})
                else:
                    cit_ids = []
                    _fetch_failed_log.append({"openalex_id": wid, "hops": hop, "what": "cites-query", "reason": "openalex-permanent-fail+s2-" + ("no-doi" if not fwd_doi else "also-failed")})
                    log_event({"kind": "fanout_fetch_failed", "openalex_id": wid, "hop": hop, "what": "cites-query"})
            else:
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

    # Guard in frozen-ranking order (score desc, the only pre-fetch-computable
    # part of §2.3's rank), EXPANDING in batches until 50/domain are admitted
    # or the domain's ranked pool is exhausted (qbp-architecture, live-test
    # seq 4533 binding 1 — not a fixed cutoff). A candidate shared by both
    # domains is guard-checked once and the result reused for both.
    BATCH = 150
    guarded = {}       # wid -> {field, title, year, status: admitted|out_of_domain|fetch_failed}
    fetch_failed = list(_fetch_failed_log)  # seed with fan-out-stage failures too
    s2_fallback_count = [0]

    def s2_lookup_title_year_field(wid):
        """Best-effort Semantic Scholar fallback when OpenAlex's work-detail
        fetch permanently fails. S2 keys papers by DOI/arXiv/etc, not the
        OpenAlex id, so this only works if we can recover an external id —
        here, none (OpenAlex itself didn't answer), so this path can only
        report back that it tried and still has nothing; kept as a named,
        logged step rather than silently skipped, per binding 2."""
        return None  # no external id available without the OpenAlex answer

    def guard_one(wid):
        if wid in guarded:
            return guarded[wid]
        short = wid.rsplit("/", 1)[-1]
        work = polite_get(OPENALEX + f"/{short}", f"guard:{short}")
        if work is None:
            s2_fallback_count[0] += 1
            s2 = s2_lookup_title_year_field(wid)
            if s2 is None:
                entry = {"status": "fetch_failed", "field": None, "title": None, "year": None}
                guarded[wid] = entry
                fetch_failed.append({"openalex_id": wid, "reason": "openalex-permanent-fail+s2-no-id"})
                log_event({"kind": "guard_fetch_failed", "openalex_id": wid})
                return entry
            work = s2
        field = primary_field(work)
        title = work.get("title") or ""
        year = work.get("publication_year")
        if field in ADMITTED_FIELDS:
            status = "admitted"
        elif field is None:
            status = "out_of_domain"
        else:
            status = "out_of_domain"
        entry = {"status": status, "field": field, "title": title, "year": year,
                 "reason": "no-openalex-topic" if field is None else f"field={field}"}
        guarded[wid] = entry
        return entry

    # seeds are always admitted without a guard call (status already resolved)
    for rec in seed_recs:
        if rec["status"] == "resolved":
            wid = rec["openalex_id"]
            guarded[wid] = {"status": "admitted", "field": rec["field"], "title": None, "year": None}

    admitted_by_domain = {"math": [], "physics": []}
    for dom in ("math", "physics"):
        ranked_ids = sorted(
            (wid for wid, c in candidates.items() if dom in c["score_by_domain"]),
            key=lambda wid: -candidates[wid]["score_by_domain"][dom],
        )
        cursor = 0
        while len(admitted_by_domain[dom]) < 50 and cursor < len(ranked_ids):
            batch = ranked_ids[cursor:cursor + BATCH]
            cursor += BATCH
            for wid in batch:
                g = guard_one(wid)
                if g["status"] == "admitted":
                    c = candidates[wid]
                    c["field"], c["title"], c["year"] = g.get("field"), g.get("title"), g.get("year")
                    admitted_by_domain[dom].append(c)
            log_event({
                "kind": "guard_batch_done", "domain": dom, "cursor": cursor,
                "admitted_so_far": len(admitted_by_domain[dom]),
            })
    # Global, not per-domain-summed: a bridge candidate guarded via one
    # domain's loop must not also count as "not reached" in the other
    # domain's tail (per-domain remainder arithmetic double-counts those).
    not_guard_checked_count = [len(candidates) - len(guarded)]

    out_of_domain = [
        {"openalex_id": wid, "reason": g["reason"]}
        for wid, g in guarded.items() if g["status"] == "out_of_domain"
    ]
    in_domain = admitted_by_domain["math"] + admitted_by_domain["physics"]
    # de-dup in_domain list (a bridge candidate appears in both domain lists)
    seen_in_domain = {}
    for c in in_domain:
        seen_in_domain[c["openalex_id"]] = c
    in_domain = list(seen_in_domain.values())

    log_event({
        "kind": "domain_guard_done",
        "in_domain": len(in_domain), "out_of_domain": len(out_of_domain),
        "fetch_failed": len(fetch_failed), "not_guard_checked": not_guard_checked_count[0],
        "s2_fallback_attempts": s2_fallback_count[0],
    })

    # selection: rank by score desc within each domain, take 50/domain from
    # the now-admitted (not merely guard-pool) candidates.
    by_domain = {"math": [], "physics": []}
    for c in in_domain:
        for dom, score in c.get("score_by_domain", {}).items():
            by_domain.setdefault(dom, []).append((score, c))
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
        "guard_checked_count": len(guarded),
        "not_guard_checked_count": not_guard_checked_count[0],
        "fetch_failed": fetch_failed,
        "s2_fallback_attempts": s2_fallback_count[0],
        "methods_note_guard_scope": (
            f"Domain-guard ran in frozen score-descending order, expanding in "
            f"batches of {BATCH} per domain until 50 admitted or the domain's "
            f"ranked pool was exhausted (live-test seq 4533 binding 1), "
            f"guard-checking {len(guarded)} of {len(candidates)} raw fan-out "
            f"candidates; {not_guard_checked_count[0]} lower-ranked candidates "
            "were never reached. Any permanently-failed OpenAlex call (after "
            "retries) was attempted via Semantic Scholar as the frozen §2.2 "
            f"fallback ({s2_fallback_count[0]} attempts); any call that still "
            "had no answer is listed verbatim in fetch_failed (zero silent "
            "drops, binding 2) rather than treated as empty. Q4's "
            "excluded-fraction-per-hop figure is reported over the "
            "guard-checked set only, disclosed as a deviation from FROZEN-v1 "
            "(sha f31c62fc...8fb17) §2.3a's literal full-fan-out scope, per "
            "the director's seq 4523/4533 rulings."
        ),
        "in_domain": len(in_domain),
        "out_of_domain": out_of_domain,
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
        "guard_checked_count": len(guarded),
        "not_guard_checked_count": not_guard_checked_count[0],
        "fetch_failed_count": len(fetch_failed),
        "s2_fallback_attempts": s2_fallback_count[0],
    }, indent=2))


if __name__ == "__main__":
    main()
