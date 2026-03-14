"""Exceptions for prompt inspection toolset.

This module defines custom exceptions for the prompt inspection
and analysis functionality.

Version: 1.14.0
"""

from pathlib import Path
from typing import Optional


class PromptInspectionError(Exception):
    """Base exception for prompt inspection toolset."""

    pass


class DocumentNotFoundError(PromptInspectionError):
    """Document path does not exist."""

    def __init__(self, path: Path):
        self.path = path
        super().__init__(f"Document not found: {path}")


class InvalidDocumentTypeError(PromptInspectionError):
    """Unknown document type."""

    VALID_TYPES = {"brd", "prd", "ears", "adr", "sys", "req", "spec", "ctr", "tspec"}

    def __init__(self, doc_type: str, valid_types: Optional[list[str]] = None):
        self.doc_type = doc_type
        self.valid_types = valid_types or list(self.VALID_TYPES)
        super().__init__(
            f"Invalid document type: {doc_type}. "
            f"Valid types: {', '.join(sorted(self.valid_types))}"
        )


class PromptFileNotFoundError(PromptInspectionError):
    """Prompt file does not exist."""

    def __init__(self, path: Path):
        self.path = path
        super().__init__(f"Prompt file not found: {path}")


class MetadataNotFoundError(PromptInspectionError):
    """Metadata file not found (non-fatal warning).

    This is raised when inspecting a prompt that doesn't have
    an accompanying .meta.json file. The inspector can still
    work in heuristic mode.
    """

    def __init__(self, prompt_path: Path):
        self.prompt_path = prompt_path
        meta_path = prompt_path.with_suffix(".meta.json")
        super().__init__(
            f"Metadata file not found: {meta_path}. "
            f"Using heuristic detection mode."
        )


class PersonaNotFoundError(PromptInspectionError):
    """Unknown persona requested."""

    VALID_PERSONAS = {
        "architect",
        "auditor",
        "tech_lead",
        "strategist",
        "chaos_engineer",  # Renamed from devils_advocate (v1.14.3)
        "operator",
        "integration_lead",
        "product_owner",
        "business_analyst",
        "fact_checker",
        "chairperson",
        "qa_lead",  # Added v1.14.3
    }

    def __init__(self, persona: str, valid_personas: Optional[list[str]] = None):
        self.persona = persona
        self.valid_personas = valid_personas or list(self.VALID_PERSONAS)
        super().__init__(
            f"Unknown persona: {persona}. "
            f"Valid personas: {', '.join(sorted(self.valid_personas))}"
        )


class TokenBudgetExceededError(PromptInspectionError):
    """Token budget exceeded (for strict mode)."""

    def __init__(self, persona: str, tokens: int, budget: int):
        self.persona = persona
        self.tokens = tokens
        self.budget = budget
        self.overage = tokens - budget
        self.overage_pct = (tokens / budget - 1) * 100
        super().__init__(
            f"{persona} exceeds budget: {tokens:,} > {budget:,} tokens "
            f"(+{self.overage:,} tokens, +{self.overage_pct:.1f}%)"
        )


class ConfigurationError(PromptInspectionError):
    """Invalid configuration."""

    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class PromptGenerationError(PromptInspectionError):
    """Error during prompt generation."""

    def __init__(self, persona: str, message: str):
        self.persona = persona
        super().__init__(f"Failed to generate prompt for {persona}: {message}")


# Utility functions for validation


def validate_doc_type(doc_type: str) -> str:
    """Validate and normalize document type.

    Args:
        doc_type: Document type string

    Returns:
        Normalized (lowercase) document type

    Raises:
        InvalidDocumentTypeError: If doc_type is not valid
    """
    normalized = doc_type.lower().strip()
    if normalized not in InvalidDocumentTypeError.VALID_TYPES:
        raise InvalidDocumentTypeError(doc_type)
    return normalized


def validate_persona(persona: str) -> str:
    """Validate and normalize persona name.

    Args:
        persona: Persona name

    Returns:
        Normalized persona name

    Raises:
        PersonaNotFoundError: If persona is not valid
    """
    normalized = persona.lower().strip().replace("-", "_")
    if normalized not in PersonaNotFoundError.VALID_PERSONAS:
        raise PersonaNotFoundError(persona)
    return normalized


def validate_personas(personas: list[str]) -> list[str]:
    """Validate and normalize a list of persona names.

    Args:
        personas: List of persona names

    Returns:
        List of normalized persona names

    Raises:
        PersonaNotFoundError: If any persona is not valid
    """
    return [validate_persona(p) for p in personas]
