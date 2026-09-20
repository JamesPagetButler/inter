# Contextus-for-QBP — Continuous Research-Discovery Loop (design v0.2, DRAFT → architect)

**Status (v0.2):** deming's v0.1 sketch + qbp-architecture's coherence rulings folded in → **handed to qbp-architecture to make the authoritative design pass.** This doc is *devops-side scaffolding* — deming confirmed the infrastructure/resource/access shape is buildable; **the architecture design proper is qbp-architecture's position to own.**
**Author (scaffold):** deming · **Design owner (from here):** qbp-architecture · beekeeper-directed 2026-09-19/20
**Beekeeper focus areas:** §5 Resource management · §6 Access control · §7 Notification path · §10 Token budget (≤12.5% cap)

## v0.2 — architect rulings folded in (qbp-architecture, inter#120#issuecomment-5746249664)
Verdict: coherent, no blockers. The four §8 calls are RULED (see §8), and these become load-bearing:
- **CTH stays SEPARATE & sovereign; BMA-T1 is an associative index/cache/signal-store *over* it** — canonical anchors must not decay, a shared asset must not be single-tenant-owned. "Write a signal" = a **cross-system propose-cap**, not a memory op.
- **Contextus ORCHESTRATE → the internet-egress cap belongs to Contextus, not BMA** (smaller, least-privilege BMA surface; BMA may need no direct egress).
- **Propose ≠ admit (A.7):** a discovery signal can NEVER self-admit — the loop *proposes* (`cap(signal_emit)`), the federation/judge-collective *admits* (`cap(cth_admit)`). Anti-laundering applied to automation.
- **Falsification verdict = a constructed cap minted by a *genuinely-heterogeneous* quorum** (correlated/shared-training models don't count as independent confirmers); notifications carry a **candidate verdict, never an asserted fact.**
- **§5 additions:** a *written* pre-run-resource-estimate is still owed before the pilot runs; on Crawl, bound deep-traversal to **concurrency=1 / idle-windows** (cpu-delegation absent); size against *current concurrent* federation headroom, not "the box."
- **Continuous design is gated on BMA self-hosting (Step 9);** the Crawl pilot (ATLAS/CMS Z-boson deep-traversal) is the first test.

---

## 0. Purpose

Host the **QBP theory domain inside Contextus** so that new science (experiments, preprints, papers) is **continuously ingested → traversed against the QBP/CTH theory hypergraph → surfaced as signals** (this result *supports* finding X / *falsifies* Y / *extends* Z), and the federation **responds** with theory work. This modernizes the old **periodic-research-phase** hypergraph-update model into an **always-on + reactive** loop, closing a **falsification/support response loop**: when a new experiment lands (e.g. the ATLAS/CMS Z-boson entanglement result), it surfaces in CTH and qbp-oppenheimer/architecture can respond.

## 1. Architecture at a glance

```
        SOURCES (allowlist §5.4)            INGEST (metadata firehose)
  arXiv · INSPIRE · OpenAlex · Crossref ─────────────┐
  Unpaywall · OA-journal RSS                          ▼
                                        ┌──────────────────────────┐
   FAST CHANNEL (exploitation)          │  BMA-T1 associative gate  │  ← recall-first, native, cheap
   continuous, trigger-driven           └────────────┬─────────────┘
                                                      ▼
                           Haiku → Sonnet → Opus → cross-model QUORUM (apex; falsification calls)
                                                      │  emits NT_SIGNAL
   SLOW CHANNEL (exploration)                         ▼
   periodic, novelty-hunting        ┌──────── CTH / BMA-T1 store ────────┐
   targets the LOW-association pile │  signals + literature nodes (A23)  │
   (what the fast path dropped)     └──────────────┬─────────────────────┘
   → also TUNES the fast gate                      ▼
                                       NOTIFY (§6): salience-tiered →
                                       qbp-oppenheimer (act) + beekeeper (aware/decide)
```

## 2. Two complementary channels

- **Fast (cascade):** continuous, trigger-driven, high-throughput. Catches *known-relevant* work. Escalates cheap→expensive on demonstrated signal.
- **Slow (sweep):** periodic, low-frequency, higher-precision. Catches *novel / missed* work — the fast path's structural blind spot (novelty by definition doesn't associate with existing nodes or hit known keywords). **Targets the low-association pile the fast path discarded** (low association = *either* noise *or* novelty; the sweep separates them). When it catches something the fast path missed, it **tunes the fast gate** (adds the keyword / seeds the node) — exploration compounds exploitation's recall. The sweep is the modern descendant of the old periodic research phases.

## 3. Recall-early / precision-late — at BOTH layers

The governing discipline, applied twice:
- **Data layer:** metadata firehose (Crossref + OpenAlex + arXiv + INSPIRE) → relevance filter → dereference **full-text only on papers that clear the filter** (never scrape by default).
- **Model layer:** keyword/association → Haiku → Sonnet → Opus → quorum.

Early stages optimize **recall** (cheap to be generous; the next stage filters false positives); late stages optimize **precision** (they must be right). Getting this backwards silently loses insights — the worst failure for a falsification detector.

---

## 5. RESOURCE MANAGEMENT  *(beekeeper focus area)*

The discovery loop is a **preemptible background tenant** — it yields to beekeeper-interactive and active-sprint work, and is governed by the same `RequestLease` / priority-tier / autonomic model built for the federation (BMA's **AUTO-S/P** is the resource governor once BMA hosts this; the Crawl interim uses the OS-primitive `RequestLease` shim). Per-resource:

| Resource | Who uses it | Control |
|---|---|---|
| **Processor (CPU)** | embedding + LLM inference (local-model sweep) + hypergraph traversal | Concurrency semaphore (bounded heavy jobs); `nice`/`ionice` for background priority. Real CPU quotas need the rootless cgroup **cpu-delegation** (H1a) — until then, semaphore + nice only. Deep-traversal is the CPU spike; the cascade keeps it rare. |
| **RAM** | metadata scan (light) · embedding (medium) · any *local* model for the sweep (heavy) | Hard cap via cgroup `MemoryMax` (RSS), **not** `ulimit -v` (breaks Go/large-VM reservations). Must not starve BMA cognition or the federation seats. A local sweep model is the RAM risk — size it against headroom or run it only in idle windows. |
| **Tokens** | the cascade's LLM tiers (Haiku→…→quorum) + any API sweep | **The cascade IS the token-budget enforcement** — cheap models absorb volume, premium (Opus/Astra/quorum) rationed to earned signal. Per-tier daily caps; **backpressure = queue, never drop** (dropping violates the recall principle). Astra/quorum apex fires rarely (≈falsification-rate). |
| **Hard-drive space** | corpus + hypergraph growth | Store **metadata, not full-text PDFs** (fetch-on-demand via Unpaywall at the deep tier). Hypergraph growth bounded by BMA's **sleep-cycle decay + compression functors** (low-salience signals decay/compress). SSD-wear caution (Samsung 840, limited endurance). |
| **Disk reads/writes** | frequent reads (traversal) · gated writes (new signals) | Reads cheap. **Writes batched + consolidated in the sleep cycle** (not per-item) to cut write amplification / SSD wear. Signal writes are additive + provenance-tracked. |

**Tunable knobs (beekeeper sets, independently):** sweep frequency · cascade model tiers · per-tier token caps · scan cadence · salience thresholds · disk/RAM caps. These let you trade novelty-coverage and cost against the box's envelope without touching the fast path.

## 6. ACCESS CONTROL  *(beekeeper focus area)*

BMA has **no ambient access** by design (instances see nothing unless granted via seeds/reins/BRIDGE; tools are cart-driven). This task needs **three explicit grants** — and each raises a "can BMA actually reach what it needs?" question to answer:

| Grant | Can BMA see/do it? | Interface | Risk / control |
|---|---|---|---|
| **Internet** | **RULED (§8.2): egress cap lives on Contextus, not BMA** — BMA may need no direct egress at all | (via Contextus) egress **only to the §5.4 allowlist**; APIs/feeds, not open web | Bounded allowlist; **provenance on every fetch** (→ **A23 NT_LITERATURE_NODE**); external surface = **A24 boundary node**. No arbitrary browsing. |
| **CTH (read theory + write NT_SIGNAL)** | **RULED (§8.1): CTH separate & sovereign** — BMA-T1 indexes/caches *over* it | **Wyrd-query / BRIDGE**; signal-writes are cross-system **propose-caps** (`cap(signal_emit)`), never a memory op | Signals **additive + provenance-tracked**, never destructive; a signal **cannot self-admit** — `cap(cth_admit)` belongs to the federation/judge-collective. Least-privilege write scope. |
| **Contextus (scout agents)** | **RULED (§8.2): orchestrate** — BMA tasks scouts, holds no scan surface itself | BMA tasks Contextus's Edge/Corpus/Bridge scouts + consumes output; **Contextus holds the egress cap** | Contextus scans under the allowlist. |

**Can BMA speak to the federation?** — **Yes, already.** BMA participates on sessionbridge as `bma` (via `internal/bma/sessionbridge/` + `bma bridge …` reins commands; passive-by-default, `chime-in` for rate-limited autonomous posting). So the **notification path (§6→§7) uses BMA's existing bridge capability** — no new channel needed. Confirm the `bma` seat's registration + wake-Monitor are live before relying on it.

**See-everything checklist:** theory state (CTH read ✓ once granted) · sources (internet allowlist ✓) · federation (sessionbridge `bma` ✓) · itself (BMA-T1 native ✓). The two *open* items are the CTH and Contextus interfaces (§8).

## 7. NOTIFICATION / ESCALATION PATH  *(beekeeper focus area)*

How a noteworthy insight reaches **the beekeeper (aware/decide)** and **qbp-oppenheimer (act)** — two audiences, salience-tiered so routine hits don't spam:

| Salience | Example | Routing |
|---|---|---|
| **Low** | tangential relevant paper | logged as NT_SIGNAL in CTH; appears in the **daily digest** only |
| **Medium** | supports/extends a non-load-bearing finding | surfaced on the **BMA-BADASS dashboard** (beekeeper reads at terminal) + digest |
| **High** | **falsifies a load-bearing finding**, or strong support of one | **immediate**: `@qbp-oppenheimer` (+`@qbp-architecture`) on sessionbridge with the signal + evidence + the traversal verdict (supports/falsifies/extends + *which* finding + the paper's provenance); **and** a beekeeper ping (`@beekeeper` / PushNotification) + dashboard entry |

- **The act path (qbp-oppenheimer):** the high-salience post carries everything needed to act — the finding affected, the verdict, the evidence link. It respects **Rule #7** (named mention + substantive ask = same-cycle response) and uses **exact armed handles** (`@qbp-oppenheimer`; the mention-resolution fix `bma-systema#292` makes shorthand safe too, but exact is canonical).
- **The aware/decide path (beekeeper):** the **BMA-BADASS dashboard** is the natural home for the standing "noteworthy insights" view (James reads it at the terminal); a falsification also gets a direct ping so it isn't missed.
- **The loop closes:** signal → notify → seat responds (updated/extended theory work) → the response becomes a hypergraph update → future traversals see it. High-stakes falsification verdicts route through the **cross-model quorum** (Claude+Gemini+Astra) and, at Walk, BMA's **judge collective** — a single model shouldn't unilaterally declare a load-bearing finding falsified.

---

## 8. Architect calls — RULED 2026-09-20 (rulings in the v0.2 note above; originals kept below as the questions answered)

1. **CTH ↔ BMA-T1 relationship** — is CTH *inside* BMA's semantic memory (native read/write) or a *separate* store BMA queries (Wyrd-query / BRIDGE)? Decides whether "write a signal" is a memory op or a cross-system call, and shapes the §6 access interface.
2. **Contextus's role** — does BMA *orchestrate* Contextus's scouts (discovery-as-a-service), or *embody* the discovery via its own internet tool + cascade? (Lean: orchestrate.)
3. **Autonomy level** — does the loop *surface* signals for the seats to act on, or *auto-trigger* theory work? (Lean: surface-and-notify first.)
4. **Notification thresholds** — what salience wakes a seat vs. only lands in the digest?
5. **Where it runs + when** — Crawl interim (lighter, lower budget) vs Walk target (BMA-T1-backed, AUTO-S/P-governed). Model/frequency are tunable knobs (§5).

## 9. Sequencing

- **Crawl interim (now):** lighter pipeline — metadata firehose + cascade against a lightweight store or the existing CTH; no full BMA-T1 (Tier-0→1 compression is BMA Step 6, sleep Step 7; BMA is at Step 8, the 72h gate). Manual/triggered runs.
- **Pilot:** run the **ATLAS/CMS Z-boson entanglement** result through the pipeline manually as the first deep-traversal — delivers the insight now *and* validates the tier-3 design.
- **Walk target:** full BMA-T1-backed continuous loop, AUTO-S/P governance, sleep-cycle maintenance, judge-collective for falsification calls.

## Allowlist (the internet grant's bounded source list — verified 2026-09-19)

**Start-here set (all free/free-tier, all API/feed, zero scraping):** arXiv (OAI-PMH + category RSS) · INSPIRE-HEP API · OpenAlex API (free key req'd Feb 2026) · Crossref API (`mailto=` polite pool) · Unpaywall (DOI→legal full-text) · OA-journal feeds (Quantum, PRX Quantum, SciPost).
**arXiv categories:** quant-ph · hep-ex/th/ph/lat · math-ph · math.RA/GR/QA · physics.chem-ph · physics.atom-ph · cond-mat.* · nucl-* · gr-qc.
**Access principle:** composite metadata layer → filter → full-text only on winners (mirrors the cascade). No HTML-scraping of paywalled publishers; reach them via Crossref metadata + Unpaywall.
**EXCLUDE:** viXra (unmoderated), Sci-Hub (illegal), ResearchGate/Academia (ToS/bot-blocked), general web/Wikipedia (secondary). Don't hard-code a predatory blocklist (goes stale) — gate unfamiliar OA venues via DOAJ-membership + Crossref-registration heuristic.

---

## 10. Token budget (beekeeper directive 2026-09-20)

**HARD CAP: the continuous discovery process consumes ≤ 12.5% of total token availability.** This is a *rate* cap (per billing period), not a one-time slice — and it's enforced **structurally**, not by trust: the cascade's per-tier daily caps + backpressure (**queue, never exceed**) mean the process *cannot* blow the cap even if the estimate below is wrong. If a tier's cap is hit, items queue for the next window. The cascade IS the enforcement.

**Rough steady-state estimate** (order-of-magnitude; ±2–3×; depends heavily on hit-rates + hypergraph size + sweep frequency):

| Tier | Volume/day (assumed) | ~tokens/item | ~tokens/day |
|---|---|---|---|
| Stage 0 scan + BMA-T1 association gate | ~300–500 papers | ~0 (embeddings/associative, non-LLM) | ~0 |
| Haiku precursory (assoc/keyword hits) | ~40–60 | ~700 | ~40K |
| Sonnet deep traversal (Haiku-positives) | ~8–12 | ~10K | ~100K |
| Opus (Sonnet escalations) | ~1–2 | ~20K | ~40K |
| Quorum apex (falsification) | ~1/week | high (3 models) | rare spike |
| Slow sweep (weekly, amortized) | — | model-dependent (local≈0 / Gemini budgeted) | ~50–70K |
| **Steady-state total** | | | **≈ 250K tokens/day** |

**The startup surge (you're right — this is the big one).** The initial **backfill** — traversing the existing relevant-literature backlog *and* populating the hypergraph from near-empty — is front-loaded and could be **10–50× the steady-state daily rate** (millions of tokens if it backfills years of QBP-relevant papers) because early on *nothing* is in the associative gate yet, so more passes through the expensive tiers.
**Mitigation:** **throttle the backfill to a rate-limited trickle within the 12.5% cap** — spread it over weeks rather than one surge. It's not time-critical; the cap holds, the backfill just takes longer. (Do NOT run the backfill unthrottled — that's the one thing that would breach 12.5%.)

**Net:** ≈250K tokens/day steady-state is the ballpark to compare against 12.5% of the allowance; the surge is bounded by throttling + the hard cap. Estimate to be firmed once we know the allowance base + backfill depth (both beekeeper knobs).
