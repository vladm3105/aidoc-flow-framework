"""UCX enumerations."""

from enum import Enum


class DocType(str, Enum):
    """Supported document types (SDD layers 1-10)."""

    BRD = "brd"      # Layer 1: Business Requirements
    PRD = "prd"      # Layer 2: Product Requirements
    EARS = "ears"    # Layer 3: Formal Requirements (EARS)
    BDD = "bdd"      # Layer 4: Behavior-Driven Development
    ADR = "adr"      # Layer 5: Architecture Decision Records
    SYS = "sys"      # Layer 6: System Requirements
    REQ = "req"      # Layer 7: Atomic Requirements
    CTR = "ctr"      # Layer 8: Data Contracts
    SPEC = "spec"    # Layer 9: Technical Specifications
    TSPEC = "tspec"  # Layer 10: Test Specifications

    @classmethod
    def from_string(cls, value: str) -> "DocType":
        """Create DocType from string, case-insensitive."""
        return cls(value.lower())

    @property
    def layer(self) -> int:
        """Get SDD layer number."""
        layer_map = {
            "brd": 1, "prd": 2, "ears": 3, "bdd": 4, "adr": 5,
            "sys": 6, "req": 7, "ctr": 8, "spec": 9, "tspec": 10,
        }
        return layer_map[self.value]

    @property
    def display_name(self) -> str:
        """Get human-readable name."""
        names = {
            "brd": "Business Requirements Document",
            "prd": "Product Requirements Document",
            "ears": "EARS Requirements",
            "bdd": "BDD Scenarios",
            "adr": "Architecture Decision Record",
            "sys": "System Requirements",
            "req": "Atomic Requirements",
            "ctr": "Data Contracts",
            "spec": "Technical Specification",
            "tspec": "Test Specification",
        }
        return names[self.value]


class Status(str, Enum):
    """Autopilot/review status."""

    PASS = "PASS"
    FAIL = "FAIL"
    NEEDS_MANUAL = "NEEDS_MANUAL"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    IN_PROGRESS = "IN_PROGRESS"
    SKIPPED = "SKIPPED"


class Confidence(str, Enum):
    """Fix confidence level."""

    AUTO_SAFE = "auto-safe"
    AUTO_ASSISTED = "auto-assisted"
    MANUAL_REQUIRED = "manual-required"

    @property
    def can_auto_apply(self) -> bool:
        """Check if this confidence level allows auto-apply."""
        return self == Confidence.AUTO_SAFE


class ValidationStatus(str, Enum):
    """Validation phase status."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    NO_VALIDATOR = "NO_VALIDATOR"


class Priority(str, Enum):
    """Finding priority level."""

    P0 = "P0"  # Critical - blocks PRD-Ready
    P1 = "P1"  # High - should fix before proceeding
    P2 = "P2"  # Enhancement - nice to have


class FixType(str, Enum):
    """Types of fixes that can be applied."""

    ADD_TEXT = "add_text"
    ADD_SECTION = "add_section"
    ADD_TABLE_ROW = "add_table_row"
    MODIFY_TEXT = "modify_text"
    ADD_FRONTMATTER = "add_frontmatter"
    ADD_TAG = "add_tag"
    DELETE_TEXT = "delete_text"
