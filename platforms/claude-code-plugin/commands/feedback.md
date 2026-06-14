---
title: "Share feedback"
description: Print a prefilled GitHub Issues URL targeting the feedback template — for feature ideas, what worked, what didn't.
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

## Instructions

1. **Print the feedback block** verbatim:

   ```text
   Share feedback here:

       https://github.com/vladm3105/aidoc-flow-framework/issues/new?template=feedback.md

   Use this for:
       - Feature ideas ("could the plugin also do X?")
       - What worked well (so we keep doing it)
       - What didn't work (so we can fix the experience)
       - Questions about the flow that aren't bugs

   For something that is clearly broken, use /aidoc-flow:bug-report instead.
   ```

2. **Stop**. Do not submit the issue, do not open a browser.

## Maintenance

The backend is `.github/ISSUE_TEMPLATE/feedback.md`. If that template moves or
is renamed, update the URL in this file. The destination repo and template
filename are the only two things this command knows; everything else is the
user's own words on the GitHub form.
