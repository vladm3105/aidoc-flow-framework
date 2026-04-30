# CHANGELOG — Framework v0.20.1

**Release Date**: 2026-04-30

## Summary

Governance migration to SDD v3.2 baseline in `governance/`, including core docs, bridge docs, setup/templates, workflow references, and legacy TASKS sync deprecation.

## Changes

- Updated core governance docs to v3.2 chain language:
  - `governance/README.md`
  - `governance/GOVERNANCE_RULES.md`
  - `governance/SDD_DEPTH_GUIDE.md`
  - `governance/AI_ISSUE_LIFECYCLE.md`
- Refactored bridge docs to v3 semantics:
  - `governance/TASKS_IPLAN_BRIDGE.md`
  - `governance/TSPEC_BDD_QA_BRIDGE.md`
  - `governance/CHG_GOVERNANCE_BRIDGE.md`
- Normalized setup/template/config defaults to `ai_dev_flow_v3`:
  - `governance/setup/SETUP_GUIDE.md`
  - `governance/setup/CONFIG.md`
  - `governance/templates/sdd_config.yaml`
  - `governance/templates/pre-commit-config.framework-library.yaml`
  - `governance/setup/PRECOMMIT_HOOK_LIBRARY_CONSUMER_GUIDE.md`
  - `governance/templates/qa/01-testing-strategy.md`
- Updated label registry text:
  - `governance/github/LABEL_REGISTRY.yaml`
- Deprecated legacy TASKS sync workflow/script in active runbooks:
  - `governance/github/GITHUB_WORKFLOWS.md`
  - `governance/scripts/workflows/sync_tasks_from_issues.py`
- Updated QA script registry mapping from TSPEC to TDD:
  - `governance/scripts/workflows/execute_qa_tests.py`
- Updated migration helper mappings and setup script references:
  - `governance/scripts/apply_doc_path_aliases.py`
  - `governance/scripts/setup_project_hybrid.sh`

## Backward Compatibility

- Legacy TASKS sync script is retained as deprecated compatibility stub.
- Active governance guidance no longer relies on legacy layer artifacts.
