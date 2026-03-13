"""Tests for context engineering functionality.

Tests the hierarchical document context and prior findings summarization.
Reference: PLAN-003_persona_prompt_restructuring.md
"""

import pytest

from ucx.core.context_engine import (
    ContextEngine,
    ContextLevel,
    PriorFindingsSummarizer,
    PERSONA_SECTION_MAP,
    PERSONA_PREFIX_MAP,
    ALWAYS_SKIP_SECTIONS,
    build_attention_steering_format,
    build_chairperson_manifest_format,
)


class TestContextEngine:
    """Test context engineering functionality."""

    @pytest.fixture
    def sample_sections(self):
        """Sample BRD sections for testing."""
        return {
            "BRD-01.0": "# Index\nDocument overview and table of contents...",
            "BRD-01.2": "# Business Context\nMarket analysis and business drivers...",
            "BRD-01.3": "# Scope\nProject scope and boundaries...",
            "BRD-01.6": "# Functional Requirements\nTransaction flows and core features...",
            "BRD-01.7": "# Quality Attributes\nPerformance targets and SLAs...",
            "BRD-01.10": "# Risk Management\nRisk register and mitigations...",
            "BRD-01.13": "# Cost-Benefit\nFinancial projections and ROI...",
            "BRD-01.14": "# Glossary\nTerms and definitions...",
            "BRD-01.18": "# Appendices\nTechnical details and diagrams...",
        }

    def test_architect_gets_relevant_sections(self, sample_sections):
        """Architect should get technical sections, skip cost/glossary."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("architect")

        assert "BRD-01.6" in ctx.sections_included
        assert "BRD-01.7" in ctx.sections_included
        assert "BRD-01.3" in ctx.sections_included
        assert "BRD-01.13" in ctx.sections_skipped  # Cost
        assert "BRD-01.14" in ctx.sections_skipped  # Glossary

    def test_strategist_gets_business_sections(self, sample_sections):
        """Strategist should get business sections, skip technical."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("strategist")

        assert "BRD-01.2" in ctx.sections_included
        assert "BRD-01.13" in ctx.sections_included
        # Note: strategist skips BRD-01.6, BRD-01.7, BRD-01.18
        assert "BRD-01.18" in ctx.sections_skipped  # Technical appendix

    def test_fact_checker_gets_most_sections(self, sample_sections):
        """Fact Checker should get all sections except glossary/index."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("fact_checker")

        # Should include most sections
        assert len(ctx.sections_included) >= 5
        assert "BRD-01.14" in ctx.sections_skipped  # Glossary

    def test_chairperson_gets_most_sections(self, sample_sections):
        """Chairperson should get comprehensive view."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("chairperson")

        # Should include most sections
        assert len(ctx.sections_included) >= 5

    def test_level1_overview_generated(self, sample_sections):
        """Level 1 should contain document overview."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("architect")

        assert "LEVEL 1: DOCUMENT OVERVIEW" in ctx.level1_overview
        assert "Section Index" in ctx.level1_overview

    def test_level2_relevant_sections_included(self, sample_sections):
        """Level 2 should contain persona-relevant sections."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("architect")

        assert "LEVEL 2: RELEVANT SECTIONS FOR ARCHITECT" in ctx.level2_relevant
        assert "Functional Requirements" in ctx.level2_relevant or "BRD-01.6" in ctx.level2_relevant

    def test_level3_reference_appendices(self, sample_sections):
        """Level 3 should contain optional appendices when requested."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("architect", include_level3=True)

        # Architect has BRD-01.18 as optional
        if ctx.level3_reference:
            assert "LEVEL 3: REFERENCE APPENDICES" in ctx.level3_reference

    def test_context_estimates_tokens(self, sample_sections):
        """Context should estimate token count."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("architect")

        assert ctx.total_tokens > 0
        # Rough check: tokens should be approximately chars / 4
        total_chars = len(ctx.level1_overview) + len(ctx.level2_relevant)
        assert ctx.total_tokens == total_chars // 4

    def test_context_tracks_included_sections(self, sample_sections):
        """Context should track which sections were included."""
        engine = ContextEngine(sample_sections)
        ctx = engine.build_hierarchical_context("architect")

        assert isinstance(ctx.sections_included, list)
        assert isinstance(ctx.sections_skipped, list)
        assert len(ctx.sections_included) > 0

    def test_always_skip_sections(self, sample_sections):
        """Certain sections should always be skipped."""
        engine = ContextEngine(sample_sections)

        # Glossary should be skipped for any persona
        for persona in ["architect", "auditor", "strategist"]:
            ctx = engine.build_hierarchical_context(persona)
            # BRD-01.14 is glossary
            assert "BRD-01.14" in ctx.sections_skipped or "glossary" in str(ctx.sections_skipped).lower()


class TestPriorFindingsSummarizer:
    """Test prior findings summarization."""

    def test_summarize_extracts_counts(self):
        """Should extract P0/P1/P2 counts correctly."""
        responses = {
            "architect": "| ARCH-P0-001 | Gap 1 |\n| ARCH-P0-002 | Gap 2 |\n| ARCH-P1-001 | Gap 3 |",
            "auditor": "| AUD-P0-001 | Compliance gap |",
        }

        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(responses, "tech_lead")

        assert "| architect | 2 | 1 |" in summary
        assert "| auditor | 1 | 0 |" in summary

    def test_summarize_lists_critical_p0s(self):
        """Should list critical P0 findings."""
        responses = {
            "architect": "| ARCH-P0-001 | Missing failover |",
        }

        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(responses, "tech_lead")

        assert "ARCH-P0-001" in summary
        assert "Critical P0 Findings" in summary

    def test_summarize_includes_totals(self):
        """Should include total counts."""
        responses = {
            "architect": "| ARCH-P0-001 | x |\n| ARCH-P0-002 | y |",
            "auditor": "| AUD-P0-001 | z |",
        }

        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(responses, "tech_lead")

        assert "TOTAL" in summary

    def test_summarize_includes_focus_guidance(self):
        """Should include guidance for current persona."""
        responses = {
            "architect": "| ARCH-P0-001 | x |",
        }

        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(responses, "tech_lead")

        assert "TECH_LEAD" in summary
        assert "Focus Areas" in summary

    def test_summary_smaller_than_raw(self):
        """Summary should be significantly smaller than raw responses."""
        # Simulate 5K per persona
        responses = {
            "architect": "| ARCH-P0-001 | " + "x" * 5000,
            "auditor": "| AUD-P0-001 | " + "x" * 5000,
            "tech_lead": "| TL-P0-001 | " + "x" * 5000,
        }

        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(responses, "operator")

        raw_size = sum(len(r) for r in responses.values())
        assert len(summary) < raw_size * 0.3  # At least 70% reduction

    def test_empty_responses_handled(self):
        """Should handle empty responses gracefully."""
        responses = {}

        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(responses, "tech_lead")

        assert "PRIOR FINDINGS SUMMARY" in summary

    def test_no_findings_in_response(self):
        """Should handle responses with no findings."""
        responses = {
            "architect": "This response has no findings in the expected format.",
        }

        summarizer = PriorFindingsSummarizer()
        summary = summarizer.summarize_all(responses, "tech_lead")

        assert "| architect | 0 | 0 |" in summary


class TestPersonaSectionMap:
    """Test persona section mapping configuration."""

    def test_all_personas_have_mapping(self):
        """All expected personas should have a section mapping."""
        expected_personas = [
            "architect", "auditor", "tech_lead", "strategist",
            "devils_advocate", "operator", "integration_lead",
            "product_owner", "business_analyst", "fact_checker", "chairperson"
        ]

        for persona in expected_personas:
            assert persona in PERSONA_SECTION_MAP, f"Missing mapping for: {persona}"

    def test_mappings_have_required_keys(self):
        """Each mapping should have required, optional, and skip keys."""
        for persona, mapping in PERSONA_SECTION_MAP.items():
            assert "required" in mapping, f"Missing 'required' for: {persona}"
            assert "optional" in mapping, f"Missing 'optional' for: {persona}"
            assert "skip" in mapping, f"Missing 'skip' for: {persona}"


class TestPersonaPrefixMap:
    """Test persona prefix mapping for finding IDs."""

    def test_all_personas_have_prefix(self):
        """All personas should have a prefix defined."""
        expected_personas = [
            "architect", "auditor", "tech_lead", "strategist",
            "devils_advocate", "operator", "integration_lead",
            "product_owner", "business_analyst", "fact_checker",
            "chairperson", "qa_lead", "ux_strategist", "requirements_specialist"
        ]

        for persona in expected_personas:
            assert persona in PERSONA_PREFIX_MAP, f"Missing prefix for: {persona}"

    def test_prefixes_are_valid_length(self):
        """Prefixes should be 2-4 characters."""
        for persona, prefix in PERSONA_PREFIX_MAP.items():
            assert 2 <= len(prefix) <= 4, f"Invalid prefix length for {persona}: {prefix}"

    def test_prefixes_are_uppercase(self):
        """Prefixes should be uppercase."""
        for persona, prefix in PERSONA_PREFIX_MAP.items():
            assert prefix == prefix.upper(), f"Prefix not uppercase for {persona}: {prefix}"


class TestAttentionSteeringFormat:
    """Test attention steering format functions."""

    def test_attention_steering_contains_prefix(self):
        """Attention steering should include the persona prefix."""
        result = build_attention_steering_format("architect", "ARCH")

        assert "ARCH" in result
        assert "ARCH-P0-001" in result

    def test_attention_steering_contains_format_instructions(self):
        """Attention steering should contain format instructions."""
        result = build_attention_steering_format("architect", "ARCH")

        assert "REQUIRED OUTPUT FORMAT" in result
        assert "Finding ID Format" in result
        assert "Required Output Table" in result

    def test_attention_steering_contains_rules(self):
        """Attention steering should contain formatting rules."""
        result = build_attention_steering_format("architect", "ARCH")

        assert "Rules" in result
        assert "unique ID" in result.lower() or "ID" in result

    def test_chairperson_manifest_contains_markers(self):
        """Chairperson manifest should contain UCX markers."""
        result = build_chairperson_manifest_format()

        assert "<!-- UCX-MANIFEST-START -->" in result
        assert "<!-- UCX-MANIFEST-END -->" in result

    def test_chairperson_manifest_contains_tables(self):
        """Chairperson manifest should contain required tables."""
        result = build_chairperson_manifest_format()

        assert "Manifest Summary" in result
        assert "Category Summary" in result
        assert "Findings Table" in result

    def test_chairperson_manifest_contains_rem_format(self):
        """Chairperson manifest should show REM prefix format."""
        result = build_chairperson_manifest_format()

        assert "REM-P0-001" in result


class TestAlwaysSkipSections:
    """Test always-skip sections configuration."""

    def test_always_skip_contains_expected(self):
        """Always-skip list should contain expected low-value sections."""
        assert "glossary" in ALWAYS_SKIP_SECTIONS
        assert "traceability" in ALWAYS_SKIP_SECTIONS
        assert "index" in ALWAYS_SKIP_SECTIONS

    def test_always_skip_is_lowercase(self):
        """Always-skip terms should be lowercase for matching."""
        for term in ALWAYS_SKIP_SECTIONS:
            assert term == term.lower(), f"Term should be lowercase: {term}"
