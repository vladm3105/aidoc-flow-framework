---
name: doc-tdd-audit
description: Audit a TDD - run declarative structural checks plus content review and produce a combined report for doc-tdd-fixer. Use for TDD quality gating before IPLAN.
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN]
    version: "0.4.2"
    framework_spec_version: "0.11.3"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold]
---

# doc-tdd-audit

## Purpose

Run a **unified TDD audit** — declarative structural checks plus content-quality
review — in one pass, producing a single combined report that
`../doc-tdd-fixer/SKILL.md` consumes. The framework ships no runtime code, so
**this skill is the validator**: Claude performs each check directly against the
TDD using the spec as the contract.

**Layer**: 7 (TDD quality gate). **Upstream**: a TDD file. **Downstream**:
`TDD-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after a TDD exists and before generating the IPLAN, or inside the
autopilot's audit↔fix cycle. Do **not** use to create a TDD (use
`../doc-tdd/SKILL.md` or `../doc-tdd-autopilot/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior scores or
cached results; compute the IPLAN-Ready score independently each run.

**Report cleanup:** after writing the new report, delete superseded
`TDD-NN.A_audit_report_v*.md`; keep `TDD-NN.F_fix_report_v*.md` and
`.drift_cache.json`. Record a cleanup summary in the report.

## Execution Contract

**Input:** TDD path (`docs/07_TDD/TDD-NN_*/...`); optional score threshold
(default 90).

**Sequence:** 1) run structural checks → 2) record findings → 3) run content
review → 4) merge/normalize findings → 5) write `TDD-NN.A_audit_report_vNNN.md`
→ 6) if auto-fixable findings exist, hand off to `doc-tdd-fixer`.

## Structural Checklist

Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/README.md`,
`${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-TEMPLATE.yaml` (embedded rules), and
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`. Style:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`.

**Template-conformance enumeration (mandatory first step).** Load
`TDD-TEMPLATE.yaml` and enumerate every required section (each top-level YAML
key that is not explicitly `required: false`). The Structure check below is
satisfied **only** when every enumerated required section appears as a `##`
heading in the artifact. Any missing required section is a **blocking finding**
— never rationalise it as a "compact" variant, "documented walkthrough",
"lint-pinned", or any other exception. There is one template per layer and one
canonical required-section set.

**Tier 1 — blocking (error):**

| Check | Verifies |
|-------|----------|
| Element ID format | every test-case ID matches `TDD.NN.04.xxxx` (4-hex hash); no removed patterns |
| Structure | every section enumerated above is present and non-empty |
| Test types | each case carries a valid `type` (unit/integration/e2e/security) |
| BDD mapping | each BDD scenario maps to tests (Section 3) |
| Cumulative tags | upstream @brd @prd @ears @bdd @adr @spec all present |
| Parent SPEC | `@spec: SPEC-NN` valid and the SPEC file exists |
| Quality gate | IPLAN-Ready score ≥ threshold (default 90) |

**Tier 2 — advisory (warning):** inputs/expected outputs present per case; edge
cases/error paths documented; e2e cases carry a `bdd_ref`; thresholds set per
type; frontmatter metadata (below); internal links and template/governance
references resolve; diagram tags present (use `../charts-flow/SKILL.md`).

**Authoring-style check (Tier 2 → Tier 1 at threshold).** Verify the document
complies with `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`:
no banned phrases, form preferences observed (tables/bullets over prose where
homogeneous), size targets met within +50%. **Promote to blocking** when ≥3
banned phrases occur in one section OR the document exceeds its size target by
>50%.

**Combined status:** `PASS` only if all Tier 1 pass **and** content score ≥
threshold **and** no blocking issues; otherwise `FAIL`.

## Metadata Checks

| Field | Required | Valid values |
|-------|----------|--------------|
| `document_type` | yes | `tdd-document` (not `template`) |
| `artifact_type` | yes | `TDD` |
| `layer` | yes | `7` |
| `deliverable_type` | yes | `code` |

Findings: `VALID-M001` missing `deliverable_type`; `VALID-M002` invalid value;
`VALID-M003` `document_type` not `tdd-document`.

## Combined Report Format

Output: `TDD-NN.A_audit_report_vNNN.md`, with sections — **Summary** (ID,
timestamp, overall status, structural status, content score) · **Score
Calculation** (`100 − deductions`, threshold compare) · **Metadata Findings** ·
**Structural Findings** · **Content Findings** · **Coverage Findings** (per-type
unit/integration/e2e/security coverage; BDD→test and SPEC-alignment summary) ·
**Fix Queue** (`auto_fixable` / `manual_required` / `blocked`) · **Recommended
Next Step** · **Cleanup Summary**.

## Hand-off to doc-tdd-fixer

Normalize every finding to: `source` (`structural`|`content`), `code`,
`severity` (`error`|`warning`|`info`), `file`, `section`, `action_hint`,
`confidence` (`auto-safe`|`auto-assisted`|`manual-required`). `doc-tdd-fixer`
consumes the latest `TDD-NN.A_audit_report_vNNN.md`.

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

- Create: `../doc-tdd/SKILL.md` · Fix: `../doc-tdd-fixer/SKILL.md` · Generate:
  `../doc-tdd-autopilot/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
