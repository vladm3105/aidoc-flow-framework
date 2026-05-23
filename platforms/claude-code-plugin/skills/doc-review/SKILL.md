---
name: doc-review
description: Cross-cutting quality review of a single file or a whole folder - finds data inconsistencies, broken references, typos, and unclear terminology. Use before publishing or committing documentation.
metadata:
  tags:
    - sdd-workflow
    - utility
    - quality-assurance
  custom_fields:
    skill_category: utility
    upstream_artifacts: []
    downstream_artifacts: []
    version: "0.2.0"
    framework_spec_version: "0.3.0"
    last_updated: "2026-05-23"
---

# doc-review

## Purpose

A cross-cutting documentation quality reviewer. `doc-review` analyzes one file
or an entire folder for four classes of issue — **data inconsistencies**,
**reference errors**, **typos/formatting**, and **terminology** — and reports
findings by severity. It is content/quality focused; it does not enforce SDD
structure or traceability.

**Layer**: cross-cutting utility (produces no artifacts).

## When to Use

**Use** to review documentation before publication or commit, after a batch of
generation, or to audit a folder for cross-file consistency.

**Do NOT use** for:
- bidirectional traceability — use `../trace-check/SKILL.md`;
- cross-document SDD validation (links, tags, IDs) — use
  `../doc-validator/SKILL.md`;
- single-document structural quality gates — use that layer's
  `../doc-<layer>-audit/SKILL.md`.

## Behavior

### Modes

| Mode | Input | Behavior |
|------|-------|----------|
| Single file | a file path | Deep analysis of one file |
| Folder | a directory path | Analyzes all files together, adding cross-file checks (terminology consistency, cross-document references, duplicate content) |

Optional inputs: `scope` (`quick` / `full` / `deep`), `focus`
(`data,references,typos,terms`), `report_format` (`markdown` / `json` /
`summary`).

### Review dimensions (four parallel sub-agents)

The skill discovers the target files, then runs four reviewers in parallel and
merges their findings:

1. **Data consistency** — count mismatches (stated vs actual), status/maturity
   mismatches, date logic (`last_updated >= created`), version format,
   duplicate content. Codes `DATA-*`.
2. **References** — markdown link and anchor resolution, relative-path
   correctness, traceability-tag format (`@brd:`/`@prd:`/`@ears:`/`@bdd:`/
   `@adr:`/`@spec:`/`@tdd:`/`@iplan:`), circular references. Codes `REF-*`.
3. **Typos / formatting** — misspellings, doubled words, markdown syntax
   (unclosed blocks, broken tables), punctuation and whitespace. Codes `TYPO-*`.
4. **Terminology** — undefined acronyms, inconsistent naming, ambiguous
   pronouns, subjective qualifiers ("fast", "simple"), conflicting
   definitions. Codes `TERM-*`.

### Severity and gates

Findings are `ERROR` (must fix), `WARNING` (should fix), or `INFO`. Default
gate: **0 errors**; warnings allowed by scope (`quick` ≤10, `full` ≤5,
`deep` 0). Auto-fix (opt-in) is limited to simple, safe patterns — date/count
normalization, relative-path fixes, tag-format fixes, doubled words,
punctuation/whitespace. Everything else is reported for manual review.

A project may add a custom dictionary and severity overrides (e.g. a
`.doc-review.yaml`) to suppress domain-term false positives.

## Related Resources

- Cross-document validation: `../doc-validator/SKILL.md`
- Traceability: `../trace-check/SKILL.md`
- Naming authority (tag/ID formats): `../doc-naming/SKILL.md`
- Quality advice: `../quality-advisor/SKILL.md`
- Workflow routing: `../doc-flow/SKILL.md`
- Governance: `framework/governance/DOC_GOVERNANCE_CORE.md`
- Diagrams: `../charts-flow/SKILL.md`
