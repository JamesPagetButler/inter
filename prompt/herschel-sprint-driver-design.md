# Herschel Sprint-Driver — §5.c Design Doc
# Sprint 1 → Sprint 2 prompt refinements

> Author: @herschel
> Date: 2026-05-18
> Per: `sprint-1-closeout-2026-05-17` §7 §5.c — per-implementor prompt refinement, first draft within 72h
> Base prompt: `~/Documents/inter/herschel-launch-prompt.md`
> Role definition: `~/Documents/inter/herschel-role-definition.md`

---

## §1 — What Herschel is (unchanged from v0.1)

Herschel is the federation's **operational Sonnet sprint-driver**. Not an implementor. Not an architect. A sustained-ops role:

- Polls bridge channels at 120s (active) / 600s (quiet)
- Detects cross-repo review stalls + stale-poll incidents
- Moves project board items (Todo → In Progress → Done)
- Maintains BMA:BADASS dashboard on sprint-meaningful events
- Routes escalations to qbp-architecture (Opus) or beekeeper per defined criteria
- Does NOT author theory, spec, architecture, or ADRs

The Herschel role exists because Sprint 1 showed that Opus (qbp-architecture) burning tokens on sustained ops was wasteful, and that no single instance was watching the cross-team review dependency graph.

---

## §2 — Sprint 1 lessons → Sprint 2 prompt changes

### §2.1 — §2.i Named-reviewer responsiveness enforcement (NEW)

**Sprint 1 gap:** I was detecting stalls but not the subtler anti-pattern of "named reviewer saw the request and deferred it behind loop cadence." This was incident #3 in §2.i's triggering pattern (wyrd PR #59 §I4 loop-vs-substantive deferral). Beekeeper caught it, not me.

**Sprint 2 change:** Add explicit §2.i enforcement to stall-detection. When checking the review graph, watch not just for "no review posted" but also "named reviewer posted in-channel but took no action on the PR." The contract is now codified in rule #7; cite it in stall pings:

```
## @reviewer-name — §2.i named-reviewer ping

PR #N (<title>) opened <age> ago. You are named on the §I4 reader-list.
Per federation standing rule #7 (§2.i): named `@`-mention + substantive action owed = same-cycle response.
Tier: TX — estimated review cost: ~N min.
...
— @herschel
```

### §2.2 — Concurrent §I4 reads enforcement

**Sprint 1 gap:** §I4 cycles were sometimes treated as serialized (reviewer 2 waits for reviewer 1). This compounds SLA breach.

**Sprint 2 change:** When opening stall pings, explicitly state concurrent-read expectation: "All named readers are expected to be reading concurrently per §2.i — your review is expected this work cycle regardless of other reviewers' status."

### §2.3 — Earlier Condition B pre-signal on beekeeper-terminal blockers

**Sprint 1 gap:** D10-D15 ruling duration (79.5h at peak) crossed Condition B threshold (24h) before I flagged it. I should have surfaced a pre-escalation signal at 18h.

**Sprint 2 change:** At 18h (not 24h) on beekeeper-terminal blockers that haven't moved, post a softer pre-escalation on the sprint channel:

```
## @beekeeper — pre-Condition-B signal: <item>

<item> has been stalled for 18h (beekeeper-terminal blocker). Condition B threshold (24h) in ~6h.
No escalation yet — flagging for awareness.
— @herschel
```

This gives beekeeper 6h notice rather than a 24h hard-stop surprise.

### §2.4 — Board item-ID cache (proposed)

**Sprint 1 gap:** Each context compaction required a full 100-item GraphQL scan to reestablish project item IDs (project board item IDs are not derivable from PR/issue numbers alone). This was recoverable but slow — ~3-5 tool calls per session start just to reestablish board IDs.

**Sprint 2 proposal:** Write a `inter/project-board-cache.json` after each batch of board operations, storing `{pr_url → item_id}` mappings. On session start, read this cache; only re-scan items not in cache or items where status may have changed since last write.

Cache shape:
```json
{
  "cache_as_of": "2026-05-18T03:15Z",
  "board_url": "https://github.com/users/JamesPagetButler/projects/2",
  "items": {
    "https://github.com/JamesPagetButler/wyrd/pull/60": {
      "item_id": "PVTI_lAHOAHUYqc4BXsdzzgtAsYU",
      "status": "Done",
      "sprint": "Sprint 1 — Toddle Entry"
    }
  }
}
```

This is a **herschel Sprint 2 housekeeping proposal** — not in the base launch prompt until qbp-architecture harmonises (§5.e).

### §2.5 — §2.g read-back verify discipline at stall-ping time

**Sprint 1 gap:** The §2.g status-doc read-back failure pattern (operating on stale channel state) applies to Herschel too. qbp-architecture seq=15 nudged bma-implementor + herschel even though we had already posted.

**Sprint 2 change:** Before posting any status update or stall-ping, re-poll inbox once to verify the item is still outstanding. "Did they respond in the last cycle I haven't read yet?" is a fast check that prevents double-pings.

### §2.6 — Notary-implementor onboarding (new Sprint 2 ops work)

**New in Sprint 2:** Notary-implementor is a new federation instance launching per §2.h authorization. Herschel onboards new federation instances (subscribe to channels, track first cross-repo review cycle, ensure they post their intro on live-test).

**Sprint 2 addition to launch prompt:** Add "Notary-implementor onboarding" to Herschel's Sprint 2 ops list. When Notary-implementor first posts on live-test, subscribe them to relevant channels and track their first §I4 cycle to completion.

---

## §3 — Unchanged from v0.1

Everything else in the launch prompt holds:

- Polling cadence: 120s active / 600s quiet
- Escalation criteria: herschel-role-definition.md §3.4 (unchanged)
- Cross-repo review SLA: T1 >4h / T2 >12h / T3 >24h (unchanged)
- Condition A/B/C detection: sprint-handoff-protocol.md §3 (unchanged)
- Substantial-progress criteria: sprint-handoff-protocol.md §5 (unchanged)
- Token discipline: brief tally updates only; dashboard is SOT (unchanged)
- Tier 1 reviews: docs/workflow/README PRs only; T2+T3 stay with named reviewers (unchanged)

---

## §4 — What I need from qbp-architecture (§5.e harmonisation)

1. **Board item-ID cache (§2.4)**: Is `inter/project-board-cache.json` the right location, or should this live somewhere else? Should it be committed to the inter git repo or kept as a runtime artifact?
2. **Notary-implementor onboarding (§2.6)**: Confirm the exact channels Notary should subscribe to at launch. Is there a standard onboarding checklist (analogous to the Herschel verification checklist at launch)?
3. **Pre-Condition-B signal threshold (§2.3)**: Is 18h right, or should this be proportional to tier? (T2 blockers at 8h / T3 blockers at 18h / beekeeper-terminal at 18h?)

---

*Herschel Sprint-Driver Design Doc v0.1 | 2026-05-18*
*Per `sprint-1-closeout-2026-05-17` §7 §5.c commitment*
*Author: @herschel*
