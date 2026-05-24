---
name: doc-ears-audit
description: Audit an EARS document - run declarative structural checks plus content review and produce a combined report for doc-ears-fixer. Use for EARS quality gating before BDD.
metadata:
  tags:
    - sdd-workflow
    - layer-3-artifact
    - quality-assurance
  custom_fields:
    layer: 3
    artifact_type: EARS
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD]
    downstream_artifacts: [BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.4.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold]
---

# doc-ears-audit

## Purpose

Run a **unified EARS audit** — declarative structural checks plus content-quality
review — in one pass, producing a single combined report that
`../doc-ears-fixer/SKILL.md` consumes. The framework ships no runtime code, so
**this skill is the validator**: Claude performs each check directly against the
EARS using the spec as the contract.

**Layer**: 3 (EARS quality gate). **Upstream**: an EARS file. **Downstream**:
`EARS-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after an EARS exists and before generating the BDD, or inside the autopilot's
audit↔fix cycle. Do **not** use to create an EARS (use `../doc-ears/SKILL.md` or
`../doc-ears-autopilot/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior scores or
cached results; compute the BDD-Ready score independently each run.

**Report cleanup:** after writing the new report, delete superseded
`EARS-NN.A_audit_report_v*.md`; keep `EARS-NN.F_fix_report_v*.md` and
`.drift_cache.json`. Record a cleanup summary in the report.

## Execution Contract

**Input:** EARS path (`docs/03_EARS/EARS-NN_*/...`); optional score threshold
(default 90).

**Sequence:** 1) run structural checks → 2) record findings → 3) run content
review → 4) merge/normalize findings → 5) write `EARS-NN.A_audit_report_vNNN.md`
→ 6) if auto-fixable findings exist, hand off to `doc-ears-fixer`.

## Structural Checklist

Authority: `framework/layers/03_EARS/README.md`,
`framework/layers/03_EARS/EARS-TEMPLATE.yaml` (embedded rules), and
`framework/governance/ID_NAMING_STANDARDS.md`.

**Tier 1 — blocking (error):**

| Check | Verifies |
|-------|----------|
| Element ID format | every ID matches `EARS.NN.SS.xxxx` (4-hex hash) |
| Structure | all 5 template sections present and non-empty |
| EARS syntax | every requirement has a trigger (WHEN/IF/WHILE) + `THE … SHALL`; statements atomic |
| Quantifiable constraints | timing uses p50/p95/p99; no vague terms ("fast", "real-time") |
| Quality gate | BDD-Ready score ≥ threshold (default 90) |

**Tier 2 — advisory (warning):** frontmatter metadata (below); single `@prd:` in
Document Control; cumulative `@brd`/`@prd` tags pipe-separated, no ranges,
correct prefixes; `@threshold:` tags well-formed; internal links and
template/governance references resolve; no downstream numbers cited before they
exist; diagram tags present where state/sequence diagrams apply (use
`../charts-flow/SKILL.md`).

**Combined status:** `PASS` only if all Tier 1 pass **and** content score ≥
threshold **and** no blocking issues; otherwise `FAIL`.

## Metadata Checks

| Field | Required | Valid values |
|-------|----------|--------------|
| `document_type` | yes | `ears-document` (not `template`) |
| `artifact_type` | yes | `EARS` |
| `layer` | yes | `3` |
| `deliverable_type` | yes | `code`, `document`, `ux`, `risk`, `process` |

Findings: `VALID-M001` missing `deliverable_type`; `VALID-M002` invalid value;
`VALID-M003` `document_type` not `ears-document`.

## Combined Report Format

Output: `EARS-NN.A_audit_report_vNNN.md`, with sections — **Summary** (ID,
timestamp, overall status, structural status, content score) · **Score
Calculation** (`100 − deductions`, threshold compare) · **Metadata Findings** ·
**Structural Findings** · **Content Findings** (EARS syntax, atomicity, threshold
coverage) · **Traceability/Tag Findings** · **Fix Queue** (`auto_fixable` /
`manual_required` / `blocked`) · **Recommended Next Step** · **Cleanup Summary**.

## Hand-off to doc-ears-fixer

Normalize every finding to: `source` (`structural`|`content`), `code`,
`severity` (`error`|`warning`|`info`), `file`, `section`, `action_hint`,
`confidence` (`auto-safe`|`auto-assisted`|`manual-required`). `doc-ears-fixer`
consumes the latest `EARS-NN.A_audit_report_vNNN.md`.

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

- Create: `../doc-ears/SKILL.md` · Fix: `../doc-ears-fixer/SKILL.md` · Generate:
  `../doc-ears-autopilot/SKILL.md`
- Authority: `framework/layers/03_EARS/README.md`,
  `framework/layers/03_EARS/EARS-TEMPLATE.yaml`,
  `framework/governance/ID_NAMING_STANDARDS.md`
