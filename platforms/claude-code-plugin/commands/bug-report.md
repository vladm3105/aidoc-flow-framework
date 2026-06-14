---
title: "Report a bug"
description: Draft a bug-report issue title + body from the user's prompt and the current conversation context, then print a GitHub Issues URL with both URL-encoded into `?title=&body=`. The user reviews on github.com and clicks Submit; the plugin does not auto-submit.
tags:
  - meta
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Bug Report

Turn a one-line user complaint into a well-structured GitHub bug-report issue
that is **prefilled with both title and body**, then hand the user a URL to
review and submit on github.com. The user types one sentence describing what
broke; the LLM does the writing work using the prompt **and** the current
conversation context (what command was running, what error appeared, what
files were involved).

## Invocation

```text
/aidoc-flow:bug-report <one-sentence description of what's broken>
```

Examples:

```text
/aidoc-flow:bug-report this feature generate error and does not work as expected
/aidoc-flow:bug-report /aidoc-flow:status crashes on projects without docs/
/aidoc-flow:bug-report doc-brd-autopilot timed out at the audit step
```

Running `/aidoc-flow:bug-report` with no text still works — the LLM uses
only the conversation context.

## Instructions

1. **Capture the user's argument** — every word after `/aidoc-flow:bug-report`
   is the user's report. Store it as `user_complaint`. If empty, set
   `user_complaint = "(none provided — using conversation context only)"`.

2. **Gather the environment stamp** — read:
   - `${CLAUDE_PLUGIN_ROOT}/VERSION` → `plugin_version`
   - `${CLAUDE_PLUGIN_ROOT}/FRAMEWORK_SPEC_VERSION` → `framework_spec`
   - `uname -srm` → `os_arch`
   - `claude --version` → `claude_version` (fall back to `(unknown)` if
     unavailable)

3. **Read the conversation context** — review the recent messages and tool
   calls in the current chat. Look for:
   - The most recent **error message**, traceback, or failure output (if any).
   - The most recent **command or skill the user was running** when the
     problem appeared (e.g. `/aidoc-flow:status`, `doc-brd-autopilot`,
     `gh pr create`).
   - **Files referenced** in the failure (paths from tool calls, error
     locations).
   - What the user appeared to **expect** vs what **happened**, if it can be
     inferred from the surrounding conversation.

   If the conversation is fresh and contains no failure context, do not
   fabricate one — leave `Steps to reproduce` and `Actual behaviour` as
   placeholders the user fills in.

4. **Draft the issue** — produce two strings, `title` and `body`. The body
   uses the same section structure as `.github/ISSUE_TEMPLATE/bug_report.md`
   so the result reads naturally on github.com.

   **Title rules:**
   - One line, ≤ 80 characters.
   - Concrete and specific. Start with the affected surface in backticks if
     identifiable (e.g. `/aidoc-flow:status crashes when docs/ tree is absent`).
   - Imperative or descriptive, never speculative ("crashes" not
     "I think crashes"; never "Maybe a bug in…").
   - Reuse the user's wording where it is specific; rephrase only when their
     text is vague.

   **Body template** — populate every section; for any section without
   evidence, write `_(please fill in)_` so the user notices the gap rather
   than seeing a confidently wrong claim:

   ```markdown
   ## Summary

   <One paragraph. State plainly what is broken and on which surface.
   Weave in `user_complaint` and the inferred surface.>

   ## Steps to reproduce

   <Numbered list, derived from the conversation context. If the steps cannot
   be reconstructed, write `_(please fill in — exact commands or actions
   that trigger the bug)_`.>

   ## Expected behaviour

   <What should have happened. If the user's complaint implies the
   expectation ("does not work as expected"), name the documented or
   intuitive correct behaviour. If unclear, write `_(please fill in)_`.>

   ## Actual behaviour

   <What happened. Quote the actual error message or output verbatim inside
   a fenced code block when one is available in the conversation. If no
   error is in context, write `_(please fill in — paste the error or
   unexpected output here)_`.>

   ## Environment

   - Plugin version: <plugin_version>
   - Framework spec: <framework_spec>
   - OS / arch: <os_arch>
   - Claude Code version: <claude_version>

   ## Additional context

   <Optional — anything else relevant: file paths from the conversation,
   what the user was trying to accomplish, related issues. Omit this
   section entirely if there is nothing genuinely useful to add.>
   ```

   Do **not** include log content, file contents, or paths that look like
   secrets (anything matching `(token|secret|key|password|api[_-]?key)`),
   even if they appear in the conversation. Replace such fragments with
   `(redacted)` in the body.

5. **URL-encode `title` and `body`** following RFC 3986 (LF → `%0A`,
   space → `%20`, `#` → `%23`, `:` → `%3A`, `/` → `%2F`, `(` `)` → `%28`
   `%29`, letters / digits / `.` / `-` unchanged).

6. **Construct the URL** by joining the parts with `?` and `&`:

   ```text
   https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=bug_report.md&title=<encoded title>&body=<encoded body>
   ```

   One continuous string; no spaces or line breaks inside the URL.

7. **Print the preview, then the URL**, in this exact layout:

   ```text
   Drafted issue (review before clicking):

     Title:
       <title>

     Body:
       <body, indented two spaces per line>

   Click to open the prefilled issue form:

       <URL from step 6>

   Review on github.com before clicking Submit. The form is prefilled but
   not submitted — only you click Submit. Edit the title or body directly
   on github.com if anything is wrong; the URL prefill is a starting point,
   not a final submission.
   ```

8. **Stop**. Do not open a browser, do not call any GitHub API. The user
   clicks the link themselves.

## Fallback path

If the encoded URL exceeds 6000 characters (a soft browser/GitHub limit some
browsers enforce), do this instead of step 7:

1. Print the title and body in chat as plain text the user can copy.
2. Print only the bare template URL:
   `https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=bug_report.md`
3. Tell the user to paste the title and body into the form on github.com.

In practice the body is short and the limit is rarely hit; this fallback is
a safety net.

## Honest framing

- The plugin **never** submits the issue. The user clicks Submit on
  github.com.
- The drafted title and body are an LLM **proposal**. The user is expected
  to review and edit them, on github.com if needed.
- The command does **not** include secrets it sees in the conversation. If
  the user wants to share logs that may contain secrets, they paste them
  manually on github.com after redacting.

## Error handling

- Empty user argument: still produce a draft using the conversation context;
  if context is also empty, populate the body with `_(please fill in)_`
  placeholders so the user notices.
- Any environment value unreadable: substitute `(unknown)`; do not skip the
  line.
- Conversation context has nothing relevant: the body is mostly
  `_(please fill in)_` placeholders alongside the env stamp. That is
  acceptable — the user finishes the writing on github.com.

## Why URL-prefill (not API submit, not gh CLI)

- **Not API submit:** the plugin has no GitHub token; auto-submitting a
  permanent public issue without explicit user review is wrong UX.
- **Not gh CLI shell-out:** requires `gh` installed + authenticated on the
  user's machine, which most users don't have, and submits as the user's
  account without an explicit confirmation step.
- **URL prefill (chosen):** works on every platform; user reviews on
  github.com before clicking Submit; no auth required; matches GitHub's
  documented `?title=&body=` prefill mechanism.
