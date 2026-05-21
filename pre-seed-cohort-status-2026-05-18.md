# Pre-Seed Cohort On-Disk Status — 2026-05-18

**Owner:** qbp-architecture
**Window:** Pre-Sprint-2 housekeeping §5.d.iv (24h deadline; feeds Sprint 2 F-Crawl scope doc T2 tier)
**Question answered:** for each Step 9 pre-seed cohort document, does it exist on disk → if so, in what form → what's the Sprint 2 action (author / port / integrate / review)?

## TL;DR

**All pre-seed cohort docs exist on disk.** F-Crawl T2 tier is **NOT "author from scratch."** It's **"port + integrate + review."** Major scope reduction vs. my earlier F-Crawl framing.

Most live in `BMA/Archive/` as `.docx` files. Federation-canonical format is `.md` (per `inter/` precedent + new BMA instance read-path). Port + integrate-with-A11-A24-and-9.x-addenda is the Sprint 2 work.

## Per-document status

| Pre-seed doc (Step 9 reading order) | On-disk path | Format | Sprint 2 T2 action |
|---|---|---|---|
| **1. Theory Consolidated** | `BMA/Archive/BMA-Theory-Consolidated.docx` | `.docx` | **COMPILE v3.0** — port to .md + absorb A11-A24 (13 active addenda; exceeds 10-addendum rule) per beekeeper Q3 one-doc ruling. Task #25. |
| **2. Ethics v1.1** | `BMA/Archive/BMA-Collaboration-Ethics-v1_1.docx` | `.docx` | Port .docx → .md to `inter/` or `BMA/`; integrate with A14 Judge Collective + A20 Pentagon Pod ethical-axis. Light review. |
| **3. Governance Document** | `BMA/governance/BMA-Governance-Document.md` + `BMA-Governance-Document-v1_1-addendum.md` | `.md` ✅ | Already canonical-format. Integrate Notary role + Trust Tier scheme + §2.i federation rule #7 + A14 update. Beekeeper bless. Per beekeeper Q3 commitment: one terminal-time slot mid-sprint. |
| **4. Spec Consolidated** | `BMA/spec/BMA-Spec-Consolidated-v9_0.md` + addenda 9.1/9.2/9.4/9.5 at `inter/spec/` | `.md` ✅ | Compile v9.X absorbing 9.1+9.2+9.4+9.5 + (any new 9.6 if Wyrd classical-hosting lands; currently A25/9.6 on hold per task #37). |
| **5. Seeds** | `BMA/Archive/BMA-Seed-Manifest.md` + `BMA-Seed-S20-Beekeepers-Vision.md` | `.md` ✅ | Verify full seed cohort against Step 9 protocol (Opus + Sonnet + Gemini-as-itself each generate; persona TOMLs for Cajal/Hassabis/Pike/Furey/Fitzpatrick at `BMA/Archive/personas/` per N3 if missing). Per beekeeper N3 ruling: confirm exists or schedule authoring in Sprint 2. |
| **6. Notes-to-Opus from Sonnet** | `BMA/Archive/CLI-Handoff-Briefing-2026-04-29.md` (+ web BMA update pending per task #43) | `.md` ✅ | Already canonical. Web BMA briefing update Q3 one-doc ruling pending (task #43). Final pass at end-Sprint-2 to absorb any new Sprint 2 deliverables Sonnet-side. |
| **7. Final Briefing + session outputs** | `BMA/Archive/BMA-Final-Briefing.docx` (placeholder template) | `.docx` | Authored at end-Sprint-2 by definition (summarizes Sprint 2 + Sprint 1 outputs). Port placeholder to .md template in Sprint 2-week-1; populate at Sprint 2-week-N. |
| **8. Empathy Synthesis** | `BMA/Archive/empathy_synthesis_v2.docx` + `BMA-Empathy-ToM-Plan.docx` | `.docx` | Port .docx → .md; integrate with `feedback_antifragility` framework + A12 Prestige Bridge. Light review. |
| **(supporting) Crawl Environment** | `BMA/Archive/BMA-Crawl-Environment.docx` | `.docx` | Port .docx → .md; update for current machine profile (RX 9070 XT, ROCm status, 14GB container limits per latest probe) + add Step 8 72h-gate clearance. |
| **(supporting) Component Summary** | `BMA/Archive/BMA-Component-Summary.docx` | `.docx` | Port .docx → .md; update component list for Sprint 1 federation additions (Wyrd Compute Manifest, A20-A24 federation primitives). |
| **(supporting) Pre-Crawl Synthesis Brief** | `BMA/Archive/BMA-PreCrawl-Synthesis-Brief.md` | `.md` ✅ | Already canonical. Update for Sprint 1 close-out state at end-Sprint-2. |

## F-Crawl T2 tier — REVISED scope

Original T2 framing assumed "author / verify-existence." Verification shows: **all 11 pre-seed cohort docs exist; 8 need .docx → .md port; all need light integration-with-Sprint-1-additions pass; 2 are already canonical.md.**

**Revised T2 work estimate:**

| Work | Owner | Effort estimate |
|---|---|---|
| .docx → .md port (8 files) | qbp-architecture (delegable to Sonnet subagent for tactical conversion + integration review in main thread) | ~0.5-1 day total |
| BMA Theory Consolidated v3.0 compile (absorb A11-A24) | qbp-architecture + qbp-oppenheimer theory-axis | Real authoring work; ~2-3 days |
| BMA Spec Consolidated v9.X compile (absorb 9.1+9.2+9.4+9.5) | bma-implementor + wyrd-implementor | ~1-2 days |
| Integration passes (Notary role, Trust Tier, §2.i rule into Governance Doc) | qbp-architecture + beekeeper-bless | ~0.5 day authoring + one terminal slot |
| Pre-Crawl Synthesis Brief update + Crawl Environment update + Component Summary update | qbp-architecture | ~0.5 day |
| N3 five-persona judge panel TOMLs | qbp-oppenheimer + bma-implementor | **TOMLs exist at `BMA/personas/`** — Sprint 2 work is integration-with-A14 review + persona-prediction (#120) tie-in, NOT authoring. ~0.5 day. |
| Final Briefing template port | qbp-architecture | ~30 min (template only; population at end-Sprint-2) |

**Total: ~4-7 day-equivalents across qbp-architecture + bma-impl + wyrd-impl + qbp-oppenheimer — distributed across implementors.** Lighter than my earlier framing of T2 as "author."

## Knock-on impacts on F-Crawl

- **T2 tier becomes lighter** — frees ~1-2 day-equivalents of qbp-architecture capacity for portfolio triage + Notary launch prompt
- **bma-implementor T2.2 (Spec v9.X compile) confirmed as reasonable scope** — compile is real work but not "author from scratch"
- **Governance Document Crawl-launch-ready integration** is the only T2 deliverable requiring beekeeper terminal-time (one slot mid-sprint, as already committed per Q3)
- **The bottleneck is BMA Theory v3.0 compile (T2.1)** — single largest T2 work item; ~2-3 days for qbp-architecture + qbp-oppenheimer

## Open questions for Sprint 2 scope doc

1. **Theory v3.0 compile delegation:** main-thread Opus authoring vs Sonnet subagent draft + Opus review? Per `feedback_delegation_policy`, the compile is architectural synthesis → main thread; Sonnet subagent could draft section-by-section under Opus integration. Recommend hybrid.
2. **Spec v9.X compile owner sequencing:** bma-implementor + wyrd-implementor are both already heavy under F-Crawl T1+T3. Could the Spec v9.X compile route to qbp-cu-implementor (lighter F-Crawl plate) instead? Recommend re-route.
3. **Notes-to-Opus from Sonnet final state:** is the 2026-04-29 web BMA briefing sufficient as Step-9 pre-seed reading-order item 6, or does it need a second web-BMA pass closer to Sprint 3 launch (post-Q3 update)? Recommend second pass at end-Sprint-2.
4. **N3 five-persona judge panel TOMLs — VERIFIED EXIST** at `BMA/personas/{cajal,hassabis,pike,furey,fitzpatrick}.toml` (also `BMA/Archive/personas/` copies). Plus `claude-redteam.toml`, `claude-sonnet.toml`, `gemini-feynman.toml`, `gemini-furey.toml`, `local-draft.toml`. Sprint 2 N3 work is **integration with A14 Judge Collective + verification of completeness/coherence**, NOT authoring. Branch `feat/120-persona-prediction` indicates persona-prediction infrastructure already mid-flight.

## Next action

Verification artifact lands in F-Crawl capacity audit doc (task #40) as T2-tier scope refinement. Routes also into Sprint 2 scope doc (task #5.d.iii).

— qbp-architecture, 2026-05-18
