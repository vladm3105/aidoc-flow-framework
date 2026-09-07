---
title: "Budget — effort knob for the doc-* skills"
description: Focused editor for `budget.profile` (max | standard | min) and the per-layer override map. Behavior knob, not a token cap — see caveat.
tags:
  - config
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Budget

Focused editor for the `budget.*` keys of `.claude/aidoc-flow.config.yaml`.
For the full schema and every other setting, see
`${CLAUDE_PLUGIN_ROOT}/docs/CONFIG.md` or run `/aidoc-flow:configure`.

## Honest caveat (read this first)

This is a **behavior knob**, not a token meter.

The profile tells the `doc-*` skills how much *work* to do per artifact —
how many review passes, how deep the checklists, how verbose the output.
The plugin has **no token-budget enforcement hook**: nothing stops a Claude
Code session from spending tokens, and this command cannot impose a hard
cap.

- `max` — multi-pass review, deeper checklists, longer outputs
- `standard` — default; what every skill does today
- `min` — single-pass, terse, skip optional checks

Empirically, `min` reduces tokens 40–60% on most `doc-*` skills versus
`standard`, by skipping passes the skill itself owns. That is the real cost
lever this command offers. If you need an actual cap, use Claude Code's
session-level controls.

This command is advisory in the same way `/aidoc-flow:model` is advisory:
it sets the user's preference so skills can read it and adjust behavior, but
the runtime guarantees live with Claude Code, not with the plugin.

## Instructions

1. **Read current state** — load `.claude/aidoc-flow.config.yaml` if it
   exists; otherwise start from the defaults documented in
   `${CLAUDE_PLUGIN_ROOT}/docs/CONFIG.md`.

2. **Print the caveat banner** (one paragraph; reuse the language above so
   the user sees it inside the running command, not only in this file).

3. **Prompt for the default profile** — `AskUserQuestion` (single-select):

   - `max — multi-pass, deeper, longer`
   - `standard — default` *(recommended for production work)*
   - `min — single-pass, terse` *(recommended for test/scratch projects)*

   Show the current value as the first option.

4. **Offer per-layer overrides** — ask `AskUserQuestion` (yes/no): "Set a
   different profile for specific layers? (e.g. `max` for BRD, `min` for
   IPLAN scratch.)"

   If yes, for each of the eight layers (`BRD`, `PRD`, `EARS`, `BDD`,
   `ADR`, `SPEC`, `TDD`, `IPLAN`) ask single-select: `inherit | max |
   standard | min`. `inherit` means no override — the default profile
   applies. Record only non-`inherit` choices in `budget.profile_per_layer`.

5. **Write back** — merge the new `budget.*` keys into the existing config
   file (preserve every other key untouched). If the file does not exist,
   create it with `schema: 1` and only the keys this command sets.

6. **Confirm** — print the effective state:

   ```text
   Budget profile set:
     default: <chosen>
     overrides:
       BRD:   <override or 'inherits default'>
       PRD:   <…>
       …

   Wrote .claude/aidoc-flow.config.yaml.

   Reminder: profile changes skill behavior, not session token usage.
   ```

7. **Stop**. Do not touch `model.*` or any other key.

## Error handling

- Invalid YAML in the existing file: do not overwrite. Print the parse error
  and recommend `/aidoc-flow:configure reset` or hand-editing.
- User picks `inherit` for every per-layer prompt: drop the
  `profile_per_layer` map entirely (don't write an empty object); rely on
  the default profile alone.
- `.claude/` directory missing: create it before writing.
