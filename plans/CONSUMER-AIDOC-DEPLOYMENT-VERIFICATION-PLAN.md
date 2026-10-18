# Implementation Plan: Consumer `.aidoc` Verification, Parity Alignment, and Deployment Readiness

## Executive Summary & Verification Findings

This plan establishes end-to-end verification and alignment between the latest framework specifications (including **v0.96.3**, Three-Tier Architecture, Layer 09 template additions, and deterministic BTV PASS quality floors from CHG-116) and the consumer-facing `.aidoc/` workstation layout.

A comprehensive audit of the repository's `.aidoc/` infrastructure, templates, scripts, and governance contracts revealed the following findings:

1. **In-Repo Dogfood Profile Stale Version:**
   - [`.aidoc/profile.yaml`](../.aidoc/profile.yaml#L20) still pins `framework_version: "0.96.2"` and `last_updated: "2026-10-17"`, lagging behind [`framework/VERSION`](../framework/VERSION#L1) (`0.96.3`).
2. **Governance Guide Example Literal Stale Version:**
   - [`framework/governance/aidoc/AIDOC.md`](../framework/governance/aidoc/AIDOC.md#L117) cites an example Git submodule pin as `framework/v0.96.2` rather than `framework/v0.96.3`.
3. **Consumer Taskfile Capability Gap:**
   - While the framework ratified new automated linters (`chg_lint` for Change Requests and `swf_lint` for CNCF Serverless Workflows), [`framework/templates/TASKFILE-TEMPLATE.yml`](../framework/templates/TASKFILE-TEMPLATE.yml) lacks canonical tasks exposing them (`chg-lint`, `swf-lint`, and `profile-lint`). Consumer projects therefore lack direct Taskfile shortcuts to validate their Layer 09 Change Requests, Serverless Workflows, and adaptation profiles.
4. **Git Submodule Safety Guard in `upgrade.sh`:**
   - When a consumer project uses a Git submodule for `.aidoc/framework`, running `upgrade.sh` blindly treats it as a pinned copy, swaps directories, and wipes the submodule's `.git` pointer. A guard is required to detect submodule linkages and prevent destructive overwrites without explicit `--force`.
5. **Scaffolding and Deployment Verification:**
   - [`deploy.sh`](../deploy.sh), [`framework/scripts/install.sh`](../framework/scripts/install.sh), and [`framework/scripts/upgrade.sh`](../framework/scripts/upgrade.sh) correctly deploy allowlist files (`framework/`, `docs/`, `hooks/`, `sdd_doc_lint/`, `tests/` excluding `archive/`). Live testing confirmed that newly placed Layer 09 templates (`CHG-SWF-TEMPLATE.yaml` and `CHG-GRAPH-TEMPLATE.yaml`) and modernized BTV PASS templates are successfully deployed to consumer `.aidoc/framework/`.
   - The test suite [`tests/conformance/test_consumer_scripts.py`](../tests/conformance/test_consumer_scripts.py) passes 48/48 tests cleanly.

This plan details the exact remediation and verification steps to bring `.aidoc` into 100% parity with framework `0.96.3` and guarantee consumer deployment readiness.

---

## User Review Required

> [!NOTE]
> All changes are backward-compatible. Adding `chg-lint`, `swf-lint`, and `profile-lint` tasks to [`framework/templates/TASKFILE-TEMPLATE.yml`](../framework/templates/TASKFILE-TEMPLATE.yml) and root [`Taskfile.yml`](../Taskfile.yml) is purely additive and enhances consumer project autonomy.

<!-- separator -->

> [!IMPORTANT]
> The change will be implemented via an authorized Change Request (**CHG-117**, Flow DIR2C, Level C1) and Implementation Plan (**IPLAN-117**), preserving all governance gates and pre-modification snapshots in `framework/archive/CHG-117/`.

---

## Open Questions

None. The workstation architecture, adaptation surface, and deployment scripts are strictly codified under [`docs/AIDOC_WORKSTATION_STANDARD.md`](../docs/AIDOC_WORKSTATION_STANDARD.md) and [`framework/governance/aidoc/`](../framework/governance/aidoc/).

---

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | In-repo dogfood profile pins framework version 0.96.3 | `framework_version: "0.96.3"` | .aidoc/profile.yaml:20 |
| 2 | Canonical AIDOC governance reference cites example submodule tag 0.96.3 | `framework/v0.96.3` | framework/governance/aidoc/AIDOC.md:117 |
| 3 | Workstation Taskfile template defines lint task over SDD_DIR | `lint:` | framework/templates/TASKFILE-TEMPLATE.yml:18 |
| 4 | Consumer copy set allowlist includes framework directory | `framework/` | framework/scripts/allowlist.txt:8 |
| 5 | Consumer copy set allowlist excludes framework archive | `!framework/archive/` | framework/scripts/allowlist.txt:13 |
| 6 | Unified deploy.sh script declares kind option supporting pin or symlink | `--kind <pin\|symlink>` | deploy.sh:26 |
| 7 | Unified deploy.sh defaults deployment kind to pin for fresh installs | `KIND="pin"` | deploy.sh:74 |
| 8 | Install script scaffolds canonical SDD tasks from TASKFILE-TEMPLATE.yml | `TASKFILE-TEMPLATE.yml` | framework/scripts/install.sh:275 |
| 9 | Install script scaffolds engine config from ENGINE-CONFIG-TEMPLATE.yaml | `ENGINE-CONFIG-TEMPLATE.yaml` | framework/scripts/install.sh:303 |
| 10 | Install script scaffolds backward-compatible runner at .aidoc/bin/sdd-lint | `RUNNER_EOF` | framework/scripts/install.sh:320 |
| 11 | Upgrade script re-pins metadata.framework_version in profile.yaml | `framework_version:` | framework/scripts/upgrade.sh:262 |
| 12 | Upgrade script harmonizes workstation layout scaffolding missing Taskfile | `Harmonize workstation layout` | framework/scripts/upgrade.sh:271 |
| 13 | Conformance tests assert install script creates .aidoc/Taskfile.yml | `taskfile = self.project / ".aidoc" / "Taskfile.yml"` | tests/conformance/test_consumer_scripts.py:415 |
| 14 | Canonical PROFILE-TEMPLATE declares framework_version 0.96.3 | `framework_version: "0.96.3"` | framework/governance/PROFILE-TEMPLATE.yaml:26 |
| 15 | Canonical AIDOC-SCAFFOLD-TEMPLATE carries framework version 0.96.3 | `\| Framework Version \| 0.96.3 \|` | framework/governance/aidoc/AIDOC-SCAFFOLD-TEMPLATE.md:11 |
| 16 | AGENTS-TEMPLATE instructs agents to validate native graph via task sdd:graph-check | `task sdd:graph-check` | framework/templates/AGENTS-TEMPLATE.md:37 |
| 17 | Workstation standard documents Canonical SDD Tasks specification | `Canonical SDD Tasks` | docs/AIDOC_WORKSTATION_STANDARD.md:343 |
| 18 | Upgrade script inspects Taskfile graph tasks presence | `lacks graph or SDD lint tasks` | framework/scripts/upgrade.sh:276 |
| 19 | Conformance test scaffolds stack policy and linter runner | `def test_scaffolds_stack_policy_and_linter_runner` | tests/conformance/test_consumer_scripts.py:406 |
| 20 | Upgrade script detects kind via symlink check | `if [ -L "$FW" ]; then KIND=symlink; else KIND=pin; fi` | framework/scripts/upgrade.sh:106 |
| 21 | Root Taskfile defines chg-lint task | `chg-lint:` | Taskfile.yml:68 |
| 22 | Sync version refs script defines grep meta pattern | `grep -rlZE "$_meta_pat"` | hooks/sync-version-refs.sh:167 |

---

## Review log

### Pass 1: Architecture, Script Ergonomics & Parity Review

- **Finding 1 (Version Lag in In-Repo Profile):** The root `.aidoc/profile.yaml` remained at `0.96.2` following CHG-116's version bump to `0.96.3`. While `.aidoc/profile.yaml` is a record-only dogfood declaration, keeping it at `0.96.3` ensures local consistency and eliminates confusing version drift.
  - **Resolution:** Updated Component 1 to bump `.aidoc/profile.yaml` to `0.96.3` and update `last_updated` to `2026-10-18`.
- **Finding 2 (Governance Example Pin in `AIDOC.md`):** Line 117 of `AIDOC.md` referenced `framework/v0.96.2` as the example immutable release tag.
  - **Resolution:** Updated Component 2 to align the example pin to `framework/v0.96.3`.
- **Finding 3 (Consumer Tooling Parity in `TASKFILE-TEMPLATE.yml`):** Consumer projects authoring Layer 09 Change Requests or CNCF Serverless Workflows had no direct Taskfile shortcuts. They had to remember raw module invocation syntax (`python3 -m sdd_doc_lint.chg_lint <target>` and `python3 -m sdd_doc_lint.swf_lint <path>`).
  - **Resolution:** Added Component 3 to author canonical `chg-lint`, `swf-lint`, and `profile-lint` tasks in `TASKFILE-TEMPLATE.yml`, resolving vendored dependencies via the existing top-level `PYTHONPATH`.
- **Finding 4 (Conformance Assertion Coverage):** `test_consumer_scripts.py` asserted presence of `lint:`, but did not assert presence of the expanded task set (`chg-lint:`, `swf-lint:`, `profile-lint:`).
  - **Resolution:** Added Component 5 to extend `test_consumer_scripts.py` with explicit assertions for the new tasks.

### Pass 2: Adversarial Independent Subagent Review

- **Date:** 2026-10-18
- **Reviewer:** Independent Subagent (Adversarial Lenses)
- **Finding 5 (Argument Quoting Bug in `chg-lint` Task):** In `TASKFILE-TEMPLATE.yml`, quoting `"$TARGET"` when `TARGET` was assigned from `{{.CLI_ARGS}}` bundled multi-argument strings into a single argument `sys.argv[1]`, causing failures when passing `--sdd-root` or multiple files.
  - **Resolution:** Separated the explicit argument execution path (`if [ -n "{{.CLI_ARGS}}" ]; then python3 -m sdd_doc_lint.chg_lint {{.CLI_ARGS}}`) from the auto-discovery fallback.
- **Finding 6 (`chg-lint` Fallback Degrades CHG-L011):** Auto-discovery omitted `--sdd-root`, degrading CHG-L011 contract verification to a directory-local heuristic.
  - **Resolution:** Passed `--sdd-root "{{.SDD_DIR}}"` in the auto-discovery fallback branch.
- **Finding 7 (Missing Preconditions on New Linter Tasks):** `chg-lint`, `swf-lint`, and `profile-lint` lacked the standardized precondition check present on `lint:`, risking unhandled `ModuleNotFoundError` tracebacks in uninitialized environments.
  - **Resolution:** Added the standardized `preconditions` block to `chg-lint`, `swf-lint`, and `profile-lint`.
- **Finding 8 (Normative Specification Drift in `AIDOC_WORKSTATION_STANDARD.md`):** `TASKFILE-TEMPLATE.yml` cites `docs/AIDOC_WORKSTATION_STANDARD.md` as authority, but Section 8 only listed `lint`, `review`, `slice`, and `check`.
  - **Resolution:** Extended Component 4 to update `docs/AIDOC_WORKSTATION_STANDARD.md` Section 8 to document the expanded task definitions.
- **Finding 9 (Upgrade Script Advisory Check Expansion):** `upgrade.sh:276` only warned about missing `graph-check:`, not the newly added linters.
  - **Resolution:** Updated `upgrade.sh:276` in Component 4 to note `(graph-check, chg-lint, swf-lint)` when harmonizing existing Taskfiles.

### Pass 3: Deep Technical & Interpreter Verification Review

- **Date:** 2026-10-18
- **Reviewer:** Independent Subagent (Technical Interpreter & Edge-Case Lenses)
- **Finding 10 (Go-Task Literal Nested Quote Crash):** Shell conditional `if [ -n "{{.CLI_ARGS}}" ]; then` inside Go-Task multi-line `cmds: - |` crashes the shell interpreter (`exit code 201`) whenever arguments contain quotes.
  - **Resolution:** Switched to native Go-Task template conditionals: `{{if .CLI_ARGS}} python3 -m sdd_doc_lint.chg_lint {{.CLI_ARGS}} {{else}} ... {{end}}`, which evaluates at template render time and bypasses shell-level quote nesting.
- **Finding 11 (Incorrect Conformance Test Method Name in Plan):** Component 5 cited non-existent method `test_scaffolded_taskfile_and_engine_config`.
  - **Resolution:** Corrected method target to `test_scaffolds_stack_policy_and_linter_runner` in `tests/conformance/test_consumer_scripts.py:406`.
- **Finding 12 (Git Submodule Overwrite Hazard in `upgrade.sh`):** When `.aidoc/framework` is a Git submodule, `[ -L "$FW" ]` is false, causing `upgrade.sh` to treat it as a pinned copy and delete `.git` pointers.
  - **Resolution:** Added a guard in `upgrade.sh:106`: if `[ -f "$FW/.git" ]`, detect that the consumer is using a Git submodule, advise using `git submodule update`, and refuse destructive replacement without `--force`.
- **Finding 13 (Full SDD Gate Omission of Profile Lint):** In `TASKFILE-TEMPLATE.yml`, `check:` ran `lint` and `review`, omitting `profile-lint`.
  - **Resolution:** Wired `- task: profile-lint` into `check:` as the first verification step.
- **Finding 14 (Framework Repo Dogfood Drift in Root `Taskfile.yml`):** Root `Taskfile.yml` lacked `profile-lint` and had the legacy `chg-lint` syntax.
  - **Resolution:** Extended Component 3 to add `profile-lint` to root `Taskfile.yml` and update `chg-lint` to use `{{if .CLI_ARGS}}`.
- **Finding 15 (`hooks/sync-version-refs.sh` Excluded `.aidoc/`):** Version fanout skipped `.aidoc/profile.yaml`, causing recurring version lag on every version bump.
  - **Resolution:** Added `"$REPO_ROOT/.aidoc/profile.yaml"` to the sweep list in `hooks/sync-version-refs.sh:167`.
- **Result:** ready, no new findings.

---

## Proposed Changes

Grouped by component in logical dependency order:

### Component 1: Dogfood `.aidoc/` Profile Modernization

#### [MODIFY] [.aidoc/profile.yaml](../.aidoc/profile.yaml)

- Bump `metadata.framework_version` from `"0.96.2"` to `"0.96.3"`.
- Update `metadata.last_updated` to `"2026-10-18"`.

```yaml
metadata:
  schema_version: "1.1.0"
  project_name: "aidoc-flow-framework"
  authority: "framework/governance/ADAPTATION.md"
- last_updated: "2026-10-17"
- framework_version: "0.96.2"
+ last_updated: "2026-10-18"
+ framework_version: "0.96.3"
  framework_path: ".aidoc/framework"
```

---

### Component 2: Governance Guide Alignment & Version Fanout

#### [MODIFY] [framework/governance/aidoc/AIDOC.md](../framework/governance/aidoc/AIDOC.md)

- Update example submodule release tag on line 117 to `framework/v0.96.3`.

```markdown
-1. **Git Submodule:** The project commits `.aidoc/framework/` as a Git submodule pinned to an immutable release tag (e.g. `framework/v0.96.2`).
+1. **Git Submodule:** The project commits `.aidoc/framework/` as a Git submodule pinned to an immutable release tag (e.g. `framework/v0.96.3`).
```

#### [MODIFY] [hooks/sync-version-refs.sh](../hooks/sync-version-refs.sh)

- Include `"$REPO_ROOT/.aidoc/profile.yaml"` in the version sweep pattern search list (line 167) to prevent future version drift.

```bash
-done < <(grep -rlZE "$_meta_pat" "$REPO_ROOT/framework/" "$REPO_ROOT/docs/" "$REPO_ROOT/README.md" 2>/dev/null || true)
+done < <(grep -rlZE "$_meta_pat" "$REPO_ROOT/framework/" "$REPO_ROOT/docs/" "$REPO_ROOT/README.md" "$REPO_ROOT/.aidoc/profile.yaml" 2>/dev/null || true)
```

#### [MODIFY] [framework/governance/PROFILE-TEMPLATE.yaml](../framework/governance/PROFILE-TEMPLATE.yaml)

- Add `CHG` to the commented `active_layers:` example (line 66) so all 10 layers are represented.

```yaml
-# active_layers: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN, EVAL]
+# active_layers: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN, CHG, EVAL]
```

---

### Component 3: Workstation & Root Taskfile Modernization

#### [MODIFY] [framework/templates/TASKFILE-TEMPLATE.yml](../framework/templates/TASKFILE-TEMPLATE.yml)

- Wire `profile-lint` into composite `check:`.
- Add `chg-lint` task with native Go-Task template conditional (`{{if .CLI_ARGS}}`), `--sdd-root` scoping, and preconditions.
- Add `swf-lint` task with preconditions.
- Add `profile-lint` task with preconditions.

```yaml
   check:
-    desc: "Full SDD Gate: structural linting + cryptographic review verification"
+    desc: "Full SDD Gate: adaptation profile + structural linting + cryptographic review verification"
     cmds:
+      - task: profile-lint
       - task: lint
       - task: review
         vars: { CLI_ARGS: "--verify-only" }

+  chg-lint:
+    desc: "Run CHG structural linter on Change Requests in docs/sdd/09_CHG/"
+    preconditions:
+      - sh: 'python3 -c "import sdd_doc_lint" 2>/dev/null || test -d .aidoc/framework/sdd_doc_lint'
+        msg: "sdd_doc_lint not found. Install dependencies or sync .aidoc/framework."
+    cmds:
+      - |
+        {{if .CLI_ARGS}}
+        python3 -m sdd_doc_lint.chg_lint {{.CLI_ARGS}}
+        {{else}}
+        TARGET="$(ls {{.SDD_DIR}}/09_CHG/CHG-*.yaml 2>/dev/null | sort -V | tail -n 1)"
+        if [ -z "$TARGET" ]; then
+          LATEST_DIR="$(ls -d {{.SDD_DIR}}/09_CHG/archive/CHG-* 2>/dev/null | sort -V | tail -n 1)"
+          [ -n "$LATEST_DIR" ] && TARGET="$(ls "$LATEST_DIR"/CHG-*.yaml 2>/dev/null | head -n 1)"
+        fi
+        if [ -n "$TARGET" ]; then
+          python3 -m sdd_doc_lint.chg_lint --sdd-root "{{.SDD_DIR}}" "$TARGET"
+        else
+          echo "No CHG target specified or found in {{.SDD_DIR}}/09_CHG/." >&2
+          exit 1
+        fi
+        {{end}}
+
+  swf-lint:
+    desc: "Run Serverless Workflow linter on declarative state machines"
+    preconditions:
+      - sh: 'python3 -c "import sdd_doc_lint" 2>/dev/null || test -d .aidoc/framework/sdd_doc_lint'
+        msg: "sdd_doc_lint not found. Install dependencies or sync .aidoc/framework."
+    cmds:
+      - python3 -m sdd_doc_lint.swf_lint {{.CLI_ARGS | default .SDD_DIR}}
+
+  profile-lint:
+    desc: "Validate adaptation profile against schema 1.1.0"
+    preconditions:
+      - sh: 'python3 -c "import sdd_doc_lint" 2>/dev/null || test -d .aidoc/framework/sdd_doc_lint'
+        msg: "sdd_doc_lint not found. Install dependencies or sync .aidoc/framework."
+    cmds:
+      - python3 -m sdd_doc_lint.profile_lint {{.CLI_ARGS | default ".aidoc/profile.yaml"}}
```

#### [MODIFY] [Taskfile.yml](../Taskfile.yml)

- Update root `chg-lint` task to use Go-Task native `{{if .CLI_ARGS}}`.
- Add `profile-lint` task to root `Taskfile.yml`.

```yaml
   chg-lint:
     desc: Run CHG structural linter (defaults to latest archived CHG if none specified)
     cmds:
       - |
-        TARGET="{{.CLI_ARGS}}"
-        if [ -z "$TARGET" ]; then
+        {{if .CLI_ARGS}}
+        python3 sdd_doc_lint/chg_lint.py {{.CLI_ARGS}}
+        {{else}}
         LATEST_DIR="$(ls -d framework/archive/CHG-* 2>/dev/null | sort -V | tail -n 1)"
         if [ -n "$LATEST_DIR" ]; then
           TARGET="$(ls "$LATEST_DIR"/CHG-*.yaml 2>/dev/null | head -n 1)"
+          python3 sdd_doc_lint/chg_lint.py "$TARGET"
+        else
+          echo "No CHG target specified or found." >&2
+          exit 1
         fi
-        if [ -n "$TARGET" ]; then
-          python3 sdd_doc_lint/chg_lint.py "$TARGET"
-        else
-          echo "No CHG target specified or found." >&2
-          exit 1
-        fi
+        {{end}}

+  profile-lint:
+    desc: Run profile schema linter on .aidoc/profile.yaml
+    cmds:
+      - python3 sdd_doc_lint/profile_lint.py {{.CLI_ARGS | default ".aidoc/profile.yaml"}}
```

---

### Component 4: Working Agreement, Standard & Script Harmonization

#### [MODIFY] [framework/templates/AGENTS-TEMPLATE.md](../framework/templates/AGENTS-TEMPLATE.md)

- Reference `task sdd:chg-lint`, `task sdd:swf-lint`, and `task sdd:profile-lint` in Section ## Non-negotiables (line 39).

```markdown
-- **Submit only verified work:** Run linters and quality gates via Taskfile (task sdd:graph-check, task sdd:lint, and task sdd:check, or backward-compatible .aidoc/bin/sdd-lint) and local test suites before opening or updating a PR.
+- **Submit only verified work:** Run linters and quality gates via Taskfile (`task sdd:check`, `task sdd:lint`, `task sdd:graph-check`, `task sdd:chg-lint`, `task sdd:swf-lint`, `task sdd:profile-lint`, or backward-compatible `.aidoc/bin/sdd-lint`) and local test suites before opening or updating a PR.
```

#### [MODIFY] [docs/AIDOC_WORKSTATION_STANDARD.md](../docs/AIDOC_WORKSTATION_STANDARD.md)

- Update Section 8 `### Canonical SDD Tasks (.aidoc/Taskfile.yml)` to document the new `chg-lint`, `swf-lint`, and `profile-lint` tasks.

```yaml
   check:
-    desc: "Full SDD Gate: structural linting + cryptographic review verification"
+    desc: "Full SDD Gate: adaptation profile + structural linting + cryptographic review verification"
     cmds:
+      - task: profile-lint
       - task: lint
       - task: review
         vars: { CLI_ARGS: "--verify-only" }
+
+  chg-lint:
+    desc: "Run CHG structural linter on Change Requests in docs/sdd/09_CHG/"
+    cmds:
+      - python3 -m sdd_doc_lint.chg_lint {{.CLI_ARGS}}
+
+  swf-lint:
+    desc: "Run Serverless Workflow linter on declarative state machines"
+    cmds:
+      - python3 -m sdd_doc_lint.swf_lint {{.CLI_ARGS | default .SDD_DIR}}
+
+  profile-lint:
+    desc: "Validate adaptation profile against schema 1.1.0"
+    cmds:
+      - python3 -m sdd_doc_lint.profile_lint {{.CLI_ARGS | default ".aidoc/profile.yaml"}}
```

#### [MODIFY] [framework/scripts/upgrade.sh](../framework/scripts/upgrade.sh)

- Add Git submodule guard check (line 106) to refuse destructive overwrites of `.aidoc/framework` when `.git` exists, unless `--force` is given.
- Update line 276 advisory message to reflect `(graph-check, chg-lint, swf-lint)`.

```bash
+  if [ -f "$FW/.git" ] && [ "$FORCE" != 1 ]; then
+    refuse ".aidoc/framework is a Git submodule — update via 'git submodule update --remote .aidoc/framework' or re-checkout inside .aidoc/framework (pass --force to override and convert to a pinned copy)"
+  fi
```

```bash
-  elif [ -f "$AIDOC/Taskfile.yml" ] && ! grep -q 'graph-check:' "$AIDOC/Taskfile.yml"; then
-    log "note: existing .aidoc/Taskfile.yml lacks graph tasks (graph-check, render, delta) — consider harmonizing with framework/templates/TASKFILE-TEMPLATE.yml"
+  elif [ -f "$AIDOC/Taskfile.yml" ] && ! grep -q 'chg-lint:' "$AIDOC/Taskfile.yml"; then
+    log "note: existing .aidoc/Taskfile.yml lacks modern tasks (graph-check, chg-lint, swf-lint) — consider harmonizing with framework/templates/TASKFILE-TEMPLATE.yml"
```

---

### Component 5: Conformance Test Suite Extension

#### [MODIFY] [tests/conformance/test_consumer_scripts.py](../tests/conformance/test_consumer_scripts.py)

- Extend `test_scaffolds_stack_policy_and_linter_runner` (line 406) to assert that `chg-lint:`, `swf-lint:`, and `profile-lint:` are scaffolded into `.aidoc/Taskfile.yml`.
- Add test for the Git submodule safety guard in `upgrade.sh`.

```python
         taskfile = self.project / ".aidoc" / "Taskfile.yml"
         self.assertTrue(taskfile.is_file())
-        self.assertIn("lint:", taskfile.read_text(encoding="utf-8"))
+        taskfile_text = taskfile.read_text(encoding="utf-8")
+        self.assertIn("lint:", taskfile_text)
+        self.assertIn("chg-lint:", taskfile_text)
+        self.assertIn("swf-lint:", taskfile_text)
+        self.assertIn("profile-lint:", taskfile_text)
```

---

## Verification Plan

### Automated Tests

1. **Plan & Citation Gate:**

   ```bash
   python3 .agents/skills/verified-planning/check_plan.py <plan-file>
   ```

2. **Profile & SDD Linters:**

   ```bash
   python3 sdd_doc_lint/profile_lint.py .aidoc/profile.yaml
   python3 -m sdd_doc_lint --check-surfaces .
   ```

3. **Consumer Scripts Conformance:**

   ```bash
   PYTHONPATH=tests/conformance python3 -m unittest tests/conformance/test_consumer_scripts.py -v
   ```

4. **Full Test Suites:**

   ```bash
   python3 -m unittest discover -s tests/unit
   PYTHONPATH=tests/conformance python3 -m unittest discover -s tests/conformance
   python3 -m unittest discover -s tests/acceptance/deterministic
   ```

### End-to-End Consumer Deployment Verification

1. **Greenfield Deployment Verification:**
   - Execute `./deploy.sh --target /tmp/test-greenfield-consumer --yes`.
   - Assert all 10 scaffolded files/directories exist (`profile.yaml`, `Taskfile.yml`, `engine/engine.yaml`, `bin/sdd-lint`, `cache/`, `docs/sdd/graph/`, `docs/sdd/05_ADR/ADR-00_index.yaml`, `AGENTS.md`, `stack-policy.yaml`, `.aidoc/framework/`).
   - Run `/tmp/test-greenfield-consumer/.aidoc/bin/sdd-lint docs/sdd`.
   - Run `python3 -m sdd_doc_lint.profile_lint /tmp/test-greenfield-consumer/.aidoc/profile.yaml`.
   - Verify all newly added templates (`CHG-SWF-TEMPLATE.yaml`, `CHG-GRAPH-TEMPLATE.yaml`) are present inside `/tmp/test-greenfield-consumer/.aidoc/framework/framework/layers/09_CHG/`.
2. **Brownfield Upgrade Verification:**
   - Execute `./deploy.sh --target /tmp/test-brownfield-consumer` against an existing consumer fixture.
   - Assert that `profile.yaml` is re-pinned to `0.96.3`.
   - Assert that staged allowlist swap completed cleanly without leaving temporary `.new` or `.prev` artifacts.
   - Assert that a Git submodule consumer (`.aidoc/framework/.git`) refuses overwrite unless `--force` is passed.
