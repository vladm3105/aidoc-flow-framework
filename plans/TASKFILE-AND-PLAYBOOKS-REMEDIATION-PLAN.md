# Implementation Plan: Root Taskfile Orchestration, Consumer `.aidoc` Audit, Script Remediation, and Playbook Alignment

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-17 |
| Author | Framework Maintainer |
| Framework Version | 0.96.1 |
| Linked Issue | #1007 |
| Authority | [CHG_REQUEST_FLOWS.md](../framework/governance/CHG_REQUEST_FLOWS.md), [WORKTREE_FLOW.md](../framework/governance/WORKTREE_FLOW.md), [LINT_RULES.md](../framework/governance/LINT_RULES.md) |

---

## 1. Objective

This change delivers a cohesive, comprehensive modernization of the framework's local task tooling, consumer-facing `.aidoc` architecture, installer/upgrade scripts, and layer playbooks across four core areas:

1. **Root `Taskfile.yml` Orchestration:** Introduces a canonical, developer- and agent-friendly root `Taskfile.yml` for `aidoc-flow-framework` exposing key workflows (`task test`, `task test:unit`, `task test:conformance`, `task test:acceptance`, `task lint`, `task chg-lint`, `task swf-lint`, `task pre-push`, `task links`, `task sync-versions`).
2. **Consumer `.aidoc` Part & Dogfood Profile Audit & Remediation:**
   - **Repository Dogfood Profile:** Modernizes `.aidoc/profile.yaml` to schema `1.1.0`, populates `project_name: "aidoc-flow-framework"`, bumps `framework_version` from `0.68.3` to `0.96.2`, and passes `profile_lint.py` cleanly.
   - **Repository Dogfood Learnings:** Modernizes `.aidoc/learning/learnings.md` graduation rule to remove graduation to retired `DECISIONS.md`.
   - **Scaffold Profile Template (`PROFILE-TEMPLATE.yaml`):** Scrubs legacy "symlink to shared framework" comments, replacing them with sanctioned submodule / pinned-copy guidance; aligns `audit_threshold` documentation with deterministic `BTV PASS` and zero blocking findings while preserving the column-0 commented key anchor `# audit_threshold:`.
   - **Workstation Adaptation Guide (`docs/ADAPTATION-GUIDE.md`):** Scrubs claims that raw symlinks are the "canonical form" (which contradicts `AIDOC_WORKSTATION_STANDARD.md:341`); updates the `.aidoc/` directory layout diagram to include all Quad-Pillar components (`Taskfile.yml`, `stack-policy.yaml`, `engine/engine.yaml`, `contracts/`, `ctx-tools/`, `cache/`); corrects CHG path to `docs/sdd/09_CHG/`.
   - **Consumer Governance Guides (`framework/governance/aidoc/`):** Scrubs "symlink convention" references in `README.md` and `UPGRADE-RUNBOOK.md`; annotates `DECISIONS.md` references in `AIDOC.md` and `BOOTSTRAP.md` as historical tombstones; replaces "consumer changelog" wording in `UPGRADE-RUNBOOK.md` with structured change records (`docs/sdd/09_CHG/`).
   - **Consumer Taskfile Template (`TASKFILE-TEMPLATE.yml`):** Injects top-level `vars:` and `env:` blocks exporting `PYTHONPATH: '{{.PYTHONPATH | default ".aidoc/framework:framework"}}'` so all `task sdd:*` commands resolve vendored `sdd_doc_lint` modules without requiring site-packages installation.
3. **Scripts Remediation:**
   - Updates `deploy.sh` default deployment kind from `--kind symlink` to `--kind pin` to comply with `docs/AIDOC_WORKSTATION_STANDARD.md:341` and emits deprecation notices when `--kind symlink` is requested.
   - Enhances `deploy.sh` brownfield upgrade handling when `--kind` is omitted (`KIND_SPECIFIED=0`) to inspect target filesystem state (`[[ -L "$TARGET/.aidoc/framework" ]]`) and pass `--shared "$SHARED"` vs `--canon-dir "$SCRIPT_DIR"` matching `upgrade.sh`'s native auto-detection.
   - Reconciles `framework/scripts/upgrade.sh` Step 1 output to direct operators to inspect `framework/archive/CHG-*/` and GitHub Releases rather than the frozen `framework/CHANGELOG.md` (frozen at 0.94.0 per CHG-94).
4. **Playbooks Remediation:**
   - Annotates `governance/DECISIONS.md` in `framework/playbooks/09_CHG/document_control.md` as a historical tombstone (GD-24 / GD-71 / GD-78).
   - Updates `framework/playbooks/10_EVAL/README.md` to document the complete Three-Tier Architecture (`*-TEMPLATE.yaml`, `*-GRAPH-TEMPLATE.yaml`, `*-SWF-TEMPLATE.yaml`).
   - Corrects the gate archive path in `framework/playbooks/09_CHG/gate_spec_change.md` to reflect the flat `framework/archive/CHG-{NN}/` structure.
   - Fixes typo in `framework/playbooks/07_TDD/qa_lead.md` (`discorded` -> `discarded`).

---

## Review Log

### Pass 1: Architecture, Script Ergonomics & Governance Review

- **Gap Found 1 (Brownfield `deploy.sh` upgrade):** Previously `deploy.sh` unconditionally passed `--kind "$KIND"` to `upgrade.sh`. If `KIND` defaulted to `pin`, running `deploy.sh --target <symlink-repo>` would trigger `upgrade.sh`'s refusal: `refuse "--kind pin but .aidoc/framework is a link"`.
  - **Resolution:** Added `KIND_SPECIFIED` tracking in `deploy.sh`. For fresh installs, default to `pin`. For upgrades, pass `--kind` only if the user explicitly provided it, otherwise let `upgrade.sh` auto-detect the existing kind.
- **Gap Found 2 (`TASKFILE-TEMPLATE.yml` environment scope):** Preconditions in `TASKFILE-TEMPLATE.yml` check for `.aidoc/framework/sdd_doc_lint`, but without top-level `env: PYTHONPATH`, executing `python3 -m sdd_doc_lint` would fail with `ModuleNotFoundError` for all tasks (`lint`, `slice`, `render`, `graph-check`).
  - **Resolution:** Configured top-level `vars:` and `env:` blocks in `TASKFILE-TEMPLATE.yml` exporting `PYTHONPATH`.
- **Gap Found 3 (`task chg-lint` zero-argument failure):** `chg_lint.py` requires at least one file argument; running `task chg-lint` with empty `{{.CLI_ARGS}}` would fail with exit code 2.
  - **Resolution:** Enhanced `task chg-lint` to dynamically inspect `framework/archive/CHG-*` and select the latest change request if no argument is passed.
- **Gap Found 4 (Test coverage for default kind):** `test_consumer_scripts.py` only exercised `deploy.sh` with explicit `--kind pin`.
  - **Resolution:** Added `test_deploy_default_kind_is_pin` in `tests/conformance/test_consumer_scripts.py` asserting `framework.is_dir() and not framework.is_symlink()`.

### Pass 2: Architecture & Dogfood Store Validation

- **Gap Found 5 (Dogfood `.aidoc/profile.yaml` schema failure):** Running `python3 sdd_doc_lint/profile_lint.py .aidoc/profile.yaml` failed with `schema_version must be '1.1.0'` and missing `project_name`, plus an ancient `0.68.3` pin.
  - **Resolution:** Added Component 2 to remediate `.aidoc/profile.yaml` to schema 1.1.0, set `project_name: "aidoc-flow-framework"`, and pin `0.96.2`.
- **Gap Found 6 (`docs/ADAPTATION-GUIDE.md` symlink promotion):** Section 2 claimed `.aidoc/framework/` symlink was the "Canonical form" and omitted Quad-Pillar topology files from the directory diagram.
  - **Resolution:** Standardized Section 2 on Git submodule and pinned allowlist copy, and added all Quad-Pillar components (`Taskfile.yml`, `stack-policy.yaml`, `engine/engine.yaml`, etc.) to the layout.
- **Gap Found 7 (`PROFILE-TEMPLATE.yaml` metadata comments):** Line 28 documented `.aidoc/framework` as a symlink.
  - **Resolution:** Updated comment to reference git submodule or pinned copy.
- **Gap Found 8 (`.aidoc/learning/learnings.md` graduation rule):** Lines 9–10 still referenced graduating lessons to retired `framework/governance/DECISIONS.md`.
  - **Resolution:** Updated graduation target to GitHub issues and Change Requests per GD-71/GD-78.

### Pass 3: Independent Subagent Review (Adversarial Lenses)

- **Gap Found 9 (`deploy.sh` brownfield argument pairing):** In `deploy.sh`, if `KIND_SPECIFIED=0`, defaulting the argument pairing to `--canon-dir "$SCRIPT_DIR"` would cause `upgrade.sh` to immediately abort with `refuse "--canon-dir is for --kind pin; the symlink kind reads --shared"` when run on an existing symlink repo.
  - **Resolution:** Updated `deploy.sh` so when `KIND_SPECIFIED=0`, it tests `[[ -L "$TARGET/.aidoc/framework" ]]` to select `--shared "$SHARED"` vs `--canon-dir "$SCRIPT_DIR"`, perfectly matching `upgrade.sh`'s native auto-detection.
- **Gap Found 10 (`TASKFILE-TEMPLATE.yml` Go-Task `env:` evaluation):** In Go-Task 3.53.1, top-level `env:` does not evaluate sprig default filters on undefined variables, evaluating `PYTHONPATH` to an empty string `""` and breaking all python subcommands.
  - **Resolution:** Switched to declaring default in `vars: PYTHONPATH: '{{.PYTHONPATH | default ".aidoc/framework:framework"}}'` and referencing `env: PYTHONPATH: '{{.PYTHONPATH}}'`, preserving caller overrides while correctly providing fallbacks.
- **Gap Found 11 (`PROFILE-TEMPLATE.yaml` regex anchor protection):** `tests/conformance/test_governance.py` validates that all profile surface knobs are documented using the regex `^# ([a-z][a-z0-9_]*):`.
  - **Resolution:** Ensured the `# audit_threshold:` commentary in `PROFILE-TEMPLATE.yaml` retains `# audit_threshold:` starting at column 0.
- **Status:** **Result:** ready, no new findings. Zero load-bearing findings.

---

## Claim Ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | `deploy.sh` currently defaults `KIND` to `symlink` | `KIND="symlink"` | deploy.sh:16 |
| 2 | `deploy.sh` usage string declares default as `symlink` | `Deployment kind (default: symlink)` | deploy.sh:25 |
| 3 | `install.sh` defaults `KIND` to `pin` | `KIND="pin"` | framework/scripts/install.sh:79 |
| 4 | Workstation standard bans raw filesystem symlinks | `Raw filesystem symlinks` | docs/AIDOC_WORKSTATION_STANDARD.md:341 |
| 5 | `upgrade.sh` logs instructions pointing to frozen `CHANGELOG.md` | `canon changelog: $CANON/framework/CHANGELOG.md` | framework/scripts/upgrade.sh:189 |
| 6 | Dogfood profile has schema `1.0.0` and pin `0.68.3` | `schema_version: "1.0.0"` | .aidoc/profile.yaml:16 |
| 7 | `ADAPTATION-GUIDE.md` claims symlink is canonical form | `.aidoc/framework/` is a symlink | docs/ADAPTATION-GUIDE.md:85 |
| 8 | `PROFILE-TEMPLATE.yaml` comments state symlink | `symlink to shared framework` | framework/governance/PROFILE-TEMPLATE.yaml:28 |
| 9 | `learnings.md` references graduating to `DECISIONS.md` | `framework/governance/DECISIONS.md` | .aidoc/learning/learnings.md:10 |
| 10 | `document_control.md` cites `governance/DECISIONS.md` without tombstone note | `(Document control convention)` | framework/playbooks/09_CHG/document_control.md:171 |
| 11 | `10_EVAL/README.md` lists only single template without Three-Tier references | `framework/layers/10_EVAL/EVAL-TEMPLATE.yaml` | framework/playbooks/10_EVAL/README.md:64 |
| 12 | `qa_lead.md` contains typo "discorded" | `discorded by the synthesizer` | framework/playbooks/07_TDD/qa_lead.md:57 |
| 13 | `TASKFILE-TEMPLATE.yml` linter task lacks explicit `PYTHONPATH` | `python3 -m sdd_doc_lint {{.SDD_DIR}} {{.CLI_ARGS}}` | framework/templates/TASKFILE-TEMPLATE.yml:20 |

---

## 4. Proposed Changes

### Component 1: Root Taskfile Orchestration

- **[NEW] `Taskfile.yml`**: Exposes canonical root workflows (`task test`, `task test:unit`, `task test:conformance`, `task test:acceptance`, `task lint`, `task chg-lint`, `task swf-lint`, `task pre-push`, `task links`, `task sync-versions`).

### Component 2: Consumer `.aidoc` Part & Dogfood Profile Remediation

- **[MODIFY] `.aidoc/profile.yaml`**: Update schema to `1.1.0`, set `project_name: "aidoc-flow-framework"`, bump `framework_version` to `0.96.2`.
- **[MODIFY] `.aidoc/learning/learnings.md`**: Update graduation target to GitHub issues and Change Requests.
- **[MODIFY] `framework/governance/PROFILE-TEMPLATE.yaml`**: Align commentary with Git submodules / pinned copies and deterministic `BTV PASS`, preserving column-0 `# audit_threshold:`.
- **[MODIFY] `docs/ADAPTATION-GUIDE.md`**: Decommission raw symlinks as canonical form, update directory layout diagram with Quad-Pillar topology.
- **[MODIFY] `framework/governance/aidoc/README.md` & `UPGRADE-RUNBOOK.md`**: Scrub symlink convention and consumer changelog wording.
- **[MODIFY] `framework/governance/aidoc/AIDOC.md` & `BOOTSTRAP.md`**: Annotate `DECISIONS.md` references as historical tombstones.
- **[MODIFY] `framework/templates/TASKFILE-TEMPLATE.yml`**: Add `vars:` and `env:` blocks exporting `PYTHONPATH`.

### Component 3: Scripts Remediation

- **[MODIFY] `deploy.sh`**: Default `KIND="pin"`, warn on `symlink`, auto-detect target kind pairing when `KIND_SPECIFIED=0`.
- **[MODIFY] `framework/scripts/upgrade.sh`**: Point Step 1 instructions to `framework/archive/CHG-*/` and GitHub Releases.
- **[MODIFY] `tests/conformance/test_consumer_scripts.py`**: Add `test_deploy_default_kind_is_pin`.

### Component 4: Playbooks Remediation

- **[MODIFY] `framework/playbooks/09_CHG/document_control.md`**: Annotate `governance/DECISIONS.md` tombstone.
- **[MODIFY] `framework/playbooks/10_EVAL/README.md`**: Document Three-Tier Architecture.
- **[MODIFY] `framework/playbooks/09_CHG/gate_spec_change.md`**: Fix archive path.
- **[MODIFY] `framework/playbooks/07_TDD/qa_lead.md`**: Fix typo `discorded` -> `discarded`.

### Component 5: Governance & Version Fanout

- **[NEW] `framework/archive/CHG-115/CHG-115.yaml` & `IPLAN-115.yaml`**: Ratify DIR2C Change Request for Level C2 Architecture, Spec & Tooling change.
- **[MODIFY] `framework/VERSION`**: Bump from `0.96.1` to `0.96.2`.
- **[MODIFY] `hooks/sync-version-refs.sh`**: Add `0.96.1` to `OLD_VERSIONS` and execute sync.

---

## 5. Verification Plan

### Automated Tests

```bash
python3 sdd_doc_lint/profile_lint.py .aidoc/profile.yaml
python3 sdd_doc_lint/chg_lint.py framework/archive/CHG-115/CHG-115.yaml
python3 -m sdd_doc_lint.swf_lint framework/layers/ framework/governance/
PYTHONPATH=tests/conformance python3 -m unittest tests/conformance/test_consumer_scripts.py
python3 -m unittest discover -s sdd_doc_lint/tests
python3 -m unittest discover -s tests/unit
PYTHONPATH=tests/conformance python3 -m unittest discover -s tests/conformance
bash hooks/pre_push_check.sh
```

### Taskfile Verification

```bash
task --list
task test
task lint
task chg-lint
task swf-lint
task links
```
