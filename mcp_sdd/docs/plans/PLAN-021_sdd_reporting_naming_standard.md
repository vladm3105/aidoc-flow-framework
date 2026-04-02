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

## `doc_id` Extraction Strategy

Runners need `doc_id` to construct report filenames. Strategy:

**New helper in `utils/source_files.py`:**

```python
def extract_doc_id(path: Path) -> str:
    """Extract document ID (e.g., 'BRD-03') from filename or parent folder.
    
    Handles:
    - BRD-03_security_compliance.yaml → BRD-03
    - BRD-03_security_compliance/ (directory) → BRD-03
    - BRD-03.validate.json (report) → BRD-03
    """
    name = path.name if path.is_file() else path.name
    match = re.match(r"^([A-Z]+-\d+)", name)
    if match:
        return match.group(1)
    # Fallback: try parent folder name
    match = re.match(r"^([A-Z]+-\d+)", path.parent.name)
    return match.group(1) if match else "UNKNOWN"
```

**Runner integration:** Each runner calls `extract_doc_id(document_path)` to get the ID for report filenames. No signature changes needed — `document_path`/`target_path` is already available in all runners.

| Runner | Has | Extraction |
|--------|-----|-----------|
| `validation/runner.py` | `document_path` | `extract_doc_id(document_path)` |
| `remediation/runner.py` | `document_path` | `extract_doc_id(document_path)` |
| `consistency/runner.py` | `target_path` | `extract_doc_id(target_path)` |
| `link_validation/runner.py` | `target_path` | `extract_doc_id(target_path)` |
| `prescreening/runner.py` | `document_path` | `extract_doc_id(document_path)` |
| `scan/runner.py` | `report_file` | `extract_doc_id(report_file)` |

---

## Implementation

### Phase 1: Standards Document + Helpers

1. Create `ai_dev_ssd_flow/REPORT_NAMING_STANDARDS.md` — canonical reference
2. Add `extract_doc_id()` to `utils/source_files.py`
3. Add `REPORT_PATTERN`, `DERIVED_COPY_PATTERN` constants to `utils/source_files.py`

### Phase 2: mcp_sdd Report Output

Update report filenames in all runners:

| Runner | Current | New |
|--------|---------|-----|
| `validation/runner.py` | `validation_report.json/.txt` | `{doc_id}.validate.json/.txt` |
| `remediation/runner.py` | `remediation_report.json/.txt` | `{doc_id}.remediate.json/.txt` |
| `remediation/runner.py` (validate_fix) | `validate_fix_report.json/.txt` | `{doc_id}.validate_fix.json/.txt` |
| `remediation/runner.py` (remediate_fix) | `remediate_fix_report.json/.txt` | `{doc_id}.remediate_fix.json/.txt` |
| `consistency/runner.py` | `consistency_report.json/.txt` | `{doc_id}.consistency.json/.txt` |
| `link_validation/runner.py` | `link_validation_report.json/.txt` | `{doc_id}.links.json/.txt` |
| `prescreening/runner.py` | `prescreen_report.json/.txt` | `{doc_id}.prescreen.json/.txt` |

Also update `tool_registry.py` dispatch handlers that construct report paths between stages:
- `sdd_validate` handler returns `report_path` — downstream tools use this path
- `_handle_lifecycle_pipeline` passes stage results — report paths must use new names
- `_build_remediate_fix_prompt` reads `remediation_report_path` — callers pass new name

### Phase 3: Derived Copy Naming

Update in `remediation/runner.py`:

| Function | Change |
|----------|--------|
| `_copy_with_suffix(src, "validation", ...)` | → `_copy_with_suffix(src, "validate_copy", ...)` |
| `_copy_with_suffix(src, "remediated", ...)` | → `_copy_with_suffix(src, "remediate_copy", ...)` |
| `_copy_with_canonical_suffix(src, "remediated", ...)` | → `_copy_with_canonical_suffix(src, "remediate_copy", ...)` |
| `_canonical_stem()` | Strip `_validate_copy` and `_remediate_copy` (remove `_validation`/`_remediated`) |
| `_resolve_validation_copy_path()` | Search for `_validate_copy.{md,yaml,yml}` (remove `_validation.md` pattern) |
| `_resolve_source_document_path()` | Search both `.md` and `.yaml` (currently `.md` only) |

### Phase 4: Detection Updates

| File | Function | Change |
|------|----------|--------|
| `utils/source_files.py` | `collect_source_files()` | Exclude `_validate_copy`/`_remediate_copy` (replace `_validation`/`_remediated`) |
| `utils/source_files.py` | `_is_excluded()` | Update stem checks |
| `tool_registry.py` | `_inspect_document_folder()` | New detection patterns: |

```python
# In _inspect_document_folder():
has_validation_report = any(
    REPORT_PATTERN.match(f.name) and ".validate." in f.name
    for f in json_files + md_files + yaml_files
)
has_validation_copy = any(
    "_validate_copy" in f.stem for f in md_files + yaml_files
)
has_review_report = any(
    REPORT_PATTERN.match(f.name) and ".review." in f.name
    for f in json_files + md_files
)
has_remediation_report = any(
    REPORT_PATTERN.match(f.name) and ".remediate." in f.name
    for f in json_files + md_files
)
has_remediated_copy = any(
    "_remediate_copy" in f.stem for f in md_files + yaml_files
)
```

Also update `consistency/runner.py` derived artifact detection (lines 100-114) to use new names.

### Phase 5: Delete Legacy Reports

**Projects:**
- `/opt/data/b-local/b-local-docs/` — all `docs/01_BRD/` subfolders
- `/opt/data/docs_flow_framework/` — if any exist

**Procedure:**
1. Dry run: `find docs/01_BRD -name "*.V_validation_report_*" -o -name "*.A_audit_report_*" ...` — count files
2. Delete: `find ... -delete`
3. Also delete old mcp_sdd generic reports: `validation_report.json`, `consistency_report.json`, etc.
4. Git commit the deletions

**Patterns to delete:**
```bash
find docs/ \( \
  -name "*.V_validation_report_*.md" -o \
  -name "*.A_audit_report_*.md" -o \
  -name "*.UCR_review_report_*.md" -o \
  -name "*.UCRem_remediation_report_*.md" -o \
  -name "*.UCRem_report.md" -o \
  -name "*.F_fix_report_*.md" -o \
  -name "*.R_review_report_*.md" -o \
  -name "validation_report.json" -o \
  -name "validation_report.txt" -o \
  -name "consistency_report.*" -o \
  -name "link_validation_report.*" -o \
  -name "prescreen_report.*" -o \
  -name "remediation_report.*" -o \
  -name "remediate_fix_report.*" -o \
  -name "validate_fix_report.*" -o \
  -name "*_validation.yaml" -o \
  -name "*_validation.md" -o \
  -name "*_remediated.yaml" -o \
  -name "*_remediated.md" \
\) -type f
```

### Phase 6: Tests

**16 test files need updating:**

Unit tests (11):
- `test_yaml_parity.py` — report path assertions
- `test_api_aliases.py` — minor if any
- `test_validation_runner.py` — report filename assertions
- `test_server.py` — tool handler tests
- `test_cli_main.py` — CLI output paths
- `test_creation_profile_contracts.py` — if report refs
- `test_link_validation_runner.py` — report filename
- `test_prescreening.py` — report filename
- `test_source_files.py` — derived copy patterns
- `test_remediation_runner.py` — report filenames + copy names
- `test_reporting_contracts.py` — report format

Integration tests (4):
- `test_migration_flows.py` — report detection
- `test_creation_profile_contracts_integration.py`
- `test_lifecycle_pipeline_integration.py` — pipeline report passing
- `test_reporting_contracts_integration.py`

Contract tests (1):
- `test_context_engineering_contracts.py`

New tests:
- `test_report_naming.py` — regex patterns, `extract_doc_id()`, naming convention

**Estimated: ~250 lines of test changes across 16 files + ~80 lines new test file.**

### Phase 7: Documentation + Changelogs

- mcp_sdd CHANGELOG v1.11.0
- mcp_sdd ROADMAP — add v1.11.0
- mcp_sdd README — add changelog link
- Framework CHANGELOG v0.18.0
- Framework ROADMAP — add v0.18.0
- Update `ai_dev_ssd_flow/ID_NAMING_STANDARDS.md` — cross-reference to REPORT_NAMING_STANDARDS

---

## File Changes

| File | Action | Est. Lines |
|------|--------|-----------|
| `ai_dev_ssd_flow/REPORT_NAMING_STANDARDS.md` | **Create** | ~120 |
| `mcp_sdd/src/mcp_server/utils/source_files.py` | Modify — `extract_doc_id()`, patterns | +30 |
| `mcp_sdd/src/mcp_server/validation/runner.py` | Modify — report filenames | +10 |
| `mcp_sdd/src/mcp_server/remediation/runner.py` | Modify — filenames + copy naming + `_canonical_stem` + `_resolve_*` | +30 |
| `mcp_sdd/src/mcp_server/consistency/runner.py` | Modify — filenames + derived detection | +15 |
| `mcp_sdd/src/mcp_server/link_validation/runner.py` | Modify — filenames | +10 |
| `mcp_sdd/src/mcp_server/prescreening/runner.py` | Modify — filenames | +10 |
| `mcp_sdd/src/mcp_server/scan/runner.py` | Modify — if outputs reports | +5 |
| `mcp_sdd/src/mcp_server/tool_registry.py` | Modify — `_inspect_document_folder` + dispatch paths | +20 |
| `mcp_sdd/tests/unit/test_report_naming.py` | **Create** — naming tests | ~80 |
| 16 existing test files | Modify — report name assertions | ~250 |
| Documentation (6 files) | Changelogs, roadmaps, READMEs | ~100 |

**Total**: ~680 lines across 25+ files

---

## Risks

| Risk | Mitigation |
|------|-----------|
| `extract_doc_id` returns "UNKNOWN" for unexpected paths | Validate in tests; log warning when fallback used |
| Pipeline breaks between stages (report path mismatch) | Update all dispatch handlers in same commit; integration test covers pipeline |
| 16 test files is large blast radius | Run full suite after each phase; commit per phase |
| Legacy report deletion removes useful audit history | This is intentional — clean break, no backward compat |

---

## Dependencies

- All prior plans (016-020) done
- Claude skill alignment is downstream — not in this plan's scope
