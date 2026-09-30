# Troubleshooting

Common failures and resolutions. Plugin/harness-era entries were retired with
the platforms (CHG-08 #670); the live record is below.

## `test_layer_<x>.test_broken_fixture_emits_expected_codes` fails

- The expected code in `<TYPE>-01_drift_codes.yaml` doesn't fire, OR
- The fixture triggers a different code than expected.
- Run `python3 -m sdd_doc_lint <fixture-dir> --format=json` and inspect.
- Update either the lint check or the fixture (commit which).

## `test_forward_tag_closure` fails

- An upstream artifact was edited; downstream hashes stale.
- Re-run the ID coordinator (Task 5.0 helper) for that layer; commit updated tags.

## "Test passes locally but fails in CI"

- Check Python version: CI uses 3.12.
- No submodules: clone normally, install `tests/conformance/requirements.txt`.

## Pre-commit hooks fail to install (anaconda libstdc++ conflict)

- Symptom: `nodejs: ... GLIBCXX_3.4.30 not found`.
- Workaround: run `env -u LD_LIBRARY_PATH git commit ...` to unset anaconda's
  LD_LIBRARY_PATH override.
