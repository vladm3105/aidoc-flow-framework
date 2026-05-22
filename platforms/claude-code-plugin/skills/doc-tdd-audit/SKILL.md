---
name: doc-tdd-audit
description: Unified TDD audit wrapper that runs validator then reviewer and produces a combined report for fixer consumption

metadata:
  tags:
    - sdd-workflow
    - quality-assurance
    - tdd-audit
    - layer-7-artifact
    - shared-architecture
  custom_fields:
    layer: 7
    artifact_type: TDD
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [TDD]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.1"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"

---

# doc-tdd-audit

## Purpose

Run a **single TDD audit workflow** that executes:

1. `doc-tdd-validator` (structural/schema gate)
2. `doc-tdd-reviewer` (semantic/content quality gate)

Then emit one **combined report** optimized for `doc-tdd-fixer` input.

**Layer**: 7 (TDD Quality Gate Wrapper)

**Upstream**: TDD file(s)

**Downstream**:
- Combined Audit Report: `TDD-NN.A_audit_report_vNNN.md`
- Optional Fix Cycle trigger for `doc-tdd-fixer`

---

## Why This Skill Exists

Use this wrapper to avoid user confusion between validator and reviewer while preserving separation of concerns.

| Concern | Owner Skill |
|---------|-------------|
| Schema/template compliance | `doc-tdd-validator` |
| Content quality and implementation readiness | `doc-tdd-reviewer` |
| Single user-facing audit command | `doc-tdd-audit` |

---

## When to Use

Use `doc-tdd-audit` when:
- You want one command for TDD quality checks
- You need a combined report for `doc-tdd-fixer`
- You are running QA before IPLAN generation

Do NOT use when:
- TDD does not exist (use `doc-tdd` / `doc-tdd-autopilot` generation first)
- You only need one specific check domain (use validator or reviewer directly)

---

## Execution Contract

### Input
- TDD path (`docs/07_TDD/TDD-NN_*/TDD-NN_*.yaml`)
- Optional: threshold (default review threshold: 90)

### Sequence (Mandatory)

```text
1) Run doc-tdd-validator
2) Run doc-tdd-reviewer
3) Normalize and merge findings
4) Write TDD-NN.A_audit_report_vNNN.md
5) If auto-fixable findings exist, hand off to doc-tdd-fixer
```

### Combined Status Rules

- `PASS`: Validator PASS AND Reviewer score >= threshold AND no blocking issues
- `FAIL`: Validator FAIL OR Reviewer score < threshold OR blocking/manual-required issues present

---

## Combined Report Format (for doc-tdd-fixer)

Output file: `TDD-NN.A_audit_report_vNNN.md`

Required sections:

1. `## Summary`
   - TDD ID, timestamp (EST), overall status
   - Validator status, reviewer score
2. `## Score Calculation (Deduction-Based)`
   - Formula: `100 - total_deductions`
   - Threshold comparison (`>=90` pass gate)
3. `## Validator Findings`
   - List by severity/code
4. `## Reviewer Findings`
   - List by severity/code
5. `## Coverage Findings`
   - Test-type coverage summary (unit / integration / e2e / security)
   - Traceability/tag coverage summary
   - SPEC alignment and edge-case coverage summary
6. `## Fix Queue for doc-tdd-fixer`
   - `auto_fixable`
   - `manual_required`
   - `blocked`
7. `## Recommended Next Step`
   - `run doc-tdd-fixer`
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

## Hand-off Contract to doc-tdd-fixer

`doc-tdd-fixer` MUST accept combined audit report as equivalent upstream input:
- `TDD-NN.A_audit_report_vNNN.md` (preferred)
- `TDD-NN.R_review_report_vNNN.md` (legacy compatibility)

Precedence rule:
1. Select newest timestamp.
2. If timestamps are equal, prefer `.A_audit_report` over `.R_review_report`.

---

## Example Invocation

```bash
/doc-tdd-audit docs/07_TDD/TDD-01_auth_service/TDD-01_auth_service.yaml
```

Expected outcome:
1. validator runs
2. reviewer runs
3. combined audit report generated
4. fixer can execute directly from combined report

---

## Standards & References

- **TDD layer guide**: `framework/layers/07_TDD/README.md`
- **TDD template**: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- **ID naming standards**: `framework/governance/ID_NAMING_STANDARDS.md`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-05-22 | Migrated to the 8-layer framework model: TDD (Layer 7), single unified template (no test subtypes); test-type coverage (unit/integration/e2e/security) summarized as TDD test-case content; input path is the TDD nested folder (`docs/07_TDD/TDD-NN_*/...yaml`); audit precedes IPLAN (Layer 8); references point at `framework/layers/07_TDD/` and `framework/governance/` |
| 1.0 | 2026-02-27 | Initial audit wrapper; validator→reviewer orchestration; combined report contract for fixer with `.A_` preferred and `.R_` legacy compatibility |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.
