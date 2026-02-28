---
name: doc-prd-audit
description: Unified PRD audit wrapper that runs validator then reviewer and produces a combined report for fixer consumption

metadata:
  tags:
    - sdd-workflow
    - quality-assurance
    - prd-audit
    - layer-2-artifact
    - shared-architecture
  custom_fields:
    layer: 2
    artifact_type: PRD
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [PRD]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.0"
    last_updated: "2026-02-26"
  versioning_policy: "tracks PRD-MVP-TEMPLATE schema_version"

---

# doc-prd-audit

## Purpose

Run a **single PRD audit workflow** that executes:

1. `doc-prd-validator` (structural/schema gate)
2. `doc-prd-reviewer` (semantic/content quality gate)

Then emit one **combined report** optimized for `doc-prd-fixer` input.

**Layer**: 2 (PRD Quality Gate Wrapper)

**Upstream**: PRD file(s)

**Downstream**:
- Combined Audit Report: `PRD-NN.A_audit_report_vNNN.md`
- Optional Fix Cycle trigger for `doc-prd-fixer`

---

## Why This Skill Exists

Use this wrapper to avoid user confusion between validator and reviewer while preserving separation of concerns.

| Concern | Owner Skill |
|---------|-------------|
| Schema/template compliance | `doc-prd-validator` |
| Content quality and product alignment | `doc-prd-reviewer` |
| Single user-facing audit command | `doc-prd-audit` |

---

## When to Use

Use `doc-prd-audit` when:
- You want one command for PRD quality checks
- You need a combined report for `doc-prd-fixer`
- You are running QA before EARS generation

Do NOT use when:
- PRD does not exist (use `doc-prd` / `doc-prd-autopilot` generation first)
- You only need one specific check domain (use validator or reviewer directly)

---

## Execution Contract

### Input
- PRD path (`docs/02_PRD/PRD-NN_*/...`)
- Optional: threshold (default review threshold: 90)

### Sequence (Mandatory)

```text
1) Run doc-prd-validator
2) Run doc-prd-reviewer
3) Normalize and merge findings
4) Write PRD-NN.A_audit_report_vNNN.md
5) If auto-fixable findings exist, hand off to doc-prd-fixer
```

### Combined Status Rules

- `PASS`: Validator PASS AND Reviewer score >= threshold AND no blocking issues
- `FAIL`: Validator FAIL OR Reviewer score < threshold OR blocking/manual-required issues present

### Diagram Contract Gate (BLOCKING for PRD)

Audit MUST fail when any blocking diagram code is present:
- `PRD-E023` missing `@diagram: c4-l2`
- `PRD-E024` missing `@diagram: dfd-l1`
- `PRD-E025` missing `@diagram: sequence-*`
- `PRD-E026` sequence diagram missing `alt/else` exception path

Also include warning diagnostics when present:
- `PRD-W011` diagram intent metadata incomplete

---

## Combined Report Format (for doc-prd-fixer)

Output file: `PRD-NN.A_audit_report_vNNN.md`

Required sections:

1. `## Summary`
   - PRD ID, timestamp (EST), overall status
   - Validator status, reviewer score
2. `## Score Calculation (Deduction-Based)`
   - Formula: `100 - total_deductions`
   - Threshold comparison (`>=90` pass gate)
3. `## Validator Findings`
   - List by severity/code
4. `## Reviewer Findings`
   - List by severity/code
5. `## Diagram Contract Findings`
   - Required PRD tags status (`c4-l2`, `dfd-l1`, `sequence-*`)
   - Exception-flow evidence status (`alt/else`)
   - Intent header completeness status
6. `## Fix Queue for doc-prd-fixer`
   - `auto_fixable`
   - `manual_required`
   - `blocked`
7. `## Recommended Next Step`
   - `run doc-prd-fixer`
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

## Hand-off Contract to doc-prd-fixer

`doc-prd-fixer` MUST accept combined audit report as equivalent upstream input:
- `PRD-NN.A_audit_report_vNNN.md` (preferred)
- `PRD-NN.R_review_report_vNNN.md` (legacy compatibility)

If both exist, fixer should prefer latest timestamp.

---

## Example Invocation

```bash
/doc-prd-audit docs/02_PRD/PRD-01_f1_iam/PRD-01_f1_iam.md
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
| 1.0 | 2026-02-26 | Initial PRD audit wrapper; validator→reviewer orchestration; blocking PRD diagram contract gate; combined report contract for fixer |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

