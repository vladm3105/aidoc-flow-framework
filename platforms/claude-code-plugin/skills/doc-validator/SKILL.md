---
name: doc-validator
description: Validate the SDD corpus - cross-document references, orphans, cumulative-tag gaps, duplicate IDs, and full bidirectional traceability (with optional repair), plus a prose/terminology pass. Use before releases, after batch generation, or to validate and repair the corpus.
metadata:
  tags:
    - sdd-workflow
    - utility
    - quality-assurance
  custom_fields:
    skill_category: utility
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
    downstream_artifacts: []
    version: "0.4.0"
    framework_spec_version: "0.11.0"
    last_updated: "2026-05-27"
    adapts: [active_layers, glossary]
---

# doc-validator

## Purpose

Validate relationships and consistency **across** documents in the SDD corpus:
broken cross-references, orphaned artifacts, one-way links, cumulative-tag
gaps, duplicate or malformed IDs, and traceability-matrix completeness across
the 8 layers. This skill **is** the validator — the framework ships no runtime
code; it applies declarative checks against `${CLAUDE_PLUGIN_ROOT}/framework/governance/` and the
layer `README.md` files.

**Layer**: cross-cutting utility (reads all 8 layers; produces no artifacts).

## When to Use

**Use** for project-wide checks: relationships between documents, cumulative
tagging, orphan detection, bidirectional-link consistency, duplicate IDs,
deep traceability (with optional link repair), prose/terminology review, and
before major releases. It is the single corpus-level validator — it also covers
the traceability depth + repair and the prose review that were previously
separate skills.

**Do NOT use** for:

- single-document structure/metadata/content — use that layer's
  `../doc-<layer>-audit/SKILL.md`;
- the *definition* of the ID-format rules — that authority is
  `../doc-naming/SKILL.md`. (This skill **enforces** ID format and emits
  `XDOC-E007`; use it to *check* IDs — `doc-naming` is where the rules live.)

Inputs: `docs_path` (required), `scope` (`cross-document` default /
`traceability` / `prose` / `full`), `strictness` (`strict` / `permissive`),
`auto_fix` (repair broken links / regenerate counts where safe), `report_format`.

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

### Traceability depth + repair

Beyond the cross-document checks, run the full bidirectional traceability pass:

- **Bidirectional symmetry** — for each A→B link confirm B→A exists; score
  `(matched pairs / total) × 100` (target ≥ 95%).
- **Coverage + orphans** — upstream is required for every artifact except BRD;
  downstream is optional; flag mid-chain artifacts with no downstream and
  unexpected orphans; report coverage by type.
- **Repair (`auto_fix`)** — when enabled, repair only safely-fixable issues: add
  a missing reciprocal link, regenerate section/COUNT metadata, normalize
  terminology. **Write a timestamped backup first and print a rollback command;
  never invent placeholder IDs** to satisfy a check. Structural/content gaps stay
  reported for the relevant `-fixer`.

### Prose review (`scope: prose`)

Review a single file or a folder for prose quality independent of traceability,
across four classes:

- **DATA** — stated counts / status / date logic vs. content (e.g. "5 features"
  but 4 listed; `last_updated` earlier than `created`).
- **REF** — inline link / anchor / tag-format resolution.
- **TYPO** — misspellings, doubled words, broken markdown.
- **TERM** — undefined acronyms, inconsistent or subjective terminology.

Severity follows `strictness`: under `strict`, any DATA/REF/TYPO/TERM finding is
an error (blocks); under `permissive`, they are warnings. Honor the project
`glossary` (`.aidoc/profile.yaml`; see *Adaptation*) to suppress domain-term TERM
false positives. Use before publishing or committing documentation.

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

Authority: `${CLAUDE_PLUGIN_ROOT}/framework/registry/LAYER_REGISTRY.yaml` (`required_tags`) and
`${CLAUDE_PLUGIN_ROOT}/framework/governance/TRACEABILITY.md`.

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

## Adaptation

Read the project adaptation profile (`.aidoc/profile.yaml`) before validating.
Honor this skill's declared knobs:

- `active_layers` — when a skippable layer (BDD / ADR) is disabled, treat it as
  absent **by design**: apply the cascade (drop it from downstream
  `required_tags` / `can_reference`) so the cumulative-tag, orphan, and
  bidirectional checks do **not** flag the intentional gap as an error.
- `glossary` — use the project's preferred terms to normalize and suppress
  domain-term `TERM` findings in the prose pass (no false positives on accepted
  vocabulary).

Ignore unknown / out-of-surface keys; absent a profile, use framework defaults.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Governance: `${CLAUDE_PLUGIN_ROOT}/framework/governance/DOC_GOVERNANCE_CORE.md` ·
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/TRACEABILITY.md` ·
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Layer registry: `${CLAUDE_PLUGIN_ROOT}/framework/registry/LAYER_REGISTRY.yaml`
- Per-layer authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/NN_<X>/README.md`
- ID-format authority: `../doc-naming/SKILL.md`
- Single-document gates: `../doc-brd-audit/SKILL.md` … `../doc-iplan-audit/SKILL.md`
- Workflow routing: `../doc-flow/SKILL.md` · Diagrams: `../charts-flow/SKILL.md`
