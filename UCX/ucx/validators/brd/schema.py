"""BRD validation schema constants.

Defines:
- Required metadata fields and custom_fields
- Required tags and forbidden patterns
- Required sections for standard and MVP profiles
- Element type codes and section mappings
- File naming patterns
- Quality gate check definitions
"""

import re
from typing import Dict, List, Set, Tuple, Union

# =============================================================================
# METADATA CONSTANTS
# =============================================================================

# Required custom_fields in YAML frontmatter
REQUIRED_CUSTOM_FIELDS: Dict[str, Dict] = {
    "document_type": {"allowed": ["brd", "template"]},
    "artifact_type": {"allowed": ["BRD"]},
    "layer": {"allowed": [1]},
    "architecture_approaches": {"type": "array"},
    "priority": {"allowed": ["primary", "shared", "fallback"]},
    "status": {
        "allowed": [
            "development",
            "production",
            "active",
            "draft",
            "deprecated",
            "reference",
            "planned",
        ]
    },
}

# Legacy status values that should trigger migration warning
LEGACY_STATUS_VALUES = {"active", "draft", "deprecated", "reference", "planned"}

# Required tags
REQUIRED_TAGS = {"brd", "layer-1-artifact"}

# Forbidden tag patterns (compiled)
FORBIDDEN_TAG_PATTERNS = [
    re.compile(r"^business-brd$"),
    re.compile(r"^business-requirements$"),
    re.compile(r"^business_requirements$"),
    re.compile(r"^brd-\d{3}$"),
]

# =============================================================================
# SECTION REQUIREMENTS
# =============================================================================

# Standard profile sections (legacy 5-section format)
REQUIRED_SECTIONS_STANDARD: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^# BRD-\d{2,}:"), "Title (H1 with BRD-NN format)"),
    (re.compile(r"^## 0\. Document Control"), "Section 0: Document Control"),
    (re.compile(r"^## 1\. Executive Summary"), "Section 1: Executive Summary"),
    (re.compile(r"^## 2\. Business Context"), "Section 2: Business Context"),
    (re.compile(r"^## 3\. Business Requirements"), "Section 3: Business Requirements"),
]

# MVP profile sections (18-section format)
REQUIRED_SECTIONS_MVP: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^# BRD-\d{2,}:"), "Title (H1 with BRD-NN format)"),
    (re.compile(r"^## 0\. Document Control"), "Section 0: Document Control"),
    (re.compile(r"^## 1\. Introduction"), "Section 1: Introduction"),
    (re.compile(r"^## 2\. Business Objectives"), "Section 2: Business Objectives"),
    (re.compile(r"^## 3\. Project Scope"), "Section 3: Project Scope"),
    (re.compile(r"^## 4\. Stakeholders"), "Section 4: Stakeholders"),
    (re.compile(r"^## 5\. User Stories"), "Section 5: User Stories"),
    (re.compile(r"^## 6\. Functional Requirements"), "Section 6: Functional Requirements"),
    (re.compile(r"^## 7\. Quality Attributes"), "Section 7: Quality Attributes"),
    (
        re.compile(r"^## 8\. Business Constraints and Assumptions"),
        "Section 8: Business Constraints and Assumptions",
    ),
    (re.compile(r"^## 9\. Acceptance Criteria"), "Section 9: Acceptance Criteria"),
    (re.compile(r"^## 10\. Business Risk Management"), "Section 10: Business Risk Management"),
    (re.compile(r"^## 11\. Implementation Approach"), "Section 11: Implementation Approach"),
    (re.compile(r"^## 12\. Support and Maintenance"), "Section 12: Support and Maintenance"),
    (re.compile(r"^## 13\. Cost-Benefit Analysis"), "Section 13: Cost-Benefit Analysis"),
    (re.compile(r"^## 14\. Project Governance"), "Section 14: Project Governance"),
    (re.compile(r"^## 15\. Quality Assurance"), "Section 15: Quality Assurance"),
    (re.compile(r"^## 16\. Traceability"), "Section 16: Traceability"),
    (re.compile(r"^## 17\. Glossary"), "Section 17: Glossary"),
    (re.compile(r"^## 18\. Appendices"), "Section 18: Appendices"),
]

# Profile to section list mapping
SECTION_PROFILES: Dict[str, List[Tuple[re.Pattern, str]]] = {
    "standard": REQUIRED_SECTIONS_STANDARD,
    "mvp": REQUIRED_SECTIONS_MVP,
}

# Document Control required fields
DOCUMENT_CONTROL_FIELDS = [
    "Project Name",
    "Document Version",
    "Date",
    "Document Owner",
    "Status",
]

# =============================================================================
# ELEMENT ID CONSTANTS
# =============================================================================

# Valid BRD element type codes
# Source: ID_NAMING_STANDARDS.md (Canonical authority for element type codes)
# Codes 74-90 are reserved for future use
VALID_BRD_CODES: Set[str] = {
    "01",  # Functional Requirement
    "02",  # Quality Attribute (generic)
    "03",  # Constraint
    "04",  # Assumption
    "05",  # Dependency
    "06",  # Acceptance Criteria
    "07",  # Risk
    "08",  # Metric
    "09",  # User Story
    "10",  # Decision
    "22",  # Feature Item
    "23",  # Business Objective
    "24",  # Stakeholder Need
    "32",  # Architecture Topic (Legacy compatibility)
    # Quality Attribute Subcategories (91-99 series) - Section 7.x
    "91",  # Performance Requirement (Section 7.3)
    "92",  # Reliability Requirement (Section 7.4)
    "93",  # Availability Requirement (reserved)
    "94",  # Scalability Requirement (Section 7.5)
    "95",  # Usability Requirement (reserved)
    "96",  # Security Requirement (Section 7.6)
    "97",  # Compatibility Requirement (reserved)
    "98",  # Observability Requirement (Section 7.7)
    "99",  # Maintainability Requirement (Section 7.8)
}

# Element type code descriptions
# Source: ID_NAMING_STANDARDS.md (Canonical authority for element type codes)
ELEMENT_CODE_DESCRIPTIONS: Dict[str, str] = {
    "01": "Functional Requirement",
    "02": "Quality Attribute",
    "03": "Constraint",
    "04": "Assumption",
    "05": "Dependency",
    "06": "Acceptance Criteria",
    "07": "Risk",
    "08": "Metric",
    "09": "User Story",
    "10": "Decision",
    "22": "Feature Item",
    "23": "Business Objective",
    "24": "Stakeholder Need",
    "32": "Architecture Topic",
    # Quality Attribute Subcategories (91-99 series)
    "91": "Performance Requirement",
    "92": "Reliability Requirement",
    "93": "Availability Requirement",
    "94": "Scalability Requirement",
    "95": "Usability Requirement",
    "96": "Security Requirement",
    "97": "Compatibility Requirement",
    "98": "Observability Requirement",
    "99": "Maintainability Requirement",
}

# Section to valid element type code(s) mapping
# Values can be a single code string or a set of valid codes
# Source: ID_NAMING_STANDARDS.md - QA Subcategories use hierarchical codes 91-99
SECTION_CODE_MAP: Dict[str, Union[str, Set[str]]] = {
    "2": "23",  # Business Objectives
    "3": "22",  # Project Scope / Feature Items
    "4": "24",  # Stakeholders / Stakeholder Needs
    "5": "09",  # User Stories
    "6": {"01", "06"},  # Functional Requirements (01) + Acceptance Criteria tables (06)
    "7.1": "02",  # Quality Attributes (generic overview)
    "7.2": {"10", "32"},  # ADR Topics / Architecture Topics (10 canonical, 32 legacy)
    # Quality Attribute Subcategory Sections - hierarchical codes 91-99
    # Code 02/05 tolerated for legacy; specific 9x codes are canonical
    "7.3": {"02", "05", "91"},  # Performance Requirements (91 canonical)
    "7.4": {"02", "05", "92"},  # Reliability Requirements (92 canonical)
    "7.5": {"02", "05", "94"},  # Scalability Requirements (94 canonical)
    "7.6": {"02", "05", "96"},  # Security Requirements (96 canonical)
    "7.7": {"02", "05", "98"},  # Observability Requirements (98 canonical)
    "7.8": {"02", "05", "99"},  # Maintainability Requirements (99 canonical)
    "8.1": "03",  # Constraints
    "8.2": "04",  # Assumptions
    "9": "06",  # Acceptance Criteria
    "10": {"05", "07"},  # Risk Management: 07 canonical, 05 tolerated for legacy
}

# Preferred codes when multiple are valid
PREFERRED_SECTION_CODES: Dict[str, str] = {
    "6": "01",   # Functional Requirements primary; Acceptance Criteria embedded
    "7.2": "10", # Decision (canonical) over Architecture Topic (legacy)
    "7.3": "91", # Performance (canonical)
    "7.4": "92", # Reliability (canonical)
    "7.5": "94", # Scalability (canonical)
    "7.6": "96", # Security (canonical)
    "7.7": "98", # Observability (canonical)
    "7.8": "99", # Maintainability (canonical)
    "10": "07",  # Risk (canonical) over Dependency (legacy)
}

# =============================================================================
# FILE NAMING PATTERNS
# =============================================================================

# Monolithic: BRD-NN_slug.md
FILE_NAME_PATTERN_MONOLITHIC = re.compile(r"^BRD-\d{2,}_[A-Za-z0-9_]+\.md$")

# Section (shortened): BRD-NN.S_section_type.md (PREFERRED for nested folders)
FILE_NAME_PATTERN_SECTION_SHORT = re.compile(r"^BRD-\d{2,}\.\d+_[A-Za-z_]+\.md$")

# Section (full): BRD-NN.S_slug_section_type.md (backward compatible)
FILE_NAME_PATTERN_SECTION_FULL = re.compile(r"^BRD-\d{2,}\.\d+_[A-Za-z0-9_]+_[A-Za-z_]+\.md$")

# H1 title pattern
H1_TITLE_PATTERN = re.compile(r"^# BRD-\d{2,}:")

# Section number pattern
SECTION_NUMBER_PATTERN = re.compile(r"^## (\d+)\.")

# Element ID pattern
ELEMENT_ID_PATTERN = re.compile(r"\bBRD\.(\d{2,})\.(\d{2})\.(\d{2,})\b")

# Section heading pattern (for current section detection)
SECTION_HEADING_PATTERN = re.compile(r"^#{2,3}\s+(\d+(?:\.\d+)*)\.")

# =============================================================================
# QUALITY GATE DEFINITIONS
# =============================================================================

# Quality gate check tiers
# Tier 1: Core (blocking for pre-commit)
# Tier 2: Advisory (non-blocking)
QUALITY_GATE_TIERS: Dict[str, int] = {
    "GATE-01": 1,  # Placeholder detection - Tier 1 for existing BRDs
    "GATE-02": 1,  # Premature downstream references
    "GATE-03": 2,  # Internal count consistency
    "GATE-04": 1,  # Index synchronization
    "GATE-05": 0,  # DEPRECATED (Inter-BRD cross-linking)
    "GATE-06": 1,  # Diagram contract validation
    "GATE-07": 2,  # Glossary consistency
    "GATE-08": 1,  # Element ID uniqueness (duplicates=error, misplaced=warn)
    "GATE-09": 2,  # Cost estimate format
    "GATE-10": 1,  # File size compliance (>20K tokens)
}

# Placeholder patterns to detect
PLACEHOLDER_PATTERNS = [
    re.compile(r"\[TBD\]", re.IGNORECASE),
    re.compile(r"\[TODO\]", re.IGNORECASE),
    re.compile(r"\bTODO\b"),  # Case-sensitive for code comments
    re.compile(r"\bFIXME\b"),  # Case-sensitive for code comments
    re.compile(r"\[PLACEHOLDER\]", re.IGNORECASE),
    re.compile(r"\[INSERT\s+.*?\]", re.IGNORECASE),
    re.compile(r"\[PENDING\]", re.IGNORECASE),
    re.compile(r"\[WIP\]", re.IGNORECASE),
]

# Downstream reference patterns (should not appear in BRD)
DOWNSTREAM_REF_PATTERNS = [
    re.compile(r"@prd:\s*PRD-\d+", re.IGNORECASE),
    re.compile(r"@adr:\s*ADR-\d+", re.IGNORECASE),
    re.compile(r"@sys:\s*SYS-\d+", re.IGNORECASE),
    re.compile(r"@req:\s*REQ\.\d+", re.IGNORECASE),
]

# Diagram tag patterns
DIAGRAM_TAG_PATTERNS = {
    "c4-l1": re.compile(r"@diagram:\s*c4-l1", re.IGNORECASE),
    "dfd-l0": re.compile(r"@diagram:\s*dfd-l0", re.IGNORECASE),
    "sequence": re.compile(r"@diagram:\s*sequence-(sync|async|error)", re.IGNORECASE),
}

# Diagram intent header required fields
DIAGRAM_INTENT_FIELDS = [
    "diagram_type:",
    "level:",
    "scope_boundary:",
    "upstream_refs:",
    "downstream_refs:",
]

# Maximum token limit for BRD files
MAX_TOKENS = 20000

# =============================================================================
# LEGACY ID PATTERNS
# =============================================================================

# Patterns for detecting legacy (non-unified) element IDs
LEGACY_ID_PATTERNS = {
    "FR": re.compile(r"\bFR-\d{3}\b"),  # FR-001
    "NFR": re.compile(r"\bNFR-\d{3}\b"),  # NFR-001
    "AC": re.compile(r"\bAC-\d{2,3}\b"),  # AC-01, AC-001
    "BR": re.compile(r"\bBR-\d{3}\b"),  # BR-001
    "US": re.compile(r"\bUS-\d{3}\b"),  # US-001
}
