---
title: "Report a bug"
description: Print a single GitHub Issues URL with the environment block already URL-encoded into `&body=`, so bug reports open with the version stamp prefilled — no manual paste step.
tags:
  - meta
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Bug Report

Help the user file a bug report that arrives at triage with the environment
stamp already in the issue body — by constructing a GitHub `issues/new` URL
that uses both `?template=bug_report.md` (template selection) and `&body=…`
(URL-encoded prefilled body). The user clicks the link, the form opens
prefilled, they add the reproduction steps, and click Submit.

The command does **not** submit the issue. It prints the URL.

## Instructions

1. **Gather the environment values** — read the same identity files as
   `/aidoc-flow:about`:
   - `${CLAUDE_PLUGIN_ROOT}/VERSION`
   - `${CLAUDE_PLUGIN_ROOT}/FRAMEWORK_SPEC_VERSION`

   And shell out (read-only) for:
   - `uname -srm` — OS / kernel / arch
   - `claude --version` — if available; if not, use `(unknown)`

2. **Assemble the environment block** — exactly four lines (LF-separated),
   with the values you just gathered:

   ```text
   ## Environment

   - Plugin version: <VERSION>
   - Framework spec: <FRAMEWORK_SPEC_VERSION>
   - OS / arch: <uname -srm>
   - Claude Code version: <claude --version, or (unknown)>
   ```

3. **URL-encode the environment block** following RFC 3986 / HTML form
   conventions (the encoding GitHub's `?body=` parameter accepts):

   | Character | Encoded as |
   |---|---|
   | newline (LF) | `%0A` |
   | space | `%20` |
   | `#` | `%23` |
   | `-` (hyphen) | `-` (no change) |
   | `.` | `.` (no change) |
   | `/` | `%2F` |
   | `:` | `%3A` |
   | `(` `)` | `%28` `%29` |
   | all other ASCII letters/digits | unchanged |

   The block from step 2, URL-encoded, becomes the value of the `body`
   query parameter.

4. **Construct the URL** by joining three parts with `?` and `&`:

   ```text
   https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=bug_report.md&body=<URL-encoded block from step 3>
   ```

   Do not add spaces or line breaks inside the URL — it must be one
   continuous string.

5. **Print exactly this output** (no extra commentary):

   ```text
   File a bug — click this link and the environment stamp will be prefilled:

       <the URL from step 4>

   Then add reproduction steps and what you expected vs what happened.
   The form opens on github.com; review before clicking Submit.
   ```

6. **Stop**. Do not open a browser, do not call any GitHub API. The user
   clicks the link themselves.

## Error handling

- If any environment value cannot be read, substitute `(unknown)` in that
  field — do not skip the line.
- If `uname` or `claude` is unavailable, the command still succeeds with
  `(unknown)` placeholders.
- If the encoded URL would exceed 6000 characters (a soft GitHub limit
  some browsers enforce), fall back to the legacy paste flow: print the
  bare template URL `https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=bug_report.md`,
  print the environment block as text, and instruct the user to paste it.
  In practice the four-line block is well under the limit; this fallback
  exists as a safety net.

## Why URL-prefill (not paste, not API submit)

- **Not API submit:** the plugin has no GitHub token; auto-submitting a
  permanent public issue without explicit user review is wrong UX.
- **Not gh CLI shell-out:** requires `gh` installed + authenticated on
  the user's machine, which most users don't have.
- **Not paste-and-fill:** the previous design (paste this block) added one
  manual step. The `&body=` query parameter is GitHub's documented prefill
  mechanism — same destination, no paste.

The user still clicks Submit on github.com — the plugin never auto-creates
issues.
