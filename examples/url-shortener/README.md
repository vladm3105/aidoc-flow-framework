# Plugin flow walkthrough — URL shortener

A committed, end-to-end example of the **Claude Code plugin** driving a single
requirement through all **8 SDD layers** (BRD → PRD → EARS → BDD → ADR → SPEC →
TDD → IPLAN).

It was produced by following each
`platforms/claude-code-plugin/skills/doc-<layer>/SKILL.md` against
[`seed/initial-requirements.md`](seed/initial-requirements.md), gating every
layer with the plugin's deterministic structural validator (`sdd_doc_lint`).

## Re-run the deterministic gate

```bash
PYTHONPATH=platforms/claude-code-plugin python3 -m sdd_doc_lint examples/url-shortener/docs
# exit 0 = no error-level findings
```

## What this demonstrates

- The full **8-layer chain** for one feature set (shorten a URL, redirect, count clicks).
- **Cumulative traceability**: each layer carries `@brd … @tdd` tags that reference
  real upstream element IDs (4-segment `TYPE.NN.SS.xxxx`).
- The **C4 + DFD + sequence diagram** model per layer
  (`framework/governance/DIAGRAM_STANDARDS.md`): BRD `c4-l1`/`dfd-l1`,
  PRD `c4-l2`/`dfd-l2`/`sequence`, ADR decision `sequence`, SPEC `c4-l3`/`dfd-l3`.

> The plugin has no runtime — its skills are LLM instructions — so this chain was
> authored by following the skills, and the **deterministic gate** here is
> `sdd_doc_lint`. The semantic readiness score (≥90) is the LLM `-audit` skill's
> judgment and is noted per document, not machine-checked.
