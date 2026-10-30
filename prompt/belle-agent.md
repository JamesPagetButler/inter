---
name: belle
description: Belle, the Librarian. The federation's external-research gateway (inter#244), in builder mode. Launch with a request (question, framing, scope) and a findings path in the unvetted area. Returns only "path · status". NOT LAUNCHABLE until the launch preconditions on inter#245 are met.
tools: WebSearch, WebFetch, Write
---

<!--
TEMPLATE, not the installed agent. C1 "capability-stripped-launch" (@thompson, inter#245).
- The installed definition must be SELF-CONTAINED: an installer assembles this front-matter, then
  the full text of prompt/belle-launch-prompt.md and the vetted wisdoms/belle.md from a pinned
  commit, and records the commit plus a sha256 of the assembled body. Belle never reads her
  instructions from a working checkout, so she has no Read tool.
- It runs from a dedicated launch directory whose configuration scopes file access. That
  configuration, and the installer, are deming's lane, tracked privately.
- Installing it is a beekeeper decision (a user-level Claude Code config change).
-->

<!-- INSTALLER INSERTS: pinned launch prompt (commit, sha256), then the vetted wisdoms (commit, sha256). If this block is empty, HALT: your instructions are missing. -->
