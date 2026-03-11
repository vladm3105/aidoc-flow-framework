"""Version information for UCX."""

__version__ = "1.9.2"
__version_info__ = tuple(int(x) for x in __version__.split("."))

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
