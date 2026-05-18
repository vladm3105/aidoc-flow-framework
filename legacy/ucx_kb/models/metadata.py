"""Domain-neutral metadata model for project knowledge documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class DocumentMetadata:
    """Canonical metadata used across RAG and Graph modules."""

    doc_id: str
    entity_id: str | None = None
    domain: str = "general"
    source_type: str = "document"
    source_path: str | None = None
    title: str | None = None
    tags: list[str] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    schema_version: str = "v1"

    def normalized_entity_id(self) -> str | None:
        """Return normalized entity identifier for indexing/filtering."""
        if not self.entity_id:
            return None
        return self.entity_id.strip().lower()

    def normalized_tags(self) -> list[str]:
        """Return lowercased unique tags with stable ordering."""
        seen = set()
        normalized: list[str] = []
        for tag in self.tags:
            cleaned = tag.strip().lower()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                normalized.append(cleaned)
        return normalized
