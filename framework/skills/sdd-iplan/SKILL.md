---
name: sdd-iplan
description: >-
  Author the scoped or full IPLAN the CHG points at: In Progress status, authorizing CHG, and a file manifest covering every touched file — no code without it.
---

# SDD IPLAN Author

> Framework skill — routes to `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`
> and the executing example `framework/archive/CHG-*/IPLAN-*.yaml`.
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> The authorizing CHG (`sdd-chg-author`) must exist first, except for
> seed-phase drafting before the first BRD — the sole change needing
> neither object.

## 1. The gate (non-negotiable)

No code may be written without an IPLAN, and the IPLAN must be `In Progress`,
reference its authorizing CHG (`source_chg`), and list every modified file in
`file_manifest` — one entry per path with `action` (create/modify) and
`status` (TODO → DONE). A manifest that misses a file the diff touches fails
the gate the same way a missing IPLAN does.

## 2. Shape follows the flow

Match the IPLAN shape to the classified flow: DIR2C takes a scoped IPLAN
(manifest + steps + rollback only); CODE2C takes a bugfix-subtype IPLAN
(`parent_iplan` + `source_chg`, repair-scoped manifest, rollback); full
flows take the full form with all code steps and the complete manifest.
Bug fixes ride their IPLAN's authorizing CHG when it is active, otherwise
the bugfix vehicle (C1 CHG + bugfix IPLAN, parent standing).

## 3. Execute and close out

Work the manifest TODO → DONE, keeping `phase_findings` honest (guards
observed red, fixes declined with reasons). Verification commands named in
the IPLAN run per step, not once at the end. Flip status to Implemented
only when the manifest is fully DONE and the suites are green on the head
that carries the work.
