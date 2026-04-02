# PLAN-021: SDD Reporting System Naming Standard

## Context

Report naming across the SDD framework is inconsistent — 6 different patterns coexist. This plan defines a unified standard and implements it in mcp_sdd. Legacy naming is deprecated with no backward compatibility — clean break.

**Goal**: Define and implement a unified report naming standard for the SDD framework across all sub-frameworks (sdd-lifecycle, project-governance, project-knowledge).

**Status**: Planned

**Target Release**: mcp_sdd v1.11.0 / docs_flow_framework v0.18.0

**Scope**: Standards document + mcp_sdd implementation. Legacy report files will be deleted, not migrated.

---

## SDD Sub-Framework Registry

| Code | Sub-Framework | MCP Server | Scope |
|------|--------------|------------|-------|
| `sdd` | SDD Lifecycle | `sdd-lifecycle` | Document creation, validation, review, remediation |
| `gov` | Project Governance | `project-governance` | GitHub Projects, IPLANs, governance rules |
| `kb` | Project Knowledge | `project-knowledge` | FTS5 + semantic search, frontmatter indexing |

The sub-framework code identifies which system produced the report. `sdd` is the default and can be omitted for core lifecycle reports.

---

## Naming Convention

### Reports

```
{DOC-ID}.{STAGE}.{FORMAT}
```

With optional sub-framework prefix for non-sdd reports:

```
{DOC-ID}.{SUB}.{STAGE}.{FORMAT}
```

| Component | Description | Values |
|-----------|-------------|--------|
| `{DOC-ID}` | Source document ID | `BRD-03`, `PRD-01`, `SPEC-01` |
| `{SUB}` | Sub-framework code (optional, omit for `sdd`) | `gov`, `kb` |
| `{STAGE}` | Lifecycle stage that produced the report | See table below |
| `{FORMAT}` | File extension | `.json`, `.md`, `.txt` |

### Stage Codes

| Stage Code | Full Name | mcp_sdd Tool | Description |
|------------|-----------|-------------|-------------|
| `validate` | Validation | `sdd_validate` | Structural + cross-section validation |
| `validate_fix` | Validation Fix | `sdd_validate_fix` | Source-protected fix manifest |
| `review` | Review | `sdd_review` | Multi-persona UCR review |
| `remediate` | Remediation | `sdd_remediate` | Deterministic findings + parsed review |
| `remediate_fix` | Remediation Fix | `sdd_remediate_fix` | Source-protected remediation fix manifest |
| `consistency` | Consistency | `sdd_consistency` | Artifact lineage check |
| `links` | Link Validation | `sdd_validate_links` | Markdown link check |
| `prescreen` | Prescreen | `sdd_prescreen` | Remediation candidate scan |
| `score` | Score | `sdd_score_show` | Quality score |

Reserved codes for future sub-frameworks:

| Stage Code | Sub-Framework | Description |
|------------|--------------|-------------|
| `gov.approval` | governance | Approval workflow report |
| `gov.gate` | governance | Quality gate report |
| `kb.index` | knowledge | Knowledge base index report |
| `kb.search` | knowledge | Search quality report |

### Format Roles

| Format | Role | Audience |
|--------|------|----------|
| `.json` | Machine-readable full report | Tools, pipelines, scoring |
| `.md` | Human-readable narrative report | Developers, reviewers |
| `.txt` | One-page text summary | Terminal output, logs |

### Examples

| Report | Filename |
|--------|----------|
| BRD-03 validation (machine) | `BRD-03.validate.json` |
| BRD-03 validation (summary) | `BRD-03.validate.txt` |
| BRD-03 review (human) | `BRD-03.review.md` |
| BRD-03 remediation (machine) | `BRD-03.remediate.json` |
| BRD-03 consistency | `BRD-03.consistency.json` |
| BRD-03 governance approval | `BRD-03.gov.approval.json` |
| BRD-03 knowledge index | `BRD-03.kb.index.json` |
| Versioned review | `BRD-03.review.v002.md` |

### Derived Copy Naming

Source-protected copies use underscores (not dots) to distinguish from reports:

```
{DOC-ID}_{slug}_{STAGE}_copy.{ext}
```

| Copy Type | Filename |
|-----------|----------|
| Validation copy | `BRD-03_security_compliance_validate_copy.yaml` |
| Remediation copy | `BRD-03_security_compliance_remediate_copy.yaml` |

### Versioned Reports

When audit trail is needed:

```
{DOC-ID}.{STAGE}.v{NNN}.{FORMAT}
```

Default: no version (latest overwrites). Version suffix when `--keep-history` flag is set.

---

## Detection Patterns (Regex)

```python
# Report: {DOC-ID}.{stage}.{format}
REPORT_PATTERN = re.compile(
    r"^[A-Z]+-\d+\."
    r"(?:(?:sdd|gov|kb)\.)?"  # optional sub-framework
    r"(?:validate|validate_fix|review|remediate|remediate_fix|"
    r"consistency|links|prescreen|score)"
    r"(?:\.v\d+)?"  # optional version
    r"\.(?:json|md|txt)$"
)

# Derived copy: {DOC-ID}_{slug}_{stage}_copy.{ext}
DERIVED_COPY_PATTERN = re.compile(
    r"^[A-Z]+-\d+_.+_(?:validate|remediate)_copy\.(?:md|yaml|yml)$"
)

# Source artifact: {DOC-ID}_{slug}.{ext} (not report, not derived)
SOURCE_PATTERN = re.compile(
    r"^[A-Z]+-\d+_.+\.(?:md|yaml|yml)$"
)
```

---

## Implementation

### Phase 1: Standards Document

Create `ai_dev_ssd_flow/REPORT_NAMING_STANDARDS.md` — canonical reference with:
- Sub-framework registry
- Naming convention
- Stage codes
- Format roles
- Detection regex patterns

### Phase 2: mcp_sdd Report Output

Update report filenames in all runners. Requires `doc_id` parameter passed to each runner.

| Runner | Current | New |
|--------|---------|-----|
| `validation/runner.py` | `validation_report.json` | `{doc_id}.validate.json` |
| `validation/runner.py` | `validation_report.txt` | `{doc_id}.validate.txt` |
| `remediation/runner.py` | `remediation_report.json` | `{doc_id}.remediate.json` |
| `remediation/runner.py` | `remediation_report.txt` | `{doc_id}.remediate.txt` |
| `remediation/runner.py` (validate_fix) | `validate_fix_report.json` | `{doc_id}.validate_fix.json` |
| `remediation/runner.py` (validate_fix) | `validate_fix_report.txt` | `{doc_id}.validate_fix.txt` |
| `remediation/runner.py` (remediate_fix) | `remediate_fix_report.json` | `{doc_id}.remediate_fix.json` |
| `remediation/runner.py` (remediate_fix) | `remediate_fix_report.txt` | `{doc_id}.remediate_fix.txt` |
| `consistency/runner.py` | `consistency_report.json` | `{doc_id}.consistency.json` |
| `consistency/runner.py` | `consistency_report.txt` | `{doc_id}.consistency.txt` |
| `link_validation/runner.py` | `link_validation_report.json` | `{doc_id}.links.json` |
| `link_validation/runner.py` | `link_validation_report.txt` | `{doc_id}.links.txt` |
| `prescreening/runner.py` | `prescreen_report.json` | `{doc_id}.prescreen.json` |
| `prescreening/runner.py` | `prescreen_report.txt` | `{doc_id}.prescreen.txt` |

### Phase 3: Derived Copy Naming

Update `_copy_with_suffix` and `_copy_with_canonical_suffix` in `remediation/runner.py`:
- `_validation` → `_validate_copy`
- `_remediated` → `_remediate_copy`

### Phase 4: Detection Updates

Update in `utils/source_files.py`, `tool_registry.py`, `consistency/runner.py`:
- Add `REPORT_PATTERN`, `DERIVED_COPY_PATTERN` constants
- Update `collect_source_files` to exclude new derived copy pattern
- Update `_inspect_document_folder` to detect new report/copy names

### Phase 5: Delete Legacy Reports

Remove all legacy-named reports from existing projects:
- `*.V_validation_report_*.md`
- `*.A_audit_report_*.md`
- `*.UCR_review_report_*.md`
- `*.UCRem_remediation_report_*.md`
- `*.UCRem_report.md`
- `*.F_fix_report_*.md`
- `*.R_review_report_*.md`

### Phase 6: Tests

Update existing tests + add new tests for naming patterns.

### Phase 7: Documentation + Changelogs

- mcp_sdd CHANGELOG v1.11.0 / ROADMAP
- Framework CHANGELOG v0.18.0 / ROADMAP
- Update mcp_sdd docs README

---

## File Changes

| File | Action | Est. Lines |
|------|--------|-----------|
| `ai_dev_ssd_flow/REPORT_NAMING_STANDARDS.md` | **Create** | ~100 |
| `mcp_sdd/src/mcp_server/validation/runner.py` | Modify — report filenames | +10 |
| `mcp_sdd/src/mcp_server/remediation/runner.py` | Modify — report filenames + copy naming | +20 |
| `mcp_sdd/src/mcp_server/consistency/runner.py` | Modify — report filenames | +10 |
| `mcp_sdd/src/mcp_server/link_validation/runner.py` | Modify — report filenames | +10 |
| `mcp_sdd/src/mcp_server/prescreening/runner.py` | Modify — report filenames | +10 |
| `mcp_sdd/src/mcp_server/utils/source_files.py` | Modify — detection patterns | +15 |
| `mcp_sdd/src/mcp_server/tool_registry.py` | Modify — `_inspect_document_folder` | +10 |
| Tests (updated + new) | Cover naming patterns | ~100 |
| Documentation | Changelogs, roadmaps, READMEs | ~80 |

**Total**: ~365 lines across 10+ files

---

## Risks

| Risk | Mitigation |
|------|-----------|
| `doc_id` not available in all runners | Extract from document filename or add parameter |
| Breaking existing report detection in pipelines | Update all detection logic in same release |
| Legacy reports left in repos after deletion | One-time cleanup script per project |

---

## Dependencies

- All prior plans (016-020) done
- Claude skill alignment is downstream — not in this plan's scope
