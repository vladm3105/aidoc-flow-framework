# SDD Report Naming Standards

## Sub-Framework Registry

| Code | Sub-Framework | MCP Server | Scope |
|------|--------------|------------|-------|
| `ucx` | UCX (Unified Context Framework) | `sdd-lifecycle` | Document creation, validation, review, remediation |
| `gov` | Project Governance | `project-governance` | GitHub Projects, IPLANs, governance rules |
| `kb` | Project Knowledge | `project-knowledge` | FTS5 + semantic search, frontmatter indexing |

## Report Naming Convention

Format: `{DOC-ID}.{SUB}.{STAGE}.{FORMAT}` — sub-framework code is always explicit.

### Components

| Component | Description | Examples |
|-----------|-------------|---------|
| `{DOC-ID}` | Source document ID | `BRD-03`, `PRD-01`, `SPEC-01` |
| `{SUB}` | Sub-framework code (always explicit) | `ucx`, `gov`, `kb` |
| `{STAGE}` | Lifecycle stage | `validate`, `review`, `remediate` |
| `{FORMAT}` | File extension | `.json`, `.md`, `.txt` |

### Stage Codes

| Code | Tool | Description |
|------|------|-------------|
| `validate` | `sdd_validate` | Structural + cross-section validation |
| `validate_fix` | `sdd_validate_fix` | Source-protected fix manifest |
| `review` | `sdd_review` | Multi-persona review |
| `remediate` | `sdd_remediate` | Deterministic findings + parsed review |
| `remediate_fix` | `sdd_remediate_fix` | Source-protected remediation fix |
| `consistency` | `sdd_consistency` | Artifact lineage check |
| `links` | `sdd_validate_links` | Markdown link check |
| `prescreen` | `sdd_prescreen` | Remediation candidate scan |
| `score` | `sdd_score_show` | Quality score |

### Format Roles

| Format | Role | Audience |
|--------|------|----------|
| `.json` | Machine-readable full report | Tools, pipelines |
| `.md` | Human-readable narrative | Developers, reviewers |
| `.txt` | One-page summary | Terminal, logs |

### Examples

| Report | Filename |
|--------|----------|
| BRD-03 validation | `BRD-03.ucx.validate.json` |
| BRD-03 review | `BRD-03.ucx.review.md` |
| BRD-03 remediation | `BRD-03.ucx.remediate.json` |
| Governance approval | `BRD-03.gov.approval.json` |
| Versioned review | `BRD-03.ucx.review.v002.md` |

## Derived Copy Naming

Source-protected copies use underscores:

Format: `{DOC-ID}_{slug}_{STAGE}_copy.{ext}`

| Copy | Filename |
|------|----------|
| Validation | `BRD-03_security_compliance_validate_copy.yaml` |
| Remediation | `BRD-03_security_compliance_remediate_copy.yaml` |

## Versioned Reports

Format: `{DOC-ID}.{STAGE}.v{NNN}.{FORMAT}`

Default: no version (latest overwrites). Version suffix with `--keep-history`.

## Detection Patterns

```python
import re

REPORT_PATTERN = re.compile(
    r"^[A-Z]+-\d+\."
    r"(?:ucx|gov|kb)\."
    r"(?:validate|validate_fix|review|remediate|remediate_fix|"
    r"consistency|links|prescreen|score)"
    r"(?:\.v\d+)?"
    r"\.(?:json|md|txt)$"
)

DERIVED_COPY_PATTERN = re.compile(
    r"^[A-Z]+-\d+_.+_(?:validate|remediate)_copy\.(?:md|yaml|yml)$"
)

SOURCE_PATTERN = re.compile(
    r"^[A-Z]+-\d+_.+\.(?:md|yaml|yml)$"
)
```

## Reference

- [ID_NAMING_STANDARDS.md](ID_NAMING_STANDARDS.md) -- document and element ID formats
- [PLAN-021](../mcp_sdd/docs/plans/PLAN-021_sdd_reporting_naming_standard.md) -- implementation plan
