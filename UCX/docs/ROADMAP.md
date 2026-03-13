# UCX Roadmap

## Overview

This roadmap outlines planned features and improvements for UCX (Unified Context Framework).

**Current Version**: 1.13.1
**Next Major**: 1.14.0 (Multi-Document Validation)

---

## Version Timeline

```
v1.12.0 ──► v1.13.0 ──► v1.13.1 (Current) ──► v1.14.0 ──► v2.0.0
   │           │            │                    │           │
   │           │            │                    │           └─► Breaking changes
   │           │            │                    └─► Multi-document validation
   │           │            └─► Advanced Context Engineering
   │           └─► Context Engineering + Finding ID
   └─► Category-Weighted Scoring
```

---

## Planned Releases

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

### v1.13.1 (2026-03-13) - Current

**Features**:
- **Advanced Context Engineering**: Completes deferred features from v1.13.0
- **Hybrid Keyword Scan**: `RelevantSnippet`, `_scan_other_sections_for_keywords()` for discovering relevant content in non-mapped sections
- **Appendix-on-Demand**: `AppendixInfo`, `_build_appendix_index()` for lightweight appendix metadata (~500 tokens vs 20-50K)
- **Dynamic Section Mapping**: `SECTION_CATEGORIES`, `DynamicSectionMapper` for semantic category-based filtering across document types
- **VERIFY Tag Pattern**: `[VERIFY: appendix-id]` for post-processing verification
- **AppendixVerifier**: Validates findings against actual appendix content
- See [CHANGELOG_v1.13.1](CHANGELOG_v1.13.1.md) and [PLAN-004](plans/PLAN-004_advanced_context_engineering.md)

### v1.13.0 (2026-03-13)

**Features**:
- **Context Engineering & Finding ID Standardization**: Core context engineering system
- Canonical Finding ID format: `PREFIX-P0-NNN` (e.g., `ARCH-P0-001`)
- Context engineering reduces prompts from 170KB to ~60-80KB
- Attention steering places format instructions at prompt END
- Prior findings summarization (90% token reduction)
- Hierarchical document context (4-level structure)
- Chairperson manifest validation
- See [CHANGELOG_v1.13.0](CHANGELOG_v1.13.0.md) and [PLAN-003](plans/PLAN-003_persona_prompt_restructuring.md)

### v1.12.0 (2026-03-12)

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
| Context Engineering | High | ✅ Complete (v1.13.0) | PLAN-003 |
| Finding ID Standardization | High | ✅ Complete (v1.13.0) | PLAN-003 |
| Advanced Context Engineering | High | ✅ Complete (v1.13.1) | PLAN-004 |
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
- [PLAN-003: Persona Prompt Restructuring](plans/PLAN-003_persona_prompt_restructuring.md) - Complete
- [PLAN-004: Advanced Context Engineering](plans/PLAN-004_advanced_context_engineering.md) - Complete
- [CHANGELOG_v1.12.0.md](CHANGELOG_v1.12.0.md) - Category-weighted scoring
- [CHANGELOG_v1.13.0.md](CHANGELOG_v1.13.0.md) - Context engineering & Finding ID
- [CHANGELOG_v1.13.1.md](CHANGELOG_v1.13.1.md) - Advanced context engineering

---

*Last Updated: 2026-03-13*
