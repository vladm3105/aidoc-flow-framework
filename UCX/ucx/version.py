"""Version information for UCX."""

__version__ = "1.19.0"
__version_info__ = tuple(int(x) for x in __version__.split(".")[:3])

# v1.19.0 - Hash-Based Finding and Action ID Generation
# - NEW: FindingIDGenerator class for content-addressable finding IDs
#   - Format: P{0-2}-{xxxx} (e.g., P1-a7f3) replaces REM-P1-001
#   - Stateless: no counter synchronization needed across 11+ personas
#   - Deterministic: same content always produces same ID
#   - Natural deduplication: identical findings = identical hashes
# - NEW: ActionIDGenerator class for content-addressable action IDs
#   - Format: ACT-{xxxx} (e.g., ACT-b2c1) replaces ACT-001
# - NEW: FindingIdentity and ActionIdentity dataclasses
#   - Encapsulate hash input components (file, section, category, description)
# - NEW: CategoryConflictResolver.resolve_with_id() method
#   - Combined category resolution and hash-based ID generation
# - NEW: Dual-format pattern support (transition period)
#   - Accepts both legacy (REM-P1-001) and hash (P1-a7f3) formats
#   - is_legacy_finding_id(), is_hash_finding_id() utilities
# - NEW: ucx/utils/finding_hash.py module
#   - Core hash generation with collision handling (4-8 char auto-extend)
#   - Normalization functions for path, section, description
# - UPDATED: ucx/core/context_engine.py
#   - PriorFindingsSummarizer pattern supports both formats
#   - build_attention_steering_format() supports hash ID prompts
#   - build_chairperson_manifest_format() supports hash ID examples
# - TESTS: 39 unit tests in tests/unit/test_finding_hash.py
# - BENEFIT: Eliminates sequential counter synchronization issues
# - BENEFIT: Stable finding tracking across report versions
# - See: docs/CHANGELOG_v1.19.0.md, docs/plans/PLAN-008_hash_based_finding_ids.md

# v1.18.0 - Layer Action Handoff System
# - NEW: ACTION handoff system for BRD review
#   - Captures out-of-scope items as ACTIONS instead of P0/P1/P2 findings
#   - Actions do NOT affect BRD score (0 score impact)
#   - Target layers: PRD (L2), EARS (L3), BDD (L4), ADR (L5), CTR (L8)
# - NEW: Action format with UCX-ACTION-START/END markers
#   - Fields: ACTION_ID, TYPE, TARGET, PRIORITY, SOURCE, PERSONA, CONTEXT, REQUIREMENT
#   - ACTION_ID format: ACT-{8-char-hex} (e.g., ACT-7f3a2b1c)
#   - TYPE: HANDOFF (v1.18.0), future: INFORM, REVIEW, DEFER
# - NEW: extract_actions.py script
#   - Extract actions from UCR review reports
#   - Filter by target, type, priority
#   - Output formats: json, md, csv, summary
# - NEW: validate_actions.py script
#   - Validate action format in review reports
#   - Strict mode: warnings treated as errors
# - UPDATED: All 11 core review personas can create actions
# - UPDATED: Chairperson output includes Actions Manifest
# - UPDATED: UCR report output includes Section 12 (Downstream Layer Actions)
# - BENEFIT: BRD scores no longer penalized for items belonging in downstream layers
# - See: docs/CHANGELOG_v1.18.0.md, docs/plans/PLAN-007_layer_notice_handoff.md

# v1.17.0 - Fixer-to-LLM Hand-off System
# - NEW: Validation now ALWAYS fixes by default (no --fix flag needed)
#   - Use --no-fix to skip fixing (e.g., for pre-commit hooks)
#   - --fix flag deprecated with warning for backwards compatibility
# - NEW: FixerContext dataclass for fixer session tracking
#   - Records fixed, partial, and skipped issues
#   - Identifies LLM_COMPLETION (partial fix, LLM completes) and LLM_ONLY codes
# - NEW: Validation Report Section 7 "Fixer Session Summary"
#   - Embedded JSON with FIXER_CONTEXT_START/END markers
#   - Human-readable tables for partial fixes, LLM-only, protected changes
# - NEW: LLM_COMPLETION markers in documents
#   - <!-- LLM_COMPLETION: CODE --> with Script and Task comments
#   - Inserted at safe locations (avoiding YAML frontmatter)
#   - Deduplicated to prevent accumulation
# - NEW: `ucx clean-markers` command to remove LLM markers after remediation
# - NEW: UCRem integration reads fixer context from validation report
#   - _load_fixer_context() parses Section 7 JSON
#   - _format_fixer_handoff_section() injects into remediation prompts
# - UPDATED: All 6 fixer personas with "Fixer Hand-off Protocol" section
#   - architect, auditor, qa_lead, integration_lead, chaos_engineer, chairperson
# - BENEFIT: Smooth hand-off between script-based fixer and LLM remediation
# - BENEFIT: LLM knows what was fixed, what needs completion, what to protect
# - See: docs/CHANGELOG_v1.17.0.md, docs/plans/PLAN-006_fixer_to_llm_handoff.md

# v1.16.2 - Duplicate Fixer Guardrails & Reference Detection Sync
# - FIXED: Circular rename prevention in GATE-E008 duplicate fixer
#   Previously: Fixer could rename ID A→B, then later rename something to A
#   Now: IDs being renamed FROM are excluded from the target ID pool
# - FIXED: Backtick-wrapped element IDs now detected as references in fixer
#   Previously: Only element_codes.py detected `BRD.XX.XX.XX` as references
#   Now: duplicate_fixer.py also skips backtick-wrapped IDs
# - SYNCED: _is_reference_context() logic between element_codes.py and duplicate_fixer.py
# - NEW: Guardrail logging when circular rename is prevented (verbose mode)
# - BENEFIT: Prevents infinite fix loops where fixer creates new duplicates
# - See: docs/CHANGELOG_v1.16.2.md

# v1.16.1 - Single-File Validation Reports
# - CHANGED: Validation reports now use single-file approach with meaningful name
#   Previously: {doc_id}.V_validation_report_v{NNN}.md (versioned, accumulated)
#   Now: precommit_validation_report.md (single file, overwrites each run)
# - BENEFIT: Cleaner repo history, no accumulation of versioned reports
# - BENEFIT: Meaningful filename for pre-commit hook validation output
# - UPDATED: `--clean-reports` flag now cleans legacy versioned reports only
# - UPDATED: NON_BRD_FILE_PATTERNS includes new filename pattern
# - UPDATED: COMPANION_REPORT_PATTERN recognizes new validation filename
# - See: docs/CHANGELOG_v1.16.1.md

# v1.16.0 - Auto-Detection of Latest Review Report
# - NEW: `ucx remediate` now auto-detects latest UCR review report
#   Previously: Required explicit review_report path as first argument
#   Now: `ucx remediate docs/01_BRD/BRD-01` finds latest *.UCR_review_report_v*.md
# - NEW: `--report` / `-r` option to specify explicit report (override auto-detect)
# - NEW: find_latest_review_report() utility in ucx/utils/file_ops.py
# - NEW: find_latest_remediation_report() utility for UCRem reports
# - CHANGED: UCRemPhase.generate_fixes() argument order changed:
#   Previously: (review_report, doc_path)
#   Now: (doc_path, review_report=None) - review_report is optional
# - NEW: UCRemPhase.last_review_report attribute tracks which report was used
# - UPDATED: Documentation in HOW_TO_USE.md, UCRem_PERSONAS.md
# - BENEFIT: Simpler CLI usage - no need to specify exact report version
# - BENEFIT: API parity - programmatic usage mirrors CLI behavior
# - See: docs/CHANGELOG_v1.16.0.md

# v1.15.6 - Chairperson Findings Extraction Fix
# - FIXED: Chairperson REM-* findings now extract Description column correctly
#   Previously: Extracted "P1" (Priority column) instead of actual description
#   Now: Extracts last column (Description) from multi-column manifest table
# - IMPROVED: Table extraction handles multi-column formats for all personas
#   - Skips short columns (Priority, Status, etc.)
#   - Finds first column with >20 chars as title
# - BUG: Affected REM-P0-001 through REM-P2-NNN findings in review reports
# - See: docs/CHANGELOG_v1.15.6.md

# v1.15.5 - Persona Prompts as Default Review Mode
# - CHANGED: `ucx review` now uses persona prompts mode by default
#   Previously: unified prompt (single API call) was default
#   Now: persona prompts (sequential per-persona calls) is default
# - BENEFIT: Better review quality for all document sizes
# - BENEFIT: No more "large document detected" auto-switching messages
# - USE `--unified` or `-u` flag to force unified prompt mode
# - The `--persona` flag is kept for backwards compatibility (no-op)
# - See: docs/CHANGELOG_v1.15.5.md

# v1.15.4 - BRD-E002 Invalid Value Fixer & GATE-E001 Recursion Fix
# - FIXED: BRD-E002 now fixes INVALID values (not just missing fields):
#   - status: 'Draft' → 'development'
#   - document_type: 'brd-document' → 'brd'
#   - document_type: 'guide' → 'brd'
#   - artifact_type: 'VALIDATION_SUMMARY' → 'BRD'
# - FIXED: BRD-E002 default status changed from 'draft' to 'development'
# - FIXED: GATE-E001 no longer causes recursive nesting of DEFERRED comments
#   Previously: TODO inside DEFERRED got re-converted, causing infinite nesting
#   Now: Existing DEFERRED comments are protected before pattern matching
# - FIXED: GATE-E001 now handles [Pending] and [placeholder] patterns
# - FIXED: BRD-E003 forbidden tag remover (business-requirements → removed)
# - NEW: NON_BRD_FILE_PATTERNS exclusion list for non-BRD files in BRD folders:
#   - BRD_VALIDATION_REPORT.md, EXECUTIVE_SUMMARY.md, GCP_DIAGRAM_GUIDE.md
#   - README.md, CHANGELOG*.md, *.V_validation_report*.md
# - FIXED: GATE-W008 TYPE_TO_SECTION mapping - added missing codes:
#   - 07 (Risk) → Section 10, 08 (Metric) → Section 8
#   - 09 (User Story) → Section 5, 10 (Decision) → Section 7
#   - 23 (Business Objective) → Section 2, 32 (Arch Topic) → Section 7
# - CHANGED: GATE-W008 fixer now adds MOVE-TO-SECTION markers instead of
#   actually moving elements (prevents file corruption from stale line numbers)
# - Impact: Fixed 50 Tier 1 errors (187 → 137), reduced GATE-W008 by 12
# - See: docs/CHANGELOG_v1.15.4.md

# v1.15.3 - BRD-E002, BRD-E009, and GATE-E008 Auto-Fix Improvements
# - FIXED: BRD-E002 now adds `status: draft` field to custom_fields
# - FIXED: BRD-E009 now adds missing fields to EXISTING Document Control tables
#   Previously: Only created new section if none existed, skipped existing tables
#   Now: Parses existing table and adds missing rows with defaults:
#     - Project Name: "BeeLocal Cross-Border Remittance Platform"
#     - Document Version: "1.0"
#     - Date: current date (YYYY-MM-DD)
#     - Document Owner: "BeeLocal Team"
#     - Status: "Draft"
# - FIXED: GATE-E008 now detects additional reference patterns:
#   - Parenthetical refs with suffix: (BRD.14.23.01.02 target)
#   - Checkbox items: - [ ] P1 BRD.40.01.01 — Auth0
#   - Priority-prefixed items: - P1 BRD.40.01.01: Description
#   - Em-dash separated items: BRD.40.01.01 — Auth0
#   - 4-part element IDs: BRD.14.23.01.02
#   - @brd: cross-references: per @brd: BRD.03.01.04
# - SYNCED: element_codes.py and duplicate_fixer.py share same patterns
# - Impact: Fixes 45 BRD-E002 errors, ~18 BRD-E009 errors, ~32 GATE-E008 errors
# - See: docs/CHANGELOG_v1.15.3.md

# v1.15.2 - Extended Auto-Fix Suite (21 fixable codes)
# - NEW: GATE-E001 fixer - converts [TBD]/TODO/FIXME to DEFERRED comments
# - NEW: DIAG-E001 fixer - adds DIAGRAM-REQUIRED placeholder for architecture
# - NEW: FWDREF-E001 fixer - converts forward refs to FWDREF-DEFERRED comments
# - TOTAL: 21 auto-fixable error codes (was 18)
# - IMPACT: Reduces Tier 1 blocking errors significantly
#   - GATE-E001: ~25 placeholder errors converted to deferred
#   - DIAG-E001: ~23 missing diagram errors get placeholders
#   - FWDREF-E001: ~476 forward references converted to deferred
# - See: docs/CHANGELOG_v1.15.2.md

# v1.15.1 - BRD-E020 Invalid Type Code Auto-Fixer
# - NEW: BRD-E020 fixer - remaps invalid type codes to valid BRD codes
# - NEW: INVALID_CODE_REMAP table with 60+ common invalid → valid mappings
# - STRATEGY: Uses remap table, section context, or fallback to "01"
# - IMPACT: Fixes ~1,260 BRD-E020 errors automatically
# - TOTAL: 18 auto-fixable error codes (was 17)
# - See: docs/CHANGELOG_v1.15.1.md

# v1.15.0 - Extended Auto-Fix Suite (17 fixable codes)
# - NEW: BRD-W010 fixer - auto-detects BRD references and adds @depends tags
# - NEW: GATE-W008 fixer - moves elements to correct section files
# - NEW: GATE-E010 fixer - splits large files (>20K tokens) at section boundaries
# - NEW: VAL-E002 fixer - creates YAML frontmatter from scratch for files without it
# - FIXED: BRD-E002 now handles both custom_fields AND Section 0 contexts
# - TOTAL: 17 auto-fixable error codes (was 13)
# - BRD-03 improved: 89.5 → 96.0 (PASS) after applying all fixes
# - See: docs/CHANGELOG_v1.15.0.md

# v1.14.9 - Duplicate Element ID Auto-Fixer (GATE-E008)
# - NEW: DuplicateElementFixer class for automatic ID renumbering
# - NEW: fix_duplicate_ids.py CLI script for standalone use
# - FIXED: Improved reference context detection eliminates false positives
# - NEW: Patterns for category lists, range notation, multiple IDs per line
# - IMPACT: BRD-03 score improved from 0.0 to 89.5/100
# - Fixable codes: GATE-E008 added to FIXABLE_CODES in fixer.py
# - See: docs/CHANGELOG_v1.14.9.md

# v1.14.8 - Terminology Update: Unified Prompt / Persona Prompts
# - RENAMED: "one-turn" → "unified prompt" (single prompt with all personas)
# - RENAMED: "multi-turn" → "persona prompts" (per-persona filtered prompts)
# - UPDATED: Documentation, code comments, and file naming
# - BENEFIT: Clearer terminology that describes what each mode does
# - See: docs/CHANGELOG_v1.14.8.md

# v1.14.7 - Unified Prompt Attention Steering Fix
# - FIXED: Format instructions now placed at END of prompt (was at START)
#   Previously: Format instructions before document content
#   Now: Format instructions after document content (better LLM attention)
# - NEW: _load_format_instructions() method in UCRPhase
# - NEW: UCR_FORMAT_{TYPE}_PROJECT.md files for format instructions
# - BENEFIT: LLMs pay more attention to output requirements
# - BENEFIT: Better compliance with finding ID format and category tags
# - See: docs/CHANGELOG_v1.14.7.md

# v1.14.6 - Session Directory Rename & Review Mode Documentation
# - BREAKING: .doc_review_memory/ → .ucx_review_session/
# - BREAKING: final_body.md → assembled_report.md
# - NEW: Comprehensive unified prompt vs persona prompts documentation
# - See: docs/CHANGELOG_v1.14.6.md

# v1.14.5 - Unified Prompt Feature Parity
# - FIXED: Unified prompt review now loads project-specific skills first
#   Previously: unified used framework skills, persona prompts used project skills
#   Now: both modes use project-specific skills ({project_dir}/docs/UCX/skills/)
# - BENEFIT: Unified prompt reviews include Category Tagging guidance from project skills
# - BENEFIT: Consistent review quality between unified and persona prompts modes
# - Updated: UCRPhase._load_skills() with project-first priority
# - See: docs/CHANGELOG_v1.14.5.md

# v1.14.4 - Extraction Pattern Fixes & Enhancements
# - FIXED: Extraction patterns stopped at ### headers, truncating content
# - ADDED: 15 new extraction patterns for auditor, fact_checker, product_owner
# - All 12 personas now meet 750+ instruction token target
# - 11/12 personas meet 5-10% instruction ratio target
# - See: docs/CHANGELOG_v1.14.4.md

# v1.14.0 - Prompt Inspection Toolset
# - NEW: `ucx prompt` command group with 5 subcommands
#   - `ucx prompt tokens` - Analyze token usage per persona
#   - `ucx prompt sections` - Show section inclusion matrix
#   - `ucx prompt inspect` - Inspect generated prompt files
#   - `ucx prompt check` - Validate document for prompt generation
#   - `ucx prompt generate` - Generate prompts for personas
# - NEW: ucx/prompts/ package with inspection toolset modules:
#   - models.py: PromptSection, InspectionResult, PersonaTokens, TokenAnalysis,
#     SectionMatrix, CheckResult, GeneratedPrompt, GenerationResult, PromptMetadata
#   - exceptions.py: Custom exception hierarchy for prompt inspection
#   - document.py: DocumentLoader for multi-file and single-file documents
#   - inspector.py: PromptInspector for analyzing prompt structure
#   - analyzer.py: TokenAnalyzer for token budget analysis
#   - mapper.py: SectionMapper for section inclusion matrix
#   - api.py: UCPromptPhase main API class
# - NEW: .meta.json metadata files alongside generated prompts
# - NEW: Heuristic structure detection using regex patterns
# - NEW: Dynamic section mapping via semantic categories
# - PURPOSE: Pre-LLM inspection to review prompts before expensive API calls
# - BENEFIT: Debug token budgets, section inclusion, format positioning
# - See: docs/CHANGELOG_v1.14.0.md, docs/plans/PLAN-005_prompt_engineering_toolset.md

# v1.12.0 - Category-Weighted Scoring
# - NEW: Category-weighted scoring replaces legacy formula
#   Formula: raw_deduction = (P0×10) + (P1×3) + (P2×1)
#   Per-category: capped_deduction = min(raw_deduction, max_deduction)
#   Final: weighted_score = 100 - sum(capped_deduction × category_weight)
# - NEW: 8 scoring categories: functional, quality, compliance, constraints,
#   integration, acceptance, risk, architecture
# - NEW: Category detection priority: explicit [CAT:xxx] tag > element code >
#   keyword match > persona default > fallback to OTHER
# - NEW: ScoringCalculator class with per-category scoring
# - NEW: CategoryConflictResolver for multi-source category resolution
# - NEW: Manifest includes Category Summary table with weighted deductions
# - UPDATED: ReviewResult model with weighted_score field
# - UPDATED: Chairperson skill with category summary output format
# - REMOVED: --scoring legacy CLI option (legacy scoring deprecated)
# - DEPRECATED: calculate_legacy_score() emits DeprecationWarning
# - Weights align with ID_NAMING_STANDARDS element type codes
# - Per-category caps prevent runaway negative scores
# - Backward compatible: old reports use persona-based category fallback
# - See: docs/scoring/SCORING_GUIDE.md, docs/CHANGELOG_v1.12.0.md

# v1.11.1 - Validate Command: Report Generation by Default
# - CHANGED: `ucx validate` now generates report to document directory by default
#   Previously: required `--report` flag to generate report
#   Now: generates report automatically, use `--no-report` to skip
# - Aligns validate behavior with review command (both write reports by default)
# - Examples:
#   `ucx validate brd docs/01_BRD/BRD-01/` → generates BRD-01.V_validation_report_v001.md
#   `ucx validate brd docs/01_BRD/BRD-01/ --no-report` → console output only

# v1.11.0 - Unified UCX Scanner with Chairperson Manifest (VALIDATED)
# - NEW: `ucx scan` command - unified report scanner (replaces prescreen)
# - NEW: Chairperson Remediation Findings Manifest - authoritative findings source
#   Chairperson now outputs structured manifest between UCX-MANIFEST-START/END markers
#   with: Finding ID (REM-P0-001), Priority, Status, Fixer assignment, Target file/section
# - NEW: ManifestResult, ManifestFinding dataclasses for manifest parsing
# - NEW: scan_ucr_report() - unified scanner returning ScanResult with both:
#   - manifest extraction (authoritative counts, PRD-Ready score, fixer assignments)
#   - persona extraction (backward compat, fixer routing for pre-manifest reports)
# - NEW: parse_chairperson_manifest() - extract from Chairperson section
# - UPDATED: UCR_PROMPT_BRD_PROJECT.md - Chairperson output format with manifest
# - UPDATED: chairperson.md skill - manifest output requirements and fixer assignment rules
# - BENEFIT: Eliminates discrepancy between CLI counts and Chairperson synthesis
#   Previously: CLI showed P0=116 (raw), Chairperson showed P0=5 (deduplicated)
#   Now: ucx scan shows authoritative counts from manifest when present
# - BENEFIT: Remediation can skip pre-screening - manifest includes all routing info
# - VALIDATED: BRD-02 review (2026-03-12) confirmed manifest generation
#   - Raw CLI: P0=115 → Manifest: P0=10 (91% reduction through synthesis)
#   - PRD-Ready Score: 62/100 extracted correctly
#   - Fixer assignments: 6 fixers with 33 findings total
#   - Target files/sections: Full traceability for remediation

# v1.10.3 - Pre-Screening Accuracy Improvements
# - FIXED: Duplicate counting - now reports unique finding IDs (72 vs 103)
#   Previous: counted same finding ID multiple times across persona sections
#   Now: ScreeningResult.unique_findings, resolved/open/deferred counts deduplicated
# - FIXED: Summary row extraction - excludes "DA-P1-NEW-008 through DA-P1-NEW-012"
#   Previous: standalone pattern extracted IDs from range expressions
#   Now: skips IDs preceded by "through" or "to" in context
# - FIXED: False DEFERRED detection - removed POST-MVP/FUTURE from row pattern
#   Previous: "B2C ONLY (B2B is post-MVP)" triggered DEFERRED
#   Now: only explicit "Defer to X" patterns trigger DEFERRED
# - FIXED: False RESOLVED detection - "CLOSED" no longer triggers in descriptions
#   Previous: "closed/frozen bank account" triggered RESOLVED due to "CLOSED"
#   Now: uses word boundary matching for RESOLVED/VERIFIED/FIXED, excludes CLOSED
# - CLI updated to show unique findings counts
# - JSON output uses unique counts for all metrics
# - Correct results: 72 unique, 62 open, 8 resolved, 2 deferred, 56 actionable

# v1.10.2 - Pre-Screening DEFERRED Status Detection Fix
# - Fixed bug where "Defer to SPEC/BRD" findings were marked as OPEN
# - Previous logic only checked description column for DEFERRED markers
# - Now checks full table row for DEFER/DEFERRED/POST-MVP patterns
# - DEFERRED findings now excluded from actionable count (not just RESOLVED)
# - is_actionable property now excludes status in ("RESOLVED", "VERIFIED", "CLOSED", "DEFERRED")
# - Result: 4 fewer actionable findings (AUD-P1-001, AUD-P1-003 correctly excluded)

# v1.10.1 - Pre-Screening Status Detection Fix
# - Fixed bug where findings were incorrectly marked as RESOLVED
# - Previous regex searched entire document for "✅|RESOLVED" patterns
# - Now only checks within the same table row as the finding ID
# - Added explicit detection of "NOT APPLIED" / "❌" markers as OPEN status
# - Result: accurate actionable finding count and domain fixer mapping

# v1.10.0 - Adaptive Remediation with Pre-Screening
# - NEW: Pre-screening phase automatically runs before remediation
# - NEW: `ucx prescreen` command for standalone screening analysis
# - Adaptive fixer loading: only domain fixers with findings are loaded
# - Added mandatory fixers: chaos_engineer (safety) + chairperson (synthesis)
# - Domain fixers: architect, auditor, qa_lead, integration_lead (adaptive)
# - Chairperson skill updated with remediation synthesis responsibilities
# - New prescreening module: ucx/prescreening/ucr_analyzer.py
# - Token savings: 30-60% reduction by excluding unnecessary personas
# - Pre-screening results embedded in UCRem reports
# - Empty report generated when no actionable findings exist

# v1.9.9 - UCRem Project Path Resolution & Prior Review Reconciliation
# - Fixed UCRem prompt path: now checks project-specific paths first
#   ({project_dir}/docs/UCX/remediation/UCRem_PROMPT_{TYPE}_PROJECT.md)
# - Fixed _load_fixer_skills mapping: integration_expert → integration_lead
# - Fixed project directory auto-detection bug in review/remediate commands:
#   resolves to absolute path before searching, prevents skipping current directory
# - UCRem now loads skills from project-specific paths before framework paths
# - UCRem report now writes to document folder by default (not review report folder)
# - Report naming: {DOC-ID}.UCRem_report.md (e.g., BRD-01.UCRem_report.md)
# - UCR Prior Review Reconciliation: Fact Checker now verifies prior findings resolution
# - Chairperson only counts UNRESOLVED findings in score calculation
# - Auditor adds "Prior Review Findings - Verification Status" table

# v1.9.8 - Tier 2 Diagram Advisory Auto-Fix & Bug Fixes
# - Added auto-fix for BRD-W011 (C4-L1): Adds @diagram-request notice for ADR layer
# - Added auto-fix for BRD-W012 (DFD-L0): Adds @diagram-request notice for ADR layer
# - Added auto-fix for BRD-W013 (Sequence): Auto-detects sync/async/error type
# - Added auto-fix for BRD-W014 (Intent Header): Adds diagram metadata fields
# - New @diagram-request pattern: honest traceability without false claims
# - Fixed version numbering bug: now uses max(version) + 1 instead of len(files) + 1
# - Fixed FIXER_SKILLS: changed integration_expert to integration_lead for consistency

# v1.9.7 - Tier 2 Count Mismatch Auto-Fix
# - Extended --fix to handle GATE-W003 (count mismatch: stated vs actual)
# - Extended --fix to handle DIAG-W001 (diagram node count mismatch)
# - Deterministic fixes for prose count discrepancies
# - Updates "N requirements" to match actual element counts
# - Updates "N nodes" to match actual Mermaid diagram nodes

# v1.9.6 - Auto-Fix for Structural Issues
# - Added --fix flag to `ucx validate` command for deterministic fixes
# - Added --report flag to auto-generate report after fixing (use with --fix)
# - New ucx/validators/brd/fixer.py module with BRDFixer class
# - Fixable issues: BRD-E002 (metadata), BRD-E003/E004 (tags), BRD-E009 (Doc Control),
#   BRD-W005 (legacy status field), VAL-W002 (legacy status value)
# - Auto re-validates after applying fixes to show updated results
# - No AI required - pure script-based structural fixes

# v1.9.5 - Validation Report Cleanup
# - Added --clean-reports flag to `ucx validate` command
# - Added --keep-versions option (default: 1) to control retention
# - Cleans up old *.V_validation_report_v*.md files
# - Matches cleanup functionality in `ucx review` command

# v1.9.4 - QA Subcategory Codes and Pattern Compliance
# - Added QA subcategory codes 91-99 to VALID_BRD_CODES:
#   - 91: Performance Requirement (Section 7.3)
#   - 92: Reliability Requirement (Section 7.4)
#   - 94: Scalability Requirement (Section 7.5)
#   - 96: Security Requirement (Section 7.6)
#   - 98: Observability Requirement (Section 7.7)
#   - 99: Maintainability Requirement (Section 7.8)
# - Added Section 3 (Feature Item=22) and Section 4 (Stakeholder Need=24) to SECTION_CODE_MAP
# - Updated TAG_PATTERNS to require 2+ digit document numbers (\d{2,})
# - Fixed ADR filename pattern from \d{3,} to \d{2,}
# - Updated REQ tag pattern to full element ID format (REQ.\d{2,}.\d{2}.\d{2,})
# - Added PREFERRED_SECTION_CODES for QA sections (7.3-7.8)
# - Fixed GATE-06 tier classification in docstring
# - All validators now compliant with ID_NAMING_STANDARDS.md v2.2

# v1.9.3 - SDD-Compliant Validation Reports
# - Added --output (-o) option to `ucx validate` command
# - Validation reports follow SDD format with YAML frontmatter
# - Report sections: Document Control, Executive Summary, Score Breakdown,
#   Tier 1/2 Findings, Checks Performed, Recommended Next Steps
# - Auto-versioning when writing to document directory
# - Report naming: {DOC-ID}.V_validation_report_v{NNN}.md
# - New format_report() method in UnifiedValidationResult

# v1.9.2 - Unified Validator Registry Integration
# - BRDValidator (registry) now delegates to UnifiedBRDValidator
# - `ucx review brd` and `ucx validate brd` use same validation logic
# - Full Tier 1 + Tier 2 checks available through registry

# v1.9.1 - Tier 2 Advisory Validators
# - New ucx/validators/common/links.py: Markdown link validation
# - New ucx/validators/common/references.py: SDD forward reference validation
# - New ucx/validators/common/diagrams.py: Mermaid/SVG diagram consistency
# - New error codes: LINK-*, FWDREF-*, DIAG-*
# - BRD validator now includes full Tier 2 checks when --tier1-only not used

# v1.9.0 - Unified BRD Validation
# - New ucx/validators/common/ module with shared validation utilities
# - New ucx/validators/brd/ module with UnifiedBRDValidator
# - Tiered validation: Tier 1 (core, blocking) and Tier 2 (advisory)
# - CLI: `ucx validate brd <path>` with --tier1-only, --strict, --format
# - Quality gates: 10 GATE checks (GATE-01 to GATE-10)
# - Element code validation: BRD.NN.TT.SS format with section mapping
# - Deprecated: ai_dev_ssd_flow/01_BRD/scripts/ validators (removal in v2.0.0)

# v1.8.0 - Project-specific skills support
# - SkillLoader now accepts project_dir parameter
# - Skills are loaded from {project_dir}/docs/UCX/skills/ first
# - Falls back to framework skills if project skill not found
# - UnifiedPromptLoader injects project skills into persona prompts
