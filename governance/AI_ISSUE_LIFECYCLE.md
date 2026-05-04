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
4. Round 1 PR gates execute: `sdd_validate` -> `sdd_review` -> `sdd_remediate` -> post-remediation `sdd_validate` -> Hermes final blocker-gap check
5. If Round 1 fails, Round 2 executes with same gates
6. If Round 2 fails, Hermes escalates to human review and blocks merge
7. If gates pass, PR merges and linked issue transitions to done

## Control-Plane / Execution-Plane Split

1. Hermes (control plane) owns triage, planning decisions, and lifecycle governance.
2. Execution agents (Claude Code, Codex, OpenCode, or equivalent) own implementation, PR submission, and deployment execution for approved issues.
3. Hermes owns round-based PR governance, merge-time escalation decisions, post-deployment verification, and closure decisions.

## Deployment and QA Loop

1. Deployment issue created after merge
2. QA issue created for functional changes
3. QA runs on staging
4. Failures create bug issues (bounded iterations)
5. Success enables production readiness

## Observability-Driven Fix Loop

1. Monitoring/alerting tools emit incident or anomaly signals.
2. Hermes translates signals into actionable GitHub issues with severity, impact, repro context, and traceability links.
3. Approved issues enter `ai:ready` queue for autonomous execution.
4. Execution agents run fix -> PR.
5. Hermes runs Round 1 and, when needed, Round 2 PR governance gates.
6. Round 2 failure triggers human escalation and merge block.
7. Successful gates allow merge and linked issue closure.
8. Hermes validates production/staging evidence and closes or reopens issues based on outcomes.

## Traceability Policy

- IPLAN is mandatory execution artifact.
- Upstream references use v3 artifact IDs.
- Legacy TASKS-based issue generation is deprecated.
