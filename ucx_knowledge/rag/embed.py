"""Full embedding pipeline: parse → chunk → embed → store."""

import hashlib
import json
import logging
import os
import time
from datetime import UTC, date, datetime
from pathlib import Path

from dotenv import load_dotenv
import psycopg
import yaml

# Load .env file for credentials
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

from ucx_knowledge.utils import is_real_document
from ucx_knowledge.validation import get_schema_for_path, validate_document
from . import RAG_VERSION
from .chunk import chunk_yaml_document
from .embedding_client import get_embedding, get_embeddings_batch
from .exceptions import EmbedError
from .models import ChunkResult, EmbedResult
from .schema import get_database_url

log = logging.getLogger(__name__)

# Load configuration
_config_path = Path(__file__).parent / "config.yaml"
_config: dict = {}


def _expand_env_vars(content: str) -> str:
    """Expand ${VAR} and ${VAR:-default} patterns in config."""
    import re

    pattern = r"\$\{([A-Z_][A-Z0-9_]*)(?::-([^}]*))?\}"

    def replacer(match):
        var_name = match.group(1)
        default = match.group(2) if match.group(2) is not None else ""
        return os.getenv(var_name, default)

    return re.sub(pattern, replacer, content)


if _config_path.exists():
    with open(_config_path) as f:
        config_content = f.read()
        config_content = _expand_env_vars(config_content)
        _config = yaml.safe_load(config_content)


def embed_document(file_path: str, force: bool = False) -> EmbedResult:
    """
    Embed a YAML document into pgvector.

    Pipeline:
    1. Validate file (must be real document)
    2. Check file_hash (skip if unchanged and not force)
    3. Parse YAML and extract metadata
    4. Chunk document using section_mappings
    5. Embed each chunk
    6. Store in rag_documents and rag_chunks tables
    7. Log to rag_embed_log

    Args:
        file_path: Path to YAML document
        force: Re-embed even if file unchanged

    Returns:
        EmbedResult with embedding details
    """
    start_time = time.time()

    # Validate file
    if not is_real_document(file_path):
        raise EmbedError(f"Not a real document (template?): {file_path}")

    if not Path(file_path).exists():
        raise EmbedError(f"File not found: {file_path}")

    # Parse YAML
    with open(file_path) as f:
        doc = yaml.safe_load(f)

    if not doc:
        raise EmbedError(f"Empty or invalid YAML: {file_path}")

    # Schema validation (optional - logs at debug level, doesn't block)
    # Note: Schema may be outdated relative to template - validation is informational only
    if validate_document is not None:
        validation_result = validate_document(file_path)
        if not validation_result.valid:
            log.debug(
                f"Schema validation info for {file_path}: {validation_result.error_summary}"
            )
        elif validation_result.warnings:
            log.debug(f"Validation warnings for {file_path}: {validation_result.warnings}")

    # Extract metadata
    meta = doc.get("_meta", {})
    doc_id = meta.get("id", Path(file_path).stem)
    doc_type = meta.get("doc_type", _infer_doc_type(file_path))
    ticker = meta.get("ticker") or doc.get("ticker")
    doc_date = _parse_date(meta.get("date") or doc.get("date"))
    quarter = meta.get("quarter")

    # Compute file hash
    file_hash = _compute_file_hash(file_path)

    # Check if already embedded with same hash
    if not force:
        existing = _get_document_by_id(doc_id)
        if existing and existing.get("file_hash") == file_hash:
            log.info(f"Document {doc_id} unchanged, skipping")
            return EmbedResult(
                doc_id=doc_id,
                file_path=file_path,
                doc_type=doc_type,
                ticker=ticker,
                doc_date=doc_date,
                chunk_count=existing.get("chunk_count", 0),
                embed_model=_config.get("embedding", {})
                .get("ollama", {})
                .get("model", "nomic-embed-text"),
                embed_version=RAG_VERSION,
                duration_ms=0,
                error_message="unchanged",
            )

    # Chunk document
    max_tokens = int(_config.get("chunking", {}).get("max_tokens", 1500))
    min_tokens = int(_config.get("chunking", {}).get("min_tokens", 50))

    chunks = chunk_yaml_document(file_path, max_tokens=max_tokens, min_tokens=min_tokens)

    if not chunks:
        raise EmbedError(f"No chunks generated from {file_path}")

    # Get embeddings
    try:
        texts = [c.prepared_text for c in chunks]
        embeddings = get_embeddings_batch(texts)
    except Exception as e:
        raise EmbedError(f"Embedding failed: {e}")

    # Store in database
    try:
        _store_document(
            doc_id=doc_id,
            file_path=file_path,
            doc_type=doc_type,
            ticker=ticker,
            doc_date=doc_date,
            quarter=quarter,
            file_hash=file_hash,
            chunks=chunks,
            embeddings=embeddings,
        )
    except Exception as e:
        raise EmbedError(f"Database storage failed: {e}")

    duration_ms = int((time.time() - start_time) * 1000)
    embed_model = _config.get("embedding", {}).get("ollama", {}).get("model", "nomic-embed-text")

    result = EmbedResult(
        doc_id=doc_id,
        file_path=file_path,
        doc_type=doc_type,
        ticker=ticker,
        doc_date=doc_date,
        chunk_count=len(chunks),
        embed_model=embed_model,
        embed_version=RAG_VERSION,
        duration_ms=duration_ms,
    )

    # Log result
    _log_embed(result)

    return result


def embed_text(
    text: str,
    doc_id: str,
    doc_type: str,
    ticker: str | None = None,
) -> EmbedResult:
    """
    Embed raw text (for external content).

    Args:
        text: Raw text to embed
        doc_id: Document identifier
        doc_type: Document type
        ticker: Optional ticker symbol

    Returns:
        EmbedResult
    """
    start_time = time.time()

    # Get embedding
    embedding = get_embedding(text)

    # Store as single chunk
    chunk = ChunkResult(
        section_path="content",
        section_label="Content",
        chunk_index=0,
        content=text,
        content_tokens=len(text.split()),  # Rough estimate
        prepared_text=f"[{doc_type}] [{ticker or 'N/A'}] [Content]\n{text}",
    )

    file_hash = hashlib.sha256(text.encode()).hexdigest()[:16]

    _store_document(
        doc_id=doc_id,
        file_path="text",
        doc_type=doc_type,
        ticker=ticker,
        doc_date=None,
        quarter=None,
        file_hash=file_hash,
        chunks=[chunk],
        embeddings=[embedding],
    )

    duration_ms = int((time.time() - start_time) * 1000)

    return EmbedResult(
        doc_id=doc_id,
        file_path="text",
        doc_type=doc_type,
        ticker=ticker,
        doc_date=None,
        chunk_count=1,
        embed_model=_config.get("embedding", {}).get("ollama", {}).get("model", "nomic-embed-text"),
        embed_version=RAG_VERSION,
        duration_ms=duration_ms,
    )


def delete_document(doc_id: str) -> bool:
    """
    Delete document and all its chunks.

    Args:
        doc_id: Document ID

    Returns:
        True if deleted, False if not found
    """
    try:
        with psycopg.connect(get_database_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM nexus.rag_documents WHERE doc_id = %s RETURNING id", (doc_id,)
                )
                result = cur.fetchone()
            conn.commit()
        return result is not None
    except Exception as e:
        log.error(f"Failed to delete document {doc_id}: {e}")
        return False


def reembed_all(version: str | None = None) -> int:
    """
    Re-embed all documents (or those with specific version).

    Args:
        version: Optional version filter

    Returns:
        Number of documents re-embedded
    """
    count = 0

    try:
        with psycopg.connect(get_database_url()) as conn:
            with conn.cursor() as cur:
                if version:
                    cur.execute(
                        "SELECT file_path FROM nexus.rag_documents WHERE embed_version = %s",
                        (version,),
                    )
                else:
                    cur.execute("SELECT file_path FROM nexus.rag_documents")

                rows = cur.fetchall()

        for (file_path,) in rows:
            if file_path and file_path != "text" and Path(file_path).exists():
                try:
                    embed_document(file_path, force=True)
                    count += 1
                except Exception as e:
                    log.error(f"Failed to re-embed {file_path}: {e}")

    except Exception as e:
        log.error(f"Re-embed query failed: {e}")

    return count


def _compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of file contents."""
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _get_document_by_id(doc_id: str) -> dict | None:
    """Get existing document by ID."""
    try:
        with psycopg.connect(get_database_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT file_hash, chunk_count FROM nexus.rag_documents WHERE doc_id = %s",
                    (doc_id,),
                )
                row = cur.fetchone()
                if row:
                    return {"file_hash": row[0], "chunk_count": row[1]}
    except Exception:
        pass
    return None


def _store_document(
    doc_id: str,
    file_path: str,
    doc_type: str,
    ticker: str | None,
    doc_date: date | None,
    quarter: str | None,
    file_hash: str,
    chunks: list[ChunkResult],
    embeddings: list[list[float]],
) -> None:
    """Store document and chunks in PostgreSQL."""
    embed_model = _config.get("embedding", {}).get("ollama", {}).get("model", "nomic-embed-text")

    with psycopg.connect(get_database_url()) as conn:
        with conn.cursor() as cur:
            # Upsert document
            cur.execute(
                """
                INSERT INTO nexus.rag_documents
                    (doc_id, file_path, doc_type, ticker, doc_date, quarter,
                     chunk_count, embed_version, embed_model, file_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (doc_id) DO UPDATE SET
                    file_path = EXCLUDED.file_path,
                    doc_type = EXCLUDED.doc_type,
                    ticker = EXCLUDED.ticker,
                    doc_date = EXCLUDED.doc_date,
                    quarter = EXCLUDED.quarter,
                    chunk_count = EXCLUDED.chunk_count,
                    embed_version = EXCLUDED.embed_version,
                    embed_model = EXCLUDED.embed_model,
                    file_hash = EXCLUDED.file_hash,
                    updated_at = now()
                RETURNING id
            """,
                (
                    doc_id,
                    file_path,
                    doc_type,
                    ticker,
                    doc_date,
                    quarter,
                    len(chunks),
                    RAG_VERSION,
                    embed_model,
                    file_hash,
                ),
            )

            doc_pk = cur.fetchone()[0]

            # Delete existing chunks
            cur.execute("DELETE FROM nexus.rag_chunks WHERE doc_id = %s", (doc_pk,))

            # Insert new chunks
            for chunk, embedding in zip(chunks, embeddings):
                cur.execute(
                    """
                    INSERT INTO nexus.rag_chunks
                        (doc_id, section_path, section_label, chunk_index,
                         content, content_tokens, embedding, doc_type, ticker, doc_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::vector, %s, %s, %s)
                """,
                    (
                        doc_pk,
                        chunk.section_path,
                        chunk.section_label,
                        chunk.chunk_index,
                        chunk.content,
                        chunk.content_tokens,
                        str(embedding),
                        doc_type,
                        ticker,
                        doc_date,
                    ),
                )

        conn.commit()


def _parse_date(date_str: str | None) -> date | None:
    """Parse date string to date object."""
    if not date_str:
        return None

    # Try common formats
    for fmt in ["%Y-%m-%d", "%Y%m%d", "%m/%d/%Y"]:
        try:
            return datetime.strptime(str(date_str), fmt).date()
        except ValueError:
            continue

    return None


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


def _log_embed(result: EmbedResult) -> None:
    """Log embedding result to JSONL file."""
    log_path = Path(_config.get("logging", {}).get("embed_log", "logs/rag_embed.jsonl"))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a") as f:
        f.write(
            json.dumps(
                {
                    "ts": datetime.now(UTC).isoformat(),
                    "doc": result.doc_id,
                    "doc_type": result.doc_type,
                    "model": result.embed_model,
                    "chunks": result.chunk_count,
                    "duration_ms": result.duration_ms,
                    "status": "success" if not result.error_message else "error",
                    "error": result.error_message,
                }
            )
            + "\n"
        )
