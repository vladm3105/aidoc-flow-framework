---
name: doc-iplan-audit
description: Audit an IPLAN - run declarative structural checks plus content review and produce a combined report for doc-iplan-fixer. Use for IPLAN quality gating before code implementation.
metadata:
  tags:
    - sdd-workflow
    - layer-8-artifact
    - quality-assurance
  custom_fields:
    layer: 8
    artifact_type: IPLAN
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD]
    downstream_artifacts: [CODE]
    version: "0.6.1"
    framework_spec_version: "0.13.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold]
---

# doc-iplan-audit

## Purpose

Run a **unified IPLAN audit** — declarative structural checks plus
content-quality review — in one pass, producing a single combined report that
`../doc-iplan-fixer/SKILL.md` consumes. The framework ships no runtime code, so
**this skill is the validator**: Claude performs each check directly against the
IPLAN using the spec as the contract.

**Layer**: 8 (IPLAN quality gate). **Upstream**: an IPLAN file. **Downstream**:
`IPLAN-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after an IPLAN exists and before code implementation begins, or inside the
autopilot's audit↔fix cycle. Do **not** use to create an IPLAN (use
`../doc-iplan/SKILL.md` or `../doc-iplan-autopilot/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior scores or
cached results; compute the CODE-Ready score independently each run.

**Report cleanup:** after writing the new report, delete superseded
`IPLAN-NN.A_audit_report_v*.md`; keep `IPLAN-NN.F_fix_report_v*.md` and
`.drift_cache.json`. Record a cleanup summary in the report.

## Execution Contract

**Input:** IPLAN path (`docs/08_IPLAN/IPLAN-NN_*.yaml`); optional score
threshold (default 90).

**Sequence:** 1) run structural checks → 2) record findings → 3) run content
review → 4) merge/normalize findings → 5) write
`IPLAN-NN.A_audit_report_vNNN.md` → 6) if auto-fixable findings exist, hand off
to `doc-iplan-fixer`.

## Structural Checklist

Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/README.md`,
`${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`, and
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`. Style:
`${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md`.

**Template-conformance enumeration (mandatory first step).** Load
`IPLAN-TEMPLATE.yaml` and enumerate every required section (each top-level YAML
key that is not explicitly `required: false`). The Structure check below is
satisfied **only** when every enumerated required section appears as a `##`
heading in the artifact. Any missing required section is a **blocking finding**
— never rationalise it as a "compact" variant, "documented walkthrough",
"lint-pinned", or any other exception. There is one template per layer and one
canonical required-section set.

**Tier 1 — blocking (error):**

| Check | Verifies |
|-------|----------|
| Document ID format | IPLAN referenced as `IPLAN-NN` (dash form); no dotted `IPLAN.NN.SS.xxxx`; `@tdd` uses `TDD.NN.SS.xxxx`, `@spec` uses `SPEC-NN` |
| Structure | every section enumerated above is present and non-empty |
| Test-first order | `file_manifest` lists tests before implementation files |
| Session handoff | `session_handoff.sessions` present with a `next_session_directive` |
| Upstream references | parent SPEC/TDD references resolve to existing docs |
| Quality gate | CODE-Ready score ≥ threshold (default 90) |

**Tier 2 — advisory (warning):** frontmatter metadata (below); execution
commands cover setup/implementation/validation; implementation contracts present
when 3+ files share interfaces; `code_inventory` populated for each
created/modified file; `validation_results` recorded per session; internal links
and template/governance references resolve; permanent plan registered in
`IPLAN-00_index.yaml`; any dependency diagram uses `../charts-flow/SKILL.md`.

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
| `document_type` | yes | `iplan-document` (not `template`) |
| `artifact_type` | yes | `IPLAN` |
| `layer` | yes | `8` |
| `iplan_id` | yes | `IPLAN-NN` |
| `source_spec` | yes | `@spec: SPEC-NN` |

Findings: `VALID-M001` missing `iplan_id`/`source_spec`; `VALID-M002` invalid
value; `VALID-M003` `document_type` not `iplan-document`.

## Combined Report Format

Output: `IPLAN-NN.A_audit_report_vNNN.md`, with sections — **Summary** (ID,
timestamp, overall status, structural status, content score) · **Score
Calculation** (`100 − deductions`, threshold compare) · **Metadata Findings** ·
**Structural Findings** · **Content Findings** · **Manifest & Handoff Findings**
· **Fix Queue** (`auto_fixable` / `manual_required` / `blocked`) ·
**Recommended Next Step** · **Cleanup Summary**.

## Hand-off to doc-iplan-fixer

Normalize every finding to: `source` (`structural`|`content`), `code`,
`severity` (`error`|`warning`|`info`), `file`, `section`, `action_hint`,
`confidence` (`auto-safe`|`auto-assisted`|`manual-required`). `doc-iplan-fixer`
consumes the latest `IPLAN-NN.A_audit_report_vNNN.md`.

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

- Create: `../doc-iplan/SKILL.md` · Fix: `../doc-iplan-fixer/SKILL.md` ·
  Generate: `../doc-iplan-autopilot/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
