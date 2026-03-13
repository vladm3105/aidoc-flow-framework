"""Tests for finding ID extraction patterns.

Tests the canonical PREFIX-P0-NNN format used by UCX personas.
Reference: PLAN-003_persona_prompt_restructuring.md
"""

import pytest
import re

# Import the pattern and parse function from review_memory
from ucx.core.review_memory import FINDING_ID_PATTERN, _parse_finding_id


class TestFindingIdPattern:
    """Test the canonical finding ID pattern extraction."""

    def test_table_format_basic(self):
        """Test PREFIX-P0-NNN in table without formatting."""
        text = "| ARCH-P0-001 | Missing failover | Section 6 |"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1
        # findall returns tuples of groups
        raw_id = matches[0][0] or matches[0][1] or matches[0][2]
        assert raw_id == "ARCH-P0-001"

    def test_table_format_bold(self):
        """Test **PREFIX-P0-NNN** in table with bold formatting."""
        text = "| **ARCH-P0-001** | Missing failover | Section 6 |"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1
        raw_id = matches[0][0] or matches[0][1] or matches[0][2]
        assert raw_id == "ARCH-P0-001"

    def test_bold_format_standalone(self):
        """Test **PREFIX-P0-NNN** format outside table."""
        text = "**TL-P1-002**: Transaction state machine required"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1
        raw_id = matches[0][0] or matches[0][1] or matches[0][2]
        assert raw_id == "TL-P1-002"

    def test_line_start_format(self):
        """Test PREFIX-P0-NNN at line start."""
        text = "\nAUD-P0-003: OFAC screening frequency"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1
        raw_id = matches[0][0] or matches[0][1] or matches[0][2]
        assert raw_id == "AUD-P0-003"

    def test_all_priority_levels(self):
        """Test P0, P1, P2 extraction."""
        text = "| DA-P0-001 | x |\n| STR-P1-002 | y |\n| UX-P2-003 | z |"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 3

        ids = [m[0] or m[1] or m[2] for m in matches]
        assert "DA-P0-001" in ids
        assert "STR-P1-002" in ids
        assert "UX-P2-003" in ids

    def test_various_prefixes(self):
        """Test all supported persona prefixes."""
        prefixes = [
            "ARCH", "AUD", "TL", "OP", "IL", "DA",
            "STR", "PO", "BA", "FC", "REM", "QA", "UX", "RS"
        ]
        for prefix in prefixes:
            text = f"| {prefix}-P0-001 | Finding |"
            matches = FINDING_ID_PATTERN.findall(text)
            assert len(matches) == 1, f"Failed for prefix: {prefix}"
            raw_id = matches[0][0] or matches[0][1] or matches[0][2]
            assert raw_id == f"{prefix}-P0-001"

    def test_two_char_prefix(self):
        """Test 2-character prefix (minimum)."""
        text = "| TL-P0-001 | Tech lead finding |"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1

    def test_four_char_prefix(self):
        """Test 4-character prefix (maximum)."""
        text = "| ARCH-P0-001 | Architecture finding |"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1

    def test_three_digit_number(self):
        """Test 3-digit finding numbers."""
        text = "| ARCH-P0-123 | Finding 123 |"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1
        raw_id = matches[0][0] or matches[0][1] or matches[0][2]
        assert raw_id == "ARCH-P0-123"

    def test_single_digit_number(self):
        """Test single-digit finding number (should still match)."""
        text = "| ARCH-P0-1 | First finding |"
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 1

    def test_multiple_findings_in_text(self):
        """Test extracting multiple findings from mixed text."""
        text = """
## Architect Findings

| ID | Finding | Section |
|----|---------|---------|
| ARCH-P0-001 | Missing failover | 6.1 |
| ARCH-P0-002 | No retry logic | 6.2 |
| ARCH-P1-001 | Caching unclear | 6.3 |

**ARCH-P1-002**: Consider adding circuit breaker
"""
        matches = FINDING_ID_PATTERN.findall(text)
        assert len(matches) == 4

    def test_does_not_match_invalid_formats(self):
        """Test that invalid formats are not matched."""
        invalid_texts = [
            "P0-OP-001",        # Priority first (wrong order)
            "**[P0-1]**",      # Old bracket format
            "P0-1",            # Missing prefix
            "ARCHIT-P0-001",   # 5+ char prefix (invalid)
            "A-P0-001",        # 1 char prefix (too short)
        ]
        for text in invalid_texts:
            matches = FINDING_ID_PATTERN.findall(text)
            # Should not match, or if it does, should be empty
            if matches:
                raw_id = matches[0][0] or matches[0][1] or matches[0][2]
                assert raw_id != text, f"Should not match: {text}"


class TestParseFindingId:
    """Test the finding ID parser."""

    def test_parse_standard_format(self):
        """Test parsing standard PREFIX-P0-NNN format."""
        result = _parse_finding_id("ARCH-P0-001")
        assert result == ("ARCH", "P0", "001")

    def test_parse_p1_priority(self):
        """Test parsing P1 priority."""
        result = _parse_finding_id("TL-P1-002")
        assert result == ("TL", "P1", "002")

    def test_parse_p2_priority(self):
        """Test parsing P2 priority."""
        result = _parse_finding_id("UX-P2-003")
        assert result == ("UX", "P2", "003")

    def test_parse_four_char_prefix(self):
        """Test parsing 4-character prefix."""
        result = _parse_finding_id("ARCH-P0-001")
        assert result[0] == "ARCH"

    def test_parse_two_char_prefix(self):
        """Test parsing 2-character prefix."""
        result = _parse_finding_id("TL-P0-001")
        assert result[0] == "TL"

    def test_parse_three_digit_number(self):
        """Test parsing 3-digit number."""
        result = _parse_finding_id("FC-P0-123")
        assert result[2] == "123"

    def test_parse_malformed_returns_fallback(self):
        """Test that malformed IDs return fallback values."""
        result = _parse_finding_id("malformed")
        assert result == ("malformed", "P0", "000")


class TestFindingIdIntegration:
    """Integration tests for finding extraction workflow."""

    def test_extract_from_architect_response(self):
        """Test extraction from typical architect response."""
        response = """
## Architecture Review Findings

### Critical Findings

| ID | Finding | Section | Gap | Remediation |
|----|---------|---------|-----|-------------|
| ARCH-P0-001 | Missing partner failover criteria | 6.1 | No failover spec | Add SLA-based failover triggers |
| ARCH-P0-002 | In-flight transaction handling unclear | 6.2 | No compensation flow | Document saga pattern |

### High Priority Findings

| ID | Finding | Section | Gap | Remediation |
|----|---------|---------|-----|-------------|
| ARCH-P1-001 | Caching strategy undefined | 6.5 | Missing TTL | Specify cache policy |
"""
        matches = FINDING_ID_PATTERN.findall(response)
        assert len(matches) == 3

        ids = [m[0] or m[1] or m[2] for m in matches]
        assert "ARCH-P0-001" in ids
        assert "ARCH-P0-002" in ids
        assert "ARCH-P1-001" in ids

    def test_extract_from_chairperson_manifest(self):
        """Test extraction from chairperson manifest format."""
        response = """
<!-- UCX-MANIFEST-START -->

### Findings Table

| ID | Priority | Category | Status | Fixer | Target File | Description |
|----|----------|----------|--------|-------|-------------|-------------|
| REM-P0-001 | P0 | [CAT:compliance] | OPEN | auditor | BRD-01.6.md | Missing OFAC screening |
| REM-P0-002 | P0 | [CAT:integration] | OPEN | integration_lead | BRD-01.6.md | Webhook validation |
| REM-P1-001 | P1 | [CAT:functional] | OPEN | tech_lead | BRD-01.6.md | Idempotency pattern |

<!-- UCX-MANIFEST-END -->
"""
        matches = FINDING_ID_PATTERN.findall(response)
        assert len(matches) == 3

        ids = [m[0] or m[1] or m[2] for m in matches]
        assert "REM-P0-001" in ids
        assert "REM-P0-002" in ids
        assert "REM-P1-001" in ids

    def test_deduplication_same_id_multiple_locations(self):
        """Test that same ID appearing multiple times is handled."""
        response = """
| ARCH-P0-001 | Finding in table |
Reference to ARCH-P0-001 in text.
**ARCH-P0-001**: Detailed description here.
"""
        matches = FINDING_ID_PATTERN.findall(response)
        # Pattern may find multiple matches, deduplication happens at higher level
        ids = [m[0] or m[1] or m[2] for m in matches]
        # All should be ARCH-P0-001
        assert all(id == "ARCH-P0-001" for id in ids if id)
