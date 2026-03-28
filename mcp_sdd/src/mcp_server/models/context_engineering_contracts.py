from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json


@dataclass(frozen=True)
class RelevantSnippet:
    section_id: str
    keyword: str
    text: str
    confidence: float


@dataclass(frozen=True)
class AppendixIndexEntry:
    appendix_id: str
    title: str
    token_estimate: int
    summary: str


@dataclass(frozen=True)
class ContextContract:
    sections_included: list[str]
    sections_skipped: list[str]
    discovered_snippets: list[RelevantSnippet]
    appendix_index: list[AppendixIndexEntry]
    token_estimate: int


@dataclass(frozen=True)
class PromptMetadataSidecar:
    persona: str
    doc_type: str
    structure_blocks: list[str]
    sections_included: list[str] = field(default_factory=list)
    sections_skipped: list[str] = field(default_factory=list)
    tokens_total: int = 0


@dataclass(frozen=True)
class PromptBundle:
    context: ContextContract
    metadata: PromptMetadataSidecar


def validate_context_contract(context: ContextContract) -> list[str]:
    errors: list[str] = []

    if not context.sections_included:
        errors.append("sections_included must be non-empty")
    if context.token_estimate <= 0:
        errors.append("token_estimate must be > 0")

    for snippet in context.discovered_snippets:
        if not snippet.section_id:
            errors.append("discovered_snippets.section_id is required")
        if not (0.0 <= snippet.confidence <= 1.0):
            errors.append("discovered_snippets.confidence must be in [0.0, 1.0]")

    for appendix in context.appendix_index:
        if not appendix.appendix_id:
            errors.append("appendix_index.appendix_id is required")
        if appendix.token_estimate <= 0:
            errors.append("appendix_index.token_estimate must be > 0")

    return errors


def validate_prompt_metadata_sidecar(metadata: PromptMetadataSidecar) -> list[str]:
    errors: list[str] = []

    if not metadata.persona:
        errors.append("persona is required")
    if not metadata.doc_type:
        errors.append("doc_type is required")
    if not metadata.structure_blocks:
        errors.append("structure_blocks must be non-empty")
    if metadata.tokens_total <= 0:
        errors.append("tokens_total must be > 0")

    return errors


def deterministic_fingerprint(bundle: PromptBundle) -> str:
    """Stable hash used by regression tests to detect context/metadata drift."""

    payload = {
        "context": asdict(bundle.context),
        "metadata": asdict(bundle.metadata),
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def serialize_prompt_metadata_sidecar(metadata: PromptMetadataSidecar) -> str:
    """Serialize prompt metadata for CLI/API sidecar emission."""

    payload = {
        "persona": metadata.persona,
        "doc_type": metadata.doc_type,
        "structure_blocks": metadata.structure_blocks,
        "sections": {
            "included": metadata.sections_included,
            "skipped": metadata.sections_skipped,
        },
        "tokens": {
            "total": metadata.tokens_total,
        },
    }
    return json.dumps(payload, sort_keys=True)
