# Troubleshooting

Common failures and resolutions.

## Tier 1: `claude plugin validate --strict` fails

- Check `framework/platforms/claude-code-plugin/.claude-plugin/plugin.json`.
- Run `claude plugin validate` (no `--strict`) to see baseline errors.

## Tier 2: `test_skill_manifests.test_framework_spec_version_matches_bundle` fails

- A SKILL.md was added/changed without bumping `framework_spec_version`.
- Re-run Task 12.0 (`tools/bump_version.py <new>`) to align.

## Tier 3: `test_layer_<x>.test_broken_fixture_emits_expected_codes` fails

- The expected code in `<TYPE>-01_drift_codes.yaml` doesn't fire, OR
- The fixture triggers a different code than expected.
- Run `python3 -m sdd_doc_lint <fixture-dir> --format=json` and inspect.
- Update either the lint check or the fixture (commit which).

## Tier 4: `test_forward_tag_closure` fails

- An upstream artifact was edited; downstream hashes stale.
- Re-run the ID coordinator (Task 5.0 helper) for that layer; commit updated tags.

## Tier 3-live: `claude -p` times out

- Default per-test timeout is 420 s. Most layers complete in 60–180 s.
- A 420 s timeout usually means model in a long thinking loop.
- Inspect `tmp/probe-*.txt` if run via `scripts/test-plugin.sh`.
- Retry once; if it times out again, refine the prompt.

## Tier 5: `test_bundle_framework_subtree_matches_source` reports drift

- The sync script wasn't re-run after editing source.
- Run `bash framework/tools/sync-plugin-framework.sh` and commit.

## Tier 7: doc-flow probe fails post-deploy

- Published bundle is stale.
- Re-publish from latest release tag.
- Banned confabulation phrases → published doc-flow SKILL.md is pre-AS-series.

## "Test passes locally but fails in CI"

- Check Python version: CI uses 3.11.
- Submodules must be recursed: `submodules: recursive` in workflow.
- `ANTHROPIC_API_KEY` is a secret; PRs from forks don't see it.

## Pre-commit hooks fail to install (anaconda libstdc++ conflict)

- Symptom: `nodejs: ... GLIBCXX_3.4.30 not found`.
- Workaround: run `env -u LD_LIBRARY_PATH git commit ...` to unset anaconda's
  LD_LIBRARY_PATH override.
