---
title: "Next — recommended next action"
description: Recommend the single concrete next action based on the project's SDD state. Reads the same docs tree as `/status`.
tags:
  - workflow
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Next

Tell the user the one thing to do next. Not a menu, not the whole roadmap —
one concrete command. Uses the same detection logic as `/aidoc-flow:status`,
applies a small decision tree, and emits a single recommendation.

## Instructions

1. **Resolve project root and detect layer state** — identical to step 1-2
   of `/aidoc-flow:status`. Skip the table render; you only need the
   per-layer `(exists, instances, audited)` triple.

2. **Apply the decision tree** in order; first matching rule wins:

   | Rule | Condition | Recommend |
   |------|-----------|-----------|
   | R0 | No layer directories exist at all | `/aidoc-flow:project-init` — scaffold the SDD layout |
   | R1 | A layer exists but the layer below it (smaller `N`) does NOT — out-of-order | `/aidoc-flow:doc-flow` — out-of-order layers detected; this skill explains the canonical order |
   | R2 | The lowest-numbered missing layer is `N` and layer `N-1` exists | `/aidoc-flow:doc-<layer N>-autopilot` — draft layer `N` from the upstream artifact |
   | R3 | Every layer present has an audit, and IPLAN exists with audit | "All eight layers are present and audited. The next step is implementation — drive the IPLAN to code." |
   | R4 | At least one layer exists without an audit (the lowest such) | `/aidoc-flow:doc-<that layer>-audit` — score the layer before promoting |
   | R5 | A layer's most recent audit scores below its gate (only knowable if `.aidoc/` carries that info) | `/aidoc-flow:doc-<that layer>-fixer` — remediate the audit findings |

   If a rule needs information you cannot resolve (e.g. R5 requires gate
   scores you cannot read), skip to the next rule.

3. **Render the recommendation** — one block, three lines:

   ```text
   Position: <Highest layer present> (<N> of 8)
   Next:     <one of the recommendations above>
   Why:      <one sentence explaining the rule that fired>
   ```

   Example:

   ```text
   Position: PRD (2 of 8)
   Next:     /aidoc-flow:doc-ears-autopilot
   Why:      PRD exists; EARS (the next layer) does not.
   ```

4. **Stop**. Do not run the recommended skill — just print the recommendation
   so the user can choose to run it.

## Error handling

- No SDD layout at all: emit R0 (`/aidoc-flow:project-init`).
- Conflicting signals (e.g. layer 3 exists but layer 2 does not): emit R1 —
  out-of-order. Recommend `doc-flow` so the user can untangle without making
  it worse.
- Partial detection (cannot determine audited state): emit the recommendation
  but replace `Why` with `Why: based on layer existence only; audit state
  unknown`.
