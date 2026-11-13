---
name: working-under-the-warp
scope: federation
type: guide
maintained-by: deming (content) · qbp-architecture (inter lane, public-safety review)
primary-user: every seat
applies-to: how in-sprint work moves from "I opened a PR" to "it merged", inside one warp and across warps
provenance: Nidavellir#120 (warp L9), Nidavellir#50 (the warp epic), inter#242 (design), inter#194 (the Sprint 4 weave)
status: released to inter 2026-11-13 (warp L9)
---

# Working under the warp

The **warp** is the set of guarantees that turns the federation's process rules into things that are checked, not just promised. Who wrote a change, who reviewed it, and who merged it are proved by signatures, and a CI check decides when a PR is ready.

This guide is for every seat. It covers:
- **A.** Working on your own warp: a thread inside one repo.
- **B.** Working on a weft crossing: a thread that cuts across several repos.
- **C.** The update loop: how this guide and the tool docs stay current.

Operator detail (key handling, the sandbox, running the tests locally) lives in the private operator runbooks, not here.

## What's live today, and what switches on later

The machinery is built and tested end to end (warp L1–L8). Some parts wait on beekeeper decisions before they're enforced. **Check this table before relying on a step.**

| Piece | Today | When switched on |
|---|---|---|
| Review and merge rules (author ≠ reviewer ≠ merger, named reviewers, the merge gate) | Followed by seats; checked by the merger and notary | Also **enforced by signature**: a review counts only if its signature checks out against the seat's registered key |
| Signed verdicts (`seat-gate sign`) | Available; seats have **no production keys yet** | Each seat signs its own APPROVE / CHANGES_REQUESTED / CARRY / DEFER / AUTHORED |
| `seat-gate` merge check on PRs | Runs on every PR in **report mode** (informational; it can show red without blocking) | A **required** check: a PR can't merge until it's green |
| Review routing (`seat-gate review-request`) | Works; the routing table is marked *unconfirmed* | The routing table and each repo's reviewer/merger split are confirmed |
| Edda contract check | Runs in report mode; checks the contract's header only, for now | Blocking once the Edda compiler checks lock blocks |

The beekeeper decides each switch: key custody and rotation; who may edit the key registry and the routing table; making the check required in each repo; confirming the routing table. Until a row flips, follow the "Today" column.

## A. Working on your own warp

A **thread inside one warp** is ordinary work in the repo your seat owns. The path from change to merge:

1. **Open the PR** in your own repo. Link the issue it closes. The issue's acceptance criteria are what the merge check reads.
2. **Name your reviewer(s).** Use `seat-gate review-request` to route the review to the right seat for the kind of change. It picks from the routing table and never picks the author. It wakes the reviewer by writing a `WAKE:REVIEW` line straight into that seat's wake file, not through a bus mention, so the reviewer's waiter fires even if nobody @-mentions them. A request that can only go to the author, or only to the beekeeper, fails closed rather than routing badly.
3. **The reviewer reviews the head commit.** A review is about one exact commit. If you push again, earlier approvals no longer count. The reviewer either re-approves, or signs a **CARRY**: "my approval of the old commit still holds at the new one". Only the reviewer who gave the approval can carry it.
4. **The merge check decides readiness.** `seat-gate` is green only when:
   - every acceptance criterion's CI job is green at the head commit;
   - every named reviewer has an approval bound to that head (directly, or through a CARRY chain);
   - no CHANGES_REQUESTED stands at the head;
   - the author, each reviewer and the merger are different seats, proved by key once signing is on.
5. **Your lane's merger merges.** Never your own PR. Lanes are in the federation's merge-lane rules.

**Fix rounds stay on the same PR.** When a reviewer raises something, fix it in a new commit on the same PR and ask for a diff-only re-review. Don't promise it in a follow-up.

**What never counts as a review:** a verbal "looks fine", an approval of an older commit without a CARRY, or a review signed by the author or the merger.

## B. Working on a weft crossing

A **weft crossing** is a thread that crosses warps, e.g. a feature that needs a change in a library repo and a matching change in the repo that uses it. The Sprint 4 weave lists the crossings (see its "Weft crossings" section).

### The rules
- **Authority doesn't cross.** You push code only to your own repo, unless you hold a beekeeper-granted interim write grant on that repo. For another warp's part, open an issue there, or hand the work to its owner seat. Otherwise, never write in another seat's repo.
- **One PR per repo, each gated in its own warp.** Each repo's PR passes that repo's own merge check, with that repo's owner seat as a named reviewer and that repo's lane merger merging it. **The thread's owner is also a named reviewer on every PR in the crossing**, so one seat sees the whole shape.
- **The crossing's lock lives on the thread's meta issue** (on inter). Its legs point at each repo's PR or issue. The thread is done when every leg is green, not when one repo's part merges.
- **Merge order: dependencies first.** Merge the repo that is depended on first. Then the consumer **pins to the merged commit** (not to the PR branch), and the consumer's PR is re-checked at that pin before anyone calls it ready.
- **Mention roles still apply across warps.** Put the seat that owns the next step in `to`. Ask other warps for input with an @-name in the body. Use `cc` for awareness only, and never hide an ask in a cc.
- **Cross-reference every PR.** Each PR body lists the others in the crossing, with repo-qualified links (`repo#N`).

### Worked example: a launcher fix that a test depended on (2026-11-13)
A real two-repo crossing from building warp L8:

1. **Found:** Nidavellir's end-to-end test (Nidavellir#122) showed that inter's launcher defaulted to a layout the dead-seat detector can't see.
2. **Authority didn't cross:** the launcher is inter's, in qbp-architecture's lane. deming (Nidavellir's owner) didn't edit it. deming reported it on the bus with the evidence and a proposal, with qbp-architecture in `to`.
3. **The owner fixed it in their own warp:** qbp-architecture opened inter#292, with a test and two mutants. deming, as the finder and the owner of the affected detector, was the named reviewer and approved it at its head commit. herschel, inter's lane merger, merged it.
4. **Dependency first, then pin to the merge:** with inter#292 merged, Nidavellir#122 bumped its pinned inter version to that **merge commit**, removed its own workaround so the test exercises the new default, and added a mutant proving the old layout now fails.
5. **Each PR went through its own warp's gate:** inter#292 through inter's review and merger, and Nidavellir#122 through Nidavellir's (architect review approved, notary verified at its own head). Nidavellir#122's merge was still pending when this was written.

## C. Keeping these docs current (the update loop)

The tools will change as the federation uses them. The docs keep up this way:
1. **Hit a problem? Write one line.** When a tool misfits, fails, needs a workaround or surprises you, add one line to that tool's feedback file. Each runbook's last section has the path and format. Failures matter most; routine successes need no line.
2. **Broken tool? File an issue** on the tool's repo, as well as the line.
3. **Tool change means doc change.** A PR that changes a warp tool's behaviour updates its runbook in the same PR. A CI check (`warp-docs`) enforces this. If the doc truly needs no change, the PR body says `docs-unchanged: <reason>`.
4. **At every sprint close**, deming triages the feedback (fixing text, adding dated tool wisdoms, or filing issues), and the refined docs are **released to inter**, including this guide.

## See also
- `skills/cross-repo-coordination.md`: cross-repo PR mechanics and review surfaces.
- `skills/pr-authoring.md`, `skills/issue-authoring.md`, `skills/repo-qualified-references.md`.
- The Sprint 4 weave (inter#194), and the warp design (inter#242).
