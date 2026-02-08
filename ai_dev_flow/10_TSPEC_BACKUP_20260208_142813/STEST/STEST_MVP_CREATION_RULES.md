---
title: "STEST MVP Creation Rules"
tags:
  - stest-rules
  - mvp-guidance
  - layer-10-artifact
  - ai-guidance
custom_fields:
  document_type: creation-rules
  artifact_type: STEST
  layer: 10
  test_type_code: 42
  development_status: active
---

# STEST MVP Creation Rules

## Purpose

AI guidance for creating smoke test specifications for post-deployment validation.

## Pre-Creation Checklist

Before creating an STEST document:

- [ ] EARS documents exist for behavioral requirements
- [ ] BDD scenarios are finalized
- [ ] Critical paths identified
- [ ] Deployment pipeline defined
- [ ] Rollback procedures documented

## Document Naming

**Format**: `STEST-NN_[deployment_target].md`

**Examples**:
- `STEST-01_production_api.md`
- `STEST-02_staging_services.md`
- `STEST-03_canary_deployment.md`

## Element ID Format

**Format**: `TSPEC.NN.42.SS`

| Component | Description |
|-----------|-------------|
| `TSPEC` | Artifact type |
| `NN` | Document number (matches filename) |
| `42` | Smoke test type code |
| `SS` | Sequential test case number (01-99) |

## Required Sections

| Section | Required | Content |
|---------|----------|---------|
| 1. Document Control | Yes | Status, timeout budget |
| 2. Test Scope | Yes | Deployment context, timeout budget |
| 3. Critical Path Index | Yes | ID, path, timeout, rollback trigger |
| 4. Test Case Details | Yes | Pass/fail criteria, health checks |
| 5. Rollback Procedures | Yes | Failure actions per test |
| 6. Traceability | Yes | @ears, @bdd, @req tags |

## Critical Constraints

### Timeout Budget

| Constraint | Requirement |
|------------|-------------|
| Total suite | <300 seconds (5 minutes) |
| Individual test | <60 seconds |
| Buffer | 30-45 seconds |

### Pass/Fail Criteria

Every test MUST have binary pass/fail outcomes:
- No partial passes
- No warnings (fail or pass only)
- Timeout = FAIL

## Traceability Rules

### Required Tags

| Tag | Requirement |
|-----|-------------|
| `@ears` | Every test MUST trace to EARS requirement |
| `@bdd` | Every test MUST trace to BDD scenario |
| `@req` | Document MUST reference REQ |

### Tag Format

```markdown
@ears: EARS.NN.25.SS
@bdd: BDD.NN.01.SS
@req: REQ.NN.10.SS
```

## Rollback Procedure Requirements

Every test MUST include rollback procedure:

```markdown
| Step | Action | Command |
|------|--------|---------|
| 1 | [Action] | [Command] |
```

**Required columns**: Step, Action, Command

## Health Check Requirements

Every test MUST include executable health check:

```bash
curl -f https://api.example.com/health --max-time 10
```

## Coverage Requirements

| Metric | Target |
|--------|--------|
| Critical paths | 100% |
| Rollback defined | 100% |
| Timeout budget | <300s |
| Health checks | 100% |

## Quality Gate Scoring

| Component | Weight | Criteria |
|-----------|--------|----------|
| Critical Paths | 30% | All P0 paths covered |
| Timeout Budget | 25% | Total suite <5 minutes |
| Rollback Defined | 25% | Every test has rollback |
| Health Checks | 20% | Connectivity verified |

**Pass threshold**: 100% (no exceptions)

## Common Mistakes

| Mistake | Correction |
|---------|------------|
| Missing rollback | Every test needs rollback procedure |
| Timeout >5 min | Reduce tests or optimize |
| Partial pass criteria | Make binary pass/fail |
| No health check command | Add executable check |
| Missing @ears tag | Link to EARS requirement |

## Validation Command

```bash
python scripts/validate_stest.py docs/10_TSPEC/STEST/STEST-01_*.md
```

## See Also

- [STEST-MVP-TEMPLATE.md](STEST-MVP-TEMPLATE.md)
- [STEST_MVP_VALIDATION_RULES.md](STEST_MVP_VALIDATION_RULES.md)
- [STEST_MVP_QUALITY_GATES.md](STEST_MVP_QUALITY_GATES.md)
