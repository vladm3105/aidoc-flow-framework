# Contributing Tests

How to add tests to the suite.

## Adding a new unit test

1. Choose the right module under `tests/unit/test_<thing>.py`.
2. Class: `<Verb><Noun>Tests(unittest.TestCase)`.
3. Method: `test_<verb>_<noun>_<condition>`.
4. Run `python3 -m unittest tests.unit.test_<thing> -v`.
5. Add a row to `SCENARIOS.md` (T2.NN).
6. Commit.

## Adding a new per-layer fixture (broken case)

1. Create `tests/acceptance/fixtures/layer_NN_<x>/broken/<TYPE>-01_<descriptor>.<ext>`.
2. Create `<TYPE>-01_drift_codes.yaml` declaring expected lint codes.
3. Harness picks it up automatically.
4. Add a row to `SCENARIOS.md` under that layer.
5. Commit.

## Adding a new lint code

1. Implement the check in `framework/tools/sdd_doc_lint/__init__.py`.
2. Re-sync (from framework/ submodule root): `bash tools/sdd_doc_lint/sync-vendored.sh`.
3. Add a fixture under `tests/unit/lint_fixtures/<CODE>/`.
4. Add to CASES in `test_sdd_doc_lint_checks.py`.
5. Update `SCENARIOS.md` (T1.NN).
6. Update `framework/governance/AUTHORING_STYLE.md` if user-visible.
7. Commit.

## Adding a new live test

1. Use `_live_harness.assert_live_layer_conformant` or write a custom @skipUnlessLive class.
2. Always set `timeout=` (default 420 s).
3. Add to `SCENARIOS.md` T3L.NN.
4. Update token budget in `plans/PLUGIN-TEST-SUITE-PLAN.md §15.1` if needed.

## Adding a new SKILL.md

1. Add under `framework/platforms/claude-code-plugin/skills/<NAME>/`.
2. Frontmatter must include: `name`, `description`, and `metadata.custom_fields.{version, framework_spec_version, last_updated, skill_category}`.
3. `framework_spec_version` must match current `framework/VERSION`.
4. Tier 2 `test_skill_manifests.py` validates; run it before commit.
5. If non-layer, add to `NON_LAYER_SKILLS` in `test_nonlayer_skills.py`.

## Adding a new governance file

1. Place under `framework/governance/<NAME>.md`.
2. Add `<NAME>.md` to `EXPECTED_FILES` in `tests/conformance/test_governance.py`.
3. Tier 2 orphan-guard otherwise fails.

## Style for test code

- `unittest`, not `pytest` (parity with existing 77 conformance tests).
- One assertion per `test_*` when practical.
- Use `subTest()` for parametrized cases.
- No LLM mocks; deterministic tier uses frozen fixtures.
- Fixtures committed, never generated at test time.
