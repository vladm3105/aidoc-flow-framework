#!/usr/bin/env python3
"""
Diagram Consistency Validator for SDD Documents

Validates that Mermaid diagrams match prose claims about components.

Error Codes:
- DIAG-E001: Diagram-text component mismatch
- DIAG-E002: Missing diagram for architecture section
- DIAG-W001: Diagram count differs from text claim
- DIAG-W002: Node label not referenced in text
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

from error_codes import format_error, calculate_exit_code


def extract_mermaid_blocks(content: str) -> List[Tuple[str, int]]:
    """Extract Mermaid code blocks with their line numbers."""
    blocks = []
    pattern = r'```mermaid\s*\n(.*?)```'

    for match in re.finditer(pattern, content, re.DOTALL):
        # Calculate line number
        line_num = content[:match.start()].count('\n') + 1
        blocks.append((match.group(1), line_num))

    return blocks


def parse_mermaid_nodes(mermaid_code: str) -> Set[str]:
    """Extract node labels from Mermaid diagram code."""
    nodes = set()

    # Match various Mermaid node patterns
    patterns = [
        # flowchart: A[Label] or A(Label) or A{Label} or A((Label))
        r'(\w+)\s*[\[\(\{]+([^\]\)\}]+)',
        # flowchart: A["Label"] or A('Label')
        r'(\w+)\s*[\[\(\{]+["\']([^"\']+)',
        # graph: node definitions like "Server1[API Server]"
        r'(\w+)\[([^\]]+)\]',
        # subgraph titles
        r'subgraph\s+(\w+)\s*\[?([^\]\n]*)',
        # C4 model elements: Container, Component, System
        r'(?:Container|Component|System|Person)(?:_Boundary)?\s*\(\s*(\w+)\s*,\s*"([^"]+)"',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, mermaid_code):
            # Add both the ID and the label
            node_id = match.group(1).strip()
            label = match.group(2).strip() if match.group(2) else node_id

            # Clean up the label
            label = re.sub(r'["\'\[\]\(\)\{\}]', '', label).strip()

            if label and len(label) > 1:  # Skip single characters
                nodes.add(label)
            if node_id and len(node_id) > 1:
                nodes.add(node_id)

    return nodes


def extract_count_claims(content: str) -> List[Tuple[int, str, int]]:
    """
    Extract count claims from text like "5 servers" or "3 components".

    Returns list of (count, item_type, line_number)
    """
    claims = []

    # Common countable items in architecture docs
    countable_items = [
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

    pattern = r'\b(\d+)\s+(' + '|'.join(countable_items) + r')\b'

    for match in re.finditer(pattern, content, re.IGNORECASE):
        count = int(match.group(1))
        item_type = match.group(2).lower()
        line_num = content[:match.start()].count('\n') + 1
        claims.append((count, item_type, line_num))

    return claims


def get_surrounding_text(content: str, diagram_start: int, diagram_end: int) -> str:
    """Get text surrounding a diagram (previous and next paragraphs)."""
    # Find paragraph before diagram
    before_text = content[:diagram_start]
    para_start = before_text.rfind('\n\n')
    para_start = para_start + 2 if para_start != -1 else 0

    # Find paragraph after diagram
    after_text = content[diagram_end:]
    para_end = after_text.find('\n\n')
    para_end = diagram_end + para_end if para_end != -1 else len(content)

    return content[para_start:para_end]


def check_nodes_in_text(nodes: Set[str], text: str) -> Set[str]:
    """Check which nodes are mentioned in the surrounding text."""
    unreferenced = set()
    text_lower = text.lower()

    for node in nodes:
        # Check if node label appears in text (case-insensitive)
        if node.lower() not in text_lower:
            # Try partial match for compound names
            words = node.split()
            if not any(word.lower() in text_lower for word in words if len(word) > 2):
                unreferenced.add(node)

    return unreferenced


def validate_diagram_consistency(
    filepath: str
) -> Tuple[List[str], List[str]]:
    """
    Validate diagram consistency in a document.

    Args:
        filepath: Path to markdown file

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(filepath)

    # Extract Mermaid diagrams
    mermaid_blocks = extract_mermaid_blocks(content)

    # Check for architecture sections without diagrams
    arch_sections = re.findall(
        r'^##\s+.*(?:Architecture|System Design|Infrastructure|Deployment).*$',
        content,
        re.MULTILINE | re.IGNORECASE
    )

    if arch_sections and not mermaid_blocks:
        errors.append(format_error(
            "DIAG-E002",
            f"{filename}: Architecture section found but no Mermaid diagram"
        ))

    # Validate each diagram
    for mermaid_code, line_num in mermaid_blocks:
        nodes = parse_mermaid_nodes(mermaid_code)

        if not nodes:
            continue

        # Get surrounding text
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

            for node in unreferenced:
                warnings.append(format_error(
                    "DIAG-W002",
                    f"{filename}:{line_num}: Node '{node}' not referenced in surrounding text"
                ))

    # Check count claims vs diagram
    count_claims = extract_count_claims(content)

    for mermaid_code, diagram_line in mermaid_blocks:
        nodes = parse_mermaid_nodes(mermaid_code)
        node_count = len(nodes)

        for claimed_count, item_type, claim_line in count_claims:
            # Check if claim is near this diagram
            if abs(claim_line - diagram_line) < 20:  # Within 20 lines
                # Rough heuristic: if claim count differs significantly
                if claimed_count > 1 and abs(claimed_count - node_count) > 1:
                    # Only warn if the difference is significant
                    if item_type in ['component', 'components', 'node', 'nodes',
                                     'server', 'servers', 'service', 'services']:
                        warnings.append(format_error(
                            "DIAG-W001",
                            f"{filename}:{claim_line}: Text claims {claimed_count} {item_type}, "
                            f"diagram near line {diagram_line} has {node_count} nodes"
                        ))

    return errors, warnings


def find_markdown_files(directory: str) -> List[str]:
    """Find all markdown files in a directory tree."""
    md_files = []

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                md_files.append(os.path.join(root, filename))

    return md_files


def main():
    parser = argparse.ArgumentParser(
        description="Validate Mermaid diagram consistency with prose"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to markdown file or directory to scan"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    args = parser.parse_args()

    all_errors = []
    all_warnings = []

    if os.path.isfile(args.path):
        errors, warnings = validate_diagram_consistency(args.path)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    else:
        md_files = find_markdown_files(args.path)

        for filepath in md_files:
            errors, warnings = validate_diagram_consistency(filepath)
            all_errors.extend(errors)
            all_warnings.extend(warnings)

    # Output results
    for error in all_errors:
        print(error)
    for warning in all_warnings:
        print(warning)

    # Summary
    if all_errors or all_warnings:
        print(f"\nSummary: {len(all_errors)} error(s), {len(all_warnings)} warning(s)")
    else:
        print("Diagram consistency validation passed")

    sys.exit(calculate_exit_code(all_errors, all_warnings, args.strict))


if __name__ == "__main__":
    main()
