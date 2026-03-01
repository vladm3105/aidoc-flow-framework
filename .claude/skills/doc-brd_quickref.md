# doc-brd* Skills Quick Reference

## Core Positioning (2-Skill Model)

- `doc-brd` = **root/shared BRD contract** (authoring rules, section semantics, template compliance)
- `doc-brd-autopilot` = **primary execution pipeline** (generation + audit/fix orchestration)
- `doc-brd-audit` = **unified quality gate** (all validation + scoring, runs FROM SCRATCH)
- `doc-brd-fixer` = **issue remediation** from audit reports

**Deprecated** (merged into `doc-brd-audit`):
- `doc-brd-validator` - DEPRECATED
- `doc-brd-reviewer` - DEPRECATED

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
| Apply fixable findings | `doc-brd-fixer` |

## Fresh Audit Policy (MANDATORY)

**ALWAYS run audits from scratch:**
- Do NOT reference previous audit reports
- Re-compute PRD-ready score independently each time

## Standard Validation Loop

1. Run `/doc-brd-audit BRD-NN` (FROM SCRATCH).
2. If FAIL, run `/doc-brd-fixer BRD-NN`.
3. Re-run `/doc-brd-audit BRD-NN` (FROM SCRATCH).
4. Stop on PASS or manual-only findings.

## Fast Commands

```bash
/doc-brd                          # Root rules/manual authoring
/doc-brd-autopilot BRD-04         # Full orchestration
/doc-brd-audit BRD-04             # Single audit
/doc-brd-fixer BRD-04             # Apply fixes
```

## Pass/Fail Gate

- PASS: score >= 90 and no blocking structural errors
- FAIL: score < 90 or structural gate fails

## Source of Truth

- Template: `ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md`
- Validation policy: `ai_dev_ssd_flow/01_BRD/BRD_MVP_VALIDATION_RULES.md`
- Wrapper/quality workflow: `ai_dev_ssd_flow/01_BRD/BRD_QUALITY_GATE_WORKFLOW.md`

---

*Version: 2.2 | Updated: 2026-03-01*
