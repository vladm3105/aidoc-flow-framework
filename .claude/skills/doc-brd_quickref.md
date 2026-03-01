# doc-brd* Skills Quick Reference

## Core Positioning

- `doc-brd` = **root/shared BRD contract** (authoring rules, section semantics, template compliance)
- `doc-brd-autopilot` = **primary execution pipeline** (generation + validation/review/fix orchestration)
- `doc-brd-audit` = unified quality gate (`validator` + `reviewer`)
- `doc-brd-fixer` = issue remediation from audit/review reports
- `doc-brd-validator` = structural/schema gate
- `doc-brd-reviewer` = semantic/content quality gate

## Location Policy

- This framework BRD skill family is intended for many downstream projects.
- Canonical skill/docs home: `docs_flow_framework/.claude/skills/`
- Project repositories consume `doc-brd*` skills via symlinks only.

## When to Use Which Skill

| Goal | Skill |
| --- | --- |
| Manual BRD authoring / root guidance | `doc-brd` |
| End-to-end automated BRD processing | `doc-brd-autopilot` |
| One-command quality assessment | `doc-brd-audit` |
| Structural conformance only | `doc-brd-validator` |
| Content quality only | `doc-brd-reviewer` |
| Apply fixable findings | `doc-brd-fixer` |

## Standard Validation Loop

1. Run `/doc-brd-audit BRD-NN`.
2. If FAIL, run `/doc-brd-fixer BRD-NN --revalidate`.
3. Re-run `/doc-brd-audit BRD-NN`.
4. Stop on PASS or manual-only findings.

## Fast Commands

```bash
/doc-brd
/doc-brd-autopilot BRD-04
/doc-brd-audit BRD-04
/doc-brd-fixer BRD-04 --revalidate
/doc-brd-validator BRD-04
/doc-brd-reviewer BRD-04
```

## Pass/Fail Gate

- PASS: score >= 90 and no blocking structural errors
- FAIL: score < 90 or structural gate fails

## Source of Truth

- Template: `ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md`
- Validation policy: `ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md`
- Wrapper/quality workflow: `ai_dev_ssd_flow/01_BRD/BRD_QUALITY_GATE_WORKFLOW.md`
