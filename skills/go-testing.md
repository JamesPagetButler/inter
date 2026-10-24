---
name: go-testing
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every seat writing or reviewing Go tests
applies-to: Go test tooling choice (stdlib `testing`, `testify`, testo), race detection, test synchronization
provenance: code-review-best-practices.md §7.2 (testo); go-coding-guide.md (Stack "Testing", Commands "Test", Boundaries "time.Sleep in tests", Verification step 4)
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Go testing

## Default stack
- Testing: stdlib `testing`; `testify` only when assertion ergonomics genuinely matter.
- Always run with the race detector: `go test -race ./...` (must pass before reporting a Go change as done — `skills/go-coding.md` § verification).
- Coverage for review sign-off: `go test -cover` (`skills/code-review.md` § supporting tools).
- Bench: `go test -bench=. -benchmem -run='^$' ./pkg/...`
- **Never** use `time.Sleep` in tests for synchronization (use channels, `sync.WaitGroup`, or `eventually`-style polling).

## testo (Ozon Tech testing framework)
https://github.com/ozontech/testo — suite-based Go testing framework on top of `testing.T`.

**Adopt selectively** for:
- BMA 30-day continuous-operation suites (lifecycle hooks BeforeAll/AfterAll/BeforeEach/AfterEach)
- Wyrd bridge-promotion + holographic-hypergraph integration tests (parametrized over algebra hierarchy ℝ/ℂ/ℍ/𝕆/𝕊)
- CTH ρ_net + ChainFidelity computation suites with shared fixtures
- Federation cross-repo E2E (where Allure Report integration adds visibility)

**Do NOT adopt** for:
- Simple unit tests — standard `testing` is leaner; testo adds abstraction overhead
- Projects on Go < 1.24 (testo's minimum requirement)
- Cases where the reviewer can't easily debug the suite if it fails

Review implication: when reviewing tests that use testo, verify the suite uses lifecycle hooks for real shared state (BeforeAll/AfterAll), not as a vibe.

## Wisdom anchors
`w-test-can-fail` · `w-tests-ship-with-code` · `w-determinism` (no sleep-based synchronization) — see `inter/wisdoms/_federation.md`.
