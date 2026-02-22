"""YAML section-level chunking for RAG."""

import logging
import os
from pathlib import Path
from typing import Any

import yaml

from .exceptions import ChunkingError
from .flatten import humanize_key, section_to_text
from .models import ChunkResult
from .tokens import estimate_tokens, split_by_tokens

log = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

# Load config
_config_path = Path(__file__).parent / "config.yaml"
_config: dict = {}
if _config_path.exists():
    with open(_config_path) as f:
        _config = yaml.safe_load(f) or {}

# Chunking parameters (environment variables override config)
_chunk_config = _config.get("chunking", {})
_features = _config.get("features", {})


def _get_config_value(key: str, default: Any, env_var: str | None = None) -> Any:
    """Get config value with environment variable override."""
    if env_var and os.getenv(env_var):
        val = os.getenv(env_var)
        # Try to convert to int/float if numeric
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val
    return default


# Chunk size parameters (optimized based on arXiv 2402.05131)
MAX_TOKENS = _get_config_value(
    "max_tokens", _chunk_config.get("max_tokens", 768), "CHUNK_MAX_TOKENS"
)
MIN_TOKENS = _get_config_value(
    "min_tokens", _chunk_config.get("min_tokens", 50), "CHUNK_MIN_TOKENS"
)
OVERLAP_TOKENS = _get_config_value(
    "overlap_tokens", _chunk_config.get("overlap_tokens", 150), "CHUNK_OVERLAP"
)

# Feature flags
PRESERVE_TABLES = _features.get("preserve_tables", True)
ELEMENT_AWARE = _features.get("element_aware_chunking", True)

# Load section mappings
_section_mappings_path = Path(__file__).parent / "section_mappings.yaml"
_section_mappings: dict = {}

if _section_mappings_path.exists():
    with open(_section_mappings_path) as f:
        _section_mappings = yaml.safe_load(f)


# =============================================================================
# Table Detection (for element-aware chunking)
# =============================================================================


def is_table_content(content: str) -> bool:
    """
    Detect if content is a table that should be kept atomic.

    Tables are identified by:
    - Multiple lines with pipe characters (markdown tables)
    - Lines with consistent column alignment
    """
    lines = content.strip().split("\n")
    if len(lines) < 3:
        return False

    # Check for pipe-delimited tables (markdown style)
    pipe_lines = sum(1 for line in lines if "|" in line)
    if pipe_lines / len(lines) > 0.5:
        return True

    # Check for aligned columns (YAML table-like structures)
    colon_lines = sum(1 for line in lines if ": " in line and line.startswith("  "))
    if colon_lines / len(lines) > 0.7:
        return True

    return False


def prepare_chunk_text(
    section_label: str,
    content: str,
    ticker: str | None,
    doc_type: str,
) -> str:
    """
    Add context prefix to improve embedding relevance.

    Format: [doc_type] [ticker] [section_label]\\n{content}

    Example:
    [earnings-analysis] [NVDA] [Competitive Context]
    Compare ABSOLUTE DOLLARS, not percentages. NVDA adding $17B vs AMD...
    """
    prefix_parts = [f"[{doc_type}]"]
    if ticker:
        prefix_parts.append(f"[{ticker}]")
    prefix_parts.append(f"[{section_label}]")
    prefix = " ".join(prefix_parts)
    return f"{prefix}\n{content}"


def chunk_yaml_document(
    file_path: str,
    max_tokens: int | None = None,
    min_tokens: int | None = None,
) -> list[ChunkResult]:
    """
    Split YAML document into semantic chunks.

    Pipeline:
    1. Parse YAML
    2. Get section mappings for this doc type
    3. Extract and flatten each section
    4. Split large sections (>max_tokens) into sub-chunks
    5. Skip very small sections (<min_tokens)
    6. Prepare text with context prefix

    Args:
        file_path: Path to YAML document
        max_tokens: Maximum tokens per chunk
        min_tokens: Minimum tokens (skip smaller sections)

    Returns:
        List of ChunkResult objects
    """
    # Use config values if not specified
    if max_tokens is None:
        max_tokens = MAX_TOKENS
    if min_tokens is None:
        min_tokens = MIN_TOKENS

    if not Path(file_path).exists():
        raise ChunkingError(f"File not found: {file_path}")

    with open(file_path) as f:
        doc = yaml.safe_load(f)

    if not doc:
        raise ChunkingError(f"Empty or invalid YAML: {file_path}")

    # Get document metadata
    meta = doc.get("_meta", {})
    doc_type = meta.get("doc_type", _infer_doc_type(file_path))
    ticker = meta.get("ticker") or doc.get("ticker")

    # Get section mappings for this doc type
    mappings = _section_mappings.get(doc_type, {})
    sections = mappings.get("sections", [])
    skip_sections = mappings.get("skip", ["_meta", "_graph", "_links"])

    chunks = []

    # If no specific sections defined, use all top-level keys
    if not sections:
        sections = [
            {"path": k, "label": humanize_key(k)} for k in doc.keys() if k not in skip_sections
        ]

    for section in sections:
        section_path = section["path"] if isinstance(section, dict) else section
        section_label = (
            section.get("label", humanize_key(section_path))
            if isinstance(section, dict)
            else humanize_key(section)
        )

        # Get section data
        section_data = _get_nested_value(doc, section_path)
        if section_data is None:
            continue

        # Convert to text
        content = section_to_text(section_data, section_label)
        if not content:
            continue

        # Estimate tokens
        token_count = estimate_tokens(content)

        # Skip very small sections
        if token_count < min_tokens:
            log.debug(f"Skipping small section {section_path} ({token_count} tokens)")
            continue

        # Table preservation: keep tables atomic (up to 2x max_tokens)
        if PRESERVE_TABLES and is_table_content(content):
            if token_count <= max_tokens * 2:
                log.debug(f"Preserving table in {section_path} ({token_count} tokens)")
                prepared = prepare_chunk_text(section_label, content, ticker, doc_type)
                chunks.append(
                    ChunkResult(
                        section_path=section_path,
                        section_label=section_label,
                        chunk_index=0,
                        content=content,
                        content_tokens=token_count,
                        prepared_text=prepared,
                    )
                )
                continue

        # Split large sections
        if token_count > max_tokens:
            sub_chunks = chunk_yaml_section(
                content, section_path, section_label, ticker, doc_type, max_tokens
            )
            chunks.extend(sub_chunks)
        else:
            prepared = prepare_chunk_text(section_label, content, ticker, doc_type)
            chunks.append(
                ChunkResult(
                    section_path=section_path,
                    section_label=section_label,
                    chunk_index=0,
                    content=content,
                    content_tokens=token_count,
                    prepared_text=prepared,
                )
            )

    return chunks


def chunk_yaml_section(
    content: str,
    section_path: str,
    section_label: str,
    ticker: str | None,
    doc_type: str,
    max_tokens: int | None = None,
    overlap: int | None = None,
) -> list[ChunkResult]:
    """
    Split a single section into chunks when it exceeds max_tokens.

    Splitting strategy:
    - Split by paragraphs/lines first
    - Then by token count if still too large
    - Uses configurable overlap for continuity
    """
    # Use config values if not specified
    if max_tokens is None:
        max_tokens = MAX_TOKENS
    if overlap is None:
        overlap = OVERLAP_TOKENS

    chunks = []

    # Try splitting by paragraphs
    paragraphs = content.split("\n\n")

    if len(paragraphs) > 1:
        # Combine paragraphs into chunks under max_tokens
        current_content = []
        current_tokens = 0
        chunk_index = 0

        for para in paragraphs:
            para_tokens = estimate_tokens(para)

            if current_tokens + para_tokens > max_tokens and current_content:
                # Save current chunk
                combined = "\n\n".join(current_content)
                prepared = prepare_chunk_text(section_label, combined, ticker, doc_type)
                chunks.append(
                    ChunkResult(
                        section_path=section_path,
                        section_label=section_label,
                        chunk_index=chunk_index,
                        content=combined,
                        content_tokens=current_tokens,
                        prepared_text=prepared,
                    )
                )
                chunk_index += 1
                current_content = [para]
                current_tokens = para_tokens
            else:
                current_content.append(para)
                current_tokens += para_tokens

        # Don't forget last chunk
        if current_content:
            combined = "\n\n".join(current_content)
            prepared = prepare_chunk_text(section_label, combined, ticker, doc_type)
            chunks.append(
                ChunkResult(
                    section_path=section_path,
                    section_label=section_label,
                    chunk_index=chunk_index,
                    content=combined,
                    content_tokens=current_tokens,
                    prepared_text=prepared,
                )
            )
    else:
        # Split by token count with configurable overlap
        sub_texts = split_by_tokens(content, max_tokens, overlap=overlap)
        for i, sub_text in enumerate(sub_texts):
            tokens = estimate_tokens(sub_text)
            prepared = prepare_chunk_text(section_label, sub_text, ticker, doc_type)
            chunks.append(
                ChunkResult(
                    section_path=section_path,
                    section_label=section_label,
                    chunk_index=i,
                    content=sub_text,
                    content_tokens=tokens,
                    prepared_text=prepared,
                )
            )

    return chunks


def _get_nested_value(doc: dict, path: str) -> Any:
    """Get nested value from document using dot notation."""
    parts = path.split(".")
    current = doc

    for part in parts:
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None

    return current


def _infer_doc_type(file_path: str) -> str:
    """Infer document type from file path."""
    path = Path(file_path)
    parent = path.parent.name

    type_map = {
        "earnings": "earnings-analysis",
        "stock": "stock-analysis",
        "trades": "trade-journal",
        "reviews": "post-trade-review",
        "research": "research-analysis",
        "strategies": "strategy",
        "learnings": "learning",
        "ticker-profiles": "ticker-profile",
    }

    for key, value in type_map.items():
        if key in parent.lower():
            return value

    return "unknown"
