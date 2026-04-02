# PLAN-021: SDD Reporting System Naming Standard

## Context

Report naming across the SDD framework is inconsistent — 6 different patterns coexist between mcp_sdd tools and legacy Claude skills. This creates confusion for tooling, automation, and human operators.

**Goal**: Define a unified report naming standard for the SDD framework that works across all sub-frameworks (mcp_sdd, project governance, project knowledge base) and all lifecycle stages.

**Status**: Planned

**Scope**: Standards document + mcp_sdd implementation. Claude `doc-*` skill alignment is downstream.

---

## Current State: 6 Competing Patterns

| # | Pattern | Example | Source |
|---|---------|---------|--------|
| 1 | `{DOC-ID}.V_validation_report_v{NNN}.md` | `BRD-04.V_validation_report_v003.md` | Legacy Claude skills |
| 2 | `{DOC-ID}.A_audit_report_v{NNN}.md` | `BRD-04.A_audit_report_v007.md` | Legacy Claude skills |
| 3 | `{DOC-ID}.UCRem_remediation_report_v{NNN}.md` | `BRD-04.UCRem_remediation_report_v001.md` | Legacy Claude skills |
| 4 | `{DOC-ID}.UCR_review_report_v{NNN}.md` | `BRD-04.UCR_review_report_v005.md` | Legacy Claude skills |
| 5 | `validation_report.{json\|txt}` | `validation_report.json` | mcp_sdd tools |
| 6 | `{DOC-ID}_{slug}_validation.yaml` | `BRD-03_security_compliance_validation.yaml` | mcp_sdd validate_fix |

### Problems

1. **Pattern 5 has no document ID** — multiple docs in same folder would overwrite each other
2. **Patterns 1-4 use different separators** — `.V_`, `.A_`, `.UCRem_`, `.UCR_` (dot + type prefix)
3. **Pattern 6 appends stage to the slug** — `_validation`, `_remediated` (derived copies)
4. **No standard for sub-framework reports** — governance, knowledge base will need their own report types
5. **Version numbering inconsistent** — some use `_v{NNN}`, mcp_sdd uses no versioning
6. **Format inconsistent** — legacy uses `.md`, mcp_sdd uses `.json` + `.txt`

---

## Proposed Standard

### Report Naming Convention

```
{DOC-ID}.{STAGE}.{FORMAT}
```

| Component | Description | Values |
|-----------|-------------|--------|
| `{DOC-ID}` | Source document ID | `BRD-03`, `PRD-01`, `SPEC-01` |
| `{STAGE}` | Lifecycle stage that produced the report | See stage table below |
| `{FORMAT}` | File extension | `.json` (machine), `.md` (human), `.txt` (summary) |

### Stage Codes

| Stage Code | Full Name | mcp_sdd Tool | Description |
|------------|-----------|-------------|-------------|
| `validate` | Validation Report | `sdd_validate` | Structural + cross-section validation |
| `validate_fix` | Validation Fix Report | `sdd_validate_fix` | Source-protected fix manifest |
| `review` | Review Report | `sdd_review` | Multi-persona UCR review |
| `remediate` | Remediation Report | `sdd_remediate` | Deterministic findings + parsed review |
| `remediate_fix` | Remediation Fix Report | `sdd_remediate_fix` | Source-protected remediation fix manifest |
| `consistency` | Consistency Report | `sdd_consistency` | Artifact lineage check |
| `links` | Link Validation Report | `sdd_validate_links` | Markdown link check |
| `prescreen` | Prescreen Report | `sdd_prescreen` | Remediation candidate scan |
| `score` | Score Report | `sdd_score_show` | Quality score |

### Examples

| Current Name | Proposed Name |
|-------------|---------------|
| `validation_report.json` | `BRD-03.validate.json` |
| `validation_report.txt` | `BRD-03.validate.txt` |
| `review_report.md` | `BRD-03.review.md` |
| `remediation_report.json` | `BRD-03.remediate.json` |
| `remediate_fix_report.json` | `BRD-03.remediate_fix.json` |
| `consistency_report.json` | `BRD-03.consistency.json` |
| `link_validation_report.json` | `BRD-03.links.json` |
| `prescreen_report.json` | `BRD-03.prescreen.json` |

### Derived Copy Naming

Source-protected copies (validation, remediated):

```
{DOC-ID}_{slug}.{STAGE}.{ext}
```

| Current Name | Proposed Name |
|-------------|---------------|
| `BRD-03_security_compliance_validation.yaml` | `BRD-03_security_compliance.validate_copy.yaml` |
| `BRD-03_security_compliance_remediated.yaml` | `BRD-03_security_compliance.remediate_copy.yaml` |

### Versioned Reports (optional, for audit trail)

When version history is needed (e.g., iterative review cycles):

```
{DOC-ID}.{STAGE}.v{NNN}.{FORMAT}
```

Example: `BRD-03.review.v002.md`

Default: no version suffix (latest overwrites). Version suffix only when `--keep-history` flag is set.

### Sub-Framework Report Types

Reserved stage codes for future sub-frameworks:

| Sub-Framework | Stage Prefix | Example |
|--------------|-------------|---------|
| mcp_sdd | (none — core stages) | `BRD-03.validate.json` |
| project-governance | `gov_` | `BRD-03.gov_approval.json` |
| project-knowledge | `kb_` | `BRD-03.kb_index.json` |

---

## Legacy Compatibility

### Mapping Table

| Legacy Pattern | Standard Name | Migration |
|---------------|---------------|-----------|
| `BRD-04.V_validation_report_v003.md` | `BRD-04.validate.v003.md` | Rename |
| `BRD-04.A_audit_report_v007.md` | `BRD-04.audit.v007.md` | Rename (`audit` = combined validate+review) |
| `BRD-04.UCR_review_report_v005.md` | `BRD-04.review.v005.md` | Rename |
| `BRD-04.UCRem_remediation_report_v001.md` | `BRD-04.remediate.v001.md` | Rename |
| `BRD-04.F_fix_report_v002.md` | `BRD-04.fix.v002.md` | Rename |
| `BRD-04.R_review_report_v001.md` | `BRD-04.review.v001.md` | Rename |

### Transition Period

- mcp_sdd tools adopt new naming immediately
- Legacy Claude skill reports remain readable (backward-compatible glob patterns)
- `sdd_consistency` updated to detect both naming conventions
- No mass rename of existing legacy reports

---

## Implementation Scope

### Phase 1: Standards Document

Create `ai_dev_ssd_flow/REPORT_NAMING_STANDARDS.md` — the canonical reference.

### Phase 2: mcp_sdd Report Output

Update report output filenames in all runners:

| Runner | Current Output | New Output |
|--------|---------------|------------|
| `validation/runner.py` | `validation_report.json` | `{doc_id}.validate.json` |
| `remediation/runner.py` | `remediation_report.json` | `{doc_id}.remediate.json` |
| `remediation/runner.py` (validate_fix) | `validate_fix_report.json` | `{doc_id}.validate_fix.json` |
| `remediation/runner.py` (remediate_fix) | `remediate_fix_report.json` | `{doc_id}.remediate_fix.json` |
| `consistency/runner.py` | `consistency_report.json` | `{doc_id}.consistency.json` |
| `link_validation/runner.py` | `link_validation_report.json` | `{doc_id}.links.json` |
| `prescreening/runner.py` | `prescreen_report.json` | `{doc_id}.prescreen.json` |

Requires passing `doc_id` to runners that don't currently receive it.

### Phase 3: Derived Copy Naming

Update `_copy_with_suffix` and `_copy_with_canonical_suffix` in `remediation/runner.py`:
- `_validation.yaml` → `.validate_copy.yaml`
- `_remediated.yaml` → `.remediate_copy.yaml`

### Phase 4: Detection Updates

Update `_inspect_document_folder` and `_collect_yaml_files` to recognize both old and new naming patterns during transition.

### Phase 5: Documentation + Changelogs

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Breaking existing `_validation`/`_remediated` detection | Support both patterns during transition |
| Legacy reports not renamed | Glob patterns match both conventions |
| Sub-framework naming conflicts | Reserved prefix system |
| doc_id extraction from file path | Parse from filename or require as parameter |

---

## Dependencies

- All prior plans (016-020) done — this builds on the stabilized mcp_sdd
- Claude skill alignment is downstream — not in this plan's scope
