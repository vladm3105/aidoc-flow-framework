"""Version information for UCX."""

__version__ = "1.9.7"
__version_info__ = tuple(int(x) for x in __version__.split("."))

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
