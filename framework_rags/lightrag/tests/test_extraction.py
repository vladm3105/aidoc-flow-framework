"""Tests for LightRAG entity extraction."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "config"))

from entity_types import CUSTOM_ENTITY_TYPES, ENTITY_TYPE_DESCRIPTIONS


class TestEntityTypes:
    """Tests for entity type configuration."""

    def test_entity_types_defined(self):
        """Verify all 12 entity types are defined."""
        assert len(CUSTOM_ENTITY_TYPES) == 12

    def test_entity_types_have_descriptions(self):
        """Verify all entity types have descriptions."""
        for entity_type in CUSTOM_ENTITY_TYPES:
            assert entity_type in ENTITY_TYPE_DESCRIPTIONS
            assert len(ENTITY_TYPE_DESCRIPTIONS[entity_type]) > 10

    def test_expected_types_present(self):
        """Verify expected entity types are present."""
        expected = [
            "organization",
            "person",
            "product",
            "technology",
            "concept",
            "metric",
            "event",
            "decision",
            "finding",
            "risk",
            "regulation",
            "market_segment",
        ]
        for etype in expected:
            assert etype in CUSTOM_ENTITY_TYPES


class TestCustomPrompts:
    """Tests for custom extraction prompts."""

    def test_entity_extraction_prompt(self):
        """Test entity extraction prompt generation."""
        from lightrag_service.custom_prompts import get_entity_extraction_prompt

        prompt = get_entity_extraction_prompt()

        # Should contain all entity types
        for etype in CUSTOM_ENTITY_TYPES:
            assert etype in prompt

        # Should contain key instructions
        assert "Extract entities" in prompt or "Identify Entities" in prompt
        assert "Normalize" in prompt

    def test_query_prompt_modes(self):
        """Test query prompt for different modes."""
        from lightrag_service.custom_prompts import get_query_prompt

        modes = ["local", "global", "hybrid", "naive", "mix"]
        for mode in modes:
            prompt = get_query_prompt(mode)
            assert "Context:" in prompt
            assert "Question:" in prompt

    def test_relationship_extraction_prompt(self):
        """Test relationship extraction prompt."""
        from lightrag_service.custom_prompts import get_relationship_extraction_prompt

        prompt = get_relationship_extraction_prompt()

        # Should mention common relationships
        assert "develops" in prompt or "relationship" in prompt.lower()


class TestEntityExtraction:
    """Integration tests for entity extraction (requires API)."""

    @pytest.mark.skip(reason="Requires OpenAI API key")
    def test_extract_from_sample_doc(self, sample_research_doc, entity_types):
        """Test entity extraction from sample document."""
        # This would require actual API calls
        pass
