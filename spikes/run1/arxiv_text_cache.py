#!/usr/bin/env python3
"""contextus-seed-corpus round 1 — §2.5 arXiv text-cache fetcher.

For each of the 99 papers in corpus_construct_output.json's
`selected_final`:
  1. Fetch the OpenAlex work record and reconstruct the abstract from
     `abstract_inverted_index`.
  2. Look in `locations` for an arXiv location and extract the arXiv id.
  3. If found, fetch ar5iv's LaTeXML HTML rendering
     (https://ar5iv.labs.arxiv.org/html/{id}) and parse out the
     introduction plus every labelled theorem/definition/proposition/
     lemma/conjecture statement.
  4. Build cached text = abstract + intro + labelled statements, truncate
     to a token budget, sha256 it, write to text_cache/<sha>.txt.
  5. If no arXiv id resolves, or the ar5iv fetch/parse fails or yields no
     statements, mark the paper text-unavailable (abstract alone does not
     count as usable text -- established by the §4 pilot: abstract-only
     text yields zero extractable claims under the frozen extraction
     prompt because its `locator` field needs theorem/section labels).

This is a real HTML fetch+parse, not a new structured dependency: the
parser below is hand-rolled regex/balanced-tag matching over ar5iv's
fairly regular LaTeXML output (stdlib only -- html.unescape + re), per
the task's "no new pip installs" constraint.

Politeness: reuses the polite_get() discipline from corpus_construct.py /
pilot_text_cache.py -- mailto query param on OpenAlex, MIN_INTERVAL
seconds between calls to the SAME host (tracked per-host, since this
script talks to two hosts), exponential backoff on 429/5xx, bounded
retries, then give up on that one paper and move on (one paper's failure
never blocks the other 98).
"""
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(RUN_DIR, "corpus_construct_output.json")
CACHE_DIR = os.path.join(RUN_DIR, "text_cache")
MANIFEST = os.path.join(RUN_DIR, "text_cache_manifest.jsonl")
LOG = os.path.join(RUN_DIR, "arxiv_text_cache_log.jsonl")

UA = "contextus-seed-corpus-spike/1.0 (Helpful Engineering federation research; mailto:contact@helpfulengineering.org)"
MAILTO = "contact@helpfulengineering.org"
MIN_INTERVAL = 4.0  # per-host; matches corpus_construct.py's OpenAlex-earned
# backoff (five-plus full pipeline passes against OpenAlex triggered a real
# 429 throttle on this box before -- see corpus_construct.py comment). ar5iv
# is a separate host and gets its own independent clock below, but the same
# conservative interval, since we have no prior measurement of its limits.
MAX_RETRIES_PER_CALL = 6       # exponential-backoff retries inside one HTTP
# call (matches the existing polite_get pattern -- transient 429/5xx).
MAX_PAPER_ATTEMPTS = 2          # per the task: "2 failed retries then move
# on" at the PAPER level, distinct from the per-call retry loop above. A
# paper gets at most this many independent fetch attempts (OpenAlex record,
# or the ar5iv page) before its status is decided and we move to the next
# paper -- no paper's failure can block the other 98.

# ~10,000 tokens, 1 token ~= 4 chars (budgeting heuristic only, not a real
# tokenizer -- documented per the task spec).
MAX_CHARS = 40_000

_last_call = {}  # host -> last call time, so OpenAlex and ar5iv rate-limit
# independently of each other.

os.makedirs(CACHE_DIR, exist_ok=True)
_logf = open(LOG, "a")


def log_event(ev):
    ev["ts"] = time.time()
    _logf.write(json.dumps(ev) + "\n")
    _logf.flush()


def _host(url):
    return urllib.parse.urlparse(url).netloc


def polite_get(url, what, is_json=True):
    """Fetch url, respecting a per-host MIN_INTERVAL and retrying 429/5xx
    with exponential backoff, up to MAX_RETRIES_PER_CALL times. Returns the
    parsed JSON (is_json=True) or raw decoded text (is_json=False), or None
    on permanent failure."""
    host = _host(url)
    backoff = 2.0
    for attempt in range(MAX_RETRIES_PER_CALL):
        last = _last_call.get(host, 0.0)
        wait = MIN_INTERVAL - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                _last_call[host] = time.time()
                log_event({"kind": "http_ok", "what": what, "host": host, "status": resp.status, "retry_count": attempt})
                if is_json:
                    return json.loads(body)
                return body.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            _last_call[host] = time.time()
            if e.code == 429 or 500 <= e.code < 600:
                log_event({"kind": "retry", "what": what, "host": host, "code": e.code, "attempt": attempt, "backoff": backoff})
                time.sleep(backoff)
                backoff = min(backoff * 2, 60.0)
                continue
            log_event({"kind": "http_error", "what": what, "host": host, "url": url, "code": e.code, "retry_count": attempt})
            return None
        except Exception as e:
            _last_call[host] = time.time()
            log_event({"kind": "fetch_error", "what": what, "host": host, "url": url, "error": str(e), "attempt": attempt})
            time.sleep(backoff)
            backoff = min(backoff * 2, 60.0)
            continue
    log_event({"kind": "giving_up_after_retries", "what": what, "host": host, "url": url, "retry_count": MAX_RETRIES_PER_CALL})
    return None


def with_mailto(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}mailto={urllib.parse.quote(MAILTO)}"


def invert_abstract(inv_idx):
    if not inv_idx:
        return None
    positions = {}
    for word, idxs in inv_idx.items():
        for i in idxs:
            positions[i] = word
    if not positions:
        return None
    return " ".join(positions[i] for i in sorted(positions))


ARXIV_ID_RE = re.compile(
    r"arxiv\.org/(?:abs|pdf|html|format)/"
    r"([a-zA-Z](?:[a-zA-Z.\-])*/\d{7}|\d{4}\.\d{4,5})"
    r"(?:v\d+)?",
    re.IGNORECASE,
)


def extract_arxiv_id(work):
    """Scan `locations` (OpenAlex work record) for an arXiv location —
    host/landing_page_url containing arxiv.org, or source.display_name ==
    'arXiv' — and pull the arXiv id (new-style 2301.12345 or old-style
    hep-th/9901001) out of the URL."""
    for loc in (work.get("locations") or []):
        if not loc:
            continue
        src = loc.get("source") or {}
        candidates = [
            loc.get("landing_page_url") or "",
            loc.get("pdf_url") or "",
        ]
        is_arxiv_source = (src.get("display_name") or "").strip().lower() == "arxiv"
        for url in candidates:
            if "arxiv.org" in url.lower() or is_arxiv_source:
                m = ARXIV_ID_RE.search(url)
                if m:
                    return m.group(1)
        if is_arxiv_source:
            # source says arXiv but URL didn't match our pattern (e.g. a
            # DOI-only record) -- still worth a second look at the doi url
            doi_url = loc.get("doi") or ""
            m = ARXIV_ID_RE.search(doi_url)
            if m:
                return m.group(1)
    # also check openalex's own top-level `doi`/`ids` for an arxiv id some
    # records carry (e.g. ids.arxiv)
    ids = work.get("ids") or {}
    arxiv_field = ids.get("arxiv") or ""
    m = ARXIV_ID_RE.search(arxiv_field)
    if m:
        return m.group(1)
    return None


# ---------------------------------------------------------------------------
# ar5iv HTML parsing (stdlib regex/balanced-tag matching -- no new deps)
# ---------------------------------------------------------------------------

VOID_LIKE = False  # not used; kept for clarity that we match real tag pairs


def strip_tags(fragment):
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_matching_close(doc, open_tag_end_idx, tag_name):
    """Given the index just after a tag's opening '>' (i.e. we are already
    inside one open <tag_name ...>), scan forward counting nested
    <tag_name ...> / </tag_name> occurrences of the SAME tag name and
    return the index of the start of the matching '</tag_name>' (i.e. the
    end of this element's inner content). Returns len(doc) if unterminated
    (truncated/malformed page -- fail soft, not an exception)."""
    depth = 1
    pattern = re.compile(r"<(/?)" + re.escape(tag_name) + r"(?=[\s/>])", re.IGNORECASE)
    pos = open_tag_end_idx
    while True:
        m = pattern.search(doc, pos)
        if not m:
            return len(doc)
        if m.group(1):  # closing tag
            depth -= 1
            if depth == 0:
                return m.start()
            pos = m.end()
        else:  # nested opening tag of the same name
            # advance past this nested tag's own '>' so we don't re-match
            # inside its attribute string (attrs could theoretically
            # contain '<tag_name' text, but that's not a realistic risk in
            # LaTeXML output)
            gt = doc.find(">", m.end())
            depth += 1
            pos = gt + 1 if gt != -1 else m.end()


def open_tag_span(doc, start_idx):
    """Given the index of '<' for an opening tag, return (attrs_str, end_idx)
    where end_idx is the index just after the tag's closing '>'."""
    gt = doc.find(">", start_idx)
    if gt == -1:
        return "", len(doc)
    tag_text = doc[start_idx:gt + 1]
    return tag_text, gt + 1


THEOREM_KEYWORDS = ("ltx_theorem", "ltx_definition", "ltx_proposition", "ltx_lemma", "ltx_conjecture")
TITLE_TAG_RE = re.compile(r"<h[1-6][^>]*class=\"[^\"]*ltx_title_theorem[^\"]*\"[^>]*>", re.IGNORECASE)
SECTION_TITLE_RE = re.compile(r"<h[1-6][^>]*class=\"[^\"]*ltx_title_section[^\"]*\"[^>]*>(.*?)</h[1-6]>", re.IGNORECASE | re.DOTALL)
ABSTRACT_RE = re.compile(r'<div\b[^>]*class="[^"]*ltx_abstract[^"]*"[^>]*>', re.IGNORECASE)


def parse_theorem_blocks(doc):
    """Returns a list of {label, text} for every element whose class
    attribute contains one of THEOREM_KEYWORDS."""
    out = []
    # div is the tag LaTeXML consistently emits for theorem-like
    # environments; scan all div open tags and filter by class.
    for m in re.finditer(r'<div\b([^>]*)class="([^"]*)"([^>]*)>', doc, re.IGNORECASE):
        classes = m.group(2)
        if not any(k in classes for k in THEOREM_KEYWORDS):
            continue
        open_end = m.end()
        close_start = find_matching_close(doc, open_end, "div")
        inner = doc[open_end:close_start]
        tm = TITLE_TAG_RE.search(inner)
        label = None
        body = inner
        if tm:
            title_open_end = tm.end()
            # the title tag name is whichever h1-6 matched; recover it
            htag = re.match(r"<(h[1-6])", tm.group(0), re.IGNORECASE).group(1)
            title_close_start = find_matching_close(inner, title_open_end, htag)
            title_html = inner[title_open_end:title_close_start]
            label = strip_tags(title_html).rstrip(". ").strip()
            title_close_end = inner.find(">", title_close_start)
            title_close_end = title_close_end + 1 if title_close_end != -1 else title_close_start
            body = inner[:tm.start()] + inner[title_close_end:]
        text = strip_tags(body)
        if not text and not label:
            continue
        out.append({"label": label, "text": text})
    return out


def find_introduction(doc):
    """Top-level <section> blocks only (nesting-depth 0), in document
    order; pick the first whose heading matches /introduction/i, else fall
    back to the first top-level section at all (= the first section after
    the abstract, since the abstract always precedes the body in ar5iv's
    output). Returns the plain-text content, or "" if no section found."""
    depth = 0
    top_starts = []
    for m in re.finditer(r"<section\b|</section\s*>", doc, re.IGNORECASE):
        if doc[m.start():m.start() + 2].lower() == "</":
            depth -= 1
        else:
            if depth == 0:
                top_starts.append(m.start())
            depth += 1
    if not top_starts:
        return ""
    top_starts.append(len(doc))  # sentinel end
    intro_idx = None
    for i in range(len(top_starts) - 1):
        start, end = top_starts[i], top_starts[i + 1]
        window = doc[start:min(end, start + 4000)]
        hm = SECTION_TITLE_RE.search(window)
        heading_text = strip_tags(hm.group(1)) if hm else ""
        if re.search(r"introduction", heading_text, re.IGNORECASE):
            intro_idx = i
            break
    if intro_idx is None:
        intro_idx = 0  # fallback: first section after the abstract
    start, end = top_starts[intro_idx], top_starts[intro_idx + 1]
    return strip_tags(doc[start:end])


def build_cached_text(abstract, intro, statements):
    parts = []
    if abstract:
        parts.append(abstract)
    if intro:
        parts.append(intro)
    for s in statements:
        label = s["label"] or "Statement"
        parts.append(f"{label}: {s['text']}")
    text = "\n\n".join(p for p in parts if p)
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
    return text


def fetch_openalex_work(openalex_id, work_id):
    url = with_mailto(f"https://api.openalex.org/works/{work_id}")
    return polite_get(url, f"openalex:{work_id}")


def fetch_ar5iv(arxiv_id):
    url = f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"
    return polite_get(url, f"ar5iv:{arxiv_id}", is_json=False)


def process_paper(paper):
    oaid = paper["openalex_id"]
    work_id = oaid.rstrip("/").rsplit("/", 1)[-1]
    result = {
        "openalex_id": oaid,
        "arxiv_id": None,
        "status": "text-unavailable",
        "sha256": None,
        "approx_tokens": None,
        "n_statements_found": 0,
        "fetch_ts": time.time(),
    }

    work = None
    for attempt in range(MAX_PAPER_ATTEMPTS):
        work = fetch_openalex_work(oaid, work_id)
        if work is not None:
            break
        log_event({"kind": "paper_attempt_failed", "openalex_id": oaid, "what": "openalex-work", "attempt": attempt})
    if work is None:
        log_event({"kind": "paper_status", "openalex_id": oaid, "status": "text-unavailable", "reason": "openalex-fetch-failed"})
        result["fetch_ts"] = time.time()
        return result

    abstract = invert_abstract(work.get("abstract_inverted_index"))
    arxiv_id = extract_arxiv_id(work)
    result["arxiv_id"] = arxiv_id

    if not arxiv_id:
        log_event({"kind": "paper_status", "openalex_id": oaid, "status": "text-unavailable", "reason": "no-arxiv-id"})
        result["fetch_ts"] = time.time()
        return result

    html_body = None
    for attempt in range(MAX_PAPER_ATTEMPTS):
        html_body = fetch_ar5iv(arxiv_id)
        if html_body is not None:
            break
        log_event({"kind": "paper_attempt_failed", "openalex_id": oaid, "what": "ar5iv-fetch", "arxiv_id": arxiv_id, "attempt": attempt})
    if html_body is None:
        log_event({"kind": "paper_status", "openalex_id": oaid, "status": "text-unavailable", "reason": "ar5iv-fetch-failed", "arxiv_id": arxiv_id})
        result["fetch_ts"] = time.time()
        return result

    try:
        intro = find_introduction(html_body)
        statements = parse_theorem_blocks(html_body)
    except Exception as e:
        log_event({"kind": "paper_status", "openalex_id": oaid, "status": "text-unavailable", "reason": f"parse-error:{e}", "arxiv_id": arxiv_id})
        result["fetch_ts"] = time.time()
        return result

    result["n_statements_found"] = len(statements)
    if not statements:
        log_event({"kind": "paper_status", "openalex_id": oaid, "status": "text-unavailable", "reason": "no-statements-parsed", "arxiv_id": arxiv_id})
        result["fetch_ts"] = time.time()
        return result

    text = build_cached_text(abstract, intro, statements)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{sha}.txt")
    with open(cache_path, "w") as f:
        f.write(text)

    result["status"] = "ok"
    result["sha256"] = sha
    result["approx_tokens"] = len(text) // 4
    result["fetch_ts"] = time.time()
    log_event({"kind": "paper_status", "openalex_id": oaid, "status": "ok", "arxiv_id": arxiv_id, "n_statements": len(statements), "sha256": sha})
    return result


def main():
    with open(INPUT) as f:
        data = json.load(f)
    papers = data["selected_final"]
    log_event({"kind": "start", "n_papers": len(papers)})

    # fresh manifest per run (append-only during the run itself) so a
    # re-invocation never silently doubles up lines for the same paper.
    open(MANIFEST, "w").close()

    manifest_lines = []
    for i, paper in enumerate(papers):
        log_event({"kind": "paper_start", "index": i, "openalex_id": paper["openalex_id"]})
        rec = process_paper(paper)
        manifest_lines.append(rec)
        with open(MANIFEST, "a") as mf:
            mf.write(json.dumps(rec) + "\n")

    n_ok = sum(1 for r in manifest_lines if r["status"] == "ok")
    n_unavail = len(manifest_lines) - n_ok
    log_event({"kind": "done", "n_ok": n_ok, "n_unavailable": n_unavail, "n_total": len(manifest_lines)})
    print(json.dumps({"n_ok": n_ok, "n_unavailable": n_unavail, "n_total": len(manifest_lines)}, indent=2))


if __name__ == "__main__":
    main()
