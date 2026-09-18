# Tool-vetting security — research grounding for @thompson

Grounding for the federation security agent (`inter/prompt/thompson-security-agent-launch-prompt.md`). Deep-research pass 2026-09-04. Threat-model summary + concrete lessons + sources; the launch-prompt distils this into the six-dimension methodology + verdict rubric.

## Threat models the methodology is built against (named, real)

- **xz-utils backdoor (CVE-2024-3094)** — a 2–3yr social-engineering campaign hid a backdoor in **build artifacts / binary test fixtures** reassembled only at build time — invisible to source review of the `.c` files. → **Diff the published tarball against the source repo**, not just read the source.
- **Shai-Hulud / "Mini Shai-Hulud" (2025–2026)** — self-replicating npm worm using **postinstall scripts** to harvest GitHub/AWS/GCP tokens and auto-republish. → `--ignore-scripts` by default; install-time network/exec = auto-escalate to REJECT.
- **axios / atool account-takeover (2026)** — maintainer credential compromise → poisoned new version of an *already-trusted* package. → a trusted maintainer today doesn't bound future releases; pin versions; watch publish-velocity spikes.
- **MCP tool-poisoning / rug-pulls / line-jumping** — malicious instructions in a tool *description* (invisible in UI, visible to the model); schema swapped after approval; Unicode zero-width/tag-block concealment. → read every manifest/description fully; pin+hash schemas; higher scrutiny than a normal dep.
- **dependency confusion / typosquatting / protestware** (node-ipc peacenotwar, colors/faker sabotage) → scoped packages + private-registry precedence; char-by-char name check; version pinning.

## Framework anchors
- **SLSA v1.2** build/provenance levels (L0 none → L3 unforgeable) — verify via `npm audit signatures` (Sigstore/Rekor), cosign, GitHub Artifact Attestations.
- **OWASP Top 10:2025 A03 "Software Supply Chain Failures"** (expanded from A06:2021) — a clean `npm audit` is necessary-not-sufficient; the failure moved upstream of known-CVE scanning.
- **OpenSSF Scorecard** — process-hygiene floor; explicitly does NOT assess maintainer human-trust.
- **Sandbox tiers:** bubblewrap (`--unshare-all`) / firejail / `unshare --net` / seccomp-bpf / Podman-rootless / gVisor-Firecracker — pick the *lightest tier that proves the claim*.

## Consolidated sources
- SLSA levels — https://slsa.dev/spec/v1.0/levels · Wiz — https://www.wiz.io/academy/application-security/slsa-framework
- OWASP Top 10:2025 — https://owasp.org/Top10/2025/ · changes — https://patrowl.io/en/blog/owasp-top-10-2025-what-s-changed-and-the-2026-data
- npm threat landscape — https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/
- Shai-Hulud CISA — https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem · Shai-Hulud 2.0 (Microsoft) — https://www.microsoft.com/en-us/security/blog/2025/12/09/shai-hulud-2-0-guidance-for-detecting-investigating-and-defending-against-the-supply-chain-attack/
- node-ipc protestware (Snyk) — https://snyk.io/blog/peacenotwar-malicious-npm-node-ipc-package-vulnerability/
- xz-utils backdoor — https://en.wikipedia.org/wiki/XZ_Utils_backdoor · https://www.crowdstrike.com/en-us/blog/cve-2024-3094-xz-upstream-supply-chain-attack/
- OWASP NPM Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/NPM_Security_Cheat_Sheet.html · ignore-scripts — https://www.nodejs-security.com/blog/npm-ignore-scripts-best-practices-as-security-mitigation-for-malicious-packages
- GuardDog (PyPI) — https://securitylabs.datadoghq.com/articles/guarddog-identify-malicious-pypi-packages/ · PyPI best practices — https://github.com/lirantal/pypi-security-best-practices
- npm provenance — https://github.com/npm/provenance · Sigstore npm GA — https://blog.sigstore.dev/npm-provenance-ga/ · cosign — https://blog.sigstore.dev/cosign-verify-bundles/
- OWASP MCP Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html · Tool Poisoning — https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks · rug pulls/line jumping — https://lenshq.io/blog/mcp-security-tool-poisoning-threat-model/ · MCP security 2026 (Microsoft) — https://techcommunity.microsoft.com/blog/microsoft-security-blog/the-state-of-mcp-security-in-2026/4531327
- Claude extension ecosystem — https://pluto.security/blog/claude-extension-ecosystem-security-practitioner-guide/ · Snyk/Vercel skill ecosystem — https://snyk.io/blog/snyk-vercel-securing-agent-skill-ecosystem/ · Repello skill audit — https://repello.ai/blog/claude-code-skill-security · Claude Code security — https://code.claude.com/docs/en/security-guidance
- Unicode tag-block concealment — https://arxiv.org/pdf/2607.05744
- tcpdump in netns — https://oneuptime.com/blog/post/2026-03-20-monitor-traffic-namespace-tcpdump/view · capturing process traffic — https://www.baeldung.com/linux/capture-process-network-traffic
- bubblewrap vs firejail vs nsjail — https://www.bigiron.cc/guides/bubblewrap-vs-firejail-vs-nsjail-application-sandboxing · bubblewrap — https://github.com/containers/bubblewrap
- obfuscation (JFrog) — https://jfrog.com/blog/detecting-known-and-unknown-malicious-packages-and-how-they-obfuscate-their-malicious-code/ · Socket obfuscation 101 — https://socket.dev/blog/obfuscation-101-the-tricks-behind-malicious-code · Cycode — https://cycode.com/blog/malicious-code-hidden-in-npm-packages/
- FOSSA license compatibility — https://fossa.com/resources/devops-tools/license-compatibility-checker/
- OpenSSF Scorecard — https://github.com/ossf/scorecard · https://scorecard.dev/ · Scorecard maintainer-trust limitation — https://www.systemshardening.com/articles/cross-cutting/oss-project-ai-trust-framework/
