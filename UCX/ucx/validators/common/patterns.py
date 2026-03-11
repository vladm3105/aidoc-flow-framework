"""Shared regex patterns for UCX validators.

Provides centralized pattern definitions for:
- YAML frontmatter
- Element IDs by document type
- Section headings
- Traceability tags
"""

import re
from typing import Dict

# =============================================================================
# YAML FRONTMATTER
# =============================================================================

YAML_FRONTMATTER_PATTERN = re.compile(
    r"^---\n(.*?)\n---",
    re.DOTALL,
)

# =============================================================================
# ELEMENT ID PATTERNS
# =============================================================================

# Generic element ID pattern: TYPE.NN.TT.SS
GENERIC_ELEMENT_ID_PATTERN = re.compile(
    r"\b([A-Z]+)\.(\d{2,})\.(\d{2})\.(\d{2,})\b"
)

# Document-specific element ID patterns
ELEMENT_ID_PATTERNS: Dict[str, re.Pattern] = {
    "brd": re.compile(r"\bBRD\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
    "prd": re.compile(r"\bPRD\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
    "ears": re.compile(r"\bEARS\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
    "bdd": re.compile(r"\bBDD\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
    "adr": re.compile(r"\bADR\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
    "sys": re.compile(r"\bSYS\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
    "req": re.compile(r"\bREQ\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
    "ctr": re.compile(r"\bCTR\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
    "spec": re.compile(r"\bSPEC\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
    "tasks": re.compile(r"\bTASKS\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
    "tspec": re.compile(r"\bTSPEC\.(\d{2,})\.(\d{2})\.(\d{2,})\b"),
}

# Legacy ID patterns to detect
LEGACY_ID_PATTERNS: Dict[str, re.Pattern] = {
    "FR": re.compile(r"\bFR-\d{3}\b"),  # FR-001
    "NFR": re.compile(r"\bNFR-\d{3}\b"),  # NFR-001
    "AC": re.compile(r"\bAC-\d{2,3}\b"),  # AC-01, AC-001
    "BR": re.compile(r"\bBR-\d{3}\b"),  # BR-001
    "US": re.compile(r"\bUS-\d{3}\b"),  # US-001
}

# =============================================================================
# SECTION HEADINGS
# =============================================================================

# Markdown section heading pattern (H1-H6)
SECTION_HEADING_PATTERN = re.compile(
    r"^(#{1,6})\s+(\d+(?:\.\d+)*\.?)\s*(.*)$",
    re.MULTILINE,
)

# H1 document title pattern
H1_TITLE_PATTERN = re.compile(
    r"^#\s+([A-Z]+-\d+):\s*(.+)$",
    re.MULTILINE,
)

# Section number extraction
SECTION_NUMBER_PATTERN = re.compile(r"^(\d+(?:\.\d+)*)")

# =============================================================================
# TRACEABILITY TAGS
# =============================================================================

TAG_PATTERNS: Dict[str, re.Pattern] = {
    "brd": re.compile(r"@brd:\s*BRD-\d+", re.IGNORECASE),
    "prd": re.compile(r"@prd:\s*PRD-\d+", re.IGNORECASE),
    "ears": re.compile(r"@ears:\s*EARS-\d+", re.IGNORECASE),
    "bdd": re.compile(r"@bdd:\s*BDD-\d+", re.IGNORECASE),
    "adr": re.compile(r"@adr:\s*ADR-\d+", re.IGNORECASE),
    "sys": re.compile(r"@sys:\s*SYS-\d+", re.IGNORECASE),
    "req": re.compile(r"@req:\s*REQ\.\d+\.\d+\.\d+", re.IGNORECASE),
    "ctr": re.compile(r"@ctr:\s*CTR-\d+", re.IGNORECASE),
    "spec": re.compile(r"@spec:\s*SPEC-\d+", re.IGNORECASE),
    "tasks": re.compile(r"@tasks:\s*TASKS-\d+", re.IGNORECASE),
    "ref": re.compile(r"@ref:\s*[A-Z]+-\d+", re.IGNORECASE),
    "diagram": re.compile(r"@diagram:\s*\S+", re.IGNORECASE),
}

# Generic traceability tag pattern
GENERIC_TAG_PATTERN = re.compile(r"@(\w+):\s*(\S+)")

# =============================================================================
# PLACEHOLDER PATTERNS
# =============================================================================

PLACEHOLDER_PATTERNS = [
    re.compile(r"\[TBD\]", re.IGNORECASE),
    re.compile(r"\[TODO\]", re.IGNORECASE),
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"\[PLACEHOLDER\]", re.IGNORECASE),
    re.compile(r"\[INSERT\s+.*?\]", re.IGNORECASE),
    re.compile(r"\[PENDING\]", re.IGNORECASE),
    re.compile(r"\[WIP\]", re.IGNORECASE),
]

# =============================================================================
# DIAGRAM PATTERNS
# =============================================================================

MERMAID_BLOCK_PATTERN = re.compile(
    r"```mermaid\n(.*?)```",
    re.DOTALL,
)

DIAGRAM_TAG_PATTERNS = {
    "c4-l1": re.compile(r"@diagram:\s*c4-l1", re.IGNORECASE),
    "c4-l2": re.compile(r"@diagram:\s*c4-l2", re.IGNORECASE),
    "dfd-l0": re.compile(r"@diagram:\s*dfd-l0", re.IGNORECASE),
    "dfd-l1": re.compile(r"@diagram:\s*dfd-l1", re.IGNORECASE),
    "sequence": re.compile(r"@diagram:\s*sequence-\w+", re.IGNORECASE),
}

# =============================================================================
# FILE NAME PATTERNS
# =============================================================================

FILE_NAME_PATTERNS: Dict[str, re.Pattern] = {
    "brd": re.compile(r"^BRD-\d{2,}_[\w-]+\.md$"),
    "prd": re.compile(r"^PRD-\d{2,}_[\w-]+\.md$"),
    "ears": re.compile(r"^EARS-\d{2,}_[\w-]+\.md$"),
    "bdd": re.compile(r"^[\w-]+\.feature$"),
    "adr": re.compile(r"^ADR-\d{3,}_[\w-]+\.md$"),
    "sys": re.compile(r"^SYS-\d{2,}_[\w-]+\.md$"),
    "req": re.compile(r"^REQ-\d{2,}_[\w-]+\.md$"),
    "ctr": re.compile(r"^CTR-\d{2,}_[\w-]+\.(md|yaml)$"),
    "spec": re.compile(r"^SPEC-\d{2,}_[\w-]+\.yaml$"),
    "tasks": re.compile(r"^TASKS-\d{2,}_[\w-]+\.md$"),
}

# Section-based file pattern (e.g., BRD-01.1_overview.md)
SECTION_FILE_NAME_PATTERN = re.compile(
    r"^([A-Z]+-\d+)\.(\d+)_([\w-]+)\.md$"
)
