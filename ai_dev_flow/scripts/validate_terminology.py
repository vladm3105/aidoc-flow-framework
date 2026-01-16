#!/usr/bin/env python3
"""
Terminology Consistency Validator for SDD Documents

Validates terminology and acronym usage across documents.
Supports auto-fix for inconsistent term capitalization.

Error Codes:
- TERM-E001: Conflicting term definition
- TERM-E002: Undefined acronym
- TERM-W001: Inconsistent term usage
- TERM-W002: Missing glossary entry
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from error_codes import format_error, calculate_exit_code


def extract_glossary(content: str) -> Dict[str, str]:
    """
    Extract glossary entries from document.

    Returns dict of term -> definition
    """
    glossary = {}

    # Find glossary section
    glossary_match = re.search(
        r'^##\s+(?:\d+\.\s*)?Glossary.*?\n(.*?)(?=^##\s|\Z)',
        content,
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    if not glossary_match:
        return glossary

    glossary_section = glossary_match.group(1)

    # Parse glossary entries in various formats
    # Format 1: **Term**: Definition
    for match in re.finditer(r'\*\*([^*]+)\*\*:\s*(.+?)(?=\n\*\*|\n\n|\Z)', glossary_section, re.DOTALL):
        term = match.group(1).strip()
        definition = match.group(2).strip()
        glossary[term.lower()] = definition

    # Format 2: - **Term**: Definition
    for match in re.finditer(r'-\s*\*\*([^*]+)\*\*:\s*(.+?)(?=\n-|\n\n|\Z)', glossary_section, re.DOTALL):
        term = match.group(1).strip()
        definition = match.group(2).strip()
        glossary[term.lower()] = definition

    # Format 3: | Term | Definition |
    for match in re.finditer(r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|', glossary_section):
        term = match.group(1).strip()
        definition = match.group(2).strip()
        if term.lower() not in ['term', 'definition', '---', '-']:  # Skip headers
            glossary[term.lower()] = definition

    return glossary


def extract_acronym_definitions(content: str) -> Dict[str, Tuple[str, int]]:
    """
    Extract acronym definitions from content.

    Returns dict of acronym -> (full_form, line_number)
    """
    acronyms = {}

    # Pattern: Full Name (ACRONYM)
    pattern1 = r'([A-Z][a-zA-Z\s]+)\s+\(([A-Z]{2,})\)'

    # Pattern: ACRONYM (Full Name)
    pattern2 = r'([A-Z]{2,})\s+\(([A-Z][a-zA-Z\s]+)\)'

    for match in re.finditer(pattern1, content):
        full_name = match.group(1).strip()
        acronym = match.group(2)
        line_num = content[:match.start()].count('\n') + 1
        acronyms[acronym] = (full_name, line_num)

    for match in re.finditer(pattern2, content):
        acronym = match.group(1)
        full_name = match.group(2).strip()
        line_num = content[:match.start()].count('\n') + 1
        if acronym not in acronyms:  # Don't override first definition
            acronyms[acronym] = (full_name, line_num)

    return acronyms


def find_undefined_acronyms(content: str, defined_acronyms: Set[str]) -> List[Tuple[str, int]]:
    """
    Find undefined acronyms in content.

    Returns list of (acronym, line_number)
    """
    undefined = []

    # Common acronyms that don't need definition
    well_known = {
        'API', 'REST', 'HTTP', 'HTTPS', 'URL', 'URI', 'JSON', 'XML', 'HTML', 'CSS',
        'SQL', 'TCP', 'IP', 'UDP', 'SSL', 'TLS', 'SSH', 'FTP', 'SMTP', 'DNS',
        'AWS', 'GCP', 'CLI', 'GUI', 'IDE', 'SDK', 'CDN', 'VM', 'CPU', 'RAM',
        'SSD', 'HDD', 'OS', 'UI', 'UX', 'ID', 'UUID', 'UTC', 'ISO', 'RFC',
        'YAML', 'CSV', 'PDF', 'JWT', 'OAuth', 'LDAP', 'SAML', 'SSO', 'MFA',
        'CI', 'CD', 'DevOps', 'SRE', 'SLA', 'SLO', 'SLI', 'KPI', 'OKR',
        'TODO', 'TBD', 'TBC', 'WIP', 'POC', 'MVP', 'EOF', 'ETL',
        # SDD specific
        'SDD', 'BRD', 'PRD', 'ADR', 'SYS', 'REQ', 'SPEC', 'IMPL', 'CTR',
        'TASKS', 'BDD', 'EARS', 'YAML', 'MD', 'MCP',
    }

    all_known = defined_acronyms | well_known

    # Find all uppercase letter sequences (potential acronyms)
    for match in re.finditer(r'\b([A-Z]{2,})\b', content):
        acronym = match.group(1)

        # Skip if defined or well-known
        if acronym in all_known:
            continue

        # Skip if appears to be a constant or code
        context = content[max(0, match.start()-20):min(len(content), match.end()+20)]
        if '`' in context or '_' in acronym:
            continue

        line_num = content[:match.start()].count('\n') + 1
        undefined.append((acronym, line_num))

    return undefined


def find_inconsistent_terms(content: str, glossary: Dict[str, str]) -> List[Tuple[str, str, int]]:
    """
    Find terms used with inconsistent capitalization.

    Returns list of (found_term, canonical_term, line_number)
    """
    inconsistencies = []

    for canonical_term in glossary.keys():
        # Build regex for case-insensitive search
        pattern = r'\b' + re.escape(canonical_term) + r'\b'

        for match in re.finditer(pattern, content, re.IGNORECASE):
            found_term = match.group(0)

            # Check if capitalization differs
            if found_term.lower() == canonical_term.lower() and found_term != canonical_term:
                line_num = content[:match.start()].count('\n') + 1
                inconsistencies.append((found_term, canonical_term, line_num))

    return inconsistencies


def find_conflicting_definitions(
    docs: List[Tuple[str, str]]  # List of (filepath, content)
) -> List[Tuple[str, str, str, str]]:
    """
    Find terms with conflicting definitions across documents.

    Returns list of (term, def1, file1, def2, file2)
    """
    conflicts = []
    term_definitions = defaultdict(list)  # term -> [(filepath, definition)]

    for filepath, content in docs:
        glossary = extract_glossary(content)
        for term, definition in glossary.items():
            term_definitions[term].append((filepath, definition))

    for term, defs in term_definitions.items():
        if len(defs) > 1:
            # Check if definitions differ
            unique_defs = set(d[1].lower().strip() for d in defs)
            if len(unique_defs) > 1:
                # Report conflict between first two differing definitions
                conflicts.append((
                    term,
                    defs[0][1],
                    defs[0][0],
                    defs[1][1],
                    defs[1][0]
                ))

    return conflicts


def validate_terminology(
    filepath: str,
    auto_fix: bool = False
) -> Tuple[List[str], List[str]]:
    """
    Validate terminology consistency in a document.

    Args:
        filepath: Path to markdown file
        auto_fix: If True, normalize term capitalization

    Returns:
        Tuple of (errors, warnings)
    """
    errors = []
    warnings = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(filepath)

    # Extract glossary and acronyms
    glossary = extract_glossary(content)
    acronym_defs = extract_acronym_definitions(content)
    defined_acronyms = set(acronym_defs.keys())

    # Check for undefined acronyms
    undefined = find_undefined_acronyms(content, defined_acronyms)

    # Deduplicate undefined acronyms
    seen_undefined = set()
    for acronym, line_num in undefined:
        if acronym not in seen_undefined:
            seen_undefined.add(acronym)
            errors.append(format_error(
                "TERM-E002",
                f"{filename}:{line_num}: Undefined acronym '{acronym}'"
            ))

    # Check for inconsistent term usage
    inconsistencies = find_inconsistent_terms(content, glossary)

    if inconsistencies and auto_fix:
        # Apply auto-fix
        for found_term, canonical_term, _ in set((f, c, 0) for f, c, _ in inconsistencies):
            pattern = r'\b' + re.escape(found_term) + r'\b'
            content = re.sub(pattern, canonical_term, content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        warnings.append(format_error(
            "TERM-W001",
            f"{filename}: Auto-fixed {len(set((f, c) for f, c, _ in inconsistencies))} term capitalization issues"
        ))
    else:
        for found_term, canonical_term, line_num in inconsistencies[:5]:  # Limit output
            warnings.append(format_error(
                "TERM-W001",
                f"{filename}:{line_num}: '{found_term}' should be '{canonical_term}'"
            ))

    # Check for legacy EARS terminology usage
    legacy_phrase = "Easy Approach to Requirements Syntax"
    if legacy_phrase in content:
        # Allow citations that explicitly frame legacy usage
        if ("EARS-inspired structured patterns" not in content
                and "In this framework, EARS stands for" not in content):
            warnings.append(format_error(
                "TERM-W003",
                f"{filename}: Replace legacy term with 'Event-Action-Response-State (Engineering Requirements)'"
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
        description="Validate terminology and acronym consistency"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to markdown file or directory to scan"
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Auto-fix term capitalization inconsistencies"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    parser.add_argument(
        "--cross-check",
        action="store_true",
        help="Check for conflicting definitions across documents"
    )

    args = parser.parse_args()

    all_errors = []
    all_warnings = []

    if os.path.isfile(args.path):
        errors, warnings = validate_terminology(args.path, args.auto_fix)
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    else:
        md_files = find_markdown_files(args.path)

        for filepath in md_files:
            errors, warnings = validate_terminology(filepath, args.auto_fix)
            all_errors.extend(errors)
            all_warnings.extend(warnings)

        # Cross-document validation
        if args.cross_check:
            docs = []
            for filepath in md_files:
                with open(filepath, 'r', encoding='utf-8') as f:
                    docs.append((filepath, f.read()))

            conflicts = find_conflicting_definitions(docs)
            for term, def1, file1, def2, file2 in conflicts:
                all_errors.append(format_error(
                    "TERM-E001",
                    f"Term '{term}' has conflicting definitions: "
                    f"'{def1[:50]}...' in {os.path.basename(file1)} vs "
                    f"'{def2[:50]}...' in {os.path.basename(file2)}"
                ))

    # Output results
    for error in all_errors:
        print(error)
    for warning in all_warnings:
        print(warning)

    # Summary
    if all_errors or all_warnings:
        print(f"\nSummary: {len(all_errors)} error(s), {len(all_warnings)} warning(s)")
    else:
        print("Terminology validation passed")

    sys.exit(calculate_exit_code(all_errors, all_warnings, args.strict))


if __name__ == "__main__":
    main()
