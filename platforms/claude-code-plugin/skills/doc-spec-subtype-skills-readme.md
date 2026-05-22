# SPEC Subtype Skills Index

## Overview

This index documents the specialized skills for each SPEC subtype. SPEC (Layer 6) serves as an orchestrator that routes to subtypes based on `deliverable_type`. The subtypes are plugin-only authoring helpers under the SPEC layer — each references (does not redefine) the single `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` template.

## Subtype Skills Matrix

| Subtype | deliverable_type | Skills |
|---------|------------------|--------|
| **CSPEC** | `code` | autopilot, validator, reviewer, fixer, audit |
| **DSPEC** | `document` | autopilot, validator, reviewer, fixer, audit |
| **UXSPEC** | `ux` | autopilot, validator, reviewer, fixer, audit |
| **RISKSPEC** | `risk` | autopilot, validator, reviewer, fixer, audit |
| **PROCSPEC** | `process` | autopilot, validator, reviewer, fixer, audit |

## Skill Types

### Autopilot Skills
Generate subtype documents from upstream ADR/BDD/EARS.

| Skill | Description |
|-------|-------------|
| `doc-cspec-autopilot` | Code specifications for source code |
| `doc-dspec-autopilot` | Documentation specifications |
| `doc-uxspec-autopilot` | UX specifications for wireframes/mockups |
| `doc-riskspec-autopilot` | Risk specifications for risk matrices |
| `doc-procspec-autopilot` | Process specifications for SOPs/runbooks |

### Validator Skills
Validate documents against schema standards.

| Skill | Description |
|-------|-------------|
| `doc-cspec-validator` | Validate against CSPEC schema |
| `doc-dspec-validator` | Validate against DSPEC schema |
| `doc-uxspec-validator` | Validate against UXSPEC schema |
| `doc-riskspec-validator` | Validate against RISKSPEC schema |
| `doc-procspec-validator` | Validate against PROCSPEC schema |

### Reviewer Skills
Comprehensive content review and quality assurance.

| Skill | Description |
|-------|-------------|
| `doc-cspec-reviewer` | Review code specifications |
| `doc-dspec-reviewer` | Review documentation specifications |
| `doc-uxspec-reviewer` | Review UX specifications |
| `doc-riskspec-reviewer` | Review risk specifications |
| `doc-procspec-reviewer` | Review process specifications |

### Fixer Skills
Apply automated fixes from review reports.

| Skill | Description |
|-------|-------------|
| `doc-cspec-fixer` | Fix CSPEC issues |
| `doc-dspec-fixer` | Fix DSPEC issues |
| `doc-uxspec-fixer` | Fix UXSPEC issues |
| `doc-riskspec-fixer` | Fix RISKSPEC issues |
| `doc-procspec-fixer` | Fix PROCSPEC issues |

### Audit Skills
Unified quality gates with readiness scoring.

| Skill | Readiness Score | Target |
|-------|-----------------|--------|
| `doc-cspec-audit` | CODE-Ready | ≥90% |
| `doc-dspec-audit` | DOC-Ready | ≥85% |
| `doc-uxspec-audit` | DESIGN-Ready | ≥85% |
| `doc-riskspec-audit` | RISK-Ready | ≥85% |
| `doc-procspec-audit` | PROC-Ready | ≥85% |

## Readiness Thresholds

| Subtype | Score Name | Pass | Conditional | Fail |
|---------|------------|------|-------------|------|
| CSPEC | CODE-Ready | ≥90% | 80-89% | <80% |
| DSPEC | DOC-Ready | ≥85% | 75-84% | <75% |
| UXSPEC | DESIGN-Ready | ≥85% | 75-84% | <75% |
| RISKSPEC | RISK-Ready | ≥85% | 75-84% | <75% |
| PROCSPEC | PROC-Ready | ≥85% | 75-84% | <75% |

## Workflow Integration

```
ADR (with deliverable_type)
    ↓
SPEC Orchestrator (routes based on deliverable_type)
    ↓
┌─────────────────────────────────────────────────┐
│ CSPEC │ DSPEC │ UXSPEC │ RISKSPEC │ PROCSPEC │
└─────────────────────────────────────────────────┘
    ↓
Per-Subtype Workflow:
    autopilot → validator → reviewer → fixer → audit
    ↓
TDD / IPLAN
```

## References

- SPEC Parent Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- SPEC README: `framework/layers/06_SPEC/README.md`
- ID & Tag Standards: `framework/governance/ID_NAMING_STANDARDS.md`

---

**Version**: 2.0
**Last Updated**: 2026-05-22
