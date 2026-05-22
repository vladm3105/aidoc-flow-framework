# BRD Skills Quick README

## Scope

This guide defines the minimum command flow for BRD quality operations.

## Location Policy

- This framework BRD skill set is designed for reuse across multiple projects.
- Canonical location for `doc-brd*` skills and docs: the plugin's `skills/` directory (sibling skills referenced as `../doc-X/`).
- Downstream projects should reference these via the installed plugin.
- Keep the `framework/` spec as single source of truth for templates and standards.

## Core Model (2-Skill Quality Pipeline)

- `doc-brd` is the **root/shared BRD contract skill** (rules, structure, template semantics).
- `doc-brd-autopilot` is the **primary execution/orchestration skill**.
- `doc-brd-audit` is the **unified quality gate** (all validation + scoring, runs FROM SCRATCH).
- `doc-brd-fixer` is the **issue remediation skill** (applies fixes from audit report).

## Skills

| Skill | Purpose |
|-------|---------|
| `doc-brd` | Root/shared BRD creation contract used by other `doc-brd*` skills |
| `doc-brd-autopilot` | Orchestrates audit/fix loop for a BRD target |
| `doc-brd-audit` | All validation + scoring (runs FROM SCRATCH per Fresh Audit Policy) |
| `doc-brd-fixer` | Applies auto-fixable items from latest audit report |

## Deprecated Skills

| Skill | Status | Replacement |
|-------|--------|-------------|
| `doc-brd-validator` | DEPRECATED | Merged into `doc-brd-audit` |
| `doc-brd-reviewer` | DEPRECATED | Merged into `doc-brd-audit` |

## Binary Score Gate

- PASS: score >= 90
- FAIL: score < 90

No score warning band is used.

## Fresh Audit Policy (MANDATORY)

**ALWAYS run audits from scratch:**
- Do NOT reference previous audit reports for scoring decisions
- Do NOT skip validation steps based on drift cache history
- Re-compute PRD-ready score independently each time
- Generate a new audit report with incremented version

## Default Execution Order

1. Run `doc-brd-audit` (FROM SCRATCH).
2. If FAIL, run `doc-brd-fixer`.
3. Run `doc-brd-audit` again (FROM SCRATCH).
4. Repeat until PASS or manual-only items remain.

## Standard Outputs

- Audit: `BRD-NN.A_audit_report_vNNN.md`
- Fix: `BRD-NN.F_fix_report_vNNN.md`
- Drift cache: `.drift_cache.json`

**Legacy (historical only):**
- Review: `BRD-NN.R_review_report_vNNN.md` (doc-brd-reviewer - deprecated)
- Validation: `BRD-NN.V_validation_report_vNNN.md` (doc-brd-validator - deprecated)

## Fast Start

- Root rules/manual authoring: `/doc-brd`
- Single BRD audit: `/doc-brd-audit BRD-04`
- Fix + re-audit cycle: `/doc-brd-fixer BRD-04` then `/doc-brd-audit BRD-04`
- Full orchestration: `/doc-brd-autopilot BRD-04`

## Decision Rules

- If structural validation fails, status is FAIL regardless of score.
- If score < 90, status is FAIL.
- If manual-required items remain, route to manual update.

## Source of Truth

- Template structure: `framework/layers/01_BRD/BRD-TEMPLATE.yaml`
- BRD README: `framework/layers/01_BRD/README.md`
- ID & tag standards: `framework/governance/ID_NAMING_STANDARDS.md`

---

*Version: 2.3 | Updated: 2026-05-22*
