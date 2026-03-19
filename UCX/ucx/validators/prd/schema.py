"""PRD Schema Definitions for UCX Framework v1.20.0.

This module contains all constants, element type codes, section mappings,
and pattern definitions for PRD validation.

Key Constants:
- 13 element type codes (01-09, 11, 22-24)
- 21 required sections (MVP and Standard)
- Section-to-type-code mappings
- Template profiles (mvp: 85%, standard: 90%)
- Forward reference blocking patterns
- Legacy pattern detection
"""

import re
from typing import Dict, List, Set, Pattern

# =============================================================================
# ELEMENT TYPE CODES (13 valid codes for PRD)
# =============================================================================

VALID_TYPE_CODES: Set[str] = {
    "01",  # Functional Requirement
    "02",  # Quality Attribute / NFR
    "03",  # Constraint
    "04",  # Assumption
    "05",  # Dependency
    "06",  # Acceptance Criteria
    "07",  # Risk
    "08",  # Metric / KPI
    "09",  # User Story
    "11",  # Use Case
    "22",  # Feature Item
    "23",  # Goal
    "24",  # Stakeholder Need
}

TYPE_CODE_DESCRIPTIONS: Dict[str, str] = {
    "01": "Functional Requirement",
    "02": "Quality Attribute",
    "03": "Constraint",
    "04": "Assumption",
    "05": "Dependency",
    "06": "Acceptance Criteria",
    "07": "Risk",
    "08": "Metric/KPI",
    "09": "User Story",
    "11": "Use Case",
    "22": "Feature Item",
    "23": "Goal",
    "24": "Stakeholder Need",
}

# Primary section for each type code
TYPE_CODE_PRIMARY_SECTION: Dict[str, int] = {
    "01": 9,   # Functional Requirements
    "02": 21,  # Quality Assurance
    "03": 12,  # Constraints & Assumptions
    "04": 12,  # Constraints & Assumptions
    "05": 7,   # Scope & Requirements
    "06": 11,  # Acceptance Criteria
    "07": 13,  # Risk Assessment
    "08": 5,   # Success Metrics (KPIs)
    "09": 8,   # User Stories
    "11": 9,   # Functional Requirements (Use Cases)
    "22": 7,   # Scope & Requirements (Features)
    "23": 6,   # Goals & Objectives
    "24": 4,   # Target Audience (Stakeholder Needs)
}

# =============================================================================
# SECTION STRUCTURE (21 Mandatory Sections)
# =============================================================================

REQUIRED_SECTIONS: Dict[int, str] = {
    1: "Document Control",
    2: "Executive Summary",
    3: "Problem Statement",
    4: "Target Audience & User Personas",
    5: "Success Metrics (KPIs)",
    6: "Goals & Objectives",
    7: "Scope & Requirements",
    8: "User Stories & User Roles",
    9: "Functional Requirements",
    10: "Customer-Facing Content & Messaging",
    11: "Acceptance Criteria",
    12: "Constraints & Assumptions",
    13: "Risk Assessment",
    14: "Success Definition",
    15: "Stakeholders & Communication",
    16: "Implementation Approach",
    17: "Budget & Resources",
    18: "Traceability",
    19: "References",
    20: "EARS Enhancement Appendix",
    21: "Quality Assurance & Testing Strategy",
}

# Sections that are BLOCKING (must have substantive content)
BLOCKING_SECTIONS: Set[int] = {10}  # Customer-Facing Content

# Sections that require special notes/structure
SPECIAL_SECTIONS: Dict[int, str] = {
    8: "layer_separation_note",  # User Stories requires layer separation note
    10: "substantive_content",    # Customer-Facing requires real content
    18: "adr_topics_table",       # Traceability should have ADR topics
    20: "ears_appendix",          # EARS Enhancement Appendix structure
}

# Section-to-valid-type-codes mapping
SECTION_CODE_MAP: Dict[str, List[str]] = {
    "1": [],                    # Document Control - no elements
    "2": [],                    # Executive Summary
    "3": [],                    # Problem Statement
    "4": ["24"],                # Target Audience (Stakeholder Need)
    "5": ["08"],                # Success Metrics (Metric/KPI)
    "6": ["23"],                # Goals & Objectives (Goal)
    "7": ["05", "22"],          # Scope & Requirements (Dependency, Feature)
    "8": ["09"],                # User Stories (User Story)
    "9": ["01", "11", "22"],    # Functional Requirements (FR, Use Case, Feature)
    "10": [],                   # Customer-Facing Content (no IDs)
    "11": ["06"],               # Acceptance Criteria
    "12": ["03", "04"],         # Constraints & Assumptions
    "13": ["07"],               # Risk Assessment
    "14": [],                   # Success Definition
    "15": ["24"],               # Stakeholders (Stakeholder Need)
    "16": [],                   # Implementation Approach
    "17": [],                   # Budget & Resources
    "18": [],                   # Traceability
    "19": [],                   # References
    "20": [],                   # EARS Enhancement Appendix
    "21": ["02"],               # Quality Assurance (Quality Attribute)
}

# =============================================================================
# TEMPLATE PROFILES
# =============================================================================

TEMPLATE_PROFILES: Dict[str, Dict] = {
    "mvp": {
        "sections": 21,
        "sys_ready_threshold": 85,
        "ears_ready_threshold": 85,
        "description": "Minimum Viable Product template",
    },
    "standard": {
        "sections": 21,
        "sys_ready_threshold": 90,
        "ears_ready_threshold": 90,
        "description": "Standard production template",
    },
}

# =============================================================================
# ELEMENT ID PATTERNS
# =============================================================================

# Valid PRD element ID format: PRD.NN.TT.SS
PRD_ELEMENT_ID_PATTERN: Pattern = re.compile(
    r"PRD\.(\d{2})\.(\d{2})\.(\d{2})"
)

# Pattern to extract element IDs from content
PRD_ELEMENT_ID_EXTRACT: Pattern = re.compile(
    r"\bPRD\.(\d{2})\.(\d{2})\.(\d{2})\b"
)

# BRD traceability pattern (required format)
BRD_TRACE_PATTERN: Pattern = re.compile(
    r"@brd:\s*BRD\.(\d{2})\.(\d{2})\.(\d{2})"
)

# Invalid BRD reference pattern (document-level only)
BRD_TRACE_INVALID: Pattern = re.compile(
    r"@brd:\s*BRD-(\d{2})(?!\.\d)"
)

# =============================================================================
# FORWARD REFERENCE BLOCKING
# =============================================================================

# Forbidden patterns for downstream artifacts (Layer 5+)
FORBIDDEN_DOWNSTREAM_PATTERNS: List[Pattern] = [
    re.compile(r"ADR-\d{2,}"),              # Layer 5
    re.compile(r"SYS-\d{2,}"),              # Layer 6
    re.compile(r"REQ-\d{2,}"),              # Layer 7
    re.compile(r"SPEC-\d{2,}"),             # Layer 9
    re.compile(r"TASKS-\d{2,}"),            # Layer 11
    re.compile(r"@adr:\s*ADR-"),
    re.compile(r"@sys:\s*SYS-"),
    re.compile(r"@req:\s*REQ-"),
    re.compile(r"@spec:\s*SPEC-"),
    re.compile(r"@tasks:\s*TASKS-"),
]

# Allowed downstream references (for planning)
ALLOWED_DOWNSTREAM_PATTERNS: List[Pattern] = [
    re.compile(r"@ears:\s*EARS-"),          # Layer 3 (planning)
    re.compile(r"@bdd:\s*BDD-"),             # Layer 4 (planning)
    re.compile(r"downstream.*ADR"),          # Generic reference OK
    re.compile(r"downstream.*SYS"),
    re.compile(r"To be detailed in"),
]

# =============================================================================
# LEGACY PATTERN DETECTION
# =============================================================================

LEGACY_PATTERNS: Dict[str, str] = {
    r"FR-\d{3}": "PRD.NN.01.SS",
    r"NFR-\d{3}": "PRD.NN.02.SS",
    r"AC-\d{3}": "PRD.NN.06.SS",
    r"BC-\d{3}": "PRD.NN.03.SS",
    r"BA-\d{3}": "PRD.NN.04.SS",
    r"QA-\d{3}": "PRD.NN.02.SS",
    r"RISK-\d{3}": "PRD.NN.07.SS",
    r"METRIC-\d{3}": "PRD.NN.08.SS",
    r"US-\d{2,3}": "PRD.NN.09.SS",
    r"F-\d{3}": "PRD.NN.22.SS",
    r"Feature-\d{3}-\d{3}": "PRD.NN.22.SS",
}

# Compiled legacy patterns for detection
LEGACY_PATTERN_COMPILED: List[tuple[Pattern, str]] = [
    (re.compile(pattern), suggestion)
    for pattern, suggestion in LEGACY_PATTERNS.items()
]

# =============================================================================
# LAYER SEPARATION PATTERNS
# =============================================================================

# Patterns that indicate BDD content (forbidden in PRD)
BDD_PATTERNS: List[Pattern] = [
    re.compile(r"Given\s+.+\s+When\s+.+\s+Then", re.IGNORECASE | re.DOTALL),
    re.compile(r"@given\s*\(", re.IGNORECASE),
    re.compile(r"@when\s*\(", re.IGNORECASE),
    re.compile(r"@then\s*\(", re.IGNORECASE),
]

# Patterns that indicate EARS content (forbidden in PRD Section 8)
EARS_PATTERNS: List[Pattern] = [
    re.compile(r"WHEN\s+.+\s+THE\s+.+\s+SHALL", re.IGNORECASE),
    re.compile(r"While\s+.+\s+the\s+system\s+shall", re.IGNORECASE),
]

# Layer separation note content (required in Section 8)
LAYER_SEPARATION_NOTE_KEYWORDS: List[str] = [
    "Layer Separation",
    "EARS (Layer 3)",
    "BDD (Layer 4)",
    "downstream artifact",
]

# =============================================================================
# DOCUMENT CONTROL FIELDS
# =============================================================================

DOC_CONTROL_REQUIRED_FIELDS: List[str] = [
    "Status",
    "Version",
    "Date Created",
    "Last Updated",
    "Author",
    "Reviewer",
    "Approver",
    "BRD Reference",
    "SYS-Ready Score",
    "EARS-Ready Score",
    "Revision History",  # Required for Review/Approved status
]

DOC_CONTROL_OPTIONAL_FIELDS: List[str] = [
    "Priority",
    "Target Release",
    "Estimated Effort",
]

VALID_STATUS_VALUES: Set[str] = {
    "Draft",
    "Review",
    "Approved",
    "Implemented",
}

# =============================================================================
# FILE NAMING
# =============================================================================

# Valid PRD file name patterns
PRD_FILE_PATTERN: Pattern = re.compile(
    r"^PRD-(\d{2})(?:\.(\d+))?_[a-z0-9_]+\.md$"
)

# Index file pattern (excluded from validation)
PRD_INDEX_PATTERN: Pattern = re.compile(
    r"^PRD-(\d{2})\.0_index\.md$"
)

# Template/example file pattern (excluded from validation)
PRD_TEMPLATE_PATTERN: Pattern = re.compile(
    r"^PRD-00_"
)

# =============================================================================
# DIAGRAM REQUIREMENTS
# =============================================================================

REQUIRED_DIAGRAM_TAGS: List[str] = [
    "@diagram: c4-l2",     # Container-level diagram
    "@diagram: dfd-l1",    # Data flow level 1
]

SEQUENCE_DIAGRAM_PATTERN: Pattern = re.compile(
    r"@diagram:\s*sequence-"
)

# Sequence diagrams must have alt/else branches
SEQUENCE_ALT_PATTERN: Pattern = re.compile(
    r"alt|else|opt|break|par|critical"
)

# =============================================================================
# PLACEHOLDER PATTERNS
# =============================================================================

PLACEHOLDER_PATTERNS: List[Pattern] = [
    re.compile(r"\(future\)", re.IGNORECASE),
    re.compile(r"\(TBD\)", re.IGNORECASE),
    re.compile(r"\[TODO\]", re.IGNORECASE),
    re.compile(r"\bXXX\b"),
    re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"\bHACK\b", re.IGNORECASE),
    re.compile(r"\bWIP\b"),
    re.compile(r"\?\?\?"),
    re.compile(r"<<<<<<<"),  # Merge conflict
    re.compile(r">>>>>>>"),  # Merge conflict
    re.compile(r"======="),  # Merge conflict (careful with tables)
]

# =============================================================================
# SIZE LIMITS
# =============================================================================

FILE_LINE_WARNING: int = 800
FILE_LINE_ERROR: int = 1200
TOKEN_WARNING: int = 40000
TOKEN_ERROR: int = 80000

# Approximate tokens per character
CHARS_PER_TOKEN: float = 4.0

# =============================================================================
# YAML FRONTMATTER
# =============================================================================

REQUIRED_FRONTMATTER_FIELDS: List[str] = [
    "title",
    "doc_id",
    "version",
    "status",
    "tags",
]

REQUIRED_CUSTOM_FIELDS: Dict[str, str] = {
    "document_type": "prd",
    "artifact_type": "PRD",
    "layer": "2",
}

REQUIRED_TAGS: List[str] = [
    "prd",
    "layer-2-artifact",
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def is_valid_type_code(code: str) -> bool:
    """Check if a type code is valid for PRD."""
    return code in VALID_TYPE_CODES


def get_type_code_description(code: str) -> str:
    """Get description for a type code."""
    return TYPE_CODE_DESCRIPTIONS.get(code, "Unknown")


def get_primary_section(code: str) -> int:
    """Get primary section number for a type code."""
    return TYPE_CODE_PRIMARY_SECTION.get(code, 0)


def get_expected_codes_for_section(section: int) -> List[str]:
    """Get expected type codes for a section."""
    return SECTION_CODE_MAP.get(str(section), [])


def is_blocking_section(section: int) -> bool:
    """Check if a section is blocking (requires substantive content)."""
    return section in BLOCKING_SECTIONS


def get_profile_threshold(profile: str) -> int:
    """Get score threshold for a template profile."""
    return TEMPLATE_PROFILES.get(profile, TEMPLATE_PROFILES["standard"])["sys_ready_threshold"]


def detect_legacy_pattern(text: str) -> List[tuple[str, str]]:
    """Detect legacy ID patterns and return suggestions."""
    findings = []
    for pattern, suggestion in LEGACY_PATTERN_COMPILED:
        if pattern.search(text):
            findings.append((pattern.pattern, suggestion))
    return findings


def has_forbidden_downstream_refs(content: str) -> List[str]:
    """Check for forbidden downstream references."""
    findings = []
    for pattern in FORBIDDEN_DOWNSTREAM_PATTERNS:
        matches = pattern.findall(content)
        findings.extend(matches)
    return findings


def has_bdd_patterns(content: str) -> bool:
    """Check if content contains BDD patterns."""
    for pattern in BDD_PATTERNS:
        if pattern.search(content):
            return True
    return False


def has_ears_patterns(content: str) -> bool:
    """Check if content contains EARS patterns."""
    for pattern in EARS_PATTERNS:
        if pattern.search(content):
            return True
    return False


def has_layer_separation_note(content: str) -> bool:
    """Check if content has layer separation note."""
    count = sum(1 for keyword in LAYER_SEPARATION_NOTE_KEYWORDS if keyword in content)
    return count >= 2  # Require at least 2 keywords


def estimate_tokens(content: str) -> int:
    """Estimate token count from character count."""
    return int(len(content) / CHARS_PER_TOKEN)
