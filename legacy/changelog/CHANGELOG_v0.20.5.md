# CHANGELOG — Framework v0.20.5

**Release Date**: 2026-05-06

## Summary

Enforced planning-first governance as a mandatory pre-implementation gate across UCX/Hermes documentation, governance policies, GitHub workflows, and issue templates. Standardized approval authority wording to `human reviewer or independent LLM-as-judge session`, migrated runtime executor handling to API-only paths, and aligned UCX KB integration guidance and schema handling with UCX V3 governance boundaries.

## Changes

- Governance lifecycle and policy updates:
  - Added or expanded planning-first gate requirements in:
    - `governance/GOVERNANCE_RULES.md`
    - `governance/AI_ISSUE_LIFECYCLE.md`
    - `governance/DEVELOPMENT_WORKFLOW_GUIDE.md`
    - `governance/DEFINITION_OF_DONE.md`
    - `governance/README.md`
    - `governance/HOME_REPO.md`
  - Updated governance templates for pre-implementation sequencing and approval recording:
    - `governance/templates/CLAUDE.md`
    - `governance/templates/README_AIAGENT.md`

- GitHub workflow and issue governance alignment:
  - Added planning-package enforcement and dispatch gating updates:
    - `.github/workflows/agent-dispatch.yml`
  - Updated issue creation/redispatch templates to include planning package metadata:
    - `.github/ISSUE_TEMPLATE/development_issue.md`
    - `.github/templates/bug-issue-body.md`
  - Changed automated bug/regression issue lifecycle entry from execution-ready to planning state:
    - `.github/workflows/create-bug-issue.yml`
    - `.github/workflows/deploy-staging.yml`
  - Updated GitHub governance references:
    - `governance/github/GITHUB_PROJECT_SETUP.md`
    - `governance/github/GITHUB_WORKFLOWS.md`

- UCX Hermes documentation and skills:
  - Added planning-first lifecycle flow and gate semantics to:
    - `ucx_hermes/docs/README.md`
    - `ucx_hermes/docs/HERMES_INTEGRATION.md`
    - `ucx_hermes/docs/architecture/MCP_OPERATIONAL_FLOWS.md`
    - `ucx_hermes/docs/architecture/MCP_OPERATOR_RUNBOOK.md`
    - `ucx_hermes/docs/policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md`
  - Added and expanded Hermes governance/KB skills:
    - `ucx_hermes/skills/hermes/README.md`
    - `ucx_hermes/skills/hermes/ucx-github-governance/SKILL.md`
    - `ucx_hermes/skills/hermes/ucx-github-deploy-governance/SKILL.md`
    - `ucx_hermes/skills/hermes/ucx-kb-context/SKILL.md`
    - `ucx_hermes/skills/hermes/ucx-kb-maintenance/SKILL.md`
    - `ucx_hermes/skills/hermes/ucx-kb-maintenance/KB_GENERAL_RULES.md`
    - `ucx_hermes/skills/hermes/ucx-kb-maintenance/KB_ENTRY_TEMPLATE.md`
  - Updated bridge behavior and approval semantics:
    - `ucx_hermes/skills/hermes/ucx-sdd-bridge/SKILL.md`

- Runtime executor refactor and server/tool updates:
  - Removed legacy CLI executor runner and introduced shared executor contracts:
    - deleted `ucx_hermes/src/mcp_server/executor/cli_runner.py`
    - added `ucx_hermes/src/mcp_server/executor/contracts.py`
  - Updated API-only executor routing and tool/server behavior in:
    - `ucx_hermes/src/mcp_server/cli/main.py`
    - `ucx_hermes/src/mcp_server/executor/__init__.py`
    - `ucx_hermes/src/mcp_server/executor/api_runner.py`
    - `ucx_hermes/src/mcp_server/executor/dispatcher.py`
    - `ucx_hermes/src/mcp_server/executor/registry.py`
    - `ucx_hermes/src/mcp_server/server.py`
    - `ucx_hermes/src/mcp_server/tool_registry.py`

- UCX KB governance and schema hardening:
  - Documented governance integration boundaries:
    - `ucx_kb/README.md`
  - Added validated schema-name resolution and applied schema-aware SQL references:
    - `ucx_kb/rag/schema.py`
    - `ucx_kb/rag/embed.py`
    - `ucx_kb/rag/search.py`

- Tests and compatibility checks updated:
  - `ucx_hermes/tests/unit/test_server.py`
  - `ucx_hermes/tests/unit/test_cli_main.py`
  - `ucx_hermes/tests/unit/test_api_runner.py`
  - `ucx_hermes/tests/unit/test_saga_review_orchestrator.py`
  - `ucx_hermes/tests/integration/test_executor_env.py`

## Backward Compatibility

- Approval semantics now explicitly allow `LLM-as-judge` in addition to human reviewers for planning and policy-gated outcomes.
- Issue execution eligibility remains label-driven, but governance now requires planning-package approval before execution transition.
- Runtime no longer supports legacy CLI executor paths for LLM stages; API executor names are required.
- UCX KB queries now honor `RAG_SCHEMA` with schema-name validation; default schema remains `nexus` when `RAG_SCHEMA` is unset.

## Validation Evidence

- Targeted UCX Hermes test suite executed with UCX source path:
  - `PYTHONPATH=ucx_hermes/src pytest ucx_hermes/tests/unit/test_server.py ucx_hermes/tests/unit/test_cli_main.py ucx_hermes/tests/unit/test_api_runner.py ucx_hermes/tests/unit/test_saga_review_orchestrator.py ucx_hermes/tests/integration/test_executor_env.py`
  - Result: `109 passed`.
