---
name: issue-authoring
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every seat filing a GitHub issue on a `JamesPagetButler/*` repo
applies-to: issue shapes and templates, §I4 reader-lists, closes-when criteria, linking, anti-patterns, the naked→workshop transition, tenant CONTRIBUTING overlays
provenance: issue-authoring-best-practices.md §1, §2 (2.1, 2.2, 2.3, 2.4), §4, §5, §6, §7, §8, §9, §10; code-review-best-practices.md §8
refined: 2026-10-22 (inter#61 transcription). Companion skills: `closes-when-verification-test.md` (§2.2.2), `scope-globs.md` (§2.2.1), `housekeeping-label.md` (§6a), `closing-keywords.md` (§11), `repo-qualified-references.md` (§3, §6.3).
---

# Skill: Authoring a GitHub issue

## What an issue is
The presence of a GitHub issue is the **federation's Loop 2 entry marker** (Systema v0.8 three-loop progressive hardening: Reference → Guidance → Requirement). Filing an issue is the act of crossing from naked-level work (Loop 1, awareness-only, no formal test) into **workshop-level work** (Loops 2–3, soft test → hard test, with acceptance criteria).

An issue is therefore not a place to think out loud. Thinking-out-loud lives in chat, in bridge channels, in scratch docs. An issue is where a *commitment* lives — to a question, to a scope, to a reader-list, to a closes-when criterion. If those four things are not present, the artifact filed is not yet an issue; it is a draft.

## Quick reference before filing
When opening a new issue, ask:
1. **Is this Loop 2 work yet?** If no — close the editor, write in a scratch doc instead.
2. **Which of the four shapes is this?** If "I don't know" — the issue is not yet well-posed.
3. **Who is in the §I4 reader-list and what does each verify?** If "TBD" — file it as a design-surface to determine the reader-list first.
4. **What is the closes-when?** If "we'll know it when we see it" — refine until you can name testable criteria.
5. **What is the sequencing relative to other open issues?** If unknown — add the dependency graph before publishing.

If all five answer cleanly, file. If any answer with hand-waving, refine before filing.

## The four issue shapes
Every issue falls into one of four shapes. Mixing shapes is the most common authoring error and the most reliable predictor that the issue will not close cleanly.

| Shape | Use when | Tracks |
|---|---|---|
| **Design-surface** | Before doc / code / theory exists. The issue is the place where the decision is made. | Open question(s) with named decision-options; §I4 reader-list votes on options; resolution closes the surface. |
| **Ratification** | After doc / code / theory exists. The issue tracks reviewer signoff on already-authored artifact. | Artifact path(s); load-bearing commitments; reader-list acks; closes-when = all acks landed + downstream coupling verified. |
| **Sub-issue** | A scoped subset of a parent issue, requiring its own reader-list or its own closes-when. | Explicit `parent_issue: #<N>` link; scope statement names what subset; reader-list may inherit or refine the parent's. |
| **Bug or incident** | Regression, runtime failure, post-mortem trigger. | Observed behavior; expected behavior; reproduction; impact assessment; remediation closes-when. |

### Design-surface template
A design-surface issue exists because **a decision must be made before authoring is responsible**. It is not "let's discuss"; it is "here are the named options, here is who decides, here is what 'decided' means."

```markdown
## Design-surface issue

**Why this issue exists:** <single-sentence statement of the decision required>

**Decision options:**
- **Option A:** <one-sentence + tradeoff>
- **Option B:** <one-sentence + tradeoff>
- **Option C:** <one-sentence + tradeoff>
(maximum 4 named options; if more, the decision is not yet well-posed — refine first)

**Recommendation:** <author's recommendation + one-sentence reasoning>

**§I4 D5 reader-list (decision authority):**
- [ ] @<reviewer-1> — <domain authority justification>
- [ ] @<reviewer-2> — <domain authority justification>
- [ ] @beekeeper — final call

**Closes-when:**
1. Decision recorded with named choice + rationale (PR comment or attached decision doc)
2. Downstream artifacts cited (ratification issues filed; doc PRs opened)
3. Bridge channel `<channel>` notified of the decision

**Author cart:** <Theory Cart | Engineering Cart | Information Cart>
**Sequencing:** <what's blocked-until-this-closes | what this is blocked-until>
```

### Ratification template
A ratification issue exists **after the artifact exists** — to bring the reader-list into formal signoff on a doc / spec / theory / code drop (pattern used for `repo-bma-systema-issue-#163`–`#167`).

```markdown
## Ratification + reviewer-ack issue

**Artifact(s):**
- Theory doc: `<path>`
- Operational companion: `<path>`
- (Optional) Tracking issues / sub-issues this absorbs: `repo-<name>-issue-#<N>`

**Load-bearing commitments:** (numbered list — the things reviewers must validate)
1. <commitment 1 — concrete, testable claim>
2. <commitment 2 — concrete, testable claim>
...

**§I4 D5 reader-list (signoff required before close):**
- [ ] @<reviewer-1> — <what this reviewer specifically verifies>
- [ ] @<reviewer-2> — <what this reviewer specifically verifies>
...
- [ ] @beekeeper — final HVR pass

**Closes-when:**
1. All §I4 acks landed
2. Cross-doc forward-references verified (downstream addenda / spec / code refer to this correctly)
3. Bridge channel `<channel>` receives the `LANDED — repo-<name>-issue-#<this>` ack
4. **Verification test:** named specific test that proves the artifact's claims (see §2.2.2 — REQUIRED for design-surface ratifications; OPTIONAL for doc-only or pure-process artifacts)

**Sequencing:** <blocked-after | sequenced-with | blocks>
```

Criterion 4 discipline: `skills/closes-when-verification-test.md`. If the artifact is a design surface committing to follow-on implementation PRs, also publish scope-globs: `skills/scope-globs.md`.

### Sub-issue template
A sub-issue scopes a *named subset* of a parent issue. The parent stays open; the sub-issue closes independently.

```markdown
## Sub-issue under repo-<name>-issue-#<parent>

**Parent issue:** `repo-<name>-issue-#<parent>` — <one-sentence parent scope>

**Scoped subset:** <single-sentence statement of what this sub-issue covers that the parent does not directly>

**Why subset, not parent:** <reason — independent reader-list, distinct closes-when, parallel work, etc.>

**Closes-when:**
1. <criterion 1>
2. <criterion 2>
3. Parent issue notified via comment that this sub-issue closed

**Reader-list:** <inherit parent's | refined: subset of parent's | extended: parent's + named additions>

**Sequencing:** Closing this sub-issue contributes to (but does not close) the parent.
```

### Bug or incident template
A bug or incident issue documents an observed deviation from the spec or an external incident requiring federation response.

```markdown
## Bug / incident report

**Observed behavior:** <what happens>
**Expected behavior:** <what should happen, with spec / theory reference>
**Reproduction:**
1. <step 1>
2. <step 2>
**Impact assessment:**
- Severity: ROUTINE | HIGH | SAFETY_CRITICAL
- Affected tenants: <list>
- Affected artifacts: <files / specs / running services>

**Post-mortem requirement:** <none | abbreviated | full PIVOT-class record per QBP pivot_protocol.md>

**§I4 reader-list:**
- [ ] @<implementor> — root-cause owner
- [ ] @<reviewer-cross-tenant> — federation-impact assessment
- [ ] @beekeeper — if Severity ≥ HIGH

**Closes-when:**
1. Root cause identified and recorded
2. Remediation merged (link PR)
3. Test added that would have caught the bug (per `test-quality-best-practices.md`)
4. If Severity ≥ HIGH: PIVOT-class record filed
5. If incident exposed a spec gap: design-surface issue filed for the gap
```

### Include the test that would prove the fix
When filing an issue that has a code expectation, **include the test that would prove the fix** (code-review-best-practices §8):

````markdown
## Expected behavior
<one or two sentences>

## Test that would prove the fix
```go
func TestX_when_Y_then_Z(t *testing.T) {
    // arrange
    // act
    // assert ...
}
```
````

Why it matters:
- The author gets a concrete acceptance target — no ambiguity about "fixed"
- The reviewer has a one-line check: does this test exist + pass in the PR?
- If the issue says "test would prove the fix" and the PR doesn't include it, the PR is incomplete by definition

## §I4 reader-list discipline
`§I4` in this doc's usage means **Issue-class 4 reviewer discipline** — the formalized reader-list a workshop-level artifact requires (see ledger CONFLICT C4 on the competing ADR-003 §I4 expansion).

### Reader-list structure
- **Named persons or personas** — never role-classes without names. "Wyrd-implementor" names a specific persona; "someone from Wyrd" does not.
- **Per-reviewer justification** — what specifically this reviewer verifies. "@cth-implementor — NT_AUTONOMIC_SIGNAL anchor-flow + provenance chain" is good; "@cth-implementor — review" is not.
- **Beekeeper is always last** unless the issue is *itself* a Beekeeper question. The Beekeeper's HVR pass closes the loop after domain reviewers have signed off.
- **Cross-tenant readers required for federation-impact issues** — at minimum one reviewer outside the originating tenant. This is what makes federation-impact distinct from tenant-internal.

### What counts as an ack
A reviewer's signoff takes one of three shapes, posted as a comment on the issue or in the relevant bridge channel:
- **APPROVE** — reviewer asserts the §I4 checks they were named for all pass.
- **APPROVE-WITH-CONCERN** — passes overall, but with named follow-up that does NOT block close (must be filed as a separate sub-issue if material).
- **DEFER** — reviewer cannot complete the check in scope; names another reviewer or asks for more info. DEFER does not advance the issue's close-readiness.

Implicit silence is **never** an ack. If a reviewer has not posted one of the three, they have not signed off, even if the rest of the reader-list has.

### Reader-list sizing by shape

| Shape | Minimum reader-list |
|---|---|
| Design-surface | 2 domain reviewers + Beekeeper |
| Ratification (tenant-internal) | 1 tenant-implementor + Beekeeper |
| Ratification (federation-impact) | 2 tenant-implementors + 1 cross-tenant + Beekeeper |
| Sub-issue | Inherit parent's; can be reduced if scope is genuinely narrower |
| Bug / incident | Root-cause owner + (cross-tenant if federation-impact) + Beekeeper if Severity ≥ HIGH |

## Closes-when criteria
The closes-when section is the **only** thing that makes "closed" mean something. Without it, "closed" means "we got tired of looking at this issue." Properties every criterion must have:
- **Testable.** Objectively verifiable by a third party who reads the issue cold. "Tests pass" is testable; "code is clean" is not.
- **Named.** Specifies *what* completes it. "Reader-list acks landed" without naming the reader-list is not named. "All seven reader-list acks per §I4 above landed" is named.
- **Dated where applicable.** If a criterion has a temporal component (e.g., "SAFETY_CRITICAL 72h cooldown completed"), it names the time anchor. No temporal component is fine — but ad-hoc "soon" or "after we figure out X" is not a closes-when criterion; it is a deferral.
- **Not padded.** If a criterion is not load-bearing for closing the issue, it does not belong in closes-when. Wishlist items belong in follow-up sub-issues filed alongside close. The closes-when list is the *minimum sufficient* set.

## Linking conventions
### Forward references
When this issue's closing creates downstream work, the body lists the downstream artifacts:

```markdown
**Downstream (filed when this lands):**
- Sub-issue `repo-<name>-issue-#<N>` — <scope>
- Bridge notification on `<channel>` — `LANDED — repo-<name>-issue-#<this>`
- Memory update: `<memory-file>` if applicable
- Cross-doc update: `<file-path>` references this issue
```

### Backward references
When this issue closes a gap surfaced elsewhere, the body links the surfacing context:

```markdown
**Surfaced by:**
- Gemini-3-Pro review YYYY-MM-DD point (N)
- Bridge channel `<channel>` seq=<N>
- `repo-<name>-issue-#<N>` (parent / related)
- Memory: `<memory-file>` documenting the prior decision
```

Reference form and the no-phantom-handles rule: `skills/repo-qualified-references.md`.

## Anti-patterns
Issues that exhibit these are failures of authoring discipline; close-with-redirect is the right response, not "let's just live with it."

| Anti-pattern | Why it fails | Redirect |
|---|---|---|
| **Open-ended discussion thread** | No decision, no scope, no close criterion. Belongs in chat or bridge channel. | Reframe as design-surface or close. |
| **"Investigate X"** | Investigation is naked-level work (Loop 1); not yet workshop. | Demote to TODO / scratch note; refile when there's a question or candidate decision. |
| **Reader-list with no per-reviewer justification** | "Two pairs of eyes" without naming what each reviewer checks → diffuse responsibility → silent non-review. | Add justifications, or shrink the reader-list. |
| **Closes-when = "looks good"** | Subjective; cannot be verified after-the-fact. | Replace with testable criteria. |
| **Shape mixing** (e.g., design-surface body with ratification reader-list) | Reviewers don't know whether to decide or to validate. | Split into two issues. |
| **No artifact path on ratification** | Reviewers can't find what to review. | Add path; if no path, the issue is design-surface not ratification. |
| **Wishlist closes-when** | Issue stays open forever waiting for items that aren't load-bearing. | Move wishlist to sub-issues filed alongside close. |
| **Bare `#<N>` for cross-repo** | Ambiguous in federation context. | Use a repo-qualified reference (`skills/repo-qualified-references.md`). |

## The naked → workshop transition (Systema mapping)
Per Systema v0.8 three-loop progressive hardening:

| Systema loop | Constraint hardness | Where work lives |
|---|---|---|
| **Loop 1: Ideation** | Reference (awareness, no formal test) | Chat, bridge channel, scratch doc, exploratory notebook |
| **Loop 2: Architectural** | Guidance (directional, soft test) | **GitHub issue** — design-surface or early ratification |
| **Loop 3: Real-World** | Requirement (mandatory, hard test) | GitHub PR + merged artifact + closes-when satisfied + downstream coupling verified |

Filing a GitHub issue declares "this has crossed from awareness into workshop." Once filed, the artifact is held to workshop-level discipline. Once merged + closed, it crosses to Loop 3 (Requirement).

**The transition is one-way absent explicit retrograde authorization.** A workshop-level issue does not get "downgraded back to naked" — it gets closed (with or without resolution) and any surviving uncertainty is refiled as a fresh issue with workshop-level scope. This prevents naked-level musings from contaminating workshop-level commitments. Don't file an issue you wouldn't sign your name to in front of the §I4 reader-list.

## Per-tenant CONTRIBUTING.md overlay
Each federation tenant repo (`bma-systema`, `wyrd`, `qbp`, `qbp-compute-unit`, `Contextus`, future tenants) hosts a `CONTRIBUTING.md` at the repo root that:
1. **References the federation issue-authoring standard** as the canonical standard
2. **Adds a tenant-specific overlay** for:
   - Default reader-list members (the implementors who default-review for that tenant's repo)
   - Tenant-specific issue labels (e.g., `bma:layer-0-cognitive`, `bma:layer-4-physical`, `qbp:cu-substrate`)
   - Tenant-specific closes-when extensions (e.g., "for QBP substrate-Lean PRs, additional criterion: Compute Manifest mode (b) extraction-and-execute log attached")
   - Tenant-specific shape preferences (e.g., "Wyrd never uses bug-or-incident — substrate failures are PIVOT-class incidents handled in `repo-wyrd:doc/pivots/`")

The CONTRIBUTING.md is the local extension; the federation standard is canonical. Where they conflict, the federation standard wins unless the tenant CONTRIBUTING.md explicitly documents a tenant-scoped exception with rationale. Template: `inter/contributing-md-template.md`.

## Labels and milestones
See `skills/issue-labels-and-milestones.md`.

## Wisdom anchors
`w-right-altitude` · `w-one-purpose` · `w-name-one-owner` · `w-silence-not-assent` · `w-define-done-testably` · `w-test-can-fail` — see `inter/wisdoms/_federation.md`. Gates: `pr-merge-completeness`, `named-reviewer-responsiveness`.
