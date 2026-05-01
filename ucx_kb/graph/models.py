"""Data classes for graph operations."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EntityExtraction:
    """Single extracted entity."""

    type: str  # PascalCase: Ticker, Company, Bias, etc.
    value: str  # Title Case: "NVIDIA", "Loss Aversion"
    confidence: float  # 0.0 - 1.0
    evidence: str  # Quote from source text
    properties: dict = field(default_factory=dict)
    needs_review: bool = False  # True if 0.5 <= confidence < 0.7


@dataclass
class RelationExtraction:
    """Single extracted relationship."""

    from_entity: EntityExtraction
    relation: str  # UPPER_SNAKE: COMPETES_WITH, AFFECTED_BY
    to_entity: EntityExtraction
    confidence: float
    evidence: str
    properties: dict = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Complete extraction result for a document."""

    source_doc_id: str
    source_doc_type: str
    source_file_path: str
    source_text_hash: str
    extracted_at: datetime
    extractor: str  # ollama, claude, openrouter
    extraction_version: str

    entities: list[EntityExtraction] = field(default_factory=list)
    relations: list[RelationExtraction] = field(default_factory=list)

    # Stats
    fields_processed: int = 0
    fields_failed: int = 0
    committed: bool = False
    error_message: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "source_doc_id": self.source_doc_id,
            "source_doc_type": self.source_doc_type,
            "source_file_path": self.source_file_path,
            "source_text_hash": self.source_text_hash,
            "extracted_at": self.extracted_at.isoformat(),
            "extractor": self.extractor,
            "extraction_version": self.extraction_version,
            "entities": [
                {
                    "type": e.type,
                    "value": e.value,
                    "confidence": e.confidence,
                    "evidence": e.evidence,
                    "properties": e.properties,
                    "needs_review": e.needs_review,
                }
                for e in self.entities
            ],
            "relations": [
                {
                    "from": {"type": r.from_entity.type, "value": r.from_entity.value},
                    "relation": r.relation,
                    "to": {"type": r.to_entity.type, "value": r.to_entity.value},
                    "confidence": r.confidence,
                    "evidence": r.evidence,
                    "properties": r.properties,
                }
                for r in self.relations
            ],
            "fields_processed": self.fields_processed,
            "fields_failed": self.fields_failed,
            "committed": self.committed,
            "error_message": self.error_message,
        }


@dataclass
class GraphStats:
    """Graph statistics for status command."""

    node_counts: dict[str, int]  # {"Ticker": 45, "Company": 32, ...}
    edge_counts: dict[str, int]  # {"ISSUED": 45, "COMPETES_WITH": 12, ...}
    total_nodes: int
    total_edges: int
    last_extraction: datetime | None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "node_counts": self.node_counts,
            "edge_counts": self.edge_counts,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "last_extraction": self.last_extraction.isoformat() if self.last_extraction else None,
        }
