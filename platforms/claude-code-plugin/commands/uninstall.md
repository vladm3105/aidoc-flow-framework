---
title: "Uninstall — guided exit"
description: Walk the user through removing the plugin and (optionally) plugin-written scratch files. This command does NOT remove the plugin itself.
tags:
  - lifecycle
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Uninstall

A slash command cannot remove the plugin that's running it — Claude Code's
native `/plugin uninstall` does. This command is a **guided exit**: it
confirms intent, prints the exact native command to run, lists what the
native uninstall removes vs preserves, and offers to clean only the
plugin-written scratch in the current project.

## Instructions

1. **Confirm intent** — ask once. If the user answers anything other than a
   clear yes, stop and acknowledge.

   ```text
   Removing aidoc-flow has two parts:
     1. Uninstalling the plugin itself (Claude Code native command — your job)
     2. Optionally cleaning plugin-written scratch in this project (this command)

   Want to proceed?
   ```

2. **Print the native uninstall command** — exactly:

   ```text
   To uninstall the plugin, run this in Claude Code:

       /plugin uninstall aidoc-flow@aidoc-flow-framework

   This command (the one you're running now) cannot do that for you — a
   plugin slash command cannot remove the plugin it lives in.
   ```

3. **Print what native uninstall removes vs preserves**:

   ```text
   The native uninstall WILL remove:
     - The plugin's installed files (skills, agents, commands, hooks)
     - The PostToolUse review-nudge hook registration

   The native uninstall WILL NOT touch:
     - Your project's docs/ artifacts (BRD, PRD, EARS, …)
     - Your project's .aidoc/ audit and review artifacts
     - Your project's .claude/aidoc-flow.config.yaml (if present)
     - Anything else under your project root
   ```

4. **Offer optional cleanup** of plugin-written scratch in the **current
   project only** (not the install itself). The default is to leave files
   alone — user must opt in per item.

   ```text
   Optional: clean plugin-written state in this project.

     [ ] .aidoc/ scratch directory (audit and review artifacts) — usually keep
     [ ] .claude/aidoc-flow.config.yaml (your overrides)         — usually keep
     [ ] .claude/CLAUDE.md "Work Plans Directory" line           — usually keep

   Defaults are to keep everything. Anything you check is your work — make
   sure it's backed up.
   ```

   Use `AskUserQuestion` (multi-select) to capture the choices. For each
   checked item, perform the removal and report it. For unchecked items,
   say nothing.

5. **Print the goodbye line**:

   ```text
   Before you go, tell us what we could have done better:
     /aidoc-flow:feedback

   Thanks for trying aidoc-flow.
   ```

6. **Stop**. Do not attempt `/plugin uninstall` (it's not yours to run); do
   not delete files outside the current project root.

## Honest caveats baked into the prose

This command's whole point is to be honest about its limits:

- It cannot remove the plugin (line 2 says so explicitly).
- It does not touch any user artifact unless the user explicitly opts in.
- It refuses to operate outside the current project root.

## Error handling

- If the user declines step 1: print "Okay, leaving everything in place." and
  stop.
- If a requested cleanup target does not exist: silently skip it.
- If a cleanup write fails (permissions, etc.): print the failure and
  continue with the remaining targets; never crash mid-cleanup.
