---
title: "Share feedback"
description: Print a GitHub Issues URL with the version-stamp Context section URL-encoded into `&body=`, so feedback issues open with plugin/spec versions already filled — no manual paste step.
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
feedback is "what would you change" or "what worked." Both flow to GitHub
Issues, with different templates so triage can route them.

The command prefills the version stamp into the issue body via the `&body=`
URL parameter, so the user only fills in their actual feedback. It does
**not** submit the issue.

## Instructions

1. **Gather the version stamp** — read the same identity files as
   `/aidoc-flow:about`:
   - `${CLAUDE_PLUGIN_ROOT}/VERSION`
   - `${CLAUDE_PLUGIN_ROOT}/FRAMEWORK_SPEC_VERSION`

2. **Assemble the Context section** — exactly four lines (LF-separated),
   matching the `## Context` slot in `.github/ISSUE_TEMPLATE/feedback.md`:

   ```text
   ## Context

   - Plugin version: <VERSION>
   - Framework spec: <FRAMEWORK_SPEC_VERSION>
   ```

3. **URL-encode the Context section** using the same RFC 3986 / HTML form
   conventions documented in `commands/bug-report.md` (LF → `%0A`,
   space → `%20`, `#` → `%23`, `:` → `%3A`, etc.).

4. **Construct the URL** by joining three parts with `?` and `&`:

   ```text
   https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=feedback.md&body=<URL-encoded Context section from step 3>
   ```

   One continuous string; no spaces or line breaks inside the URL.

5. **Print exactly this output**:

   ```text
   Share feedback — click this link and the version stamp will be prefilled:

       <the URL from step 4>

   Use this for:
       - Feature ideas ("could the plugin also do X?")
       - What worked well (so we keep doing it)
       - What didn't work (so we can fix the experience)
       - Questions about the flow that aren't bugs

   For something that is clearly broken, use /aidoc-flow:bug-report instead.

   The form opens on github.com; review before clicking Submit.
   ```

6. **Stop**. Do not submit the issue, do not open a browser.

## Error handling

- If either identity file cannot be read, substitute `(unknown)` for that
  field — do not skip the line.
- If the encoded URL would exceed 6000 characters, fall back to the bare
  template URL `https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=feedback.md`
  and print the Context section as text for the user to paste. The version
  stamp is short (well under the limit); this fallback exists as a safety net.

## Maintenance

The backend is `.github/ISSUE_TEMPLATE/feedback.md`. If that template moves
or is renamed, update the URL in step 4. The destination repo, template
filename, and the encoding contract in step 3 are the three things this
command knows; everything else is the user's own words on the GitHub form.
