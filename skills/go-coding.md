---
name: go-coding
scope: federation
type: skill
maintained-by: qbp-architecture
primary-user: every seat writing Go (bma-implementor, wyrd-implementor, cth-implementor, qbp-cu-implementor, qbp-implementor, edda-implementor, …)
applies-to: Go code in any federation repo
provenance: ~/Documents/go-coding-guide.md (outside the repo; whole doc). Workspace-specific notes routed persona-local — see ledger.
refined: 2026-10-22 (inter#61 transcription)
---

# Skill: Go coding

Reference for any Go work in this workspace. Load at session start or `@`-import from a project CLAUDE.md. Testing specifics: `skills/go-testing.md`. CI minimum: `skills/ci-workflows.md`.

## Stack & versions
- Go 1.23+ (use `go.mod` `go` directive to pin)
- Module path uses full repo URL; `GOPRIVATE` set for any private orgs (`GOPRIVATE=github.com/JamesPagetButler/*` — private modules need this set in shell or `~/.netrc` for module fetch)
- Tooling: `gofmt`, `go vet`, `staticcheck`, `golangci-lint`, `goimports`
- Testing: stdlib `testing`; `testify` only when assertion ergonomics genuinely matter
- Concurrency primitives: stdlib `sync`, `context`, `golang.org/x/sync/errgroup`

## Commands
- Build: `go build ./...`
- Test (always with race detector): `go test -race ./...`
- Vet: `go vet ./...`
- Lint: `golangci-lint run`
- Format check: `gofmt -l . | tee /dev/stderr | wc -l` returns `0`
- Tidy: `go mod tidy`
- Bench: `go test -bench=. -benchmem -run='^$' ./pkg/...`

## Code style (rules gofmt and linters can't enforce)
- `context.Context` is the first parameter of any function that does I/O, blocking, or cancellable work. Name it `ctx`.
- Accept interfaces, return concrete types. Define interfaces at the consumer, not the producer.
- Errors: wrap with `fmt.Errorf("doing X: %w", err)`. Use `errors.Is` / `errors.As` to inspect. Never compare error strings.
- Sentinel errors are package-level `var Err... = errors.New(...)`.
- One return path. Prefer guard clauses + early return over nested `if/else`. *(See ledger CONFLICT C9 — the two halves of this line pull in opposite directions; the early-return half is the operative rule.)*
- No naked returns in functions longer than ~10 lines.
- Receivers: pointer receivers when the method mutates or the struct is large; otherwise value receivers. Be consistent across all methods of a type.
- Package names: short, lowercase, no underscores, no plurals. `user` not `users`, `usermgr`, or `UserManager`.
- Exported identifiers get a doc comment that starts with the identifier name.

## Conventions
- Errors over panics in library code. `panic` only for programmer-error invariants that should crash the process.
- `defer` for cleanup immediately after acquisition (`f, err := os.Open(...); if err != nil { ... }; defer f.Close()`).
- Channels carry ownership: the goroutine that writes to a channel closes it. Receivers never close.
- Slice/map zero values are useful — prefer them to constructors when no invariant needs enforcing.
- Struct literal init: use named fields. Positional only for ≤2 fields with obvious meaning (e.g., `image.Point{1, 2}`).
- Time: `time.Time` for instants, `time.Duration` for spans. Never `int` seconds in APIs.
- Logging: structured (`slog`). One log per error, at the top of the call stack. Don't log-and-return.

## Concurrency
- Every goroutine has a documented termination condition. No fire-and-forget without a `context` or explicit shutdown channel.
- Use `errgroup.WithContext` for parallel work that should cancel on first error.
- Shared state: `sync.Mutex` for simple cases, channels for ownership transfer. Don't mix paradigms in one struct.
- `sync.Once` for lazy init. Never use `sync.Mutex` zero-copied.
- Pass `context.Context` explicitly. Never store it in a struct field except for long-lived background services where it's the lifetime root.

## Boundaries

**Always do**
- Run `go test -race ./...` before reporting a Go change as done
- Run `go vet ./...` and `golangci-lint run` before commit
- Wrap errors with context when crossing layer boundaries
- Cancel goroutines via `context` before the parent returns

**Ask first**
- Adding a new direct dependency (run `go mod why` after to confirm)
- Introducing CGO, `unsafe`, or assembly
- Changing a public API signature in any package consumed elsewhere
- Adding a new top-level package or `internal/` boundary

**Never do**
- Ignore errors with `_ =` outside of `defer x.Close()` patterns
- Use `panic` for control flow
- Start a goroutine without a termination plan
- Use `time.Sleep` in tests for synchronization (use channels, `sync.WaitGroup`, or `eventually`-style polling)
- Commit `replace` directives pointing at local paths
- Add `//nolint` without a comment explaining why

## Verification
After any non-trivial change, observe all of the following pass:
1. `gofmt -l .` empty
2. `go vet ./...` clean
3. `golangci-lint run` clean
4. `go test -race ./...` passes
5. `go mod tidy` produces no diff

## References
- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)
- `staticcheck` checks: https://staticcheck.dev/docs/checks/

## Wisdom anchors
`w-widening-trust-ask-first` · `w-no-silent-suppression` · `w-verify-before-summarize` · `w-determinism` — see `inter/wisdoms/_federation.md`.
