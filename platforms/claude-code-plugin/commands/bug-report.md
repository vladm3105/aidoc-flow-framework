---
title: "Report a bug"
description: Print a prefilled GitHub Issues URL and an environment block to paste, so bug reports arrive with the version stamp already in them.
tags:
  - meta
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Bug Report

Help the user file a bug report that already carries the information triage
needs (plugin version, framework spec version, OS, Claude Code version). The
command does **not** submit the issue; it prints what the user pastes into
GitHub.

## Instructions

1. **Gather the environment block** — read the same identity files as
   `/aidoc-flow:about`:
   - `${CLAUDE_PLUGIN_ROOT}/VERSION`
   - `${CLAUDE_PLUGIN_ROOT}/FRAMEWORK_SPEC_VERSION`

   And shell out (read-only) for:
   - `uname -srm` — OS / kernel / arch
   - `claude --version` — if available; if not, write `(unknown)`

2. **Print the bug-report block** — exactly this layout, with the values
   filled in:

   ```text
   File a bug here:

       https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=bug_report.md

   Paste this block into the issue body so triage has the version stamp:

       Plugin version:       <VERSION>
       Framework spec:       <FRAMEWORK_SPEC_VERSION>
       OS / arch:            <uname -srm>
       Claude Code version:  <claude --version, or (unknown)>
   ```

3. **Add a one-line nudge**:

   ```text
   Include reproduction steps and what you expected vs what happened.
   ```

4. **Stop**. Do not open a browser, do not call any GitHub API. The user
   copies the block into the form themselves.

## Error handling

- If any environment value cannot be read, substitute `(unknown)` in that
  field — do not skip the line.
- If the user is on a system where `uname` or `claude` is unavailable, the
  command still succeeds with `(unknown)` placeholders.
