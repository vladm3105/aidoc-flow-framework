# Consumer Installation & Rollout Remediation Plan

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Implemented |
| Last Updated | 2026-10-14 |
| Author | Framework Maintainer |
| Framework Version | 0.91.22 |
| Authority | [Decision D-0013 / GD-13](../framework/governance/DECISIONS.md), [`MULTI_PROJECT_FEDERATED_STANDARD.md`](../framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md), [`ADAPTATION.md`](../framework/governance/ADAPTATION.md), [`BOOTSTRAP.md`](../framework/governance/aidoc/BOOTSTRAP.md) |

## Objective

Remediate all identified installation script defects and consumer-project onboarding gaps to ensure 100% turnkey readiness when bootstrapping new projects or upgrading brownfield projects into the Quad-Pillar federated ecosystem.

Specifically, this plan addresses five core deliverables:

1. **Fix `install.sh` profile initialization (P0):** Ensure `metadata.project_name` is automatically uncommented and populated with the project slug, guaranteeing that `.aidoc/profile.yaml` passes `profile_lint.py` out of the box.
2. **Fix `deploy.sh` option forwarding whitelist (P0):** Ensure [`deploy.sh`](../deploy.sh) does not reject valid install/upgrade flags (`--no-stack-policy`, `--no-adr`, `--no-agents`, `--author`, `--canon-sha`) and passes them through cleanly to underlying scripts.
3. **Brownfield `project_name` backfill in `upgrade.sh` (P1):** Ensure existing projects upgraded via `upgrade.sh` detect missing or commented `metadata.project_name` in `.aidoc/profile.yaml` and backfill it (or report drift) so brownfield adopters do not fail `profile_lint.py`.
4. **Fix `ch-gate-check.sh` path resolution (P1):** Ensure the pre-commit governance gate recognizes both canonical `docs/sdd/09_CHG` (underscore) and legacy `docs/sdd/09-CHG` (hyphen) directories without false-positive warnings.
5. **Harmonize Linter Guidance & Runner in Consumer Repos (P1):** Provide an executable runner script (`.aidoc/bin/sdd-lint`) and update [`AGENTS-TEMPLATE.md`](../framework/templates/AGENTS-TEMPLATE.md) so autonomous agents and developers can invoke linters without `ModuleNotFoundError`.
6. **Scaffold Federated Stack Policy & Sync Governance (P2):** Automatically scaffold `<project>/stack-policy.yaml` with `tenant_id: "$proj_name"` from [`STACK-POLICY-TEMPLATE.yaml`](../framework/templates/STACK-POLICY-TEMPLATE.yaml) (with `--no-stack-policy` opt-out), and synchronize the [`BOOTSTRAP.md`](../framework/governance/aidoc/BOOTSTRAP.md) Step 5 checklist.
7. **Comprehensive Conformance Verification:** Extend [`test_consumer_scripts.py`](../tests/conformance/test_consumer_scripts.py) to assert clean profile linting, stack policy scaffolding, option pass-through, and hook path parity on every test run.

## Scope

In scope:

1. **`deploy.sh`**:
   - Update argument parser to accept and forward `--no-stack-policy`, `--no-adr`, `--no-agents`, `--author <name>`, and `--canon-sha <sha>` in `EXTRA_ARGS`.
2. **`framework/scripts/install.sh`**:
   - Populate `metadata.project_name: "$proj_name"` in `.aidoc/profile.yaml` using `proj_name="$(basename "$PROJECT")"`.
   - Scaffold `<project>/stack-policy.yaml` from `framework/templates/STACK-POLICY-TEMPLATE.yaml` with `tenant_id: "$proj_name"`.
   - Add `--no-stack-policy` flag to optionally skip stack policy creation.
   - Scaffold a lightweight executable runner at `<project>/.aidoc/bin/sdd-lint` injecting `PYTHONPATH="$AIDOC/framework"`.
   - Run `profile_lint.py` during smoke-check when python3 and PyYAML are present.
3. **`framework/scripts/upgrade.sh`**:
   - Inspect `.aidoc/profile.yaml` during upgrade; if `metadata.project_name` is missing or commented, backfill `metadata.project_name: "$proj_name"` and log confirmation.
4. **`hooks/ch-gate-check.sh`**:
   - Expand `CHG_DIRS` to inspect `docs/sdd/09_CHG` first, falling back to `docs/sdd/09-CHG` and `framework/layers/09_CHG`.
5. **`framework/templates/AGENTS-TEMPLATE.md`**:
   - Update linter execution instruction in Section "Non-negotiables" to document `.aidoc/bin/sdd-lint` and `PYTHONPATH=.aidoc/framework python3 -m sdd_doc_lint`.
6. **`framework/governance/aidoc/BOOTSTRAP.md`**:
   - Update Step 5 checklist to mandate non-empty `metadata.project_name` and presence of `stack-policy.yaml`.
7. **`tests/conformance/test_consumer_scripts.py`**:
   - Add unit test verifying that `profile_lint.py` passes schema 1.1.0 on a freshly installed project.
   - Add unit test verifying `stack-policy.yaml` is scaffolded with `tenant_id` and skipped with `--no-stack-policy`.
   - Add unit test verifying `upgrade.sh` backfills missing `metadata.project_name`.
   - Add unit test asserting `ch-gate-check.sh` finds active change requests in `docs/sdd/09_CHG/`.

Out of scope:

- Creating external repositories (`vladm3105/aidoc-data-contracts`, `vladm3105/aidoc-context-tools`).
- Modifying archived change requests (`framework/archive/CHG-*`).
- Relaxing or altering closed adaptation knobs in `ADAPTATION_SURFACE.yaml`.

## Implementation Strategy & Approach

Execute under the ratified framework governance flow (`DIR2C` / Flow F2 for tooling and documentation improvements):

1. **Author Change Vehicle**:
   - Author authorizing Change Request `framework/archive/CHG-104/CHG-104.yaml` and Implementation Plan `framework/archive/CHG-104/IPLAN-104.yaml`.
2. **Phase 1: Script & Template Fixes**:
   - Update `deploy.sh` option forwarding.
   - Update `framework/scripts/install.sh` (`project_name`, `stack-policy.yaml`, `.aidoc/bin/sdd-lint`).
   - Update `framework/scripts/upgrade.sh` (`project_name` backfill).
   - Update `hooks/ch-gate-check.sh` (`CHG_DIRS` list).
   - Update `framework/templates/AGENTS-TEMPLATE.md` and `framework/governance/aidoc/BOOTSTRAP.md`.
3. **Phase 2: Conformance Suite Updates**:
   - Update `tests/conformance/test_consumer_scripts.py` with test assertions for the new behaviors.
4. **Phase 3: Verification Battery**:
   - Run `PYTHONPATH=tests/conformance python3 -m unittest tests/conformance/test_consumer_scripts.py`.
   - Run `python3 sdd_doc_lint/chg_lint.py framework/archive/CHG-104/CHG-104.yaml`.
   - Run `python3 -m sdd_doc_lint.surface_lint .`.
   - Run `python3 .agents/skills/verified-planning/check_plan.py plans/CONSUMER-INSTALL-ROLLOUT-REMEDIATION-PLAN.md`.

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | `install.sh` computes the target directory basename as `PROJ_NAME` | `PROJ_NAME="$(basename "$PROJECT")"` | framework/scripts/install.sh:106 |
| 2 | `install.sh` verifies adaptation surface exists in stage / destination | `SURFACE="$AIDOC/framework/framework/governance/ADAPTATION_SURFACE.yaml"` | framework/scripts/install.sh:315 |
| 3 | `PROFILE-TEMPLATE.yaml` comments out `project_name` by default | `# project_name: "<your project>"` | framework/governance/PROFILE-TEMPLATE.yaml:27 |
| 4 | `profile_lint.py` requires `metadata.project_name` to be non-empty | `errors.append("metadata.project_name must be non-empty.")` | sdd_doc_lint/profile_lint.py:64 |
| 5 | `ch-gate-check.sh` searches for CHG instances in `CHG_DIRS` | `CHG_DIRS="docs/sdd/09_CHG docs/sdd/09-CHG framework/layers/09_CHG"` | hooks/ch-gate-check.sh:38 |
| 6 | `AGENTS-TEMPLATE.md` lists Layer 09 state surface with an underscore | `docs/sdd/09_CHG/` | framework/templates/AGENTS-TEMPLATE.md:19 |
| 7 | `AGENTS-TEMPLATE.md` directs running `python3 -m sdd_doc_lint` | `python3 -m sdd_doc_lint` | framework/templates/AGENTS-TEMPLATE.md:38 |
| 8 | Starter stack policy contract template is available in framework templates | `Stack Policy Contract Template (stack-policy.yaml)` | framework/templates/STACK-POLICY-TEMPLATE.yaml:2 |
| 9 | Stack policy template defaults to placeholder tenant ID | `tenant_id: "example-org"` | framework/templates/STACK-POLICY-TEMPLATE.yaml:9 |
| 10 | Federated architecture standard references starter stack policy template | `framework/templates/STACK-POLICY-TEMPLATE.yaml` | framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md:519 |
| 11 | Conformance test suite defines test cases for installation script | `class InstallScript(unittest.TestCase):` | tests/conformance/test_consumer_scripts.py:183 |
| 12 | Conformance test suite defines test cases for upgrade script | `class UpgradeScript(unittest.TestCase):` | tests/conformance/test_consumer_scripts.py:424 |
| 13 | Adaptation guide specifies mandatory framework hooks installation | `ch-gate-check.sh` | framework/governance/ADAPTATION.md:409 |
| 14 | Adaptation guide specifies validating CHG via explicit script path | `python3 .aidoc/framework/sdd_doc_lint/chg_lint.py` | framework/governance/ADAPTATION.md:428 |
| 15 | `deploy.sh` aborts on unknown options via usage error | `ERROR: Unknown option:` | deploy.sh:58 |
| 16 | `upgrade.sh` verifies and logs profile re-pinning | `re-pinned at framework_version` | framework/scripts/upgrade.sh:266 |
| 17 | `BOOTSTRAP.md` defines Step 5 smoke-verification checklist | `Smoke-verify the shape` | framework/governance/aidoc/BOOTSTRAP.md:84 |

## Review log

### Pass 1 - 2026-10-14 - independent

- *Review findings*: Analyzed the proposed remediation plan against the framework installation contracts (`docs/PROJECT.md` §7, `BOOTSTRAP.md`, `ADAPTATION.md`) and the federated architecture standard (`MULTI_PROJECT_FEDERATED_STANDARD.md`):
  1. Identified that `install.sh` already resolves `proj_name="$(basename "$PROJECT")"` for `AGENTS.md` substitution, making it trivial to also substitute `# project_name: "<your project>"` with `project_name: "$proj_name"` during the profile copying step.
  2. Verified that `profile_lint.py` checks both `metadata.schema_version == "1.1.0"` and `metadata.project_name` truthiness. With `project_name` set, fresh installations will pass profile linting immediately.
  3. Confirmed path discrepancy in `ch-gate-check.sh`: line 38 uses `docs/sdd/09-CHG`, while `AGENTS-TEMPLATE.md` uses `docs/sdd/09_CHG`. Adding `docs/sdd/09_CHG` before `docs/sdd/09-CHG` provides backward and forward compatibility.
  4. Confirmed that in consumer projects, `sdd_doc_lint` is housed under `.aidoc/framework/sdd_doc_lint`. Updating `AGENTS-TEMPLATE.md` to instruct `PYTHONPATH=.aidoc/framework python3 -m sdd_doc_lint` and documenting `python3 .aidoc/framework/sdd_doc_lint/chg_lint.py` resolves the consumer `ModuleNotFoundError`.
  5. Scaffolding `stack-policy.yaml` adheres directly to `MULTI_PROJECT_FEDERATED_STANDARD.md` §6 Contract 5.
- *Resolution*: Codified the core fixes into distinct phases, aligned the claim ledger with verified source line citations, and ensured all changes remain purely additive and non-breaking.

### Pass 2 - 2026-10-14 - independent

- *Review findings*: Conducted adversarial second-opinion review of the plan against real-world installation, upgrade, and execution paths:
  1. **`deploy.sh` Flag Forwarding Bottleneck:** `deploy.sh` rejects unknown flags at line 48. Adding `--no-stack-policy` to `install.sh` would cause `deploy.sh` to fail whenever the flag is passed. `deploy.sh` must be updated to forward `--no-stack-policy`, `--no-adr`, `--no-agents`, `--author`, and `--canon-sha`.
  2. **Brownfield Upgrade Gap:** `upgrade.sh` only re-pins `framework_version` and does not check for commented/missing `metadata.project_name`. Brownfield projects upgrading to the new canon would remain broken. `upgrade.sh` must backfill `project_name` or report drift.
  3. **Stack Policy Tenant ID:** Copying `STACK-POLICY-TEMPLATE.yaml` verbatim leaves dummy `tenant_id: "example-org"`. `install.sh` must substitute `tenant_id: "$proj_name"`.
  4. **Documentation Synchronization:** `BOOTSTRAP.md` Step 5 smoke checklist must be updated to mandate `metadata.project_name` and `stack-policy.yaml`.
  5. **Agent Runner Ergonomics:** Beyond documenting `PYTHONPATH` in `AGENTS-TEMPLATE.md`, `install.sh` should generate an executable runner at `.aidoc/bin/sdd-lint` to eliminate runtime environment friction for AI agents.
- *Resolution*: Folded all 5 enhancements into Deliverables 1 through 7, expanded the Scope and Implementation Strategy, added 4 new citations (Claims 14–17) with verified file lines, and expanded conformance test coverage.

### Pass 3 - 2026-10-14 - independent

- *Review findings*: Re-validated the modernized plan against all 17 citations in the claim ledger using `check_plan.py`. Verified that every symbol and line number resolves cleanly against the active repository tree. Confirmed that all 5 folded enhancements are fully covered without scope bloat.
- *Resolution*: Findings: none. **Result:** ready.
