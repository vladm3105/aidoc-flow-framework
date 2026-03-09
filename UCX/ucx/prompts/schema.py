"""Prompt context schemas for UCX phases.

Defines the context models that are passed to Jinja2 templates for rendering.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class BasePromptContext(BaseModel):
    """Base context for all prompt templates."""

    doc_type: str = Field(..., description="Document type (brd, prd, etc.)")
    doc_id: Optional[str] = Field(None, description="Document ID")
    version: str = Field("1.0", description="Document version")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Generation timestamp",
    )

    # Skill injection
    skills: list[str] = Field(
        default_factory=list,
        description="List of skill/persona names to inject",
    )
    skill_content: dict[str, str] = Field(
        default_factory=dict,
        description="Loaded skill content by name",
    )

    # Configuration
    model: str = Field("opus", description="AI model to use")
    max_tokens: int = Field(8000, description="Maximum output tokens")

    class Config:
        extra = "allow"  # Allow additional fields for flexibility


class UCCContext(BasePromptContext):
    """Context for UCC (Unified Context Creation) phase."""

    # Source content
    reference_content: str = Field(
        "",
        description="Content from reference documents (00_REF)",
    )
    upstream_content: str = Field(
        "",
        description="Content from upstream artifact",
    )
    iplan_content: str = Field(
        "",
        description="Content from implementation plan",
    )

    # Generation settings
    target_path: Optional[str] = Field(
        None,
        description="Target path for generated document",
    )
    template_path: Optional[str] = Field(
        None,
        description="Path to document template",
    )

    # Project context
    project_name: Optional[str] = Field(None, description="Project name")
    project_description: Optional[str] = Field(None, description="Project description")

    # Additional context
    existing_content: Optional[str] = Field(
        None,
        description="Existing document content (for updates)",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Generation constraints",
    )


class UCRContext(BasePromptContext):
    """Context for UCR (Unified Context Review) phase."""

    # Document to review
    document_content: str = Field(
        ...,
        description="Content of document being reviewed",
    )
    document_path: Optional[str] = Field(
        None,
        description="Path to document being reviewed",
    )

    # Validation context
    validation_results: Optional[dict[str, Any]] = Field(
        None,
        description="Results from structural validation",
    )
    validation_errors: list[str] = Field(
        default_factory=list,
        description="Errors from structural validation",
    )
    validation_warnings: list[str] = Field(
        default_factory=list,
        description="Warnings from structural validation",
    )

    # Review criteria
    required_sections: list[str] = Field(
        default_factory=list,
        description="Required sections for this document type",
    )
    element_id_pattern: Optional[str] = Field(
        None,
        description="Expected element ID pattern",
    )

    # Upstream context
    upstream_content: Optional[str] = Field(
        None,
        description="Upstream document for traceability check",
    )

    # Review settings
    min_score: int = Field(90, description="Minimum passing score")
    strict_mode: bool = Field(False, description="Enable strict validation")


class UCRemContext(BasePromptContext):
    """Context for UCRem (Unified Context Remediation) phase."""

    # Review results
    review_report: str = Field(
        ...,
        description="Content of UCR review report",
    )
    review_score: int = Field(
        0,
        description="Score from review",
    )

    # Document to fix
    document_content: str = Field(
        ...,
        description="Content of document to remediate",
    )
    document_path: Optional[str] = Field(
        None,
        description="Path to document being remediated",
    )

    # Findings categorized
    findings_p0: list[str] = Field(
        default_factory=list,
        description="Critical findings (P0)",
    )
    findings_p1: list[str] = Field(
        default_factory=list,
        description="High priority findings (P1)",
    )
    findings_p2: list[str] = Field(
        default_factory=list,
        description="Enhancement recommendations (P2)",
    )

    # Fix settings
    auto_fix_threshold: int = Field(
        90,
        description="Score threshold for auto-fix",
    )
    confidence_threshold: str = Field(
        "auto-safe",
        description="Minimum confidence for auto-apply (auto-safe, auto-assisted, manual-required)",
    )

    # Iteration tracking
    iteration: int = Field(1, description="Current fix iteration")
    max_iterations: int = Field(3, description="Maximum iterations")
    previous_fixes: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Fixes applied in previous iterations",
    )


class PromptResult(BaseModel):
    """Result of prompt rendering."""

    prompt: str = Field(..., description="Rendered prompt text")
    context: dict[str, Any] = Field(..., description="Context used for rendering")
    template_name: str = Field(..., description="Template that was used")
    tokens_estimated: int = Field(0, description="Estimated token count")
