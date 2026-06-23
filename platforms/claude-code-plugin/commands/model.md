---
title: "Model — recommended model per layer"
description: Focused editor for the `model.*` keys. Advisory only — the plugin cannot switch the session model. Prints copy-paste `/model` commands.
tags:
  - config
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Model

Focused editor for the `model.*` keys of `.claude/aidoc-flow.config.yaml`.
Records the user's preferred model per SDD layer and the precheck strictness.
For the full schema and every other setting, see
`${CLAUDE_PLUGIN_ROOT}/docs/CONFIG.md` or run `/aidoc-flow:configure`.

## Honest caveat (read this first)

This command is **advisory**. The plugin cannot switch the Claude Code session
model. The session model is set by the user via Claude Code's native
`/model <id>` command. Plugin commands and skills run on whatever model the
session is currently on, full stop.

What this command actually does:

1. Records the user's preferred model **per layer** in the config file.
2. Prints the **copy-paste `/model <id>` commands** so the user can switch
   manually when starting work on each layer.
3. Sets the `precheck` mode the **layer autopilots** consult to decide how
   prominently to surface the per-layer recommendation before drafting. (The
   plugin cannot read or switch the session model, so the autopilots *print*
   the recommendation — they do not compare against the current model.)

Naming note: the user invokes this as `/aidoc-flow:model`, which is
namespaced and **does not collide** with Claude Code's built-in `/model`.

## Instructions

1. **Read current state** — load `.claude/aidoc-flow.config.yaml` if it
   exists; otherwise start from the defaults documented in
   `${CLAUDE_PLUGIN_ROOT}/docs/CONFIG.md`.

2. **Print the caveat banner** (one paragraph; reuse the language above so
   the user sees it inside the command, not only in this file).

3. **Prompt for the default model** — `AskUserQuestion` (free text or
   single-select if you offer a curated short list):

   - Current value (from config or default `claude-sonnet-4-6`) — keep
   - A free-text field for any model id that Claude Code's native `/model`
     accepts

   Do not validate the id against a hard-coded list; new models ship faster
   than this command updates.

4. **Offer per-layer overrides** — `AskUserQuestion` (yes/no): "Set a
   different model recommendation for specific layers? (e.g. Opus for BRD
   and IPLAN, default for the rest.)"

   If yes, for each of the eight layers (`BRD`, `PRD`, `EARS`, `BDD`,
   `ADR`, `SPEC`, `TDD`, `IPLAN`) prompt for a model id (free text). Empty
   input means "no override; use the default model." Record only non-empty
   choices in `model.per_layer`.

5. **Prompt for `precheck` mode** — single-select:

   - `warn` — print a one-line recommendation (the layer's model + the
     `/model <id>` command), then proceed *(recommended)*
   - `silent` — print nothing, just proceed
   - `block` — print the recommendation, then wait for the user to confirm or
     switch before drafting

6. **Write back** — merge the new `model.*` keys into the existing config
   file (preserve every other key untouched). If the file does not exist,
   create it with `schema: 1` and only the keys this command sets.

7. **Print the copy-paste switching commands** — for each layer with a
   recommendation, print the exact native command:

   ```text
   To switch model in Claude Code, run one of:

       /model <model.default>                 # for general work
       /model <model.per_layer.BRD>           # before authoring a BRD
       /model <model.per_layer.IPLAN>         # before drafting an IPLAN
       …
   ```

   Only print layers that have an override; the default model line is
   always there.

8. **Confirm**:

   ```text
   Model recommendations recorded.
     default: <chosen>
     per-layer overrides: <list, or "none">
     precheck: <warn | silent | block>

   Wrote .claude/aidoc-flow.config.yaml.

   Reminder: this command records the recommendation. To switch model,
   run the native /model <id> command in Claude Code.
   ```

9. **Stop**. Do not touch `budget.*` or any other key.

## Error handling

- Invalid YAML in the existing file: do not overwrite. Print the parse error
  and recommend `/aidoc-flow:configure reset` or hand-editing.
- User leaves every per-layer prompt empty: drop the `per_layer` map
  entirely (don't write an empty object); the default model alone applies.
- `.claude/` directory missing: create it before writing.
