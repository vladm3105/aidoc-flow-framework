---
name: doc-validator
description: Cross-document validation for the SDD flow - broken cross-references, orphaned artifacts, cumulative-tag gaps, duplicate IDs, and traceability-matrix completeness across the corpus. Use before releases or after batch generation.
metadata:
  tags:
    - sdd-workflow
    - utility
    - quality-assurance
  custom_fields:
    skill_category: utility
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
    downstream_artifacts: []
    version: "0.2.0"
    framework_spec_version: "0.4.0"
    last_updated: "2026-05-23"
---

# doc-validator

## Purpose

Validate relationships and consistency **across** documents in the SDD corpus:
broken cross-references, orphaned artifacts, one-way links, cumulative-tag
gaps, duplicate or malformed IDs, and traceability-matrix completeness across
the 8 layers. This skill **is** the validator — the framework ships no runtime
code; it applies declarative checks against `framework/governance/` and the
layer `README.md` files.

**Layer**: cross-cutting utility (reads all 8 layers; produces no artifacts).

## When to Use

**Use** for project-wide checks: relationships between documents, cumulative
tagging, orphan detection, bidirectional-link consistency, duplicate IDs, and
before major releases.

**Do NOT use** for:

- single-document structure/metadata/content — use that layer's
  `../doc-<layer>-audit/SKILL.md`;
- ID-format compliance — use `../doc-naming/SKILL.md`;
- detailed traceability analysis — use `../trace-check/SKILL.md`;
- prose quality (typos, terms) — use `../doc-review/SKILL.md`.

Inputs: `docs_path` (required), `scope` (`cross-document` default /
`traceability` / `full`), `strictness` (`strict` / `permissive`),
`report_format`.

## Behavior

### Cross-document checks

| Category | Check | Error codes |
|----------|-------|-------------|
| LINKS | Every markdown/document link and anchor resolves | XDOC-E001, XDOC-E004 |
| CROSS-REF | Each cited document/element ID exists in the corpus | XDOC-E001, XDOC-E003 |
| ORPHAN | No artifact lacks an upstream connection | XDOC-E005 |
| TAGS | Cumulative upstream tags complete per the 8-layer hierarchy | XDOC-E002 |
| IDS | Element IDs `TYPE.NN.SS.xxxx`; doc refs `SPEC-NN`/`ADR-NN`/`IPLAN-NN`; no duplicates; no legacy/3-segment/retired forms | XDOC-E006, XDOC-E007 |
| MATRIX | Traceability-matrix completeness across 8 layers | XDOC-W001 |
| SECTION | Section file count matches metadata | SEC-E001…E003, SEC-W001 |
| DIAGRAM | Mermaid entities match prose | DIAG-E001/E002, DIAG-W001/W002 |
| TERM | Terminology/acronym consistency | TERM-E001/E002, TERM-W001/W002 |
| COUNT | Stated counts match itemized totals | COUNT-E001, COUNT-W001 |
| FWDREF | No upstream→downstream references; no cycles | FWDREF-E001/E002, FWDREF-W001 |

SECTION / TERM / COUNT findings are typically auto-fixable (regenerate
counts/sections, normalize terms); the rest are reported for manual fix.

### Cumulative-tag hierarchy

| Layer | Artifact | Required upstream tags |
|-------|----------|------------------------|
| 1 | BRD | none |
| 2 | PRD | @brd |
| 3 | EARS | @brd, @prd |
| 4 | BDD | @brd, @prd, @ears |
| 5 | ADR | @brd, @prd, @ears, @bdd |
| 6 | SPEC | + @adr (5) |
| 7 | TDD | + @spec (6) |
| 8 | IPLAN | + @tdd (7) |

Authority: `framework/registry/LAYER_REGISTRY.yaml` (`required_tags`) and
`framework/governance/TRACEABILITY.md`.

### ID-format enforcement (IDS)

Require element IDs in the 4-segment form `TYPE.NN.SS.xxxx`
(`TYPE` ∈ {BRD, PRD, EARS, BDD, ADR, TDD}) and document-level refs in the dash
form `SPEC-NN`/`ADR-NN`/`IPLAN-NN`. **Reject** legacy 3-segment element IDs,
the numeric type-code scheme, and any reference to retired 12-layer artifacts —
flag each with XDOC-E007. See `../doc-naming/SKILL.md`.

### Quality gates

`ERROR` blocks (exit 2); `WARNING` blocks only under `--strict` (exit 1);
`INFO` is advisory. Project-wide gates: zero cross-reference errors, zero
orphans, 100% bidirectional and 100% cumulative-tag compliance, zero duplicate
IDs. Output is a consolidated report (markdown/json/text) listing each finding,
its code, and a fix hint.

## Related Resources

- Governance: `framework/governance/DOC_GOVERNANCE_CORE.md` ·
  `framework/governance/TRACEABILITY.md` ·
  `framework/governance/ID_NAMING_STANDARDS.md`
- Layer registry: `framework/registry/LAYER_REGISTRY.yaml`
- Per-layer authority: `framework/layers/NN_<X>/README.md`
- ID formats: `../doc-naming/SKILL.md` · Traceability: `../trace-check/SKILL.md`
- Single-document gates: `../doc-brd-audit/SKILL.md` … `../doc-iplan-audit/SKILL.md`
- Prose review: `../doc-review/SKILL.md` · Workflow routing: `../doc-flow/SKILL.md`
- Diagrams: `../charts-flow/SKILL.md`
