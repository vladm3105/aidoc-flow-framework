"""
Unit tests for UCX scoring conflicts module.

Tests category conflict resolution and tag parsing.
"""

import pytest

from ucx.scoring import (
    Category,
    CategoryConflictResolver,
    ConflictResolution,
    ResolutionMethod,
    parse_category_tag,
    strip_category_tag,
)


class TestCategoryConflictResolver:
    """Tests for CategoryConflictResolver class."""

    @pytest.fixture
    def resolver(self):
        """Create a fresh resolver."""
        return CategoryConflictResolver()

    def test_resolve_by_explicit_tag(self, resolver):
        """Explicit tag takes highest priority."""
        result = resolver.resolve(
            finding_id="BRD.01.01.01",  # Would be functional by code
            finding_text="Some compliance text",  # Would be compliance by keyword
            persona="architect",  # Would be architecture by default
            explicit_tag="risk"  # Explicit tag
        )
        assert result.resolved_category == Category.RISK
        assert result.method == ResolutionMethod.EXPLICIT_TAG
        assert result.had_conflict  # Multiple matches = conflict

    def test_resolve_by_element_code(self, resolver):
        """Element code is second priority."""
        result = resolver.resolve(
            finding_id="BRD.01.01.01",  # Element code 01 = functional
            finding_text="Random text",
            persona="architect",  # Would be architecture by default
            explicit_tag=None
        )
        assert result.resolved_category == Category.FUNCTIONAL
        assert result.method == ResolutionMethod.ELEMENT_CODE

    def test_resolve_by_keyword(self, resolver):
        """Keyword is third priority."""
        result = resolver.resolve(
            finding_id="ARCH-P0-001",  # No element code
            finding_text="KYC compliance requirement",  # Compliance keyword
            persona="architect",
            explicit_tag=None
        )
        assert result.resolved_category == Category.COMPLIANCE
        assert result.method == ResolutionMethod.KEYWORD

    def test_resolve_by_persona_default(self, resolver):
        """Persona default is fourth priority."""
        result = resolver.resolve(
            finding_id="ARCH-P0-001",  # No element code
            finding_text="Some generic finding",  # No keywords
            persona="architect",  # Primary: architecture
            explicit_tag=None
        )
        assert result.resolved_category == Category.ARCHITECTURE
        assert result.method == ResolutionMethod.PERSONA_DEFAULT

    def test_resolve_fallback_to_other(self, resolver):
        """Falls back to OTHER when nothing matches."""
        result = resolver.resolve(
            finding_id="XXX-001",
            finding_text="xyz abc 123",
            persona="chairperson",  # No primary category
            explicit_tag=None
        )
        assert result.resolved_category == Category.OTHER
        assert result.method == ResolutionMethod.FALLBACK

    def test_conflict_detection(self, resolver):
        """Detects when multiple methods would match."""
        result = resolver.resolve(
            finding_id="BRD.01.01.01",  # Functional by code
            finding_text="AML compliance requirement",  # Compliance by keyword
            persona="architect",  # Architecture by default
            explicit_tag=None
        )
        # Element code wins
        assert result.resolved_category == Category.FUNCTIONAL
        # But alternatives were found
        assert result.had_conflict
        assert len(result.alternatives) > 0

    def test_conflict_count_tracking(self, resolver):
        """Tracks total conflicts resolved."""
        assert resolver.conflict_count == 0

        # Resolve with conflict
        resolver.resolve(
            finding_id="BRD.01.01.01",
            finding_text="KYC compliance",  # Creates conflict
            persona="architect",
            explicit_tag=None
        )
        assert resolver.conflict_count == 1

        # Resolve without conflict
        resolver.resolve(
            finding_id="ARCH-P0-001",
            finding_text="generic text",
            persona="architect",
            explicit_tag=None
        )
        # Still 1 (no new conflict)
        assert resolver.conflict_count == 1


class TestResolutionStats:
    """Tests for resolution statistics tracking."""

    @pytest.fixture
    def resolver(self):
        return CategoryConflictResolver()

    def test_stats_tracking(self, resolver):
        """Tracks resolution methods used."""
        # Multiple resolutions
        resolver.resolve("BRD.01.01.01", "text", "arch", None)  # ELEMENT_CODE
        resolver.resolve("ARCH-P0-001", "KYC", "arch", None)  # KEYWORD
        resolver.resolve("XXX", "text", "architect", None)  # PERSONA_DEFAULT

        stats = resolver.resolution_stats
        assert stats[ResolutionMethod.ELEMENT_CODE] == 1
        assert stats[ResolutionMethod.KEYWORD] == 1
        assert stats[ResolutionMethod.PERSONA_DEFAULT] == 1

    def test_stats_reset(self, resolver):
        """Stats can be reset."""
        resolver.resolve("BRD.01.01.01", "text", "arch", None)
        resolver.reset_stats()

        assert resolver.conflict_count == 0
        assert all(v == 0 for v in resolver.resolution_stats.values())

    def test_stats_summary(self, resolver):
        """Generate summary text."""
        resolver.resolve("BRD.01.01.01", "text", "arch", None)
        resolver.resolve("ARCH-P0-001", "KYC", "arch", None)

        summary = resolver.get_stats_summary()
        assert "Resolution Statistics" in summary
        assert "element_code" in summary
        assert "Total resolutions: 2" in summary


class TestConflictResolutionDataclass:
    """Tests for ConflictResolution dataclass."""

    def test_is_fallback_property(self):
        """is_fallback identifies fallback resolutions."""
        fallback = ConflictResolution(
            finding_id="test",
            resolved_category=Category.OTHER,
            method=ResolutionMethod.FALLBACK,
            alternatives=[],
            had_conflict=False
        )
        assert fallback.is_fallback

        persona = ConflictResolution(
            finding_id="test",
            resolved_category=Category.ARCHITECTURE,
            method=ResolutionMethod.PERSONA_DEFAULT,
            alternatives=[],
            had_conflict=False
        )
        assert persona.is_fallback

        element = ConflictResolution(
            finding_id="test",
            resolved_category=Category.FUNCTIONAL,
            method=ResolutionMethod.ELEMENT_CODE,
            alternatives=[],
            had_conflict=False
        )
        assert not element.is_fallback


class TestParseCategoryTag:
    """Tests for parse_category_tag function."""

    @pytest.mark.parametrize("text,expected", [
        ("[CAT:functional] Missing scope", "functional"),
        ("Some text [CAT:compliance] more text", "compliance"),
        ("[CAT:RISK] Critical issue", "risk"),
        ("[cat:Architecture] Decision needed", "architecture"),
    ])
    def test_parse_valid_tag(self, text, expected):
        """Parse valid category tags."""
        assert parse_category_tag(text) == expected

    @pytest.mark.parametrize("text", [
        "No tag here",
        "[CAT:] empty tag",
        "[CATEGORY:functional] wrong format",
        "",
    ])
    def test_parse_no_tag(self, text):
        """Return None when no valid tag."""
        assert parse_category_tag(text) is None


class TestStripCategoryTag:
    """Tests for strip_category_tag function."""

    @pytest.mark.parametrize("text,expected", [
        ("[CAT:functional] Missing scope", "Missing scope"),
        ("Some text [CAT:compliance] more text", "Some text more text"),
        ("No tag here", "No tag here"),
        ("[CAT:risk]", ""),
    ])
    def test_strip_tag(self, text, expected):
        """Strip category tag from text."""
        assert strip_category_tag(text) == expected
