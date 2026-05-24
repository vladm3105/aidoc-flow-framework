---
name: Development Issue
about: Create a development issue for the 4-stage QA workflow
title: "[P{phase}-{task_id}] "
labels: ai:development
assignees: ''
---

## Summary

<!-- One sentence describing what needs to be implemented -->

## Phase & Task

| Field | Value |
|:------|:------|
| Phase | <!-- e.g., 1, 2, 3 --> |
| Task ID | <!-- e.g., 1.1, 2.3a --> |
| Epic | <!-- e.g., #11 --> |
| Priority | <!-- P0/P1/P2/P3 --> |
| Size | <!-- XS/S/M/L/XL --> |

## Acceptance Criteria

<!-- Checkboxes for verifiable completion criteria -->
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Test Plan

<!-- IMPORTANT: This section is extracted by the QA workflow -->
<!-- List specific test scenarios for staging verification -->

### Unit Tests

- [ ] Test case 1: {description}
- [ ] Test case 2: {description}

### Integration Tests

- [ ] Test case 1: {description}

### Feature-Specific Tests

- [ ] Functional test: {description}
- [ ] Edge case: {description}

## Technical Specification

### Input
<!-- Data structures, API parameters, user inputs -->

### Output
<!-- Expected results, return values, side effects -->

### Files to Modify
<!-- List files that will be created or modified -->
- `path/to/file.py`

## Dependencies

<!-- Issues that must be completed before this one -->
- Depends on: #
- Blocks: #

## Planning Package (Mandatory Before `ai:ready`)

<!-- Planning-first governance gate artifacts -->
| Field | Value |
|:------|:------|
| Planning Roadmap | <!-- link/path/reference --> |
| Planning Index | <!-- link/path/reference --> |
| Changelog Plan | <!-- link/path/reference --> |
| Approved IPLAN | <!-- IPLAN-### reference --> |
| Plan Approval | <!-- Human or LLM-as-judge --> |

## AI Implementation Notes

<!-- Special instructions for AI agent -->
- Follow existing patterns in `src/`
- Maintain test coverage ≥90%
- Update documentation if needed

---

*After PR merge, this issue will trigger:*

1. *Deployment issue creation (`ai:deployment`)*
2. *QA testing issue creation (`ai:qa-testing`)*
