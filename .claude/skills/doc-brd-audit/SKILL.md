---
name: doc-brd-audit
description: Unified BRD audit wrapper that runs validator then reviewer and produces a combined report for fixer consumption

metadata:
  tags:
    - sdd-workflow
    - quality-assurance
    - brd-audit
    - layer-1-artifact
    - shared-architecture
  custom_fields:
    layer: 1
    artifact_type: BRD
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [BRD]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "2.1"
    last_updated: "2026-03-01"
  versioning_policy: "tracks BRD-MVP-TEMPLATE schema_version"

---

# doc-brd-audit

## Purpose

Run a **unified BRD audit workflow** that combines structural validation and content quality checks into a single pass, producing one **combined report** optimized for `doc-brd-fixer` input.

**2-Skill Model**: This skill replaces the separate `doc-brd-validator` and `doc-brd-reviewer` skills (now deprecated). All validation and review logic is consolidated here.

**Deprecated Skills**:
| Skill | Status | Replacement |
|-------|--------|-------------|
| `doc-brd-validator` | DEPRECATED | Merged into `doc-brd-audit` |
| `doc-brd-reviewer` | DEPRECATED | Merged into `doc-brd-audit` |

**Layer**: 1 (BRD Quality Gate Wrapper)

**Upstream**: BRD file(s)

**Downstream**:
- Combined Audit Report: `BRD-NN.A_audit_report_vNNN.md`
- Optional Fix Cycle trigger for `doc-brd-fixer`

---

## Why This Skill Exists

The 2-skill model (`doc-brd-audit` + `doc-brd-fixer`) simplifies the BRD quality workflow.

| Concern | Owner Skill |
|---------|-------------|
| All validation + scoring | `doc-brd-audit` (this skill) |
| Apply fixes from audit report | `doc-brd-fixer` |

---

## Fresh Audit Policy (MANDATORY)

**ALWAYS run the audit from scratch.** Do NOT:
- Reference previous audit reports for scoring decisions
- Skip validation steps based on drift cache history
- Assume compliance from prior fix history
- Use cached results from previous runs

**ALWAYS**:
- Run all validation scripts fresh every time
- Re-check all structure/schema compliance
- Re-compute PRD-ready score independently
- Generate a new audit report with incremented version

---

## When to Use

Use `doc-brd-audit` when:
- You want one command for BRD quality checks
- You need a combined report for `doc-brd-fixer`
- You are running CI/manual QA before PRD generation

Do NOT use when:
- BRD does not exist (use `doc-brd` / `doc-brd-autopilot` generation first)
- You only need one specific check domain (use validator or reviewer directly)

---

## Execution Contract

### Input
- BRD path (`docs/01_BRD/BRD-NN_*/...`)
- Optional: threshold (default review threshold: 90)

### Sequence (Mandatory)

```text
1) Run doc-brd-validator
2) Run doc-brd-reviewer
3) Normalize and merge findings
4) Write BRD-NN.A_audit_report_vNNN.md
5) If auto-fixable findings exist, hand off to doc-brd-fixer
```

### Combined Status Rules

- `PASS`: Validator PASS AND Reviewer score >= threshold AND no blocking issues
- `FAIL`: Validator FAIL OR Reviewer score < threshold OR blocking/manual-required issues present

**Diagram Contract Gate (ADVISORY for BRD)**:
- BRD diagram findings are recorded as non-blocking by default.
- Recommended tags: `@diagram: c4-l1` and `@diagram: dfd-l0`
- If sequence diagram exists, recommend one sequence tag (`@diagram: sequence-sync|sequence-async|sequence-error`)
- Recommended intent fields: `diagram_type`, `level`, `scope_boundary`, `upstream_refs`, `downstream_refs`
- Optional strict mode only when explicitly enabled (e.g., `audit_strict_diagrams: true`).

---

## Combined Report Format (for doc-brd-fixer)

Output file: `BRD-NN.A_audit_report_vNNN.md`

Required sections:

1. `## Summary`
   - BRD ID, timestamp (EST), overall status
   - Validator status, reviewer score
2. `## Score Calculation (Deduction-Based)`
   - Formula: `100 - total_deductions`
   - Deductions grouped by: contamination (max 50), FR completeness (max 30), structure/quality (max 20)
   - Threshold comparison (`>=90` pass gate)
3. `## Validator Findings`
   - List by severity/code
4. `## Reviewer Findings`
   - List by severity/code
5. `## Diagram Contract Findings`
   - Required BRD tags status (`c4-l1`, `dfd-l0`)
   - Sequence contract status when sequence is present
   - Intent header completeness status
6. `## Fix Queue for doc-brd-fixer`
   - `auto_fixable`
   - `manual_required`
   - `blocked`
7. `## Recommended Next Step`
   - `run doc-brd-fixer`
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

## Hand-off Contract to doc-brd-fixer

`doc-brd-fixer` MUST accept combined audit report as equivalent upstream input:
- `BRD-NN.A_audit_report_vNNN.md`
- `BRD-NN.R_review_report_vNNN.md` (legacy compatibility)

If both exist, fixer should prefer latest timestamp.

---

## Example Invocation

```bash
/doc-brd-audit docs/01_BRD/BRD-01_platform/BRD-01_platform.md
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
| 2.1 | 2026-03-01 | **2-Skill Model**: Deprecated `doc-brd-validator` and `doc-brd-reviewer`; Added Fresh Audit Policy (MANDATORY); All validation and scoring unified in this skill |
| 1.3 | 2026-02-26 | Added advisory BRD C4/DFD/sequence diagram contract checks and required `Diagram Contract Findings` section in combined audit reports; strict mode optional |
| 1.2 | 2026-02-26 | Initial audit wrapper; validator→reviewer orchestration; combined report contract for fixer |
