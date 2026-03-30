"""Link validation for SDD documents.

Validates:
- Internal relative link resolution
- Anchor existence in target files
- External link format

Error Codes:
- LINK-E001: Broken file link (file not found)
- LINK-E002: Broken anchor (anchor not found in target)
- LINK-W001: Placeholder link detected
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from ucx.validators.common.result import (
    UnifiedValidationResult,
    ValidationTier,
)

# Regex for markdown links
MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

# Ignore markers for link validation
IGNORE_START = re.compile(r'<!--\s*VALIDATOR:IGNORE-LINKS-START\s*-->')
IGNORE_END = re.compile(r'<!--\s*VALIDATOR:IGNORE-LINKS-END\s*-->')

# Placeholder patterns in links
PLACEHOLDER_PATTERNS = [
    re.compile(r'\[TBD\]', re.IGNORECASE),
    re.compile(r'\(TBD\)', re.IGNORECASE),
    re.compile(r'\(planned\)', re.IGNORECASE),
    re.compile(r'\(to be created\)', re.IGNORECASE),
    re.compile(r'\(coming soon\)', re.IGNORECASE),
]


def strip_ignored_regions(content: str) -> str:
    """Remove content inside validator ignore markers and code blocks."""
    # Remove ignore-marked regions
    content = re.sub(
        r'<!--\s*VALIDATOR:IGNORE-LINKS-START\s*-->.*?<!--\s*VALIDATOR:IGNORE-LINKS-END\s*-->',
        '',
        content,
        flags=re.DOTALL
    )
    # Remove fenced code blocks
    content = re.sub(r'```[\s\S]*?```', '', content)
    return content


def extract_traceability_section(content: str) -> Optional[str]:
    """Extract Traceability section content."""
    content = strip_ignored_regions(content)
    # Match any Traceability section number
    pattern = r'## \d+\. Traceability.*?(?=\n## |\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(0) if match else None


def extract_markdown_links(content: str) -> List[Tuple[str, str, int]]:
    """
    Extract all markdown links from content.

    Returns:
        List of (link_text, link_path, line_number)
    """
    links = []
    lines = content.splitlines()

    for line_no, line in enumerate(lines, start=1):
        for match in MARKDOWN_LINK_PATTERN.finditer(line):
            links.append((match.group(1), match.group(2), line_no))

    return links


def check_anchor_exists(target_path: Path, anchor: str) -> bool:
    """Check if an anchor exists in the target file."""
    try:
        target_content = target_path.read_text(encoding='utf-8')
    except Exception:
        return False

    # Check various anchor formats
    checks = [
        # Format 1: # ANCHOR (markdown header)
        f'#{anchor}' in target_content,
        # Format 2: {#anchor} (pandoc style)
        f'{{#{anchor}}}' in target_content,
        # Format 3: <a name="anchor"></a>
        f'<a name="{anchor}"' in target_content or f"<a name='{anchor}'" in target_content,
        # Format 4: id: anchor (YAML)
        f'id: {anchor}' in target_content,
        # Format 5: id="anchor" (HTML attribute)
        f'id="{anchor}"' in target_content or f"id='{anchor}'" in target_content,
        # Format 6: Header converted to anchor
        bool(re.search(f'#+ {anchor.replace("-", "[- ]")}', target_content, re.IGNORECASE)),
    ]

    return any(checks)


def validate_single_link(
    source_file: Path,
    link_text: str,
    link_path: str,
    line_no: int,
    result: UnifiedValidationResult,
) -> None:
    """Validate a single markdown link."""
    # Skip external URLs
    if link_path.startswith(('http://', 'https://', 'mailto:')):
        return

    # Skip anchor-only links (same document)
    if link_path.startswith('#'):
        return

    source_dir = source_file.parent

    # Split path and anchor
    if '#' in link_path:
        file_part, anchor_part = link_path.split('#', 1)
    else:
        file_part, anchor_part = link_path, None

    try:
        if file_part:
            target_path = (source_dir / file_part).resolve()

            # Check file exists
            if not target_path.exists():
                result.add_issue(
                    "LINK-E001",
                    file_path=source_file,
                    line=line_no,
                    context=f"File not found: {file_part}",
                    tier=ValidationTier.TIER2,
                )
                return

            # Check anchor exists
            if anchor_part:
                if not check_anchor_exists(target_path, anchor_part):
                    result.add_issue(
                        "LINK-E002",
                        file_path=source_file,
                        line=line_no,
                        context=f"Anchor not found: #{anchor_part} in {file_part}",
                        tier=ValidationTier.TIER2,
                    )
    except Exception as e:
        result.add_issue(
            "LINK-E001",
            file_path=source_file,
            line=line_no,
            context=f"Path resolution error: {e}",
            tier=ValidationTier.TIER2,
        )


def check_placeholder_links(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
) -> None:
    """Check for placeholder references in links."""
    lines = content.splitlines()

    for line_no, line in enumerate(lines, start=1):
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(line):
                result.add_issue(
                    "LINK-W001",
                    file_path=file_path,
                    line=line_no,
                    context=f"Placeholder link detected: {pattern.pattern}",
                    tier=ValidationTier.TIER2,
                )


def validate_links(
    content: str,
    file_path: Path,
    result: UnifiedValidationResult,
    traceability_only: bool = False,
) -> None:
    """
    Validate all links in a document.

    Args:
        content: File content
        file_path: Path to file
        result: Result to populate
        traceability_only: If True, only validate links in Traceability section
    """
    if traceability_only:
        section = extract_traceability_section(content)
        if not section:
            return  # No traceability section
        content = section

    # Strip ignored regions and code blocks
    cleaned_content = strip_ignored_regions(content)

    # Extract and validate links
    links = extract_markdown_links(cleaned_content)

    for link_text, link_path, line_no in links:
        validate_single_link(file_path, link_text, link_path, line_no, result)

    # Check for placeholder links
    check_placeholder_links(cleaned_content, file_path, result)


__all__ = [
    "validate_links",
    "extract_markdown_links",
    "check_anchor_exists",
]
