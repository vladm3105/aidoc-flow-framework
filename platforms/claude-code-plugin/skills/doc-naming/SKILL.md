---
name: doc-naming
description: The ID and naming authority for the SDD flow - validates document IDs, 4-segment element IDs, threshold tags, and flags removed/legacy patterns. Use before creating or editing any artifact.
metadata:
  tags:
    - sdd-workflow
    - utility
  custom_fields:
    skill_category: utility
    upstream_artifacts: []
    downstream_artifacts: []
    version: "0.22.0"
    framework_spec_version: "0.23.1"
    last_updated: "2026-05-23"
---

# doc-naming

## Purpose

The naming authority for the 8-layer SDD flow. `doc-naming` validates document
IDs, element IDs, threshold tags, and file names against
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`, and flags removed/legacy
patterns. It produces no artifacts — it is the declarative ID validator (the
framework ships no runtime code).

**Layer**: cross-cutting utility (applies to all 8 layers).

## When to Use

**Use** before creating or editing any artifact, to:

- verify a document or element ID format,
- check a `@threshold:` tag, or
- detect removed/legacy ID patterns and get the migration target.

**Do NOT use** for cross-document traceability or content review — use
`../doc-validator/SKILL.md`.

## Behavior

### 1. Document ID — `TYPE-NN`

`^[A-Z]{2,8}-[0-9]{2,}$` — uppercase type, single dash, 2+ digit sequence (no
extra leading zeros beyond two: `BRD-01`, `ADR-99`, `IPLAN-102`). File name:
`TYPE-NN_descriptive_slug.md`.

### 2. Element ID — `TYPE.NN.SS.xxxx` (4-segment)

`^[A-Z]+\.[0-9]{2,}\.[0-9]{2,}\.[a-f0-9]{4,8}$`

| Segment | Meaning | Format |
|---------|---------|--------|
| TYPE | Artifact prefix | `BRD PRD EARS BDD ADR TDD` |
| NN | Document number | 2+ digits |
| SS | Source section number | 2+ digits |
| xxxx | Content hash (SHA256, first 4 hex; extend to 8 on collision) | `[a-f0-9]{4,8}` |

Example: `BRD.01.07.a7f3`. Element IDs appear as markdown headings
(`### BRD.01.07.a7f3: Title`).

### 3. Reference granularity (element vs document)

There are **no numeric element-type codes** — identity is the section + hash,
not a fixed code.

| Layer | Reference form | Example |
|-------|----------------|---------|
| BRD, PRD, EARS, BDD, TDD | element (dotted) `TYPE.NN.SS.xxxx` | `PRD.01.09.1dbc` |
| ADR | both: document `ADR-NN` and element `ADR.NN.SS.xxxx` | `ADR-05`, `ADR.05.03.e5b1` |
| SPEC, IPLAN | document (dash) `TYPE-NN` | `SPEC-06`, `IPLAN-01` |

Traceability tags carry these refs: `@brd: BRD.01.07.a7f3`, `@spec: SPEC-06`,
`@iplan: IPLAN-01`.

### 4. Threshold tags

`@threshold: {TYPE}.{NN}.{key}` where `key` is
`category.subcategory.attribute[.qualifier]`. Categories: `perf timeout rate
retry circuit alert cache pool queue batch`. Doc reference is mandatory and
dot-separated — `@threshold: PRD.035.timeout.partner.bridge` (valid);
`@threshold: timeout.partner.bridge` (missing doc ref — invalid). Threshold
sources: BRD (business SLAs), PRD (product metrics), ADR (technical limits).

### 5. Reserved-ID and REF exemptions

- **`TYPE-00_*`** (indexes, templates, glossaries) — framework infrastructure;
  skip element-ID and traceability checks.
- **`TYPE-REF-NN_{slug}.md`** (BRD/ADR only, via `../doc-ref/SKILL.md`) —
  free-format reference targets; no element IDs, no quality gates.

### 6. Removed / legacy patterns (reject)

Migrate every match to `TYPE.NN.SS.xxxx` (or a dash doc ref for SPEC/IPLAN):

| Removed | Applies to |
|---------|-----------|
| `AC-XXX`, `FR-XXX`, `BC-XXX`, `BA-XXX`, `QA-XXX`, `BO-XXX`, `RISK-XXX`, `METRIC-XXX`, `Feature F-XXX` | BRD, PRD |
| `Event-XXX`, `State-XXX` | EARS |
| `DEC-XXX`, `ALT-XXX`, `CON-XXX` | ADR |
| 3-segment `TYPE.NN.xxxx` | all element layers |

Detect with grep, e.g. `grep -E "(AC|FR|BC|BA|QA|BO|NFR|RISK|METRIC)(-[A-Za-z0-9]+)*-[0-9]+" file.md`
(the optional `(-[A-Za-z0-9]+)*` catches compound forms like `FR-CICD-001`).
Migration: derive `TYPE`/`NN` from the file name, `SS` from the source section,
`xxxx` from the element content hash; replace all occurrences and re-verify.

### 7. ISO 8601 timestamps

Date/time fields (frontmatter `last_updated`, `created_date`; `review_date`,
`fix_date`, `approval_date`, `decision_date`) use
`YYYY-MM-DDTHH:MM:SS` (optionally `Z` or `±HH:MM`), enabling same-day drift
detection. Date-only values are deprecated.

### Pre-flight checklist

- [ ] Document ID is `TYPE-NN`; file name is `TYPE-NN_slug.md`.
- [ ] Element IDs are 4-segment `TYPE.NN.SS.xxxx` with a 4–8 hex hash, unique
      within the document; SPEC/IPLAN use dash doc refs.
- [ ] `@threshold:` tags include the doc reference and an approved category.
- [ ] No removed/legacy patterns; no 3-segment element IDs.
- [ ] Traceability tag prefixes (`@brd:` … `@tdd:`) are correct and targets exist.

## Related Resources

- ID & tag authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
- Threshold rules: `${CLAUDE_PLUGIN_ROOT}/framework/governance/THRESHOLD_NAMING_RULES.md`
- Layer registry (roster, chains, folders): `${CLAUDE_PLUGIN_ROOT}/framework/registry/LAYER_REGISTRY.yaml`
- Per-layer templates & READMEs: `${CLAUDE_PLUGIN_ROOT}/framework/layers/NN_<X>/`
- Cross-document validation: `../doc-validator/SKILL.md`
- Workflow routing: `../doc-flow/SKILL.md`
- Diagrams: `../charts-flow/SKILL.md`
