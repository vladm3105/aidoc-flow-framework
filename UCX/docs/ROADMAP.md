# UCX Roadmap

## Overview

This roadmap outlines planned features and improvements for UCX (Unified Context Framework).

**Current Version**: 1.12.0
**Next Major**: 1.13.0 (Context Engineering & Finding ID Standardization)

---

## Version Timeline

```
v1.12.0 (Current) ──► v1.13.0 ──► v1.14.0 ──► v2.0.0
     │                   │           │           │
     │                   │           │           └─► Breaking changes
     │                   │           └─► Multi-document validation
     │                   └─► Context Engineering + Finding ID
     └─► Category-Weighted Scoring
```

---

## Planned Releases

### v1.13.0 - Context Engineering & Finding ID Standardization (Next)

**Status**: In Progress (Core Complete)
**ETA**: Q1 2026
**Plan**: [PLAN-003](/opt/data/docs_flow_framework/UCX/docs/plans/PLAN-003_persona_prompt_restructuring.md)

**Problem**: UCX review outputs are unreliable due to:
- Finding extraction regex mismatch (shows 0 findings when 30+ exist)
- Prompt size explosion (170KB+) causing LLM to ignore format instructions
- Inconsistent Finding ID formats across personas
- Missing Chairperson manifest markers

**Solution**: Context engineering with canonical Finding ID format:
- **Unified Finding ID Format**: `PREFIX-P0-NNN` (e.g., `ARCH-P0-001`)
- **Attention Steering**: Format instructions at END of prompt
- **Hierarchical Context**: 3-level document filtering (Overview/Relevant/Reference)
- **Prior Findings Summarization**: 90% reduction in prior context size

**Key Features**:
| Feature | Description |
|---------|-------------|
| `context_engine.py` | Hierarchical document context and prior findings summarization |
| `FINDING_ID_PATTERN` | Canonical regex for `PREFIX-P0-NNN` extraction |
| `PriorFindingsSummarizer` | Reduces 50K → 5K tokens (90% reduction) |
| `build_attention_steering_format()` | Format instructions at prompt END |
| Chairperson Manifest | `<!-- UCX-MANIFEST-START -->` markers guaranteed |

**Deliverables**:
- [x] `ucx/core/context_engine.py` module
- [x] Updated `_extract_findings()` with canonical pattern
- [x] Chairperson validation in `save_response()`
- [x] `build_persona_prompt()` with context engineering
- [x] Unit tests for finding extraction and context engine
- [x] UCR prompt updates (BRD/PRD) with Finding ID format
- [x] Skill file updates (chairperson.md, operator.md)
- [x] README documentation (v1.13.0 features)
- [ ] Integration testing with BRD-01 re-review

**Advanced Features** (Deferred to v1.13.1):
- [ ] `RelevantSnippet` dataclass for hybrid context
- [ ] `_scan_other_sections_for_keywords()` method
- [ ] `AppendixInfo` with on-demand loading
- [ ] `DynamicSectionMapper` for semantic category mapping

---

### v1.14.0 - Multi-Document Validation

**Status**: Planned
**ETA**: Q2 2026

**Features**:
| Feature | Description |
|---------|-------------|
| Corpus Validation | Validate entire `docs/` directory in one command |
| Cross-Document Traceability | Validate @ref: tags across document types |
| Dependency Graph | Build and validate document dependency tree |
| Batch Review | Review multiple documents with shared context |

**Deliverables**:
- [ ] `ucx validate --all` command
- [ ] Cross-document traceability validator
- [ ] Dependency graph visualization
- [ ] Batch review mode

---

### v1.15.0 - PRD/EARS Validation Parity

**Status**: Planned
**ETA**: Q2 2026

**Features**:
| Feature | Description |
|---------|-------------|
| PRD Validators | Full PRD validation parity with BRD |
| EARS Validators | EARS syntax and requirement validation |
| Unified Quality Gates | Consistent gates across Layer 1-3 |

**Deliverables**:
- [ ] `ucx/validators/prd/` module
- [ ] `ucx/validators/ears/` module
- [ ] PRD/EARS quality gate scripts
- [ ] Pre-commit hooks for PRD/EARS

---

### v2.0.0 - Breaking Changes Release

**Status**: Future
**ETA**: Q3 2026

**Breaking Changes**:
| Change | Migration Path |
|--------|----------------|
| Remove deprecated `doc-brd-validator` skill | Use `doc-brd-audit` |
| Remove deprecated `doc-brd-reviewer` skill | Use `doc-brd-audit` |
| Remove legacy scoring formula | Update to category-weighted |
| Require Python 3.12+ | Upgrade Python |
| Remove `--skip-validation` flag | Use `--no-validation` |

**New Features**:
- Full SPEC/TASKS/CTR validation
- Real-time review streaming
- Interactive fix application
- VS Code extension

---

## Completed Releases

### v1.12.0 (2026-03-12) - Current

**Features**:
- **Category-Weighted Scoring**: 8 scoring categories with per-category weights and caps
- Categories mapped to element type codes (ID_NAMING_STANDARDS.md)
- `ucx/scoring/` module with calculator, categories, weights
- Manifest includes category summary table
- See [CHANGELOG_v1.12.0](CHANGELOG_v1.12.0.md)

### v1.11.1 (2026-03-12)

**Features**:
- `ucx validate` generates report by default (like review)
- `--no-report` flag for console-only output
- Aligned validate/review behavior

### v1.11.0 (2026-03-12)

**Features**:
- Chairperson Manifest in UCR reports
- UCX Scanner (`ucx scan`) for pre-remediation analysis
- De-duplicated finding counts via manifest
- PRD-Ready Score extraction
- Smart fixer routing based on manifest

### v1.10.0 (2026-03-12)

**Features**:
- Multi-turn review mode (`--multi-turn`)
- Session persistence and resume (`--resume`)
- Large document handling (auto-splits >100K chars)
- Review memory in `.doc_review_memory/`

### v1.9.x (2026-03-09 to 2026-03-11)

**Features**:
- Unified BRD validation in UCX
- Pre-commit hook integration
- Tier 1/2/3 validation tiers
- Report generation for validation
- Web search mode (`--enable-web-search`)

---

## Feature Requests

| Request | Priority | Status | Notes |
|---------|----------|--------|-------|
| Context Engineering | High | In Progress (v1.13.0) | PLAN-003 |
| Finding ID Standardization | High | In Progress (v1.13.0) | PLAN-003 |
| PRD validation parity | Medium | Planned (v1.15.0) | After multi-doc |
| Interactive fix mode | Medium | Future (v2.0.0) | Requires TUI |
| VS Code extension | Low | Future | Post-v2.0.0 |
| Real-time streaming | Low | Future | Requires API mode changes |

---

## Contributing

To propose new features or changes:

1. Create a plan document in `docs/plans/PLAN-NNN_feature_name.md`
2. Follow the PLAN-001/PLAN-002 template
3. Submit for review

---

## References

- [PLAN-001: Unified BRD Validation](plans/PLAN-001_unified_brd_validation.md) - Complete
- [PLAN-002: Category-Weighted Scoring](plans/PLAN-002_category_weighted_scoring.md) - Complete
- [PLAN-003: Persona Prompt Restructuring](plans/PLAN-003_persona_prompt_restructuring.md) - In Progress
- [CHANGELOG_v1.12.0.md](CHANGELOG_v1.12.0.md) - Category-weighted scoring
- [CHANGELOG_v1.13.0.md](CHANGELOG_v1.13.0.md) - Context engineering (upcoming)

---

*Last Updated: 2026-03-13*
