# Plugin flow walkthrough — URL shortener (seed only)

This example currently carries **only the seed prompt**
([`seed/initial-requirements.md`](seed/initial-requirements.md)) — the input
to the 8-layer SDD flow.

The previous worked output chain (`docs/01_BRD/` through `docs/08_IPLAN/`)
was authored before the current `STRUCT01` lint and the v0.4.0 skill
consolidation; it has been cleared. The new demo chain will be authored
from a Claude Code session by driving the seed through every
`doc-{layer}-autopilot` skill against the current templates, then
committed under `docs/` once it passes both `sdd_doc_lint` and each
layer's `-audit` quality gate.

The test-suite live tier (`LIVE=1 bash scripts/test-plugin.sh
--suite=fullpath --live`) exercises the same end-to-end path for
**regression validation** — it asserts the autopilot skills can produce a
structurally-conformant chain — but its outputs are test-instrumented
(staged fixtures, per-layer assertions) and are **not** suitable as
production demo content. The demo lives under `examples/`; the live tier
runs in ephemeral test workspaces.

## How to drive the seed through the 8-layer flow yourself

From a Claude Code session with the plugin installed:

```text
/aidoc-flow:doc-brd-autopilot from examples/url-shortener/seed/initial-requirements.md
```

Then continue layer-by-layer with `doc-prd-autopilot`, `doc-ears-autopilot`,
…, `doc-iplan-autopilot`. Each layer gates with its `-audit` skill and the
deterministic structural validator (`sdd_doc_lint`).

## Re-run the deterministic gate (after you've authored a chain)

```bash
PYTHONPATH=platforms/claude-code-plugin python3 -m sdd_doc_lint examples/url-shortener/docs
# exit 0 = no error-level findings
```

## What this demonstrates (once regenerated)

- The full **8-layer chain** for one feature set (shorten a URL, redirect,
  count clicks — see scope in the seed file).
- **Cumulative traceability**: each downstream layer carries `@brd … @tdd`
  tags referencing real upstream element IDs (4-segment `TYPE.NN.SS.xxxx`).
- The **C4 + DFD + sequence diagram** model per layer
  (`framework/governance/DIAGRAM_STANDARDS.md`): BRD `c4-l1`/`dfd-l1`,
  PRD `c4-l2`/`dfd-l2`/`sequence`, ADR decision `sequence`,
  SPEC `c4-l3`/`dfd-l3`.

> The plugin has no runtime — its skills are LLM instructions — so the
> output chain is authored by following the skills, and the
> **deterministic gate** is `sdd_doc_lint`. The semantic readiness score
> (≥90) is the LLM `-audit` skill's judgment, noted per document and not
> machine-checked.
