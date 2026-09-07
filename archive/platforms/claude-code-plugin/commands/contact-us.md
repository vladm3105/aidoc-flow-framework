---
title: "Contact us"
description: One-line per contact channel — repo, issues, maintainer GitHub.
tags:
  - meta
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Contact Us

Print the available contact channels for the aidoc-flow project, one line each.
Static output; no file reads, no shell calls.

## Instructions

1. **Print the channels block** verbatim:

   ```text
   aidoc-flow — contact

   Repository:        https://github.com/vladm3105/aidoc-flow-framework
   Issues (bugs):     https://github.com/vladm3105/aidoc-flow-framework/issues
   Maintainer:        @vladm3105 (GitHub)

   For bug reports:   /aidoc-flow:bug-report
   For feedback:      /aidoc-flow:feedback
   ```

2. **Stop**. Do not invent additional channels (Slack, Discord, email) — if a
   channel is not listed here, it does not exist for this project yet.

## Maintenance

When a new contact channel is added (Discussions, mailing list, etc.), update
this file directly. The command output is intentionally hand-edited rather
than auto-discovered to avoid surfacing channels that are not yet ready.
