"""Diagram consistency validation for SDD documents.

Validates that Mermaid diagrams match prose claims about components.

Error Codes:
- DIAG-E001: Missing diagram for architecture section
- DIAG-W001: Diagram count differs from text claim
- DIAG-W002: Node label not referenced in surrounding text
- DIAG-W003: SVG file referenced but not found
"""

import re
from pathlib import Path
from typing import List, Optional, Set, Tuple

from ucx.validators.common.result import (
    UnifiedValidationResult,
    ValidationTier,
)

# Mermaid code block pattern
MERMAID_BLOCK_PATTERN = re.compile(r'```mermaid\s*\n(.*?)```', re.DOTALL)

# Architecture section headers (for visual system architecture diagrams)
# Excludes Architecture Decision Topics (ADT), Architecture Decision Records (ADR)
# which describe decisions, not visual system architecture
ARCH_SECTION_PATTERN = re.compile(
    r'^##\s+.*(?:Architecture|System Design|Infrastructure|Deployment).*$',
    re.MULTILINE | re.IGNORECASE
)

# Exclusion patterns for architecture decision sections (not visual architecture)
ARCH_DECISION_EXCLUSION_PATTERN = re.compile(
    r'(?:Decision|ADT|ADR|Topic|Record|Overview)',
    re.IGNORECASE
)

# SVG reference patterns
SVG_REF_PATTERN = re.compile(r'!\[[^\]]*\]\(([^)]+\.svg)\)')

# Countable architecture items
COUNTABLE_ITEMS = [
    'server', 'servers',
    'component', 'components',
    'service', 'services',
    'layer', 'layers',
    'node', 'nodes',
    'container', 'containers',
    'module', 'modules',
    'database', 'databases',
    'endpoint', 'endpoints',
    'api', 'apis',
    'system', 'systems',
    'interface', 'interfaces',
]


def extract_mermaid_blocks(content: str) -> List[Tuple[str, int]]:
    """
    Extract Mermaid code blocks with their line numbers.

    Returns:
        List of (mermaid_code, line_number)
    """
    blocks = []

    for match in MERMAID_BLOCK_PATTERN.finditer(content):
        line_num = content[:match.start()].count('\n') + 1
        blocks.append((match.group(1), line_num))

    return blocks


def parse_mermaid_nodes(mermaid_code: str) -> Set[str]:
    """Extract node labels from Mermaid diagram code."""
    nodes = set()

    # Various Mermaid node patterns
    patterns = [
        # flowchart: A[Label] or A(Label) or A{Label} or A((Label))
        r'(\w+)\s*[\[\(\{]+([^\]\)\}]+)',
        # flowchart: A["Label"] or A('Label')
        r'(\w+)\s*[\[\(\{]+["\']([^"\']+)',
        # graph: node definitions
        r'(\w+)\[([^\]]+)\]',
        # subgraph titles
        r'subgraph\s+(\w+)\s*\[?([^\]\n]*)',
        # C4 model elements
        r'(?:Container|Component|System|Person)(?:_Boundary)?\s*\(\s*(\w+)\s*,\s*"([^"]+)"',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, mermaid_code):
            node_id = match.group(1).strip()
            label = match.group(2).strip() if match.group(2) else node_id

            # Clean up the label
            label = re.sub(r'["\'\[\]\(\)\{\}]', '', label).strip()

            if label and len(label) > 1:
                nodes.add(label)
            if node_id and len(node_id) > 1:
                nodes.add(node_id)

    return nodes


def extract_count_claims(content: str) -> List[Tuple[int, str, int]]:
    """
    Extract count claims from text.

    Returns:
        List of (count, item_type, line_number)

    Note: Uses negative lookbehind to avoid matching:
    - Ranges like "3-10 nodes" (would incorrectly extract "10")
    - Section numbers like "## 5.2 components"
    - Version numbers like "v1.2 services"
    """
    claims = []
    # Use negative lookbehind to avoid matching after ., -, or digits
    safe_prefix = r'(?<![.\d-])'
    pattern = safe_prefix + r'\b(\d+)\s+(' + '|'.join(COUNTABLE_ITEMS) + r')\b'

    lines = content.splitlines()
    for line_no, line in enumerate(lines, start=1):
        for match in re.finditer(pattern, line, re.IGNORECASE):
            count = int(match.group(1))
            item_type = match.group(2).lower()
            claims.append((count, item_type, line_no))

    return claims


def get_surrounding_text(
    content: str,
    diagram_start: int,
    diagram_end: int,
    context_lines: int = 10
) -> str:
    """Get text surrounding a diagram."""
    lines = content.splitlines()
    start_line = content[:diagram_start].count('\n')
    end_line = content[:diagram_end].count('\n')

    # Get context before and after
    before_start = max(0, start_line - context_lines)
    after_end = min(len(lines), end_line + context_lines)

    return '\n'.join(lines[before_start:after_end])


def check_nodes_in_text(nodes: Set[str], text: str) -> Set[str]:
    """Check which nodes are NOT mentioned in the surrounding text."""
    unreferenced = set()
    text_lower = text.lower()

    for node in nodes:
        # Skip generic node names
        if node.lower() in ['a', 'b', 'c', 'd', 'e', 'start', 'end']:
            continue

        # Check if node label appears in text
        if node.lower() not in text_lower:
            # Try partial match for compound names
            words = node.split()
            if not any(word.lower() in text_lower for word in words if len(word) > 2):
                unreferenced.add(node)

    return unreferenced


def extract_svg_references(content: str) -> List[Tuple[str, int]]:
    """
    Extract SVG file references from content.

    Returns:
        List of (svg_path, line_number)
    """
    refs = []
    lines = content.splitlines()

    for line_no, line in enumerate(lines, start=1):
        for match in SVG_REF_PATTERN.finditer(line):
            refs.append((match.group(1), line_no))

    return refs


def validate_diagrams(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """
    Validate diagram consistency in a document.

    Args:
        content: File content
        file_path: Path to file
        result: Result to populate
    """
    # Extract Mermaid diagrams
    mermaid_blocks = extract_mermaid_blocks(content)

    # Check for architecture sections without diagrams
    arch_sections = ARCH_SECTION_PATTERN.findall(content)

    # Filter out architecture decision sections (ADT, ADR, Topic, etc.)
    # These describe decisions, not visual system architecture
    visual_arch_sections = [
        section for section in arch_sections
        if not ARCH_DECISION_EXCLUSION_PATTERN.search(section)
    ]

    if visual_arch_sections and not mermaid_blocks:
        # Check if SVG diagrams are present instead
        svg_refs = extract_svg_references(content)
        if not svg_refs:
            result.add_issue(
                "DIAG-E001",
                file_path=file_path,
                context="Architecture section found but no diagram (Mermaid or SVG)",
                tier=ValidationTier.TIER1,  # E001 = Error, must be Tier 1
            )

    # Validate SVG references exist
    for svg_path, line_no in extract_svg_references(content):
        # Resolve relative path
        svg_full_path = (file_path.parent / svg_path).resolve()
        if not svg_full_path.exists():
            result.add_issue(
                "DIAG-W003",
                file_path=file_path,
                line=line_no,
                context=f"SVG file not found: {svg_path}",
                tier=ValidationTier.TIER2,
            )

    # Validate each Mermaid diagram
    for mermaid_code, diagram_line in mermaid_blocks:
        nodes = parse_mermaid_nodes(mermaid_code)

        if not nodes:
            continue

        # Find the diagram in content to get surrounding text
        diagram_match = re.search(
            r'```mermaid\s*\n' + re.escape(mermaid_code) + r'```',
            content
        )
        if diagram_match:
            surrounding_text = get_surrounding_text(
                content,
                diagram_match.start(),
                diagram_match.end()
            )

            # Check nodes referenced in text
            unreferenced = check_nodes_in_text(nodes, surrounding_text)

            for node in list(unreferenced)[:3]:  # Limit to 3 warnings per diagram
                result.add_issue(
                    "DIAG-W002",
                    file_path=file_path,
                    line=diagram_line,
                    context=f"Node '{node}' not referenced in surrounding text",
                    tier=ValidationTier.TIER2,
                )

    # Check count claims vs diagram node counts
    count_claims = extract_count_claims(content)

    for mermaid_code, diagram_line in mermaid_blocks:
        nodes = parse_mermaid_nodes(mermaid_code)
        node_count = len(nodes)

        for claimed_count, item_type, claim_line in count_claims:
            # Check if claim is near this diagram (within 20 lines)
            if abs(claim_line - diagram_line) < 20:
                # Only warn if difference is significant
                if claimed_count > 1 and abs(claimed_count - node_count) > 2:
                    if item_type in ['component', 'components', 'node', 'nodes',
                                     'server', 'servers', 'service', 'services']:
                        result.add_issue(
                            "DIAG-W001",
                            file_path=file_path,
                            line=claim_line,
                            context=(
                                f"Text claims {claimed_count} {item_type}, "
                                f"diagram (line {diagram_line}) has {node_count} nodes"
                            ),
                            tier=ValidationTier.TIER2,
                        )


__all__ = [
    "validate_diagrams",
    "extract_mermaid_blocks",
    "parse_mermaid_nodes",
]
