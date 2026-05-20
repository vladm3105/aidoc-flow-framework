# SPEC-005: MCP Source Input and Ingestion Contracts

| Field | Value |
| --- | --- |
| Canonical ID | SPEC-005 |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-24 |
| Scope | Source section input contracts and ingestion behavior for create-build and review-build |

---

## 1. Purpose

Define normative source payload contracts, precedence rules, and ingestion failure handling for implemented MCP runtime operations.

Implementation complexity: 4/5.

---

## 2. Scope and Boundaries

In scope:
- SourceSection payload contract
- sections-json ingestion behavior
- include and skip semantics
- source-of-truth precedence for conflicting source claims

Out of scope:
- direct markdown ingestion mode as a first-class create-build interface
- external preprocessing pipelines not represented in runtime modules

---

## 3. Source Payload Contract

sections-json element required fields:
- section_id
- title
- content

sections-json optional field:
- included (default true)

Required top-level structure:
- JSON array of section objects

Failure modes:
- missing required field in any element
- unreadable file path
- invalid JSON syntax

---

## 4. Ingestion Behavior Contracts

### 4.1 create-build

Normative behavior:
- sections-json is optional.
- if sections-json is provided, create-build must parse and pass SourceSection list to assembly runtime.
- if sections-json is omitted, create-build may proceed with fallback behavior provided by assembly runtime.

Constraint:
- runtime does not define a dedicated direct-markdown ingestion mode at CLI contract level.

### 4.2 review-build

Normative behavior:
- One of sections-json or document is required.
- If sections-json is provided, it takes precedence.
- If document is provided (folder or file), the review pipeline collects source files automatically:
  - Supported extensions: `.md`, `.yaml`, `.yml`.
  - Canonical source identified by `^[A-Z]+-\d+_.+\.(md|yaml|yml)$` (excluding appendix files).
  - YAML-first precedence: when both `.yaml` and `.md` canonical sources exist in the same folder, `.yaml` is selected.
  - Legacy files (`_LEGACY` in stem) are excluded from candidate lists.
  - Appendix files are included by name signal (`appendix`/`appendices`).

---

## 5. Inclusion and Filtering Semantics

Normative behavior:
- included field false marks section as ineligible for included section list.
- section categorization and multi-persona mapping behavior (via `persona_mappings.yaml`) is handled by assembly runtime contracts.
- skipped sections may still contribute discovered snippets under contextual rules.

---

## 6. Source Conflict Semantics

When input statements conflict with implemented runtime behavior:
1. runtime code and tests take precedence
2. canonical specs take precedence over architecture and runbook documents
3. reconciliation log entry is required for conflict closure

Failure modes:
- source statement preserved in active canonical artifact after conflict closure without rationale
- source precedence applied inconsistently across docs

---

## 7. Validation Evidence Requirements

Required evidence:
- CLI contract parity check against ucx_hermes/src/mcp_server/cli/main.py
- source mapping behavior review against ucx_hermes/src/mcp_server/prompts/context_builder.py
- reconciliation update in DOC-RECONCILIATION-LOG-001

---

## 8. Resource Requirements and Constraints

- CPU: low to moderate
- Memory: moderate for section payload parsing
- Storage: low
- Constraint: ingestion contract changes require lifecycle policy version update
