"""Validation helpers for ucx_kb ingestion."""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ValidationResult:
    valid: bool
    error_summary: str | None = None
    warnings: list[str] | None = None


def validate_document(file_path: str) -> ValidationResult:
    """Validate basic document integrity required for ingestion."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return ValidationResult(valid=False, error_summary=f"File not found: {file_path}", warnings=[])

    try:
        with path.open(encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
    except Exception as exc:
        return ValidationResult(valid=False, error_summary=f"Invalid YAML: {exc}", warnings=[])

    if payload is None:
        return ValidationResult(valid=False, error_summary="YAML document is empty", warnings=[])

    if not isinstance(payload, dict):
        return ValidationResult(
            valid=False,
            error_summary="Top-level YAML structure must be a mapping",
            warnings=[],
        )

    warnings: list[str] = []
    if "_meta" not in payload:
        warnings.append("Missing _meta section")

    return ValidationResult(valid=True, warnings=warnings)


def get_schema_for_path(file_path: str) -> str | None:
    """Resolve schema path for the given document path when available."""
    return None
