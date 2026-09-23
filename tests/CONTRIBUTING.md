# Contributing Tests

How to add tests to the suite.

## Adding a new unit test

1. Choose the right module under `tests/unit/test_<thing>.py`.
2. Class: `<Verb><Noun>Tests(unittest.TestCase)`.
3. Method: `test_<verb>_<noun>_<condition>`.
4. Run `python3 -m unittest tests.unit.test_<thing> -v` from the repo root.
5. Commit.

## Adding a new per-layer fixture (broken case)

1. Create `tests/acceptance/fixtures/layer_NN_<x>/broken/<TYPE>-01_<descriptor>.<ext>`.
2. Create `<TYPE>-01_drift_codes.yaml` declaring expected lint codes.
3. Harness picks it up automatically.
4. Commit.

## Adding a new lint code

1. Implement the check in `sdd_doc_lint/` (linter) and catalog it in
   `framework/governance/LINT_RULES.md` (codes-vs-catalog agreement is pinned
   by test).
2. Add fixtures + cases in `sdd_doc_lint/tests/test_<lint>.py`.
3. Update `framework/governance/AUTHORING_STYLE.md` if user-visible.
4. Commit.

## Adding a new governance file

1. Place under `framework/governance/<NAME>.md`.
2. Add `<NAME>.md` to `EXPECTED_FILES` in `tests/conformance/test_governance.py`.
3. The registry-coverage test otherwise fails.

## Style for test code

- `unittest`, not `pytest` (parity with the conformance suite).
- One assertion per `test_*` when practical.
- Use `subTest()` for parametrized cases.
- No LLM mocks; deterministic tier uses frozen fixtures.
- Fixtures committed, never generated at test time.
