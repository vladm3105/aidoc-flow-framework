# Conformance Suite

The shared, runnable contract for the AI Doc Flow Framework. It defines what
it means to conform to the engine-agnostic spec in [`framework/`](../../framework/).

The suite has two halves:

1. **Framework self-consistency** (implemented here) — checks that the
   `framework/` spec is internally coherent: the registry agrees with itself
   and with the files on disk, layer templates match the registry, governance
   files are present, and no engine-specific tokens have leaked in.
2. **Platform conformance** (`tests/conformance/platforms/`) — checks that a
   *platform* implementation honours the spec. **Implemented and running**: 16
   modules covering the Claude Code plugin (framework-bundle drift guard,
   `sdd_doc_lint` vendoring identity, version/spec-version declarations, plugin
   manifest + release metadata + config schema, autopilot saga parity, model
   precheck, engine isolation, adaptation surface, skill-template alignment).

## Running it

The suite uses only the Python 3.11+ standard library (`unittest`) plus
`PyYAML`. No `pytest` required.

```sh
pip install -r tests/conformance/requirements.txt   # PyYAML only
python3 -m unittest discover -s tests/conformance -v
```

Run from the repository root. The suite must pass green against the current
`framework/`; a failure means either the spec or the suite needs a fix — never
weaken a check to make it pass.

`unittest.TestCase` classes are also discoverable by `pytest` should a platform
prefer that runner.

## What is checked

| Module | Checks |
|--------|--------|
| `test_registry.py` | registry structure; 8 dense layers; required keys; `error_prefix` == `artifact`; `downstream` chain; cumulative `required_tags`; `can_reference` consistency; `folder`/`template` resolve; `layer_groups` partition; `c4_mapping` artifacts known; `id_patterns` compile |
| `test_layers.py` | each layer folder has template + README + index template; templates parse; `metadata.layer` matches the registry; `metadata.document_type` present |
| `test_governance.py` | the governance + CHG files listed in `EXPECTED_FILES` are present (and only those — any new `framework/governance/` file must be registered); `CHG-TEMPLATE.yaml` parses |
| `test_version.py` | `framework/VERSION` is present and a bare `X.Y.Z` SemVer string |
| `test_spec_hygiene.py` | no engine tokens (`hermes`, `ucx_`, `.claude/`, `mcp`, `mermaid-gen`, `charts-flow`, engine SDD verbs) and no stale version strings under `framework/` |

`_spec.py` is the shared helper (locates `framework/`, loads the registry); it
is not a test module.

## Platform-conformance contract

A platform (Hermes, the Claude Code plugin) conforms to the framework when:

- it declares the `framework_spec_version` it implements (see `framework/VERSION`);
- every artifact it generates validates against the matching layer template in
  `framework/layers/` and the `id_patterns` in the registry;
- it enforces the traceability rules the registry encodes (`required_tags`,
  `can_reference`, `downstream`);
- it carries no expectation of the other platform's engine.

The `tests/conformance/platforms/` modules exercise this contract against the
Claude Code plugin (see the second suite half above). The plugin ships a
byte-identical vendored copy of the spec subtrees it consumes (D-0022); a drift
guard fails CI if the bundle and the canonical spec diverge.
