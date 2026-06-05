---
name: doc-spec-audit
description: Audit a SPEC - run declarative structural checks plus content review and produce a combined report for doc-spec-fixer. Use for SPEC quality gating before TDD.
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN]
    version: "0.5.0"
    framework_spec_version: "0.12.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold]
---

# doc-spec-audit

## Purpose

Run a **unified SPEC audit** — declarative structural checks plus content-quality
review — in one pass, producing a single combined report that
`../doc-spec-fixer/SKILL.md` consumes. The framework ships no runtime code, so
**this skill is the validator**: Claude performs each check directly against the
SPEC using the spec as the contract.

**Layer**: 6 (SPEC quality gate). **Upstream**: a SPEC file. **Downstream**:
`SPEC-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after a SPEC exists and before generating the TDD, or inside the autopilot's
audit↔fix cycle. Do **not** use to create a SPEC (use `../doc-spec/SKILL.md` or
`../doc-spec-autopilot/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior scores or
cached results; compute the TDD-Ready score independently each run.

**Report cleanup:** after writing the new report, delete superseded
`SPEC-NN.A_audit_report_v*.md`; keep `SPEC-NN.F_fix_report_v*.md` and
`.drift_cache.json`. Record a cleanup summary in the report.

## Execution Contract

**Input:** SPEC path (`docs/06_SPEC/SPEC-NN_*/...`); optional score threshold
(default 90).

**Sequence:** 1) run structural checks → 2) record findings → 3) run content
review → 4) merge/normalize findings → 5) write `SPEC-NN.A_audit_report_vNNN.md`
→ 6) if auto-fixable findings exist, hand off to `doc-spec-fixer`.

## Structural Checklist

Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/README.md`,
`${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` (embedded rules), and
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`. Style:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`.

**Template-conformance enumeration (mandatory first step).** Load
`SPEC-TEMPLATE.yaml` and enumerate every required section (each top-level YAML
key that is not explicitly `required: false`). The Structure check below is
satisfied **only** when every enumerated required section appears as a `##`
heading in the artifact. Any missing required section is a **blocking finding**
— never rationalise it as a "compact" variant, "documented walkthrough",
"lint-pinned", or any other exception. There is one template per layer and one
canonical required-section set.

**Tier 1 — blocking (error):**

| Check | Verifies |
|-------|----------|
| YAML syntax | the SPEC parses as valid YAML |
| Document ID | dash form `SPEC-NN`; no dotted SPEC element IDs; no removed patterns |
| Structure | every section enumerated above is present and non-empty |
| Cumulative tags | upstream chain complete (`@brd @prd @ears @bdd @adr`); no gaps |
| Quality gate | TDD-Ready score ≥ threshold (default 90) |

**Tier 2 — advisory (warning):** frontmatter metadata (below); C4-L3 scope holds
(interfaces/data/behavior only, no code/SQL/deployment detail); internal links
and template/governance references resolve; quantitative values use `@threshold:`
references; downstream `@tdd: TDD-NN` contract present; diagram contract tags
present (`@diagram: c4-l3`, `@diagram: dfd-l3` — use `../charts-flow/SKILL.md`).

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
| `document_type` | yes | `spec-document` (not `template`) |
| `artifact_type` | yes | `SPEC` |
| `layer` | yes | `6` |
| `deliverable_type` | yes | `code`, `document`, `ux`, `risk`, `process` |

Findings: `VALID-M001` missing `deliverable_type`; `VALID-M002` invalid value;
`VALID-M003` `document_type` not `spec-document`.

## Combined Report Format

Output: `SPEC-NN.A_audit_report_vNNN.md`, with sections — **Summary** (ID,
timestamp, overall status, structural status, content score) · **Score
Calculation** (`100 − deductions`, threshold compare) · **Metadata Findings** ·
**Structural Findings** · **Content Findings** (interface/data-model/behavior
coverage, cumulative-tag coverage) · **Diagram Contract Findings** · **Fix
Queue** (`auto_fixable` / `manual_required` / `blocked`) · **Recommended Next
Step** · **Cleanup Summary**.

## Hand-off to doc-spec-fixer

Normalize every finding to: `source` (`structural`|`content`), `code`,
`severity` (`error`|`warning`|`info`), `file`, `section`, `action_hint`,
`confidence` (`auto-safe`|`auto-assisted`|`manual-required`). `doc-spec-fixer`
consumes the latest `SPEC-NN.A_audit_report_vNNN.md`.

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

- Create: `../doc-spec/SKILL.md` · Fix: `../doc-spec-fixer/SKILL.md` · Generate:
  `../doc-spec-autopilot/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
