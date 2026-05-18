"""Two-pass entity/relationship extraction pipeline."""

import hashlib
import json
import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path

import requests
import yaml
from ratelimit import limits, sleep_and_retry
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ucx_kb.utils import is_real_document
from ucx_kb.validation import get_schema_for_path, validate_document
from . import EXTRACT_VERSION
from .exceptions import ExtractionError, GraphUnavailableError
from .layer import TradingGraph
from .models import EntityExtraction, ExtractionResult, RelationExtraction
from .normalize import dedupe_entities, normalize_entity
from .prompts import ENTITY_EXTRACTION_PROMPT, RELATION_EXTRACTION_PROMPT

log = logging.getLogger(__name__)

# Load configuration
_config_path = Path(__file__).parent / "config.yaml"
_config: dict = {}
_field_mappings: dict = {}


def _expand_env_vars(content: str) -> str:
    """Expand ${VAR} and ${VAR:-default} patterns in config."""
    import re

    # Match ${VAR:-default} or ${VAR}
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

_field_mappings_path = Path(__file__).parent / "field_mappings.yaml"
if _field_mappings_path.exists():
    with open(_field_mappings_path) as f:
        _field_mappings = yaml.safe_load(f)


def _get_default_extractor() -> str:
    """Get default extractor from env var or config.

    Priority: EXTRACT_PROVIDER env var > LLM_PROVIDER env var > config > ollama
    """
    # Check env vars directly (dotenv may not be loaded when config is parsed)
    extractor = os.getenv("EXTRACT_PROVIDER")
    if extractor:
        return extractor

    extractor = os.getenv("LLM_PROVIDER")
    if extractor:
        return extractor

    # Fall back to config (may have stale env expansion)
    extractor = _config.get("extraction", {}).get("default_extractor", "ollama")
    # Strip any trailing } from failed nested expansion
    return extractor.rstrip("}")


def extract_document(
    file_path: str,
    extractor: str | None = None,
    commit: bool = True,
    dry_run: bool = False,
) -> ExtractionResult:
    """
    Extract entities and relationships from a YAML document.

    Pipeline:
    1. Validate file (must be real document, not template)
    2. Parse YAML
    3. Load field mappings for document type
    4. Pass 1: Entity extraction (per field)
    5. Pass 2: Relationship extraction (whole document)
    6. Normalize all entities
    7. Apply confidence thresholds
    8. Commit to Neo4j (if commit=True and not dry_run)
    9. Log extraction result

    Args:
        file_path: Path to YAML document
        extractor: LLM backend (ollama, claude-api, openrouter)
        commit: Whether to commit to Neo4j
        dry_run: If True, don't commit even if commit=True

    Returns:
        ExtractionResult with entities and relations
    """
    # Use default extractor from config if not specified
    if extractor is None:
        extractor = _get_default_extractor()

    # Validate file
    if not is_real_document(file_path):
        raise ExtractionError(f"Not a real document (template?): {file_path}")

    if not Path(file_path).exists():
        raise ExtractionError(f"File not found: {file_path}")

    # Parse YAML
    with open(file_path) as f:
        doc = yaml.safe_load(f)

    if not doc:
        raise ExtractionError(f"Empty or invalid YAML: {file_path}")

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

    # Compute hash
    with open(file_path, "rb") as f:
        text_hash = hashlib.sha256(f.read()).hexdigest()[:16]

    # Get field mappings
    mappings = _field_mappings.get(doc_type, {})
    extract_fields = mappings.get("extract_fields", [])
    skip_fields = mappings.get("skip_fields", ["_meta", "_graph", "_links"])

    # Initialize result
    result = ExtractionResult(
        source_doc_id=doc_id,
        source_doc_type=doc_type,
        source_file_path=file_path,
        source_text_hash=text_hash,
        extracted_at=datetime.now(UTC),
        extractor=extractor,
        extraction_version=EXTRACT_VERSION,
    )

    # Pass 1: Entity extraction
    all_entities = []
    timeout = int(_config.get("extraction", {}).get("timeout_seconds", 30))

    for field_path in extract_fields:
        try:
            text = _get_field_value(doc, field_path)
            if not text:
                continue

            entities = _extract_entities_from_field(text, extractor, timeout)
            all_entities.extend(entities)
            result.fields_processed += 1

        except Exception as e:
            log.warning(f"Failed to extract from {field_path}: {e}")
            result.fields_failed += 1

    # Normalize and dedupe entities
    normalized_entities = [normalize_entity(e) for e in all_entities]
    unique_entities = dedupe_entities(normalized_entities)

    # Convert to EntityExtraction objects
    result.entities = [
        EntityExtraction(
            type=e["type"],
            value=e["value"],
            confidence=e.get("confidence", 0.5),
            evidence=e.get("evidence", ""),
            properties=e.get("properties", {}),
            needs_review=0.5 <= e.get("confidence", 0.5) < 0.7,
        )
        for e in unique_entities
    ]

    # Pass 2: Relationship extraction
    if result.entities:
        full_text = _flatten_doc_for_relations(doc, skip_fields)
        relations = _extract_relations_from_entities(result.entities, full_text, extractor, timeout)
        result.relations = relations

    # Apply confidence thresholds
    result = _apply_confidence_thresholds(result)

    # Commit to Neo4j
    if commit and not dry_run:
        try:
            _commit_to_graph(result)
            result.committed = True
        except GraphUnavailableError as e:
            log.warning(f"Graph unavailable, queuing for retry: {e}")
            _queue_pending_commit(result)
        except Exception as e:
            log.error(f"Failed to commit: {e}")
            result.error_message = str(e)

    # Log result
    _log_extraction(result)

    return result


def extract_text(
    text: str,
    doc_type: str,
    doc_id: str,
    source_url: str | None = None,
    extractor: str | None = None,
) -> ExtractionResult:
    """Extract from raw text (for external content)."""
    # Use default extractor from config if not specified
    if extractor is None:
        extractor = _get_default_extractor()

    text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
    timeout = int(_config.get("extraction", {}).get("timeout_seconds", 60))

    result = ExtractionResult(
        source_doc_id=doc_id,
        source_doc_type=doc_type,
        source_file_path=source_url or "text",
        source_text_hash=text_hash,
        extracted_at=datetime.now(UTC),
        extractor=extractor,
        extraction_version=EXTRACT_VERSION,
    )

    # Extract entities
    entities = _extract_entities_from_field(text, extractor, timeout)
    normalized = [normalize_entity(e) for e in entities]
    unique = dedupe_entities(normalized)

    result.entities = [
        EntityExtraction(
            type=e["type"],
            value=e["value"],
            confidence=e.get("confidence", 0.5),
            evidence=e.get("evidence", ""),
        )
        for e in unique
    ]

    # Extract relationships
    if result.entities:
        result.relations = _extract_relations_from_entities(
            result.entities, text, extractor, timeout
        )

    result = _apply_confidence_thresholds(result)
    return result


def _get_field_value(doc: dict, field_path: str) -> str | None:
    """Extract field value from YAML document using dot notation."""
    # Handle array notation: "risks[].risk"
    parts = field_path.replace("[]", "[*]").split(".")
    current = doc

    for part in parts:
        if current is None:
            return None

        if "[*]" in part:
            # Array access
            key = part.replace("[*]", "")
            if key:
                current = current.get(key, [])
            if not isinstance(current, list):
                return None
            # Collect all values from array
            values = []
            for item in current:
                if isinstance(item, dict):
                    remaining = ".".join(parts[parts.index(part) + 1 :])
                    if remaining:
                        val = _get_field_value(item, remaining)
                        if val:
                            values.append(val)
                    else:
                        values.append(str(item))
                else:
                    values.append(str(item))
            return "\n".join(values) if values else None
        else:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None

    if current is None:
        return None
    if isinstance(current, (list, dict)):
        return yaml.dump(current, default_flow_style=False)
    return str(current)


def _flatten_doc_for_relations(doc: dict, skip_fields: list[str]) -> str:
    """Flatten document to text for relationship extraction."""

    def flatten(obj, prefix=""):
        lines = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in skip_fields:
                    continue
                lines.extend(flatten(v, f"{prefix}{k}: "))
        elif isinstance(obj, list):
            for item in obj:
                lines.extend(flatten(item, prefix))
        else:
            lines.append(f"{prefix}{obj}")
        return lines

    return "\n".join(flatten(doc))


def _infer_doc_type(file_path: str) -> str:
    """Infer document type from file path."""
    path = Path(file_path)

    # Check parent directory name
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


def _get_generation_options() -> dict:
    """Get LLM generation options from config."""
    gen_config = _config.get("extraction", {}).get("generation", {})
    options = {}

    if gen_config.get("temperature"):
        options["temperature"] = float(gen_config["temperature"])
    if gen_config.get("num_predict"):
        options["num_predict"] = int(gen_config["num_predict"])
    if gen_config.get("top_p"):
        options["top_p"] = float(gen_config["top_p"])
    if gen_config.get("top_k"):
        options["top_k"] = int(gen_config["top_k"])

    return options


@sleep_and_retry
@limits(calls=45, period=1)  # Ollama rate limit: 45 req/sec
def _call_ollama_rate_limited(prompt: str, model: str, timeout: int) -> str:
    """Rate-limited Ollama API call."""
    base_url = (
        _config.get("extraction", {}).get("ollama", {}).get("base_url", "http://localhost:11434")
    )
    gen_options = _get_generation_options()

    payload = {"model": model, "prompt": prompt, "stream": False}
    if gen_options:
        payload["options"] = gen_options

    response = requests.post(
        f"{base_url}/api/generate",
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["response"]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=10, max=30),
    retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
)
def _extract_entities_from_field(text: str, extractor: str, timeout: int) -> list[dict]:
    """Pass 1: Extract entities from a single text field."""
    prompt = ENTITY_EXTRACTION_PROMPT.format(text=text)

    if extractor == "ollama":
        model = _config.get("extraction", {}).get("ollama", {}).get("model", "qwen3:8b")
        response = _call_ollama_rate_limited(prompt, model, timeout)
    else:
        response = _call_cloud_llm(prompt, extractor, timeout)

    return _parse_json_response(response)


def _extract_relations_from_entities(
    entities: list[EntityExtraction],
    full_text: str,
    extractor: str,
    timeout: int,
) -> list[RelationExtraction]:
    """Pass 2: Extract relationships given discovered entities."""
    entities_json = json.dumps([{"type": e.type, "value": e.value} for e in entities])

    prompt = RELATION_EXTRACTION_PROMPT.format(
        entities_json=entities_json,
        text=full_text[:4000],  # Limit text length
    )

    if extractor == "ollama":
        model = _config.get("extraction", {}).get("ollama", {}).get("model", "qwen3:8b")
        response = _call_ollama_rate_limited(prompt, model, timeout)
    else:
        response = _call_cloud_llm(prompt, extractor, timeout)

    raw_relations = _parse_json_response(response)

    # Convert to RelationExtraction objects
    relations = []
    for r in raw_relations:
        from_data = r.get("from", {})
        to_data = r.get("to", {})

        relations.append(
            RelationExtraction(
                from_entity=EntityExtraction(
                    type=from_data.get("type", ""),
                    value=from_data.get("value", ""),
                    confidence=r.get("confidence", 0.5),
                    evidence="",
                ),
                relation=r.get("relation", ""),
                to_entity=EntityExtraction(
                    type=to_data.get("type", ""),
                    value=to_data.get("value", ""),
                    confidence=r.get("confidence", 0.5),
                    evidence="",
                ),
                confidence=r.get("confidence", 0.5),
                evidence=r.get("evidence", ""),
            )
        )

    return relations


def _call_cloud_llm(prompt: str, extractor: str, timeout: int) -> str:
    """Call cloud LLM (Claude API, OpenRouter, or OpenAI)."""
    gen_config = _config.get("extraction", {}).get("generation", {})
    max_tokens = int(gen_config.get("max_tokens", 2000))
    temperature = float(gen_config.get("temperature", 0.1))

    if extractor == "claude-api":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        model = (
            _config.get("extraction", {})
            .get("claude_api", {})
            .get("model", "claude-sonnet-4-20250514")
        )
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]

    elif extractor == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        model = (
            _config.get("extraction", {})
            .get("openrouter", {})
            .get("model", "anthropic/claude-3-5-sonnet")
        )
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    elif extractor == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        model = _config.get("extraction", {}).get("openai", {}).get("model", "gpt-4o-mini")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    raise ExtractionError(f"Unknown extractor: {extractor}")


def _parse_json_response(response: str) -> list[dict]:
    """Parse JSON from LLM response with error handling."""
    response = response.strip()

    # Try to extract JSON array from response
    # LLMs sometimes wrap in markdown code blocks
    if response.startswith("```"):
        lines = response.split("```")
        if len(lines) >= 2:
            response = lines[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()

    # Try to find JSON array
    match = re.search(r"\[.*\]", response, re.DOTALL)
    if match:
        response = match.group()

    try:
        result = json.loads(response)
        if isinstance(result, list):
            return result
        return []
    except json.JSONDecodeError as e:
        log.warning(f"Failed to parse JSON response: {e}")
        log.debug(f"Raw response: {response[:500]}")
        return []


def _apply_confidence_thresholds(result: ExtractionResult) -> ExtractionResult:
    """
    Apply confidence thresholds:
    - >= commit_threshold (0.7): include normally
    - >= flag_threshold (0.5): include with needs_review=True
    - < flag_threshold: exclude from result
    """
    extraction_config = _config.get("extraction", {})
    commit_threshold = float(extraction_config.get("commit_threshold", 0.7))
    flag_threshold = float(extraction_config.get("flag_threshold", 0.5))

    # Filter entities
    filtered_entities = []
    for e in result.entities:
        if e.confidence >= commit_threshold:
            filtered_entities.append(e)
        elif e.confidence >= flag_threshold:
            e.needs_review = True
            filtered_entities.append(e)
        # < flag_threshold: skip

    result.entities = filtered_entities

    # Filter relations
    filtered_relations = []
    for r in result.relations:
        if r.confidence >= flag_threshold:
            filtered_relations.append(r)

    result.relations = filtered_relations

    return result


def _commit_to_graph(result: ExtractionResult) -> None:
    """Commit extraction result to Neo4j."""
    with TradingGraph() as graph:
        # Create document node
        graph.merge_node(
            "Document",
            "id",
            {
                "id": result.source_doc_id,
                "file_path": result.source_file_path,
                "doc_type": result.source_doc_type,
                "extraction_version": result.extraction_version,
                "extracted_at": result.extracted_at.isoformat(),
            },
        )

        # Create entity nodes
        for entity in result.entities:
            key_prop = "symbol" if entity.type == "Ticker" else "name"
            if entity.type in ("Analysis", "Trade", "Learning", "Document"):
                key_prop = "id"

            props = {
                key_prop: entity.value,
                "extraction_version": result.extraction_version,
            }
            props.update(entity.properties)

            if entity.needs_review:
                props["needs_review"] = True

            graph.merge_node(entity.type, key_prop, props)

            # Link to document
            graph.merge_relation(
                (entity.type, key_prop, entity.value),
                "EXTRACTED_FROM",
                ("Document", "id", result.source_doc_id),
                {"confidence": entity.confidence, "evidence": entity.evidence[:200]},
            )

        # Create relationships
        for rel in result.relations:
            from_key = "symbol" if rel.from_entity.type == "Ticker" else "name"
            to_key = "symbol" if rel.to_entity.type == "Ticker" else "name"

            if rel.from_entity.type in ("Analysis", "Trade", "Learning"):
                from_key = "id"
            if rel.to_entity.type in ("Analysis", "Trade", "Learning"):
                to_key = "id"

            graph.merge_relation(
                (rel.from_entity.type, from_key, rel.from_entity.value),
                rel.relation,
                (rel.to_entity.type, to_key, rel.to_entity.value),
                rel.properties,
            )


def _queue_pending_commit(result: ExtractionResult) -> None:
    """Queue failed commit to pending_commits.jsonl for retry."""
    log_path = Path(_config.get("logging", {}).get("pending_commits", "logs/pending_commits.jsonl"))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a") as f:
        f.write(
            json.dumps(
                {
                    "ts": datetime.now(UTC).isoformat(),
                    "doc": result.source_doc_id,
                    "file_path": result.source_file_path,
                    "reason": result.error_message or "unknown",
                    "retry_count": 0,
                }
            )
            + "\n"
        )


def _log_extraction(result: ExtractionResult) -> None:
    """Log extraction result to JSONL file."""
    log_path = Path(
        _config.get("logging", {}).get("extraction_log", "logs/graph_extractions.jsonl")
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a") as f:
        f.write(
            json.dumps(
                {
                    "ts": datetime.now(UTC).isoformat(),
                    "doc": result.source_doc_id,
                    "doc_type": result.source_doc_type,
                    "extractor": result.extractor,
                    "entities": len(result.entities),
                    "relations": len(result.relations),
                    "committed": result.committed,
                    "error": result.error_message,
                }
            )
            + "\n"
        )
