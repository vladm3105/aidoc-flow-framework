# Plugin Test Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tiered, layered test suite for the `aidoc-flow` Claude Code plugin and SDD framework. The suite must cover static checks, unit tests, per-layer acceptance (BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN — each runnable in isolation), end-to-end full-path acceptance (BRD → IPLAN), packaging integrity, marketplace pre-deploy gate, and post-deploy smoke. Deterministic tests run on every PR; live LLM tests are opt-in. Optional LLM-based code review is wired as a release-time check.

**Architecture:** All test code lives in `framework/tests/` (per user decision). A single bash entry point `scripts/test-plugin.sh` (parent repo) routes to tiers via flags (`--suite`, `--layer`, `--live`, `--review`). The deterministic core uses Python `unittest` (matching the existing conformance suite of 77 tests); live LLM probes use `claude -p` with a token budget. Fixture corpus is split into `valid/`, `broken/`, `golden_chain/`, and frozen `live_snapshots/`. GitHub Actions runs deterministic on every PR, the full live tier on release-candidate tags, and a network-isolated smoke after marketplace publish.

**Tech Stack:** Python 3.11 `unittest` · PyYAML · jsonschema · `claude plugin validate` (Anthropic CLI) · `claude -p` (live probe) · bash 5 · pre-commit · GitHub Actions · markdownlint · ruff · bandit · `sdd_doc_lint` (framework-internal).

---

## 1 — Scope and Non-Goals

### In scope

- 8 deterministic test tiers (static → unit → per-layer → full-path → packaging → release → post-deploy → optional review).
- Per-layer test runner (any of the 8 layers in isolation).
- Full-path runner (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN chain).
- Tiered LLM strategy: deterministic default + opt-in `--live` tier.
- GitHub Actions workflows: PR gate, release gate, nightly live, post-deploy smoke.
- Pre-commit hook tier (lightweight subset).
- Anthropic Claude Code plugin marketplace pre-deploy and post-deploy validation.
- Optional LLM-based code-review tier (`--review`) using Claude Code agents.
- Bash entry-point `scripts/test-plugin.sh` extension (subcommands).

### Out of scope

- Replacing existing 77 conformance tests (extend, do not duplicate).
- Per-skill prompt regression tests against specific LLM outputs (the live tier asserts *structural* properties, not exact wording).
- Mutation testing or fuzzing of skill prompts.
- Performance benchmarking of the framework.
- Mocking the LLM (deterministic tier uses frozen artifacts, not mocks).

### Non-goals deferred to NON-GOAL-1 / NON-GOAL-2 (per AUTHORING-STYLE-FOLLOWUP.md)

- Pure cross-document semantic drift detection without element-ID links (covered by review-team).
- External-reality drift (production telemetry, marketplace pricing) — out of corpus.

---

## 2 — Test Pyramid

```
Tier 8: LLM code review (--review, opt-in, release-time)
                       │
Tier 7: Post-deploy smoke (marketplace install + live probe)
                       │
Tier 6: Marketplace release gate (full deterministic + live + integrity)
                       │
Tier 5: Packaging integrity (bundle byte-identity, VERSION gate, sync idempotency)
                       │
Tier 4: Full-path acceptance (BRD→IPLAN chain, deterministic + opt-in live)
                       │
Tier 3: Per-layer acceptance (8 layers × deterministic + opt-in live)
                       │
Tier 2: Unit tests (per-skill, per-template, per-lint-check)
                       │
Tier 1: Static checks (manifest, YAML, markdownlint, ruff, bandit)
```

### Gating policy

| Tier | PR gate | Release gate | Nightly | Post-publish |
|------|:-:|:-:|:-:|:-:|
| 1 — Static | ✅ | ✅ | ✅ | ✅ |
| 2 — Unit | ✅ | ✅ | ✅ | — |
| 3 — Per-layer (det) | ✅ | ✅ | ✅ | — |
| 3 — Per-layer (live) | — | ✅ | ✅ | — |
| 4 — Full-path (det) | ✅ | ✅ | ✅ | — |
| 4 — Full-path (live) | — | ✅ | ✅ | — |
| 5 — Packaging | ✅ | ✅ | ✅ | — |
| 6 — Release gate | — | ✅ | — | — |
| 7 — Post-deploy | — | — | — | ✅ |
| 8 — LLM review | — | opt-in | — | — |

---

## 3 — File Structure

### Created in this plan (under `framework/`)

```
framework/
  VERSION                                 # MODIFIED Task 12.0
  FRAMEWORK_SPEC_VERSION                  # MODIFIED Task 12.0
  CHANGELOG.md                            # MODIFIED Task 12.0
  tools/
    bump_version.py                       # NEW Task 12.0 (portable, Linux + macOS)
    sdd_doc_lint/__init__.py              # MODIFIED Task 1.3 (STRUCT01, --format=json)
    sdd_doc_lint/__main__.py              # MODIFIED Task 1.3
  platforms/claude-code-plugin/           # MODIFIED Task 12.0 (re-synced, all skills bumped)
  tests/
    README.md                             # NEW Task 11.2
    SCENARIOS.md                          # NEW Task 11.5.1
    HOWTO.md                              # NEW Task 11.5.2
    ENVIRONMENT.md                        # NEW Task 11.5.3
    TROUBLESHOOTING.md                    # NEW Task 11.5.4
    CONTRIBUTING.md                       # NEW Task 11.5.5
    conformance/                          # EXISTING 77 tests
      _spec.py                            # MODIFIED Task 0.2 (helpers)
      requirements.txt                    # MODIFIED Task 0.3 (jsonschema)
      test_governance.py                  # MODIFIED Task 0.3 (orphan guard)
    unit/                                 # NEW
      README.md                           # Task 11.5.6
      __init__.py
      test_spec_helpers.py                # Task 0.2
      test_skill_manifests.py             # Task 2.1
      test_template_yaml.py               # Task 1.1
      test_sdd_doc_lint_checks.py         # Task 2.2 (JSON-parsed)
      test_sdd_doc_lint_struct01.py       # Task 1.3
      test_sdd_doc_lint_json_format.py    # Task 1.3 (split out)
      test_sync_scripts.py                # Task 2.3
      test_nonlayer_skills.py             # Task 6.5.3
      lint_fixtures/<code>/<file>         # one subdir per code, Task 2.2 + 1.3
    acceptance/                           # NEW
      README.md                           # Task 11.5.6
      __init__.py
      _harness.py                         # Task 3.1
      _id_coordinator.py                  # Task 5.0
      fixtures/
        layer_01_brd/{valid,broken}/      # Task 3.2
        layer_02_prd/{valid,broken}/      # Task 3.3
        layer_03_ears/{valid,broken}/     # Task 3.4
        layer_04_bdd/{valid,broken}/      # Task 3.5
        layer_05_adr/{valid,broken}/      # Task 3.6
        layer_06_spec/{valid,broken}/     # Task 3.7
        layer_07_tdd/{valid,broken}/      # Task 3.8
        layer_08_iplan/{valid,broken}/    # Task 3.9
        fullpath/
          ID_REGISTRY.yaml                # Task 5.0
          seed_prompt.txt
          golden_chain/                   # Task 5.1
          broken_chain/                   # Task 5.1b
      deterministic/
        __init__.py
        test_layer_{brd,prd,ears,bdd,adr,spec,tdd,iplan}.py   # Tasks 3.2-3.9
        test_fullpath.py                  # Tasks 5.1 + 5.1b
        test_doc_validator.py             # Task 6.5.2
      live/                               # @skipUnless(LIVE)
        __init__.py
        _live_harness.py                  # Task 4.1 + 4.2.5
        test_layer_{brd,prd,ears,bdd,adr,spec,tdd,iplan}_live.py   # Tasks 4.2-4.9
        test_fullpath_live.py             # Task 5.2
        test_doc_flow_live.py             # Task 6.5.1
    packaging/                            # NEW
      README.md                           # Task 11.5.6
      __init__.py
      test_manifest_strict.py             # Task 1.2
      test_bundle_integrity.py            # Task 6.1
      test_version_gate.py                # Task 6.2
    release/                              # NEW
      README.md                           # Task 11.5.6
      __init__.py
      limits.yaml                         # Task 7.2
      test_marketplace_gate.py            # Task 7.3
      test_changelog_entry.py             # Task 7.1
      test_bundle_size.py                 # Task 7.2
    smoke/                                # NEW
      README.md                           # Task 11.5.6
      COMMANDS.md                         # Task 8.0
      __init__.py
      test_post_deploy.py                 # Task 8.1
      install-from-marketplace.sh         # Task 8.1
    review/                               # NEW (opt-in)
      README.md                           # Task 11.5.6
      __init__.py
      test_llm_code_review.py             # Task 9.1
      run-claude-review.sh                # Task 9.1
```

### Created in this plan (under parent `aidoc-flow/`)

```
aidoc-flow/
  scripts/
    test-plugin.sh                        # EXISTING — refactored Task 10.1
    test-layer.sh                         # NEW — thin wrapper
    test-fullpath.sh                      # NEW — thin wrapper
  .github/workflows/
    pr-checks.yml                         # NEW
    release.yml                           # NEW
    nightly-live.yml                      # NEW
    post-deploy.yml                       # NEW
  .pre-commit-config.yaml                 # EXTENDED Task 9.2
```

### Why this layout

- **`framework/tests/`** keeps test code with the code it tests; survives `git submodule` add into any consumer.
- **`acceptance/deterministic/` vs `acceptance/live/`** lets the runner discover one tree by default and the other only when `LIVE=1` is set — no `@skipIf` boilerplate per test.
- **`fixtures/layer_NN_<x>/{valid,broken}/`** mirrors the 8-layer numbering used everywhere else (`docs/01_BRD/`, `framework/layers/01_BRD/`).
- **`packaging/`, `release/`, `smoke/`, `review/`** are separate suites so a release engineer can run just `python -m unittest discover framework/tests/release` without dragging in 200+ unit tests.

---

## 4 — Fixture Corpus Design

Each layer has the same fixture pattern:

```
fixtures/layer_NN_<x>/
  valid/
    <TYPE>-01_golden.{md|yaml}             # passes lint + audit, ≥90/100 ready
    <TYPE>-01_golden.meta.yaml             # expected: section list, IDs, tags
  broken/
    <TYPE>-01_missing_section.{md|yaml}    # known structural drift
    <TYPE>-01_drift_codes.yaml             # expected lint codes (STY01, FM01, …)
    <TYPE>-01_banned_phrase.{md|yaml}      # AUTHORING_STYLE violation
    <TYPE>-01_id_collision.{md|yaml}       # duplicate hashes
```

### `<TYPE>-01_drift_codes.yaml` (example)

```yaml
file: BRD-01_missing_section.md
expected_findings:
  # STRUCT01 = new deterministic check added by Task 1.3.
  - code: STRUCT01
    severity: error
    message_match: "missing required section: project_scope"
  - code: STY03
    severity: warning
    section: business_objectives
    word_count_over_target: true
```

> **Gate to Task 1.3:** `STRUCT01` is a new lint code introduced by this plan
> (see Task 1.3 below). Before any per-layer broken fixture is authored,
> Task 1.3 must land. The existing `sdd_doc_lint` ships STY01/02/03, FM01,
> DG02, HASH01, CSC01, STALE01, TH02 — *no* STRUCT01.

### Full-path chain (`fixtures/fullpath/golden_chain/`)

- 8 files (BRD-01 → IPLAN-01) hand-authored to current templates.
- Cumulative tags resolve forward (BRD-01 elements referenced by `@brd:` from PRD onward).
- Element IDs deterministic (hashes computed once and committed).
- Test verifies: forward-tag closure, backward-tag emptiness on Layer 1, downstream `code_paths` non-empty on Layer 8.

---

## 5 — Anthropic / Marketplace Best Practices Baked Into the Plan

These are encoded as test cases in `tests/release/test_marketplace_gate.py` and `tests/packaging/test_bundle_integrity.py`:

1. **Manifest validation:** `claude plugin validate --strict` must pass.
2. **No filesystem writes outside plugin scope:** test scans for `open(.*, "w")` / `Path(...).write_*` calls in skill-bundled code and asserts paths resolve under `${CLAUDE_PLUGIN_ROOT}` or `.aidoc/` or a temp dir.
3. **No network egress from plugin code:** static scan for `requests.`, `urllib.request`, `httpx.`, raw sockets in `framework/platforms/claude-code-plugin/sdd_doc_lint/`.
4. **No `--dangerously-skip-permissions` defaults:** scan SKILL.md files; flag any literal use outside `tests/` and the documented harness.
5. **Bundle size cap:** assert plugin bundle ≤ 10 MiB (configurable in `release/limits.yaml`).
6. **CHANGELOG entry for current VERSION:** parse `CHANGELOG.md`; assert top section matches `framework/VERSION`.
7. **No PII / secrets in any committed artifact:** extend existing `detect-secrets` baseline check; add a positive test for known-bad patterns.
8. **Deterministic IDs:** every element ID's hash matches `SHA256("{doc_id}:{section_id}:{title}:{description}")[:4]`.
9. **Skill metadata complete:** every SKILL.md frontmatter has `framework_spec_version`, `version`, `last_updated`, `artifact_type`, `layer`, `skill_category`.
10. **Skill bundle equivalence:** every file under `framework/platforms/claude-code-plugin/framework/` is byte-identical to its sibling under `framework/`.

---

## 6 — Test Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Unit module | `test_<thing>.py` | `test_skill_manifests.py` |
| Per-layer module | `test_layer_<lower>.py` | `test_layer_brd.py` |
| Live module | `test_layer_<lower>_live.py` | `test_layer_brd_live.py` |
| Test method | `test_<verb>_<noun>_<condition>` | `test_audit_flags_missing_section_in_broken_brd` |
| Fixture file | `<TYPE>-01_<descriptor>.{md\|yaml}` | `BRD-01_missing_section.md` |
| Lint-code fixture | `<TYPE>-01_drift_codes.yaml` | `BRD-01_drift_codes.yaml` |
| Class | `class <Verb><Noun>Tests(unittest.TestCase)` | `class LayerBrdTests(unittest.TestCase)` |

---

## 7 — Execution Order Dependencies

Tasks are numbered sequentially but several cross-phase dependencies exist. A
subagent runner must honor these:

```
0.1 ── 0.2 ── 0.3 ───────────────────────────────────────────────────────────────────────────────────►
                │
                └── 1.1
                    1.2
                    1.3* (must precede every per-layer broken-fixture test)
                        │
                        └── 2.1, 2.2 (Task 2.2 uses --format=json from 1.3)
                            2.3
                                │
                                └── 3.1 (harness)
                                        │
                                        └── 3.2 (BRD)
                                            3.3 (PRD)  — depends on 3.2 (PRD references BRD elements)
                                            3.4 (EARS) — depends on 3.3
                                            3.5 (BDD)  — depends on 3.4
                                            3.6 (ADR)  — depends on 3.5
                                            3.7 (SPEC) — depends on 3.6
                                            3.8 (TDD)  — depends on 3.7
                                            3.9 (IPLAN) — depends on 3.8
                                            3.10 (test-layer.sh wrapper)
                                                │
                                                └── 4.1 → 4.2.5 (live harness) → 4.2 → 4.3 → … → 4.9
                                                    (live tasks are independent of one another;
                                                    can run in any order once 4.2.5 lands)
                                                        │
                                                        └── 5.0 (ID coordinator) → 5.1 → 5.1b → 5.2 → 5.3
                                                                │
                                                                └── 6.1, 6.2, 6.3
                                                                    6.5.1 — needs Phase 3 BRD fixtures
                                                                    6.5.2 — needs 5.1b broken_chain
                                                                    6.5.3
                                                                        │
                                                                        └── 7.1, 7.2, 7.3
                                                                            8.0 → 8.1
                                                                            9.1
                                                                            10.1, 10.2, 10.3, 10.4
                                                                            11.1, 11.2
                                                                            11.5.1, 11.5.2, …, 11.5.6
                                                                                │
                                                                                └── 12.0 (full VERSION bump)
                                                                                    12.1 (parent submodule bump)
                                                                                    13.1 (final code reviewer)
```

`*` = must complete before its dependent phase even *begins*.

### Critical sequencing rules

1. **Task 1.3 (STRUCT01 + JSON) must land before any Phase 3 broken fixture is authored.**
   Without it, the per-layer `<TYPE>-01_drift_codes.yaml` files reference a code that
   doesn't exist.
2. **Task 5.0 (ID coordinator + ID_REGISTRY) must land before Task 5.1.**
   The fullpath chain depends on the registry being populatable.
3. **Task 8.0 (verify CLI commands) must land before Tasks 8.1 / 10.2 / 10.4.**
   Otherwise CI workflows reference unverified install syntax.
4. **Task 12.0 (full VERSION bump) is the *final* framework commit** before the parent
   submodule bump (Task 12.1). All test infrastructure must already be in place.
5. **Phase 3 per-layer fixture tasks are sequential** — each layer's golden references
   the previous layer's element IDs. Parallel authoring breaks the ID closure.
6. **Phase 4 per-layer live tasks are independent** — they each stage their own
   upstream goldens. May be parallelized (within the skill's "no parallel implementers"
   guardrail: one implementer at a time, but the order among 4.3–4.9 is free).

---

## Phase 0 — Foundation

## Task 0.1: Create the test directory skeleton

**Files:**

- Create: `framework/tests/unit/__init__.py`
- Create: `framework/tests/acceptance/__init__.py`
- Create: `framework/tests/acceptance/deterministic/__init__.py`
- Create: `framework/tests/acceptance/live/__init__.py`
- Create: `framework/tests/packaging/__init__.py`
- Create: `framework/tests/release/__init__.py`
- Create: `framework/tests/smoke/__init__.py`
- Create: `framework/tests/review/__init__.py`

- [ ] **Step 1: Create the directory skeleton**

```bash
mkdir -p framework/tests/{unit,acceptance/{deterministic,live,fixtures/fullpath/golden_chain},packaging,release,smoke,review}
for L in 01_brd 02_prd 03_ears 04_bdd 05_adr 06_spec 07_tdd 08_iplan; do
  mkdir -p "framework/tests/acceptance/fixtures/layer_${L}"/{valid,broken}
done
for d in unit acceptance acceptance/deterministic acceptance/live packaging release smoke review; do
  touch "framework/tests/${d}/__init__.py"
done
```

- [ ] **Step 2: Verify layout**

Run: `find framework/tests -maxdepth 3 -type d | sort`
Expected: lists all 8 layer fixture dirs, 4 acceptance subdirs (deterministic/live/fixtures), and the 5 new top-level suites.

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/
git -C framework commit -m "test: scaffold tiered test suite directories"
```

## Task 0.2: Extend `_spec.py` with shared helpers

**Files:**

- Modify: `framework/tests/conformance/_spec.py`

- [ ] **Step 1: Write failing test for the new helper `layer_root(name)`**

Create `framework/tests/unit/test_spec_helpers.py`:

```python
"""Unit: tests/conformance/_spec.py helper extensions."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import ARTIFACTS, FRAMEWORK, layer_root, template_path


class SpecHelperTests(unittest.TestCase):
    def test_layer_root_returns_existing_directory_for_each_artifact(self):
        for name in ARTIFACTS:
            with self.subTest(layer=name):
                root = layer_root(name)
                self.assertTrue(root.exists(), f"missing layer dir for {name}: {root}")
                self.assertTrue(root.is_dir())

    def test_template_path_resolves_for_each_artifact(self):
        for name in ARTIFACTS:
            with self.subTest(layer=name):
                tpl = template_path(name)
                self.assertTrue(tpl.exists(), f"missing template: {tpl}")
                self.assertEqual(tpl.suffix, ".yaml")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd framework && python3 -m unittest tests.unit.test_spec_helpers -v`
Expected: ImportError on `layer_root` / `template_path`.

- [ ] **Step 3: Add helpers to `_spec.py`**

Append to `framework/tests/conformance/_spec.py`:

```python
LAYER_DIR_BY_NAME = {
    "BRD":   FRAMEWORK / "layers" / "01_BRD",
    "PRD":   FRAMEWORK / "layers" / "02_PRD",
    "EARS":  FRAMEWORK / "layers" / "03_EARS",
    "BDD":   FRAMEWORK / "layers" / "04_BDD",
    "ADR":   FRAMEWORK / "layers" / "05_ADR",
    "SPEC":  FRAMEWORK / "layers" / "06_SPEC",
    "TDD":   FRAMEWORK / "layers" / "07_TDD",
    "IPLAN": FRAMEWORK / "layers" / "08_IPLAN",
}


def layer_root(name: str) -> Path:
    """Return the framework/layers/NN_<X>/ directory for an artifact name."""
    return LAYER_DIR_BY_NAME[name]


def template_path(name: str) -> Path:
    """Return the canonical TYPE-TEMPLATE.yaml for an artifact name."""
    return layer_root(name) / f"{name}-TEMPLATE.yaml"


def plugin_bundle_root() -> Path:
    """Return the claude-code-plugin bundle root."""
    return PLATFORMS_ROOT / "claude-code-plugin"


def skill_dirs() -> list[Path]:
    """Return sorted list of every SKILL.md-bearing skill directory in the plugin."""
    return sorted((plugin_bundle_root() / "skills").iterdir())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd framework && python3 -m unittest tests.unit.test_spec_helpers -v`
Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git -C framework add tests/conformance/_spec.py tests/unit/test_spec_helpers.py
git -C framework commit -m "test(unit): extend _spec.py with layer/template/plugin helpers"
```

## Task 0.3: Pin test dependencies + guard `test_governance.EXPECTED_FILES`

**Files:**

- Modify: `framework/tests/conformance/requirements.txt`
- Modify: `framework/tests/conformance/test_governance.py`

**Why this task exists:** The new test tiers add `jsonschema` (Phase 1) and rely on
existing `pyyaml`. CI workflows currently pip-install these ad hoc — drift risk.
And every prior AS-series PR had to extend `test_governance.EXPECTED_FILES` when a
governance file was added; the plan should reaffirm that contract.

- [ ] **Step 1: Extend the pin file**

Edit `framework/tests/conformance/requirements.txt`:

```text
# Pin file for the full test suite (used by CI workflows and pre-commit).
pyyaml>=6.0
jsonschema>=4.20      # added by plan Phase 1
```

- [ ] **Step 2: Add the EXPECTED_FILES guard**

The existing `test_governance.EXPECTED_FILES` is a hand-maintained list. Add an
assertion that catches drift between the list and what's actually under
`framework/governance/`:

Append to `framework/tests/conformance/test_governance.py`:

```python
class GovernanceFilesNoOrphans(unittest.TestCase):
    """Any new file under framework/governance/ must be added to EXPECTED_FILES."""

    def test_no_orphan_governance_files(self):
        actual = {p.name for p in GOVERNANCE.iterdir() if p.is_file()}
        expected = set(EXPECTED_FILES)
        new_in_dir = actual - expected
        self.assertFalse(
            new_in_dir,
            "Governance file(s) on disk but not in EXPECTED_FILES: "
            f"{sorted(new_in_dir)}. Add them to the list (and document in CHANGELOG).",
        )
```

- [ ] **Step 3: Run**

```bash
cd framework && python3 -m unittest tests.conformance.test_governance -v
```

Expected: PASS (existing files all in list; orphan check finds nothing today).

- [ ] **Step 4: Commit**

```bash
git -C framework add tests/conformance/requirements.txt tests/conformance/test_governance.py
git -C framework commit -m "test(conformance): pin jsonschema + guard for orphan governance files"
```

---

## Phase 1 — Tier 1: Static Checks (Extend Existing)

## Task 1.1: Add YAML schema check for all `<TYPE>-TEMPLATE.yaml`

**Files:**

- Create: `framework/tests/unit/test_template_yaml.py`

- [ ] **Step 1: Write the failing test**

```python
"""Unit: every TYPE-TEMPLATE.yaml is parseable and structurally sound."""

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import ARTIFACTS, template_path


REQUIRED_TOP_KEYS = {"metadata"}


class TemplateYamlTests(unittest.TestCase):
    def test_every_template_parses(self):
        for name in ARTIFACTS:
            with self.subTest(layer=name):
                with template_path(name).open(encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
                self.assertIsInstance(data, dict, f"{name}: template root not a mapping")

    def test_every_template_carries_required_top_keys(self):
        for name in ARTIFACTS:
            with self.subTest(layer=name):
                with template_path(name).open(encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
                missing = REQUIRED_TOP_KEYS - set(data)
                self.assertFalse(missing, f"{name}: missing top keys: {missing}")

    def test_every_section_with_size_target_has_positive_integer(self):
        for name in ARTIFACTS:
            with self.subTest(layer=name):
                with template_path(name).open(encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
                offenders = []
                for section_key, section in data.items():
                    if isinstance(section, dict) and "_size_target" in section:
                        tgt = section["_size_target"]
                        if not (isinstance(tgt, int) and tgt > 0):
                            offenders.append((section_key, tgt))
                self.assertFalse(offenders, f"{name}: bad _size_target values: {offenders}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to confirm it passes (templates already shipped)**

Run: `cd framework && python3 -m unittest tests.unit.test_template_yaml -v`
Expected: 3 tests PASS (templates were validated in AS3–AS12; this codifies the invariant).

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/unit/test_template_yaml.py
git -C framework commit -m "test(unit): YAML schema check for every TYPE-TEMPLATE.yaml"
```

## Task 1.2: Add `claude plugin validate --strict` to the static tier

**Files:**

- Create: `framework/tests/packaging/test_manifest_strict.py`

- [ ] **Step 1: Write the test**

```python
"""Packaging: `claude plugin validate --strict` passes on the bundle."""

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root


@unittest.skipUnless(shutil.which("claude"), "claude CLI not on PATH")
class ManifestStrictTests(unittest.TestCase):
    def test_plugin_validate_strict_succeeds(self):
        result = subprocess.run(
            ["claude", "plugin", "validate", str(plugin_bundle_root()), "--strict"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0,
                         f"validate --strict failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run**

Run: `cd framework && python3 -m unittest tests.packaging.test_manifest_strict -v`
Expected: PASS (it was passing in `scripts/test-plugin.sh` Phase 1).

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/packaging/test_manifest_strict.py
git -C framework commit -m "test(packaging): assert claude plugin validate --strict"
```

## Task 1.3: Extend `sdd_doc_lint` with `STRUCT01` check and `--format=json`

**Files:**

- Modify: `framework/tools/sdd_doc_lint/__init__.py`
- Modify: `framework/tools/sdd_doc_lint/__main__.py`
- Modify: `framework/platforms/claude-code-plugin/sdd_doc_lint/__init__.py` (sync target)
- Modify: `framework/platforms/claude-code-plugin/sdd_doc_lint/__main__.py` (sync target)
- Create: `framework/tests/unit/test_sdd_doc_lint_struct01.py`
- Create: `framework/tests/unit/test_sdd_doc_lint_json_format.py`

**Why this task exists:** the plan's per-layer broken fixtures (Tasks 3.2 onward) assert
that "BRD missing `project_scope`" emits `STRUCT01`. The current `sdd_doc_lint` has no
such code — it ships STY01/02/03, FM01, DG02, HASH01, CSC01, STALE01, TH02. Without
`STRUCT01` the per-layer broken-fixture tests have no deterministic detector to assert
against (the LLM-driven audit catches it, but tests need determinism). Also, Task 2.2
parses lint output with brittle `split()`. Adding `--format=json` gives every test
suite a structured channel.

- [ ] **Step 1: Write the failing STRUCT01 test**

Create `framework/tests/unit/test_sdd_doc_lint_struct01.py`:

```python
"""Unit: STRUCT01 fires when a required template section is missing."""

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root


class Struct01Tests(unittest.TestCase):

    def _run_lint(self, body: str) -> list[dict]:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "BRD-01_test.md"
            f.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "sdd_doc_lint", td, "--format=json"],
                env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
                capture_output=True, text=True, check=False,
            )
            return json.loads(result.stdout or "[]")

    def test_struct01_fires_when_required_section_missing(self):
        body = textwrap.dedent("""
            ---
            artifact_id: BRD-01
            layer: 1
            ---
            # BRD-01
            ## Document Control
            (...)
            ## Introduction
            (...)
            ## Business Objectives
            (...)
            # (project_scope deliberately omitted)
        """).strip()
        findings = self._run_lint(body)
        codes = {f["code"] for f in findings}
        self.assertIn("STRUCT01", codes, f"expected STRUCT01, got {codes}")

    def test_struct01_silent_when_all_required_sections_present(self):
        # Minimal complete BRD with all sections from the template (truncated for brevity in
        # the test fixture; the per-layer goldens are the real coverage).
        body = "---\nartifact_id: BRD-01\nlayer: 1\n---\n# BRD-01\n" + \
               "\n".join(f"## {s}\nbody\n" for s in [
                   "Document Control", "Introduction", "Business Objectives",
                   "Project Scope", "Stakeholders", "Functional Requirements",
                   "Architecture Decision Topics", "Quality Expectations",
                   "Constraints and Assumptions", "Acceptance Criteria",
                   "Business Risk Management", "Approval", "Traceability", "Glossary",
               ])
        findings = self._run_lint(body)
        codes = {f["code"] for f in findings}
        self.assertNotIn("STRUCT01", codes)
```

- [ ] **Step 2: Run to confirm it fails**

Run: `cd framework && python3 -m unittest tests.unit.test_sdd_doc_lint_struct01 -v`
Expected: both subtests FAIL (no STRUCT01, no JSON format yet).

- [ ] **Step 3: Add `_check_required_template_sections` to `framework/tools/sdd_doc_lint/__init__.py`**

The existing module exposes these helpers (verified by `grep -n "^def" __init__.py`):

| Helper | What it returns |
|---|---|
| `find_registry(start=None)` | Path to `framework/registry/LAYER_REGISTRY.yaml` |
| `_load_registry(registry=None)` | Parsed registry dict |
| `detect_layer(path, layers)` | Artifact-type string (`"BRD"`, `"PRD"`, …) or `None` |
| `_normalise_heading(heading)` | `"Project Scope"` → `"project_scope"` |
| `_section_word_counts(body)` | `[(heading, level, word_count), …]` for H2/H3 |
| `_extract_frontmatter(text)` | Parsed YAML frontmatter dict or `None` |
| `_load_section_targets(artifact, registry)` | `{section_key: size_target, …}` from `<TYPE>-TEMPLATE.yaml` |
| `Finding` (class) | Canonical finding object — use this, not raw dicts |

Add the check function — uses only published helpers above:

```python
def _check_required_template_sections(
    rel: str,
    text: str,
    artifact: str | None,
    registry: Path | None,
) -> list["Finding"]:
    """STRUCT01: every required <TYPE>-TEMPLATE.yaml section must appear as a `##` heading.

    `artifact` is detected upstream by detect_layer(); pass-through here.
    """
    findings: list[Finding] = []
    if not artifact:
        return findings
    # _load_section_targets returns {section_key: size_target}; keys are the canonical
    # section identifiers from the template, with non-required sections already excluded.
    targets = _load_section_targets(artifact, registry)
    if not targets:
        return findings
    # Body excludes frontmatter; reuse _split_frontmatter to be safe.
    _, body = _split_frontmatter(text.splitlines())
    present = {_normalise_heading(h) for h, lvl, _wc in _section_word_counts(body) if lvl == 2}
    for key in targets:
        if key not in present:
            findings.append(Finding(
                code="STRUCT01",
                severity="error",
                path=rel,
                line=1,
                section=key,
                message=f"missing required section: {key}",
            ))
    return findings
```

Wire it into `lint_file()` (around line 488 in the current module) alongside the
existing `_check_style`, `_check_frontmatter_consistency`, `_check_diagram_level` calls:

```python
findings.extend(_check_required_template_sections(rel, text, artifact, registry))
```

> All helpers above already exist in the module — verified by `grep -n "^def "
> framework/tools/sdd_doc_lint/__init__.py` (see lines 26, 120, 128, 143, 155,
> 186, 291, 305, 673). The implementer adds only the one new function and the
> one new dispatch line; no new helpers are required.

- [ ] **Step 4: Add `--format=json` flag to `framework/tools/sdd_doc_lint/__main__.py`**

Replace the existing argparse + output section with:

```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sdd_doc_lint")
    parser.add_argument("paths", nargs="+", help="file(s) or directory(ies) to lint")
    parser.add_argument(
        "--registry",
        type=Path,
        default=None,
        help="path to LAYER_REGISTRY.yaml (else $SDD_REGISTRY or an upward search)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (text = human-readable; json = single array of findings)",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    findings = []
    try:
        for arg in args.paths:
            findings.extend(lint_path(Path(arg), registry=args.registry))
    except OSError as exc:
        print(f"sdd-doc-lint: registry unavailable ({exc}); skipping.", file=sys.stderr)
        return 2

    if args.format == "json":
        import json
        payload = [
            {
                "code": f.code,
                "severity": f.severity,
                "file": str(f.path),
                "line": f.line,
                "section": getattr(f, "section", None),
                "message": f.message,
            }
            for f in sorted(findings, key=lambda x: (x.path, x.line, x.code))
        ]
        print(json.dumps(payload))
    else:
        # Existing human-readable text path: stderr for errors, stdout for warnings.
        errors = [f for f in findings if f.severity == "error"]
        for f in sorted(findings, key=lambda x: (x.path, x.line, x.code)):
            stream = sys.stderr if f.severity == "error" else sys.stdout
            print(str(f), file=stream)
        if errors:
            print(
                f"\nsdd-doc-lint: {len(errors)} error(s) across "
                f"{len({f.path for f in errors})} file(s).",
                file=sys.stderr,
            )
        elif not findings:
            print("sdd-doc-lint: no structural findings.")

    return 1 if any(f.severity == "error" for f in findings) else 0
```

> The `Finding` class (line 109 in `__init__.py`) carries `code`, `severity`,
> `path`, `line`, `message`, and an optional `section` attribute. Verify with
> `grep -n '^class Finding' framework/tools/sdd_doc_lint/__init__.py`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd framework && python3 -m unittest tests.unit.test_sdd_doc_lint_struct01 -v`
Expected: 2 subtests PASS.

- [ ] **Step 6: Re-sync the bundle copy**

```bash
cd framework && bash tools/sdd_doc_lint/sync-vendored.sh
```

- [ ] **Step 7: Verify the bundle copy also passes the new tests**

Run: `cd framework && PYTHONPATH=platforms/claude-code-plugin python3 -m unittest tests.unit.test_sdd_doc_lint_struct01 -v`
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git -C framework add tools/sdd_doc_lint/ platforms/claude-code-plugin/sdd_doc_lint/ \
                    tests/unit/test_sdd_doc_lint_struct01.py
git -C framework commit -m "lint: add STRUCT01 (missing required section) + --format=json"
```

---

## Phase 2 — Tier 2: Unit Tests

## Task 2.1: Per-skill `SKILL.md` frontmatter test

**Files:**

- Create: `framework/tests/unit/test_skill_manifests.py`

- [ ] **Step 1: Write the failing test**

```python
"""Unit: every plugin skill carries complete, current frontmatter."""

import re
import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root, skill_dirs


def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"{skill_md}: missing YAML frontmatter"
    return yaml.safe_load(match.group(1))


REQUIRED_FRONTMATTER_KEYS = {"name", "description", "metadata"}
REQUIRED_CUSTOM_FIELDS = {
    "version", "framework_spec_version", "last_updated", "skill_category",
}


def framework_version() -> str:
    return (plugin_bundle_root() / "VERSION").read_text(encoding="utf-8").strip()


class SkillManifestTests(unittest.TestCase):

    def test_every_skill_has_skill_md(self):
        missing = [d for d in skill_dirs() if not (d / "SKILL.md").exists()]
        self.assertFalse(missing, f"skills lacking SKILL.md: {missing}")

    def test_frontmatter_parses_and_has_required_top_keys(self):
        for skill in skill_dirs():
            with self.subTest(skill=skill.name):
                fm = parse_frontmatter(skill / "SKILL.md")
                self.assertGreaterEqual(set(fm), REQUIRED_FRONTMATTER_KEYS,
                                        f"{skill.name}: top-level fm missing keys")

    def test_custom_fields_complete(self):
        for skill in skill_dirs():
            with self.subTest(skill=skill.name):
                fm = parse_frontmatter(skill / "SKILL.md")
                custom = fm["metadata"].get("custom_fields", {})
                missing = REQUIRED_CUSTOM_FIELDS - set(custom)
                self.assertFalse(missing, f"{skill.name}: missing custom_fields: {missing}")

    def test_framework_spec_version_matches_bundle(self):
        target = framework_version()
        for skill in skill_dirs():
            with self.subTest(skill=skill.name):
                fm = parse_frontmatter(skill / "SKILL.md")
                got = fm["metadata"]["custom_fields"]["framework_spec_version"]
                self.assertEqual(got, target, f"{skill.name}: framework_spec_version {got!r} != bundle {target!r}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to confirm it passes**

Run: `cd framework && python3 -m unittest tests.unit.test_skill_manifests -v`
Expected: 4 tests PASS (the recent AS-series PRs aligned all skills to 0.10.0).

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/unit/test_skill_manifests.py
git -C framework commit -m "test(unit): per-skill SKILL.md frontmatter invariants"
```

## Task 2.2: Per-check `sdd_doc_lint` test matrix

**Files:**

- Create: `framework/tests/unit/test_sdd_doc_lint_checks.py`
- Create: `framework/tests/unit/lint_fixtures/sty01/sty01_banned_phrase.md`
- Create: `framework/tests/unit/lint_fixtures/sty02/sty02_oversize_section.md`
- Create: `framework/tests/unit/lint_fixtures/sty03/sty03_missing_size_marker.md`
- Create: `framework/tests/unit/lint_fixtures/hash01/hash01_id_collision.md`
- Create: `framework/tests/unit/lint_fixtures/csc01/csc01_broken_cascade.md`
- Create: `framework/tests/unit/lint_fixtures/stale01/stale01_spec_mismatch.md`
- Create: `framework/tests/unit/lint_fixtures/fm01/fm01_frontmatter_drift.md`
- Create: `framework/tests/unit/lint_fixtures/dg02/dg02_diagram_level.md`
- Create: `framework/tests/unit/lint_fixtures/th02/th02_threshold_inconsistent.md`
- Create: `framework/tests/unit/lint_fixtures/struct01/struct01_missing_section.md`
- Create: `framework/tests/unit/lint_fixtures/clean/clean.md`

- [ ] **Step 1: Create one fixture per lint code**

Each fixture is the minimum input that triggers exactly one code. Use `clean.md` as the negative baseline. Example for `sty01_banned_phrase.md`:

```markdown
---
artifact_id: TEST-01
layer: 1
---

# Test

This document is **amazing** and provides powerful capabilities.
```

(One banned phrase from `AUTHORING_STYLE.md` per fixture; the rest of the file mimics minimum-valid structure.)

- [ ] **Step 2: Write the parametrized test**

```python
"""Unit: each sdd_doc_lint check fires only on its target fixture."""

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root


FIXTURES = Path(__file__).resolve().parent / "lint_fixtures"

CASES = [
    ("sty01",   {"STY01"}),
    ("sty02",   {"STY02"}),
    ("sty03",   {"STY03"}),
    ("hash01",  {"HASH01"}),
    ("csc01",   {"CSC01"}),
    ("stale01", {"STALE01"}),
    ("fm01",    {"FM01"}),
    ("dg02",    {"DG02"}),
    ("th02",    {"TH02"}),
    ("struct01", {"STRUCT01"}),         # added by Task 1.3
    ("clean",   set()),
]


def run_lint_json(fixture_dir: Path) -> list[dict]:
    """Run sdd_doc_lint in JSON mode (added in Task 1.3) and return findings."""
    import json
    result = subprocess.run(
        [sys.executable, "-m", "sdd_doc_lint", str(fixture_dir), "--format=json"],
        env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True, check=False,
    )
    return json.loads(result.stdout or "[]")


class LintCheckMatrixTests(unittest.TestCase):
    def test_each_fixture_emits_exactly_its_expected_codes(self):
        for dirname, expected_codes in CASES:
            with self.subTest(fixture=dirname):
                fixture_dir = FIXTURES / dirname           # one fixture file per directory
                findings = run_lint_json(fixture_dir)
                emitted = {f["code"] for f in findings}
                spurious = emitted - expected_codes
                missing = expected_codes - emitted
                self.assertFalse(missing, f"{dirname}: missing codes {missing}")
                self.assertFalse(spurious, f"{dirname}: spurious codes {spurious}")
```

> **Layout note:** `sdd_doc_lint` runs against a *directory*. Each fixture lives
> in its own subdirectory so its findings are scoped: `lint_fixtures/sty01/sty01_banned_phrase.md`,
> `lint_fixtures/sty02/sty02_oversize_section.md`, etc. The `CASES` list above is keyed
> by directory name, not filename. Adjust `_fixtures.py` accordingly.

- [ ] **Step 3: Run**

Run: `cd framework && python3 -m unittest tests.unit.test_sdd_doc_lint_checks -v`
Expected: 10 subtests PASS.

- [ ] **Step 4: Commit**

```bash
git -C framework add tests/unit/test_sdd_doc_lint_checks.py tests/unit/lint_fixtures/
git -C framework commit -m "test(unit): sdd_doc_lint per-check fixture matrix"
```

## Task 2.3: Sync-script tests (`tools/sync-plugin-framework.sh`, `tools/sdd_doc_lint/sync-vendored.sh`)

**Files:**

- Create: `framework/tests/unit/test_sync_scripts.py`

- [ ] **Step 1: Write the failing test**

```python
"""Unit: sync scripts are idempotent and produce byte-identical bundles."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import FRAMEWORK, plugin_bundle_root


def hash_tree(root: Path) -> dict[str, str]:
    """Return {relative-path: sha256-hex} for every file under root."""
    import hashlib
    out = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            out[str(path.relative_to(root))] = digest
    return out


class SyncScriptIdempotencyTests(unittest.TestCase):
    def test_sync_plugin_framework_is_idempotent(self):
        sync = FRAMEWORK / "tools" / "sync-plugin-framework.sh"
        if not sync.exists():
            self.skipTest("sync-plugin-framework.sh not present")

        before = hash_tree(plugin_bundle_root() / "framework")
        result = subprocess.run(["bash", str(sync)], cwd=FRAMEWORK,
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        after = hash_tree(plugin_bundle_root() / "framework")
        diff = {k: (before.get(k), after.get(k)) for k in set(before) | set(after) if before.get(k) != after.get(k)}
        self.assertFalse(diff, f"sync-plugin-framework.sh not idempotent: {diff}")

    def test_sdd_doc_lint_vendored_sync_is_idempotent(self):
        sync = FRAMEWORK / "tools" / "sdd_doc_lint" / "sync-vendored.sh"
        if not sync.exists():
            self.skipTest("sdd_doc_lint/sync-vendored.sh not present")
        bundle_lint = plugin_bundle_root() / "sdd_doc_lint"
        before = hash_tree(bundle_lint)
        result = subprocess.run(["bash", str(sync)], cwd=FRAMEWORK,
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        after = hash_tree(bundle_lint)
        self.assertEqual(before, after, "sdd_doc_lint vendored sync not idempotent")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run**

Run: `cd framework && python3 -m unittest tests.unit.test_sync_scripts -v`
Expected: 2 tests PASS (or skip if scripts absent).

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/unit/test_sync_scripts.py
git -C framework commit -m "test(unit): sync scripts produce idempotent bundles"
```

---

## Phase 3 — Tier 3: Per-Layer Acceptance (Deterministic)

## Task 3.1: Author the shared per-layer harness

**Files:**

- Create: `framework/tests/acceptance/_harness.py`

- [ ] **Step 1: Write the harness**

```python
"""Shared harness for per-layer acceptance tests (deterministic tier)."""

import re
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import ARTIFACTS, layer_root, plugin_bundle_root, template_path


FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"


def fixtures_for(layer_index: int, kind: str) -> Path:
    """Return the fixture directory for `valid` or `broken` per 1-indexed layer."""
    layer_name = ARTIFACTS[layer_index - 1].lower()
    folder = f"layer_{layer_index:02d}_{layer_name}"
    return FIXTURES_ROOT / folder / kind


def template_sections(name: str) -> list[str]:
    """Return required section keys from <TYPE>-TEMPLATE.yaml, in order."""
    with template_path(name).open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return [
        key for key, value in data.items()
        if isinstance(value, dict) and value.get("required", True) and key != "metadata"
    ]


def run_lint(target: Path) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, "-m", "sdd_doc_lint", str(target)],
        env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True, check=False,
    )
    return result.returncode, result.stdout + result.stderr


def headings(md_or_yaml: Path) -> list[str]:
    text = md_or_yaml.read_text(encoding="utf-8")
    if md_or_yaml.suffix == ".md":
        return [
            re.sub(r"[^a-z0-9]+", "_", line.lstrip("#").strip().lower()).strip("_")
            for line in text.splitlines() if line.startswith("## ")
        ]
    # YAML: top-level keys
    data = yaml.safe_load(text)
    return [k for k in data if not k.startswith("_") and k != "metadata"]


class LayerHarness:
    """Mix-in providing the four per-layer acceptance assertions."""

    LAYER_INDEX: int  # subclass sets this
    LAYER_NAME: str   # subclass sets this

    def assert_golden_passes_lint(self, golden: Path):
        rc, output = run_lint(golden)
        self.assertEqual(rc, 0, f"golden {golden.name} lint failed:\n{output}")  # type: ignore

    def assert_broken_fixture_emits_expected_codes(self, broken_dir: Path):
        for codes_file in broken_dir.glob("*_drift_codes.yaml"):
            with codes_file.open(encoding="utf-8") as fh:
                manifest = yaml.safe_load(fh)
            fixture = broken_dir / manifest["file"]
            _, output = run_lint(fixture)
            for finding in manifest["expected_findings"]:
                code = finding["code"]
                self.assertIn(code, output,                          # type: ignore
                              f"{fixture.name}: missing expected {code}\nLINT OUTPUT:\n{output}")

    def assert_template_sections_present_in_golden(self, golden: Path):
        expected = template_sections(self.LAYER_NAME)
        present = set(headings(golden))
        missing = [s for s in expected if s not in present]
        self.assertFalse(missing,                                    # type: ignore
                         f"{golden.name}: missing template sections {missing}")

    def assert_cumulative_upstream_tags_resolve(self, golden: Path):
        """For layer index N > 1, every @brd/@prd/... reference resolves.

        Tag format rules (from SKILL.md docs):
          BRD, PRD, EARS, BDD       — element refs in DOT form:  TYPE.NN.SS.xxxx
          ADR, SPEC                 — document refs in DASH form: TYPE-NN
                                      (TYPE.NN.SS.xxxx also valid for element refs)
          TDD                       — element refs in DOT form: TDD.NN.04.xxxx
                                      (document refs TDD-NN also valid)
          IPLAN                     — only ever document refs: IPLAN-NN
                                      (no dotted element form exists)

        The harness accepts EITHER form for ADR/SPEC/TDD/IPLAN per the rules above.
        BRD/PRD/EARS/BDD only accept dot form. The test asserts at least one
        well-formed reference per upstream layer.
        """
        if self.LAYER_INDEX == 1:
            return  # BRD has no upstream
        text = golden.read_text(encoding="utf-8")
        DOT_ONLY = {"BRD", "PRD", "EARS", "BDD"}
        for upstream_idx in range(1, self.LAYER_INDEX):
            upstream_name = ARTIFACTS[upstream_idx - 1]
            tag = f"@{upstream_name.lower()}:"
            dot = rf"{tag}\s+{upstream_name}\.\d+\.\d+\.[a-f0-9]{{4,8}}"
            dash = rf"{tag}\s+{upstream_name}-\d+"
            if upstream_name in DOT_ONLY:
                pattern = dot
            else:
                pattern = rf"(?:{dot})|(?:{dash})"
            self.assertRegex(text, pattern,                          # type: ignore
                             f"{golden.name}: no {tag} reference matching {pattern}")
```

- [ ] **Step 2: Commit**

```bash
git -C framework add tests/acceptance/_harness.py
git -C framework commit -m "test(acceptance): shared per-layer harness"
```

## Task 3.2: BRD layer — author fixtures and test

**Files:**

- Create: `framework/tests/acceptance/fixtures/layer_01_brd/valid/BRD-01_golden.md`
- Create: `framework/tests/acceptance/fixtures/layer_01_brd/broken/BRD-01_missing_section.md`
- Create: `framework/tests/acceptance/fixtures/layer_01_brd/broken/BRD-01_drift_codes.yaml`
- Create: `framework/tests/acceptance/deterministic/test_layer_brd.py`

- [ ] **Step 1: Author the BRD golden fixture from `BRD-TEMPLATE.yaml`**

Generate `BRD-01_golden.md` by enumerating the template's required sections. Engineer instruction:

```bash
# Render the canonical section list for BRD
python3 -c "
import yaml, pathlib
data = yaml.safe_load(pathlib.Path('framework/layers/01_BRD/BRD-TEMPLATE.yaml').read_text())
for k,v in data.items():
    if isinstance(v,dict) and v.get('required',True) and k!='metadata':
        print('##', k)
"
```

Then hand-write minimum-passing content under each `##` heading (Document Control first, then §3–§15 per template). Hashes are deterministic; commit them once and they freeze.

- [ ] **Step 2: Author the BRD broken fixture**

Copy the golden, remove §5 `project_scope`. Save the codes manifest:

```yaml
# BRD-01_drift_codes.yaml
file: BRD-01_missing_section.md
expected_findings:
  - code: STRUCT01
    message_match: "missing required section: project_scope"
```

- [ ] **Step 3: Write the test**

```python
"""Deterministic acceptance: Layer 1 — BRD."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


class LayerBrdTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 1
    LAYER_NAME = "BRD"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "BRD-01_golden.md"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_no_upstream_tags_on_layer_one(self):
        text = self.golden.read_text(encoding="utf-8")
        for tag in ("@brd:", "@prd:", "@ears:", "@bdd:", "@adr:", "@spec:", "@tdd:"):
            self.assertNotIn(tag, text, f"{self.golden.name} has unexpected upstream tag {tag}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run**

Run: `cd framework && python3 -m unittest tests.acceptance.deterministic.test_layer_brd -v`
Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git -C framework add tests/acceptance/fixtures/layer_01_brd/ tests/acceptance/deterministic/test_layer_brd.py
git -C framework commit -m "test(acceptance): Layer 1 BRD golden + broken fixtures + tests"
```

## Task 3.3: PRD layer — author fixtures and test

**Files:**

- Create: `framework/tests/acceptance/fixtures/layer_02_prd/valid/PRD-01_golden.md`
- Create: `framework/tests/acceptance/fixtures/layer_02_prd/broken/PRD-01_missing_section.md`
- Create: `framework/tests/acceptance/fixtures/layer_02_prd/broken/PRD-01_drift_codes.yaml`
- Create: `framework/tests/acceptance/deterministic/test_layer_prd.py`

- [ ] **Step 1: Author the PRD golden fixture from `PRD-TEMPLATE.yaml`**

Enumerate the 15 required sections:

```bash
python3 -c "
import yaml, pathlib
data = yaml.safe_load(pathlib.Path('framework/layers/02_PRD/PRD-TEMPLATE.yaml').read_text())
for k,v in data.items():
    if isinstance(v,dict) and v.get('required',True) and k!='metadata':
        print('##', k)
"
```

Hand-write minimum-passing content under each `##` heading. Frontmatter must
carry `artifact_id: PRD-01` and `layer: 2`. Section 10 (Customer-Facing Content)
must list at least 3 substantive categories (it's MANDATORY per the doc-prd skill).
Cite a single `@brd:` element from layer_01_brd/valid/BRD-01_golden.md.

- [ ] **Step 2: Author the broken fixture**

Copy the golden, remove `customer_facing_content` (§10). Write
`PRD-01_drift_codes.yaml`:

```yaml
file: PRD-01_missing_section.md
expected_findings:
  - code: STRUCT01
    message_match: "missing required section: customer_facing_content"
```

- [ ] **Step 3: Write the test**

```python
"""Deterministic acceptance: Layer 2 — PRD."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


class LayerPrdTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 2
    LAYER_NAME = "PRD"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "PRD-01_golden.md"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_customer_facing_content_has_at_least_3_substantive_categories(self):
        text = self.golden.read_text(encoding="utf-8")
        # Locate §10 by heading; count H3 subsections with non-trivial bodies.
        match = re.search(r"^##\s+Customer[- ]Facing.*?$(.*?)(?=^##\s|\Z)",
                          text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(match, "PRD-01: §10 Customer-Facing Content not found")
        body = match.group(1)
        categories = re.findall(r"^###\s+(.+)$", body, re.MULTILINE)
        # Substantive = at least one non-empty content line after the heading.
        substantive = [
            c for c in categories
            if re.search(rf"^###\s+{re.escape(c)}\s*\n\s*[A-Za-z]", body, re.MULTILINE)
        ]
        self.assertGreaterEqual(len(substantive), 3,
                                f"PRD-01 §10: need ≥3 substantive categories, got {substantive}")
```

- [ ] **Step 4: Run**

Run: `cd framework && python3 -m unittest tests.acceptance.deterministic.test_layer_prd -v`
Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git -C framework add tests/acceptance/fixtures/layer_02_prd/ tests/acceptance/deterministic/test_layer_prd.py
git -C framework commit -m "test(acceptance): Layer 2 PRD golden + broken fixtures + tests"
```

## Task 3.4: EARS layer — author fixtures and test

**Files:**

- Create: `framework/tests/acceptance/fixtures/layer_03_ears/valid/EARS-01_golden.md`
- Create: `framework/tests/acceptance/fixtures/layer_03_ears/broken/EARS-01_missing_section.md`
- Create: `framework/tests/acceptance/fixtures/layer_03_ears/broken/EARS-01_drift_codes.yaml`
- Create: `framework/tests/acceptance/deterministic/test_layer_ears.py`

- [ ] **Step 1: Author the EARS golden**

Enumerate sections from `EARS-TEMPLATE.yaml`. Every requirement under
`requirements` MUST use the canonical EARS form:
`WHEN <trigger> THE <system> SHALL <response> WITHIN <constraint>`.
Frontmatter: `artifact_id: EARS-01`, `layer: 3`. Carry `@brd:` and `@prd:` tags
referencing the layer 1 and 2 goldens.

- [ ] **Step 2: Author the broken fixture**

Remove the `requirements` section. `EARS-01_drift_codes.yaml`:

```yaml
file: EARS-01_missing_section.md
expected_findings:
  - code: STRUCT01
    message_match: "missing required section: requirements"
```

- [ ] **Step 3: Write the test**

```python
"""Deterministic acceptance: Layer 3 — EARS."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


EARS_FORM = re.compile(
    r"\bWHEN\b.+?\bTHE\b.+?\bSHALL\b.+?\bWITHIN\b",
    re.IGNORECASE | re.DOTALL,
)


class LayerEarsTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 3
    LAYER_NAME = "EARS"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "EARS-01_golden.md"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_every_requirement_uses_canonical_ears_form(self):
        text = self.golden.read_text(encoding="utf-8")
        # Each requirement is an H3 under the requirements section.
        section = re.search(r"^##\s+Requirements\b(.*?)(?=^##\s|\Z)",
                            text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(section, "EARS-01: Requirements section missing")
        body = section.group(1)
        items = re.split(r"^###\s+", body, flags=re.MULTILINE)[1:]
        self.assertTrue(items, "EARS-01: no requirements under §Requirements")
        for i, item in enumerate(items, start=1):
            with self.subTest(requirement_index=i):
                self.assertRegex(item, EARS_FORM,
                                 f"requirement {i} not in WHEN-THE-SHALL-WITHIN form")
```

- [ ] **Step 4: Run + commit**

```bash
cd framework && python3 -m unittest tests.acceptance.deterministic.test_layer_ears -v
git -C framework add tests/acceptance/fixtures/layer_03_ears/ tests/acceptance/deterministic/test_layer_ears.py
git -C framework commit -m "test(acceptance): Layer 3 EARS golden + broken fixtures + tests"
```

## Task 3.5: BDD layer — author fixtures and test

**Files:**

- Create: `framework/tests/acceptance/fixtures/layer_04_bdd/valid/BDD-01_golden.feature`
- Create: `framework/tests/acceptance/fixtures/layer_04_bdd/broken/BDD-01_missing_section.feature`
- Create: `framework/tests/acceptance/fixtures/layer_04_bdd/broken/BDD-01_drift_codes.yaml`
- Create: `framework/tests/acceptance/deterministic/test_layer_bdd.py`

- [ ] **Step 1: Author the BDD golden**

Standard Gherkin: `Feature:` declaration, optional `Background:`, then one or more
`Scenario:` blocks. Each scenario has `Given … When … Then …` steps. Frontmatter
(in a comment block at top): `# artifact_id: BDD-01`, `# layer: 4`. Tag scenarios
with `@brd:`, `@prd:`, `@ears:` references to upstream goldens.

- [ ] **Step 2: Author the broken fixture**

Remove the `Then` step from every scenario. `BDD-01_drift_codes.yaml`:

```yaml
file: BDD-01_missing_section.feature
expected_findings:
  - code: STRUCT01
    message_match: "missing required section: scenarios"
```

(If BDD's template uses `scenarios` as a top-level key — verify against
`BDD-TEMPLATE.feature` / `.yaml`; substitute the actual required section name.)

- [ ] **Step 3: Write the test**

```python
"""Deterministic acceptance: Layer 4 — BDD."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


class LayerBddTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 4
    LAYER_NAME = "BDD"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "BDD-01_golden.feature"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_every_scenario_has_given_when_then(self):
        text = self.golden.read_text(encoding="utf-8")
        scenarios = re.split(r"^\s*Scenario(?:\s+Outline)?:", text, flags=re.MULTILINE)[1:]
        self.assertTrue(scenarios, "BDD-01: no Scenario blocks")
        for i, body in enumerate(scenarios, start=1):
            with self.subTest(scenario_index=i):
                self.assertRegex(body, r"\bGiven\b", f"scenario {i} missing Given")
                self.assertRegex(body, r"\bWhen\b",  f"scenario {i} missing When")
                self.assertRegex(body, r"\bThen\b",  f"scenario {i} missing Then")
```

- [ ] **Step 4: Run + commit**

```bash
cd framework && python3 -m unittest tests.acceptance.deterministic.test_layer_bdd -v
git -C framework add tests/acceptance/fixtures/layer_04_bdd/ tests/acceptance/deterministic/test_layer_bdd.py
git -C framework commit -m "test(acceptance): Layer 4 BDD golden + broken fixtures + tests"
```

## Task 3.6: ADR layer — author fixtures and test

**Files:**

- Create: `framework/tests/acceptance/fixtures/layer_05_adr/valid/ADR-01_golden.md`
- Create: `framework/tests/acceptance/fixtures/layer_05_adr/broken/ADR-01_missing_section.md`
- Create: `framework/tests/acceptance/fixtures/layer_05_adr/broken/ADR-01_drift_codes.yaml`
- Create: `framework/tests/acceptance/deterministic/test_layer_adr.py`

- [ ] **Step 1: Author the ADR golden**

Enumerate sections from `ADR-TEMPLATE.yaml`. Frontmatter: `artifact_id: ADR-01`,
`layer: 5`. Carry cumulative `@brd:`, `@prd:`, `@ears:`, `@bdd:` references.
Status must be one of `Proposed | Accepted | Superseded | Deprecated`. Use
`Accepted` in the golden.

- [ ] **Step 2: Author the broken fixture**

Remove the `consequences` section. `ADR-01_drift_codes.yaml`:

```yaml
file: ADR-01_missing_section.md
expected_findings:
  - code: STRUCT01
    message_match: "missing required section: consequences"
```

- [ ] **Step 3: Write the test**

```python
"""Deterministic acceptance: Layer 5 — ADR."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


VALID_STATUSES = {"Proposed", "Accepted", "Superseded", "Deprecated"}


class LayerAdrTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 5
    LAYER_NAME = "ADR"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "ADR-01_golden.md"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_golden_carries_every_required_template_section(self):
        self.assert_template_sections_present_in_golden(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_status_is_a_valid_adr_status(self):
        text = self.golden.read_text(encoding="utf-8")
        match = re.search(r"^[*-]?\s*Status:\s*(\w+)", text, re.MULTILINE | re.IGNORECASE)
        self.assertIsNotNone(match, "ADR-01: Status line missing")
        self.assertIn(match.group(1), VALID_STATUSES,
                      f"ADR-01: Status {match.group(1)!r} not in {VALID_STATUSES}")
```

- [ ] **Step 4: Run + commit**

```bash
cd framework && python3 -m unittest tests.acceptance.deterministic.test_layer_adr -v
git -C framework add tests/acceptance/fixtures/layer_05_adr/ tests/acceptance/deterministic/test_layer_adr.py
git -C framework commit -m "test(acceptance): Layer 5 ADR golden + broken fixtures + tests"
```

## Task 3.7: SPEC layer — author fixtures and test

**Files:**

- Create: `framework/tests/acceptance/fixtures/layer_06_spec/valid/SPEC-01_golden.yaml`
- Create: `framework/tests/acceptance/fixtures/layer_06_spec/broken/SPEC-01_missing_section.yaml`
- Create: `framework/tests/acceptance/fixtures/layer_06_spec/broken/SPEC-01_drift_codes.yaml`
- Create: `framework/tests/acceptance/deterministic/test_layer_spec.py`

- [ ] **Step 1: Author the SPEC golden**

SPEC is YAML (not markdown). Mirror the 8 sections in `SPEC-TEMPLATE.yaml`.
`metadata: {document_type: spec-document, layer: 6, artifact_id: SPEC-01}`.
Carry `@brd:`, `@prd:`, `@ears:`, `@bdd:` (dot form) and `@adr:` (dash form,
e.g. `@adr: ADR-01`) references.

- [ ] **Step 2: Author the broken fixture**

Remove the `interfaces` section. `SPEC-01_drift_codes.yaml`:

```yaml
file: SPEC-01_missing_section.yaml
expected_findings:
  - code: STRUCT01
    message_match: "missing required section: interfaces"
```

- [ ] **Step 3: Write the test**

```python
"""Deterministic acceptance: Layer 6 — SPEC (YAML)."""

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


class LayerSpecTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 6
    LAYER_NAME = "SPEC"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "SPEC-01_golden.yaml"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_parses_as_yaml_with_metadata_layer_6(self):
        data = yaml.safe_load(self.golden.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict, "SPEC-01: not a YAML mapping")
        self.assertEqual(data.get("metadata", {}).get("layer"), 6,
                         f"SPEC-01: metadata.layer != 6: {data.get('metadata')}")
```

- [ ] **Step 4: Run + commit**

```bash
cd framework && python3 -m unittest tests.acceptance.deterministic.test_layer_spec -v
git -C framework add tests/acceptance/fixtures/layer_06_spec/ tests/acceptance/deterministic/test_layer_spec.py
git -C framework commit -m "test(acceptance): Layer 6 SPEC golden + broken fixtures + tests"
```

## Task 3.8: TDD layer — author fixtures and test

**Files:**

- Create: `framework/tests/acceptance/fixtures/layer_07_tdd/valid/TDD-01_golden.yaml`
- Create: `framework/tests/acceptance/fixtures/layer_07_tdd/broken/TDD-01_missing_section.yaml`
- Create: `framework/tests/acceptance/fixtures/layer_07_tdd/broken/TDD-01_drift_codes.yaml`
- Create: `framework/tests/acceptance/deterministic/test_layer_tdd.py`

- [ ] **Step 1: Author the TDD golden**

YAML; 7 sections per `TDD-TEMPLATE.yaml`. Section 4 holds `test_cases`; each
case carries `id`, `type` (one of `unit | integration | functional | e2e | smoke
| performance | security`), `spec_ref`. Carry cumulative `@brd:`, `@prd:`,
`@ears:`, `@bdd:` (dot form) and `@adr:`, `@spec:` (dash form).

- [ ] **Step 2: Author the broken fixture**

Remove the `test_pyramid` section (Section 2). `TDD-01_drift_codes.yaml`:

```yaml
file: TDD-01_missing_section.yaml
expected_findings:
  - code: STRUCT01
    message_match: "missing required section: test_pyramid"
```

- [ ] **Step 3: Write the test**

```python
"""Deterministic acceptance: Layer 7 — TDD (YAML)."""

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


VALID_TYPES = {"unit", "integration", "functional", "e2e",
               "smoke", "performance", "security"}


class LayerTddTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 7
    LAYER_NAME = "TDD"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "TDD-01_golden.yaml"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_every_test_case_has_a_valid_type(self):
        data = yaml.safe_load(self.golden.read_text(encoding="utf-8"))
        cases = data.get("test_cases") or data.get("test_case_definitions") or []
        self.assertTrue(cases, "TDD-01: no test_cases / test_case_definitions found")
        for i, case in enumerate(cases, start=1):
            with self.subTest(case_index=i):
                t = case.get("type")
                self.assertIn(t, VALID_TYPES,
                              f"TDD-01 case {i}: type {t!r} not in {VALID_TYPES}")
```

- [ ] **Step 4: Run + commit**

```bash
cd framework && python3 -m unittest tests.acceptance.deterministic.test_layer_tdd -v
git -C framework add tests/acceptance/fixtures/layer_07_tdd/ tests/acceptance/deterministic/test_layer_tdd.py
git -C framework commit -m "test(acceptance): Layer 7 TDD golden + broken fixtures + tests"
```

## Task 3.9: IPLAN layer — author fixtures and test

**Files:**

- Create: `framework/tests/acceptance/fixtures/layer_08_iplan/valid/IPLAN-01_golden.yaml`
- Create: `framework/tests/acceptance/fixtures/layer_08_iplan/broken/IPLAN-01_missing_section.yaml`
- Create: `framework/tests/acceptance/fixtures/layer_08_iplan/broken/IPLAN-01_drift_codes.yaml`
- Create: `framework/tests/acceptance/deterministic/test_layer_iplan.py`

- [ ] **Step 1: Author the IPLAN golden**

YAML; 6 sections per `IPLAN-TEMPLATE.yaml`. Permanent variant (not tmp/).
`metadata.layer: 8`, `document_type: iplan-document`. `file_manifest` lists
test files **before** their implementation files (TDD principle). `sessions[0]`
carries a populated `next_session_directive`. Carry cumulative `@brd:`, `@prd:`,
`@ears:`, `@bdd:` (dot form), `@adr:`, `@spec:`, `@tdd:` (mixed dot/dash per
`doc-iplan` rules).

- [ ] **Step 2: Author the broken fixture**

Remove the `implementation_contracts` section. `IPLAN-01_drift_codes.yaml`:

```yaml
file: IPLAN-01_missing_section.yaml
expected_findings:
  - code: STRUCT01
    message_match: "missing required section: implementation_contracts"
```

- [ ] **Step 3: Write the test**

```python
"""Deterministic acceptance: Layer 8 — IPLAN (YAML)."""

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import LayerHarness, fixtures_for


class LayerIplanTests(unittest.TestCase, LayerHarness):
    LAYER_INDEX = 8
    LAYER_NAME = "IPLAN"

    def setUp(self):
        self.valid = fixtures_for(self.LAYER_INDEX, "valid")
        self.broken = fixtures_for(self.LAYER_INDEX, "broken")
        self.golden = self.valid / "IPLAN-01_golden.yaml"

    def test_golden_passes_lint(self):
        self.assert_golden_passes_lint(self.golden)

    def test_broken_fixture_emits_expected_codes(self):
        self.assert_broken_fixture_emits_expected_codes(self.broken)

    def test_cumulative_upstream_tags_resolve(self):
        self.assert_cumulative_upstream_tags_resolve(self.golden)

    def test_file_manifest_lists_tests_before_implementation(self):
        data = yaml.safe_load(self.golden.read_text(encoding="utf-8"))
        manifest = data.get("file_manifest") or []
        self.assertTrue(manifest, "IPLAN-01: file_manifest is empty")
        first_impl_idx = next(
            (i for i, f in enumerate(manifest)
             if not str(f.get("path", "")).startswith(("tests/", "test_"))
             and ".test." not in str(f.get("path", ""))),
            None,
        )
        if first_impl_idx is None:
            return  # all entries are tests — vacuously OK
        # Every test file must precede the first non-test file.
        test_entries_after = [
            f for f in manifest[first_impl_idx:]
            if str(f.get("path", "")).startswith(("tests/", "test_"))
            or ".test." in str(f.get("path", ""))
        ]
        self.assertFalse(
            test_entries_after,
            f"IPLAN-01: file_manifest must list ALL tests before any implementation; "
            f"found {len(test_entries_after)} test entry(ies) after the first impl entry",
        )

    def test_first_session_has_next_session_directive(self):
        data = yaml.safe_load(self.golden.read_text(encoding="utf-8"))
        sessions = (data.get("session_handoff") or {}).get("sessions") or []
        self.assertTrue(sessions, "IPLAN-01: session_handoff.sessions is empty")
        directive = sessions[0].get("next_session_directive")
        self.assertTrue(directive,
                        "IPLAN-01: first session lacks a next_session_directive")
```

- [ ] **Step 4: Run + commit**

```bash
cd framework && python3 -m unittest tests.acceptance.deterministic.test_layer_iplan -v
git -C framework add tests/acceptance/fixtures/layer_08_iplan/ tests/acceptance/deterministic/test_layer_iplan.py
git -C framework commit -m "test(acceptance): Layer 8 IPLAN golden + broken fixtures + tests"
```

## Task 3.10: Per-layer test runner script

**Files:**

- Create: `scripts/test-layer.sh` (parent repo)

- [ ] **Step 1: Write the wrapper**

```bash
#!/usr/bin/env bash
# scripts/test-layer.sh — run one layer's deterministic acceptance suite
set -uo pipefail

LAYER="${1:-}"
if [[ -z "$LAYER" ]]; then
  echo "Usage: bash scripts/test-layer.sh <brd|prd|ears|bdd|adr|spec|tdd|iplan>" >&2
  exit 2
fi

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO/framework"
exec python3 -m unittest "tests.acceptance.deterministic.test_layer_${LAYER}" -v
```

- [ ] **Step 2: Smoke-test**

```bash
chmod +x scripts/test-layer.sh
bash scripts/test-layer.sh brd
```

Expected: 4 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add scripts/test-layer.sh
git commit -m "test: scripts/test-layer.sh — per-layer test runner"
```

---

## Phase 4 — Tier 3: Per-Layer Acceptance (Live, Opt-In)

## Task 4.1: Live harness

**Files:**

- Create: `framework/tests/acceptance/live/_live_harness.py`

- [ ] **Step 1: Write the gating helper**

```python
"""Live tier harness — skipped unless LIVE=1 in env."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import plugin_bundle_root


LIVE_ENABLED = os.environ.get("LIVE") == "1"
HAS_CLAUDE = shutil.which("claude") is not None

skipUnlessLive = unittest.skipUnless(
    LIVE_ENABLED and HAS_CLAUDE,
    "live tier disabled (set LIVE=1 and ensure `claude` CLI is on PATH)",
)


TOKEN_LEDGER = Path(os.environ.get("TOKEN_LEDGER", "tmp/token-ledger.json"))


def _append_ledger(test_id: str, prompt_chars: int, response_chars: int, elapsed_s: float) -> None:
    """Append a per-call entry. CI aggregates these to enforce tier budgets.

    `_chars` is a portable proxy for token count (~4 chars/token for English).
    If a future Claude CLI version emits structured token counts, replace this
    proxy with the real value — same field name, no test changes needed.
    """
    import json
    TOKEN_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    ledger: list[dict] = []
    if TOKEN_LEDGER.exists():
        try:
            ledger = json.loads(TOKEN_LEDGER.read_text(encoding="utf-8")) or []
        except json.JSONDecodeError:
            ledger = []
    ledger.append({
        "test_id": test_id,
        "approx_input_tokens": prompt_chars // 4,
        "approx_output_tokens": response_chars // 4,
        "elapsed_s": round(elapsed_s, 2),
    })
    TOKEN_LEDGER.write_text(json.dumps(ledger, indent=2), encoding="utf-8")


def invoke_skill(prompt: str, cwd: Path, timeout: int = 300,
                 test_id: str = "unknown") -> str:
    """Invoke a /aidoc-flow:* command via `claude -p` and return stdout.

    Records an entry to TOKEN_LEDGER so CI can enforce per-tier token budgets
    (see PLUGIN-TEST-SUITE-PLAN.md §15.1).
    """
    import time as _time
    start = _time.monotonic()
    result = subprocess.run(
        ["claude", "--plugin-dir", str(plugin_bundle_root()),
         "--dangerously-skip-permissions", "-p", prompt],
        cwd=str(cwd), capture_output=True, text=True, timeout=timeout, check=False,
    )
    elapsed = _time.monotonic() - start
    _append_ledger(test_id, prompt_chars=len(prompt),
                   response_chars=len(result.stdout), elapsed_s=elapsed)
    if result.returncode != 0:
        raise RuntimeError(f"claude -p exit {result.returncode}:\n{result.stderr}")
    return result.stdout
```

- [ ] **Step 2: Commit**

```bash
git -C framework add tests/acceptance/live/_live_harness.py
git -C framework commit -m "test(acceptance,live): gating harness (skipUnlessLive, invoke_skill)"
```

## Task 4.2: Live BRD probe

**Files:**

- Create: `framework/tests/acceptance/live/test_layer_brd_live.py`

- [ ] **Step 1: Write the test**

```python
"""Live acceptance: Layer 1 — BRD prompted from a synthetic seed."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _harness import run_lint, template_sections, headings
from _live_harness import skipUnlessLive, invoke_skill


@skipUnlessLive
class LayerBrdLiveTests(unittest.TestCase):

    def test_doc_brd_emits_an_artifact_with_all_required_sections(self):
        seed = "Build a URL shortener: shorten, redirect, count clicks. Target: 1M URLs/day."
        with tempfile.TemporaryDirectory() as td:
            workspace = Path(td)
            (workspace / "docs" / "01_BRD").mkdir(parents=True, exist_ok=True)
            prompt = (
                "/aidoc-flow:doc-brd Create BRD-01 from this brief and write it to "
                "docs/01_BRD/BRD-01_url_shortener/. Brief: " + seed
            )
            invoke_skill(prompt, cwd=workspace, timeout=420)

            brd_dir = workspace / "docs" / "01_BRD"
            candidates = list(brd_dir.rglob("BRD-01*.md"))
            self.assertTrue(candidates, "doc-brd produced no BRD-01_*.md output")
            brd = candidates[0]

            present = set(headings(brd))
            missing = [s for s in template_sections("BRD") if s not in present]
            self.assertFalse(missing, f"live BRD missing required sections: {missing}\nFile: {brd}")

            rc, output = run_lint(brd.parent)
            self.assertEqual(rc, 0, f"sdd_doc_lint failed on live BRD:\n{output}")
```

- [ ] **Step 2: Run live (opt-in)**

Run: `LIVE=1 cd framework && python3 -m unittest tests.acceptance.live.test_layer_brd_live -v`
Expected: 1 test PASS (takes 1–3 min; costs tokens).

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/acceptance/live/test_layer_brd_live.py
git -C framework commit -m "test(acceptance,live): doc-brd produces template-conformant BRD-01"
```

## Task 4.2.5: Add shared live-layer helper to `_live_harness.py`

**Files:**

- Modify: `framework/tests/acceptance/live/_live_harness.py`

The 7 downstream live tests are structurally identical: stage upstreams, invoke
skill, assert artifact + sections + lint + tags. Extract once, call seven times.

- [ ] **Step 1: Extend `_live_harness.py`**

Append to the file from Task 4.1:

```python
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import (
    fixtures_for, headings, run_lint, template_sections,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import ARTIFACTS


LAYER_OUT_EXT = {  # filename extension the skill writes per layer
    1: ".md", 2: ".md", 3: ".md", 4: ".feature",
    5: ".md", 6: ".yaml", 7: ".yaml", 8: ".yaml",
}


def stage_upstreams_into(workspace: Path, layer_index: int) -> None:
    """Copy every layer 1..N-1 golden into <workspace>/docs/<NN>_<TYPE>/."""
    for upstream_idx in range(1, layer_index):
        upstream_name = ARTIFACTS[upstream_idx - 1]
        src = fixtures_for(upstream_idx, "valid")
        dst = workspace / "docs" / f"{upstream_idx:02d}_{upstream_name}"
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if item.is_dir():
                shutil.copytree(item, dst / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst / item.name)


def assert_live_layer_conformant(testcase, layer_index: int, prompt: str,
                                 timeout: int = 420, test_id: str | None = None) -> None:
    """Stage upstreams, invoke `claude -p`, assert artifact passes structural checks.

    `test_id` is forwarded to invoke_skill so token-ledger entries bucket per tier
    (e.g. "T3L.brd.01"). If omitted, derives from the test class + method name via
    the testcase object, so per-layer ledger attribution works without callers
    threading the id manually.
    """
    layer_name = ARTIFACTS[layer_index - 1]
    ext = LAYER_OUT_EXT[layer_index]
    if test_id is None:
        # Derive: "test_layer_brd_live.LayerBrdLiveTests.test_…" → "T3L.brd.<method>"
        method = getattr(testcase, "_testMethodName", "unknown")
        test_id = f"T3L.{layer_name.lower()}.{method}"
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        stage_upstreams_into(ws, layer_index)
        (ws / "docs" / f"{layer_index:02d}_{layer_name}").mkdir(parents=True, exist_ok=True)
        invoke_skill(prompt, cwd=ws, timeout=timeout, test_id=test_id)

        candidates = list((ws / "docs" / f"{layer_index:02d}_{layer_name}").rglob(f"{layer_name}-01*{ext}"))
        testcase.assertTrue(candidates, f"no {layer_name}-01{ext} emitted")
        artifact = candidates[0]

        present = set(headings(artifact))
        missing = [s for s in template_sections(layer_name) if s not in present]
        testcase.assertFalse(missing, f"live {layer_name} missing sections: {missing}")

        rc, output = run_lint(artifact.parent)
        testcase.assertEqual(rc, 0, f"sdd_doc_lint failed:\n{output}")
```

- [ ] **Step 2: Commit**

```bash
git -C framework add tests/acceptance/live/_live_harness.py
git -C framework commit -m "test(acceptance,live): stage_upstreams + assert_live_layer_conformant helpers"
```

## Task 4.3: Live PRD probe

**Files:**

- Create: `framework/tests/acceptance/live/test_layer_prd_live.py`

- [ ] **Step 1: Write the test**

```python
"""Live acceptance: Layer 2 — PRD prompted against a staged BRD-01."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import skipUnlessLive, assert_live_layer_conformant


@skipUnlessLive
class LayerPrdLiveTests(unittest.TestCase):
    def test_doc_prd_emits_a_prd_satisfying_template(self):
        assert_live_layer_conformant(
            self, layer_index=2,
            prompt=(
                "/aidoc-flow:doc-prd Create PRD-01 from the staged BRD-01 in "
                "docs/01_BRD/. Write to docs/02_PRD/PRD-01_url_shortener/."
            ),
        )
```

- [ ] **Step 2: Run** (opt-in)

Run: `LIVE=1 cd framework && python3 -m unittest tests.acceptance.live.test_layer_prd_live -v`
Expected: PASS in ~2–4 min.

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/acceptance/live/test_layer_prd_live.py
git -C framework commit -m "test(acceptance,live): doc-prd emits template-conformant PRD-01"
```

## Task 4.4: Live EARS probe

**Files:**

- Create: `framework/tests/acceptance/live/test_layer_ears_live.py`

- [ ] **Step 1: Write the test**

```python
"""Live acceptance: Layer 3 — EARS prompted against staged BRD-01 + PRD-01."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import skipUnlessLive, assert_live_layer_conformant


@skipUnlessLive
class LayerEarsLiveTests(unittest.TestCase):
    def test_doc_ears_emits_ears_satisfying_template(self):
        assert_live_layer_conformant(
            self, layer_index=3,
            prompt=(
                "/aidoc-flow:doc-ears Create EARS-01 from the staged PRD-01. "
                "Every requirement must use WHEN-THE-SHALL-WITHIN form. "
                "Write to docs/03_EARS/EARS-01_url_shortener.md."
            ),
        )
```

- [ ] **Step 2: Run + commit**

```bash
LIVE=1 cd framework && python3 -m unittest tests.acceptance.live.test_layer_ears_live -v
git -C framework add tests/acceptance/live/test_layer_ears_live.py
git -C framework commit -m "test(acceptance,live): doc-ears emits template-conformant EARS-01"
```

## Task 4.5: Live BDD probe

**Files:**

- Create: `framework/tests/acceptance/live/test_layer_bdd_live.py`

- [ ] **Step 1: Write the test**

```python
"""Live acceptance: Layer 4 — BDD prompted against staged BRD/PRD/EARS."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import skipUnlessLive, assert_live_layer_conformant


@skipUnlessLive
class LayerBddLiveTests(unittest.TestCase):
    def test_doc_bdd_emits_bdd_satisfying_template(self):
        assert_live_layer_conformant(
            self, layer_index=4,
            prompt=(
                "/aidoc-flow:doc-bdd Create BDD-01 from the staged EARS-01. "
                "Every scenario must use Given/When/Then with concrete examples. "
                "Write to docs/04_BDD/BDD-01_url_shortener.feature."
            ),
        )
```

- [ ] **Step 2: Run + commit**

```bash
LIVE=1 cd framework && python3 -m unittest tests.acceptance.live.test_layer_bdd_live -v
git -C framework add tests/acceptance/live/test_layer_bdd_live.py
git -C framework commit -m "test(acceptance,live): doc-bdd emits template-conformant BDD-01"
```

## Task 4.6: Live ADR probe

**Files:**

- Create: `framework/tests/acceptance/live/test_layer_adr_live.py`

- [ ] **Step 1: Write the test**

```python
"""Live acceptance: Layer 5 — ADR prompted against staged BRD/PRD/EARS/BDD."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import skipUnlessLive, assert_live_layer_conformant


@skipUnlessLive
class LayerAdrLiveTests(unittest.TestCase):
    def test_doc_adr_emits_adr_satisfying_template(self):
        assert_live_layer_conformant(
            self, layer_index=5,
            prompt=(
                "/aidoc-flow:doc-adr Create ADR-01 for the short-code-generation "
                "decision. Status: Accepted. Reference BRD §8 architecture topic. "
                "Write to docs/05_ADR/ADR-01_short_code_strategy.md."
            ),
        )
```

- [ ] **Step 2: Run + commit**

```bash
LIVE=1 cd framework && python3 -m unittest tests.acceptance.live.test_layer_adr_live -v
git -C framework add tests/acceptance/live/test_layer_adr_live.py
git -C framework commit -m "test(acceptance,live): doc-adr emits template-conformant ADR-01"
```

## Task 4.7: Live SPEC probe

**Files:**

- Create: `framework/tests/acceptance/live/test_layer_spec_live.py`

- [ ] **Step 1: Write the test**

```python
"""Live acceptance: Layer 6 — SPEC prompted against staged BRD..ADR."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import skipUnlessLive, assert_live_layer_conformant


@skipUnlessLive
class LayerSpecLiveTests(unittest.TestCase):
    def test_doc_spec_emits_spec_satisfying_template(self):
        assert_live_layer_conformant(
            self, layer_index=6,
            prompt=(
                "/aidoc-flow:doc-spec Create SPEC-01 for the shorten service "
                "from the staged ADR-01. Component-level (C4-L3) only. "
                "Output: YAML at docs/06_SPEC/SPEC-01_shorten_service/SPEC-01_shorten_service.yaml."
            ),
        )
```

- [ ] **Step 2: Run + commit**

```bash
LIVE=1 cd framework && python3 -m unittest tests.acceptance.live.test_layer_spec_live -v
git -C framework add tests/acceptance/live/test_layer_spec_live.py
git -C framework commit -m "test(acceptance,live): doc-spec emits template-conformant SPEC-01"
```

## Task 4.8: Live TDD probe

**Files:**

- Create: `framework/tests/acceptance/live/test_layer_tdd_live.py`

- [ ] **Step 1: Write the test**

```python
"""Live acceptance: Layer 7 — TDD prompted against staged SPEC-01."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import skipUnlessLive, assert_live_layer_conformant


@skipUnlessLive
class LayerTddLiveTests(unittest.TestCase):
    def test_doc_tdd_emits_tdd_satisfying_template(self):
        assert_live_layer_conformant(
            self, layer_index=7,
            prompt=(
                "/aidoc-flow:doc-tdd Create TDD-01 from the staged SPEC-01 and "
                "BDD-01. Map every BDD scenario to test cases with a `type` "
                "attribute. Output: docs/07_TDD/TDD-01_shorten_service.yaml."
            ),
        )
```

- [ ] **Step 2: Run + commit**

```bash
LIVE=1 cd framework && python3 -m unittest tests.acceptance.live.test_layer_tdd_live -v
git -C framework add tests/acceptance/live/test_layer_tdd_live.py
git -C framework commit -m "test(acceptance,live): doc-tdd emits template-conformant TDD-01"
```

## Task 4.9: Live IPLAN probe

**Files:**

- Create: `framework/tests/acceptance/live/test_layer_iplan_live.py`

- [ ] **Step 1: Write the test**

```python
"""Live acceptance: Layer 8 — IPLAN prompted against staged SPEC + TDD."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import skipUnlessLive, assert_live_layer_conformant


@skipUnlessLive
class LayerIplanLiveTests(unittest.TestCase):
    def test_doc_iplan_emits_iplan_satisfying_template(self):
        assert_live_layer_conformant(
            self, layer_index=8,
            prompt=(
                "/aidoc-flow:doc-iplan Create IPLAN-01 (permanent) for SPEC-01 + "
                "TDD-01. File manifest must list tests before implementation. "
                "Output: docs/08_IPLAN/IPLAN-01_shorten_service.yaml."
            ),
        )
```

- [ ] **Step 2: Run + commit**

```bash
LIVE=1 cd framework && python3 -m unittest tests.acceptance.live.test_layer_iplan_live -v
git -C framework add tests/acceptance/live/test_layer_iplan_live.py
git -C framework commit -m "test(acceptance,live): doc-iplan emits template-conformant IPLAN-01"
```

---

## Phase 5 — Tier 4: Full-Path Acceptance (BRD → IPLAN)

## Task 5.0: Coordinate cross-layer fixture element IDs

**Files:**

- Create: `framework/tests/acceptance/_id_coordinator.py`
- Create: `framework/tests/acceptance/fixtures/fullpath/ID_REGISTRY.yaml`

**Why this task exists:** element IDs are deterministic SHA256 hashes of
`{doc_id}:{section_id}:{title}:{description}` (first 4 hex chars). The full-path
chain (Task 5.1) requires every downstream artifact to reference upstream element
IDs by exact value. PRD can't compute a `@brd:` reference until BRD's element
title + description are frozen. Without an explicit coordination step, the engineer
ends up authoring downstream goldens with placeholder hashes that drift.

**Authoring order (must be sequential):**

```
1. BRD-01 golden authored
   → compute_ids(BRD-01) → 14 element IDs
   → write to ID_REGISTRY.yaml under "layer_01_brd"
2. PRD-01 golden authored using BRD IDs from registry
   → compute_ids(PRD-01) → N element IDs
   → write to ID_REGISTRY.yaml under "layer_02_prd"
3. EARS-01 ... [same pattern]
...
8. IPLAN-01 — references all upstream IDs from registry
```

- [ ] **Step 1: Write the hash helper**

Create `framework/tests/acceptance/_id_coordinator.py`:

```python
"""Compute deterministic element IDs for fixture artifacts.

Element ID format: TYPE.NN.SS.xxxx
where xxxx = first 4 hex chars of SHA256("{doc_id}:{section_id}:{title}:{description}").
"""

import hashlib
import re
from pathlib import Path

import yaml


def element_hash(doc_id: str, section_id: str, title: str, description: str) -> str:
    """Compute the 4-hex SHA256 prefix of the canonical element key."""
    key = f"{doc_id}:{section_id}:{title}:{description}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:4]


def element_id(doc_type: str, doc_num: int, section_id: str, title: str, description: str) -> str:
    """Return TYPE.NN.SS.xxxx for the given element."""
    doc_id = f"{doc_type}-{doc_num:02d}"
    return f"{doc_type}.{doc_num:02d}.{section_id}.{element_hash(doc_id, section_id, title, description)}"


def extract_elements(artifact: Path) -> list[dict]:
    """Walk an artifact and return [{section_id, title, description, element_id}, ...].

    Dispatches by file extension:
      .md       — H2 declares the section; each H3 within that H2 is one element.
                  Description = the first non-empty paragraph following the H3.
      .yaml     — top-level keys (other than metadata/_*) are sections; each element
                  is a sub-mapping with a `title` and `description` (or `desc`) field,
                  or list items with a `name` + `description`.
      .feature  — every `Scenario:`/`Scenario Outline:` is one element of the
                  `scenarios` section; title = scenario name; description = the
                  first Given/When line.

    The element_id is computed via element_id() above and embedded so downstream
    layers can copy the literal tag.
    """
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "sdd_doc_lint"))
    from sdd_doc_lint import _normalise_heading  # type: ignore

    artifact_id_match = re.search(r"^artifact_id:\s*([A-Z]+-\d+)", artifact.read_text(encoding="utf-8"), re.MULTILINE)
    if not artifact_id_match:
        return []
    doc_type, doc_num_str = artifact_id_match.group(1).split("-", 1)
    doc_num = int(doc_num_str)

    out: list[dict] = []

    if artifact.suffix == ".md":
        lines = artifact.read_text(encoding="utf-8").splitlines()
        current_section: str | None = None
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("## "):
                current_section = _normalise_heading(line.lstrip("# ").strip())
            elif line.startswith("### ") and current_section:
                title = line.lstrip("# ").strip()
                # description = first non-empty, non-heading line after the H3
                description = ""
                for follow in lines[i + 1:]:
                    s = follow.strip()
                    if not s:
                        continue
                    if s.startswith("#"):
                        break
                    description = s
                    break
                out.append({
                    "section_id": current_section,
                    "title": title,
                    "description": description,
                    "element_id": element_id(doc_type, doc_num, current_section, title, description),
                })
            i += 1
        return out

    if artifact.suffix == ".yaml":
        data = yaml.safe_load(artifact.read_text(encoding="utf-8")) or {}
        for section_key, section in data.items():
            if section_key.startswith("_") or section_key == "metadata":
                continue
            section_id = section_key
            if isinstance(section, dict):
                for elem_key, elem in section.items():
                    if not isinstance(elem, dict):
                        continue
                    title = elem.get("title") or elem.get("name") or elem_key
                    description = elem.get("description") or elem.get("desc") or ""
                    out.append({
                        "section_id": section_id,
                        "title": str(title),
                        "description": str(description),
                        "element_id": element_id(doc_type, doc_num, section_id, str(title), str(description)),
                    })
            elif isinstance(section, list):
                for item in section:
                    if not isinstance(item, dict):
                        continue
                    title = item.get("title") or item.get("name") or ""
                    description = item.get("description") or item.get("desc") or ""
                    if not title:
                        continue
                    out.append({
                        "section_id": section_id,
                        "title": str(title),
                        "description": str(description),
                        "element_id": element_id(doc_type, doc_num, section_id, str(title), str(description)),
                    })
        return out

    if artifact.suffix == ".feature":
        text = artifact.read_text(encoding="utf-8")
        for match in re.finditer(r"^\s*(?:Scenario|Scenario Outline):\s*(.+)$", text, re.MULTILINE):
            title = match.group(1).strip()
            # description = first Given/When line after the scenario
            tail = text[match.end():]
            step_match = re.search(r"^\s*(Given|When)\s+(.+)$", tail, re.MULTILINE)
            description = step_match.group(2).strip() if step_match else ""
            out.append({
                "section_id": "scenarios",
                "title": title,
                "description": description,
                "element_id": element_id(doc_type, doc_num, "scenarios", title, description),
            })
        return out

    return []


def write_registry(registry_path: Path, layer_key: str, elements: list[dict]) -> None:
    data = {}
    if registry_path.exists():
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    data[layer_key] = elements
    registry_path.write_text(yaml.safe_dump(data, sort_keys=True), encoding="utf-8")
```

- [ ] **Step 2: Initialize empty registry**

```bash
mkdir -p framework/tests/acceptance/fixtures/fullpath
echo "# Element-ID registry. Each layer adds its IDs after authoring." \
  > framework/tests/acceptance/fixtures/fullpath/ID_REGISTRY.yaml
echo "version: 1" >> framework/tests/acceptance/fixtures/fullpath/ID_REGISTRY.yaml
```

- [ ] **Step 3: Document the workflow in `_id_coordinator.py` docstring**

```python
"""...

Workflow for authoring the fullpath golden chain (Task 5.1):

    # Step A — BRD first (no upstreams)
    author BRD-01_golden.md, freeze title+description for each H3 element
    python3 -c "
        from _id_coordinator import extract_elements, write_registry
        from pathlib import Path
        elems = extract_elements(Path('.../BRD-01_golden.md'))
        write_registry(Path('.../ID_REGISTRY.yaml'), 'layer_01_brd', elems)
    "

    # Step B — PRD references BRD IDs from registry
    open ID_REGISTRY.yaml, copy needed BRD element_id values into PRD-01_golden.md
    as @brd: BRD.01.SS.xxxx tags. Author PRD content. Compute PRD IDs:
    python3 -c "..." (same pattern)

    # Repeat for EARS, BDD, ADR, SPEC, TDD, IPLAN
"""
```

- [ ] **Step 4: Commit**

```bash
git -C framework add tests/acceptance/_id_coordinator.py \
                    tests/acceptance/fixtures/fullpath/ID_REGISTRY.yaml
git -C framework commit -m "test(acceptance): _id_coordinator + ID_REGISTRY for fullpath chain"
```

## Task 5.1: Deterministic full-path chain

**Files:**

- Create: `framework/tests/acceptance/fixtures/fullpath/golden_chain/01_BRD/BRD-01_*.md`
- ... (8 layer goldens)
- Create: `framework/tests/acceptance/deterministic/test_fullpath.py`

- [ ] **Step 1: Author all 8 layer goldens with consistent cumulative tags**

The 8 goldens reuse the per-layer goldens authored in Phase 3 (Tasks 3.2–3.9), but their element IDs and `@`-tags are coordinated:

```
BRD-01 → emits BRD.01.07.<h1>, BRD.01.08.<h2>, ...
PRD-01 → cites @brd: BRD.01.07.<h1>
EARS-01 → cites @brd: BRD.01.07.<h1> AND @prd: PRD.01.09.<h3>
... etc.
```

Engineer process:

- Copy each per-layer golden into the chain dir.
- Edit downstream layers to reference upstream IDs (using the hashes the goldens emit).
- Commit the chain as one unit.

- [ ] **Step 2: Write the test**

```python
"""Deterministic full-path acceptance: BRD-01 → IPLAN-01 chain."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import FIXTURES_ROOT, run_lint, headings, template_sections
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import ARTIFACTS


CHAIN = FIXTURES_ROOT / "fullpath" / "golden_chain"


class FullpathChainTests(unittest.TestCase):

    def test_chain_lint_passes(self):
        rc, output = run_lint(CHAIN)
        self.assertEqual(rc, 0, f"fullpath chain lint failed:\n{output}")

    def test_every_layer_has_one_artifact(self):
        for idx, name in enumerate(ARTIFACTS, start=1):
            with self.subTest(layer=name):
                folder = CHAIN / f"{idx:02d}_{name}"
                hits = list(folder.glob(f"{name}-01*"))
                self.assertEqual(len(hits), 1, f"{folder}: expected 1 artifact, got {len(hits)}")

    def test_every_layer_has_required_sections(self):
        for idx, name in enumerate(ARTIFACTS, start=1):
            with self.subTest(layer=name):
                folder = CHAIN / f"{idx:02d}_{name}"
                artifact = next(folder.glob(f"{name}-01*"))
                missing = [s for s in template_sections(name) if s not in set(headings(artifact))]
                self.assertFalse(missing, f"{name}-01: missing required sections: {missing}")

    def test_forward_tag_closure(self):
        """Every @<upstream>: reference in a downstream artifact resolves to a real ID upstream."""
        all_ids = self._gather_ids()
        for idx in range(2, 9):
            name = ARTIFACTS[idx - 1]
            folder = CHAIN / f"{idx:02d}_{name}"
            artifact = next(folder.glob(f"{name}-01*"))
            text = artifact.read_text(encoding="utf-8")
            for upstream_idx in range(1, idx):
                upstream_name = ARTIFACTS[upstream_idx - 1]
                tag = f"@{upstream_name.lower()}:"
                for match in re.finditer(rf"{tag}\s+(\S+)", text):
                    ref = match.group(1).rstrip(",.;")
                    self.assertIn(ref, all_ids,
                                  f"{name}-01 references {ref} but no such upstream ID exists")

    def _gather_ids(self) -> set[str]:
        ids: set[str] = set()
        id_re = re.compile(r"\b([A-Z]+\.\d+\.\d+\.[a-f0-9]{4,8}|[A-Z]+-\d+)\b")
        for path in CHAIN.rglob("*"):
            if path.is_file():
                ids.update(id_re.findall(path.read_text(encoding="utf-8")))
        return ids
```

- [ ] **Step 3: Run**

Run: `cd framework && python3 -m unittest tests.acceptance.deterministic.test_fullpath -v`
Expected: 4 tests PASS.

- [ ] **Step 4: Commit**

```bash
git -C framework add tests/acceptance/fixtures/fullpath/ tests/acceptance/deterministic/test_fullpath.py
git -C framework commit -m "test(acceptance): deterministic BRD→IPLAN fullpath chain"
```

## Task 5.1b: Broken-fullpath fixture (positive failure case)

**Files:**

- Create: `framework/tests/acceptance/fixtures/fullpath/broken_chain/` (mirrors `golden_chain/` layout)
- Modify: `framework/tests/acceptance/deterministic/test_fullpath.py`

**Why this task exists:** Task 5.1's `test_forward_tag_closure` asserts every
`@upstream:` reference resolves. Without a known-broken chain, the assertion is
never *proven* — a bug in the matcher would silently pass on every PR. Add a
chain with one deliberately-broken cumulative tag and assert the test catches it.

- [ ] **Step 1: Copy golden_chain → broken_chain and break one reference**

```bash
cp -R framework/tests/acceptance/fixtures/fullpath/golden_chain \
      framework/tests/acceptance/fixtures/fullpath/broken_chain
# Edit broken_chain/02_PRD/PRD-01*.md: change @brd: BRD.01.07.abcd to
# @brd: BRD.01.07.ZZZZ (non-existent hash).
```

- [ ] **Step 2: Add a negative test that asserts closure detector catches it**

Append to `test_fullpath.py`:

```python
BROKEN_CHAIN = FIXTURES_ROOT / "fullpath" / "broken_chain"


class FullpathBrokenChainTests(unittest.TestCase):
    """The closure assertion must fail loudly on a known-broken chain."""

    def test_forward_tag_closure_catches_dangling_reference(self):
        all_ids = self._gather_ids(BROKEN_CHAIN)
        offenders = []
        id_re = re.compile(r"@\w+:\s+([A-Z]+\.\d+\.\d+\.[a-f0-9]{4,8}|[A-Z]+-\d+)")
        for path in BROKEN_CHAIN.rglob("*"):
            if path.is_file():
                for match in id_re.finditer(path.read_text(encoding="utf-8")):
                    ref = match.group(1)
                    if ref not in all_ids:
                        offenders.append((str(path.relative_to(BROKEN_CHAIN)), ref))
        self.assertTrue(offenders, "broken_chain should contain at least one dangling reference")

    def _gather_ids(self, root: Path) -> set[str]:
        ids: set[str] = set()
        id_re = re.compile(r"\b([A-Z]+\.\d+\.\d+\.[a-f0-9]{4,8}|[A-Z]+-\d+)\b")
        for path in root.rglob("*"):
            if path.is_file():
                ids.update(id_re.findall(path.read_text(encoding="utf-8")))
        return ids
```

- [ ] **Step 3: Run**

Run: `cd framework && python3 -m unittest tests.acceptance.deterministic.test_fullpath.FullpathBrokenChainTests -v`
Expected: PASS (the test asserts offenders is non-empty).

- [ ] **Step 4: Commit**

```bash
git -C framework add tests/acceptance/fixtures/fullpath/broken_chain/ tests/acceptance/deterministic/test_fullpath.py
git -C framework commit -m "test(acceptance): broken fullpath fixture proves closure detector"
```

## Task 5.2: Live full-path autopilot

**Files:**

- Create: `framework/tests/acceptance/live/test_fullpath_live.py`

- [ ] **Step 1: Write the test**

```python
"""Live acceptance: invoke each layer's autopilot in sequence."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import run_lint, template_sections, headings
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import skipUnlessLive, invoke_skill

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import ARTIFACTS


SEED = "Build a URL shortener: shorten, redirect, count clicks. Target: 1M URLs/day."


@skipUnlessLive
class FullpathLiveTests(unittest.TestCase):

    def test_full_chain_from_seed_produces_all_8_layers(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            (ws / "seed").mkdir()
            (ws / "seed" / "initial-requirements.md").write_text(SEED, encoding="utf-8")

            # Run BRD-autopilot, then each downstream autopilot.
            invoke_skill(
                "/aidoc-flow:doc-brd-autopilot from seed/initial-requirements.md write BRD-01",
                cwd=ws, timeout=480,
            )
            for layer in ["prd", "ears", "bdd", "adr", "spec", "tdd", "iplan"]:
                invoke_skill(f"/aidoc-flow:doc-{layer}-autopilot continue the chain",
                             cwd=ws, timeout=480)

            for idx, name in enumerate(ARTIFACTS, start=1):
                with self.subTest(layer=name):
                    folder = ws / "docs" / f"{idx:02d}_{name}"
                    hits = list(folder.rglob(f"{name}-01*"))
                    self.assertTrue(hits, f"{folder}: no artifact emitted")

            rc, output = run_lint(ws / "docs")
            self.assertEqual(rc, 0, f"live fullpath lint failed:\n{output}")
```

- [ ] **Step 2: Run (opt-in, expensive)**

Run: `LIVE=1 cd framework && python3 -m unittest tests.acceptance.live.test_fullpath_live -v`
Expected: 1 test PASS, ~15-30 min, several hundred K tokens.

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/acceptance/live/test_fullpath_live.py
git -C framework commit -m "test(acceptance,live): full-chain autopilot from seed prompt"
```

## Task 5.3: Full-path runner script

**Files:**

- Create: `scripts/test-fullpath.sh` (parent)

- [ ] **Step 1: Write**

```bash
#!/usr/bin/env bash
# scripts/test-fullpath.sh — deterministic + optional live full-path acceptance
set -uo pipefail

LIVE_FLAG=0
for arg in "$@"; do
  case "$arg" in
    --live) LIVE_FLAG=1 ;;
    -h|--help) echo "Usage: $0 [--live]"; exit 0 ;;
    *) echo "unknown flag: $arg"; exit 2 ;;
  esac
done

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO/framework"

python3 -m unittest tests.acceptance.deterministic.test_fullpath -v
if [[ $LIVE_FLAG -eq 1 ]]; then
  LIVE=1 python3 -m unittest tests.acceptance.live.test_fullpath_live -v
fi
```

- [ ] **Step 2: Smoke-test deterministic**

```bash
chmod +x scripts/test-fullpath.sh
bash scripts/test-fullpath.sh
```

Expected: 4 deterministic tests PASS.

- [ ] **Step 3: Commit**

```bash
git add scripts/test-fullpath.sh
git commit -m "test: scripts/test-fullpath.sh — full-path runner"
```

---

## Phase 6 — Tier 5: Packaging Integrity

## Task 6.1: Bundle byte-identity test

**Files:**

- Create: `framework/tests/packaging/test_bundle_integrity.py`

- [ ] **Step 1: Write the test**

```python
"""Packaging: every file under bundle/framework/ matches its sibling under framework/.

Bundle scope (which files get copied) is derived from `tools/sync-plugin-framework.sh`
so the test and the sync script have a single source of truth. If the sync script
changes its include/exclude rules, this test follows automatically.
"""

import hashlib
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import FRAMEWORK, plugin_bundle_root


def hash_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def parse_sync_excludes() -> set[str]:
    """Parse `tools/sync-plugin-framework.sh` and return top-level dir names it excludes.

    Looks for rsync `--exclude=PATTERN` lines and the common `find ... -prune` patterns.
    Returns just the top-level directory names (parts) the sync script omits.
    """
    sync = FRAMEWORK / "tools" / "sync-plugin-framework.sh"
    if not sync.exists():
        # Fallback if sync script absent — use the historical defaults.
        return {"tests", "platforms", "tools", "plans"}
    text = sync.read_text(encoding="utf-8")
    excludes: set[str] = set()
    for match in re.finditer(r"--exclude[= ]['\"]?([^'\" \\]+)", text):
        excludes.add(match.group(1).split("/")[0])
    return excludes or {"tests", "platforms", "tools", "plans"}


class BundleIntegrityTests(unittest.TestCase):

    def test_bundle_framework_subtree_matches_source(self):
        bundle_fw = plugin_bundle_root() / "framework"
        excludes = parse_sync_excludes()
        for src in FRAMEWORK.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(FRAMEWORK)
            if any(part in excludes for part in rel.parts):
                continue  # excluded by sync script
            mirror = bundle_fw / rel
            self.assertTrue(mirror.exists(), f"bundle missing {rel}")
            self.assertEqual(hash_file(src), hash_file(mirror),
                             f"bundle drift: {rel}")

    def test_parse_sync_excludes_finds_at_least_the_known_excludes(self):
        # Sanity: the parser must find SOMETHING; an empty set means parsing broke.
        excludes = parse_sync_excludes()
        self.assertTrue(excludes, "parse_sync_excludes returned empty — parser broken")
```

- [ ] **Step 2: Run**

Run: `cd framework && python3 -m unittest tests.packaging.test_bundle_integrity -v`
Expected: 1 test PASS.

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/packaging/test_bundle_integrity.py
git -C framework commit -m "test(packaging): bundle/framework matches source byte-for-byte"
```

## Task 6.2: VERSION gate

**Files:**

- Create: `framework/tests/packaging/test_version_gate.py`

- [ ] **Step 1: Write the test**

```python
"""Packaging: VERSION and FRAMEWORK_SPEC_VERSION are aligned across the bundle."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import FRAMEWORK, plugin_bundle_root


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


class VersionGateTests(unittest.TestCase):

    def test_framework_version_is_semver(self):
        v = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(v, SEMVER_RE)

    def test_bundle_version_matches_framework_version(self):
        a = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        b = (plugin_bundle_root() / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(a, b)

    def test_framework_spec_version_files_match_version(self):
        v = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        for candidate in [
            FRAMEWORK / "FRAMEWORK_SPEC_VERSION",
            plugin_bundle_root() / "FRAMEWORK_SPEC_VERSION",
        ]:
            if candidate.exists():
                self.assertEqual(candidate.read_text(encoding="utf-8").strip(), v,
                                 f"{candidate} mismatch with VERSION")
```

- [ ] **Step 2: Run**

Run: `cd framework && python3 -m unittest tests.packaging.test_version_gate -v`
Expected: 3 tests PASS.

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/packaging/test_version_gate.py
git -C framework commit -m "test(packaging): VERSION + FRAMEWORK_SPEC_VERSION gate"
```

## Task 6.3: Skill framework_spec_version cross-check (already covered by `tests/unit/test_skill_manifests.py`)

No new task — verified that the unit test from Task 2.1 enforces this. Document the cross-reference here for traceability.

---

## Phase 6.5 — Tier 3b: Non-Layer Skill Coverage

The plan's Phase 3/4 cover the 8 `doc-<layer>` families plus their audits/fixers/autopilots.
The plugin also bundles cross-cutting skills not tied to a single layer. These need their
own tests because their failure modes don't map to "did layer N artifact pass validation?"

| Skill | Role | What to test |
|---|---|---|
| `doc-flow` | Cross-corpus orchestrator | Position table, dual-axis reporting (status vs template-conformance), anti-confabulation |
| `doc-validator` | Corpus traceability validator | Detects broken `@upstream:` tags, missing artifacts |
| `charts-flow` | Diagram contract enforcer | Emits required `@diagram:` tags per layer |
| `doc-ref` | Free-format references | Exempts BRD-REF docs from ready-scores/gates |
| `project-init` | Workspace scaffolder | Creates expected directory tree, profile placeholder |

## Task 6.5.1: Live doc-flow probe

**Files:**

- Create: `framework/tests/acceptance/live/test_doc_flow_live.py`

- [ ] **Step 1: Write the test**

```python
"""Live acceptance: doc-flow surfaces dual-axis status and refuses confabulation."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
from _live_harness import skipUnlessLive, invoke_skill

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import fixtures_for


BANNED_PHRASES = [
    "compact 10-section", "documented walkthrough",
    "pinned to lint", "enterprise template", "10-section markdown variant",
]


@skipUnlessLive
class DocFlowProbeTests(unittest.TestCase):
    def test_doc_flow_reports_dual_axis_and_no_confabulation(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            # Stage the BRD golden so doc-flow has something to scan.
            src = fixtures_for(1, "valid")
            (ws / "docs" / "01_BRD").mkdir(parents=True)
            for item in src.iterdir():
                if item.is_file():
                    (ws / "docs" / "01_BRD" / item.name).write_bytes(item.read_bytes())

            output = invoke_skill(
                "/aidoc-flow:doc-flow scan and report position plus template-conformance drift",
                cwd=ws, timeout=420,
            )
            lc = output.lower()
            for phrase in BANNED_PHRASES:
                self.assertNotIn(phrase, lc, f"doc-flow used banned phrase: {phrase}")
            # Dual-axis reporting must mention both progress and template-conformance.
            self.assertRegex(output, r"(?i)progress.*\d+/\d+",
                             "doc-flow output missing progress fraction")
            self.assertRegex(output, r"(?i)template[- ]conformance",
                             "doc-flow output missing template-conformance axis")
```

- [ ] **Step 2: Run + commit**

```bash
LIVE=1 cd framework && python3 -m unittest tests.acceptance.live.test_doc_flow_live -v
git -C framework add tests/acceptance/live/test_doc_flow_live.py
git -C framework commit -m "test(acceptance,live): doc-flow dual-axis + anti-confabulation"
```

## Task 6.5.2: doc-validator probe (deterministic — runs against broken fullpath)

**Files:**

- Create: `framework/tests/acceptance/deterministic/test_doc_validator.py`

- [ ] **Step 1: Write the test**

```python
"""Deterministic acceptance: doc-validator flags broken_chain references.

doc-validator is a quality gate, not a generator. It reads existing artifacts and
reports broken `@upstream:` references. Run it against the broken_chain fixture
and assert it surfaces the deliberately-dangling references.
"""

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import FIXTURES_ROOT
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import plugin_bundle_root


# doc-validator is a Markdown SKILL.md plus deterministic helpers. The test
# exercises the helpers directly (no LLM call) by invoking sdd_doc_lint with
# the validator's CSC01 (cumulative-tag cascade) check enabled.


class DocValidatorTests(unittest.TestCase):
    def test_csc01_fires_on_broken_chain(self):
        broken = FIXTURES_ROOT / "fullpath" / "broken_chain"
        result = subprocess.run(
            [sys.executable, "-m", "sdd_doc_lint", str(broken), "--format=json"],
            env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
            capture_output=True, text=True, check=False,
        )
        import json
        findings = json.loads(result.stdout or "[]")
        codes = {f["code"] for f in findings}
        self.assertIn("CSC01", codes,
                      f"doc-validator's CSC01 missed broken cascade in broken_chain. Got: {codes}")
```

- [ ] **Step 2: Run + commit**

```bash
cd framework && python3 -m unittest tests.acceptance.deterministic.test_doc_validator -v
git -C framework add tests/acceptance/deterministic/test_doc_validator.py
git -C framework commit -m "test(acceptance): doc-validator CSC01 catches broken cascade"
```

## Task 6.5.3: charts-flow + doc-ref + project-init (manifest checks only)

**Files:**

- Create: `framework/tests/unit/test_nonlayer_skills.py`

These three skills are exercised through their SKILL.md contracts (they're guidance
prompts, not generators with deterministic output). The test covers what is
deterministically verifiable: their SKILL.md frontmatter, layer references, and
declared file outputs.

- [ ] **Step 1: Write the test**

```python
"""Unit: non-layer skills (charts-flow, doc-ref, project-init) carry valid contracts."""

import re
import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root


SKILLS_DIR = plugin_bundle_root() / "skills"


def frontmatter(skill_dir: Path) -> dict:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return yaml.safe_load(match.group(1)) if match else {}


class NonLayerSkillContractTests(unittest.TestCase):

    NON_LAYER_SKILLS = ["charts-flow", "doc-ref", "project-init", "doc-flow", "doc-validator"]

    def test_each_non_layer_skill_exists(self):
        for name in self.NON_LAYER_SKILLS:
            with self.subTest(skill=name):
                self.assertTrue((SKILLS_DIR / name / "SKILL.md").exists(),
                                f"missing skill: {name}")

    def test_each_carries_skill_category(self):
        for name in self.NON_LAYER_SKILLS:
            with self.subTest(skill=name):
                fm = frontmatter(SKILLS_DIR / name)
                category = fm.get("metadata", {}).get("custom_fields", {}).get("skill_category")
                self.assertIsNotNone(category, f"{name}: missing skill_category")

    def test_charts_flow_references_diagram_levels(self):
        text = (SKILLS_DIR / "charts-flow" / "SKILL.md").read_text(encoding="utf-8")
        for level in ("c4-l1", "c4-l2", "c4-l3", "dfd-l1", "dfd-l2", "dfd-l3"):
            self.assertIn(level, text, f"charts-flow: missing @diagram reference for {level}")

    def test_project_init_describes_directory_scaffold(self):
        text = (SKILLS_DIR / "project-init" / "SKILL.md").read_text(encoding="utf-8")
        for marker in ("docs/01_BRD", "docs/02_PRD", "docs/08_IPLAN"):
            self.assertIn(marker, text, f"project-init: missing scaffold mention of {marker}")
```

- [ ] **Step 2: Run + commit**

```bash
cd framework && python3 -m unittest tests.unit.test_nonlayer_skills -v
git -C framework add tests/unit/test_nonlayer_skills.py
git -C framework commit -m "test(unit): non-layer skill contract tests"
```

---

## Phase 7 — Tier 6: Marketplace Release Gate

## Task 7.1: CHANGELOG-entry-for-version guard

**Files:**

- Create: `framework/tests/release/test_changelog_entry.py`

- [ ] **Step 1: Write the test**

```python
"""Release: CHANGELOG.md has an entry for the current VERSION."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import FRAMEWORK


class ChangelogEntryTests(unittest.TestCase):
    def test_changelog_has_entry_for_current_version(self):
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        changelog = (FRAMEWORK / "CHANGELOG.md").read_text(encoding="utf-8")
        pattern = rf"^## \[?{re.escape(version)}\]?"
        self.assertRegex(changelog, re.compile(pattern, re.MULTILINE),
                         f"CHANGELOG.md has no '## {version}' section")

    def test_no_unreleased_orphans(self):
        # An [Unreleased] block above the version block is fine, but a TODO-style
        # placeholder pattern is not.
        changelog = (FRAMEWORK / "CHANGELOG.md").read_text(encoding="utf-8")
        forbidden = ["TBD", "TODO:", "FILL IN"]
        for token in forbidden:
            self.assertNotIn(token, changelog, f"CHANGELOG contains {token!r}")
```

- [ ] **Step 2: Run and commit**

Run: `cd framework && python3 -m unittest tests.release.test_changelog_entry -v`
Expected: 2 tests PASS.

```bash
git -C framework add tests/release/test_changelog_entry.py
git -C framework commit -m "test(release): CHANGELOG entry for current VERSION"
```

## Task 7.2: Bundle-size cap

**Files:**

- Create: `framework/tests/release/test_bundle_size.py`
- Create: `framework/tests/release/limits.yaml`

- [ ] **Step 1: Write `limits.yaml`**

```yaml
# Tuneable marketplace gates. Edit here, not in tests.
bundle_max_bytes: 10485760   # 10 MiB
manifest_max_skill_count: 200
```

- [ ] **Step 2: Write the test**

```python
"""Release: bundle stays under marketplace size cap."""

import sys
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root


LIMITS = yaml.safe_load(
    (Path(__file__).resolve().parent / "limits.yaml").read_text(encoding="utf-8")
)


def bundle_size_bytes(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


class BundleSizeTests(unittest.TestCase):
    def test_bundle_under_cap(self):
        size = bundle_size_bytes(plugin_bundle_root())
        self.assertLessEqual(size, LIMITS["bundle_max_bytes"],
                             f"bundle {size} bytes exceeds cap {LIMITS['bundle_max_bytes']}")

    def test_skill_count_under_cap(self):
        n_skills = len([d for d in (plugin_bundle_root() / "skills").iterdir() if d.is_dir()])
        self.assertLessEqual(n_skills, LIMITS["manifest_max_skill_count"])
```

- [ ] **Step 3: Run and commit**

```bash
cd framework && python3 -m unittest tests.release.test_bundle_size -v
```

```bash
git -C framework add tests/release/limits.yaml tests/release/test_bundle_size.py
git -C framework commit -m "test(release): bundle-size and skill-count caps"
```

## Task 7.3: Marketplace gate aggregator

**Files:**

- Create: `framework/tests/release/test_marketplace_gate.py`

- [ ] **Step 1: Write the test**

```python
"""Release: aggregate gate — all release-time invariants in one suite."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root, skill_dirs


SCAN_ROOTS = [plugin_bundle_root() / "sdd_doc_lint"]


class NoNetworkEgressTests(unittest.TestCase):
    FORBIDDEN = [
        r"\bimport\s+requests\b",
        r"\bfrom\s+requests\b",
        r"\bimport\s+urllib\.request\b",
        r"\bimport\s+httpx\b",
        r"\bsocket\.socket\b",
    ]

    def test_no_network_imports_in_plugin_code(self):
        for root in SCAN_ROOTS:
            if not root.exists():
                continue
            for py in root.rglob("*.py"):
                text = py.read_text(encoding="utf-8")
                for pattern in self.FORBIDDEN:
                    self.assertNotRegex(text, pattern, f"{py}: forbidden network call ({pattern})")


class NoDangerousFlagDefaultsTests(unittest.TestCase):
    """No SKILL.md may include '--dangerously-skip-permissions' as a default."""

    ALLOWED_CONTAINERS = {"tests/", "scripts/test-plugin.sh"}

    def test_no_skip_permissions_default_in_skills(self):
        for skill in skill_dirs():
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("--dangerously-skip-permissions", text,
                             f"{skill.name}: SKILL.md must not advertise --dangerously-skip-permissions")


class ManifestSchemaTests(unittest.TestCase):
    def test_plugin_json_exists(self):
        self.assertTrue((plugin_bundle_root() / ".claude-plugin" / "plugin.json").exists())
```

- [ ] **Step 2: Run and commit**

```bash
cd framework && python3 -m unittest tests.release.test_marketplace_gate -v
```

```bash
git -C framework add tests/release/test_marketplace_gate.py
git -C framework commit -m "test(release): marketplace gate — net, perms, manifest invariants"
```

---

## Phase 8 — Tier 7: Post-Deploy Smoke

## Task 8.0: Verify Anthropic CLI install + plugin-install commands

**Files:**

- Create: `framework/tests/smoke/COMMANDS.md` (documents verified commands)

**Why this task exists:** The current draft of Task 8.1 uses
`claude plugin install <url>` and `curl -fsSL https://claude.ai/install.sh | bash`
as guesses. Both must be verified against current Anthropic documentation before
any workflow that depends on them is written. If the actual commands differ, the
post-deploy workflow and smoke test break on first run.

- [ ] **Step 1: Verify Claude Code CLI install path**

Use the `context7` MCP server (preferred) or web fetch official Anthropic docs:

```text
# Suggested official methods (verify which is current):
# - npm:    npm install -g @anthropic-ai/claude-code
# - brew:   brew install anthropic/claude/claude
# - direct: see https://docs.anthropic.com/claude-code/install
```

Record the canonical method in `tests/smoke/COMMANDS.md` with a date + URL stamp.

- [ ] **Step 2: Verify plugin install / marketplace command**

The marketplace install command in Claude Code is via the `/plugin` slash command
or `claude` CLI subcommands. Verify the exact syntax:

```text
# Candidates to verify:
# - /plugin marketplace add <name-or-url>     (slash command, interactive only)
# - /plugin install <name>                    (slash command)
# - claude --plugin-dir <path>                (CLI flag — what test-plugin.sh uses today)
# - claude plugin add <url>                   (hypothetical CLI subcommand)
```

For the post-deploy smoke specifically: prefer the **`claude --plugin-dir <local-path>`**
form against a downloaded tarball. That works without needing a marketplace endpoint
or the slash-command UI.

- [ ] **Step 3: Document verified commands**

Write `tests/smoke/COMMANDS.md`:

```markdown
# Verified Anthropic CLI commands

> Source: <official docs URL>
> Verified: YYYY-MM-DD

## Install Claude Code CLI
```

<verified command>
```

## Install plugin from a local bundle (deterministic — preferred for smoke)

```
claude --plugin-dir <path-to-bundle>
```

## Install plugin from marketplace (manual / not yet automatable)

```
<verified slash-command-or-CLI form, or note: not yet automatable>
```

```

- [ ] **Step 4: Commit**

```bash
git -C framework add tests/smoke/COMMANDS.md
git -C framework commit -m "test(smoke): COMMANDS.md verified install paths"
```

> **Downstream effect:** Tasks 8.1, 10.2, 10.4 must use the commands in COMMANDS.md.
> If marketplace install isn't programmatically available yet, the post-deploy smoke
> falls back to bundle-tarball install via `--plugin-dir`.

## Task 8.1: Install-from-marketplace harness

**Files:**

- Create: `framework/tests/smoke/install-from-marketplace.sh`
- Create: `framework/tests/smoke/test_post_deploy.py`

- [ ] **Step 1: Write the install helper**

```bash
#!/usr/bin/env bash
# tests/smoke/install-from-marketplace.sh
# Install the published plugin into a clean workspace dir for smoke testing.
set -uo pipefail

MARKETPLACE_URL="${MARKETPLACE_URL:-}"
WORKSPACE="${1:-}"
if [[ -z "$MARKETPLACE_URL" || -z "$WORKSPACE" ]]; then
  echo "Usage: MARKETPLACE_URL=<url> $0 <workspace-dir>" >&2
  exit 2
fi

mkdir -p "$WORKSPACE"
cd "$WORKSPACE"
claude plugin install "$MARKETPLACE_URL"
```

- [ ] **Step 2: Write the smoke test**

```python
"""Smoke: install plugin from marketplace URL and run the doc-flow probe."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MARKETPLACE_URL = os.environ.get("MARKETPLACE_URL")
HAS_CLAUDE = shutil.which("claude") is not None


@unittest.skipUnless(MARKETPLACE_URL and HAS_CLAUDE,
                     "MARKETPLACE_URL not set or claude CLI unavailable")
class PostDeploySmokeTests(unittest.TestCase):

    def test_install_and_invoke_doc_flow(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            installer = Path(__file__).resolve().parent / "install-from-marketplace.sh"
            r = subprocess.run(["bash", str(installer), str(ws)],
                               env={**os.environ}, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"install failed:\n{r.stderr}")

            # Run doc-flow against the bundled demo
            probe = subprocess.run(
                ["claude", "--dangerously-skip-permissions",
                 "-p", "/aidoc-flow:doc-flow scan and report status"],
                cwd=str(ws), capture_output=True, text=True, timeout=420,
            )
            self.assertEqual(probe.returncode, 0, f"doc-flow failed:\n{probe.stderr}")
            banned = ["compact 10-section", "documented walkthrough",
                      "pinned to lint", "enterprise template", "10-section markdown"]
            lc = probe.stdout.lower()
            for phrase in banned:
                self.assertNotIn(phrase, lc, f"post-deploy probe contains banned: {phrase}")
```

- [ ] **Step 3: Run (only post-deploy; CI provides MARKETPLACE_URL)**

Locally:

```bash
MARKETPLACE_URL=https://example.com/aidoc-flow.zip \
  cd framework && python3 -m unittest tests.smoke.test_post_deploy -v
```

Expected: PASS once the plugin is published; otherwise SKIP.

- [ ] **Step 4: Commit**

```bash
git -C framework add tests/smoke/install-from-marketplace.sh tests/smoke/test_post_deploy.py
chmod +x framework/tests/smoke/install-from-marketplace.sh
git -C framework commit -m "test(smoke): post-deploy install + probe + confab guard"
```

---

## Phase 9 — Tier 8: Optional LLM Code Review

## Task 9.1: Code-review hook

**Files:**

- Create: `framework/tests/review/run-claude-review.sh`
- Create: `framework/tests/review/test_llm_code_review.py`

- [ ] **Step 1: Write the runner**

```bash
#!/usr/bin/env bash
# tests/review/run-claude-review.sh
# Invoke a Claude Code code-reviewer agent on the current diff.
#
# Passes the FULL diff (not --stat) so the reviewer has actual code to read.
# Caps the diff size to keep within Claude's effective context budget; if the
# diff exceeds the cap, the runner emits a structured warning and reviews only
# the first N changed files alphabetically.
set -uo pipefail
BASE="${BASE_REF:-origin/main}"
MAX_BYTES="${MAX_DIFF_BYTES:-262144}"   # 256 KiB default; tune via env

# Capture full unified diff (-U3 default context). Use ...HEAD to scope to commits
# on the current branch only.
FULL_DIFF="$(git diff "${BASE}"...HEAD 2>&1 || true)"
DIFF_BYTES=${#FULL_DIFF}

if (( DIFF_BYTES > MAX_BYTES )); then
  echo "::warning::diff is ${DIFF_BYTES} bytes (>${MAX_BYTES}); truncating to per-file head"
  # Per-file truncation: grab the first 8KB of each file's diff section.
  TRUNCATED=$(echo "$FULL_DIFF" | awk '
    /^diff --git/ { if (n>0) print "..."; n=0; print; next }
    { if (n<200) { print; n++ } }
  ')
  DIFF_FOR_REVIEW="$TRUNCATED"
else
  DIFF_FOR_REVIEW="$FULL_DIFF"
fi

PROMPT="$(cat <<EOF
Review the diff below for security, correctness, framework convention adherence,
and any silent failure / inadequate error handling patterns. The codebase is the
aidoc-flow SDD framework + Claude Code plugin.

Surface ONLY high-confidence findings. For each finding emit:
  SEVERITY: BLOCKER|CRITICAL|MAJOR|MINOR
  FILE: <path>:<line>
  FINDING: <one sentence>
  EVIDENCE: <quote the offending line(s)>

Stop after at most 12 findings. Prefer no findings over speculative ones.

--- DIFF ---
${DIFF_FOR_REVIEW}
EOF
)"
claude --dangerously-skip-permissions -p "$PROMPT"
```

- [ ] **Step 2: Write the test (opt-in via REVIEW=1)**

```python
"""Review: spawn an LLM code-reviewer agent on the current diff."""

import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REVIEW_ENABLED = os.environ.get("REVIEW") == "1"
HAS_CLAUDE = shutil.which("claude") is not None


@unittest.skipUnless(REVIEW_ENABLED and HAS_CLAUDE,
                     "review tier disabled (set REVIEW=1; claude CLI required)")
class LlmCodeReviewTests(unittest.TestCase):

    # Reviewer emits a structured SEVERITY: header per finding. We block on
    # BLOCKER and CRITICAL; MAJOR/MINOR are informational.
    BLOCKING_LINE_PATTERN = r"^SEVERITY:\s*(BLOCKER|CRITICAL)\b"

    def test_reviewer_emits_no_blocking_findings(self):
        runner = Path(__file__).resolve().parent / "run-claude-review.sh"
        r = subprocess.run(["bash", str(runner)], capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr)
        import re as _re
        offenders = _re.findall(self.BLOCKING_LINE_PATTERN, r.stdout, flags=_re.MULTILINE)
        self.assertFalse(
            offenders,
            f"LLM reviewer surfaced {len(offenders)} blocking findings:\n{r.stdout}",
        )
```

- [ ] **Step 3: Commit**

```bash
git -C framework add tests/review/
chmod +x framework/tests/review/run-claude-review.sh
git -C framework commit -m "test(review): opt-in LLM code-reviewer hook"
```

> The review tier is intentionally lenient: it asserts the reviewer doesn't surface *blocking* findings. Refine the BLOCKING_TOKENS list after a few real runs.

---

## Phase 10 — Tier 0: CI Wiring and Pre-Commit

## Task 10.1: Pre-commit hook tier

**Files:**

- Modify: `.pre-commit-config.yaml` (parent repo)

- [ ] **Step 1: Add the lightweight check**

Add to existing pre-commit config:

```yaml
  - repo: local
    hooks:
      - id: unit-fast
        name: aidoc-flow unit tests (fast tier)
        entry: bash -c 'cd framework && python3 -m unittest discover tests/unit -q'
        language: system
        pass_filenames: false
        stages: [pre-push]   # heavier — only on push, not every commit
```

- [ ] **Step 2: Verify locally**

```bash
pre-commit run --hook-stage pre-push --all-files
```

Expected: passes.

- [ ] **Step 3: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "ci(pre-commit): aidoc-flow unit tests on push"
```

## Task 10.2: GitHub Actions — PR gate

**Files:**

- Create: `.github/workflows/pr-checks.yml`

- [ ] **Step 1: Write workflow**

```yaml
name: PR Checks
on:
  pull_request:
    branches: [main]

jobs:
  deterministic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install deps
        run: pip install pyyaml jsonschema
      - name: Install claude CLI
        run: |
          curl -fsSL https://claude.ai/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH
      - name: Tier 1 — static (manifest)
        run: bash scripts/test-plugin.sh --no-live
      - name: Tier 2 — unit
        run: cd framework && python3 -m unittest discover tests/unit -v
      - name: Tier 3 — per-layer acceptance (deterministic)
        run: cd framework && python3 -m unittest discover tests/acceptance/deterministic -v
      - name: Tier 5 — packaging
        run: cd framework && python3 -m unittest discover tests/packaging -v
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/pr-checks.yml
git commit -m "ci: PR gate workflow (Tiers 1, 2, 3-det, 5)"
```

## Task 10.3: GitHub Actions — release gate

**Files:**

- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Write workflow**

```yaml
name: Release Gate
on:
  push:
    tags: ['v*']

jobs:
  release-gate:
    runs-on: ubuntu-latest
    env:
      LIVE: "1"
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install deps + claude CLI
        run: |
          pip install pyyaml jsonschema
          curl -fsSL https://claude.ai/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH
      - name: Full suite (deterministic + live + release)
        run: |
          bash scripts/test-plugin.sh
          cd framework
          python3 -m unittest discover tests/unit -v
          python3 -m unittest discover tests/acceptance -v
          python3 -m unittest discover tests/packaging -v
          python3 -m unittest discover tests/release -v
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: release gate (full deterministic + live + release tiers)"
```

## Task 10.4: GitHub Actions — nightly live + post-deploy

**Files:**

- Create: `.github/workflows/nightly-live.yml`
- Create: `.github/workflows/post-deploy.yml`

- [ ] **Step 1: Write `nightly-live.yml`**

```yaml
name: Nightly Live Tier
on:
  schedule:
    - cron: "0 7 * * *"   # 03:00 EST
  workflow_dispatch:

jobs:
  live:
    runs-on: ubuntu-latest
    env:
      LIVE: "1"
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: |
          pip install pyyaml
          curl -fsSL https://claude.ai/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH
      - run: cd framework && python3 -m unittest discover tests/acceptance/live -v
```

- [ ] **Step 2: Write `post-deploy.yml`**

```yaml
name: Post-Deploy Smoke
on:
  workflow_dispatch:
    inputs:
      marketplace_url:
        description: "Marketplace URL to install from"
        required: true

jobs:
  smoke:
    runs-on: ubuntu-latest
    env:
      MARKETPLACE_URL: ${{ inputs.marketplace_url }}
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    steps:
      - uses: actions/checkout@v4
        with: { submodules: recursive }
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: |
          curl -fsSL https://claude.ai/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH
      - run: cd framework && python3 -m unittest tests.smoke.test_post_deploy -v
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/nightly-live.yml .github/workflows/post-deploy.yml
git commit -m "ci: nightly live tier + post-deploy smoke workflows"
```

---

## Phase 11 — Test Harness Refactor

## Task 11.1: Extend `scripts/test-plugin.sh` with subcommands

**Files:**

- Modify: `scripts/test-plugin.sh`

- [ ] **Step 1: Add `--suite`, `--layer`, `--live`, `--review` flags**

Replace the current flag parsing with:

```bash
SUITE="default"     # default | unit | layer | fullpath | pre-deploy | smoke | review | all
LAYER=""
REVIEW=0

# Live-tier toggle. Preserve the pre-refactor default for `default` suite:
#   - In `default` (Phases 1-4) live is ON by default; pass --no-live to skip.
#     This is the prior behavior; do not regress it.
#   - In all other suites (unit/layer/fullpath/pre-deploy) live is OFF by default;
#     opt in with --live.
# `LIVE` carries the final value; `LIVE_DEFAULT` per-suite below resolves the start.
LIVE=""             # empty until parsed; set after we know the suite

# Two passes through args: first to learn the suite, then to apply --live / --no-live.
RAW_ARGS=("$@")
for arg in "${RAW_ARGS[@]}"; do
  case "$arg" in
    --suite=*) SUITE="${arg#*=}" ;;
  esac
done
case "$SUITE" in
  default)  LIVE=1 ;;                # legacy default — live ON
  *)        LIVE=0 ;;                # all newer suites — live OFF
esac

for arg in "${RAW_ARGS[@]}"; do
  case "$arg" in
    --suite=*)        : ;;            # handled above
    --layer=*)        LAYER="${arg#*=}" ;;
    --live)           LIVE=1 ;;
    --no-live)        LIVE=0 ;;
    --review)         REVIEW=1 ;;
    -h|--help)        sed -n '2,24p' "$0"; exit 0 ;;
    *) echo "unknown flag: $arg"; exit 2 ;;
  esac
done
```

Extract the existing inline Phase 1–4 logic into a function so the `default`
suite branch is a single call (and `pre-deploy` / `all` can also invoke it):

```bash
# Phases 1-4 — extracted from the original inline sections of test-plugin.sh
# (claude plugin validate; conformance discover; sdd_doc_lint; live doc-flow probe).
# Preserves the existing PHASE_RESULTS bookkeeping and BANNED-confabulation grep.
run_phase_1_to_4() {
  # ----- Phase 1: Static plugin validation -----
  section "Phase 1 — Static plugin validation"
  local PRE=$FAILED
  if ! command -v claude >/dev/null 2>&1; then
    echo "  WARN: 'claude' CLI not on PATH — skipping Phase 1"
    phase_record "Phase 1 — Static plugin validation" "SKIP"
  else
    run "claude plugin validate" \
        claude plugin validate "$PLUGIN_DIR" || true
    run "claude plugin validate --strict (R1)" \
        claude plugin validate "$PLUGIN_DIR" --strict || true
    phase_check "Phase 1 — Static plugin validation" "$PRE"
  fi

  # ----- Phase 2: Conformance suite -----
  section "Phase 2 — Framework conformance suite"
  PRE=$FAILED
  run "python -m unittest discover tests/conformance" \
      bash -c "cd '$FRAMEWORK/tests/conformance' && python3 -m unittest discover -q" || true
  phase_check "Phase 2 — Framework conformance suite" "$PRE"

  # ----- Phase 3: sdd_doc_lint smoke on the demo -----
  section "Phase 3 — sdd_doc_lint on demo example"
  PRE=$FAILED
  run "sdd_doc_lint $EXAMPLE_DOCS" \
      bash -c "PYTHONPATH='$PLUGIN_DIR' python3 -m sdd_doc_lint '$EXAMPLE_DOCS'" || true
  phase_check "Phase 3 — sdd_doc_lint on demo example" "$PRE"

  # ----- Phase 4: Live doc-flow probe -----
  section "Phase 4 — Live skill probe (claude -p /aidoc-flow:doc-flow)"
  PRE=$FAILED
  if (( LIVE == 0 )); then
    echo "  SKIPPED (pass --live to enable Phase 4)"
    phase_record "Phase 4 — Live skill probe" "SKIP"
    return
  fi
  if ! command -v claude >/dev/null 2>&1; then
    echo "  WARN: 'claude' CLI not on PATH — skipping Phase 4"
    phase_record "Phase 4 — Live skill probe" "SKIP"
    return
  fi
  local PROBE="$LOG_DIR/probe-doc-flow-${TS}.txt"
  ( cd "$EXAMPLE_DIR" && \
    claude --plugin-dir "$PLUGIN_DIR" \
           --dangerously-skip-permissions \
           -p "/aidoc-flow:doc-flow scan and report status" 2>&1
  ) | tee "$PROBE" | sed 's/^/  /'
  local rc=${PIPESTATUS[0]}
  (( rc != 0 )) && { echo "  FAIL: claude -p exited $rc"; FAILED+=1; }
  if grep -qiE "$BANNED" "$PROBE"; then
    echo "  FAIL: doc-flow output contains banned confabulation language"
    grep -niE "$BANNED" "$PROBE" | sed 's/^/    /'
    FAILED+=1
  fi
  phase_check "Phase 4 — Live skill probe" "$PRE"
}
```

And dispatch to suites:

```bash
case "$SUITE" in
  default)
    run_phase_1_to_4 ;;
  unit)
    cd "$FRAMEWORK" && python3 -m unittest discover tests/unit -v ;;
  layer)
    [[ -z "$LAYER" ]] && { echo "use --layer=<brd|prd|...>"; exit 2; }
    cd "$FRAMEWORK" && python3 -m unittest "tests.acceptance.deterministic.test_layer_${LAYER}" -v
    if (( LIVE == 1 )); then
      LIVE=1 python3 -m unittest "tests.acceptance.live.test_layer_${LAYER}_live" -v
    fi ;;
  fullpath)
    cd "$FRAMEWORK" && python3 -m unittest tests.acceptance.deterministic.test_fullpath -v
    if (( LIVE == 1 )); then
      LIVE=1 python3 -m unittest tests.acceptance.live.test_fullpath_live -v
    fi ;;
  pre-deploy)
    cd "$FRAMEWORK"
    python3 -m unittest discover tests/unit -v
    python3 -m unittest discover tests/acceptance/deterministic -v
    python3 -m unittest discover tests/packaging -v
    python3 -m unittest discover tests/release -v
    [[ $LIVE -eq 1 ]] && LIVE=1 python3 -m unittest discover tests/acceptance/live -v ;;
  smoke)
    cd "$FRAMEWORK" && python3 -m unittest discover tests/smoke -v ;;
  review)
    cd "$FRAMEWORK" && REVIEW=1 python3 -m unittest tests.review.test_llm_code_review -v ;;
  all)
    "$0" --suite=pre-deploy --live ;;
  *)
    echo "unknown suite: $SUITE"; exit 2 ;;
esac
```

- [ ] **Step 2: Smoke-test each subcommand**

```bash
bash scripts/test-plugin.sh --suite=unit
bash scripts/test-plugin.sh --suite=layer --layer=brd
bash scripts/test-plugin.sh --suite=fullpath
bash scripts/test-plugin.sh --suite=pre-deploy
```

Expected: all PASS deterministically.

- [ ] **Step 3: Commit**

```bash
git add scripts/test-plugin.sh
git commit -m "test: scripts/test-plugin.sh subcommands (--suite, --layer, --live, --review)"
```

## Task 11.2: Documentation

**Files:**

- Create: `framework/tests/README.md`

- [ ] **Step 1: Write a navigation README for the suite**

```markdown
# Framework Test Suite

Navigation hub for the tiered test suite. Start here, then drill into the
companion docs below.

## Companion documents

| Doc | When to read it |
|-----|-----------------|
| [SCENARIOS.md](SCENARIOS.md) | "What does the suite cover?" — catalog of every test case |
| [HOWTO.md](HOWTO.md) | "How do I run X?" — common commands + flags |
| [ENVIRONMENT.md](ENVIRONMENT.md) | "What do I need installed?" — prerequisites + secrets |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | "Why did this fail?" — common failures + fixes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | "How do I add a test?" — fixtures, lint codes, new skills |
| Per-tier READMEs | `unit/README.md`, `acceptance/README.md`, etc. — tier-specific detail |

## Tier overview

| Tier | Path | Runs on |
|------|------|---------|
| 1 — Static | (pre-commit) | every commit |
| 2 — Unit | `tests/unit/` | every PR |
| 3 — Per-layer (det) | `tests/acceptance/deterministic/test_layer_<x>.py` | every PR |
| 3 — Per-layer (live) | `tests/acceptance/live/test_layer_<x>_live.py` | nightly + release |
| 4 — Full-path (det) | `tests/acceptance/deterministic/test_fullpath.py` | every PR |
| 4 — Full-path (live) | `tests/acceptance/live/test_fullpath_live.py` | release + nightly |
| 5 — Packaging | `tests/packaging/` | every PR |
| 6 — Release gate | `tests/release/` | release tags only |
| 7 — Post-deploy | `tests/smoke/` | manual / after publish |
| 8 — LLM review | `tests/review/` | opt-in, REVIEW=1 |

## Quick reference

| Goal | Command |
|------|---------|
| Run everything deterministic | `bash scripts/test-plugin.sh --suite=pre-deploy` |
| Run one layer | `bash scripts/test-layer.sh brd` |
| Full BRD→IPLAN chain | `bash scripts/test-fullpath.sh` |
| Include LLM probes | append `--live` |
| Run LLM code review | `REVIEW=1 bash scripts/test-plugin.sh --suite=review` |

For the full quickstart matrix see [HOWTO.md](HOWTO.md). For per-test traceability
see [SCENARIOS.md](SCENARIOS.md).

## Conventions
- All tests use `unittest` for parity with the existing `tests/conformance/` suite.
- Live tests live under `tests/acceptance/live/` and skip unless `LIVE=1`.
- LLM-review tests live under `tests/review/` and skip unless `REVIEW=1`.
- Fixtures under `tests/acceptance/fixtures/` are committed; never generate on the fly.
- Adding a new test? See [CONTRIBUTING.md](CONTRIBUTING.md).
```

- [ ] **Step 2: Commit**

```bash
git -C framework add tests/README.md
git -C framework commit -m "docs(tests): navigation README for the tiered suite"
```

---

## Phase 11.5 — Suite Documentation (Best Practices)

The suite needs documentation beyond the navigation README. Industry references
(ISTQB Test Plan template, IEEE 829, common OSS test-suite patterns) expect:
test scenarios catalog, how-to-use guide, environment & prerequisites,
troubleshooting/FAQ, contributing guide, plus per-tier README files.

Each of the six tasks below produces one markdown file under `framework/tests/`.
Files are written in framework-style prose: terse, no superlatives, table-heavy.

## Task 11.5.1: Test Scenarios catalog (`SCENARIOS.md`)

**Files:**

- Create: `framework/tests/SCENARIOS.md`

The catalog enumerates every test case with: ID, tier, layer (if any), what it
proves, expected outcome, traceability to plan task and requirement. Engineers
adding a new test add a row here.

- [ ] **Step 1: Write the scaffold**

```markdown
# Test Scenarios Catalog

> Source of truth for what the suite covers. Add a row when you add a test;
> remove a row when you remove one. Reviewers cross-check this against the
> plan's acceptance criteria (PLUGIN-TEST-SUITE-PLAN.md §13).

## Conventions
- **ID:** `<tier>.<group>.<n>` (e.g. `T3.brd.01` for tier-3 BRD layer scenario 1).
- **Layer:** 1–8 if layer-scoped; "—" if cross-cutting.
- **Tier:** 1–8 per pyramid in the plan.
- **Proof:** one sentence on what the test demonstrates.
- **Plan task:** the implementation task that builds it.

## Tier 1 — Static
| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T1.01 | — | YAML templates parse and have required top keys | 1.1 |
| T1.02 | — | `claude plugin validate --strict` passes | 1.2 |
| T1.03 | — | sdd_doc_lint STRUCT01 fires on missing required section | 1.3 |
| T1.04 | — | sdd_doc_lint `--format=json` produces structured findings | 1.3 |

## Tier 2 — Unit
| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T2.01 | — | Every SKILL.md has required frontmatter | 2.1 |
| T2.02 | — | framework_spec_version matches bundle VERSION | 2.1 |
| T2.03 | — | Each lint code fires only on its target fixture | 2.2 |
| T2.04 | — | Sync scripts are idempotent | 2.3 |
| T2.05 | — | Non-layer skills (charts-flow, doc-ref, project-init, doc-flow, doc-validator) carry valid contracts | 6.5.3 |

## Tier 3 — Per-layer acceptance (deterministic)
| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T3.brd.01 | 1 | BRD golden passes lint | 3.2 |
| T3.brd.02 | 1 | BRD golden carries every required template section | 3.2 |
| T3.brd.03 | 1 | BRD broken fixture emits expected codes | 3.2 |
| T3.brd.04 | 1 | BRD has no upstream tags | 3.2 |
| T3.prd.01–04 | 2 | … (mirror of BRD, plus §10 Customer-Facing assertion) | 3.3 |
| T3.ears.01–04 | 3 | … (mirror, plus WHEN-THE-SHALL-WITHIN form assertion) | 3.4 |
| T3.bdd.01–04 | 4 | … (mirror, plus Given/When/Then assertion) | 3.5 |
| T3.adr.01–04 | 5 | … (mirror, plus Status enum assertion) | 3.6 |
| T3.spec.01–04 | 6 | … (mirror, YAML, C4-L3 boundary) | 3.7 |
| T3.tdd.01–04 | 7 | … (mirror, type attribute on every case) | 3.8 |
| T3.iplan.01–04 | 8 | … (mirror, tests-before-impl ordering) | 3.9 |

## Tier 3 — Per-layer acceptance (live)
| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T3L.brd.01 | 1 | doc-brd produces template-conformant BRD from seed | 4.2 |
| T3L.prd.01 | 2 | doc-prd produces template-conformant PRD from staged BRD | 4.3 |
| T3L.ears.01 | 3 | doc-ears emits WHEN-THE-SHALL-WITHIN requirements | 4.4 |
| T3L.bdd.01 | 4 | doc-bdd emits Given-When-Then scenarios | 4.5 |
| T3L.adr.01 | 5 | doc-adr emits decision with Status | 4.6 |
| T3L.spec.01 | 6 | doc-spec emits YAML C4-L3 component spec | 4.7 |
| T3L.tdd.01 | 7 | doc-tdd emits test cases mapped to BDD | 4.8 |
| T3L.iplan.01 | 8 | doc-iplan emits manifest with tests-first ordering | 4.9 |

## Tier 4 — Full-path acceptance
| ID | Layer | Proof | Plan task |
|----|:-:|---|----|
| T4.01 | 1-8 | Golden chain lint passes | 5.1 |
| T4.02 | 1-8 | Every layer has one artifact | 5.1 |
| T4.03 | 1-8 | Every layer has required sections | 5.1 |
| T4.04 | 1-8 | Forward-tag closure (every `@upstream:` resolves) | 5.1 |
| T4.05 | 1-8 | Broken-chain fixture catches dangling reference | 5.1b |
| T4L.01 | 1-8 | Live autopilot chain produces all 8 layers from seed | 5.2 |

## Tier 5 — Packaging
| ID | Proof | Plan task |
|----|---|----|
| T5.01 | Bundle byte-identity (scope derived from sync script) | 6.1 |
| T5.02 | VERSION + FRAMEWORK_SPEC_VERSION aligned | 6.2 |

## Tier 3b — Non-layer skill probes
| ID | Skill | Proof | Plan task |
|----|---|---|----|
| T3b.01 | doc-flow | Dual-axis (status + template-conformance) + anti-confab | 6.5.1 |
| T3b.02 | doc-validator | CSC01 catches broken cascade | 6.5.2 |

## Tier 6 — Release gate
| ID | Proof | Plan task |
|----|---|----|
| T6.01 | CHANGELOG entry for current VERSION | 7.1 |
| T6.02 | Bundle ≤ size cap, skill count ≤ cap | 7.2 |
| T6.03 | No network egress in plugin code | 7.3 |
| T6.04 | No `--dangerously-skip-permissions` defaults in SKILL.md | 7.3 |

## Tier 7 — Post-deploy smoke
| ID | Proof | Plan task |
|----|---|----|
| T7.01 | Install plugin + doc-flow probe + no confab phrases | 8.1 |

## Tier 8 — LLM code review (opt-in)
| ID | Proof | Plan task |
|----|---|----|
| T8.01 | Reviewer emits no `SEVERITY: BLOCKER\|CRITICAL` findings | 9.1 |
```

- [ ] **Step 2: Commit**

```bash
git -C framework add tests/SCENARIOS.md
git -C framework commit -m "docs(tests): SCENARIOS.md — full catalog of test cases by tier"
```

## Task 11.5.2: How-to-Use guide (`HOWTO.md`)

**Files:**

- Create: `framework/tests/HOWTO.md`

- [ ] **Step 1: Write the guide**

```markdown
# How to Use the Test Suite

> Quick paths for common workflows. For the strategy, see PLUGIN-TEST-SUITE-PLAN.md.
> For per-test detail, see SCENARIOS.md.

## Common workflows

### "Run everything deterministic before I push"
```bash
bash scripts/test-plugin.sh --suite=pre-deploy
```

Runs Tiers 1, 2, 3 (det), 4 (det), 5. Under 5 min on a laptop.

### "Run just one layer"

```bash
bash scripts/test-layer.sh brd          # or prd, ears, bdd, adr, spec, tdd, iplan
```

### "Run the full BRD → IPLAN chain"

```bash
bash scripts/test-fullpath.sh           # deterministic
bash scripts/test-fullpath.sh --live    # include live autopilot chain (expensive)
```

### "Include live LLM probes"

Append `--live` to any suite. Requires `claude` CLI on PATH and authenticated.

### "Run the LLM code reviewer on my diff"

```bash
REVIEW=1 bash scripts/test-plugin.sh --suite=review
```

### "Run the marketplace pre-deploy gate locally"

```bash
LIVE=1 bash scripts/test-plugin.sh --suite=pre-deploy --live
```

This is what `release.yml` runs in CI.

## Selecting a single test class

```bash
cd framework
python3 -m unittest tests.acceptance.deterministic.test_layer_brd.LayerBrdTests -v
```

## Re-running only failed tests (after a CI failure)

```bash
cd framework
python3 -m unittest tests.acceptance.deterministic.test_fullpath.FullpathChainTests.test_forward_tag_closure -v
```

## Environment variables

| Variable | Effect |
|----------|--------|
| `LIVE=1` | Enables live LLM tier (claude -p) |
| `REVIEW=1` | Enables LLM code-reviewer tier |
| `MARKETPLACE_URL` | Required for post-deploy smoke |
| `BASE_REF` | Base ref for LLM reviewer diff (default `origin/main`) |
| `MAX_DIFF_BYTES` | Cap on diff size piped to reviewer (default 262144) |

```

- [ ] **Step 2: Commit**

```bash
git -C framework add tests/HOWTO.md
git -C framework commit -m "docs(tests): HOWTO.md — common workflows + flags"
```

## Task 11.5.3: Environment & prerequisites (`ENVIRONMENT.md`)

**Files:**

- Create: `framework/tests/ENVIRONMENT.md`

- [ ] **Step 1: Write the doc**

```markdown
# Test Environment & Prerequisites

## Required tools

| Tool | Version | Used by |
|------|---------|---------|
| Python | ≥3.11 | All Python tests |
| bash | ≥5.0 | Harness scripts |
| git | ≥2.30 | All tests (paths, refs) |
| Claude Code CLI | latest | Tier 1 (validate), Tier 3-live, Tier 4-live, Tier 7 |
| Anthropic API key | active | Live tiers (env: ANTHROPIC_API_KEY) |

## Python dependencies

Pin file: `framework/tests/conformance/requirements.txt`

```text
pyyaml>=6.0
jsonschema>=4.20
```

Install:

```bash
pip install -r framework/tests/conformance/requirements.txt
```

## System dependencies

None beyond the tools above.

## Disk layout assumptions

- The framework repo is checked out as a git submodule under `aidoc-flow/framework/`.
- The plugin bundle lives at `framework/platforms/claude-code-plugin/`.
- Tests must be run from `framework/` (not parent `aidoc-flow/`).

## Network

- Tiers 1–6 (det) run fully offline.
- Tiers 3-live, 4-live, 8 require outbound HTTPS to api.anthropic.com.
- Tier 7 requires HTTPS to the marketplace URL.

## Secrets

- `ANTHROPIC_API_KEY`: must be set in the shell for live tiers; in GitHub Actions
  it's pulled from `secrets.ANTHROPIC_API_KEY`. Never committed.
- `MARKETPLACE_URL`: input to post-deploy workflow.

## Local-only setup

```bash
# Clone with submodules
git clone --recurse-submodules <repo>
cd aidoc-flow

# Install Python deps
pip install -r framework/tests/conformance/requirements.txt

# Install Claude Code CLI (see tests/smoke/COMMANDS.md for verified command)
# Verify
claude --version
```

```

- [ ] **Step 2: Commit**

```bash
git -C framework add tests/ENVIRONMENT.md
git -C framework commit -m "docs(tests): ENVIRONMENT.md — prerequisites + secrets"
```

## Task 11.5.4: Troubleshooting (`TROUBLESHOOTING.md`)

**Files:**

- Create: `framework/tests/TROUBLESHOOTING.md`

- [ ] **Step 1: Write the doc**

```markdown
# Troubleshooting

Common failures and resolutions.

## Tier 1: `claude plugin validate --strict` fails
- Check `framework/platforms/claude-code-plugin/.claude-plugin/plugin.json` parses
  as JSON and lists every directory present under the bundle.
- Run `claude plugin validate` (no `--strict`) to see baseline errors first.

## Tier 2: `test_skill_manifests.test_framework_spec_version_matches_bundle` fails
- A SKILL.md was added/changed without updating its `framework_spec_version`.
- Re-run Task 12.0 (`tools/bump-version.sh <new>`) to align everything.

## Tier 3: `test_layer_<x>.test_broken_fixture_emits_expected_codes` fails
- The new code mentioned in `<TYPE>-01_drift_codes.yaml` doesn't exist in sdd_doc_lint yet,
  or the fixture triggers a *different* code than expected.
- Run `python3 -m sdd_doc_lint <fixture-dir> --format=json` and inspect actual findings.
- Update either the lint check or the fixture (commit which).

## Tier 4: `test_forward_tag_closure` fails on a valid chain
- An upstream artifact was edited; downstream hashes are stale.
- Re-run the ID coordinator (Task 5.0 helper) for that layer; commit updated tags.

## Tier 3-live: `claude -p` times out
- Default per-test timeout is 420 s. Most layers complete in 60–180 s.
- A 420 s timeout usually means the model is in a long thinking/tool loop.
- Inspect `tmp/probe-*.txt` if the harness ran via `scripts/test-plugin.sh`.
- Retry once; if it times out a second time, the prompt may be ambiguous — refine.

## Tier 5: `test_bundle_framework_subtree_matches_source` reports drift
- The sync script wasn't re-run after editing source files.
- Run `bash framework/tools/sync-plugin-framework.sh` and commit.

## Tier 7: post-deploy smoke installs but doc-flow probe fails
- The published bundle is stale (older than current source).
- Re-publish from the latest release tag.
- If output contains banned confabulation phrases, the published bundle's
  doc-flow SKILL.md hasn't received the AS-series fixes — re-sync and re-publish.

## "Test passes locally but fails in CI"
- Check Python version: CI uses 3.11; some tests use type-hints unsupported on 3.10.
- Check that submodules are recursed: workflows must use `submodules: recursive`.
- Check that `ANTHROPIC_API_KEY` is set for live tiers (it's a secret, not on PRs from forks).
```

- [ ] **Step 2: Commit**

```bash
git -C framework add tests/TROUBLESHOOTING.md
git -C framework commit -m "docs(tests): TROUBLESHOOTING.md — common failures + fixes"
```

## Task 11.5.5: Contributing guide (`CONTRIBUTING.md`)

**Files:**

- Create: `framework/tests/CONTRIBUTING.md`

- [ ] **Step 1: Write the doc**

```markdown
# Contributing Tests

How to add tests to the suite without breaking conventions.

## Adding a new unit test
1. Choose the right module under `tests/unit/test_<thing>.py`.
2. Class: `<Verb><Noun>Tests(unittest.TestCase)`.
3. Method: `test_<verb>_<noun>_<condition>`.
4. Run `python3 -m unittest tests.unit.test_<thing> -v`.
5. Add a row to `SCENARIOS.md` (T2.NN).
6. Commit.

## Adding a new per-layer fixture (broken case)
1. Create `tests/acceptance/fixtures/layer_NN_<x>/broken/<TYPE>-01_<descriptor>.<ext>`.
2. Create `<TYPE>-01_drift_codes.yaml` listing the expected lint codes.
3. The harness (`_harness.assert_broken_fixture_emits_expected_codes`) picks it up.
4. Add a row to `SCENARIOS.md` under that layer.
5. Commit.

## Adding a new lint code
1. Implement the check in `framework/tools/sdd_doc_lint/__init__.py`.
2. Re-sync vendored copy: `bash framework/tools/sdd_doc_lint/sync-vendored.sh`.
3. Add a per-check fixture under `tests/unit/lint_fixtures/<CODE>/`.
4. Add the code + dir to `CASES` in `test_sdd_doc_lint_checks.py`.
5. Update `tests/SCENARIOS.md` (T1.NN).
6. Update `framework/governance/AUTHORING_STYLE.md` if user-visible.
7. Commit.

## Adding a new live test
1. Use `_live_harness.assert_live_layer_conformant` or write a custom @skipUnlessLive class.
2. Always set `timeout=` (default 420 s, raise only if necessary).
3. Add to `SCENARIOS.md` T3L.NN.
4. Update token budget table in `PLUGIN-TEST-SUITE-PLAN.md §15.1` if the new test
   meaningfully raises tier consumption.

## Adding a new SKILL.md
1. Add the skill directory under `framework/platforms/claude-code-plugin/skills/<NAME>/`.
2. Frontmatter must include: `name`, `description`, `metadata.custom_fields.{version,
   framework_spec_version, last_updated, skill_category}`.
3. `framework_spec_version` must match current `framework/VERSION`.
4. Tier 2 `test_skill_manifests.py` will validate; run it before commit.
5. If the skill is non-layer, add to `NON_LAYER_SKILLS` in `test_nonlayer_skills.py`.

## Adding a new governance file
1. Place under `framework/governance/<NAME>.md`.
2. Add `<NAME>.md` to `EXPECTED_FILES` in `tests/conformance/test_governance.py`.
3. The orphan-guard test added in Task 0.3 will fail the build otherwise.
4. Update `tests/SCENARIOS.md` if it introduces new lint or audit behavior.

## Style for test code
- `unittest` not `pytest` (parity with the existing 77 conformance tests).
- One assertion per `test_*` method when practical.
- Use `subTest()` for parametrized cases.
- No mocks of the LLM; deterministic tier uses frozen fixtures.
- Fixtures committed, never generated at test time.
- Test prose: same `AUTHORING_STYLE.md` rules that apply to docs apply to test prose.
```

- [ ] **Step 2: Commit**

```bash
git -C framework add tests/CONTRIBUTING.md
git -C framework commit -m "docs(tests): CONTRIBUTING.md — how to add tests, fixtures, lint codes"
```

## Task 11.5.6: Per-tier README files

**Files:**

- Create: `framework/tests/unit/README.md`
- Create: `framework/tests/acceptance/README.md`
- Create: `framework/tests/packaging/README.md`
- Create: `framework/tests/release/README.md`
- Create: `framework/tests/smoke/README.md`
- Create: `framework/tests/review/README.md`

Each per-tier README is ~20 lines and answers: what does this suite cover, when
does it run, how to invoke, what env vars / flags affect it.

- [ ] **Step 1: Write all six READMEs**

Template (engineer fills in the per-tier values):

```markdown
# <Tier name>

**Path:** `tests/<dir>/`
**Pyramid tier:** N (per PLUGIN-TEST-SUITE-PLAN.md §2)
**Runs:** every PR | nightly | release-only | manual | opt-in
**Determinism:** deterministic | live (LLM)

## What this suite covers
<2-3 sentences>

## Quickstart
```bash
cd framework && python3 -m unittest discover tests/<dir> -v
```

## Environment

- Required: <tools, env vars>
- Optional: <flags, knobs>

## See also

- Scenarios: `../SCENARIOS.md`
- How-to-use: `../HOWTO.md`
- Troubleshooting: `../TROUBLESHOOTING.md`

```

Per-tier specifics:
- **unit**: deterministic; runs every PR; no env needed; covers per-skill manifests, lint matrix, sync scripts.
- **acceptance**: deterministic + live; det runs every PR, live runs nightly/release; live needs `LIVE=1` + `ANTHROPIC_API_KEY`.
- **packaging**: deterministic; runs every PR; covers bundle integrity, VERSION gate.
- **release**: deterministic; runs only on release tags; covers CHANGELOG, bundle size, network egress, dangerous flags.
- **smoke**: post-deploy only; manual workflow_dispatch or post-publish webhook; needs `MARKETPLACE_URL`.
- **review**: opt-in; needs `REVIEW=1` + `ANTHROPIC_API_KEY`; LLM-based code review.

- [ ] **Step 2: Commit**

```bash
git -C framework add tests/unit/README.md tests/acceptance/README.md \
                    tests/packaging/README.md tests/release/README.md \
                    tests/smoke/README.md tests/review/README.md
git -C framework commit -m "docs(tests): per-tier README files"
```

---

## Phase 12 — Cross-Repo Submodule Bump

## Task 12.0: Full VERSION bump across framework and bundle

**Files:**

- Modify: `framework/VERSION`
- Modify: `framework/FRAMEWORK_SPEC_VERSION`
- Modify: `framework/platforms/claude-code-plugin/VERSION`
- Modify: `framework/platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION`
- Modify: every `framework/platforms/claude-code-plugin/skills/<NAME>/SKILL.md` (~50 files)
- Modify: `framework/CHANGELOG.md`

**Why this task exists:** GATE-SPEC requires `framework/VERSION` to bump on every
`framework/**` change. Across PRs #36, #37, #38 we manually walked: VERSION → both
FRAMEWORK_SPEC_VERSION files → all skills' `framework_spec_version` → re-sync bundle.
Missing any of these breaks the conformance test `test_skill_spec_version`. This
task makes the procedure explicit and tooled.

- [ ] **Step 1: Decide the new version**

The test-suite work is a minor (additive) bump. From 0.10.0 → 0.11.0.

- [ ] **Step 2: Write a portable bump helper**

Python helper (POSIX-portable; works on Linux and macOS without `sed -i` divergence).
Create `framework/tools/bump_version.py`:

```python
#!/usr/bin/env python3
"""Bump framework/VERSION + FRAMEWORK_SPEC_VERSION files + every skill's
framework_spec_version, then re-sync the bundle.

Usage:  python3 tools/bump_version.py <semver>

Portable across Linux / macOS (no `sed -i` divergence).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

FRAMEWORK = Path(__file__).resolve().parents[1]
BUNDLE = FRAMEWORK / "platforms" / "claude-code-plugin"

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SKILL_SPEC_RE = re.compile(
    r'^(?P<lead>\s+framework_spec_version:\s*")[^"]+(?P<trail>".*)$',
    re.MULTILINE,
)


def _die(msg: str, code: int = 2) -> None:
    print(f"bump_version: {msg}", file=sys.stderr)
    sys.exit(code)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not SEMVER.match(argv[1]):
        _die("Usage: bump_version.py <semver>")
    new = argv[1]

    old = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
    print(f"Bumping {old} → {new}")

    for path in [
        FRAMEWORK / "VERSION",
        FRAMEWORK / "FRAMEWORK_SPEC_VERSION",
        BUNDLE / "VERSION",
        BUNDLE / "FRAMEWORK_SPEC_VERSION",
    ]:
        if path.exists():
            path.write_text(new + "\n", encoding="utf-8")

    skills_root = BUNDLE / "skills"
    if not skills_root.exists():
        _die(f"plugin skills directory not found: {skills_root}", 1)
    updated = 0
    for skill_md in skills_root.glob("*/SKILL.md"):
        original = skill_md.read_text(encoding="utf-8")
        patched = SKILL_SPEC_RE.sub(rf"\g<lead>{new}\g<trail>", original)
        if patched != original:
            skill_md.write_text(patched, encoding="utf-8")
            updated += 1
    print(f"Updated {updated} skill manifest(s)")

    for sync in [
        FRAMEWORK / "tools" / "sync-plugin-framework.sh",
        FRAMEWORK / "tools" / "sdd_doc_lint" / "sync-vendored.sh",
    ]:
        if sync.exists():
            subprocess.run(["bash", str(sync)], check=True)

    # Final sanity: no skill should still reference the old version.
    stragglers = [
        p for p in skills_root.glob("*/SKILL.md")
        if f'framework_spec_version: "{old}"' in p.read_text(encoding="utf-8")
    ]
    if stragglers:
        _die(f"{len(stragglers)} skill(s) still reference {old}: "
             f"{[str(p.relative_to(FRAMEWORK)) for p in stragglers]}", 1)
    print(f"Bump complete: {old} → {new}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 3: Run the bump**

```bash
cd framework && python3 tools/bump_version.py 0.11.0
```

Expected: VERSION files updated, all skill `framework_spec_version` fields updated,
bundle re-synced, no skills left referencing `0.10.0`.

- [ ] **Step 4: Add a CHANGELOG entry**

Edit `framework/CHANGELOG.md`, add at the top:

```markdown
## [0.11.0] — YYYY-MM-DD

### Added
- Tiered test suite for the plugin (`tests/unit`, `tests/acceptance`,
  `tests/packaging`, `tests/release`, `tests/smoke`, `tests/review`).
- `STRUCT01` lint check (missing required template section).
- `sdd_doc_lint --format=json` structured output mode.
- Per-layer and full-path test runners (`scripts/test-layer.sh`, `scripts/test-fullpath.sh`).
- GitHub Actions: PR gate, release gate, nightly live tier, post-deploy smoke.
- Test-suite documentation (`tests/README.md`, `SCENARIOS.md`, `HOWTO.md`,
  `ENVIRONMENT.md`, `TROUBLESHOOTING.md`, `CONTRIBUTING.md`).
```

- [ ] **Step 5: Run the full conformance + packaging suite to verify the bump**

```bash
cd framework && python3 -m unittest tests.conformance tests.packaging -v
```

Expected: 77+ conformance tests pass; packaging tests confirm version alignment.

- [ ] **Step 6: Commit (surgical paths only)**

Add only the files touched by the bump, plus the helper. Avoid `git add platforms/`
wildcard to prevent inadvertently committing unrelated changes that may sit in the
bundle directory.

```bash
git -C framework add VERSION FRAMEWORK_SPEC_VERSION CHANGELOG.md \
                    platforms/claude-code-plugin/VERSION \
                    platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION \
                    platforms/claude-code-plugin/skills/ \
                    platforms/claude-code-plugin/framework/ \
                    platforms/claude-code-plugin/sdd_doc_lint/ \
                    tools/bump_version.py
git -C framework status                     # sanity check before commit
git -C framework commit -m "chore(release): bump framework spec 0.10.0 → 0.11.0"
```

## Task 12.1: Bump framework submodule in parent

- [ ] **Step 1: After all framework commits land, bump in parent**

```bash
cd /opt/data/aidoc-flow
git -C framework rev-parse HEAD                    # capture SHA
git add framework
git commit -m "chore: bump framework submodule to plugin-test-suite head"
```

- [ ] **Step 2: Push to remote**

```bash
git push origin <branch>
```

- [ ] **Step 3: Open PR for review.**

---

## Phase 13 — Final Holistic Code Review

After every task in Phases 0–12 has merged into the feature branch, a final review
pass over the *entire* changeset catches drift that incremental per-task reviews
miss: inconsistent helper APIs, unused fixtures, dead imports, gaps between docs
and tests, etc.

## Task 13.1: Dispatch the final code-reviewer subagent

Per `superpowers:subagent-driven-development`: "Dispatch final code reviewer subagent
for entire implementation."

- [ ] **Step 1: Gather the full diff manifest**

```bash
cd /opt/data/aidoc-flow
# Framework feature branch
git -C framework log --oneline main..HEAD > /tmp/framework-commits.txt
git -C framework diff main..HEAD --stat       > /tmp/framework-diffstat.txt
git -C framework diff main..HEAD             > /tmp/framework-fulldiff.patch
# Parent feature branch
git log --oneline main..HEAD > /tmp/parent-commits.txt
git diff main..HEAD --stat   > /tmp/parent-diffstat.txt
```

- [ ] **Step 2: Dispatch `code-reviewer` agent (Agent tool, subagent_type=code-reviewer)**

Brief:

```text
Review the complete plugin-test-suite branch:
  - Framework commits: see /tmp/framework-commits.txt (~30 commits)
  - Parent commits: see /tmp/parent-commits.txt (1 submodule bump)
  - Full diff: /tmp/framework-fulldiff.patch

Focus areas (in priority order):
  1. Inter-task API consistency: helpers like `fixtures_for`, `template_sections`,
     `headings`, `invoke_skill`, `extract_elements` are used across multiple test
     modules. Confirm signatures + return types match every call site.
  2. Fixture / code coupling: every `<TYPE>-01_drift_codes.yaml` references codes
     that actually exist in sdd_doc_lint (after Task 1.3). Every fixture file
     referenced from a test exists on disk.
  3. Bundle / source byte-identity: after Task 12.0, source ↔ bundle subtree
     diff must be empty (excluding sync-script-excluded paths). Spot-check.
  4. CI workflow correctness: the four workflows (PR, release, nightly, post-deploy)
     reference scripts and paths that actually exist. No undefined env vars.
  5. Documentation coherence: tests/SCENARIOS.md rows trace to actual test methods.
     tests/HOWTO.md commands actually work. Per-tier READMEs link consistently.
  6. Security: no secrets or API keys in any committed artifact. No
     `--dangerously-skip-permissions` defaults in any SKILL.md.
  7. Cross-platform portability: bump_version.py works on macOS; no GNU-isms in any
     committed bash script.

Report only HIGH-CONFIDENCE findings. Categorize as BLOCKER / CRITICAL / MAJOR / MINOR.
Cap at 20 findings.
```

- [ ] **Step 3: Triage findings**

- BLOCKER / CRITICAL findings → spawn a follow-up implementer subagent per finding;
  add a new commit to the branch with the fix; re-run the affected test tier.
- MAJOR findings → fix if scope allows; otherwise open a follow-up issue and reference
  it in PR description.
- MINOR findings → record in PR description as "known, deferred."

- [ ] **Step 4: Document the review in `PLUGIN-TEST-SUITE-REVIEW.md`** (one-time artifact)

```bash
cat > framework/plans/PLUGIN-TEST-SUITE-REVIEW.md <<'EOF'
# Plugin Test Suite — Final Review

Date: YYYY-MM-DD
Reviewer agent: code-reviewer
Diff scope: <framework commit range> / <parent commit range>

## Findings
<paste structured report>

## Disposition
- BLOCKER/CRITICAL fixed in commits: <list>
- MAJOR deferred to issues: <list>
- MINOR accepted: <list>
EOF
git -C framework add plans/PLUGIN-TEST-SUITE-REVIEW.md
git -C framework commit -m "docs(plan): record final code review findings + disposition"
```

- [ ] **Step 5: Mark plan complete in TodoWrite / TaskList**

All phase tasks complete; branch ready for `superpowers:finishing-a-development-branch`.

---

## 14 — Acceptance Criteria

The plan is "done" when:

1. **Every tier from Phase 0 through Phase 11 has tests in `framework/tests/`** and passes locally.
2. **`bash scripts/test-plugin.sh --suite=pre-deploy`** exits 0 in under 5 minutes (deterministic).
3. **`LIVE=1 bash scripts/test-plugin.sh --suite=pre-deploy --live`** exits 0 in under 60 minutes when the `claude` CLI is on PATH and authenticated.
4. **`bash scripts/test-layer.sh <any-layer>`** runs that layer's tests in isolation.
5. **`bash scripts/test-fullpath.sh`** runs the deterministic full-path tests.
6. **GitHub Actions PR workflow** runs Tiers 1, 2, 3-det, 5 and blocks merge on failure.
7. **GitHub Actions release workflow** runs all tiers including live and release on tag push.
8. **Pre-commit `pre-push` hook** runs the unit suite.
9. **`framework/tests/README.md`** documents every entry point.
10. **No banned phrases** in any committed test fixture; STY01 check passes on the new fixtures.
11. **No `--dangerously-skip-permissions` defaults** in any SKILL.md (release gate enforces).
12. **Bundle byte-identity** holds (Tier 5 enforces).
13. **`framework/VERSION` bumped** to 0.11.0 via `tools/bump-version.sh` (Task 12.0),
    with `FRAMEWORK_SPEC_VERSION` files updated **and** every skill's
    `framework_spec_version` aligned **and** the bundle re-synced.
14. **CHANGELOG entry** present for 0.11.0 (Task 12.0).
15. **`STRUCT01` lint code lands** (Task 1.3) and is used by every per-layer broken
    fixture whose `drift_codes.yaml` declares a missing-required-section assertion
    (i.e. those `BRD-01_missing_section.md` / equivalent fixtures specifically; other
    broken-fixture variants may target STY/FM/DG/HASH/CSC/STALE/TH codes instead).
16. **`sdd_doc_lint --format=json`** is shipped and consumed by Tier 2 + Tier 3 tests.
17. **`tests/SCENARIOS.md`** lists every test case with traceability to the plan task
    that built it (Task 11.5.1).
18. **`tests/HOWTO.md`, `ENVIRONMENT.md`, `TROUBLESHOOTING.md`, `CONTRIBUTING.md`**
    all present (Tasks 11.5.2–11.5.5) with per-tier READMEs under each suite
    (Task 11.5.6).
19. **`tests/smoke/COMMANDS.md`** records the verified Anthropic CLI install +
    plugin-install commands (Task 8.0).
20. **Token budget table** declared in §15.1 and enforced via per-test timeouts
    and CI hard caps.
21. **Broken-chain fullpath fixture** proves the closure detector catches dangling
    references (Task 5.1b).
22. **doc-flow + doc-validator + non-layer skills** carry coverage (Tasks 6.5.1–6.5.3).

---

## 15 — Risks and Mitigations

## 15.1 Token + duration budget

Live LLM tiers consume real tokens. Without a budget, a runaway autopilot loop
could rack up significant cost in a single CI run. Per-tier budgets:

| Tier | Per-test timeout | Per-tier token target | Hard cap |
|------|:--:|:--:|:--:|
| 3 (live per-layer) | 420 s | ~30 K tokens / layer | 50 K tokens / layer |
| 4 (live fullpath) | 1800 s | ~250 K tokens / run | 500 K tokens / run |
| 6 (LLM review) | 600 s | ~80 K tokens / run | 200 K tokens / run |
| 7 (post-deploy smoke) | 420 s | ~10 K tokens / run | 20 K tokens / run |

Implementation:

- Every live test uses `timeout=<N>` on `subprocess.run` for the `claude -p` call
  (already encoded in `_live_harness.invoke_skill(timeout=…)`).
- `_live_harness.invoke_skill` writes an entry to `tmp/token-ledger.json` per
  invocation. Until the Claude CLI surfaces structured token counts, the entries
  carry an **approximate** token count (≈ 4 chars/token); when the CLI gains
  structured counts the proxy is swapped without touching test code.
- A CI step at the end of `release.yml` and `nightly-live.yml` reads the ledger,
  sums per-tier totals, and fails the workflow if any tier exceeds its hard cap.

CI aggregator step (add to `release.yml`, `nightly-live.yml`):

```yaml
- name: Enforce token budget
  if: always()
  run: |
    python3 - <<'PY'
    import json, sys
    from pathlib import Path
    HARD = {"layer": 50_000, "fullpath": 500_000, "review": 200_000, "smoke": 20_000}
    ledger = json.loads(Path("tmp/token-ledger.json").read_text())
    tier_totals = {}
    for entry in ledger:
        tier = entry["test_id"].split(".")[0]   # e.g. "T3L.brd.01" → "T3L"
        tier_totals[tier] = tier_totals.get(tier, 0) + entry["approx_output_tokens"]
    print(tier_totals)
    breaches = [t for t, n in tier_totals.items() if n > HARD.get(t.lower(), 1e9)]
    if breaches:
        print(f"::error::token budget exceeded for tiers: {breaches}")
        sys.exit(1)
    PY
```

### Cost guidance

Approximate per-release-run live spend (at current Claude Opus pricing, ±50%):

| Tier | Approx tokens | Approx cost |
|------|:--:|:--:|
| 3-live (per-layer × 8) | ~240 K | ~$4-8 |
| 4-live (fullpath autopilot) | ~250 K | ~$4-8 |
| 6 (LLM review) | ~80 K | ~$1-3 |
| **Total per release** | **~570 K** | **~$9-19** |

Nightly live runs hit Tier 3+4 only (~$8-16/night). Set CI budget alarms accordingly.

## 15.2 Risk register

| Risk | Likelihood | Mitigation |
|------|:-:|------------|
| Live LLM tests flake on model drift | M | Assert *structural* properties (section presence, lint pass), not exact wording. Run nightly to catch drift early. |
| Token budget blowout on full chain live test | M | Per-tier budgets in §15.1; per-test timeout; hard cap enforced in CI. |
| Fixtures fall out of sync with templates | H | Tier 2 `test_template_yaml.py` catches template drift; per-layer `assert_template_sections_present_in_golden` catches fixture drift. |
| `claude plugin install` from marketplace flaky in CI | L-M | Post-deploy workflow is `workflow_dispatch` (manual trigger); retries built into the step. |
| Test suite slow → contributors skip | H | Pre-commit only runs unit (fast); per-layer + fullpath only on PR; live only nightly/release. |
| LLM reviewer surfaces blocking findings on benign diffs | M | Initial BLOCKING_TOKENS list is conservative; refine after first 5 real runs. |
| Sync-script idempotency drifts when templates change | M | Tier 2 `test_sync_scripts.py` runs the script and asserts no-op; runs every PR. |
| GHA secrets (ANTHROPIC_API_KEY) leak via verbose logs | L | Use GitHub's automatic secret masking; never log raw API responses. |
| Submodule SHA in parent drifts ahead of test code | L | Phase 12 task: parent bump is the LAST commit. |

---

## 16 — Anthropic / Marketplace Alignment Checklist

The release gate (Phase 7) enforces:

- [x] `claude plugin validate --strict` (Task 1.2)
- [x] Manifest schema correctness (Task 7.3 `ManifestSchemaTests`)
- [x] No network egress from plugin code (Task 7.3 `NoNetworkEgressTests`)
- [x] No `--dangerously-skip-permissions` defaults (Task 7.3 `NoDangerousFlagDefaultsTests`)
- [x] CHANGELOG entry per VERSION (Task 7.1 `test_changelog_entry.py`)
- [x] Bundle ≤ 10 MiB (Task 7.2 `test_bundle_size.py`)
- [x] Skill metadata complete (Task 2.1 `test_skill_manifests.py`)
- [x] Skill `framework_spec_version` matches bundle (Task 2.1 `test_skill_manifests.py`)
- [x] Bundle byte-identity, scope derived from sync script (Task 6.1 `test_bundle_integrity.py`)
- [x] Sync idempotency (Task 2.3 `test_sync_scripts.py`)
- [x] `detect-secrets` baseline current (existing pre-commit)
- [x] No banned phrases (`AUTHORING_STYLE.md` enforcement via STY01-03)
- [x] Missing required template sections caught deterministically (Task 1.3 `STRUCT01`)
- [x] Structured lint output for machine parsing (Task 1.3 `--format=json`)
- [x] Verified CLI install commands (Task 8.0 `COMMANDS.md`)
- [x] Token + duration budget enforced per tier (§15.1)
- [x] Broken cumulative-tag chain proves closure detector (Task 5.1b)
- [x] doc-flow, doc-validator, charts-flow, doc-ref, project-init tested (Phase 6.5)
- [x] Orphan governance files blocked (Task 0.3 `GovernanceFilesNoOrphans`)
- [x] Full suite documentation: SCENARIOS, HOWTO, ENVIRONMENT, TROUBLESHOOTING,
      CONTRIBUTING, per-tier READMEs (Phase 11.5)

---

## 17 — Self-Review Notes

After drafting:

- **Spec coverage** — every user requirement maps to at least one task:
  - "Unit tests" → Phase 2 (Tasks 2.1–2.3).
  - "Acceptance tests" → Phases 3, 4, 5.
  - "Marketplace pre-deployment" → Phases 5, 6, 7.
  - "Marketplace final test suite" → Phase 8.
  - "Each layer separately" → Task 3.10 (`scripts/test-layer.sh`).
  - "Whole path BRD to IPLAN" → Task 5.1, 5.3 (`scripts/test-fullpath.sh`).
  - "Best practices + Anthropic recommendations" → §5, §15.
  - "Review by Claude Code LLM" → Phase 9 (Task 9.1).
  - "Pre-commit hook" → Task 10.1.
  - "GitHub Actions" → Tasks 10.2, 10.3, 10.4.

- **Placeholder scan** — no TBD, no "implement later", every code block has full content. Per-layer Tasks 3.3–3.9 reference an explicit per-layer override table rather than "similar to 3.2" with no detail.

- **Type consistency** — `LAYER_INDEX`, `LAYER_NAME`, `fixtures_for(layer_index, kind)`, `template_sections(name)`, `run_lint(target)`, `headings(path)` are all used consistently across Phase 3, 4, 5 tests.

---

## Execution choice (after plan approval)

After plan approval, two execution paths:

1. **Subagent-driven** (recommended) — dispatch a fresh subagent per task, two-stage review between tasks.
2. **Inline** — execute tasks in this session using `superpowers:executing-plans`, batch checkpoints for review.

Which approach to proceed with?
