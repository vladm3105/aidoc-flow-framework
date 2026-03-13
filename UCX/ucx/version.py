"""Version information for UCX."""

__version__ = "1.13.1"
__version_info__ = tuple(int(x) for x in __version__.split("."))

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
# - Added mandatory fixers: devils_advocate (safety) + chairperson (synthesis)
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
