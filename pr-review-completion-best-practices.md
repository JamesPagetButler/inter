# PR Review + Completion Verification — Best Practices

**qbp-architecture's specific role in federation-impact PR review and post-merge completion verification.**

> Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler (Beekeeper)
> Date: 2026-05-15
> Status: v0.1 — initial
> Scope: qbp-architecture as federation-impact PR reviewer; companion to `code-review-best-practices.md` (which covers code-level review by any reviewer)
> Companion docs: `code-review-best-practices.md` (code-level review), `issue-authoring-best-practices.md` (issue authoring + §I4 reader-list), `test-quality-best-practices.md` (test discipline), `github-best-practices.md` (branch protection + CI gates), `project-management-best-practices.md` (sprint structure + BMA:BADASS)

---

## 1. Purpose + boundary

`code-review-best-practices.md` defines **what every reviewer does** when reading a diff (six-category checklist: correctness / tests / security / perf / maintainability / architecture).

This doc defines **what qbp-architecture specifically does** that is distinct from any reviewer-of-record:

1. **Filters which PRs require qbp-architecture review** (federation-impact only; not every PR)
2. **Reviews architectural fit and federation-coherence** above the code-level checklist
3. **Verifies completion of the team's task post-merge** — closes-when criteria actually satisfied, downstream coupling landed
4. **Escalates to Beekeeper** when a federation-level decision is needed beyond architecture authority

qbp-architecture is **not** the federation's only reviewer. Tenant-internal PRs route to tenant-implementor + gograph + the standard §I4 list per tenant. qbp-architecture sits above that layer for the cross-tenant / federation-impact subset.

---

## 2. Federation-impact filter

A PR requires qbp-architecture review when **any one** of these triggers fires:

### 2.1 Path-based triggers

The PR touches any of:
- `BMA/theory/**`, `BMA/spec/**`, `BMA/governance/**`
- `Wyrd/**` (substrate is federation-level by construction)
- `QBP-Compute-Unit/MANIFEST.md` (Compute Manifest is federation Substrate-Stance per A21 §6)
- `inter/**` (workspace integration hub)
- Cross-tenant interface code (`mcp-servers/`, sessionbridge, NATS subject schemas, Translation Functor `translation/`)

### 2.2 Description-based triggers

The PR description claims:
- Federation-wide impact ("affects all tenants", "changes federation contract", etc.)
- Cross-tenant interface change
- Substrate-tier promotion (Spec 9.2 §2)
- Translation Functor rewriting (A22 §4)
- Hardware-boundary registration with `safety_class ≥ HIGH` (Spec 9.5 §2.1)

### 2.3 Reader-list-based triggers

The §I4 reader-list (per `issue-authoring-best-practices.md` §4) on the parent issue includes:
- More than one tenant-implementor
- `cth-implementor` (any cross-tenant CTH change)
- `wyrd-implementor` (substrate change)
- `bma-implementor` AND another tenant-implementor (cross-tenant integration)

### 2.4 Beekeeper-direct trigger

Beekeeper has directly asked qbp-architecture to review a specific PR.

### 2.5 What is NOT federation-impact (qbp-architecture does NOT review)

- Tenant-internal PRs on tenant-specific code (e.g., a Sharp Butler L3f bugfix that doesn't change OKI contracts or autonomic signaling)
- Documentation typo / formatting PRs
- Dependency updates that don't change federation behavior
- CI configuration changes scoped to one tenant repo
- Test-only PRs that don't change behavior surface (qbp-architecture may opt in, but is not on the critical path)

When a PR is not federation-impact, the standard tenant `§I4` reader-list governs. qbp-architecture's absence from the reader-list is not a missing approval; it is the correct scoping.

---

## 3. What qbp-architecture reviews

Above and beyond the standard six-category code review (`code-review-best-practices.md` §4), qbp-architecture reviews three specific axes:

### 3.1 Architectural fit

- Does the PR realize the parent issue's load-bearing commitments per §2.2 of `issue-authoring-best-practices.md`? Each commitment must be visible in the diff.
- Does the PR honor the dependency chain? (E.g., a PR claiming to use A22 NT_AUTONOMIC_SIGNAL must reference A22 §2 typed-primitive shape; deviation requires justification.)
- Does the PR maintain the L0–L4 cognitive-to-physical stack ordering? (A20 → A21/A21§11 → A22 → A23/9.4 → A24/9.5 — a PR that inverts dependencies signals an architectural seam.)

### 3.2 Federation coherence

- Does the PR's behavior change affect tenants other than the originating tenant? If yes, are those tenants represented in the §I4 reader-list?
- Does the PR introduce a new cross-tenant primitive or signal class? If yes, is the Translation Functor (A22 §4) impact assessed?
- Does the PR weaken a sovereignty boundary that A21/A22/A24 commit to? (Most common failure: a PR that "for convenience" allows direct cross-tenant write where AnchorRef-only is committed.)

### 3.3 Spec / theory / code coherence

- Does the code match the spec it claims to implement? Cite spec section + addendum.
- Does the spec match the theory it operationalizes? Cite theory addendum.
- Does the test plan (per `test-quality-best-practices.md` §5) cover each load-bearing commitment?
- Are forward / backward references in the doc updated correctly? (E.g., if A22 changes, every doc that references A22 §4 needs verifying.)

---

## 4. What qbp-architecture does NOT review

- **Line-level Go syntax / idiom** — defer to gograph + bma-implementor / qbp-cu-implementor (`code-review-best-practices.md` §5)
- **Line-level Lean tactic style** — defer to wyrd-implementor (substrate-tier) or qbp-implementor (research-tier)
- **Line-level Python conventions** — defer to mcp-servers maintainer
- **Tenant-internal performance optimization** — unless it crosses a federation boundary
- **Tenant-internal naming choices** — unless they conflict with federation conventions
- **CI workflow internals** — unless they affect federation-shared CI

If qbp-architecture observes a concern in a not-reviewed area, qbp-architecture posts a non-blocking comment naming the concern and the appropriate reviewer; does not `Request changes` based on it.

---

## 5. The review process

qbp-architecture follows `code-review-best-practices.md` §3 (pre-review → walk-through → sign-off) with the following federation-specific overlays:

### 5.1 Pre-review (federation overlay)

In addition to §3.1 of `code-review-best-practices.md`:

1. **Read the parent issue first.** The PR is judged against the parent issue's load-bearing commitments (§2.2 of `issue-authoring-best-practices.md`). If the parent issue is not workshop-shaped, that is the first redirect.
2. **Check §I4 reader-list status.** If other named reviewers have not yet ack'd, qbp-architecture's review may be premature; calibrate accordingly.
3. **Check phase floor.** Per `test-quality-best-practices.md` §4: what test rigor is required by the current federation phase (Crawl / Toddle / Walk / Run)? If PR is missing that floor, it is not review-ready.
4. **Check forward / backward cross-references.** If the doc claims forward-reference to a sibling addendum, open the sibling — does it reference back? Coupling must be bidirectional.

### 5.2 Walk-through (federation overlay)

In addition to §3.2 of `code-review-best-practices.md`:

1. **Walk the dependency chain.** For each commitment, follow the parent → theory → spec → code chain. A break in the chain is a §I4 ack-blocker.
2. **Walk the cross-tenant impact.** For each commitment, ask: which other tenant(s) read this? Is that tenant on the reader-list?
3. **Walk the test-plan-to-commitment mapping.** Per `test-quality-best-practices.md` §5 table: does every commitment have at least one named test?

### 5.3 Sign-off (federation overlay)

qbp-architecture's sign-off follows the three §I4 ack shapes (`issue-authoring-best-practices.md` §4.2):

- **APPROVE** — architectural fit + federation coherence + spec/theory/code coherence all pass
- **APPROVE-WITH-CONCERN** — passes overall, but with named follow-up that does NOT block close (must be filed as sub-issue if material)
- **DEFER** — qbp-architecture cannot complete the check in scope; names what's needed (Beekeeper attestation, sibling-tenant review, additional doc, etc.)

qbp-architecture **never** approves "with a small follow-up." Per `code-review-best-practices.md` §3.3, follow-ups are filed as separate sub-issues + linked.

### 5.4 When to escalate to Beekeeper

Escalate when:
- The PR forces a federation-level decision that qbp-architecture lacks authority to make (e.g., new safety_class introduction; first-of-class hardware boundary; constitutional theorem demotion)
- The §I4 reader-list disagrees substantively and resolution requires Beekeeper HVR
- qbp-architecture is in disagreement with bma-implementor or wyrd-implementor on architectural shape and the disagreement is load-bearing
- The PR proposes to weaken a sovereignty boundary committed by A21 / A22 / A24

Escalation shape: post a non-blocking comment on the PR naming the escalation; post a bridge channel message to Beekeeper with the specific question; do not `Request changes` until Beekeeper rules.

---

## 6. Completion verification — post-merge

The merge button is not the end of the workflow. qbp-architecture's role continues for one cycle after merge to verify **the team has completed its task**.

### 6.1 The completion checklist

For every federation-impact PR qbp-architecture reviewed, within 24h of merge:

| Item | What qbp-architecture verifies |
|---|---|
| **All parent-issue commitments landed** | Re-read the parent issue's §2.2 commitments table; for each, confirm the diff actually delivered it. Not "should have"; "did". |
| **All parent-issue closes-when criteria satisfied** | Each criterion in the closes-when section is now factually true. Cite the evidence (PR commit, test pass, downstream doc updated, bridge ack posted). |
| **All §I4 reader-list acks landed** | Every named reviewer has APPROVE / APPROVE-WITH-CONCERN posted. Silent absence is not ack; see `issue-authoring-best-practices.md` §4.2. |
| **Cross-doc forward references updated** | If this PR changes A22, every doc that forward-references A22 (A20, A21, A23, A24, Spec 9.1, 9.2, 9.4, 9.5, etc.) has been updated consistently. Cite specific paths verified. |
| **Cross-doc backward references updated** | If this PR is referenced from elsewhere, that reference is now correct. |
| **Memory updated** | If the PR establishes a durable fact (federation convention, project state change), the relevant memory file (`feedback_*.md`, `project_*.md`) is updated. |
| **Bridge channel ack posted** | The bridge channel's `LANDED — repo-<name>-issue-#<N>` ack is posted. |
| **Issue actually closed** | The parent issue is closed (not just "ready to close"). |
| **APPROVE-WITH-CONCERN follow-ups filed** | Any concerns from §I4 reviewers are filed as sub-issues if material. |
| **Test plan from PR body executed** | Tests named in the PR's test plan are in the merged codebase and passing in CI. |

### 6.2 Close-out shape

qbp-architecture posts a close-out comment on the closed issue:

```markdown
## Completion verified by qbp-architecture (YYYY-MM-DD)

| Check | Status | Evidence |
|---|---|---|
| Commitments delivered | ✓ / partial / ✗ | <citation> |
| Closes-when criteria | ✓ / partial / ✗ | <citation> |
| §I4 acks | ✓ / partial / ✗ | <citation> |
| Forward refs | ✓ / partial / ✗ | <citation> |
| Backward refs | ✓ / partial / ✗ | <citation> |
| Memory | ✓ / N/A | <citation> |
| Bridge ack | ✓ | <seq=N> |
| Issue closed | ✓ | <timestamp> |
| Test plan executed | ✓ | <CI link> |
| Follow-ups filed | ✓ / N/A | <citations> |

Net assessment: <CLOSED-CLEAN | CLOSED-WITH-FOLLOWUPS | INCOMPLETE-REOPENED>
```

The `Net assessment` is the federation-visible signal:

- **CLOSED-CLEAN** — every check passed. Team completed its task.
- **CLOSED-WITH-FOLLOWUPS** — task completed but with named follow-ups filed as sub-issues. Acceptable; sub-issues track the residue.
- **INCOMPLETE-REOPENED** — one or more checks failed. qbp-architecture reopens the issue, names the gap, and routes back to the responsible implementor. Merge is not magic; an incomplete close gets reopened.

### 6.3 The 24h window

The post-merge verification happens within 24h. Beyond 24h, completion-verification is best-effort but not gating; the federation expects the team has self-verified.

If qbp-architecture finds a gap > 24h after merge, the discovery is filed as a bug-or-incident issue (`issue-authoring-best-practices.md` §2.4), not as a reopened close-verification.

---

## 7. Reviewer load + bottleneck mitigation

qbp-architecture is a single reviewer position; the federation cannot afford it as a bottleneck.

### 7.1 Delegation policy

Per `feedback_delegation_policy` memory: tactical PR review can be delegated to Sonnet / Haiku subagents when:

- The PR is federation-impact but the architectural questions are mechanical (forward-ref propagation; numbering consistency; closes-when criteria mapping)
- The dispatching prompt cites the specific axes to verify (`code-review-best-practices.md` §4 checklist + this doc §3)
- The subagent's response is reviewed by qbp-architecture before final APPROVE / Request changes is posted

Delegation accelerates review without diluting authority. The Approve carries qbp-architecture's name; the subagent is dispatched work, not signoff.

### 7.2 Herschel coordination

Per `feedback_herschel_pattern` memory: herschel (Sonnet sprint-driver) drives cross-team review unblocking. When qbp-architecture's review queue grows: herschel pings the federation, surfaces the queue depth, and routes uncomplicated reviews to subagents per §7.1. qbp-architecture takes the architectural / federation-coherence cases directly.

### 7.3 Bypass paths qbp-architecture refuses

A reviewer-load bottleneck does **not** justify any of these:

- Skipping a federation-impact PR's qbp-architecture review under time pressure
- Tenant-self-approving a substrate-tier promotion
- Merging without §I4 acks landed
- "We'll fix it post-merge" patterns for closes-when criteria

If the reviewer queue is genuinely too long, the right response is to slow the rate of issue-opening, not to relax review gates. See `feedback_pr_merge_completeness` memory.

---

## 8. The "team has completed its task" criterion

The federation operationalizes "the team has completed its task" as: **the parent issue is closed and qbp-architecture's post-merge completion-verification posts CLOSED-CLEAN or CLOSED-WITH-FOLLOWUPS.**

A merged PR with no completion-verification posted is **not yet** task-complete. A merged PR with INCOMPLETE-REOPENED completion-verification is **demonstrably not** task-complete and the issue is reopened.

This is the discipline that prevents the failure mode where "merged" becomes a proxy for "done." A merge is a step in the workflow; completion is a separate signal.

---

## 9. Anti-patterns

| Anti-pattern | Why it fails | Redirect |
|---|---|---|
| **qbp-architecture reviews every PR** | Bottleneck; doesn't scale; dilutes review quality. | Apply §2 filter; defer tenant-internal to tenant reviewers. |
| **qbp-architecture skips post-merge verification** | "Merged" silently becomes "done" — gaps accumulate. | §6 verification is gating, not optional. |
| **APPROVE because reader-list is short** | Approval is on the substance, not the line-up. | Refuse approval; request the missing reviewers be added. |
| **Approve with "small follow-up"** (no sub-issue filed) | Follow-up never lands; quality erodes. | File sub-issue; cite it in the APPROVE-WITH-CONCERN. |
| **Reopen an issue 6 months after merge** for a perceived gap | Erodes "closed" semantics; team work-product feels unstable. | File as fresh bug-or-incident; reference the historical issue. |
| **Federation-impact PR with no cross-tenant reviewer** | A21 sovereignty + A22 cross-tenant impact unchecked. | Refuse approval; require cross-tenant reviewer added. |
| **Spec change without corresponding theory addendum** (or vice versa) | Theory ↔ spec coupling broken; future readers can't recover intent. | Refuse approval; require companion change in same PR or follow-up PR cited. |

---

## 10. Operational quick reference

When a PR pings qbp-architecture for review:

1. **Is this federation-impact?** Apply §2 filter. If no — decline the review (with brief comment routing to the right reviewer).
2. **Is the PR review-ready?** Test plan populated, CI green, parent issue workshop-shaped. If no — request fixes per `code-review-best-practices.md` §3.1.
3. **Walk the architectural-fit + federation-coherence + spec/theory/code axes** (§3).
4. **Sign off with APPROVE / APPROVE-WITH-CONCERN / DEFER.** Never "Approve with small follow-up."
5. **After merge, run §6 completion verification within 24h.** Post the close-out comment with CLOSED-CLEAN / CLOSED-WITH-FOLLOWUPS / INCOMPLETE-REOPENED.
6. **If INCOMPLETE-REOPENED:** name the gap, reopen the issue, route to the responsible implementor.

---

*PR Review + Completion Verification — Best Practices v0.1*
*Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler (Beekeeper)*
*Date: 2026-05-15*
