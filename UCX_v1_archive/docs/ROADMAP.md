# UCX Roadmap

## Overview

This roadmap outlines planned features and improvements for UCX (Unified Context Framework).

**Current Version**: 1.21.7
**Latest Patch**: 1.21.7 (PRD fixer coverage expansion and LLM handoff alignment)
**Next Minor**: 1.22.0 (PRD derived-artifact flow, EARS parity, and remediation hardening follow-up)
**Next Major**: 2.0.0

Versioning policy:

- Use one source tree rooted at `UCX/`; do not create versioned folders such as `UCX.2.0.0/`
- Use semantic versioning for all release decisions
- Use release branches only for parallel maintenance, not for version-specific source layouts
- Treat PLAN-012 workflow enforcement as `v2.0.0` scope unless backward-compatibility shims are added

---

## Version Timeline

```text
v1.12.0 ──► v1.13.x ──► v1.14.x ──► v1.15.x ──► v1.16.x ──► v1.17.0 ──► v1.18.0 ──► v1.19.0 ──► v1.20.0 ──► v1.21.x (Current) ──► v1.22.0 ──► v2.0.0
  │           │            │            │           │            │           │            │           │          │                    │           │
  │           │            │            │           │            │           │            │           │          │                    │           └─► Breaking changes
  │           │            │            │           │            │           │            │           │          │                    └─► PRD derived-artifact flow + EARS parity + hardening follow-up
  │           │            │            │           │            │           │            │           │          ├─► v1.21.7: PRD fixer coverage + LLM handoff alignment
  │           │            │            │           │            │           │            │           │          ├─► v1.21.6: Validation source protection + report-only
  │           │            │            │           │            │           │            │           │          │
  │           │            │            │           │            │           │            │           │          └─► v1.21.5: Preflight robustness (ISO date fallback)
  │           │            │            │           │            │           │            │           └─► v1.21.4: Canonical reports + source protection
  │           │            │            │           │            │           │            └─► Hash-based Finding IDs (PLAN-008)
   │           │            │            │           │            │           └─► Layer Action Handoff System
   │           │            │            │           │            └─► Fixer-to-LLM hand-off
   │           │            │            │           └─► Duplicate fixer guardrails (v1.16.2)
   │           │            │            └─► Extended auto-fix (21 codes)
   │           │            └─► Prompt Inspection, attention steering (v1.14.0-8)
   │           └─► Context Engineering (v1.13.0, v1.13.1)
   └─► Category-Weighted Scoring
```

---

## Planned Releases

### v1.22.0 - PRD Derived-Artifact Flow, EARS Parity, and Hardening Follow-Up

**Status**: Planned
**ETA**: Q3 2026

**Features**:

| Feature | Description | Status |
| --- | --- | --- |
| PRD Derived-Artifact Flow | Introduce immutable-source PRD workflow with `PRD-01_validation_report.md`, `_validation`, and `_remediated` artifacts | Planned |
| PRD Artifact Consistency Checks | Keep pre-commit limited to artifact availability and lineage consistency checks without rerunning validation logic | Planned |
| EARS Validators | Complete EARS validation parity module and quality gates | Planned |
| Remediation Safety Telemetry | Optional visibility for restored source files during generation | Planned |
| Reporting Consistency | Align PLAN-009/010/011 and user guides with PRD stage-aware artifact naming and lineage semantics | Planned |

---

### v1.20.0 - PRD/EARS Validation Parity

**Status**: In Progress (PRD complete, EARS carried forward)
**ETA**: Q3 2026

**Features**:

| Feature | Description | Status |
| --- | --- | --- |
| PRD Validators | Full PRD validation parity with BRD | ✅ Complete (PLAN-010) |
| PRD Creation | Enhanced PRD generation with 21-section template | ✅ Complete (PLAN-009) |
| EARS Validators | EARS syntax and requirement validation | Planned |
| Unified Quality Gates | Consistent gates across Layer 1-3 | Planned |

**Deliverables**:

- [x] `ucx/validators/prd/` module (10 files)
- [x] `ucx/creation/UCC_PROMPT_PRD.md` (full rewrite)
- [x] `ucx/review/UCR_PROMPT_PRD.md` (updated for dual scoring)
- [x] PRD/EARS quality gate scripts
- [x] Pre-commit hooks for PRD (in projects)
- [ ] `ucx/validators/ears/` module
- [ ] EARS quality gate scripts

---

### v2.0.0 - Breaking Changes Release

**Status**: Future
**ETA**: Q3 2026

**Release Strategy**:

- Keep the existing `UCX/` root and package name `ucx`
- Ship `v2.0.0` as a tagged release, not as a new source folder
- Create `release/1.x` only if post-v2 patch support is needed for legacy users
- Publish `docs/MIGRATION_v2.md` before release

**Breaking Changes**:

| Change | Migration Path |
| --- | --- |
| Enforce `_validation` PRD input for remediation flow | Use `ucx validate-fix prd` before `ucx review` / `ucx remediate` |
| Enforce UCX review-report contract for PRD remediation | Use versioned `*.UCX_review_report_vNNN.md` review reports |
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

### v1.21.7 (2026-03-22)

**Status**: Released
**Type**: Patch (PRD Fixer Coverage and Handoff Alignment)

**Features**:
- Added deterministic PRD fixer coverage for `PRD-W006`, `PRD-W011`, `PRD-W012`, `PRD-W019`, `PRD-W021`
- Added PRD LLM-only handoff routing for `PRD-W004`, `PRD-W009`, `PRD-W013`, `PRD-W014`
- Updated Section 14 launch-criteria fix template to avoid invalid `PRD.NN.14.xx` IDs

See [CHANGELOG_v1.21.7](CHANGELOG/CHANGELOG_v1.21.7.md)

---

### v1.21.4 (2026-03-20)

**Features**:
- Canonical remediation consolidation to a single UCX report artifact (`UCX_remediation_report_vNNN`)
- Remediation source protection: UCRem snapshots source docs and restores unexpected mutations during report generation
- `ucx ai probe` command with epoch-based preflight checks and optional full-output diagnostics
- Creation audit report generation on every `ucx create` run (`UCX_creation_report_vNNN`)
- PRD creation runtime controls (`UCX_UPSTREAM_SECTION_CHARS`, `UCX_UPSTREAM_TOTAL_CHARS`, `UCX_PRD_LLM_AUDIT_COPY`)

See [CHANGELOG_v1.21.4](CHANGELOG/CHANGELOG_v1.21.4.md)

---

### v1.21.5 (2026-03-21)

**Status**: Released
**Type**: Patch (Robustness & Reliability)

**Features**:
- **AI Preflight Probe Robustness**: Added ISO date fallback mechanism for LLM date validation
- **Formatting Drift Tolerance**: Handles responses where ISO date is correct but epoch token is malformed
- **Two-Stage Validation**: Primary epoch extraction + ISO date search as fallback
- **Confidence Preference**: Prefers expected date if found in ISO matches; uses first valid date as secondary fallback

**Problem Solved**:
LLM providers (especially Claude) occasionally return responses with correct ISO date (YYYY-MM-DD) in prose text but inconsistent/malformed epoch unix timestamp. Example: "2026-03-21" in text but epoch token `1774252800` = 2026-03-23. Preflight now accepts the logical date instead of raising false-negative errors.

**Code Changes**:
- New method: `CLIClient._extract_iso_utc_date(text, expected_date=None)` for YYYY-MM-DD pattern extraction
- Modified: `_run_availability_preflight()` Phase 3 logic to implement two-stage validation
- New test: `test_preflight_accepts_iso_date_when_epoch_is_inconsistent()` with regression coverage

**Impact**:
- ✅ Zero breaking changes (backward compatible)
- ✅ All 24 preflight tests passing
- ✅ Reduces false-negative preflight failures in remediation/review/creation workflows
- ✅ Safety preserved: ISO fallback only activates when epoch fails; must parse as valid date

**Validation**:
- 24 preflight unit tests passing (including new regression test)
- Live remediation tested with Claude CLI: Preflight passed via ISO fallback, source protection confirmed
- Integration tests passing across all provider backends

See [CHANGELOG_v1.21.5](CHANGELOG/CHANGELOG_v1.21.5.md)

---

### v1.21.4 (2026-03-20)

**Features**:
- **Hash-Based Finding IDs**: Content-addressable finding IDs (`P1-a7f3` format) replacing sequential IDs (`REM-P1-001`)
- **Hash-Based Action IDs**: Content-addressable action IDs (`ACT-a7f3` format) replacing sequential IDs (`ACT-001`)
- New `FindingIDGenerator` and `ActionIDGenerator` classes in `ucx/utils/finding_hash.py`
- `CategoryConflictResolver.resolve_with_id()` method for combined category resolution and ID generation
- Dual-format pattern support for backward compatibility
- 39 new unit tests for hash module

**Benefits**:
| Benefit | Description |
|---------|-------------|
| Stateless | No counter synchronization across 11+ personas |
| Deterministic | Same content always produces same ID |
| Deduplication | Identical findings = identical hashes |
| Stable Tracking | Same finding tracks across report versions |

See [CHANGELOG_v1.19.0](CHANGELOG_v1.19.0.md) and [PLAN-008](plans/PLAN-008_hash_based_finding_ids.md)

---

### v1.18.0 (2026-03-17)

**Features**:
- **Layer Action Handoff System**: Capture out-of-scope items as ACTIONS that handoff to downstream layers (PRD, EARS, BDD, ADR, CTR) without penalizing BRD score
- New scripts: `extract_actions.py` and `validate_actions.py` for action processing
- ACTION format with fields: ACTION_ID, TYPE, TARGET, PRIORITY, SOURCE, PERSONA, CONTEXT, REQUIREMENT
- Actions Manifest section in Chairperson output
- Support for future action types (INFORM, REVIEW, DEFER) - currently only HANDOFF implemented
- Updated all 11 review personas to create ACTIONS for out-of-scope items instead of P0/P1/P2 findings
- Score calculation explicitly excludes ACTIONS (0 score impact)

**Bug Fixes**:
- BRD scores no longer penalized for technical/product details that belong in downstream layers

See [CHANGELOG_v1.18.0](CHANGELOG_v1.18.0.md) and [PLAN-007](plans/PLAN-007_layer_notice_handoff.md)

---

### v1.17.0 (2026-03-15)

**Features**:
- **Fixer-to-LLM Hand-off System**: Seamless hand-off between script-based fixer and LLM remediation
- **Always-Fix Validation**: Validation now ALWAYS fixes by default (no `--fix` flag needed)
- **New `--no-fix` Flag**: Opt out of automatic fixing
- **FixerContext Dataclass**: Tracks fixed/partial/skipped issues with session metadata
- **Section 7 "Fixer Session Summary"**: New validation report section with embedded JSON context
- **LLM_COMPLETION Markers**: HTML comments inserted for partial fixes needing LLM completion
- **New `ucx clean-markers` Command**: Remove markers after remediation is complete
- **UCRem Integration**: Reads fixer context and injects "FIXER HAND-OFF CONTEXT" into prompts
- **Persona Updates**: All 6 fixer personas updated with hand-off protocol

**Breaking Changes**:
| Change | Migration Path |
|--------|----------------|
| `--fix` now default | Remove `--fix` from scripts and CI/CD pipelines |
| Pre-commit hooks | Add `--no-fix` to pre-commit validation (staging conflicts) |

**Code Classifications**:
| Category | Codes | Behavior |
|----------|-------|----------|
| LLM_COMPLETION | GATE-E010, BRD-W011/12, DIAG-E001, FWDREF-E001 | Script does partial fix, LLM completes |
| LLM_ONLY | CONTENT-E001, LOGIC-E001, TRACE-E001 | Only LLM can handle (semantic issues) |

See [CHANGELOG_v1.17.0](CHANGELOG_v1.17.0.md) and [PLAN-006](plans/PLAN-006_fixer_to_llm_handoff.md)

---

### v1.16.2 (2026-03-15)

**Features**:
- **Duplicate Fixer Guardrails**: Prevents circular renames in GATE-E008 fixer
- **Backtick Reference Detection**: `BRD.XX.XX.XX` now detected as references
- **Historical Report Protection**: Fixer no longer modifies audit/review reports
- **Reference Logic Sync**: `element_codes.py` and `duplicate_fixer.py` synchronized

**Bug Fixes**:
- Fixed: Circular rename loops when running `ucx validate --fix`
- Fixed: Backtick-wrapped IDs incorrectly treated as definitions
- Fixed: Historical reports corrupted by reference updates

---

### v1.16.1 (2026-03-15)

**Features**:
- **Single-File Validation Reports**: Changed from versioned to single-file approach
  - Old: `{doc_id}.V_validation_report_v{NNN}.md`
  - New: `.precommit_validation_report.md`
- Single file overwrites on each run (no version accumulation)
- `--clean-reports` flag cleans legacy versioned reports
- Updated patterns in validators to recognize new filename

See [CHANGELOG_v1.16.1](CHANGELOG_v1.16.1.md)

### v1.16.0 (2026-03-15)

**Features**:
- **Auto-Detection of Latest Review Report**: `ucx remediate` auto-detects latest UCR report
- No need to specify exact report version
- New `--report` / `-r` flag for explicit override
- New utilities: `find_latest_review_report()`, `find_latest_remediation_report()`
- API change: `UCRemPhase.generate_fixes(doc_path, review_report=None)`

See [CHANGELOG_v1.16.0](CHANGELOG_v1.16.0.md)

### v1.15.x (2026-03-14)

**Features**:
- v1.15.6: Chairperson findings extraction fix
- v1.15.5: Persona prompts as default review mode
- v1.15.4: BRD-E002 invalid value fixer, GATE-E001 recursion fix
- v1.15.3: BRD-E002, BRD-E009, GATE-E008 auto-fix improvements
- v1.15.2: Extended auto-fix suite (21 codes)
- v1.15.1: BRD-E020 invalid type code fixer
- v1.15.0: Extended auto-fix suite (17 codes)

### v1.14.8 (2026-03-14)

**Features**:
- **Terminology Update**: Renamed review modes for clarity
  - "One-turn" → "Unified Prompt"
  - "Multi-turn" → "Persona Prompts"
- **CLI Flag Changes**: Updated flags to match new terminology
  - `--multi-turn` / `-m` → `--persona` / `-p`
  - `--force-single` → `--unified` / `-u`
- Updated documentation, code comments, and file naming

**Terminology Reference**:
| Old Term | New Term | Description |
|----------|----------|-------------|
| One-turn | Unified Prompt | Single prompt with all 12 personas |
| Multi-turn | Persona Prompts | Per-persona filtered prompts |

**CLI Reference**:
| Old Flag | New Flag | Description |
|----------|----------|-------------|
| `--multi-turn` / `-m` | `--persona` / `-p` | Use persona prompts mode |
| `--force-single` | `--unified` / `-u` | Force unified prompt mode |

See [CHANGELOG_v1.14.8](CHANGELOG_v1.14.8.md)

### v1.14.7 (2026-03-14)

**Features**:
- **Attention Steering Fix**: Format instructions now placed at END of prompt (was at START)
- **New API Method**: `_load_format_instructions()` in UCRPhase
- **New File Pattern**: `UCR_FORMAT_{TYPE}_PROJECT.md` for format instructions

**Prompt Structure Change**:
| Position | Before | After |
|----------|--------|-------|
| Format Instructions | START (before document) | END (after document) |
| Inspection Result | ⚠ at START | ✓ at END |

See [CHANGELOG_v1.14.7](CHANGELOG_v1.14.7.md)

### v1.14.6 (2026-03-14)

**Features**:
- **Session Directory Rename**: `.doc_review_memory/` → `.ucx_review_session/` for clarity
- **Assembled Report Rename**: `final_body.md` → `assembled_report.md` for clarity
- **Review Mode Documentation**: Added comprehensive One-Turn vs Multi-Turn comparison

**Breaking Changes**:
| Old | New | Migration |
|-----|-----|-----------|
| `.doc_review_memory/` | `.ucx_review_session/` | Rename or delete existing directories |
| `final_body.md` | `assembled_report.md` | Automatic on next review |

**Documentation Updates**:
- `UNIFIED_CONTEXT_REVIEW.md`: Added "Review Modes: Unified vs Persona" section
- `README.md`: Added review mode comparison table and recommendations

See [CHANGELOG_v1.14.6](CHANGELOG_v1.14.6.md)

### v1.14.5 (2026-03-14)

**Features**:
- **Unified Prompt Feature Parity**: Unified prompt review now has full feature parity with persona prompts
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
- Persona prompts review mode (`--persona`)
- Session persistence and resume (`--resume`)
- Large document handling (auto-splits >100K chars)
- Review memory in `.ucx_review_session/`

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
| Unified Prompt Feature Parity | High | ✅ Complete (v1.14.5) | PLAN-005 |
| Persona Naming Standardization | High | ✅ Complete (v1.14.5) | PLAN-005 |
| Session Directory Rename | Medium | ✅ Complete (v1.14.6) | Clarity improvement |
| Review Mode Documentation | Medium | ✅ Complete (v1.14.6) | Unified vs persona prompts |
| Attention Steering Fix | High | ✅ Complete (v1.14.7) | Format instructions at END |
| Terminology Update | Medium | ✅ Complete (v1.14.8) | Unified prompt / Persona prompts |
| Extended Auto-Fix Suite | High | ✅ Complete (v1.15.x) | 21 auto-fixable error codes |
| Auto-Detect Review Report | High | ✅ Complete (v1.16.0) | Remediation workflow improvement |
| Single-File Validation | Medium | ✅ Complete (v1.16.1) | Cleaner validation reports |
| Fixer-to-LLM Hand-off | High | ✅ Complete (v1.17.0) | PLAN-006 |
| Layer Action Handoff | High | ✅ Complete (v1.18.0) | PLAN-007 |
| Hash-Based Finding IDs | High | ✅ Complete (v1.19.0) | PLAN-008 |
| Multi-Document Validation | High | Planned (v1.20.0) | After hash IDs |
| PRD validation parity | Medium | Planned (v1.21.0) | After multi-doc |
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
- [CHANGELOG_v1.14.6.md](CHANGELOG_v1.14.6.md) - Session directory rename, review mode documentation
- [CHANGELOG_v1.14.7.md](CHANGELOG_v1.14.7.md) - Attention steering fix (format instructions at END)
- [CHANGELOG_v1.14.8.md](CHANGELOG_v1.14.8.md) - Terminology update (unified prompt / persona prompts)
- [CHANGELOG_v1.16.0.md](CHANGELOG_v1.16.0.md) - Auto-detection of latest review report
- [CHANGELOG_v1.16.1.md](CHANGELOG_v1.16.1.md) - Single-file validation reports
- [CHANGELOG_v1.17.0.md](CHANGELOG_v1.17.0.md) - Fixer-to-LLM hand-off system
- [PLAN-006: Fixer-to-LLM Hand-off](plans/PLAN-006_fixer_to_llm_handoff.md) - Complete
- [CHANGELOG_v1.18.0.md](CHANGELOG_v1.18.0.md) - Layer Action Handoff System
- [PLAN-007: Layer Action Handoff](plans/PLAN-007_layer_notice_handoff.md) - Complete
- [CHANGELOG_v1.19.0.md](CHANGELOG_v1.19.0.md) - Hash-Based Finding IDs
- [PLAN-008: Hash-Based Finding IDs](plans/PLAN-008_hash_based_finding_ids.md) - Complete

---

*Last Updated: 2026-03-18*
