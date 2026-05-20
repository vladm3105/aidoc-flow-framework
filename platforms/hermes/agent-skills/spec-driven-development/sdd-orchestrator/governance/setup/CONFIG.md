# SDD Framework Configuration Variables

## Baseline

This configuration targets SDD v3.2 in `framework/`.

Canonical chain:
`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

## Core Variables

- `{PROJECT_PREFIX}`
- `{PROJECT_NAME}`
- `{REPO_NAME}`
- `{GITHUB_ORG}`
- `{GITHUB_HOST}`
- `{PROJECT_BOARD_NUMBER}`

## Validation

After customization, verify:
- no unresolved placeholders
- no legacy framework root references in active files
