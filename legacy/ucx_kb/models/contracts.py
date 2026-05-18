"""Versioned payload contracts for ucx_kb RAG and Graph tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .metadata import DocumentMetadata


ContractVersion = "v1"


@dataclass(slots=True)
class EmbedRequest:
    contract_version: str = ContractVersion
    file_path: str | None = None
    text: str | None = None
    metadata: DocumentMetadata | None = None
    force: bool = False


@dataclass(slots=True)
class EmbedResponse:
    contract_version: str = ContractVersion
    doc_id: str = ""
    chunk_count: int = 0
    status: str = "ok"
    error_message: str | None = None


@dataclass(slots=True)
class SearchRequest:
    contract_version: str = ContractVersion
    query: str = ""
    entity_id: str | None = None
    domain: str | None = None
    tags: list[str] = field(default_factory=list)
    doc_type: str | None = None
    section: str | None = None
    top_k: int = 5


@dataclass(slots=True)
class SearchResponse:
    contract_version: str = ContractVersion
    results: list[dict] = field(default_factory=list)


@dataclass(slots=True)
class ExtractRequest:
    contract_version: str = ContractVersion
    file_path: str | None = None
    text: str | None = None
    metadata: DocumentMetadata | None = None
    extractor: str | None = None
    commit: bool = True


@dataclass(slots=True)
class ExtractResponse:
    contract_version: str = ContractVersion
    entities: list[dict] = field(default_factory=list)
    relations: list[dict] = field(default_factory=list)
    committed: bool = False
    error_message: str | None = None


@dataclass(slots=True)
class HybridContextRequest:
    contract_version: str = ContractVersion
    query: str = ""
    entity_id: str | None = None
    domain: str | None = None
    analysis_type: str | None = None


@dataclass(slots=True)
class HybridContextResponse:
    contract_version: str = ContractVersion
    entity_id: str | None = None
    vector_results: list[dict] = field(default_factory=list)
    graph_context: dict = field(default_factory=dict)
    formatted: str = ""


@dataclass(slots=True)
class GraphContextRequest:
    contract_version: str = ContractVersion
    entity_id: str = ""


@dataclass(slots=True)
class GraphContextResponse:
    contract_version: str = ContractVersion
    entity_id: str = ""
    context: dict = field(default_factory=dict)


@dataclass(slots=True)
class HealthStatus:
    contract_version: str = ContractVersion
    service: str = "ucx_kb"
    status: str = "unknown"
    checked_at: datetime = field(default_factory=datetime.utcnow)
    details: dict = field(default_factory=dict)
