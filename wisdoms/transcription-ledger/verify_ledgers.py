#!/usr/bin/env python3
"""Verify the inter#61 transcription ledgers and (re)write their summaries.

Checks, per ledger in this directory:
  1. every `##`..`####` heading of the source (outside code fences) appears in the ledger's
     source-locator column;
  2. ledger rows are numbered 1..N without gaps;
  3. every destination anchor exists: `_federation.md#w-*` as an `<a id>` in
     wisdoms/_federation.md, `skills/<f>.md#<slug>` as a GitHub heading slug in that skill,
     `gate:<name>` as a CLAUDE.md HARD-GATE name;
  4. WISDOM-NEW refs point at atoms added by this PR and WISDOM-CITED refs at atoms that
     already existed on origin/main;
  5. every row has a recognised destination type;
and once overall: no atom anchor or atom title appears twice in _federation.md.

Usage:  python3 verify_ledgers.py [--write-summary]
Exit status is non-zero if any check fails. Read-only unless --write-summary is passed.
"""
import collections
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
DOCS = os.path.expanduser("~/Documents")
CLAUDE_MD = os.path.join(DOCS, "CLAUDE.md")

SOURCES = {
    "github-best-practices.md": os.path.join(REPO, "github-best-practices.md"),
    "issue-authoring-best-practices.md": os.path.join(REPO, "issue-authoring-best-practices.md"),
    "code-review-best-practices.md": os.path.join(REPO, "code-review-best-practices.md"),
    "architecture-diagrams-best-practices.md": os.path.join(REPO, "architecture-diagrams-best-practices.md"),
    "roadmap-best-practices.md": os.path.join(REPO, "roadmap-best-practices.md"),
    "go-coding-guide.md": os.path.join(DOCS, "go-coding-guide.md"),
    "python-coding-guide.md": os.path.join(DOCS, "python-coding-guide.md"),
    "lean-coding-guide.md": os.path.join(DOCS, "lean-coding-guide.md"),
}

# Atoms that existed in wisdoms/_federation.md before this PR (anchored by this PR).
PRE_EXISTING = {
    "w-separation-of-concerns": "Separation of concerns is the first cut.",
    "w-spec-before-code": "Spec-compliance before code-quality.",
    "w-verify-before-summarize": "Verify state before you summarize it.",
    "w-idempotent-self-healing": "Idempotent and self-healing by default.",
    "w-tests-ship-with-code": "Tests ship with the code that needs them",
    "w-determinism": "Determinism is cheap; non-determinism is a latent bug.",
    "w-one-writer": "One writer per resource.",
    "w-estimate-resources": "Estimate resources before a long job; bound it before launch.",
    "w-proven-not-wired": "Proven ≠ wired",
    "w-gate-driven": "Gate-driven progression.",
    "w-dependency-order": "Dependency order is the architecture of the work.",
    "w-antifragile": "Antifragile, not just robust.",
    "w-honest-negatives": "Honest negatives over optimistic greens.",
    "w-provenance": "Provenance is non-negotiable.",
    "w-skill-before-blind-use": "Skill-before-blind-use.",
}

CONFLICTS = {
    "C1": "github-best-practices internal: §2.6 (chat/sessionbridge form `repo-<name>-<type>-#<num>`; short `repo#N` fine when owner unambiguous; never bare `#N` even in a single-repo thread) vs §7.5 (`<repo>#N` in sessionbridge posts too; never abbreviate; bare `#N` OK inside the named PR/issue's own thread).",
    "C2": "issue-authoring §3 + §7 row (mandatory `repo-<name>-<issue|pr>-#<N>`; bare `#N` allowed for same-repo refs) vs github-best-practices §2.6/§7.5 (later: `owner/repo#N` / `<repo>#N` in GitHub artifacts; no bare `#N`).",
    "C3": "issue-authoring §6a.4 (next sprint gated on housekeeping backlog 'cleared or explicitly deferred by beekeeper with named reasoning') vs CLAUDE.md gate `housekeeping-before-sprint` ('all housekeeping-labeled board items resolved'; no deferral clause).",
    "C4": "Meaning of §I4: issue-authoring §4 ('Issue-class 4 reviewer discipline') vs github-best-practices §2.2/§5.3/§7.2 ('ADR-003 §I4' in qbp-compute-unit/architecture/).",
    "C5": "Review verdicts: code-review §3.4 frames sign-off as GitHub Approve / Request changes / Comment, which github §7.2.1 says is structurally impossible (review of record = signed PR comment); and three verdict vocabularies coexist (issue ack APPROVE/APPROVE-WITH-CONCERN/DEFER; Gate 1 PASS/FAIL/DEFER; Gate 2 APPROVE/APPROVE-WITH-CONCERN/REQUEST-CHANGES).",
    "C6": "architecture-diagrams internal: §5.1/§9.2 'no bidirectional arrows' vs §5.1 example 'goroutine A ↔ B' and the §3.3 L2 example's `<-->` edges (including cross-system `Subconscious <-->|read/write| Wyrd`).",
    "C7": "Colour semantics: architecture-diagrams §5.2 element-type palette ('consistent across all workspace docs': #eef internal, #efe storage, #ffe bus, #fee external) vs roadmap §5.5 status palette (#cfc passed, #ffe active, #fee blocked, #eef future) vs roadmap §5.6 work-type palette (#fce theory, #eef infra, #efe implementation, #ffe governance, #fee external).",
    "C8": "Python checks: github-best-practices §4.1 CI (`mypy` where typed; `uv lock` no diff) vs python-coding-guide (`pyright` preferred, `mypy --strict` acceptable; `uv lock --check`).",
    "C9": "go-coding-guide internal: 'One return path.' vs 'Prefer guard clauses + early return' (early return means multiple return paths).",
    "C10": "go-coding-guide BMA note (container limits `--memory 14g --cpus 6`) vs CLAUDE.md container strategy (rootless cpu cgroup not delegated; run line uses `--memory 14g` only). Persona-local to bma-implementor.",
    "C11": "github-best-practices §5.1 (force push acceptable to a feature branch you own, after a clean rebase, when no one else is reviewing) vs CLAUDE.md standing authorizations (force-push stays confirm-first anywhere, for agents).",
    "C12": "github-best-practices internal: §1.1 'Restrict who can push: enabled, owner-only' and §1.5 'conversation resolution recommended for Wyrd, BMA, QBP-CU' vs §6 PROTECTION_JSON (`\"restrictions\": null`, `\"required_conversation_resolution\": false` for every repo).",
    "C13": "Minor: architecture-diagrams §5.4 marks `[WALK: TARGET]` as preferred over SPECIFIED, while roadmap §5.3 examples use `[WALK: SPECIFIED]` and roadmap §5.2 status values (CONFIRMED/STRUCTURAL/PENDING/THEORETICAL) differ from the diagram marker set.",
    "C14": "roadmap-best-practices internal: §4 'eight sections, in this order' (1 Header, 2 Where we are, …, 8 Update protocol) vs §9 template (unnumbered header; §1 Now/Next/Later, §2 status table, … §8 Update protocol, §9 History).",
}

RETIRES = {
    "R1": "github §2.3 — the literal trailer model string `Claude Opus 4.7 (1M context)`: stale model name. The rule (always add AI co-author trailers) is kept in skills/pr-authoring.md; the trailer to use is the one the running session supplies.",
    "R2": "github §7.3 — `addendum-18-walk` channel bullet: historical meeting channel cited as the doc's own provenance; not a practice.",
    "R3": "roadmap §8.2 — '(the Opus 4.7 architect-side instance)': stale model descriptor of qbp-architecture. The ownership rule itself is kept (persona-local, qbp-architecture).",
    "R4": "architecture-diagrams §11 — Workspace Diagram Inventory: point-in-time to-do list, not a practice (two rows already done 2026-05-13). Ruling needed: convert the four open re-render rows to `housekeeping` issues, or drop.",
    "E1": "issue-authoring §2.2.2.f — private-repo identifiers and file:line references: not propagated into public skills (inter is PUBLIC); the concept is carried; detail stays in the source.",
    "E2": "Feedback-memory pointers (code-review §11/§12 `feedback_delegation_policy.md`, `feedback_code_review_policy.md`; issue-authoring §2.2.2.e/§3/§6.3/§6a.4 `feedback_antifragility`, `feedback_repo_prefixed_refs`, `feedback_housekeeping_before_sprint`; github §1.5 YubiKey memory): the memory corpus is out of scope for this PR.",
}

TYPES = ["WISDOM-NEW", "WISDOM-CITED", "SKILL", "GATE", "PERSONA-LOCAL", "META", "RETIRED", "EXCLUDED"]


def slug(h):
    s = h.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def headings(path, min_level=2, max_level=6):
    out, fence = [], False
    for line in open(path, encoding="utf-8"):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line.rstrip("\n"))
        if m and min_level <= len(m.group(1)) <= max_level:
            out.append((len(m.group(1)), m.group(2)))
    return out


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\\|", "|")).strip()


def split_row(line):
    # split a markdown table row on unescaped pipes, ignoring pipes inside backticks
    cells, cur, tick = [], "", False
    i = 0
    while i < len(line):
        c = line[i]
        if c == "`":
            tick = not tick
        if c == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if c == "|" and not tick:
            cells.append(cur)
            cur = ""
        else:
            cur += c
        i += 1
    cells.append(cur)
    return [x.strip() for x in cells[1:-1]]


def ledger_rows(path):
    rows, in_table = [], False
    for line in open(path, encoding="utf-8"):
        if line.startswith("| # |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            rows.append(split_row(line.rstrip("\n")))
        elif in_table and line.strip() == "":
            in_table = False
    return rows


def main():
    write = "--write-summary" in sys.argv
    failures = []
    fed_path = os.path.join(REPO, "wisdoms", "_federation.md")
    fed = open(fed_path, encoding="utf-8").read()
    fed_ids = re.findall(r'<a id="(w-[\w-]+)"></a>', fed)
    titles = re.findall(r'<a id="w-[\w-]+"></a>\*\*(.+?)\*\*', fed)

    # global: no duplicate atoms in _federation.md
    dup_ids = [k for k, v in collections.Counter(fed_ids).items() if v > 1]
    dup_titles = [k for k, v in collections.Counter(titles).items() if v > 1]
    bullets = [l for l in fed.splitlines() if l.startswith("- ")]
    unanchored = [l[:60] for l in bullets if '<a id="w-' not in l]
    print("== _federation.md: %d atoms, %d unique ids, %d unique titles" % (len(fed_ids), len(set(fed_ids)), len(set(titles))))
    for d in dup_ids:
        failures.append("_federation.md duplicate anchor %s" % d)
    for d in dup_titles:
        failures.append("_federation.md duplicate atom title %s" % d)
    for u in unanchored:
        failures.append("_federation.md atom without anchor: %s" % u)
    try:
        base = subprocess.run(["git", "-C", REPO, "show", "origin/main:wisdoms/_federation.md"],
                              capture_output=True, text=True, check=True).stdout
        for aid, title in PRE_EXISTING.items():
            if title not in base:
                failures.append("PRE_EXISTING %s title not found on origin/main" % aid)
            if aid not in fed_ids:
                failures.append("PRE_EXISTING %s missing from _federation.md" % aid)
        print("   pre-existing atoms confirmed on origin/main: %d; new atoms: %d" % (
            len(PRE_EXISTING), len(set(fed_ids) - set(PRE_EXISTING))))
    except subprocess.CalledProcessError as e:
        failures.append("cannot read origin/main:_federation.md (%s)" % e)

    gates = set(re.findall(r'HARD-GATE name="([\w-]+)"', open(CLAUDE_MD, encoding="utf-8").read()))
    skill_slugs = {}
    for f in os.listdir(os.path.join(REPO, "skills")):
        if f.endswith(".md"):
            skill_slugs[f] = {slug(h) for _, h in headings(os.path.join(REPO, "skills", f), 1)}

    totals = collections.Counter()
    for led in sorted(SOURCES):
        lpath = os.path.join(HERE, led)
        src = SOURCES[led]
        lfail = []
        rows = ledger_rows(lpath)
        loc_text = norm(" ".join(r[1] for r in rows if len(r) > 1))
        # 1. headings
        src_heads = headings(src, 2, 4)
        missing = [h for _, h in src_heads if norm(h) not in loc_text]
        for h in missing:
            lfail.append("source heading not in ledger: %r" % h)
        # 2. numbering
        nums = [r[0] for r in rows]
        if nums != [str(i) for i in range(1, len(rows) + 1)]:
            lfail.append("row numbering not 1..N")
        primary, refs, conflicts, retires = collections.Counter(), collections.Counter(), set(), set()
        for r in rows:
            if len(r) != 4:
                lfail.append("row %s has %d cells" % (r[0] if r else "?", len(r)))
                continue
            dest, note = r[2], r[3]
            parts = [p.strip() for p in dest.split(" ; ")]
            first = None
            for p in parts:
                t = next((t for t in TYPES if p.startswith(t)), None)
                if t is None:
                    lfail.append("row %s: unrecognised destination %r" % (r[0], p))
                    continue
                first = first or t
                refs[t] += 1
                for aid in re.findall(r"_federation\.md#(w-[\w-]+)", p):
                    if aid not in fed_ids:
                        lfail.append("row %s: missing atom anchor %s" % (r[0], aid))
                    elif t == "WISDOM-NEW" and aid in PRE_EXISTING:
                        lfail.append("row %s: %s marked NEW but pre-existed" % (r[0], aid))
                    elif t == "WISDOM-CITED" and aid not in PRE_EXISTING:
                        lfail.append("row %s: %s marked CITED but is new in this PR" % (r[0], aid))
                for f, s in re.findall(r"skills/([\w.-]+\.md)#([\w-]+)", p):
                    if f not in skill_slugs:
                        lfail.append("row %s: missing skill file %s" % (r[0], f))
                    elif s not in skill_slugs[f]:
                        lfail.append("row %s: missing anchor %s#%s" % (r[0], f, s))
                for g in re.findall(r"gate:([\w-]+)", p):
                    if g not in gates:
                        lfail.append("row %s: unknown gate %s" % (r[0], g))
            if first:
                primary[first] += 1
            conflicts |= set(re.findall(r"\bC(\d+)\b", " ".join(re.findall(r"CONFLICT C\d+(?:/C\d+)*", dest + " " + note))))
            retires |= set(re.findall(r"\b([RE]\d)\b", note + " " + dest))
        words = len(open(src, encoding="utf-8").read().split())
        totals.update(primary)
        status = "PASS" if not lfail else "FAIL (%d)" % len(lfail)
        print("== %s: %s — %d source words, %d source headings (##–####), %d ledger rows" % (
            led, status, words, len(src_heads), len(rows)))
        print("   rows by primary destination: " + ", ".join("%s=%d" % (t, primary[t]) for t in TYPES if primary[t]))
        print("   destination refs by type:    " + ", ".join("%s=%d" % (t, refs[t]) for t in TYPES if refs[t]))
        print("   conflicts: %s  retires/excludes: %s" % (
            ", ".join("C" + c for c in sorted(conflicts, key=int)) or "none",
            ", ".join(sorted(retires)) or "none"))
        for x in lfail:
            print("   ! " + x)
        failures += ["%s: %s" % (led, x) for x in lfail]
        if write:
            summ = ["<!-- SUMMARY:BEGIN (generated by verify_ledgers.py --write-summary) -->", "## Summary", "",
                    "- Source: %d words, %d headings (`##`–`####`); ledger: %d rows, in source order." % (words, len(src_heads), len(rows)),
                    "- Verification: %s (headings covered, anchors resolve, gates exist, NEW/CITED classification consistent)." % status,
                    "- Not machine-checked: that each row's destination faithfully carries the quoted paragraph/bullet, and that no paragraph lacks a row. That is the notary V&V step (inter#61 acceptance).",
                    "", "| Destination type | Rows (primary) | References (all) |", "|---|---|---|"]
            for t in TYPES:
                if primary[t] or refs[t]:
                    summ.append("| %s | %d | %d |" % (t, primary[t], refs[t]))
            summ += ["", "**CONFLICTs needing a human ruling** (not resolved here):", ""]
            summ += ["- **C%s** — %s" % (c, CONFLICTS["C" + c]) for c in sorted(conflicts, key=int)] or ["- none"]
            summ += ["", "**RETIRE / EXCLUDE items needing a human ruling:**", ""]
            summ += ["- **%s** — %s" % (k, RETIRES[k]) for k in sorted(retires)] or ["- none"]
            summ.append("<!-- SUMMARY:END -->")
            text = open(lpath, encoding="utf-8").read()
            block = "\n".join(summ)
            if "<!-- SUMMARY:BEGIN" in text:
                text = re.sub(r"<!-- SUMMARY:BEGIN.*?<!-- SUMMARY:END -->", lambda _: block, text, flags=re.S)
            else:
                text = text.replace("<!-- SUMMARY -->", block)
            open(lpath, "w", encoding="utf-8").write(text)
    print("== TOTAL rows by primary destination: " + ", ".join("%s=%d" % (t, totals[t]) for t in TYPES if totals[t]))
    print("== RESULT: %s" % ("PASS" if not failures else "FAIL — %d problem(s)" % len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
