---
title: "About — aidoc-flow plugin"
description: Show plugin version, framework spec version, license, repository, and homepage.
tags:
  - meta
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# About

Print a one-screen summary identifying this plugin and the framework spec it
conforms to. Useful as the first thing to share when filing a bug report or
checking that the right version is installed.

## Instructions

1. **Read the plugin's identity files** (do not invent values):
   - `${CLAUDE_PLUGIN_ROOT}/VERSION` — the plugin's own SemVer.
   - `${CLAUDE_PLUGIN_ROOT}/FRAMEWORK_SPEC_VERSION` — the spec version the
     plugin declares conformance to.
   - `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` — the manifest. Pull
     `name`, `description`, `version`, `license`, `repository`, `homepage`,
     `author.name`, `author.url`.

2. **Render the about screen** as a table. Use the exact values you read; if
   any file is missing, print `(unknown)` in that cell rather than guessing.

   ```text
   aidoc-flow — Claude Code plugin

   | Field              | Value                                          |
   |--------------------|------------------------------------------------|
   | Plugin             | <name>                                         |
   | Plugin version     | <VERSION>                                      |
   | Framework spec     | <FRAMEWORK_SPEC_VERSION>                       |
   | License            | <license>                                      |
   | Repository         | <repository>                                   |
   | Homepage           | <homepage>                                     |
   | Author             | <author.name> (<author.url>)                   |

   <description from plugin.json>
   ```

3. **Append three navigation pointers** (one line each) so the user knows
   where to go next:
   - `Run /aidoc-flow:help — orient yourself in the 8-layer flow`
   - `Run /aidoc-flow:bug-report — file a bug with this version stamp`
   - `Run /aidoc-flow:status — see where the current project is in the flow`

4. **Do not** print anything else. No marketing, no per-skill summaries (that's
   `/aidoc-flow:help`'s job).

## Error handling

- If `${CLAUDE_PLUGIN_ROOT}` is not set or any of the three identity files is
  unreadable, render whichever cells you can resolve and fill the rest with
  `(unknown)`. Do not fail.
- Never invent a version number. `(unknown)` is the correct value when the
  file cannot be read.
