# Meeting Prep — Toddle Design Session

**Federation-wide design alignment on Toddle scope after the 2026-05-13 architectural cluster. Loop-1 Reference review per Systema progressive-hardening: ensure shared understanding *before* any guidance-level design. Crawl→Toddle gate is currently blocked on Step 9 (succession + Governance Doc) + OD-12 (drive) + OD-11(c) implementation kickoff — implementors can scope in parallel with Step 9 completion.**

> Prepared by: qbp-architecture (Claude Opus 4.7), 2026-05-13
> Channel: `toddle-design` (auto-creates on first post)
> Format: async kickoff → sync if blockers surface → async ratification

---

## 1. Attendees

| Tier | Who | Reason |
|---|---|---|
| Required | beekeeper, bma-implementor, wyrd-implementor, qbp-architecture | Toddle scope decisions land on bma/wyrd; beekeeper has decision authority; qbp-architecture facilitates |
| Recommended | bma (Marcy gen 61), qbp-implementor | Governance read on bilateral arch; QBP-EXP-11 + 208-theorem archive are Theory-Cart-tool use cases |
| Optional | cth-implementor, contextus-impl, qbp-cu-implementor, Gemini | OD-11(c) changes the Wyrd surface they consume; Gemini is Theory-Cart counterpart per Systema §7 |

## 2. Pre-read (in order)

1. `~/Documents/inter/workspace-phase-architecture.md` **§Phase 2 — TODDLE** (~200 lines, Mermaid + ASCII)
2. `~/Documents/inter/workspace-phase-architecture.md` **§0.10 — Cart-driven tool acquisition** (cart inventory + comparison to Claude's tool registry)
3. `~/Documents/inter/workspace-roadmap.md` **§2.1 + §2.1b** (BMA Crawl→Toddle + Toddle→Walk gates)
4. `~/Documents/inter/workspace-roadmap.md` **§6 OD-2/11/12/13** (open decisions; OD-11 decided option c)
5. [bma-systema #154](https://github.com/JamesPagetButler/bma-systema/issues/154) (issue body + 3 follow-up comments)

## 3. Decisions made today — one line each

| # | Decision |
|---|---|
| 1 | **Toddle** ratified — intermediate between Crawl/Walk; 7-day endurance on Crawl hw + drive upgrade |
| 2 | **Walk HW = networked RISC-V** (not bigger workstation); same form factor as Sharp Butler House Node |
| 3 | **OD-11 = (c)** — Wyrd absorbs hg/'s BMA-specific structures; BMA `hg/` becomes thin shim then retires |
| 4 | **Sharp Butler context test at Walk** — uses Toddle's already-live L5/L6 to validate before SB joins |
| 5 | **Cart-driven tool acquisition** — BMA actively participates; tools live on carts; harness exposes them |
| 6 | **Four-cart taxonomy** (Theory + Engineering + Art + Information); supersedes v0.8 two-cart + §10.7 three-cart |
| 7 | **Art Cart loops** = Napkin → Studio → Gallery (parallels Engineering's three-loop hardening) |

Detail in pre-read items 1-5.

## 4. Agenda

**Block A — Shared understanding (async, 1 work cycle).** Each required attendee posts ack on `toddle-design` confirming pre-read complete + flagging any sections that surprised them.

**Block B — Per-implementor first-wave PR scoping (async, 1-2 cycles).**

- **bma-implementor:** continuous-loop scaffold (full bilateral on Crawl hw) + L5/L6 inference-time arch + action-selection test harness + cart-tools harness (Theory: Python+Lean; Information: deliverable generators) + Wyrd-shim consumption
- **wyrd-implementor:** OD-11(c) Wyrd extensions for NT_SEED + salience=1.0 + other BMA-specific structures (needs inventory from bma-implementor); migration path; §I4 review pattern
- **qbp-implementor:** confirm QBP-EXP-11 + 208-theorem archive are the right load-bearing use cases for Theory Cart Python+Lean

**Block C — Open decisions (sync if needed).** OD-12 drive spec, OD-13 GPU placement. OD-2 RISC-V SBC spec defers to a separate procurement meeting.

**Block D — Action items out.** Per-implementor first-wave PR list + per-repo issues filed (BMA sub-issues under #154; Wyrd new issue for OD-11(c) absorption; QBP/QBP-CU RISC-V cross-compilation prep).

## 5. Decisions needed from this meeting

| ID | Decision | Owner |
|---|---|---|
| TD-1 | First-wave Toddle PR list per implementor (BMA + Wyrd minimum) | bma-implementor + wyrd-implementor + beekeeper |
| TD-2 | OD-12 drive spec (NVMe-via-addon vs. larger durable SATA) | beekeeper |
| TD-3 | OD-13 GPU placement (ROCm-as-server default vs. T1-on-RISC-V-NPU) | beekeeper + bma-implementor |
| TD-4 | NT_SEED + BMA-specific-structure inventory passed BMA → Wyrd | bma-implementor → wyrd-implementor |
| TD-5 | Theory Cart tool priority — Python first or Lean first | bma-implementor + qbp-implementor |
| TD-6 | Sharp Butler context test design — defer to separate meeting? | beekeeper + qbp-architecture |

## 6. Out of scope (deferred, not blocking)

- Wyrd #36 + CTH #59 README refreshes (low-urgency)
- BMA #153 spec vocab refresh (next spec revision)
- Multi-tenant scaffolding design (Walk concern, not Toddle)
- Systema v0.9 spec revision (formalise 4 carts + Art Cart)

## 7. Token + model discipline (beekeeper directive 2026-05-13)

The architectural pattern is the same as cart-driven tool acquisition: **the cart picks the model + effort the way the cart picks the tool.**

### Cart-model mapping

| Cart | Default model | Effort | Why |
|---|---|---|---|
| **Theory Cart** | **Opus 4.7 (Claude) + Gemini 3-Pro / 2.5-Pro (Furey + Feynman personas per Spec §7)** | **HIGH** | Spec generation, paradigm enumeration, bifurcation detection, evidence weighing — genuinely Opus-shape. Theory is reusable, evolves slowly; investment in quality compounds. |
| **Engineering Cart** | Sonnet at Loops 1-2 (Ideation/Architectural); Opus at Loop 3 (Real-World) + gate reviews | MEDIUM at Loop 1-2; HIGH at Loop 3 | Loop 1 tolerates breadth at lower cost; Loop 3 requires precision for compliance |
| **Art Cart** | Sonnet for Napkin (exploration); Sonnet/Opus for Studio + Gallery | LOW-MEDIUM Napkin; MEDIUM-HIGH Studio/Gallery | Creative exploration is cheaper; technique application + audience-readiness requires consistency |
| **Information Cart** | Haiku for Classify + Render; Sonnet for EligibleVenues + ProposePromotion | LOW-MEDIUM | Rule-following entropy reduction; mostly cheap |

This extends [feedback_delegation_policy.md](~/.claude/projects/-home-prime-Documents/memory/feedback_delegation_policy.md). The pattern *"tactical to Sonnet/Haiku; architectural synthesis to Opus"* is the same rule now expressed in Systema vocabulary.

### Token-saving tips to adopt (per https://www.analyticsvidhya.com/blog/2026/05/tips-for-claude-code-token-saving/)

Each implementor instance should run with:

- `/compact` before long Engineering-Cart sessions; auto-compact threshold env var at 70 (Tip 3)
- `/clear` between unrelated scopes; don't carry old debugging into new work (Tip 1)
- **Filter logs** at extraction (`grep -A 5 -E "FAIL|ERROR" | head -120`) rather than dumping full output into context (Tip 12)
- **Specific file paths** in prompts; avoid "look around the repo" prompts (Tip 19)
- **Provide verification targets upfront** — exact test names, expected outputs — to prevent correction loops (Tip 20)
- **Delegate verbose research to subagents** (Explore for codebase questions); main thread reserves Opus for architectural synthesis (Tip 13)
- **Cap MCP output** via `MAX_MCP_OUTPUT_TOKENS=8000` and bash output via `BASH_MAX_OUTPUT_LENGTH=20000` (Tips 10-11)
- **Deny patterns** in `~/.claude/settings.json` for `.env`, `node_modules/`, `dist/`, `logs/` (Tip 18)

Walk these through with attendees in the meeting kickoff. Each implementor adopts what fits their workflow; report back on what worked or didn't at the closeout.

---

*Meeting Prep v0.3 (token-audited + cart-model mapping added per beekeeper directive 2026-05-13)*
*qbp-architecture (Claude Opus 4.7)*
*Token-saving tips reference: https://www.analyticsvidhya.com/blog/2026/05/tips-for-claude-code-token-saving/*
