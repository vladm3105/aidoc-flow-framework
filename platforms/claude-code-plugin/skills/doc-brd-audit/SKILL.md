---
name: doc-brd-audit
description: Audit a BRD - run declarative structural checks plus content review and produce a combined report for doc-brd-fixer. Use for BRD quality gating before PRD.
metadata:
  tags:
    - sdd-workflow
    - layer-1-artifact
    - quality-assurance
  custom_fields:
    layer: 1
    artifact_type: BRD
    skill_category: quality-assurance
    upstream_artifacts: []
    downstream_artifacts: [PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.5.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold]
---

# doc-brd-audit

## Purpose

Run a **unified BRD audit** — declarative structural checks plus content-quality
review — in one pass, producing a single combined report that
`../doc-brd-fixer/SKILL.md` consumes. The framework ships no runtime code, so
**this skill is the validator**: Claude performs each check directly against the
BRD using the spec as the contract.

**Layer**: 1 (BRD quality gate). **Upstream**: a BRD file. **Downstream**:
`BRD-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after a BRD exists and before generating the PRD, or inside the autopilot's
audit↔fix cycle. Do **not** use to create a BRD (use `../doc-brd/SKILL.md` or
`../doc-brd-autopilot/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior scores or
cached results; compute the PRD-Ready score independently each run.

**Report cleanup:** after writing the new report, delete superseded
`BRD-NN.A_audit_report_v*.md`; keep `BRD-NN.F_fix_report_v*.md` and
`.drift_cache.json`. Record a cleanup summary in the report.

## Execution Contract

**Input:** BRD path (`docs/01_BRD/BRD-NN_*/...`); optional score threshold
(default 90).

**Sequence:** 1) run structural checks → 2) record findings → 3) run content
review → 4) merge/normalize findings → 5) write `BRD-NN.A_audit_report_vNNN.md`
→ 6) if auto-fixable findings exist, hand off to `doc-brd-fixer`.

## Structural Checklist

Authority: `framework/layers/01_BRD/README.md`,
`framework/layers/01_BRD/BRD-TEMPLATE.yaml` (embedded rules +
`cross_section_rules`), and `framework/governance/ID_NAMING_STANDARDS.md`.

**Tier 1 — blocking (error):**

| Check | Verifies |
|-------|----------|
| Element ID format | every ID matches `BRD.NN.SS.xxxx` (4-hex hash) |
| Structure | all required template sections present and non-empty |
| Cross-section rules | `cross_section_rules` from the template hold |
| Quality gate | PRD-Ready score ≥ threshold (default 90) |

**Tier 2 — advisory (warning):** frontmatter metadata (below); internal links
and template/governance references resolve; no downstream numbers cited before
they exist; diagram contract tags present (`@diagram: c4-l1`, `@diagram: dfd-l1`
— advisory for BRD; use `../charts-flow/SKILL.md`).

**Combined status:** `PASS` only if all Tier 1 pass **and** content score ≥
threshold **and** no blocking issues; otherwise `FAIL`.

## Metadata Checks

| Field | Required | Valid values |
|-------|----------|--------------|
| `document_type` | yes | `brd-document` (not `template`) |
| `artifact_type` | yes | `BRD` |
| `layer` | yes | `1` |
| `deliverable_type` | yes | `code`, `document`, `ux`, `risk`, `process` |

Findings: `VALID-M001` missing `deliverable_type`; `VALID-M002` invalid value;
`VALID-M003` `document_type` not `brd-document`.

## Combined Report Format

Output: `BRD-NN.A_audit_report_vNNN.md`, with sections — **Summary** (ID,
timestamp, overall status, structural status, content score) · **Score
Calculation** (`100 − deductions`, threshold compare) · **Metadata Findings** ·
**Structural Findings** · **Content Findings** · **Diagram Contract Findings** ·
**Fix Queue** (`auto_fixable` / `manual_required` / `blocked`) · **Recommended
Next Step** · **Cleanup Summary**.

## Hand-off to doc-brd-fixer

Normalize every finding to: `source` (`structural`|`content`), `code`,
`severity` (`error`|`warning`|`info`), `file`, `section`, `action_hint`,
`confidence` (`auto-safe`|`auto-assisted`|`manual-required`). `doc-brd-fixer`
consumes the latest `BRD-NN.A_audit_report_vNNN.md`.

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor only this skill's declared knobs:
`section_toggles` (a toggled-off **optional** section is not a finding; a
missing **required** section still is), `active_layers` (never flag the
absence of — or a missing reference to — a layer the project disabled, per the
cascade rule), and `audit_threshold` (use the project's quality-gate score
only when it is **>=** the framework default; ignore any lower value). Ignore
unknown keys.
Authority: `framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-brd/SKILL.md` · Fix: `../doc-brd-fixer/SKILL.md` · Generate:
  `../doc-brd-autopilot/SKILL.md`
- Authority: `framework/layers/01_BRD/README.md`,
  `framework/layers/01_BRD/BRD-TEMPLATE.yaml`,
  `framework/governance/ID_NAMING_STANDARDS.md`
