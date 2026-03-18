"""
UCX Category Conflict Resolution.

Handles cases where a finding may match multiple categories
through different detection methods (element code, keyword, persona).

v1.19.0: Added hash-based ID generation integration via resolve_with_id().
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .categories import (
    Category,
    categorize_by_element_code,
    categorize_by_keyword,
    extract_element_code,
    get_category_by_name,
    get_persona_primary_category,
)
from ucx.utils.finding_hash import FindingIDGenerator, FindingIdentity

logger = logging.getLogger(__name__)


class ResolutionMethod(Enum):
    """Method used to resolve category assignment."""

    EXPLICIT_TAG = "explicit_tag"      # [CAT:xxx] tag in finding
    ELEMENT_CODE = "element_code"      # ID element type code
    KEYWORD = "keyword"                # Text keyword match
    PERSONA_DEFAULT = "persona_default"  # Persona's primary category
    FALLBACK = "fallback"              # OTHER category


@dataclass
class ConflictResolution:
    """Result of category conflict resolution."""

    finding_id: str
    resolved_category: Category
    method: ResolutionMethod
    alternatives: list[tuple[Category, ResolutionMethod]]
    had_conflict: bool

    @property
    def is_fallback(self) -> bool:
        """True if resolution fell back to OTHER or persona default."""
        return self.method in (ResolutionMethod.FALLBACK, ResolutionMethod.PERSONA_DEFAULT)


class CategoryConflictResolver:
    """
    Resolves category conflicts using priority order.

    Resolution Priority (per PLAN-002):
    1. Explicit [CAT:xxx] tag from persona prompt
    2. Element code from finding ID
    3. Keyword match in finding text
    4. Persona's primary category
    5. Fallback to OTHER

    When multiple methods match, the higher priority wins.
    Conflicts are logged for analysis.

    v1.19.0: Integrated hash-based ID generation via resolve_with_id().
    """

    def __init__(self, hash_length: int = 4):
        """
        Initialize the conflict resolver.

        Args:
            hash_length: Minimum hash length for generated finding IDs (default: 4).
        """
        self._conflict_count = 0
        self._resolution_stats: dict[ResolutionMethod, int] = {
            method: 0 for method in ResolutionMethod
        }
        self._stats_cache: Optional[dict[ResolutionMethod, int]] = None
        self._id_generator = FindingIDGenerator(hash_length=hash_length)

    def resolve(
        self,
        finding_id: str,
        finding_text: str,
        persona: str,
        explicit_tag: Optional[str] = None,
    ) -> ConflictResolution:
        """
        Resolve category for a finding.

        Args:
            finding_id: Finding ID (may contain element code).
            finding_text: Finding description text.
            persona: Persona that generated the finding.
            explicit_tag: Optional [CAT:xxx] tag from prompt.

        Returns:
            ConflictResolution with resolved category and details.
        """
        alternatives: list[tuple[Category, ResolutionMethod]] = []
        resolved_category: Optional[Category] = None
        resolution_method: Optional[ResolutionMethod] = None

        # 1. Check explicit tag
        if explicit_tag:
            tag_cat = get_category_by_name(explicit_tag)
            if tag_cat:
                resolved_category = tag_cat
                resolution_method = ResolutionMethod.EXPLICIT_TAG

        # 2. Check element code
        element_code = extract_element_code(finding_id)
        if element_code is not None:
            code_cat = categorize_by_element_code(element_code)
            if code_cat:
                if resolved_category is None:
                    resolved_category = code_cat
                    resolution_method = ResolutionMethod.ELEMENT_CODE
                elif code_cat != resolved_category:
                    alternatives.append((code_cat, ResolutionMethod.ELEMENT_CODE))

        # 3. Check keyword
        keyword_cat = categorize_by_keyword(finding_text)
        if keyword_cat:
            if resolved_category is None:
                resolved_category = keyword_cat
                resolution_method = ResolutionMethod.KEYWORD
            elif keyword_cat != resolved_category:
                alternatives.append((keyword_cat, ResolutionMethod.KEYWORD))

        # 4. Check persona default
        persona_cat = get_persona_primary_category(persona)
        if persona_cat:
            if resolved_category is None:
                resolved_category = persona_cat
                resolution_method = ResolutionMethod.PERSONA_DEFAULT
            elif persona_cat != resolved_category:
                alternatives.append((persona_cat, ResolutionMethod.PERSONA_DEFAULT))

        # 5. Fallback to OTHER
        if resolved_category is None:
            resolved_category = Category.OTHER
            resolution_method = ResolutionMethod.FALLBACK

        # Track statistics (invalidate cache)
        self._resolution_stats[resolution_method] += 1
        self._stats_cache = None

        # Determine if there was a conflict
        had_conflict = len(alternatives) > 0
        if had_conflict:
            self._conflict_count += 1
            logger.info(
                f"Category conflict resolved for {finding_id}: "
                f"resolved={resolved_category.value} ({resolution_method.value}) "
                f"alternatives={[(c.value, m.value) for c, m in alternatives]}"
            )

        return ConflictResolution(
            finding_id=finding_id,
            resolved_category=resolved_category,
            method=resolution_method,
            alternatives=alternatives,
            had_conflict=had_conflict,
        )

    @property
    def conflict_count(self) -> int:
        """Total number of conflicts resolved."""
        return self._conflict_count

    @property
    def resolution_stats(self) -> dict[ResolutionMethod, int]:
        """Statistics on resolution methods used (cached copy)."""
        if self._stats_cache is None:
            self._stats_cache = dict(self._resolution_stats)
        return self._stats_cache

    def reset_stats(self) -> None:
        """Reset conflict and resolution statistics."""
        self._conflict_count = 0
        self._resolution_stats = {method: 0 for method in ResolutionMethod}
        self._stats_cache = None

    def reset_id_generator(self) -> None:
        """Reset the finding ID generator (call between documents)."""
        self._id_generator.reset()

    def reset_all(self) -> None:
        """Reset both statistics and ID generator."""
        self.reset_stats()
        self.reset_id_generator()

    def resolve_with_id(
        self,
        finding_text: str,
        target_file: str,
        target_section: str,
        persona: str,
        priority: str,
        explicit_tag: Optional[str] = None,
    ) -> tuple[ConflictResolution, str]:
        """
        Resolve category and generate stable hash-based finding ID.

        This method combines category resolution with hash-based ID generation
        (v1.19.0+). Use this for new findings instead of separate resolve() + manual ID.

        Args:
            finding_text: Finding description text.
            target_file: Target file path (e.g., "BRD-02.6_functional.md").
            target_section: Section identifier (e.g., "Section 6.1").
            persona: Persona that generated the finding.
            priority: Priority level (P0, P1, P2).
            explicit_tag: Optional [CAT:xxx] tag from prompt.

        Returns:
            Tuple of (ConflictResolution, finding_id) where finding_id is
            in new hash format: P{0-2}-{xxxx}
        """
        # Resolve category using existing method
        resolution = self.resolve(
            finding_id="",  # ID will be generated, not used for resolution
            finding_text=finding_text,
            persona=persona,
            explicit_tag=explicit_tag,
        )

        # Generate hash-based finding ID
        identity = FindingIdentity(
            priority=priority.upper(),
            target_file=target_file,
            target_section=target_section,
            category=resolution.resolved_category.name,
            description=finding_text[:100],
        )

        finding_id = self._id_generator.generate(identity)

        # Update the resolution with the generated ID
        updated_resolution = ConflictResolution(
            finding_id=finding_id,
            resolved_category=resolution.resolved_category,
            method=resolution.method,
            alternatives=resolution.alternatives,
            had_conflict=resolution.had_conflict,
        )

        return updated_resolution, finding_id

    def get_stats_summary(self) -> str:
        """Generate summary of resolution statistics."""
        lines = ["Category Resolution Statistics:", ""]
        total = sum(self._resolution_stats.values())

        if total == 0:
            return "No resolutions performed."

        for method, count in self._resolution_stats.items():
            pct = (count / total) * 100 if total > 0 else 0
            lines.append(f"  {method.value}: {count} ({pct:.1f}%)")

        lines.append(f"\nTotal resolutions: {total}")
        lines.append(f"Conflicts resolved: {self._conflict_count}")

        return "\n".join(lines)


def parse_category_tag(text: str) -> Optional[str]:
    """
    Parse [CAT:xxx] tag from text.

    Args:
        text: Text that may contain category tag.

    Returns:
        Category name (lowercase), or None if no tag found.
    """
    match = re.search(r"\[CAT:(\w+)\]", text, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return None


def strip_category_tag(text: str) -> str:
    """
    Remove [CAT:xxx] tag from text.

    Args:
        text: Text that may contain category tag.

    Returns:
        Text with tag removed.
    """
    return re.sub(r"\s*\[CAT:\w+\]", "", text, flags=re.IGNORECASE).strip()
