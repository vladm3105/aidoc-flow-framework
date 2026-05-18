# Conformance Suite

The shared, runnable contract for the AI Doc Flow Framework. It defines what
it means to conform to the engine-agnostic spec in [`framework/`](../../framework/).

The suite has two halves:

1. **Framework self-consistency** (implemented here) — checks that the
   `framework/` spec is internally coherent: the registry agrees with itself
   and with the files on disk, layer templates match the registry, governance
   files are present, and no engine-specific tokens have leaked in.
2. **Platform conformance** (Phase 4) — checks that a *platform* implementation
   honours the spec. Not implemented yet; the contract is documented below.

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
| `test_governance.py` | the 18 governance + CHG files are present (and only those); `CHG-TEMPLATE.yaml` parses |
| `test_spec_hygiene.py` | no engine tokens (`hermes`, `ucx_`, `.claude/`, `mcp`, `mermaid-gen`, `charts-flow`, engine SDD verbs) and no stale version strings under `framework/` |

`_spec.py` is the shared helper (locates `framework/`, loads the registry); it
is not a test module.

## Platform-conformance contract (Phase 4)

A platform (Hermes, the Claude Code plugin) conforms to the framework when:

- it declares the `framework_spec_version` it implements (see `framework/VERSION`);
- every artifact it generates validates against the matching layer template in
  `framework/layers/` and the `id_patterns` in the registry;
- it enforces the traceability rules the registry encodes (`required_tags`,
  `can_reference`, `downstream`);
- it carries no expectation of the other platform's engine.

Phase 4 adds platform-specific test modules here that exercise this contract
against each platform's output. They are intentionally absent now — no platform
exists yet.
