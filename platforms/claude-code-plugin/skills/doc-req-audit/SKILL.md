---
name: doc-req-audit
description: Unified REQ audit wrapper that runs validator then reviewer and produces a combined report for fixer consumption

metadata:
  tags:
    - sdd-workflow
    - quality-assurance
    - req-audit
    - layer-7-artifact
    - shared-architecture
  custom_fields:
    layer: 7
    artifact_type: REQ
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [REQ]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks REQ-MVP-TEMPLATE schema_version"

---

# doc-req-audit

## Purpose

Run a **single REQ audit workflow** that executes:

1. `doc-req-validator` (structural/schema gate)
2. `doc-req-reviewer` (semantic/content quality gate)

Then emit one **combined report** optimized for `doc-req-fixer` input.

**Layer**: 7 (REQ Quality Gate Wrapper)

**Upstream**: REQ file(s)

**Downstream**:
- Combined Audit Report: `REQ-NN.A_audit_report_vNNN.md`
- Optional Fix Cycle trigger for `doc-req-fixer`

---

## Why This Skill Exists

Use this wrapper to avoid user confusion between validator and reviewer while preserving separation of concerns.

| Concern | Owner Skill |
|---------|-------------|
| Schema/template compliance | `doc-req-validator` |
| Content quality and implementation readiness | `doc-req-reviewer` |
| Single user-facing audit command | `doc-req-audit` |

---

## When to Use

Use `doc-req-audit` when:
- You want one command for REQ quality checks
- You need a combined report for `doc-req-fixer`
- You are running QA before CTR/SPEC generation

Do NOT use when:
- REQ does not exist (use `doc-req` / `doc-req-autopilot` generation first)
- You only need one specific check domain (use validator or reviewer directly)

---

## Execution Contract

### Input
- REQ path (`docs/07_REQ/REQ-NN_*/...`)
- Optional: threshold (default review threshold: 90)

### Sequence (Mandatory)

```text
1) Run doc-req-validator
2) Run doc-req-reviewer
3) Normalize and merge findings
4) Write REQ-NN.A_audit_report_vNNN.md
5) If auto-fixable findings exist, hand off to doc-req-fixer
```

### Combined Status Rules

- `PASS`: Validator PASS AND Reviewer score >= threshold AND no blocking issues
- `FAIL`: Validator FAIL OR Reviewer score < threshold OR blocking/manual-required issues present

---

## Combined Report Format (for doc-req-fixer)

Output file: `REQ-NN.A_audit_report_vNNN.md`

Required sections:

1. `## Summary`
   - REQ ID, timestamp (EST), overall status
   - Validator status, reviewer score
2. `## Score Calculation (Deduction-Based)`
   - Formula: `100 - total_deductions`
   - Threshold comparison (`>=90` pass gate)
3. `## Validator Findings`
   - List by severity/code
4. `## Reviewer Findings`
   - List by severity/code
5. `## Coverage Findings`
   - Requirement completeness summary
   - Traceability/tag coverage summary
   - Atomicity and implementation guidance coverage summary
6. `## Fix Queue for doc-req-fixer`
   - `auto_fixable`
   - `manual_required`
   - `blocked`
7. `## Recommended Next Step`
   - `run doc-req-fixer`
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

## Hand-off Contract to doc-req-fixer

`doc-req-fixer` MUST accept combined audit report as equivalent upstream input:
- `REQ-NN.A_audit_report_vNNN.md` (preferred)
- `REQ-NN.R_review_report_vNNN.md` (legacy compatibility)

Precedence rule:
1. Select newest timestamp.
2. If timestamps are equal, prefer `.A_audit_report` over `.R_review_report`.

---

## Example Invocation

```bash
/doc-req-audit docs/07_REQ/REQ-01_f1_iam/
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
| 1.0 | 2026-02-27 | Initial REQ audit wrapper; validator→reviewer orchestration; combined report contract for fixer with `.A_` preferred and `.R_` legacy compatibility |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

