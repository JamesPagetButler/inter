---
name: closes-when-verification-test
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: authors and §I4 reviewers of design-surface ratification issues
applies-to: closes-when criterion 4 (the verification test) on ratification issues whose artifact commits the federation to not-yet-implemented behavior
provenance: issue-authoring-best-practices.md §2.2.2 (a–f) — effective 2026-05-15 per beekeeper Sprint 1 close-out finding (`repo-inter-issue-#4`)
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: The verification-test criterion (closes-when #4)

> Design-on-design cycles accumulate verification debt silently when criterion 4 is left
> soft ("first post-update implementation PR demonstrates the discipline") — the
> demonstration PR sits behind another design surface, the claim space grows, the
> verification space doesn't.

## When it is required
Every **design-surface ratification issue** — an issue whose artifact is a theory addendum, spec addendum, ADR, or design doc that commits the federation to behavior NOT yet implemented in running code — MUST populate closes-when criterion 4 with **three specific fields**: the test, its landing target, and the failure mode it detects.

## Field 1 — the verification test itself
A named test that proves the artifact's claim works. Not "first implementation PR demonstrates the discipline." Not "tests pass." A specific, namable test with three properties:
1. **Names what it verifies** in test-function-name form (e.g., `TestComputeManifest_RoundTrip_RejectsMalformedYAML`, `TestPentagonPodHotSwap_StateFlushPreservesCognitiveTrace`, `TestTranslationFunctor_MagnitudePreservationUnderFuzz`)
2. **Is executable in CI** — `go test`, `python -m pytest`, `lake build`, or equivalent; a reviewer can re-run the test from the closes-when description alone
3. **Has a failure condition** — if the test passes when the artifact is broken, the test is fake; criterion 4 has not been met

Example shapes:

| Artifact class | Verification-test shape |
|---|---|
| Theory addendum (algebraic invariant claim) | Lean theorem statement + mode (a) type-instantiation + (if runtime-claim) mode (b) extraction-and-execute per Spec 9.2 §3 |
| Spec addendum (operational protocol) | Integration test exercising the protocol end-to-end against the substrate it governs |
| ADR / design doc (substrate API) | Round-trip test: load fixture → validate → snapshot → query each named field; assert validation rejects each named malformed case |
| Federation governance rule | Process-rule test: the rule's enforcement mechanism (CI check, label, gate) runs against a malformed input and rejects it |

## Field 2 — the PR or sprint where the test lands
A named landing target:
- A specific PR (e.g., "lands as Phase 2 of `repo-bma-systema-pr-#172`")
- A specific sprint (e.g., "Sprint 2 — Federation Integration; sub-issue to be filed at sprint kickoff")
- A specific milestone (e.g., "Walk-α entry gate — closes when M1 cosim Tier B runs nightly")

Vague landing ("eventually"; "TBD"; "first implementation PR demonstrates the discipline") is **not acceptable**. Reviewers refuse §I4 ack on the ratification issue until the landing target is concrete.

## Field 3 — the failure mode the test detects
A one-sentence statement of what the test catches if the artifact's claim is wrong. Example: *"This test catches an OnSeam dispatcher that does NOT enqueue deferred work when callback exceeds budget — the failure mode where the Pentagon Pod Subconscious-concurrent invariant silently breaks under heavy callback load."*

This forces the author to articulate the falsification condition. A test that passes when nothing's wrong AND passes when something IS wrong is fake; the failure-mode statement makes that visible at review time.

## Exception — non-design-surface ratifications
Doc-only artifacts that DO NOT commit the federation to behavior (e.g., best-practice docs; meeting records; status reports; the §2.2.2 amendment itself) are exempt from criterion 4. The closes-when can mark criterion 4 as `N/A — non-design-surface ratification` with a brief reason.

If a reviewer disagrees with the N/A claim — i.e., asserts the artifact DOES commit the federation to behavior — they request changes with the §I4 ack-withholding mechanism, naming the claim that requires verification. The issue author either adds the verification-test specification OR withdraws the claim from the artifact.

## Why this is structural, not procedural
Criterion 4 with this discipline operationalizes the federation's antifragility principle: tests must catch failure modes that exist, not merely run-and-pass. A design surface that closes without naming its verification test is the federation analog of mocking the database in tests — the design works on paper but never against the substrate it claims to control.

The verification-test inventory at `repo-inter-issue-#4` (Sprint 1 verification-debt audit) is the canonical example of what this discipline prevents going forward: federation-wide claim accumulation without matching verification surface.

## Working precedent
The three-field shape is not new discipline: it documents and federates a pattern already operational in BMA's tunable-parameter registry (`repo-bma-systema-issue-#90`), which records a predicted outcome and a quantitative predicted delta per change, populates actual outcome/delta post-hoc, classifies prediction accuracy, and feeds accumulated per-source accuracy into a trust-class ledger (the AHE-style approach from Lin et al., arXiv:2604.25850). Federation-wide adoption normalizes the criterion-4 fields at the issue-authoring layer; the BMA registry is the runtime instantiation that consumes them. *(Private-repo file/line detail is in the source doc §2.2.2.f, not copied here — inter is public.)*

## Wisdom anchors
`w-test-can-fail` · `w-define-done-testably` · `w-proven-not-wired` · `w-antifragile` — see `inter/wisdoms/_federation.md`. Related skill: `inter/skills/verification.md`.
