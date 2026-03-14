# UCX Roadmap

## Overview

This roadmap outlines planned features and improvements for UCX (Unified Context Framework).

**Current Version**: 1.14.5
**Next Major**: 1.15.0 (Multi-Document Validation)

---

## Version Timeline

```
v1.12.0 ──► v1.13.x ──► v1.14.x ──► v1.14.5 (Current) ──► v1.15.0 ──► v2.0.0
   │           │            │              │                  │           │
   │           │            │              │                  │           └─► Breaking changes
   │           │            │              │                  └─► Multi-document validation
   │           │            │              └─► One-turn feature parity + naming standardization
   │           │            └─► Prompt Inspection (v1.14.0-4), qa_lead, chaos_engineer
   │           └─► Context Engineering (v1.13.0, v1.13.1)
   └─► Category-Weighted Scoring
```

---

## Planned Releases

### v1.15.0 - Multi-Document Validation

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

### v1.16.0 - PRD/EARS Validation Parity

**Status**: Planned
**ETA**: Q3 2026

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

### v1.14.5 (2026-03-14) - Current

**Features**:
- **One-Turn Review Feature Parity**: One-turn review now has full feature parity with multi-turn
- **Project-First Skill Loading**: `_load_skills()` now prioritizes project-specific skills over framework skills
- **Persona Naming Standardization**: Renamed `integration_expert` → `integration_lead` for consistency
- **Category Tagging**: Added `[CAT:xxx]` tagging to auditor, fact_checker, product_owner personas
- **Settings Fix**: Fixed `get_skill_dir()` to use correct `/UCX/skills/` path

**Changes**:
| Change | Description |
|--------|-------------|
| `_load_skills()` | Project skills (`docs/UCX/skills/`) take priority over framework skills |
| `integration_expert` → `integration_lead` | Consistent persona/skill naming across codebase |
| `get_skill_dir()` | Returns `/UCX/skills/` instead of deprecated `ucx/skills/personas/` |
| Category Tagging | 3 personas updated with `[CAT:xxx]` tags for weighted scoring |

**Naming Audit**: Verified all 14 personas match their skill filenames exactly.

See [CHANGELOG_v1.14.5](CHANGELOG_v1.14.5.md)

### v1.14.4 (2026-03-14)

**Features**:
- **Extraction Pattern Fixes**: Fixed 5 old patterns that truncated at `###` headers
- **15 New Extraction Patterns**: Added patterns for all 12 personas
- **Instruction Token Target**: 11/12 personas at 5%+ ratio, all with 750+ instruction tokens

**Extraction Improvements**:
| Persona | Before | After | Key Additions |
|---------|--------|-------|---------------|
| auditor | 937 (4%) | 1,276 (5%) | Critical Compliance Gaps, Corridor Requirements |
| product_owner | 637 (3%) | 844 (5%) | MVP Boundaries, User Journey Checkpoints |
| fact_checker | 907 (3%) | 1,151 (3%) | False Positive Categories, Verification Verdicts |
| architect | 574 (3%) | 781 (5%) | Nested section capture fixed |

**Quality Metrics**: Primary metric is absolute instruction token count (750+ tokens), ratio (5-10%) is secondary.

See [CHANGELOG_v1.14.4](CHANGELOG_v1.14.4.md) and [PLAN-005](plans/PLAN-005_prompt_engineering_toolset.md)

### v1.14.3 (2026-03-14)

**Features**:
- **New Persona: qa_lead**: QA Lead for testability, BDD/Gherkin standards, test coverage (prefix: QA)
- **Renamed Persona**: `devils_advocate` → `chaos_engineer` (prefix: CE) for industry alignment
- **9 New Extraction Patterns**: BDD Standards, Test Coverage, Testability Checklist, Quality Metrics

**Persona Changes**:
| Change | Old | New |
|--------|-----|-----|
| Added | - | `qa_lead` (QA) |
| Renamed | `devils_advocate` (DA) | `chaos_engineer` (CE) |

**Total Personas**: 12 (was 11)

See [CHANGELOG_v1.14.3](CHANGELOG_v1.14.3.md) and [PLAN-005](plans/PLAN-005_prompt_engineering_toolset.md)

### v1.14.2 (2026-03-14)

**Features**:
- **Enhanced Skill Extraction**: 27 extraction patterns covering all 11 personas
- **Persona-Specific Patterns**: Domain knowledge extraction per persona role
- **Instruction Ratio**: Improved across all personas (target 5-10% achieved)

**Improvements by Persona**:
| Persona | Ratio | Improvement | Key Sections Extracted |
|---------|-------|-------------|------------------------|
| chairperson | 5.6% | +512% | Core Mission, Score Calculation, Synthesis Process |
| chaos_engineer | 7.8% | +185% | Failure Scenarios, Edge Cases, Critical Rules |
| business_analyst | 4.9% | +143% | Business Processes, Stakeholders, 5 C's Framework |
| strategist | 5.4% | +136% | Business Model, Competitive Landscape, Financials |
| integration_lead | 8.0% | +127% | Partner Ecosystem, Integration Requirements |
| fact_checker | 2.6% | +102% | Verification Areas, Verification Process |
| product_owner | 3.4% | +95% | MVP Definition, Acceptance Criteria |
| operator | 8.2% | +86% | Operational Requirements, Operational Checklist |
| tech_lead | 6.9% | +58% | Technology Stack, Technical Assessment |

See [CHANGELOG_v1.14.2](CHANGELOG_v1.14.2.md) and [PLAN-005](plans/PLAN-005_prompt_engineering_toolset.md)

### v1.14.1 (2026-03-13)

**Features**:
- **Prompt Quality Improvements**: Content preprocessing for cleaner prompts
- **Content Preprocessing**: Strip YAML frontmatter, HTML comments, navigation breadcrumbs, document metadata
- **System Instructions**: Load persona skills from skill manifests with project-specific overrides
- **Section Sorting**: Numeric ordering (BRD-01.1, BRD-01.5, BRD-01.11) instead of alphabetical
- **Anti-Pattern Extraction**: Fixed regex for extracting skill sections into prompts
- **Project Templates**: Support for `docs/UCX/skills/` project-specific persona customization
- **Token Optimization**: ~455 tokens saved per prompt through metadata stripping

See [CHANGELOG_v1.14.1](CHANGELOG_v1.14.1.md) and [PLAN-005](plans/PLAN-005_prompt_engineering_toolset.md)

### v1.14.0 (2026-03-13)

**Features**:
- **Prompt Inspection Toolset**: Pre-LLM analysis of generated prompts
- **CLI Commands**: `ucx prompt tokens/sections/inspect/check/generate`
- **UCPromptPhase API**: Programmatic access to all inspection features
- **Token Analysis**: Per-persona token breakdown with budget tracking
- **Section Matrix**: Visual matrix of section inclusion per persona
- **Prompt Inspector**: Structure analysis with attention steering detection
- **Metadata Files**: `.meta.json` files alongside generated prompts

**Code Review**: Passed (P0=0, P1=4 fixed, P2=3 fixed, 5 deferred)

See [CHANGELOG_v1.14.0](CHANGELOG_v1.14.0.md) and [PLAN-005](plans/PLAN-005_prompt_engineering_toolset.md)

### v1.13.1 (2026-03-13)

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
| Prompt Inspection Toolset | High | ✅ Complete (v1.14.0) | PLAN-005 |
| Prompt Quality Improvements | High | ✅ Complete (v1.14.1) | PLAN-005 |
| Enhanced Skill Extraction | High | ✅ Complete (v1.14.2) | PLAN-005 |
| QA Lead Persona | High | ✅ Complete (v1.14.3) | PLAN-005 |
| Chaos Engineer Rename | High | ✅ Complete (v1.14.3) | PLAN-005 |
| Extraction Pattern Fixes | High | ✅ Complete (v1.14.4) | PLAN-005 |
| One-Turn Feature Parity | High | ✅ Complete (v1.14.5) | PLAN-005 |
| Persona Naming Standardization | High | ✅ Complete (v1.14.5) | PLAN-005 |
| Multi-Document Validation | High | Planned (v1.15.0) | PLAN-006 |
| PRD validation parity | Medium | Planned (v1.16.0) | After multi-doc |
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
- [PLAN-005: Prompt Inspection Toolset](plans/PLAN-005_prompt_engineering_toolset.md) - Complete
- [CHANGELOG_v1.12.0.md](CHANGELOG_v1.12.0.md) - Category-weighted scoring
- [CHANGELOG_v1.13.0.md](CHANGELOG_v1.13.0.md) - Context engineering & Finding ID
- [CHANGELOG_v1.13.1.md](CHANGELOG_v1.13.1.md) - Advanced context engineering
- [CHANGELOG_v1.14.0.md](CHANGELOG_v1.14.0.md) - Prompt inspection toolset
- [CHANGELOG_v1.14.1.md](CHANGELOG_v1.14.1.md) - Prompt quality improvements
- [CHANGELOG_v1.14.2.md](CHANGELOG_v1.14.2.md) - Enhanced skill extraction
- [CHANGELOG_v1.14.3.md](CHANGELOG_v1.14.3.md) - QA Lead persona, Chaos Engineer rename
- [CHANGELOG_v1.14.4.md](CHANGELOG_v1.14.4.md) - Extraction pattern fixes, 15 new patterns
- [CHANGELOG_v1.14.5.md](CHANGELOG_v1.14.5.md) - One-turn feature parity, persona naming standardization

---

*Last Updated: 2026-03-14*
