---
title: "REF-00: Reference Documents Index"
tags:
  - ref-index
  - layer-0-artifact
  - shared-architecture
  - index-document
custom_fields:
  document_type: index
  artifact_type: REF
  layer: 0
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  last_updated: "2026-02-16"
---

# REF-00: Reference Documents Index

## Purpose

Layer 0 contains **Reference Documents (REF)** - foundational materials that inform the SDD workflow but exist outside the formal artifact layers.

Reference documents include:
- Initial project documentation and business context
- External specifications and standards
- Research materials and analysis documents
- Legacy documentation for migration projects
- Domain knowledge and glossaries

## Layer Position

```
Layer 0: REF (Reference Documents) - Foundation/Input
    ↓
Layer 1: BRD (Business Requirements)
    ↓
Layer 2-12: SDD Workflow Artifacts
```

REF documents serve as **input sources** for BRD creation and may be referenced throughout the SDD workflow.

## Directory Contents

| Document | Description | Status |
|----------|-------------|--------|
| `REF-TEMPLATE.md` | Template for creating reference documents | Active |
| `BRD-REF-01_example.md` | Example reference document for BRD | Example |

## Naming Convention

Reference documents follow the pattern:

```
REF-NN_{descriptive_slug}.md
```

Or when associated with a specific artifact:

```
{ARTIFACT}-REF-NN_{descriptive_slug}.md
```

Examples:
- `REF-01_project_charter.md`
- `REF-02_market_analysis.md`
- `BRD-REF-01_stakeholder_interviews.md`
- `ADR-REF-01_technology_evaluation.md`

## Usage Guidelines

### When to Create REF Documents

1. **Project Initiation**: Capture initial business context, stakeholder input
2. **External Sources**: Document external specifications, standards, APIs
3. **Research**: Record technology evaluations, market analysis
4. **Migration**: Preserve legacy documentation for reference

### REF Document Requirements

| Requirement | Description |
|-------------|-------------|
| Frontmatter | YAML frontmatter with standard tags |
| Traceability | Link to consuming artifacts (BRD, ADR, etc.) |
| Source Attribution | Document original source and date |
| Version Control | Track document revisions |

### Relationship to BRD

REF documents are the primary **upstream source** for BRD documents:

```
REF-01 (Business Context)  
REF-02 (Market Analysis)   → BRD-01 (Business Requirements)
REF-03 (Stakeholder Input) 
```

## RAG Integration

REF documents are indexed by Haystack RAG service with:
- `layer: 0`
- `doc_type: REF`

Query example:
```bash
curl -X POST http://localhost:1416/query \
  -d '{"query": "business context", "filters": {"layer": {"$eq": 0}}}'
```

## Related Documentation

- [BRD Index](../01_BRD/BRD-00_index.md) - Business Requirements (Layer 1)
- [ID Naming Standards](../ID_NAMING_STANDARDS.md) - Naming conventions
- [Traceability Guide](../TRACEABILITY.md) - Cross-references
