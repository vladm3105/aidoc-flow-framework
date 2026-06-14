---
title: "Share feedback"
description: Draft a feedback issue title + body from the user's prompt and current conversation context, then print a GitHub Issues URL with both URL-encoded into `?title=&body=`. The user reviews on github.com and clicks Submit.
tags:
  - meta
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Feedback

Separate channel from `/aidoc-flow:bug-report`. Bugs are "something is broken";
feedback is "what would you change" or "what worked." Same machinery — the LLM
drafts a structured issue from the user's one-line prompt + conversation
context, the URL is prefilled, the user clicks Submit on github.com.

## Invocation

```text
/aidoc-flow:feedback <one-sentence summary of what worked / didn't / what to change>
```

Examples:

```text
/aidoc-flow:feedback the help output is too long on small terminals
/aidoc-flow:feedback love that /status shows last edit date, big help
/aidoc-flow:feedback could /budget min also skip the audit step
```

Running `/aidoc-flow:feedback` with no text still works — the LLM uses only
the conversation context.

## Instructions

1. **Capture the user's argument** — every word after `/aidoc-flow:feedback`
   is the user's report. Store it as `user_remark`. If empty, set
   `user_remark = "(none provided — using conversation context only)"`.

2. **Gather the version stamp** — read:
   - `${CLAUDE_PLUGIN_ROOT}/VERSION` → `plugin_version`
   - `${CLAUDE_PLUGIN_ROOT}/FRAMEWORK_SPEC_VERSION` → `framework_spec`

3. **Read the conversation context** — review the recent messages. Look for:
   - Which **command, skill, or layer** the user was working with when the
     remark applies (e.g. `/aidoc-flow:help`, `doc-brd-autopilot`,
     layer `BRD`).
   - Whether the remark is a **feature idea**, **praise**, **friction**, or
     a **question**. Pick exactly one for the issue's lead-in.
   - Any **concrete suggestion** the user implied (e.g. "could /budget min
     also skip the audit step" → suggestion: "extend `budget: min` profile
     to skip optional audit passes").

4. **Draft the issue.** Produce `title` and `body`. The body matches the
   structure in `.github/ISSUE_TEMPLATE/feedback.md`.

   **Title rules:**
   - One line, ≤ 80 characters.
   - Lead with the category in brackets when known: `[idea]`, `[praise]`,
     `[friction]`, `[question]`. If you cannot classify confidently, omit
     the bracket.
   - Concrete and specific. Reuse the user's wording when it is specific;
     rephrase when vague.

   **Body template** — populate every section; write `_(please fill in)_`
   in any section without evidence:

   ```markdown
   ## What's this about

   <One short line, naming the category: feature idea / praise / friction /
   question — and the surface it relates to. Example: "Feature idea for
   `/aidoc-flow:budget`.">

   ## Your feedback

   <One or two paragraphs. Weave `user_remark` together with the surface
   identified from context. Be concrete: name the command, the skill, the
   layer.>

   ## Context

   - Plugin version: <plugin_version>
   - Framework spec: <framework_spec>
   - Surface: <command / skill / layer the feedback is about; or `_(please
     fill in)_` if not derivable>

   ## What would the ideal outcome look like

   <One or two sentences describing what "fixed" or "better" looks like.
   If the user's remark implies it, name it. Otherwise write
   `_(please fill in)_`.>
   ```

   Do **not** include log content, file contents, or paths that look like
   secrets, even if they appear in the conversation. Replace such fragments
   with `(redacted)` in the body.

5. **URL-encode `title` and `body`** following RFC 3986 (LF → `%0A`,
   space → `%20`, `#` → `%23`, `:` → `%3A`, `/` → `%2F`, `(` `)` → `%28`
   `%29`, letters / digits / `.` / `-` unchanged).

6. **Construct the URL**:

   ```text
   https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=feedback.md&title=<encoded title>&body=<encoded body>
   ```

   One continuous string; no spaces or line breaks inside the URL.

7. **Print the preview, then the URL**, in this exact layout:

   ```text
   Drafted feedback (review before clicking):

     Title:
       <title>

     Body:
       <body, indented two spaces per line>

   Click to open the prefilled issue form:

       <URL from step 6>

   Use this for feature ideas, praise, friction, and questions that aren't
   bugs. For something that is clearly broken, /aidoc-flow:bug-report is the
   better channel.

   The form is prefilled but not submitted — only you click Submit on
   github.com. Edit the title or body directly on the form if anything needs
   adjusting.
   ```

8. **Stop**. Do not submit the issue, do not open a browser.

## Fallback path

If the encoded URL exceeds 6000 characters, print the title and body as
plain text and only the bare template URL:
`https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=feedback.md`
— the user pastes the title and body into the form. In practice the body is
short and the limit is rarely hit.

## Honest framing

- The plugin **never** submits the issue. The user clicks Submit on
  github.com.
- The drafted title and body are an LLM **proposal**. The user is expected
  to review and edit on github.com if needed.
- The command does **not** include secrets it sees in the conversation.

## Error handling

- Empty user argument: still produce a draft using the conversation context;
  if context is also empty, populate the body with `_(please fill in)_`
  placeholders so the user notices.
- Cannot read version stamp files: substitute `(unknown)`; do not skip the
  line.

## Maintenance

The backend is `.github/ISSUE_TEMPLATE/feedback.md`. If that template's
section names change, update the body template in step 4 so the prefilled
body still matches the template's structure.
