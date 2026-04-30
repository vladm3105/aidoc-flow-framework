# AI Issue Lifecycle

**Framework**: SDD v3.2 governance lifecycle

## Canonical Artifact Chain

`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

## Issue Sources

1. v3 artifact-derived issues (`source:sdd`)
2. Human-created issues
3. Automation-generated issues (deployment/QA/bug)

## Development Lifecycle

1. Human/automation marks issue `ai:ready`
2. AI performs analysis and creates IPLAN
3. AI sets `ai:in-progress`, implements, opens PR
4. AI sets `ai:review-requested` after PR creation and AC sync
5. Review/merge transitions issue to done

## Deployment and QA Loop

1. Deployment issue created after merge
2. QA issue created for functional changes
3. QA runs on staging
4. Failures create bug issues (bounded iterations)
5. Success enables production readiness

## Traceability Policy

- IPLAN is mandatory execution artifact.
- Upstream references use v3 artifact IDs.
- Legacy TASKS-based issue generation is deprecated.
