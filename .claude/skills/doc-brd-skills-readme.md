# BRD Skills Quick README

## Scope

This guide defines the minimum command flow for BRD quality operations.

## Skills

- `doc-brd-validator`: Structural/schema checks.
- `doc-brd-reviewer`: PRD-ready score evaluation using deduction-based model.
- `doc-brd-audit`: Wrapper that runs validator + reviewer and writes combined audit report.
- `doc-brd-fixer`: Applies auto-fixable items from latest audit/review report.
- `doc-brd-autopilot`: Orchestrates review/fix loop for a BRD target.

## Binary Score Gate

- PASS: score >= 90
- FAIL: score < 90

No score warning band is used.

## Default Execution Order

1. Run `doc-brd-audit`.
2. If FAIL, run `doc-brd-fixer`.
3. Run `doc-brd-audit` again.
4. Repeat until PASS or manual-only items remain.

## Standard Outputs

- Audit: `BRD-NN.A_audit_report_vNNN.md`
- Review: `BRD-NN.R_review_report_vNNN.md`
- Fix: `BRD-NN.F_fix_report_vNNN.md`
- Drift cache: `.drift_cache.json`

## Fast Start

- Single BRD audit: `/doc-brd-audit BRD-04`
- Fix + re-audit cycle: `/doc-brd-fixer BRD-04` then `/doc-brd-audit BRD-04`
- Full orchestration: `/doc-brd-autopilot BRD-04`

## Decision Rules

- If validator fails, status is FAIL regardless of score.
- If score < 90, status is FAIL.
- If manual-required items remain, route to manual update.

## Source of Truth

- Template structure: `ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md`
- Scoring policy: `ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md`
