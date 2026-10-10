# Root README.md Reconciliation & Version Pin Conformance Guard Plan

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Ready |
| Last Updated | 2026-10-10 |
| Author | Framework Maintainer |
| Framework Version | 0.91.3 |
| Authority | [Decision GD-72](../framework/governance/DECISIONS.md) & [CHG-84](../framework/archive/CHG-84/CHG-84.yaml) |

## Objective

Reconcile root `README.md` and `plans/TECHSTACK-ALIGNMENT-PLAN.md` with live framework version `0.91.3`, reflect platform technology stack architecture guidance, and establish an automated conformance guard in `tests/conformance/test_sync_version_refs.py` preventing future version drift in root `README.md`.

## Status

Ready for execution under Change Request `CHG-84` (C1 Documentation and Conformance Guard).

## Scope

In scope:

1. Reconcile root `README.md` tracking spec version from `0.91.2` to `0.91.3` (as of 2026-10-10).
2. Update workflow counts in `README.md` to reflect 22 declarative CNCF Serverless Workflows (13 core lifecycle + 9 review-remediation).
3. Document platform reference architecture in `README.md` pointing to `framework/governance/RECOMMENDED_PLATFORM_STACK.md` and `framework/governance/aidoc/`.
4. Reconcile `plans/TECHSTACK-ALIGNMENT-PLAN.md` Document Control header to framework version `0.91.3`.
5. Add automated conformance test `test_root_readme_spec_version_matches` in `tests/conformance/test_sync_version_refs.py`.

Out of scope:

- Adding root `README.md` to automatic regex sweeps in `hooks/sync-version-refs.sh` (preventing prose clobbering).
- Normative changes to core SDD layers.

## Approach

Execute under the DIR2C (iplan_to_code) flow:

1. Create isolated task worktree `feature/chg-84-reconcile-readme`.
2. Author authorizing change request `CHG-84.yaml` and implementation plan `IPLAN-84.yaml`.
3. Update `README.md` and `plans/TECHSTACK-ALIGNMENT-PLAN.md`.
4. Implement `test_root_readme_spec_version_matches` in `tests/conformance/test_sync_version_refs.py`.
5. Validate via `chg_lint.py`, `check_plan.py`, pytest conformance suite, and pre-commit hooks.
6. Perform multi-agent self-review per `OPS-0065`.

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Framework version is canonical in framework/VERSION | 0.91.3 | framework/VERSION:1 |
| 2 | Root README tracks framework spec version | tracking framework spec | README.md:316 |
| 3 | Conformance suite verifies metadata version pins | test_metadata_pins_covered | tests/conformance/test_sync_version_refs.py:81 |
| 4 | Platform technology stack reference architecture is defined | Recommended Platform Technology Stack | framework/governance/RECOMMENDED_PLATFORM_STACK.md:1 |

## Review log

### Pass 1 - 2026-10-10 - independent

- *Review findings*: Verified that root README.md exclusion from `hooks/sync-version-refs.sh` was intentional per issue #927 to protect prose, making a dedicated conformance test assertion the ideal enforcement mechanism.
- *Resolution*: Added `test_root_readme_spec_version_matches` to `test_sync_version_refs.py` ensuring CI fails if root README.md is not updated during framework version bumps.

### Pass 2 - 2026-10-10 - independent

- *Review findings*: Verified that claim ledger citations resolve against local active repository tree with zero missing symbols and zero path errors.
- *Resolution*: Findings: none. Result: ready.
