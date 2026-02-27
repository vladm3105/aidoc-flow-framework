---
name: doc-tspec-audit
description: Unified TSPEC audit wrapper that runs validator then reviewer and produces a combined report for fixer consumption

metadata:
  tags:
    - sdd-workflow
    - quality-assurance
    - tspec-audit
    - layer-10-artifact
    - shared-architecture
  custom_fields:
    layer: 10
    artifact_type: TSPEC
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [TSPEC]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks TSPEC-MVP-TEMPLATE schema_version"

---

# doc-tspec-audit

## Purpose

Run a **single TSPEC audit workflow** that executes:

1. `doc-tspec-validator` (structural/schema gate)
2. `doc-tspec-reviewer` (semantic/content quality gate)

Then emit one **combined report** optimized for `doc-tspec-fixer` input.

**Layer**: 10 (TSPEC Quality Gate Wrapper)

**Upstream**: TSPEC file(s)

**Downstream**:
- Combined Audit Report: `TSPEC-NN.A_audit_report_vNNN.md`
- Optional Fix Cycle trigger for `doc-tspec-fixer`

---

## Why This Skill Exists

Use this wrapper to avoid user confusion between validator and reviewer while preserving separation of concerns.

| Concern | Owner Skill |
|---------|-------------|
| Schema/template compliance | `doc-tspec-validator` |
| Content quality and implementation readiness | `doc-tspec-reviewer` |
| Single user-facing audit command | `doc-tspec-audit` |

---

## When to Use

Use `doc-tspec-audit` when:
- You want one command for TSPEC quality checks
- You need a combined report for `doc-tspec-fixer`
- You are running QA before TASKS generation

Do NOT use when:
- TSPEC does not exist (use `doc-tspec` / `doc-tspec-autopilot` generation first)
- You only need one specific check domain (use validator or reviewer directly)

---

## Execution Contract

### Input
- TSPEC path (`docs/10_TSPEC/{TYPE}/{TYPE}-NN_*/...`)
- Optional: threshold (default review threshold: 90)

### Sequence (Mandatory)

```text
1) Run doc-tspec-validator
2) Run doc-tspec-reviewer
3) Normalize and merge findings
4) Write TSPEC-NN.A_audit_report_vNNN.md
5) If auto-fixable findings exist, hand off to doc-tspec-fixer
```

### Combined Status Rules

- `PASS`: Validator PASS AND Reviewer score >= threshold AND no blocking issues
- `FAIL`: Validator FAIL OR Reviewer score < threshold OR blocking/manual-required issues present

---

## Combined Report Format (for doc-tspec-fixer)

Output file: `TSPEC-NN.A_audit_report_vNNN.md`

Required sections:

1. `## Summary`
   - TSPEC ID, timestamp (EST), overall status
   - Validator status, reviewer score
2. `## Score Calculation (Deduction-Based)`
   - Formula: `100 - total_deductions`
   - Threshold comparison (`>=90` pass gate)
3. `## Validator Findings`
   - List by severity/code
4. `## Reviewer Findings`
   - List by severity/code
5. `## Coverage Findings`
   - Test-type coverage summary (UTEST/ITEST/STEST/FTEST/PTEST/SECTEST)
   - Traceability/tag coverage summary
   - SPEC alignment and edge-case coverage summary
6. `## Fix Queue for doc-tspec-fixer`
   - `auto_fixable`
   - `manual_required`
   - `blocked`
7. `## Recommended Next Step`
   - `run doc-tspec-fixer`
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

## Hand-off Contract to doc-tspec-fixer

`doc-tspec-fixer` MUST accept combined audit report as equivalent upstream input:
- `TSPEC-NN.A_audit_report_vNNN.md` (preferred)
- `TSPEC-NN.R_review_report_vNNN.md` (legacy compatibility)

Precedence rule:
1. Select newest timestamp.
2. If timestamps are equal, prefer `.A_audit_report` over `.R_review_report`.

---

## Example Invocation

```bash
/doc-tspec-audit docs/10_TSPEC/UTEST/UTEST-01_auth_service/UTEST-01_auth_service.md
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
| 1.0 | 2026-02-27 | Initial TSPEC audit wrapper; validator→reviewer orchestration; combined report contract for fixer with `.A_` preferred and `.R_` legacy compatibility |
