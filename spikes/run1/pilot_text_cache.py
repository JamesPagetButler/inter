#!/usr/bin/env python3
"""contextus-seed-corpus §4 PILOT ONLY — text-cache fetch for a 3-paper
harness-proof batch, not part of round 1's canonical 99-paper run. Reuses
the polite_get() discipline from spikes/run1/corpus_construct.py (mailto
query param, MIN_INTERVAL=4.0s, exponential backoff) against the same
OpenAlex API.

Scope note (disclosed, matching the spike's existing disclosure pattern):
this pilot caches **abstract only** via the OpenAlex `works/{id}` endpoint.
Full intro + statements text (FROZEN-v1 §2.5) requires fetching and parsing
the paper's actual PDF/HTML, which this pilot does not attempt -- that is
a real gap to close before the canonical 99-paper run, not something to
silently work around.
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(RUN_DIR, "pilot_text_cache")
LOG = os.path.join(RUN_DIR, "pilot_text_cache_log.jsonl")
MANIFEST = os.path.join(RUN_DIR, "pilot_text_cache_manifest.json")

UA = "contextus-seed-corpus-spike/1.0 (Helpful Engineering federation research; mailto:contact@helpfulengineering.org)"
MAILTO = "contact@helpfulengineering.org"
MIN_INTERVAL = 4.0
MAX_RETRIES = 6
_last_call = [0.0]

os.makedirs(CACHE_DIR, exist_ok=True)
_logf = open(LOG, "a")


def log_event(ev):
    ev["ts"] = time.time()
    _logf.write(json.dumps(ev) + "\n")
    _logf.flush()


def _with_mailto(url):
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


def main(openalex_ids):
    manifest = []
    for oaid in openalex_ids:
        work_id = oaid.rstrip("/").rsplit("/", 1)[-1]
        url = f"https://api.openalex.org/works/{work_id}"
        log_event({"kind": "fetch_start", "openalex_id": oaid})
        data = polite_get(url, f"pilot-fetch:{work_id}")
        if data is None:
            log_event({"kind": "fetch_failed", "openalex_id": oaid})
            manifest.append({"openalex_id": oaid, "status": "fetch-failed"})
            continue
        title = data.get("title")
        abstract = invert_abstract(data.get("abstract_inverted_index"))
        doi = data.get("doi")
        if abstract is None:
            status = "text-unavailable"
            text = None
        else:
            status = "abstract-only"
            text = f"# {title}\n\nAbstract:\n{abstract}"
        cache_path = os.path.join(CACHE_DIR, f"{work_id}.txt")
        text_sha = None
        if text:
            with open(cache_path, "w") as f:
                f.write(text)
            text_sha = hashlib.sha256(text.encode()).hexdigest()
        manifest.append({
            "openalex_id": oaid,
            "work_id": work_id,
            "title": title,
            "doi": doi,
            "status": status,
            "cache_path": os.path.relpath(cache_path, RUN_DIR) if text else None,
            "text_sha256": text_sha,
        })
        log_event({"kind": "fetch_done", "openalex_id": oaid, "status": status})

    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
