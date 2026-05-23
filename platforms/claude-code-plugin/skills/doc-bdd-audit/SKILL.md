---
name: doc-bdd-audit
description: Audit a BDD suite - run declarative structural checks plus content review and produce a combined report for doc-bdd-fixer. Use for BDD quality gating before ADR.
metadata:
  tags:
    - sdd-workflow
    - layer-4-artifact
    - quality-assurance
  custom_fields:
    layer: 4
    artifact_type: BDD
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS]
    downstream_artifacts: [ADR, SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.1.0"
    last_updated: "2026-05-23"
---

# doc-bdd-audit

## Purpose

Run a **unified BDD audit** — declarative structural checks plus content-quality
review — in one pass, producing a single combined report that
`../doc-bdd-fixer/SKILL.md` consumes. The framework ships no runtime code, so
**this skill is the validator**: Claude performs each check directly against the
BDD suite using the spec as the contract.

**Layer**: 4 (BDD quality gate). **Upstream**: a BDD file. **Downstream**:
`BDD-NN.A_audit_report_vNNN.md` and an optional fix-cycle trigger.

## When to Use

Use after a BDD suite exists and before generating the ADR, or inside the
autopilot's audit↔fix cycle. Do **not** use to create a BDD (use
`../doc-bdd/SKILL.md` or `../doc-bdd-autopilot/SKILL.md`).

**Fresh-audit policy:** always audit from scratch — never reuse prior scores or
cached results; compute the ADR-Ready score independently each run.

**Report cleanup:** after writing the new report, delete superseded
`BDD-NN.A_audit_report_v*.md`; keep `BDD-NN.F_fix_report_v*.md` and
`.drift_cache.json`. Record a cleanup summary in the report.

## Execution Contract

**Input:** BDD path (`docs/04_BDD/BDD-NN_*/...`); optional score threshold
(default 90).

**Sequence:** 1) run structural checks → 2) record findings → 3) run content
review → 4) merge/normalize findings → 5) write `BDD-NN.A_audit_report_vNNN.md`
→ 6) if auto-fixable findings exist, hand off to `doc-bdd-fixer`.

## Structural Checklist

Authority: `framework/layers/04_BDD/README.md`,
`framework/layers/04_BDD/BDD-TEMPLATE.yaml` (embedded rules + scenario
conventions), and `framework/governance/ID_NAMING_STANDARDS.md`.

**Tier 1 — blocking (error):**

| Check | Verifies |
|-------|----------|
| Element ID format | every ID matches `BDD.NN.SS.xxxx` (4-hex hash) |
| Structure | all 5 template sections present and non-empty |
| Gherkin quality | scenarios are atomic, executable, valid Given-When-Then |
| Cumulative tags | `@brd @prd @ears` present, Gherkin-native, no space after colon |
| Scenario tags | each scenario has `@scenario-type`, priority, `@scenario-id`, `spec_trace` |
| Thresholds | quantitative values use `@threshold:` keys (no magic numbers) |
| Quality gate | ADR-Ready score ≥ threshold (default 90) |

**Tier 2 — advisory (warning):** frontmatter metadata (below); internal links
and template/governance references resolve; no downstream numbers cited before
they exist; five scenario categories represented; times `HH:MM:SS` with IANA
timezones; sequence-diagram tag present if a flow is illustrated (use
`../charts-flow/SKILL.md`).

**Combined status:** `PASS` only if all Tier 1 pass **and** content score ≥
threshold **and** no blocking issues; otherwise `FAIL`.

## Metadata Checks

| Field | Required | Valid values |
|-------|----------|--------------|
| `document_type` | yes | `bdd-document` (not `template`) |
| `artifact_type` | yes | `BDD` |
| `layer` | yes | `4` |
| `deliverable_type` | yes | `code`, `document`, `ux`, `risk`, `process` |

Findings: `VALID-M001` missing `deliverable_type`; `VALID-M002` invalid value;
`VALID-M003` `document_type` not `bdd-document`.

## Combined Report Format

Output: `BDD-NN.A_audit_report_vNNN.md`, with sections — **Summary** (ID,
timestamp, overall status, structural status, content score) · **Score
Calculation** (`100 − deductions`, threshold compare) · **Metadata Findings** ·
**Structural Findings** · **Content Findings** · **Coverage Findings** (Gherkin
syntax, five-category coverage, cumulative-tag coverage, `spec_trace` presence) ·
**Fix Queue** (`auto_fixable` / `manual_required` / `blocked`) · **Recommended
Next Step** · **Cleanup Summary**.

## Hand-off to doc-bdd-fixer

Normalize every finding to: `source` (`structural`|`content`), `code`,
`severity` (`error`|`warning`|`info`), `file`, `section`, `action_hint`,
`confidence` (`auto-safe`|`auto-assisted`|`manual-required`). `doc-bdd-fixer`
consumes the latest `BDD-NN.A_audit_report_vNNN.md`.

## Related Resources

- Create: `../doc-bdd/SKILL.md` · Fix: `../doc-bdd-fixer/SKILL.md` · Generate:
  `../doc-bdd-autopilot/SKILL.md`
- Authority: `framework/layers/04_BDD/README.md`,
  `framework/layers/04_BDD/BDD-TEMPLATE.yaml`,
  `framework/governance/ID_NAMING_STANDARDS.md`
