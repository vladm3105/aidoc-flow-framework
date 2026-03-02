---
title: "Metadata Core Matrix"
tags:
  - framework-guide
  - metadata
  - validation
  - shared-architecture
custom_fields:
  document_type: guide
  artifact_type: REF
  status: production
  schema_version: "1.0"
  last_updated: "2026-03-01"
---

# Metadata Core Matrix

## 1. Purpose

Define a single mandatory core metadata contract for SDD artifacts while allowing layer-specific custom fields and tags.

## 2. Canonical Core Metadata (Mandatory)

| Field | Meaning | Allowed Values | Required |
|---|---|---|---|
| `title` | Human-readable document title | non-empty string | Yes |
| `tags` | Classification tags | array of strings (layer-specific required minimum + optional extensions) | Yes |
| `custom_fields.document_type` | Document role/type | layer-defined; minimum supports `template` and instance type | Yes |
| `custom_fields.artifact_type` | Artifact family identity | layer-defined constant (`BRD`, `PRD`, `REQ`, etc.) | Yes |
| `custom_fields.layer` | SDD layer number | integer matching artifact layer | Yes |
| `custom_fields.status` | Lifecycle state (canonical) | `draft`, `development`, `production`, `deprecated`, `reference` | Yes |
| `custom_fields.schema_version` | Contract/template version | semantic string | Yes |
| `custom_fields.last_updated` | Last metadata update timestamp/date | ISO date or datetime string | Yes |

## 3. Additional Core Routing Field

| Field | Meaning | Allowed Values | Required |
|---|---|---|---|
| `custom_fields.deliverable_type` | Downstream SPEC subtype routing | `code`, `document`, `ux`, `risk`, `process` | Required where routing applies (BRD/PRD/EARS/BDD/ADR/SYS/REQ/TASKS); optional/absent in CTR; represented in SPEC family schemas |

## 4. Compatibility Policy (`development_status` -> `status`)

Transition behavior:
1. Accept both `custom_fields.status` and legacy `custom_fields.development_status`.
2. If both exist, `status` is authoritative.
3. Emit warning when `development_status` is used.
4. Remove legacy acceptance after strict cutover gate.

## 5. Pre-Commit Enforcement Scope

Blocking pre-commit metadata checks are scoped to reduce noise:

- Ignore `custom_fields.document_type: template`
- Ignore `custom_fields.status: draft`
- Enforce blocking checks only for instance artifacts with `custom_fields.status` in:
  - `development`
  - `production`

Notes:
- Non-blocking report mode may include template/draft artifacts for visibility.
- During compatibility window, `development_status` is mapped to `status` for evaluation.

## 6. Per-Layer Applicability Matrix

| Layer Family | Core Metadata Contract | Notes |
|---|---|---|
| L1 BRD | Applies | Core fields in `custom_fields`; routing field used |
| L2 PRD | Applies | Core fields in `custom_fields`; routing field used |
| L3 EARS | Applies | Core fields in `custom_fields`; routing field used |
| L4 BDD | Applies | Core fields in `custom_fields`; routing field used |
| L5 ADR | Applies | Core fields in `custom_fields`; routing field used |
| L6 SYS | Applies | Core fields in `custom_fields`; routing field used |
| L7 REQ | Applies | Core fields in `custom_fields`; routing field used |
| L8 CTR | Applies with extension | Core fields apply; `deliverable_type` may be absent by contract |
| L9 SPEC parent | Applies by mapping | Equivalent fields may be top-level/metadata mix; keep semantic parity |
| L9 SPEC subtypes (CSPEC/DSPEC/UXSPEC/RISKSPEC/PROCSPEC) | Applies by mapping | Subtype schemas may place fields differently; semantic parity required |
| L10 TSPEC family (UTEST/ITEST/STEST/FTEST/PTEST/SECTEST) | Applies by mapping | JSON-schema style metadata/document_control model; use field mapping |
| L11 TASKS | Applies | Core fields in `custom_fields`; routing field used |
| CHG / support docs | Applies where frontmatter exists | Use core fields for governance docs where feasible |

## 7. Layer Extension Policy

- Layers may define additional custom fields and additional required tags.
- Layer extensions must not redefine the meaning of core fields.
- Layer-specific fields are documented in each layer schema/template and referenced from this matrix.

## 8. Acceptance Evidence Commands

```bash
grep -R --line-number -E 'status:|development_status:' ai_dev_ssd_flow
grep -R --line-number -E 'required_custom_fields:|status:|development_status:' ai_dev_ssd_flow/**/*_MVP_SCHEMA.yaml
grep -R --line-number 'METADATA_CORE_MATRIX.md' ai_dev_ssd_flow/METADATA_TAGGING_GUIDE.md ai_dev_ssd_flow/METADATA_QUICK_REFERENCE.md ai_dev_ssd_flow/README.md
grep -R --line-number -E 'document_type|status|template|draft|development|production' ai_dev_ssd_flow/scripts/pre_commit_hooks ai_dev_ssd_flow/.pre-commit-config.yaml
```
