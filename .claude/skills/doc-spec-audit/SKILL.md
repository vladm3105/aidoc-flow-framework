---
name: doc-spec-audit
description: Unified SPEC audit wrapper that runs validator then reviewer and produces a combined report for fixer consumption

metadata:
  tags:
    - sdd-workflow
    - quality-assurance
    - spec-audit
    - layer-9-artifact
    - shared-architecture
  custom_fields:
    layer: 9
    artifact_type: SPEC
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SPEC]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks SPEC-MVP-TEMPLATE schema_version"

---

# doc-spec-audit

## Purpose

Run a **single SPEC audit workflow** that executes:

1. `doc-spec-validator` (structural/schema gate)
2. `doc-spec-reviewer` (semantic/content quality gate)

Then emit one **combined report** optimized for `doc-spec-fixer` input.

**Layer**: 9 (SPEC Quality Gate Wrapper)

**Upstream**: SPEC file(s)

**Downstream**:
- Combined Audit Report: `SPEC-NN.A_audit_report_vNNN.md`
- Optional Fix Cycle trigger for `doc-spec-fixer`

---

## Why This Skill Exists

Use this wrapper to avoid user confusion between validator and reviewer while preserving separation of concerns.

| Concern | Owner Skill |
|---------|-------------|
| Schema/template compliance | `doc-spec-validator` |
| Content quality and implementation readiness | `doc-spec-reviewer` |
| Single user-facing audit command | `doc-spec-audit` |

---

## When to Use

Use `doc-spec-audit` when:
- You want one command for SPEC quality checks
- You need a combined report for `doc-spec-fixer`
- You are running QA before TSPEC/TASKS generation

Do NOT use when:
- SPEC does not exist (use `doc-spec` / `doc-spec-autopilot` generation first)
- You only need one specific check domain (use validator or reviewer directly)

---

## Execution Contract

### Input
- SPEC path (`docs/09_SPEC/SPEC-NN_*/...`)
- Optional: threshold (default review threshold: 90)

### Sequence (Mandatory)

```text
1) Run doc-spec-validator
2) Run doc-spec-reviewer
3) Normalize and merge findings
4) Write SPEC-NN.A_audit_report_vNNN.md
5) If auto-fixable findings exist, hand off to doc-spec-fixer
```

### Combined Status Rules

- `PASS`: Validator PASS AND Reviewer score >= threshold AND no blocking issues
- `FAIL`: Validator FAIL OR Reviewer score < threshold OR blocking/manual-required issues present

---

## Combined Report Format (for doc-spec-fixer)

Output file: `SPEC-NN.A_audit_report_vNNN.md`

Required sections:

1. `## Summary`
   - SPEC ID, timestamp (EST), overall status
   - Validator status, reviewer score
2. `## Score Calculation (Deduction-Based)`
   - Formula: `100 - total_deductions`
   - Threshold comparison (`>=90` pass gate)
3. `## Validator Findings`
   - List by severity/code
4. `## Reviewer Findings`
   - List by severity/code
5. `## Coverage Findings`
   - Requirement implementation coverage summary
   - Traceability/tag coverage summary
   - Interface and error-handling coverage summary
6. `## Fix Queue for doc-spec-fixer`
   - `auto_fixable`
   - `manual_required`
   - `blocked`
7. `## Recommended Next Step`
   - `run doc-spec-fixer`
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

## Hand-off Contract to doc-spec-fixer

`doc-spec-fixer` MUST accept combined audit report as equivalent upstream input:
- `SPEC-NN.A_audit_report_vNNN.md` (preferred)
- `SPEC-NN.R_review_report_vNNN.md` (legacy compatibility)

Precedence rule:
1. Select newest timestamp.
2. If timestamps are equal, prefer `.A_audit_report` over `.R_review_report`.

---

## Example Invocation

```bash
/doc-spec-audit docs/09_SPEC/SPEC-01_f1_iam/
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
| 1.0 | 2026-02-27 | Initial SPEC audit wrapper; validator→reviewer orchestration; combined report contract for fixer with `.A_` preferred and `.R_` legacy compatibility |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

