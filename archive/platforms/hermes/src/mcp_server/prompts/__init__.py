"""Prompt assembly and validation for MCP runtime."""

from .context_builder import (
    ContractValidationError,
    CreationAssembly,
    PromptAssembly,
    SectionMappingResult,
    SourceSection,
    assemble_project_creation_prompt,
    assemble_project_review_prompt,
    build_appendix_index,
    build_prompt_bundle,
    build_runtime_context,
    categorize_section,
    discover_relevant_snippets,
    inspect_prompt_bundle,
    map_sections_for_personas,
    validate_prompt_bundle_or_raise,
)

__all__ = [
    "CreationAssembly",
    "PromptAssembly",
    "ContractValidationError",
    "SectionMappingResult",
    "SourceSection",
    "assemble_project_creation_prompt",
    "assemble_project_review_prompt",
    "build_prompt_bundle",
    "build_appendix_index",
    "build_runtime_context",
    "categorize_section",
    "discover_relevant_snippets",
    "inspect_prompt_bundle",
    "map_sections_for_personas",
    "validate_prompt_bundle_or_raise",
]
