"""Lightweight validation stubs used by extracted modules."""

from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    error_summary: str | None = None
    warnings: list[str] | None = None


def validate_document(file_path: str) -> ValidationResult:
    """Return permissive validation result; schema checks are optional in MVP."""
    return ValidationResult(valid=True, warnings=[])


def get_schema_for_path(file_path: str) -> str | None:
    """Placeholder schema resolver."""
    return None
