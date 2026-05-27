---
name: doc-prd-audit
description: Audit a PRD - run declarative structural checks plus content review and produce a combined report for doc-prd-fixer. Use for PRD quality gating before EARS.
metadata:
  tags:
    - sdd-workflow
    - layer-2-artifact
    - quality-assurance
  custom_fields:
    layer: 2
    artifact_type: PRD
    skill_category: quality-assurance
    upstream_artifacts: [BRD]
    downstream_artifacts: [EARS, BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.8.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold]
---

# doc-prd-audit

## Purpose

Run a **unified PRD audit** — declarative structural checks plus content-quality
review — in one pass, producing a single combined report that
`../doc-prd-fixer/SKILL.md` consumes. The framework ships no runtime code, so
**this skill is the validator**: Claude performs each check directly against the
PRD using the spec as the contract.

**Layer**: 2 (PRD quality gate). **Upstream**: a PRD file. **Downstream**:
`PRD-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after a PRD exists and before generating EARS, or inside the autopilot's
audit↔fix cycle. Do **not** use to create a PRD (use `../doc-prd/SKILL.md` or
`../doc-prd-autopilot/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior scores or
cached results; compute the EARS-Ready score independently each run.

**Report cleanup:** after writing the new report, delete superseded
`PRD-NN.A_audit_report_v*.md`; keep `PRD-NN.F_fix_report_v*.md` and
`.drift_cache.json`. Record a cleanup summary in the report.

## Execution Contract

**Input:** PRD path (`docs/02_PRD/PRD-NN_*/...`); optional score threshold
(default 90).

**Sequence:** 1) run structural checks → 2) record findings → 3) run content
review → 4) merge/normalize findings → 5) write `PRD-NN.A_audit_report_vNNN.md`
→ 6) if auto-fixable findings exist, hand off to `doc-prd-fixer`.

## Structural Checklist

Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/README.md`,
`${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/PRD-TEMPLATE.yaml` (embedded rules), and
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`.

**Tier 1 — blocking (error):**

| Check | Verifies |
|-------|----------|
| Element ID format | every ID matches `PRD.NN.SS.xxxx` (4-hex hash); `SS` = host section |
| Structure | all 15 template sections present and non-empty |
| Cumulative tags | `@brd:` tags present and resolving to existing BRD elements |
| Customer-facing content | §10 substantive in ≥3 categories (not placeholders) |
| Quality gate | EARS-Ready score ≥ threshold (default 90) |

**Tier 2 — advisory (warning):** frontmatter metadata (below); §8 holds
PRD-level summaries with the layer-separation note; internal links and
template/governance references resolve; no ADR numbers cited before they exist;
thresholds consistent across sections and with the BRD source; diagram contract
tags present (`@diagram: c4-l2`, `@diagram: dfd-l2`, `@diagram: sequence-sync`
with `alt/else` — use `../charts-flow/SKILL.md`).

**Combined status:** `PASS` only if all Tier 1 pass **and** content score ≥
threshold **and** no blocking issues; otherwise `FAIL`.

## Metadata Checks

| Field | Required | Valid values |
|-------|----------|--------------|
| `document_type` | yes | `prd-document` (not `template`) |
| `artifact_type` | yes | `PRD` |
| `layer` | yes | `2` |
| `deliverable_type` | yes | `code`, `document`, `ux`, `risk`, `process` |

Findings: `VALID-M001` missing `deliverable_type`; `VALID-M002` invalid value;
`VALID-M003` `document_type` not `prd-document`.

## Combined Report Format

Output: `PRD-NN.A_audit_report_vNNN.md`, with sections — **Summary** (ID,
timestamp, overall status, structural status, content score) · **Score
Calculation** (`100 − deductions`, threshold compare) · **Metadata Findings** ·
**Structural Findings** · **Content Findings** · **Diagram Contract Findings** ·
**Fix Queue** (`auto_fixable` / `manual_required` / `blocked`) · **Recommended
Next Step** · **Cleanup Summary**.

## Hand-off to doc-prd-fixer

Normalize every finding to: `source` (`structural`|`content`), `code`,
`severity` (`error`|`warning`|`info`), `file`, `section`, `action_hint`,
`confidence` (`auto-safe`|`auto-assisted`|`manual-required`). `doc-prd-fixer`
consumes the latest `PRD-NN.A_audit_report_vNNN.md`.

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor only this skill's declared knobs:
`section_toggles` (a toggled-off **optional** section is not a finding; a
missing **required** section still is), `active_layers` (never flag the
absence of — or a missing reference to — a layer the project disabled, per the
cascade rule), and `audit_threshold` (use the project's quality-gate score
only when it is **>=** the framework default; ignore any lower value). Ignore
unknown keys.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-prd/SKILL.md` · Fix: `../doc-prd-fixer/SKILL.md` · Generate:
  `../doc-prd-autopilot/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/PRD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
