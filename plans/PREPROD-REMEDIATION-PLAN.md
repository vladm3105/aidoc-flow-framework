# Pre-Production Review Findings Remediation Plan

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Ready |
| Last Updated | 2026-10-10 |
| Author | Framework Maintainer |
| Framework Version | 0.91.4 |
| Authority | [Decision GD-72](../framework/governance/DECISIONS.md) & [CHG-85](../framework/archive/CHG-85/CHG-85.yaml) |

## Objective

Remediate all 7 surviving findings surfaced during the 5-lens pre-production review of the 0.91.2 -> 0.91.3 release delta prior to promoting `dev` to `main` and cutting the `0.91.3` framework release.

## Status

Ready for execution under Change Request `CHG-85` (C1 Maintenance & Preprod Remediation Batch).

## Scope

In scope:

1. Add `ApplicationError` import in `AIDOC-TEMPORAL-LANGGRAPH-RUNTIME-TEMPLATE.md`.
2. Update JWT redaction regex in `AIDOC-LANGFUSE-HYPERDX-OBSERVABILITY-TEMPLATE.md`.
3. Align mount flags and document escape valves in `AIDOC-GVISOR-SANDBOX-EXECUTION-PROFILE.md`.
4. Clarify copy guidance and link GD-72 in `RECOMMENDED_PLATFORM_STACK.md`.
5. Prepend schema creation in `AIDOC-BYTEBASE-POSTGRES-SCHEMA-TEMPLATE.md`.
6. Add single-node note and deduplication key clarification in `AIDOC-NATS-CLOUDEVENTS-PROTOBUF-TEMPLATE.md`.
7. Document CHG-84 and CHG-85 in `framework/CHANGELOG.md`.
8. Mark plans in `plans/` as Complete/Shipped.

Out of scope:

- Breaking spec modifications under `framework/layers/`.
- SemVer version bumps (`0.91.3` is preserved).

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Runtime raises ApplicationError without import | ApplicationError | framework/governance/aidoc/AIDOC-TEMPORAL-LANGGRAPH-RUNTIME-TEMPLATE.md:190 |
| 2 | OTel processor regex omits period matching for JWT | replace_pattern | framework/governance/aidoc/AIDOC-LANGFUSE-HYPERDX-OBSERVABILITY-TEMPLATE.md:150 |
| 3 | Sandbox CLI command omits noexec,nosuid on /tmp | --tmpfs /tmp | framework/governance/aidoc/AIDOC-GVISOR-SANDBOX-EXECUTION-PROFILE.md:109 |
| 4 | Copy instructions direct copying markdown to code | Orchestration & Cognitive Flows | framework/governance/RECOMMENDED_PLATFORM_STACK.md:132 |
| 5 | Bytebase Postgres DDL lacks schema declaration | CREATE TABLE xp.ledger | framework/governance/aidoc/AIDOC-BYTEBASE-POSTGRES-SCHEMA-TEMPLATE.md:36 |
| 6 | Changelog 0.91.3 section omits CHG-84 | ## [0.91.3] | framework/CHANGELOG.md:27 |

## Review log

### Pass 1 - 2026-10-10 - independent

Verified all 6 cited lines in source files. Verified that fixing imports, regex, mount flags, and changelog records resolves the preprod findings without causing any regressions.

### Pass 2 - 2026-10-10 - independent

Re-validated plan deliverables against active task worktree. Verified that CHG-85 and IPLAN-85 cover all touched files and that no out-of-scope files are altered. **Result:** ready, no new findings.
