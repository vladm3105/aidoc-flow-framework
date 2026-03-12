# UCX Roadmap

## Overview

This roadmap outlines planned features and improvements for UCX (Unified Context Framework).

**Current Version**: 1.11.1
**Next Major**: 1.12.0 (Category-Weighted Scoring)

---

## Version Timeline

```
v1.11.1 (Current) ──► v1.12.0 ──► v1.13.0 ──► v2.0.0
     │                   │           │           │
     │                   │           │           └─► Breaking changes
     │                   │           └─► Multi-type validation
     │                   └─► Category-Weighted Scoring
     └─► Scanner + Manifest
```

---

## Planned Releases

### v1.12.0 - Category-Weighted Scoring (Next)

**Status**: Planning
**ETA**: Q1 2026
**Plan**: [PLAN-002](/opt/data/docs_flow_framework/UCX/docs/plans/PLAN-002_category_weighted_scoring.md)

**Problem**: UCX review scoring produces inconsistent results due to:
- AI non-determinism in finding counts
- No per-category caps (scores go negative)
- Different scoring methodologies between versions

**Solution**: Category-weighted scoring system with:
- 8 categories mapped to element type codes (ID_NAMING_STANDARDS.md)
- Per-category weight and deduction caps
- Persona → Category mapping for expertise alignment
- Consistent methodology across all document types

**Key Features**:
| Feature | Description |
|---------|-------------|
| Scoring Module | `ucx.scoring` with calculator, categories, weights |
| Category Config | `scoring_weights.yaml` with per-doc-type variations |
| Chairperson Manifest | Category summary table in output |
| Scanner Integration | Category extraction and weighted score display |

**Deliverables**:
- [ ] `ucx/scoring/` module
- [ ] Chairperson prompt updates (all doc types)
- [ ] `ucx scan` category breakdown
- [ ] SCORING_GUIDE.md documentation
- [ ] Unit tests for scoring logic

---

### v1.13.0 - Multi-Document Validation

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

### v1.14.0 - PRD/EARS Validation Parity

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

### v1.11.1 (2026-03-12) - Current

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
| Category-weighted scoring | High | Planning (v1.12.0) | PLAN-002 |
| PRD validation parity | Medium | Planned (v1.14.0) | After scoring |
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
- [PLAN-002: Category-Weighted Scoring](plans/PLAN-002_category_weighted_scoring.md) - Planning
- [CHANGELOG_v1.11.0.md](CHANGELOG_v1.11.0.md) - Latest changes

---

*Last Updated: 2026-03-12*
