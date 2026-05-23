---
name: doc-adr-audit
description: Audit an ADR - run declarative structural checks plus content review and produce a combined report for doc-adr-fixer. Use for ADR quality gating before SPEC.
metadata:
  tags:
    - sdd-workflow
    - layer-5-artifact
    - quality-assurance
  custom_fields:
    layer: 5
    artifact_type: ADR
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD]
    downstream_artifacts: [SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.1.0"
    last_updated: "2026-05-23"
---

# doc-adr-audit

## Purpose

Run a **unified ADR audit** — declarative structural checks plus content-quality
review — in one pass, producing a single combined report that
`../doc-adr-fixer/SKILL.md` consumes. The framework ships no runtime code, so
**this skill is the validator**: Claude performs each check directly against the
ADR using the spec as the contract.

**Layer**: 5 (ADR quality gate). **Upstream**: an ADR file. **Downstream**:
`ADR-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after an ADR exists and before generating the SPEC, or inside the
autopilot's audit↔fix cycle. Do **not** use to create an ADR (use
`../doc-adr/SKILL.md` or `../doc-adr-autopilot/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior scores or
cached results; compute the SPEC-Ready score independently each run.

**Report cleanup:** after writing the new report, delete superseded
`ADR-NN.A_audit_report_v*.md`; keep `ADR-NN.F_fix_report_v*.md` and
`.drift_cache.json`. Record a cleanup summary in the report.

## Execution Contract

**Input:** ADR path (`docs/05_ADR/ADR-NN_*/...`); optional score threshold
(default 90).

**Sequence:** 1) run structural checks → 2) record findings → 3) run content
review → 4) merge/normalize findings → 5) write `ADR-NN.A_audit_report_vNNN.md`
→ 6) if auto-fixable findings exist, hand off to `doc-adr-fixer`.

## Structural Checklist

Authority: `framework/layers/05_ADR/README.md`,
`framework/layers/05_ADR/ADR-TEMPLATE.yaml` (embedded rules + `_antipatterns`),
and `framework/governance/ID_NAMING_STANDARDS.md`.

**Tier 1 — blocking (error):**

| Check | Verifies |
|-------|----------|
| Element ID format | every internal ID matches `ADR.NN.SS.xxxx` (4-hex hash); document refs use dash `ADR-NN` |
| Single decision | the ADR records exactly one decision |
| Structure | all 10 required sections present and non-empty |
| Cumulative tags | `@brd @prd @ears @bdd` all present and well-formed |
| Quality gate | SPEC-Ready score ≥ threshold (default 90) for Accepted status |

**Tier 2 — advisory (warning):** frontmatter metadata (below); alternatives
include 2–3 options with cost/fit and rejection reasons; consequences cover
trade-offs with severity; internal links and template/governance references
resolve; no downstream (SPEC/TDD/IPLAN) numbers cited before they exist;
architecture-flow diagram present (use `../charts-flow/SKILL.md`).

**Combined status:** `PASS` only if all Tier 1 pass **and** content score ≥
threshold **and** no blocking issues; otherwise `FAIL`.

## Metadata Checks

| Field | Required | Valid values |
|-------|----------|--------------|
| `document_type` | yes | `adr-document` (not `template`) |
| `artifact_type` | yes | `ADR` |
| `layer` | yes | `5` |
| `status` | yes | `Proposed`, `Accepted`, `Deprecated`, `Superseded` |
| `deliverable_type` | yes | `code`, `document`, `ux`, `risk`, `process` |

Findings: `VALID-M001` missing `deliverable_type`; `VALID-M002` invalid value;
`VALID-M003` `document_type` not `adr-document`; `VALID-M004` invalid `status`.

## Combined Report Format

Output: `ADR-NN.A_audit_report_vNNN.md`, with sections — **Summary** (ID,
timestamp, overall status, structural status, content score) · **Score
Calculation** (`100 − deductions`, threshold compare) · **Metadata Findings** ·
**Structural Findings** · **Content Findings** · **Diagram Contract Findings** ·
**Fix Queue** (`auto_fixable` / `manual_required` / `blocked`) · **Recommended
Next Step** · **Cleanup Summary**.

## Hand-off to doc-adr-fixer

Normalize every finding to: `source` (`structural`|`content`), `code`,
`severity` (`error`|`warning`|`info`), `file`, `section`, `action_hint`,
`confidence` (`auto-safe`|`auto-assisted`|`manual-required`). `doc-adr-fixer`
consumes the latest `ADR-NN.A_audit_report_vNNN.md`.

## Related Resources

- Create: `../doc-adr/SKILL.md` · Fix: `../doc-adr-fixer/SKILL.md` · Generate:
  `../doc-adr-autopilot/SKILL.md`
- Authority: `framework/layers/05_ADR/README.md`,
  `framework/layers/05_ADR/ADR-TEMPLATE.yaml`,
  `framework/governance/ID_NAMING_STANDARDS.md`
