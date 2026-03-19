"""Tests for PRD creation improvements (PLAN-009)."""

import pytest
from pathlib import Path


class TestPRDPrompt:
    """Test UCC_PROMPT_PRD.md content."""

    @pytest.fixture
    def prompt_path(self):
        """Get the PRD prompt path."""
        return Path(__file__).parents[2] / "creation" / "UCC_PROMPT_PRD.md"

    @pytest.fixture
    def prompt_content(self, prompt_path):
        """Load prompt content."""
        return prompt_path.read_text(encoding="utf-8")

    def test_prompt_exists(self, prompt_path):
        """Verify PRD prompt file exists."""
        assert prompt_path.exists(), f"PRD prompt not found at {prompt_path}"

    def test_prompt_has_21_sections(self, prompt_content):
        """Verify prompt defines all 21 sections."""
        # Check section table has 21 entries
        section_count = prompt_content.count("| 1 |") + sum(
            1 for i in range(2, 22) if f"| {i} |" in prompt_content
        )
        assert section_count >= 21, f"Expected 21 sections, found {section_count}"

    def test_prompt_forbids_bdd_patterns(self, prompt_content):
        """Verify Given-When-Then is forbidden."""
        assert "FORBIDDEN" in prompt_content
        assert "Given" in prompt_content and "When" in prompt_content and "Then" in prompt_content

    def test_prompt_requires_section_10(self, prompt_content):
        """Verify Section 10 is marked as BLOCKING."""
        assert "BLOCKING" in prompt_content
        assert "Section 10" in prompt_content or "Customer-Facing" in prompt_content

    def test_prompt_has_layer_separation_note(self, prompt_content):
        """Verify Section 8 layer separation note requirement."""
        assert "Layer Separation Note" in prompt_content
        assert "EARS" in prompt_content and "BDD" in prompt_content

    def test_prompt_has_correct_type_codes(self, prompt_content):
        """Verify 13 element type codes defined."""
        expected_codes = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "11", "22", "23", "24"]
        for code in expected_codes:
            assert f"| {code} |" in prompt_content, f"Missing type code {code}"

    def test_prompt_has_dual_scoring(self, prompt_content):
        """Verify dual scoring guidance present."""
        assert "SYS-Ready" in prompt_content
        assert "EARS-Ready" in prompt_content
        assert "90%" in prompt_content or "≥90%" in prompt_content

    def test_prompt_has_diagram_requirements(self, prompt_content):
        """Verify diagram requirements present."""
        assert "c4-l2" in prompt_content
        assert "dfd-l1" in prompt_content
        assert "sequence-" in prompt_content

    def test_prompt_has_7_personas(self, prompt_content):
        """Verify 7 personas listed for PRD creation."""
        personas = [
            "PRODUCT_OWNER",
            "UX_STRATEGIST",
            "CONTENT_STRATEGIST",
            "TECH_LEAD",
            "QA_LEAD",
            "ARCHITECT",
            "REQUIREMENTS_SPECIALIST",
        ]
        for persona in personas:
            assert persona in prompt_content, f"Missing persona {persona}"


class TestPersonaFiles:
    """Test persona skill files."""

    @pytest.fixture
    def personas_dir(self):
        """Get personas directory."""
        return Path(__file__).parents[2] / "ucx" / "skills" / "personas"

    def test_content_strategist_exists(self, personas_dir):
        """Verify content_strategist persona file exists."""
        path = personas_dir / "content_strategist.md"
        assert path.exists(), f"content_strategist.md not found at {path}"

    def test_content_strategist_has_section_10_focus(self, personas_dir):
        """Verify content_strategist focuses on Section 10."""
        path = personas_dir / "content_strategist.md"
        content = path.read_text(encoding="utf-8")
        assert "Section 10" in content
        assert "BLOCKING" in content or "blocking" in content.lower()

    def test_requirements_specialist_has_ucc_phase(self, personas_dir):
        """Verify requirements_specialist supports UCC phase."""
        path = personas_dir / "requirements_specialist.md"
        content = path.read_text(encoding="utf-8")
        assert "ucc" in content.lower() or "Creation Focus" in content

    def test_requirements_specialist_has_layer_separation(self, personas_dir):
        """Verify requirements_specialist enforces layer separation."""
        path = personas_dir / "requirements_specialist.md"
        content = path.read_text(encoding="utf-8")
        assert "Layer Separation" in content or "layer separation" in content.lower()
        assert "FORBIDDEN" in content


class TestLayerSkills:
    """Test layer skills configuration."""

    def test_prd_has_seven_personas(self):
        """Verify PRD has 7 personas configured."""
        from ucx.config.layer_skills import UCC_LAYER_SKILLS
        from ucx.models.enums import DocType

        prd_skills = UCC_LAYER_SKILLS[DocType.PRD]
        assert len(prd_skills) == 7, f"Expected 7 personas, got {len(prd_skills)}: {prd_skills}"

    def test_prd_has_content_strategist(self):
        """Verify content_strategist in PRD skills."""
        from ucx.config.layer_skills import UCC_LAYER_SKILLS
        from ucx.models.enums import DocType

        prd_skills = UCC_LAYER_SKILLS[DocType.PRD]
        assert "content_strategist" in prd_skills

    def test_prd_has_requirements_specialist(self):
        """Verify requirements_specialist in PRD skills."""
        from ucx.config.layer_skills import UCC_LAYER_SKILLS
        from ucx.models.enums import DocType

        prd_skills = UCC_LAYER_SKILLS[DocType.PRD]
        assert "requirements_specialist" in prd_skills


class TestCreationAPI:
    """Test UCCPhase API."""

    def test_create_accepts_validate_after_param(self):
        """Verify create() accepts validate_after parameter."""
        from ucx.api.creation import UCCPhase
        import inspect

        sig = inspect.signature(UCCPhase.create)
        params = list(sig.parameters.keys())
        assert "validate_after" in params, "create() missing validate_after parameter"

    def test_validate_and_score_prd_method_exists(self):
        """Verify _validate_and_score_prd method exists."""
        from ucx.api.creation import UCCPhase

        assert hasattr(UCCPhase, "_validate_and_score_prd")


class TestPostCreationScoring:
    """Test scoring integration (requires PLAN-010 Phase 7)."""

    def test_scoring_module_graceful_import(self):
        """Verify scoring module import is handled gracefully."""
        # This test verifies the import handling works even if PLAN-010 not implemented
        try:
            from ucx.validators.prd.scoring import PRDScorer
            assert PRDScorer is not None
        except ImportError:
            # Expected until PLAN-010 Phase 7 is implemented
            pytest.skip("PLAN-010 Phase 7 not implemented yet - scoring module not available")

    def test_validator_module_graceful_import(self):
        """Verify validator module import is handled gracefully."""
        try:
            from ucx.validators.prd import UnifiedPRDValidator
            assert UnifiedPRDValidator is not None
        except ImportError:
            # Expected until PLAN-010 is implemented
            pytest.skip("PLAN-010 not implemented yet - PRD validator not available")
