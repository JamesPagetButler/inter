# Issue Authoring — Best Practices

**Federation-wide standard for GitHub issue authoring.** Defines the four issue shapes, required sections per shape, repo-prefix referencing, §I4 reader-list discipline, and acceptance-criteria conventions.

> Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler (Beekeeper)
> Date: 2026-05-15
> Status: v0.1 — initial
> Scope: All workspace repos (BMA, QBP, QBP-Compute-Unit, Wyrd, CTH, Contextus, Sharp Butler, Möbius Fusion, future tenants)
> Companion docs: `code-review-best-practices.md`, `pr-review-completion-best-practices.md`, `test-quality-best-practices.md`, `github-best-practices.md`, `project-management-best-practices.md`

---

## 1. Purpose

The presence of a GitHub issue is the **federation's Loop 2 entry marker** (Systema v0.8 three-loop progressive hardening: Reference → Guidance → Requirement). Filing an issue is the act of crossing from naked-level work (Loop 1, awareness-only, no formal test) into **workshop-level work** (Loops 2–3, soft test → hard test, with acceptance criteria).

An issue therefore is not a place to think out loud. Thinking-out-loud lives in chat, in bridge channels, in scratch docs. An issue is the place where a *commitment* lives — to a question, to a scope, to a reader-list, to a closes-when criterion. If those four things are not present, the artifact filed is not yet an issue; it is a draft.

This doc names the four legitimate issue shapes, the required sections per shape, and the discipline that makes "closed" mean something.

---

## 2. The four issue shapes

Every issue in the federation falls into one of four shapes. Mixing shapes is the most common authoring error and the most reliable predictor that the issue will not close cleanly.

| Shape | Use when | Tracks |
|---|---|---|
| **Design-surface** | Before doc / code / theory exists. The issue is the place where the decision is made. | Open question(s) with named decision-options; §I4 reader-list votes on options; resolution closes the surface. |
| **Ratification** | After doc / code / theory exists. The issue tracks reviewer signoff on already-authored artifact. | Artifact path(s); load-bearing commitments; reader-list acks; closes-when = all acks landed + downstream coupling verified. |
| **Sub-issue** | A scoped subset of a parent issue, requiring its own reader-list or its own closes-when. | Explicit `parent_issue: #<N>` link; scope statement names what subset; reader-list may inherit or refine the parent's. |
| **Bug or incident** | Regression, runtime failure, post-mortem trigger. | Observed behavior; expected behavior; reproduction; impact assessment; remediation closes-when. |

### 2.1 Design-surface shape

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

### 2.2 Ratification shape

A ratification issue exists **after the artifact exists** — to bring the reader-list into formal signoff on a doc / spec / theory / code drop. The pattern most recently used for `repo-bma-systema-issue-#163`–`#167`.

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

### 2.2.2 Verification-test discipline — closes-when criterion 4

*Effective 2026-05-15 per beekeeper Sprint 1 close-out finding (`repo-inter-issue-#4`). Federation-wide concern: design-on-design cycles accumulate verification debt silently when closes-when criterion 4 is left soft ("first post-update implementation PR demonstrates the discipline") — the demonstration PR sits behind another design surface, the claim space grows, the verification space doesn't.*

Every **design-surface ratification issue** (per §2.2 — issues whose artifact is a theory addendum, spec addendum, ADR, or design doc that commits the federation to behavior NOT yet implemented in running code) MUST populate closes-when criterion 4 with **three specific fields**:

#### 2.2.2.a The verification test itself

A named test that proves the artifact's claim works. Not "first implementation PR demonstrates the discipline." Not "tests pass." A specific, namable test with three properties:

1. **Names what it verifies** in test-function-name form (e.g., `TestComputeManifest_RoundTrip_RejectsMalformedYAML`, `TestPentagonPodHotSwap_StateFlushPreservesCognitiveTrace`, `TestTranslationFunctor_MagnitudePreservationUnderFuzz`)
2. **Is executable in CI** — `go test`, `python -m pytest`, `lake build`, or equivalent; reviewer can re-run the test from the closes-when description alone
3. **Has a failure condition** — if the test passes when the artifact is broken, the test is fake; closes-when criterion 4 has not been met

Example shapes:

| Artifact class | Verification-test shape |
|---|---|
| Theory addendum (algebraic invariant claim) | Lean theorem statement + mode (a) type-instantiation + (if runtime-claim) mode (b) extraction-and-execute per Spec 9.2 §3 |
| Spec addendum (operational protocol) | Integration test exercising the protocol end-to-end against the substrate it governs |
| ADR / design doc (substrate API) | Round-trip test: load fixture → validate → snapshot → query each named field; assert validation rejects each named malformed case |
| Federation governance rule | Process-rule test: the rule's enforcement mechanism (CI check, label, gate) runs against a malformed input and rejects it |

#### 2.2.2.b The PR or sprint where the test lands

A named landing target:
- A specific PR (e.g., "lands as Phase 2 of `repo-bma-systema-pr-#172`")
- A specific sprint (e.g., "Sprint 2 — Federation Integration; sub-issue to be filed at sprint kickoff")
- A specific milestone (e.g., "Walk-α entry gate — closes when M1 cosim Tier B runs nightly")

Vague landing ("eventually"; "TBD"; "first implementation PR demonstrates the discipline") is **not acceptable**. Reviewers refuse §I4 ack on the ratification issue until the landing target is concrete.

#### 2.2.2.c The failure mode the test detects

A one-sentence statement of what the test catches if the artifact's claim is wrong. Example: *"This test catches an OnSeam dispatcher that does NOT enqueue deferred work when callback exceeds budget — the failure mode where the Pentagon Pod Subconscious-concurrent invariant silently breaks under heavy callback load."*

This forces the test author to articulate the falsification condition. A test that passes when nothing's wrong AND passes when something IS wrong is fake; the failure-mode statement makes that visible at review time.

#### 2.2.2.d Exception — non-design-surface ratifications

Doc-only artifacts that DO NOT commit the federation to behavior (e.g., best-practice docs; meeting records; status reports; this very §2.2.2 amendment) are exempt from criterion 4. The closes-when can mark criterion 4 as `N/A — non-design-surface ratification` with a brief reason.

If a reviewer disagrees with the N/A claim — i.e., they assert the artifact DOES commit the federation to behavior — they request changes with the §I4 ack-withholding mechanism, naming the claim that requires verification. The issue author either adds the verification-test specification OR withdraws the claim from the artifact.

#### 2.2.2.e Why this is structural, not procedural

Closes-when criterion 4 with this discipline operationalizes the federation's antifragility principle (`feedback_antifragility`): tests must catch failure modes that exist, not merely run-and-pass. A design surface that closes without naming its verification test is the federation analog of mocking the database in tests — the design works on paper but never against the substrate it claims to control.

The verification-test inventory at `repo-inter-issue-#4` (Sprint 1 verification-debt audit) is the canonical example of what this discipline prevents going forward: federation-wide claim accumulation without matching verification surface.

---

### 2.2.1 Scope-glob discipline for design-surface PRs that commit to follow-on implementation PRs

When a ratification issue's artifact is a **design surface** (a doc-only PR per the §I4 design-doc-as-S-01-review-surface pattern from ADR-003) that commits to follow-on implementation PRs, the design surface MUST publish **HARD scope-globs per implementation PR** in its body. Reviewers enforce scope-globs at implementation-PR review time: a diff outside the published scope-glob is `request changes` with a redirect to "file a new PR for that surface."

This discipline keeps implementation-cycle reviews bounded — scope-creep gets flagged at PR-open time rather than discovered late.

**Federation precedents:**
- `repo-qbp-compute-unit-pr-#33` §8 (M1 Gearbox design surface) commits to three implementation PRs (m1.1 / m1.2 / m1.3) with HARD scope-globs per file
- `repo-qbp-compute-unit-pr-#35` §5 (M1 verification strategy) commits to three implementation PRs (cosim-Tier-A / archtest / Tier-B-nightly) with the same shape

**Required format — `## Implementation sequence` section in the design surface body:**

```markdown
## Implementation sequence

The implementation PRs gated on this design surface, in dependency order:

| PR | Scope (HARD glob) | Effort | Depends on |
|---|---|---|---|
| `feat(<area>.<N>)` <one-sentence title> | `path/to/file1.<ext>` + `path/to/file2.<ext>` + `path/to/<area>_test.<ext>` | ~<N> days | <prior-PR or "none"> |
| `feat(<area>.<N+1>)` <title> | <files> | ~<N> days | <prior-PR> |
| ... | ... | ... | ... |
```

**Rules for the scope-glob:**

1. **HARD scope-glob means file-list, not pattern.** "Anywhere under `internal/foo/**`" is too loose; "`internal/foo/bar.go` + `internal/foo/bar_test.go`" is enforceable.
2. **Tests in scope.** Every implementation PR's scope includes its test files; a PR that adds production code without tests is request-changes by default per `test-quality-best-practices.md` §4 phase floor.
3. **Test files for new packages may be added on first scope-glob.** Subsequent PRs do not need to re-list existing test files unless they modify them.
4. **Generated files declared explicitly.** If the implementation generates code (codegen, protobuf, etc.), the generated files are part of the scope-glob; reviewers verify the generator + the generated artifact land together.
5. **Documentation in scope when implementation changes user-visible behavior.** A PR that ships a new API surface includes the README + relevant `doc/` sections in scope.
6. **Cross-package work splits across PRs.** If an implementation PR's natural scope spans two packages with separable surfaces, split into two PRs rather than widening scope.

**Reviewer enforcement:**

When an implementation PR is opened that cites its parent design-surface PR, the reviewer's first action (before reading the diff) is **scope-glob comparison**:

1. Fetch the parent design-surface's `## Implementation sequence` table
2. Find this PR's row
3. Run `git diff --name-only <base>...HEAD` and compare against the scope-glob
4. Files in the diff that are NOT in the scope-glob → `request changes` with redirect: *"Out-of-scope file `<path>` — file a separate PR or amend the design surface."*
5. Files in the scope-glob that are NOT in the diff → only fail if the PR's title/body claims them; absence-of-expected is a `comment`, not a `request changes`

If the parent design-surface lacked an `## Implementation sequence` section, the implementation PR's first review action is to redirect to the design-surface PR: *"Parent design surface missing `## Implementation sequence` table; please amend before implementation cycle proceeds."*

**Authoring exception:**

If the implementation work genuinely cannot be partitioned into scope-globs (e.g., a refactor that crosses many files atomically), the design surface MUST declare *why* in a `### Scope-glob exception` subsection of `## Implementation sequence`, naming the reason and the alternative bounding mechanism (e.g., line-count cap; or "single atomic refactor PR; reviewer reads the whole diff"). The exception is a deliberate decision, not a default.

**When this discipline does NOT apply:**

- Issues whose artifact is not a design surface (e.g., direct ratification of a doc; bug fixes; mechanical chores)
- Implementation PRs that are not gated on a design surface (open-design / iterative-development PRs)
- Single-PR scopes where the design + implementation land together (no follow-on cycle)

In these cases, normal PR-review discipline per `code-review-best-practices.md` §3-§4 governs.

---

### 2.3 Sub-issue shape

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

### 2.4 Bug or incident shape

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

---

## 3. Repo-prefix referencing — mandatory

All cross-issue and cross-PR references use the format:

```
repo-<repo-name>-<issue|pr>-#<number>
```

Examples:
- `repo-bma-systema-issue-#163`
- `repo-qbp-pr-#414`
- `repo-wyrd-issue-#42`

The bare form `#163` is acceptable **only** when the reference is in the same repo as the artifact being referenced. Cross-repo references always carry the repo prefix.

This is the federation discipline that prevents the "which #163 do you mean" failure mode when a session spans multiple repos. See `feedback_repo_prefixed_refs` memory for the original incident motivating this rule.

---

## 4. §I4 reader-list discipline

`§I4` in federation usage refers to **Issue-class 4 reviewer discipline** — the formalized reader-list that a workshop-level artifact requires. The shape:

### 4.1 Reader-list structure

- **Named persons or personas** — never role-classes without names. "Wyrd-implementor" names a specific persona; "someone from Wyrd" does not.
- **Per-reviewer justification** — what specifically this reviewer verifies. "@cth-implementor — NT_AUTONOMIC_SIGNAL anchor-flow + provenance chain" is good; "@cth-implementor — review" is not.
- **Beekeeper is always last** unless the issue is *itself* a Beekeeper question. Beekeeper's HVR pass closes the loop after domain reviewers have signed off.
- **Cross-tenant readers required for federation-impact issues** — at minimum one reviewer outside the originating tenant. This is what makes federation-impact distinct from tenant-internal.

### 4.2 What counts as a §I4 ack

A reviewer's signoff takes one of three shapes, posted as a comment on the issue or in the relevant bridge channel:

- **APPROVE** — reviewer asserts the §I4 checks they were named for all pass.
- **APPROVE-WITH-CONCERN** — passes overall, but with named follow-up that does NOT block close (must be filed as a separate sub-issue if material).
- **DEFER** — reviewer cannot complete the check in scope; names another reviewer or asks for more info. DEFER does not advance the issue's close-readiness.

Implicit silence is **never** an ack. If a reviewer has not posted one of the three, they have not signed off, even if the rest of the reader-list has.

### 4.3 Reader-list sizing by shape

| Shape | Minimum reader-list |
|---|---|
| Design-surface | 2 domain reviewers + Beekeeper |
| Ratification (tenant-internal) | 1 tenant-implementor + Beekeeper |
| Ratification (federation-impact) | 2 tenant-implementors + 1 cross-tenant + Beekeeper |
| Sub-issue | Inherit parent's; can be reduced if scope is genuinely narrower |
| Bug / incident | Root-cause owner + (cross-tenant if federation-impact) + Beekeeper if Severity ≥ HIGH |

---

## 5. Closes-when acceptance criteria

The closes-when section is the **only** thing that makes "closed" mean something. Without it, "closed" means "we got tired of looking at this issue." Three properties every closes-when criterion must have:

### 5.1 Testable

Each criterion must be objectively verifiable by a third party who reads the issue cold. "Tests pass" is testable; "code is clean" is not.

### 5.2 Named

Each criterion specifies *what* completes it. "Reader-list acks landed" without naming the reader-list is not named. "All seven reader-list acks per §I4 above landed" is named.

### 5.3 Dated where applicable

If a criterion has a temporal component (e.g., "SAFETY_CRITICAL 72h cooldown completed"), the criterion names the time anchor. If it has no temporal component, that is fine — but ad-hoc "soon" or "after we figure out X" is not a closes-when criterion; it is a deferral.

### 5.4 Closes-when must not be padded

If a criterion is not load-bearing for closing the issue, it does not belong in closes-when. Wishlist items belong in follow-up sub-issues filed alongside close. The closes-when list is the *minimum sufficient* set of criteria.

---

## 6. Linking conventions

### 6.1 Forward references

When this issue's closing creates downstream work, the issue body lists the downstream artifacts:

```markdown
**Downstream (filed when this lands):**
- Sub-issue `repo-<name>-issue-#<N>` — <scope>
- Bridge notification on `<channel>` — `LANDED — repo-<name>-issue-#<this>`
- Memory update: `<memory-file>` if applicable
- Cross-doc update: `<file-path>` references this issue
```

### 6.2 Backward references

When this issue closes a gap surfaced elsewhere, the issue body links the surfacing context:

```markdown
**Surfaced by:**
- Gemini-3-Pro review YYYY-MM-DD point (N)
- Bridge channel `<channel>` seq=<N>
- `repo-<name>-issue-#<N>` (parent / related)
- Memory: `<memory-file>` documenting the prior decision
```

### 6.3 No phantom handles

A reference must be to a real, filed artifact. Do not use placeholder handles like "the A18 handle" unless an A18 file actually exists at a known path. The 2026-05-14 phantom-handles incident is the canonical bad example — see `feedback_repo_prefixed_refs` memory for the cautionary tale. **Grep the repo before treating a handle as load-bearing.**

---

## 6a. The `housekeeping` label — non-blocking, important, not trivial

**Effective 2026-05-15 per beekeeper standing ruling.** Federation repos carry a `housekeeping` label (color `#fbca04`, gold-yellow) on `bma-systema`, `wyrd`, `qbp-compute-unit`, `QBP`, `Contextus`, `confluent-trust`, `inter`. The label exists to keep work flowing without sliding either way: it catches things that would be lost as "minor" if untagged, and it prevents agents from using "housekeeping" as a synonym for "I don't want to do this now."

### 6a.1 Three-criteria threshold

An issue qualifies for the `housekeeping` label **only if all three hold**:

1. **Important.** The work matters; deferring it costs the federation something measurable (audit trail gap, reference drift, doc rot, broken cross-link, stale convention). If the work is genuinely optional or cosmetic, do not file an issue at all.
2. **Non-blocking.** The work does not block any in-flight sprint scope. If it blocks, it's sprint-scope, not housekeeping — the label is wrong shape.
3. **Not trivial.** The work takes more than ~15 minutes of focused effort. Trivial fixes (typo, dead link, single-line tweak) belong in a passing PR or a one-line commit, not in a tracked issue with a label.

If any criterion fails, do not label as `housekeeping`. Either escalate to sprint-scope (criterion 2 fail = it's blocking), do the work in-line (criterion 3 fail = it's trivial), or close as "won't fix" (criterion 1 fail = it doesn't matter enough).

### 6a.2 Who labels

- **qbp-architecture** sets the policy + audits the housekeeping queue periodically (especially before sprint kickoff)
- **Tenant implementors** may apply the `housekeeping` label themselves **after** qbp-architecture has notified them they're authorized to do so (initial authorization happens via bridge announcement; renewed implicitly each sprint)
- **Beekeeper** can override any housekeeping classification at any time

The "implementor self-label" path is meant to keep momentum during normal work — when an implementor surfaces a non-blocking-important-non-trivial item, they tag it `housekeeping` themselves and continue with sprint work. The audit catches misclassifications.

### 6a.3 Anti-pattern: housekeeping as laziness shield

The most common failure mode is **using `housekeeping` to defer work that should be done now**. Test:

- "I'll get to this later" + label → if the work is actually blocking something, this is sprint-scope mislabeled. Re-classify.
- "This isn't urgent enough to interrupt my sprint work" + label → check criterion 3. If trivial → do it now (15 min). If non-trivial → criterion 1 check: is it actually important? Or just nice-to-have?
- Bulk-labeling a batch of issues `housekeeping` to clear the sprint board → red flag. Each housekeeping classification should pass the three-criteria test individually.

When qbp-architecture's audit finds mis-labeled housekeeping (anything that fails the three-criteria test), the issue is re-classified with a brief comment naming the failure mode. Pattern-of-mislabeling by a single implementor is surfaced to beekeeper.

### 6a.4 Pre-sprint housekeeping gate

Per the standing rule `feedback_housekeeping_before_sprint`: **a new sprint cannot open while housekeeping work is outstanding.** qbp-architecture conducts a housekeeping audit as the final close-out step (after all sprint-scope PRs are merged, before the kickoff doc for the next sprint is drafted). The audit produces:

- **Briefing:** what the sprint accomplished (closed issues, merged PRs, cross-doc artifacts shipped)
- **Housekeeping backlog:** what `housekeeping`-labeled work remains, classified by effort + repo, with a recommended schedule for clearing it before the next sprint kicks off

The next-sprint kickoff is gated on the housekeeping backlog being **either cleared or explicitly deferred by beekeeper** with named reasoning.

### 6a.5 Operational checklist for the label

When considering whether to apply `housekeeping`:

```
1. Will deferring this cost the federation something measurable?         [important]
2. Is sprint-scope work unblocked by deferring this?                     [non-blocking]
3. Does this take ≥ 15 minutes of focused work?                          [not trivial]
4. (Audit guard) Would qbp-architecture's audit confirm 1+2+3?           [honest classification]
```

All four → apply. Any failure → re-classify or do-it-now or won't-fix.

---

## 7. Anti-patterns

Issues that exhibit these patterns are failures of authoring discipline; close-with-redirect is the right response, not "let's just live with it."

| Anti-pattern | Why it fails | Redirect |
|---|---|---|
| **Open-ended discussion thread** | No decision, no scope, no close criterion. Belongs in chat or bridge channel. | Reframe as design-surface or close. |
| **"Investigate X"** | Investigation is naked-level work (Loop 1); not yet workshop. | Demote to TODO / scratch note; refile when there's a question or candidate decision. |
| **Reader-list with no per-reviewer justification** | "Two pairs of eyes" without naming what each reviewer checks → diffuse responsibility → silent non-review. | Add justifications, or shrink the reader-list. |
| **Closes-when = "looks good"** | Subjective; cannot be verified after-the-fact. | Replace with testable criteria. |
| **Shape mixing** (e.g., design-surface body with ratification reader-list) | Reviewers don't know whether to decide or to validate. | Split into two issues. |
| **No artifact path on ratification** | Reviewers can't find what to review. | Add path; if no path, the issue is design-surface not ratification. |
| **Wishlist closes-when** | Issue stays open forever waiting for items that aren't load-bearing. | Move wishlist to sub-issues filed alongside close. |
| **Bare `#<N>` for cross-repo** | Ambiguous in federation context. | Use `repo-<name>-issue-#<N>`. |

---

## 8. The naked → workshop transition (Systema mapping)

Per Systema v0.8 three-loop progressive hardening:

| Systema loop | Constraint hardness | Where work lives |
|---|---|---|
| **Loop 1: Ideation** | Reference (awareness, no formal test) | Chat, bridge channel, scratch doc, exploratory notebook |
| **Loop 2: Architectural** | Guidance (directional, soft test) | **GitHub issue (this doc)** — design-surface or early ratification |
| **Loop 3: Real-World** | Requirement (mandatory, hard test) | GitHub PR + merged artifact + closes-when satisfied + downstream coupling verified |

Filing a GitHub issue is the act of declaring "this has crossed from awareness into workshop." Once filed, the artifact is held to workshop-level discipline. Once merged + closed, it crosses to Loop 3 (Requirement).

**The transition is one-way absent explicit retrograde authorization.** A workshop-level issue does not get "downgraded back to naked" — it gets closed (with or without resolution) and any surviving uncertainty refiled as a fresh issue with workshop-level scope.

This is the mechanism that prevents naked-level musings from contaminating workshop-level commitments. Don't file an issue you wouldn't sign your name to in front of the §I4 reader-list.

---

## 9. Per-tenant CONTRIBUTING.md overlay

Each federation tenant repo (`bma-systema`, `wyrd`, `qbp`, `qbp-compute-unit`, `Contextus`, future tenants) hosts a `CONTRIBUTING.md` at the repo root that:

1. **References this doc** as the federation-wide canonical standard
2. **Adds tenant-specific overlay** for:
   - Default reader-list members (the implementors who default-review for that tenant's repo)
   - Tenant-specific issue labels (e.g., `bma:layer-0-cognitive`, `bma:layer-4-physical`, `qbp:cu-substrate`)
   - Tenant-specific closes-when extensions (e.g., "for QBP substrate-Lean PRs, additional criterion: Compute Manifest mode (b) extraction-and-execute log attached")
   - Tenant-specific shape preferences (e.g., "Wyrd never uses bug-or-incident — substrate failures are PIVOT-class incidents handled in `repo-wyrd:doc/pivots/`")

The CONTRIBUTING.md is the local extension; this doc is the federation-wide canonical. Where they conflict, this doc wins unless the tenant CONTRIBUTING.md explicitly documents a tenant-scoped exception with rationale.

---

## 10. Operational quick reference

When opening a new issue, the author asks:

1. **Is this Loop 2 work yet?** If no — close the editor, write in a scratch doc instead.
2. **Which of the four shapes is this?** If "I don't know" — the issue is not yet well-posed.
3. **Who is in the §I4 reader-list and what does each verify?** If "TBD" — file it as a design-surface to determine the reader-list first.
4. **What is the closes-when?** If "we'll know it when we see it" — refine until you can name testable criteria.
5. **What is the sequencing relative to other open issues?** If unknown — add the dependency graph before publishing.

If all five answer cleanly, file. If any answer with hand-waving, refine before filing.

---

*Issue Authoring — Best Practices v0.1*
*Author: qbp-architecture (Claude Opus 4.7) + James Paget Butler (Beekeeper)*
*Date: 2026-05-15*
