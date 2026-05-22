---
name: doc-adr-audit
description: Unified ADR audit wrapper that runs validator then reviewer and produces a combined report for fixer consumption

metadata:
  tags:
    - sdd-workflow
    - quality-assurance
    - adr-audit
    - layer-5-artifact
    - shared-architecture
  custom_fields:
    layer: 5
    artifact_type: ADR
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [ADR]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.1"
    last_updated: "2026-05-22"
  versioning_policy: "tracks ADR-TEMPLATE schema_version"

---

# doc-adr-audit

## Purpose

Run a **single ADR audit workflow** that executes:

1. `doc-adr-validator` (structural/schema gate)
2. `doc-adr-reviewer` (semantic/content quality gate)

Then emit one **combined report** optimized for `doc-adr-fixer` input.

**Layer**: 5 (ADR Quality Gate Wrapper)

**Upstream**: ADR file(s)

**Downstream**:
- Combined Audit Report: `ADR-NN.A_audit_report_vNNN.md`
- Optional Fix Cycle trigger for `doc-adr-fixer`

---

## Why This Skill Exists

Use this wrapper to avoid user confusion between validator and reviewer while preserving separation of concerns.

| Concern | Owner Skill |
|---------|-------------|
| Schema/template compliance | `doc-adr-validator` |
| Content quality and decision completeness | `doc-adr-reviewer` |
| Single user-facing audit command | `doc-adr-audit` |

---

## When to Use

Use `doc-adr-audit` when:
- You want one command for ADR quality checks
- You need a combined report for `doc-adr-fixer`
- You are running QA before SPEC generation

Do NOT use when:
- ADR does not exist (use `doc-adr` / `doc-adr-autopilot` generation first)
- You only need one specific check domain (use validator or reviewer directly)

---

## Execution Contract

### Input
- ADR path (`docs/05_ADR/ADR-NN_*/...`)
- Optional: threshold (default review threshold: 90)

### Sequence (Mandatory)

```text
1) Run doc-adr-validator
2) Run doc-adr-reviewer
3) Normalize and merge findings
4) Write ADR-NN.A_audit_report_vNNN.md
5) If auto-fixable findings exist, hand off to doc-adr-fixer
```

### Combined Status Rules

- `PASS`: Validator PASS AND Reviewer score >= threshold AND no blocking issues
- `FAIL`: Validator FAIL OR Reviewer score < threshold OR blocking/manual-required issues present

---

## Combined Report Format (for doc-adr-fixer)

Output file: `ADR-NN.A_audit_report_vNNN.md`

Required sections:

1. `## Summary`
   - ADR ID, timestamp (EST), overall status
   - Validator status, reviewer score
2. `## Score Calculation (Deduction-Based)`
   - Formula: `100 - total_deductions`
   - Threshold comparison (`>=90` pass gate)
3. `## Validator Findings`
   - List by severity/code
4. `## Reviewer Findings`
   - List by severity/code
5. `## Coverage Findings`
   - Decision completeness summary
   - Architecture flow/diagram coverage summary
   - Traceability/tag coverage summary
6. `## Fix Queue for doc-adr-fixer`
   - `auto_fixable`
   - `manual_required`
   - `blocked`
7. `## Recommended Next Step`
   - `run doc-adr-fixer`
   - or `manual update required`

### Fix Queue Normalization

Each finding MUST include:
- `source`: `validator` | `reviewer`
- `code`: issue code
- `severity`: `error|warning|info`
- `file`: relative path
- `section`: heading/anchor if known
- `action_hint`: short imperative guidance
- `confidence`: `high|medium|manual-required`

---

## Hand-off Contract to doc-adr-fixer

`doc-adr-fixer` MUST accept combined audit report as equivalent upstream input:
- `ADR-NN.A_audit_report_vNNN.md` (preferred)
- `ADR-NN.R_review_report_vNNN.md` (legacy compatibility)

Precedence rule:
1. Select newest timestamp.
2. If timestamps are equal, prefer `.A_audit_report` over `.R_review_report`.

---

## Example Invocation

```bash
/doc-adr-audit docs/05_ADR/ADR-01_f1_iam/
```

Expected outcome:
1. validator runs
2. reviewer runs
3. combined audit report generated
4. fixer can execute directly from combined report

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-05-22 | Migrated to the framework 8-layer model: ADR downstream gate is now SPEC (Layer 6), not SYS; tracks `ADR-TEMPLATE` schema version |
| 1.0 | 2026-02-27 | Initial ADR audit wrapper; validator→reviewer orchestration; combined report contract for fixer with `.A_` preferred and `.R_` legacy compatibility |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

