"""
Hash-based Finding and Action ID generation.

Provides deterministic, collision-resistant IDs for UCR findings and actions.
Replaces sequential REM-P{0-2}-{NNN} format with P{0-2}-{xxxx}.
Replaces sequential ACT-{NNN} format with ACT-{xxxx}.

Benefits:
- Stateless generation (no counter synchronization needed)
- Deterministic: same content always produces same ID
- Natural deduplication (identical content = identical hash)
- Stable across report regeneration

Reference: PLAN-008_hash_based_finding_ids.md
Version: UCX 1.19.0+
"""

import hashlib
import re
from dataclasses import dataclass
from typing import Optional


# Regex patterns for ID format validation
LEGACY_FINDING_PATTERN = re.compile(r"REM-P[012]-\d{3}")
HASH_FINDING_PATTERN = re.compile(r"P[012]-[a-f0-9]{4,8}")
LEGACY_ACTION_PATTERN = re.compile(r"ACT-\d{3}")
HASH_ACTION_PATTERN = re.compile(r"ACT-[a-f0-9]{4,8}")


@dataclass
class FindingIdentity:
    """Components that uniquely identify a finding."""

    priority: str           # P0, P1, P2
    target_file: str        # Target file path
    target_section: str     # Section identifier
    category: str           # Finding category (functional, compliance, etc.)
    description: str        # Finding description

    def to_hash_input(self) -> str:
        """Generate normalized hash input string."""
        return ":".join([
            _normalize_path(self.target_file),
            _normalize_section(self.target_section),
            self.category.lower().strip(),
            _normalize_description(self.description),
        ])


@dataclass
class ActionIdentity:
    """Components that uniquely identify an action."""

    fixer: str              # Assigned fixer persona (auditor, tech_lead, etc.)
    target_file: str        # Target file path
    target_section: str     # Section identifier
    description: str        # Action description

    def to_hash_input(self) -> str:
        """Generate normalized hash input string."""
        return ":".join([
            self.fixer.lower().strip().replace(" ", "_"),
            _normalize_path(self.target_file),
            _normalize_section(self.target_section),
            _normalize_description(self.description),
        ])


class FindingIDGenerator:
    """
    Stateless finding ID generator using content hashing.

    Benefits:
    - No counter synchronization needed
    - Deterministic: same finding = same ID
    - Natural deduplication
    - Stable across report regeneration

    Usage:
        >>> gen = FindingIDGenerator()
        >>> identity = FindingIdentity(
        ...     priority="P1",
        ...     target_file="BRD-02.6_functional_requirements.md",
        ...     target_section="Section 6.1",
        ...     category="compliance",
        ...     description="SAR filing workflow missing"
        ... )
        >>> finding_id = gen.generate(identity)
        >>> print(finding_id)  # e.g., "P1-a7f3"
    """

    def __init__(self, hash_length: int = 4):
        """
        Initialize the generator.

        Args:
            hash_length: Minimum hash suffix length (4-8). Default: 4.
        """
        if not 1 <= hash_length <= 8:
            raise ValueError("hash_length must be between 1 and 8")
        self.hash_length = hash_length
        self._generated_ids: set[str] = set()

    def generate(self, identity: FindingIdentity) -> str:
        """
        Generate unique finding ID.

        Args:
            identity: FindingIdentity with finding attributes.

        Returns:
            Finding ID in format: P{0-2}-{hash}
        """
        hash_input = identity.to_hash_input()
        hash_digest = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        # Validate priority format
        priority = identity.priority.upper()
        if priority not in ("P0", "P1", "P2"):
            raise ValueError(f"Invalid priority: {priority}. Must be P0, P1, or P2.")

        # Try increasing hash lengths until unique
        for length in range(self.hash_length, 9):
            candidate = f"{priority}-{hash_digest[:length]}"
            if candidate not in self._generated_ids:
                self._generated_ids.add(candidate)
                return candidate

        # Fallback: sequence suffix (extremely rare - collision on 8-char hash)
        base = f"{priority}-{hash_digest[:self.hash_length]}"
        seq = 1
        while f"{base}{seq}" in self._generated_ids:
            seq += 1
        final_id = f"{base}{seq}"
        self._generated_ids.add(final_id)
        return final_id

    def generate_from_parts(
        self,
        priority: str,
        target_file: str,
        target_section: str,
        category: str,
        description: str,
    ) -> str:
        """
        Convenience method to generate ID from individual parts.

        Args:
            priority: P0, P1, or P2
            target_file: Target file path
            target_section: Section identifier
            category: Finding category
            description: Finding description

        Returns:
            Finding ID in format: P{0-2}-{hash}
        """
        identity = FindingIdentity(
            priority=priority,
            target_file=target_file,
            target_section=target_section,
            category=category,
            description=description,
        )
        return self.generate(identity)

    def reset(self) -> None:
        """Reset generated ID cache (call between documents/sessions)."""
        self._generated_ids.clear()

    @property
    def generated_count(self) -> int:
        """Number of IDs generated in current session."""
        return len(self._generated_ids)


class ActionIDGenerator:
    """
    Stateless action ID generator using content hashing.

    Used for generating IDs for handoff actions in UCR reports.

    Usage:
        >>> gen = ActionIDGenerator()
        >>> identity = ActionIdentity(
        ...     fixer="auditor",
        ...     target_file="PRD-01",
        ...     target_section="Section 3.2",
        ...     description="Add SAR filing user story"
        ... )
        >>> action_id = gen.generate(identity)
        >>> print(action_id)  # e.g., "ACT-b2c1"
    """

    def __init__(self, hash_length: int = 4):
        """
        Initialize the generator.

        Args:
            hash_length: Minimum hash suffix length (4-8). Default: 4.
        """
        if not 1 <= hash_length <= 8:
            raise ValueError("hash_length must be between 1 and 8")
        self.hash_length = hash_length
        self._generated_ids: set[str] = set()

    def generate(self, identity: ActionIdentity) -> str:
        """
        Generate unique action ID.

        Args:
            identity: ActionIdentity with action attributes.

        Returns:
            Action ID in format: ACT-{hash}
        """
        hash_input = identity.to_hash_input()
        hash_digest = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        # Try increasing hash lengths until unique
        for length in range(self.hash_length, 9):
            candidate = f"ACT-{hash_digest[:length]}"
            if candidate not in self._generated_ids:
                self._generated_ids.add(candidate)
                return candidate

        # Fallback: sequence suffix (extremely rare)
        base = f"ACT-{hash_digest[:self.hash_length]}"
        seq = 1
        while f"{base}{seq}" in self._generated_ids:
            seq += 1
        final_id = f"{base}{seq}"
        self._generated_ids.add(final_id)
        return final_id

    def generate_from_parts(
        self,
        fixer: str,
        target_file: str,
        target_section: str,
        description: str,
    ) -> str:
        """
        Convenience method to generate ID from individual parts.

        Args:
            fixer: Assigned fixer persona
            target_file: Target file path
            target_section: Section identifier
            description: Action description

        Returns:
            Action ID in format: ACT-{hash}
        """
        identity = ActionIdentity(
            fixer=fixer,
            target_file=target_file,
            target_section=target_section,
            description=description,
        )
        return self.generate(identity)

    def reset(self) -> None:
        """Reset generated ID cache (call between documents/sessions)."""
        self._generated_ids.clear()

    @property
    def generated_count(self) -> int:
        """Number of IDs generated in current session."""
        return len(self._generated_ids)


# =============================================================================
# Normalization Functions
# =============================================================================


def _normalize_path(path: str) -> str:
    """
    Extract document identifier from path.

    Examples:
        >>> _normalize_path("BRD-02.6_functional_requirements.md")
        'brd-02.6'
        >>> _normalize_path("docs/01_BRD/BRD-50.5.md")
        'brd-50.5'
        >>> _normalize_path("random_file.md")
        'random_file.md'
    """
    if not path:
        return ""

    # Try to extract BRD/PRD/REQ/etc pattern
    match = re.search(r"([A-Z]{2,5}-\d+(?:\.\d+)?)", path, re.IGNORECASE)
    if match:
        return match.group(1).lower()

    # Fallback: use filename without extension
    filename = path.split("/")[-1].split("\\")[-1]
    return filename.lower()


def _normalize_section(section: str) -> str:
    """
    Normalize section reference.

    Examples:
        >>> _normalize_section("Section 6.1")
        '6.1'
        >>> _normalize_section("SECTION 6.1 BRD.02.01.01")
        '6.1 brd.02.01.01'
        >>> _normalize_section("6.1.2")
        '6.1.2'
    """
    if not section:
        return ""

    section = section.lower().strip()
    # Remove "Section " prefix
    section = re.sub(r"^section\s+", "", section)
    return section


def _normalize_description(desc: str, max_len: int = 100) -> str:
    """
    Normalize description for consistent hashing.

    Removes special characters, normalizes whitespace, truncates to max_len.

    Examples:
        >>> _normalize_description("SAR Filing: Missing CO review!!!")
        'sar filing missing co review'
        >>> _normalize_description("Add  spacing   test")
        'add spacing test'
    """
    if not desc:
        return ""

    desc = desc.lower()
    # Remove special characters (keep alphanumeric and spaces)
    desc = re.sub(r"[^a-z0-9\s]", "", desc)
    # Normalize whitespace
    desc = " ".join(desc.split())
    return desc[:max_len]


# =============================================================================
# ID Format Utilities
# =============================================================================


def is_legacy_finding_id(finding_id: str) -> bool:
    """
    Check if ID uses legacy sequential format.

    Args:
        finding_id: ID to check

    Returns:
        True if matches REM-P{0-2}-{NNN} format
    """
    return bool(LEGACY_FINDING_PATTERN.match(finding_id))


def is_hash_finding_id(finding_id: str) -> bool:
    """
    Check if ID uses new hash format.

    Args:
        finding_id: ID to check

    Returns:
        True if matches P{0-2}-{hex} format
    """
    return bool(HASH_FINDING_PATTERN.match(finding_id))


def is_legacy_action_id(action_id: str) -> bool:
    """
    Check if ID uses legacy sequential format.

    Args:
        action_id: ID to check

    Returns:
        True if matches ACT-{NNN} format
    """
    return bool(LEGACY_ACTION_PATTERN.match(action_id))


def is_hash_action_id(action_id: str) -> bool:
    """
    Check if ID uses new hash format.

    Args:
        action_id: ID to check

    Returns:
        True if matches ACT-{hex} format
    """
    return bool(HASH_ACTION_PATTERN.match(action_id))


def extract_priority_from_id(finding_id: str) -> Optional[str]:
    """
    Extract priority level from finding ID.

    Args:
        finding_id: Finding ID in any format

    Returns:
        Priority string (P0, P1, P2) or None if not found
    """
    match = re.search(r"P([012])", finding_id)
    if match:
        return f"P{match.group(1)}"
    return None


def normalize_finding_id(finding_id: str) -> str:
    """
    Normalize legacy ID format to indicate legacy status.

    Used during transition period for backward compatibility.

    Args:
        finding_id: ID to normalize

    Returns:
        Original ID if hash format, or priority-LEGACY if legacy format
    """
    if is_hash_finding_id(finding_id):
        return finding_id

    if is_legacy_finding_id(finding_id):
        priority = extract_priority_from_id(finding_id)
        if priority:
            return f"{priority}-LEGACY"

    return finding_id


# =============================================================================
# Combined Pattern for Dual-Format Support
# =============================================================================


# Regex that matches BOTH legacy and hash finding ID formats
DUAL_FORMAT_FINDING_PATTERN = re.compile(
    r"((?:REM-)?P[012]-(?:[a-f0-9]{4,8}|\d{3}))",
    re.IGNORECASE,
)

# Regex that matches BOTH legacy and hash action ID formats
DUAL_FORMAT_ACTION_PATTERN = re.compile(
    r"(ACT-(?:[a-f0-9]{4,8}|\d{3}))",
    re.IGNORECASE,
)
