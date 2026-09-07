---
title: "Help — orient in the aidoc-flow plugin"
description: Show the 8-layer SDD flow, the top entry skills, and the full command index. Routes to `doc-flow` for skill-specific routing.
tags:
  - meta
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Help

Orient a first-time (or returning) user in the plugin. With 50+ skills, 11
agents, and 12 commands installed, the user needs a single screen that tells
them: what the plugin does, where to start, and what's available.

This command **does not orchestrate skills**. The `doc-flow` skill is the
orchestrator-of-record — it routes intent to the right skill and reports
current position. `/aidoc-flow:help` is one level above that: it points users
at `doc-flow`.

## Instructions

1. **Print the elevator line** (one paragraph):

   ```text
   aidoc-flow is a Spec-Driven Development (SDD) workflow for Claude Code.
   It drives a project from a Business Requirements Document down to an
   implementation plan through eight traceable layers:

       BRD (1) → PRD (2) → EARS (3) → BDD (4) → ADR (5) → SPEC (6) → TDD (7) → IPLAN (8) → Code

   Each layer is a SKILL. Run the skill, audit the output, fix it, promote
   to the next layer.
   ```

2. **Top entry skills** — print three lines, the same three the README
   Quickstart promotes:

   - `doc-flow` — "which skill do I need?" — start here when unsure
   - `project-init` — scaffold the `docs/` layer tree for a new project
   - `doc-brd-autopilot` — draft the first layer (BRD) end-to-end

3. **Full command index** — enumerate every file under
   `${CLAUDE_PLUGIN_ROOT}/commands/*.md`, reading the `title` and
   `description` from each frontmatter block. Render as a grouped table; use
   the `tags` field to group (meta | workflow | lifecycle | config | utility).
   For each command print `/aidoc-flow:<filename-without-md>` and the
   description. Do not invent commands — only enumerate what's on disk.

   ```text
   Commands

   Meta
     /aidoc-flow:about         — show plugin/spec version, license, repo
     /aidoc-flow:help          — this command
     /aidoc-flow:bug-report    — file a bug with prefilled version stamp
     /aidoc-flow:contact-us    — contact channels
     /aidoc-flow:feedback      — share what worked / didn't / what to change

   Workflow
     /aidoc-flow:status        — per-layer state of the current project
     /aidoc-flow:next          — one concrete next action

   Lifecycle
     /aidoc-flow:uninstall     — guided exit
     /aidoc-flow:save-plan     — save the current session's plan to disk

   Config
     /aidoc-flow:configure     — bulk editor for .claude/aidoc-flow.config.yaml
     /aidoc-flow:budget        — effort knob (advisory — see caveat in command)
     /aidoc-flow:model         — recommended model per layer (advisory)
   ```

   If `tags` is missing from a frontmatter block, place the command under
   `Other` rather than skipping it.

4. **One-line README pointer**:

   ```text
   Full README: ${CLAUDE_PLUGIN_ROOT}/README.md
   ```

5. **Stop**. Do not run any skill; do not draft an artifact. If the user
   wants to act, they will run `/aidoc-flow:doc-flow` or the specific
   command.

## Error handling

- If a command file is missing a `title` or `description`, use the filename
  itself as the title and print `(no description)` rather than skipping.
- If `${CLAUDE_PLUGIN_ROOT}/commands/` cannot be listed, print the elevator
  line and the top three entry skills only; note that the command index was
  unavailable.
