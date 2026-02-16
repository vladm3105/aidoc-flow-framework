# Test Fixtures

This directory contains sample SDD artifacts for testing and validation.

## budget_alert/

Worked example demonstrating the Budget Alert feature implementation.

### Files

| File | Description | Layer |
|------|-------------|-------|
| `BRD-01.md` | Business Requirements Document | L1 |
| `PRD-01.md` | Product Requirements Document | L2 |
| `SPEC-05.yaml` | Technical Specification | L9 |
| `TASKS-05.yaml` | Task Breakdown | L11 |

### Usage

These fixtures are used by:
- `tasks_to_github.py` for testing issue creation
- `validate_artifact.py` for testing validation dispatch
- `drift_check.py` for testing drift detection
- Integration tests for end-to-end workflow validation

### Adding New Fixtures

1. Create a subdirectory for the feature/example
2. Add SDD artifacts following the same naming convention
3. Ensure proper traceability tags between artifacts
4. Update this README with the new fixture description
