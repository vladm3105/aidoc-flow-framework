# Technology Stack Alignment & Scaffolding Blueprints Plan

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Ready |
| Last Updated | 2026-10-10 |
| Author | Framework Maintainer |
| Framework Version | 0.91.2 |
| Authority | [Decision D-0013 / GD-13](framework/governance/DECISIONS.md) & [CHG-83](framework/archive/CHG-83/CHG-83.yaml) |

## Objective

Align `aidoc-flow-framework` with our ecosystem's authoritative platform technology stack (defined across `/mnt/e/dev/technology_stack/` documents 00 through 09) while strictly preserving **engine-agnostic core specifications** under Decision D-0013 / GD-13.

## Status

Ready for execution under Change Request `CHG-83` (C1/DIR2C governance and specification readiness flow).

## Scope

In scope:

1. Author `framework/governance/RECOMMENDED_PLATFORM_STACK.md` providing authoritative platform reference architecture guidance.
2. Author five operational blueprints in `framework/governance/aidoc/`:
   - `AIDOC-TEMPORAL-LANGGRAPH-RUNTIME-TEMPLATE.md`
   - `AIDOC-BYTEBASE-POSTGRES-SCHEMA-TEMPLATE.md`
   - `AIDOC-NATS-CLOUDEVENTS-PROTOBUF-TEMPLATE.md`
   - `AIDOC-GVISOR-SANDBOX-EXECUTION-PROFILE.md`
   - `AIDOC-LANGFUSE-HYPERDX-OBSERVABILITY-TEMPLATE.md`
3. Enhance core vendor-agnostic specifications with open-standard primitives:
   - Layer 06 SPEC: CloudEvents v1.0, Protobuf IDL, UUIDv7 monotonic keys, and database contracts.
   - Layer 07 TDD: Containerized database testing, migration verification, and message deduplication assertions.
   - Layer 10 EVAL: Prompt manifest traceability and benchmark dataset evaluation metrics.
   - Governance: Cognitive loop heartbeating protocol (`DURABLE_EXECUTION_STANDARD.md`), sandboxed agent execution profile (`WORKTREE_FLOW.md`), and prompt manifest telemetry attributes (`ENGINE_TELEMETRY.md`).
4. Cross-link guides in `framework/governance/README.md`, `framework/governance/aidoc/README.md`, and `docs/ADAPTATION-GUIDE.md`.

Out of scope:

- Bundling proprietary runtime engines or orchestrator SDKs into the framework core.
- Modifying frozen historical archives prior to CHG-83.

## Approach

Execute under the DIR2C (iplan_to_code) flow:

1. Create isolated task worktree `feature/chg-83-techstack-alignment`.
2. Author authorizing change request `CHG-83.yaml` and implementation plan `IPLAN-83.yaml` with archive snapshots.
3. Validate CHG using `sdd_doc_lint/chg_lint.py`.
4. Apply spec and governance enhancements.
5. Author platform guidance and operational blueprints.
6. Verify against `sdd_doc_lint.swf_lint`, `test_spec_hygiene`, and full conformance suite.
7. Perform multi-agent self-review per `OPS-0065`.

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Core framework bundles no orchestrators and workflows compile dynamically into engines | Engine-agnostic purity (D-0013) | framework/governance/DECISIONS.md:342 |
| 2 | Durable execution standard partitions platform into 3 tiers: Workflow, Cognitive Graphs, and Deterministic Services | TIER 1: DURABLE WORKFLOW | framework/governance/DURABLE_EXECUTION_STANDARD.md:43 |
| 3 | Autonomous execution golden rule: Reasoning in Cognitive Graphs, Effects in Deterministic Services, Control in Workflows | Reasoning in Cognitive Graphs | framework/governance/DURABLE_EXECUTION_STANDARD.md:78 |
| 4 | Engine telemetry standardizes attempt and gate verdict spans | aidoc.attempt | framework/governance/ENGINE_TELEMETRY.md:46 |
| 5 | Engine telemetry standardizes correlation attributes for CHG, IPLAN, and EVAL | aidoc.chg_id | framework/governance/ENGINE_TELEMETRY.md:74 |
| 6 | Worktree flow defines multi-worktree port and container isolation | 2.2 Multi-Worktree Port & Container Isolation | framework/governance/WORKTREE_FLOW.md:46 |
| 7 | SPEC layer disallows raw SQL/ORM schemas in data models | FAIL: SQL/ORM schemas in data_models | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:66 |
| 8 | SPEC layer defines component public API exports | exports: | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:120 |
| 9 | TDD mock strategy includes real database testing | SQLite/in-memory for speed | framework/layers/07_TDD/TDD-TEMPLATE.yaml:168 |
| 10 | EVAL layer is 1:1 coupled with IPLAN | lifecycle: iplan-coupled | framework/layers/10_EVAL/EVAL-TEMPLATE.yaml:36 |
| 11 | Adaptation guide indexes recommended platform technology stack | Recommended Platform Technology Stack | docs/ADAPTATION-GUIDE.md:201 |
| 12 | Aidoc governance directory indexes operational runtime template | AIDOC-TEMPORAL-LANGGRAPH-RUNTIME-TEMPLATE.md | framework/governance/aidoc/README.md:31 |

## Review log

### Pass 1 - 2026-10-10 - independent

- *Review findings*: Identified 2 load-bearing requirements: (1) Core framework specifications must not leak engine-specific or vendor tokens (`test_spec_hygiene.py`); (2) All archive snapshots for modified templates (`SPEC-TEMPLATE.yaml`, `TDD-TEMPLATE.yaml`, `EVAL-TEMPLATE.yaml`) must be placed in `framework/archive/CHG-83/` and verified via `chg_lint.py`.
- *Resolution*: Replaced all vendor token references with neutral standards in core templates, created snapshots in `framework/archive/CHG-83/`, and verified `chg_lint.py` passes with zero errors and zero warnings.

### Pass 2 - 2026-10-10 - independent

- *Review findings*: Verified cross-links across `RECOMMENDED_PLATFORM_STACK.md`, `docs/ADAPTATION-GUIDE.md`, and `aidoc/README.md`. Verified that `check_plan.py` claim ledger citations resolve against the active repository tree with zero missing symbols.
- *Resolution*: Findings: none. Result: ready.
