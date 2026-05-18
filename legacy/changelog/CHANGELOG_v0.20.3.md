# CHANGELOG — Framework v0.20.3

**Release Date**: 2026-04-30

## Summary

Executed strict repository-wide legacy naming cleanup, replacing remaining `ai_dev_flow`/`ai_dev_ssd_flow` token variants with `ucx_flow_v3`/UCX Flow naming in active and archived content.

## Changes

- Applied strict token replacement at repository root scope:
  - Replaced legacy path/name variants including:
    - `ai_dev_flow`
    - `ai_dev_ssd_flow`
    - `ai-dev-flow`
    - `AI Dev Flow` and related case variants
- Updated documentation, templates, plans, changelogs, governance docs, and test references to align with UCX Flow naming.
- Updated mcp_ucx source/doc references to remove legacy naming tokens.
- Corrected post-replacement smoke-test helper text duplication in:
  - `tests/smoke/test_brd_hook_scripts_smoke.py`

## Validation Evidence

- Repository-wide legacy token scan returned zero matches after cleanup.
- Targeted test validation executed successfully:
  - `pytest mcp_ucx/tests/unit/test_scaffold_init.py mcp_ucx/tests/integration/test_creation_profile_contracts_integration.py tests/smoke/test_sample.py tests/smoke/test_brd_hook_scripts_smoke.py`
  - Result: 23 passed, 4 skipped

## Backward Compatibility

- No runtime interface changes were introduced by this release.
- This release updates textual and path naming references; consumers that parse legacy naming strings from repository docs/files should update downstream assumptions.
