"""Custom prompts for LightRAG entity extraction."""

from pathlib import Path
import sys

# Add config to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))

from entity_types import CUSTOM_ENTITY_TYPES, ENTITY_TYPE_DESCRIPTIONS


def get_entity_extraction_prompt() -> str:
    """Generate entity extraction prompt for LightRAG.

    Returns:
        Formatted prompt string for entity extraction.
    """
    entity_list = "\n".join(
        f"- **{etype}**: {ENTITY_TYPE_DESCRIPTIONS[etype]}"
        for etype in CUSTOM_ENTITY_TYPES
    )

    return f"""You are an expert knowledge graph builder. Extract entities and relationships from the following text.

## Entity Types to Extract

{entity_list}

## Instructions

1. **Identify Entities**: Find all significant entities in the text that match the types above.
2. **Normalize Names**: Use consistent naming (e.g., "PayPal" not "PYPL" or "PayPal Holdings").
3. **Extract Relationships**: Identify how entities relate to each other.
4. **Be Thorough**: Extract all relevant entities, even if mentioned briefly.
5. **Be Precise**: Only extract entities clearly mentioned or strongly implied.

## Output Format

For each entity:
- Name: [normalized entity name]
- Type: [entity type from list above]
- Description: [brief context from the document]

For each relationship:
- Source: [entity name]
- Relationship: [relationship type]
- Target: [entity name]
- Context: [supporting evidence from text]

## Text to Analyze

{{text}}

## Extracted Entities and Relationships
"""


def get_query_prompt(mode: str = "hybrid") -> str:
    """Generate query prompt based on mode.

    Args:
        mode: Query mode (local, global, hybrid, naive, mix).

    Returns:
        Query prompt string.
    """
    base_prompt = """Answer the question based on the provided context from the knowledge graph.

Context:
{context}

Question: {query}

Instructions:
- Use ONLY information from the provided context
- If the context doesn't contain enough information, say so
- Cite specific entities and relationships when relevant
- Be concise but thorough
"""

    mode_additions = {
        "local": "\n- Focus on specific entities directly mentioned in the question",
        "global": "\n- Consider broader themes and patterns across the knowledge graph",
        "hybrid": "\n- Balance specific entity information with broader context",
        "naive": "",
        "mix": "\n- Combine direct retrieval with graph-based context",
    }

    return base_prompt + mode_additions.get(mode, "")


def get_relationship_extraction_prompt() -> str:
    """Generate relationship extraction prompt.

    Returns:
        Relationship extraction prompt string.
    """
    return """Extract relationships between entities in the following text.

Common relationship types:
- develops, uses, competes_with, reports_to, founded
- announced, measured_by, addresses, requires, contradicts
- supports, governs, affects, mitigates

For each relationship, provide:
1. Source entity name
2. Relationship type
3. Target entity name
4. Brief context/evidence

Text:
{text}

Relationships:
"""
