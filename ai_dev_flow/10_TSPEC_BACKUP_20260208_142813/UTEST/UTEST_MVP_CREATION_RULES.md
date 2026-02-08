---
title: "UTEST MVP Creation Rules"
tags:
  - utest-rules
  - mvp-guidance
  - layer-10-artifact
  - ai-guidance
custom_fields:
  document_type: creation-rules
  artifact_type: UTEST
  layer: 10
  test_type_code: 40
  development_status: active
---

# UTEST MVP Creation Rules

## Purpose

AI guidance for creating unit test specifications that meet TDD workflow requirements.

## Pre-Creation Checklist

Before creating a UTEST document:

- [ ] SPEC document exists and is approved
- [ ] REQ documents are finalized
- [ ] Component boundaries are defined
- [ ] Dependencies are identified

## Document Naming

**Format**: `UTEST-NN_[component_name].md`

**Examples**:
- `UTEST-01_auth_service.md`
- `UTEST-02_data_validator.md`
- `UTEST-03_cache_manager.md`

## Element ID Format

**Format**: `TSPEC.NN.40.SS`

| Component | Description |
|-----------|-------------|
| `TSPEC` | Artifact type |
| `NN` | Document number (matches filename) |
| `40` | Unit test type code |
| `SS` | Sequential test case number (01-99) |

## Required Sections

| Section | Required | Content |
|---------|----------|---------|
| 1. Document Control | Yes | Status, version, scores |
| 2. Test Scope | Yes | Component, dependencies, categories |
| 3. Test Case Index | Yes | ID, name, category, REQ coverage |
| 4. Test Case Details | Yes | I/O tables, pseudocode, errors |
| 5. REQ Coverage Matrix | Yes | REQ → Test mapping |
| 6. Traceability | Yes | @req, @spec tags |

## Test Categories

Use these category prefixes for all test cases:

| Category | Purpose | Example |
|----------|---------|---------|
| `[Logic]` | Business logic validation | Calculation correctness |
| `[State]` | State transitions | Object lifecycle |
| `[Validation]` | Input validation | Schema compliance |
| `[Edge]` | Boundary conditions | Min/max values |

## Traceability Rules

### Required Tags

| Tag | Requirement |
|-----|-------------|
| `@req` | Every test MUST trace to at least one REQ |
| `@spec` | Document MUST reference source SPEC |

### Tag Format

```markdown
@req: REQ.NN.10.SS
@spec: SPEC-NN
```

## I/O Table Requirements

Every test case MUST include an Input/Output table:

```markdown
| Input | Expected Output | Notes |
|-------|-----------------|-------|
| [input value] | [expected result] | [explanation] |
```

**Minimum rows**: 3 (happy path, error case, edge case)

## Pseudocode Requirements

Complex tests MUST include pseudocode using Given-When-Then format:

```markdown
GIVEN [precondition]
WHEN [action] is called
THEN [expected result]
AND [additional assertions]
```

## Error Case Documentation

Each test case MUST document error conditions:

```markdown
| Error Condition | Expected Behavior |
|-----------------|-------------------|
| [condition] | [behavior] |
```

## Coverage Requirements

| Metric | Target |
|--------|--------|
| REQ coverage | ≥90% |
| Test categories | All 4 represented |
| I/O table rows | ≥3 per test |
| Error cases | ≥1 per test |

## Quality Gate Scoring

| Component | Weight | Criteria |
|-----------|--------|----------|
| REQ Coverage | 30% | Every REQ has ≥1 unit test |
| I/O Tables | 25% | Every test has input/output table |
| Category Prefixes | 15% | All tests use category prefixes |
| Pseudocode | 15% | Executable pseudocode present |
| Error Cases | 15% | Error conditions documented |

**Pass threshold**: ≥90%

## Common Mistakes

| Mistake | Correction |
|---------|------------|
| Missing @req tag | Every test MUST trace to REQ |
| No I/O table | Add input/output examples |
| Missing error cases | Document failure scenarios |
| Vague pseudocode | Use specific Given-When-Then |
| Wrong ID format | Use TSPEC.NN.40.SS format |

## Validation Command

```bash
python scripts/validate_utest.py docs/10_TSPEC/UTEST/UTEST-01_*.md
```

## See Also

- [UTEST-MVP-TEMPLATE.md](UTEST-MVP-TEMPLATE.md)
- [UTEST_MVP_VALIDATION_RULES.md](UTEST_MVP_VALIDATION_RULES.md)
- [UTEST_MVP_QUALITY_GATES.md](UTEST_MVP_QUALITY_GATES.md)
