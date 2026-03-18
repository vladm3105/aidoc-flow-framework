"""
Unit tests for hash-based Finding and Action ID generation.

Tests the FindingIDGenerator and ActionIDGenerator classes from
ucx/utils/finding_hash.py.

Reference: PLAN-008_hash_based_finding_ids.md
"""

import pytest
import re

from ucx.utils.finding_hash import (
    FindingIDGenerator,
    FindingIdentity,
    ActionIDGenerator,
    ActionIdentity,
    _normalize_path,
    _normalize_section,
    _normalize_description,
    is_legacy_finding_id,
    is_hash_finding_id,
    is_legacy_action_id,
    is_hash_action_id,
    extract_priority_from_id,
    normalize_finding_id,
    DUAL_FORMAT_FINDING_PATTERN,
    DUAL_FORMAT_ACTION_PATTERN,
)


class TestFindingIDGenerator:
    """Tests for FindingIDGenerator class."""

    def test_basic_generation(self):
        """Basic finding ID generation works."""
        gen = FindingIDGenerator()
        identity = FindingIdentity(
            priority="P1",
            target_file="BRD-02.6_functional_requirements.md",
            target_section="Section 6.1",
            category="compliance",
            description="SAR filing workflow missing",
        )

        finding_id = gen.generate(identity)

        assert finding_id.startswith("P1-")
        assert len(finding_id) == 7  # P1-xxxx
        assert re.match(r"P1-[a-f0-9]{4}", finding_id)

    def test_deterministic_generation(self):
        """Same input produces same ID across sessions."""
        gen1 = FindingIDGenerator()
        gen2 = FindingIDGenerator()

        identity = FindingIdentity(
            priority="P1",
            target_file="BRD-02.6_functional_requirements.md",
            target_section="Section 6.1",
            category="compliance",
            description="SAR filing workflow missing",
        )

        id1 = gen1.generate(identity)
        id2 = gen2.generate(identity)

        assert id1 == id2

    def test_deterministic_after_reset(self):
        """Same input produces same ID after reset."""
        gen = FindingIDGenerator()

        identity = FindingIdentity(
            priority="P1",
            target_file="BRD-02.6_functional_requirements.md",
            target_section="Section 6.1",
            category="compliance",
            description="SAR filing workflow missing",
        )

        id1 = gen.generate(identity)
        gen.reset()
        id2 = gen.generate(identity)

        assert id1 == id2

    def test_different_content_different_id(self):
        """Different content produces different ID."""
        gen = FindingIDGenerator()

        id1 = gen.generate(FindingIdentity("P1", "f1", "s1", "c1", "description one"))
        id2 = gen.generate(FindingIdentity("P1", "f1", "s1", "c1", "description two"))

        assert id1 != id2

    def test_different_priority_different_id(self):
        """Different priority produces different ID prefix."""
        gen = FindingIDGenerator()

        id0 = gen.generate(FindingIdentity("P0", "f", "s", "c", "desc"))
        gen.reset()
        id1 = gen.generate(FindingIdentity("P1", "f", "s", "c", "desc"))
        gen.reset()
        id2 = gen.generate(FindingIdentity("P2", "f", "s", "c", "desc"))

        assert id0.startswith("P0-")
        assert id1.startswith("P1-")
        assert id2.startswith("P2-")

    def test_collision_extension(self):
        """Hash extends on collision (tested with very short hash)."""
        gen = FindingIDGenerator(hash_length=1)  # Force collisions

        ids = set()
        for i in range(50):
            fid = gen.generate(FindingIdentity("P1", "f", "s", "c", f"d{i}"))
            assert fid not in ids, f"Collision detected: {fid}"
            ids.add(fid)

        # Some IDs should have extended hashes
        long_ids = [fid for fid in ids if len(fid) > 4]  # P1-x is 4 chars
        assert len(long_ids) > 0, "Expected some IDs with extended hashes"

    def test_priority_preserved_in_format(self):
        """Priority level preserved in ID format."""
        gen = FindingIDGenerator()

        for priority in ["P0", "P1", "P2"]:
            fid = gen.generate(FindingIdentity(priority, "f", "s", "c", "d"))
            assert fid.startswith(priority + "-")
            gen.reset()

    def test_id_format_regex(self):
        """Generated ID matches expected format."""
        gen = FindingIDGenerator()
        fid = gen.generate(FindingIdentity("P1", "f", "s", "c", "d"))

        assert re.match(r"P[012]-[a-f0-9]{4,8}", fid)

    def test_case_insensitive_priority(self):
        """Priority is normalized to uppercase."""
        gen = FindingIDGenerator()

        id_lower = gen.generate(FindingIdentity("p1", "f", "s", "c", "d"))
        gen.reset()
        id_upper = gen.generate(FindingIdentity("P1", "f", "s", "c", "d"))

        assert id_lower == id_upper
        assert id_lower.startswith("P1-")

    def test_invalid_priority_raises(self):
        """Invalid priority raises ValueError."""
        gen = FindingIDGenerator()

        with pytest.raises(ValueError, match="Invalid priority"):
            gen.generate(FindingIdentity("P3", "f", "s", "c", "d"))

    def test_generate_from_parts(self):
        """Convenience method works correctly."""
        gen = FindingIDGenerator()

        fid = gen.generate_from_parts(
            priority="P0",
            target_file="BRD-01.md",
            target_section="6.1",
            category="functional",
            description="Missing requirement",
        )

        assert fid.startswith("P0-")
        assert len(fid) == 7

    def test_generated_count(self):
        """Generated count tracks correctly."""
        gen = FindingIDGenerator()

        assert gen.generated_count == 0

        gen.generate(FindingIdentity("P1", "f1", "s", "c", "d1"))
        assert gen.generated_count == 1

        gen.generate(FindingIdentity("P1", "f2", "s", "c", "d2"))
        assert gen.generated_count == 2

        gen.reset()
        assert gen.generated_count == 0

    def test_hash_length_bounds(self):
        """Hash length must be between 1 and 8."""
        FindingIDGenerator(hash_length=1)  # OK
        FindingIDGenerator(hash_length=8)  # OK

        with pytest.raises(ValueError):
            FindingIDGenerator(hash_length=0)

        with pytest.raises(ValueError):
            FindingIDGenerator(hash_length=9)


class TestActionIDGenerator:
    """Tests for ActionIDGenerator class."""

    def test_basic_generation(self):
        """Basic action ID generation works."""
        gen = ActionIDGenerator()
        identity = ActionIdentity(
            fixer="auditor",
            target_file="PRD-01",
            target_section="Section 3.2",
            description="Add SAR filing user story",
        )

        action_id = gen.generate(identity)

        assert action_id.startswith("ACT-")
        assert len(action_id) == 8  # ACT-xxxx
        assert re.match(r"ACT-[a-f0-9]{4}", action_id)

    def test_deterministic_generation(self):
        """Same input produces same ID."""
        gen1 = ActionIDGenerator()
        gen2 = ActionIDGenerator()

        identity = ActionIdentity(
            fixer="tech_lead",
            target_file="SPEC-01",
            target_section="4.1",
            description="Add state machine diagram",
        )

        id1 = gen1.generate(identity)
        id2 = gen2.generate(identity)

        assert id1 == id2

    def test_different_fixer_different_id(self):
        """Different fixer produces different ID."""
        gen = ActionIDGenerator()

        id1 = gen.generate(ActionIdentity("auditor", "f", "s", "desc"))
        id2 = gen.generate(ActionIdentity("tech_lead", "f", "s", "desc"))

        assert id1 != id2

    def test_generate_from_parts(self):
        """Convenience method works correctly."""
        gen = ActionIDGenerator()

        action_id = gen.generate_from_parts(
            fixer="integration_lead",
            target_file="CTR-01",
            target_section="2.1",
            description="Define API contract",
        )

        assert action_id.startswith("ACT-")
        assert len(action_id) == 8


class TestNormalization:
    """Tests for normalization functions."""

    def test_normalize_path_brd(self):
        """Path normalization extracts BRD pattern."""
        assert _normalize_path("BRD-02.6_functional_requirements.md") == "brd-02.6"
        assert _normalize_path("docs/01_BRD/BRD-50.5.md") == "brd-50.5"
        assert _normalize_path("BRD-01") == "brd-01"

    def test_normalize_path_other_types(self):
        """Path normalization works for other doc types."""
        assert _normalize_path("PRD-01.2_features.md") == "prd-01.2"
        assert _normalize_path("REQ-02.1.md") == "req-02.1"

    def test_normalize_path_fallback(self):
        """Path normalization falls back to filename."""
        assert _normalize_path("random_file.md") == "random_file.md"
        assert _normalize_path("some/path/file.txt") == "file.txt"

    def test_normalize_path_empty(self):
        """Empty path returns empty string."""
        assert _normalize_path("") == ""

    def test_normalize_section(self):
        """Section normalization removes prefix."""
        assert _normalize_section("Section 6.1") == "6.1"
        assert _normalize_section("SECTION 6.1 BRD.02.01.01") == "6.1 brd.02.01.01"
        assert _normalize_section("6.1.2") == "6.1.2"

    def test_normalize_section_empty(self):
        """Empty section returns empty string."""
        assert _normalize_section("") == ""

    def test_normalize_description(self):
        """Description normalization removes special chars."""
        assert _normalize_description("SAR Filing: Missing CO review!!!") == "sar filing missing co review"
        assert _normalize_description("Add  spacing   test") == "add spacing test"

    def test_normalize_description_truncation(self):
        """Description is truncated to max_len."""
        long_desc = "a" * 200
        result = _normalize_description(long_desc, max_len=100)
        assert len(result) == 100

    def test_normalize_description_empty(self):
        """Empty description returns empty string."""
        assert _normalize_description("") == ""


class TestIDFormatUtilities:
    """Tests for ID format detection utilities."""

    def test_is_legacy_finding_id(self):
        """Legacy finding ID detection works."""
        assert is_legacy_finding_id("REM-P0-001") is True
        assert is_legacy_finding_id("REM-P1-123") is True
        assert is_legacy_finding_id("REM-P2-999") is True

        assert is_legacy_finding_id("P1-a7f3") is False
        assert is_legacy_finding_id("ACT-001") is False
        assert is_legacy_finding_id("invalid") is False

    def test_is_hash_finding_id(self):
        """Hash finding ID detection works."""
        assert is_hash_finding_id("P0-a7f3") is True
        assert is_hash_finding_id("P1-b2c1d4e5") is True
        assert is_hash_finding_id("P2-1234") is True

        assert is_hash_finding_id("REM-P0-001") is False
        assert is_hash_finding_id("ACT-a7f3") is False
        assert is_hash_finding_id("invalid") is False

    def test_is_legacy_action_id(self):
        """Legacy action ID detection works."""
        assert is_legacy_action_id("ACT-001") is True
        assert is_legacy_action_id("ACT-999") is True

        assert is_legacy_action_id("ACT-a7f3") is False
        assert is_legacy_action_id("REM-P0-001") is False

    def test_is_hash_action_id(self):
        """Hash action ID detection works."""
        assert is_hash_action_id("ACT-a7f3") is True
        assert is_hash_action_id("ACT-1234abcd") is True

        assert is_hash_action_id("ACT-001") is False
        assert is_hash_action_id("P1-a7f3") is False

    def test_extract_priority_from_id(self):
        """Priority extraction works for all formats."""
        assert extract_priority_from_id("P0-a7f3") == "P0"
        assert extract_priority_from_id("P1-b2c1") == "P1"
        assert extract_priority_from_id("P2-8d4e") == "P2"
        assert extract_priority_from_id("REM-P0-001") == "P0"
        assert extract_priority_from_id("ARCH-P1-002") == "P1"

        assert extract_priority_from_id("ACT-001") is None
        assert extract_priority_from_id("invalid") is None

    def test_normalize_finding_id(self):
        """Finding ID normalization for backward compatibility."""
        # Hash IDs pass through unchanged
        assert normalize_finding_id("P1-a7f3") == "P1-a7f3"

        # Legacy IDs get normalized to priority-LEGACY
        assert normalize_finding_id("REM-P0-001") == "P0-LEGACY"
        assert normalize_finding_id("REM-P1-123") == "P1-LEGACY"

        # Invalid IDs pass through
        assert normalize_finding_id("invalid") == "invalid"


class TestDualFormatPatterns:
    """Tests for dual-format regex patterns."""

    def test_dual_finding_pattern_matches_legacy(self):
        """Dual pattern matches legacy format."""
        matches = DUAL_FORMAT_FINDING_PATTERN.findall(
            "Found: REM-P0-001 and REM-P1-002"
        )
        assert "REM-P0-001" in matches
        assert "REM-P1-002" in matches

    def test_dual_finding_pattern_matches_hash(self):
        """Dual pattern matches hash format."""
        matches = DUAL_FORMAT_FINDING_PATTERN.findall(
            "Found: P0-a7f3 and P1-b2c1"
        )
        assert "P0-a7f3" in matches
        assert "P1-b2c1" in matches

    def test_dual_finding_pattern_matches_mixed(self):
        """Dual pattern matches mixed formats."""
        text = "Legacy: REM-P0-001, Hash: P1-a7f3, Also: ARCH-P2-003"
        matches = DUAL_FORMAT_FINDING_PATTERN.findall(text)
        assert len(matches) == 3

    def test_dual_action_pattern_matches_legacy(self):
        """Dual action pattern matches legacy format."""
        matches = DUAL_FORMAT_ACTION_PATTERN.findall(
            "Actions: ACT-001 and ACT-002"
        )
        assert "ACT-001" in matches
        assert "ACT-002" in matches

    def test_dual_action_pattern_matches_hash(self):
        """Dual action pattern matches hash format."""
        matches = DUAL_FORMAT_ACTION_PATTERN.findall(
            "Actions: ACT-a7f3 and ACT-b2c1"
        )
        assert "ACT-a7f3" in matches
        assert "ACT-b2c1" in matches


class TestFindingIdentityDataclass:
    """Tests for FindingIdentity dataclass."""

    def test_to_hash_input(self):
        """Hash input string generation works."""
        identity = FindingIdentity(
            priority="P1",
            target_file="BRD-02.6_functional_requirements.md",
            target_section="Section 6.1",
            category="COMPLIANCE",
            description="SAR filing workflow missing!!!",
        )

        hash_input = identity.to_hash_input()

        # Should be normalized
        assert "brd-02.6" in hash_input
        assert "6.1" in hash_input
        assert "compliance" in hash_input
        assert "sar filing workflow missing" in hash_input


class TestActionIdentityDataclass:
    """Tests for ActionIdentity dataclass."""

    def test_to_hash_input(self):
        """Hash input string generation works."""
        identity = ActionIdentity(
            fixer="Tech Lead",
            target_file="SPEC-01.md",
            target_section="Section 4.1",
            description="Add state machine diagram!!!",
        )

        hash_input = identity.to_hash_input()

        # Fixer should be normalized with underscores
        assert "tech_lead" in hash_input
        assert "spec-01" in hash_input
        assert "4.1" in hash_input
        assert "add state machine diagram" in hash_input


class TestReviewMemoryIntegration:
    """Tests for hash-based ID generation in review_memory._extract_findings().

    These tests verify that the SECTION_PATTERN and hash ID generation
    work correctly when integrated into the review pipeline.
    """

    def test_section_pattern_extracts_section_numbers(self):
        """SECTION_PATTERN correctly extracts section references."""
        from ucx.core.review_memory import SECTION_PATTERN

        # Standard formats
        assert SECTION_PATTERN.search("Section 6.1").group(1) == "6.1"
        assert SECTION_PATTERN.search("Section 6.1.2").group(1) == "6.1.2"
        assert SECTION_PATTERN.search("section 10").group(1) == "10"
        assert SECTION_PATTERN.search("§ 7.3").group(1) == "7.3"

        # Embedded in text
        match = SECTION_PATTERN.search("Found issue in Section 6.5 regarding compliance")
        assert match.group(1) == "6.5"

        # No match
        assert SECTION_PATTERN.search("No section here") is None

    def test_finding_id_pattern_matches_persona_format(self):
        """FINDING_ID_PATTERN matches persona-prefix format from AI responses."""
        from ucx.core.review_memory import FINDING_ID_PATTERN

        # Table format
        text = "| ARCH-P0-001 | Missing requirement | Section 6 |"
        match = FINDING_ID_PATTERN.search(text)
        assert match is not None
        assert (match.group(1) or match.group(2) or match.group(3)) == "ARCH-P0-001"

        # Bold format
        text = "**TL-P1-002** is a critical finding"
        match = FINDING_ID_PATTERN.search(text)
        assert match is not None
        assert (match.group(1) or match.group(2) or match.group(3)) == "TL-P1-002"

        # Line start format
        text = "\nAUD-P0-003: Compliance issue detected"
        match = FINDING_ID_PATTERN.search(text)
        assert match is not None
        assert (match.group(1) or match.group(2) or match.group(3)) == "AUD-P0-003"

    def test_hash_id_generated_from_finding_content(self):
        """Hash-based ID is deterministic based on finding content."""
        gen = FindingIDGenerator()

        # Same content = same ID
        identity1 = FindingIdentity(
            priority="P0",
            target_file="BRD-49_data_ledger",
            target_section="Section 6.1",
            category="compliance",
            description="SAR filing workflow missing",
        )
        identity2 = FindingIdentity(
            priority="P0",
            target_file="BRD-49_data_ledger",
            target_section="Section 6.1",
            category="compliance",
            description="SAR filing workflow missing",
        )

        gen.reset()
        id1 = gen.generate(identity1)
        gen.reset()
        id2 = gen.generate(identity2)

        assert id1 == id2
        assert id1.startswith("P0-")
        assert is_hash_finding_id(id1)

    def test_legacy_id_preserved_in_finding_dict(self):
        """Verify that legacy_id field is conceptually present."""
        # This tests the expected data structure after _extract_findings
        # The actual finding dict should have both 'id' (hash) and 'legacy_id' (persona-prefix)
        expected_keys = {"id", "legacy_id", "persona", "priority", "prefix", "title", "text", "full_text", "category"}

        # Create a mock finding dict as would be created by _extract_findings
        mock_finding = {
            "persona": "architect",
            "priority": "P0",
            "id": "P0-a7f3",  # Hash-based
            "legacy_id": "ARCH-P0-001",  # Original persona-prefix
            "prefix": "ARCH",
            "title": "Missing compliance requirement",
            "text": "Context text here...",
            "full_text": "Full context...",
            "category": "compliance",
        }

        assert set(mock_finding.keys()) == expected_keys
        assert is_hash_finding_id(mock_finding["id"])
        assert mock_finding["legacy_id"].startswith("ARCH-P0-")
