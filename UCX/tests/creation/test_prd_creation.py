"""Tests for PRD creation improvements (PLAN-009)."""

import pytest
from pathlib import Path

from ucx.api.creation import UCCPhase
from ucx.models.enums import DocType
from ucx.models.document import Document
from ucx.models.enums import ValidationStatus
from ucx.models.review import ValidationResult


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


class TestCreationGuardrails:
    """Regression tests for creation-time metadata and identity guardrails."""

    def test_load_prompt_requires_project_specific_file(self, tmp_path, monkeypatch):
        """Ensure creation uses the project prompt only and never merges framework fallback."""
        project_root = tmp_path / "project"
        framework_root = tmp_path / "framework_prompts"

        project_prompt = project_root / "docs" / "UCX" / "creation" / "UCC_PROMPT_PRD_PROJECT.md"
        framework_prompt = framework_root / "ucc" / "UCC_PROMPT_PRD.md"
        project_prompt.parent.mkdir(parents=True, exist_ok=True)
        framework_prompt.parent.mkdir(parents=True, exist_ok=True)

        project_prompt.write_text("PROJECT-ONLY-CONTEXT", encoding="utf-8")
        framework_prompt.write_text("FRAMEWORK-CONTRACT", encoding="utf-8")

        ucc = UCCPhase()
        monkeypatch.setattr(
            ucc.config.__class__,
            "get_project_dir",
            lambda self: project_root,
        )
        monkeypatch.setattr(
            ucc.config.__class__,
            "get_prompt_dir",
            lambda self: framework_root,
        )

        prompt = ucc._load_prompt(DocType.PRD)

        assert prompt == "PROJECT-ONLY-CONTEXT"

    def test_load_template_requires_project_specific_file(self, tmp_path, monkeypatch):
        """Ensure creation loads templates from docs/UCX/templates only."""
        project_root = tmp_path / "project"
        framework_root = tmp_path / "framework_templates"

        project_template = project_root / "docs" / "UCX" / "templates" / "PRD-MVP-TEMPLATE.md"
        framework_template = framework_root / "PRD-MVP-TEMPLATE.md"
        project_template.parent.mkdir(parents=True, exist_ok=True)
        framework_template.parent.mkdir(parents=True, exist_ok=True)

        project_template.write_text("PROJECT-TEMPLATE", encoding="utf-8")
        framework_template.write_text("FRAMEWORK-TEMPLATE", encoding="utf-8")

        ucc = UCCPhase()
        monkeypatch.setattr(ucc.config.__class__, "get_project_dir", lambda self: project_root)
        monkeypatch.setattr(ucc.config.__class__, "get_template_dir", lambda self: framework_root)

        template = ucc._load_template(DocType.PRD)

        assert template == "PROJECT-TEMPLATE"

    def test_load_skills_requires_project_specific_files(self, tmp_path, monkeypatch):
        """Ensure creation fails if a required project skill is missing."""
        project_root = tmp_path / "project"
        skills_dir = project_root / "docs" / "UCX" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        (skills_dir / "product_owner.md").write_text("po", encoding="utf-8")

        ucc = UCCPhase()
        monkeypatch.setattr(ucc.config.__class__, "get_project_dir", lambda self: project_root)

        with pytest.raises(Exception) as exc_info:
            ucc._load_skills(["product_owner", "qa_lead"])

        assert "qa_lead" in str(exc_info.value)

    def test_prd_output_guardrails_enforce_identity_and_frontmatter(self):
        """Ensure generated PRD output is normalized to required metadata and doc ID."""
        ucc = UCCPhase()
        output_path = Path("docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md")

        raw = """---
title: \"PRD-76: Sample\"
status: draft
tags:
  - prd
custom_fields:
  document_type: prd-document
---

# PRD-76: Sample

| Document ID | PRD-76 |

- PRD.76.08.01: Example requirement
"""

        fixed = ucc._apply_prd_output_guardrails(raw, output_path)

        assert fixed.startswith("---\n")
        assert "doc_id: PRD-01" in fixed
        assert "version: 1.0.0" in fixed
        assert "status: Draft" in fixed
        assert "document_type: prd" in fixed
        assert "artifact_type: PRD" in fixed
        assert "layer: 2" in fixed
        assert "# PRD-01: Sample" in fixed
        assert "| Document ID | PRD-01 |" in fixed
        assert "PRD.01.08.01" in fixed

    def test_prd_output_guardrails_inject_section_8_note(self):
        """Ensure Section 8 gets the exact validator-compatible layer note when omitted."""
        ucc = UCCPhase()
        output_path = Path("docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md")

        raw = """---
title: \"PRD-01: Sample\"
doc_id: PRD-01
version: \"1.0.0\"
status: Draft
tags:
  - prd
  - layer-2-artifact
custom_fields:
  document_type: prd
  artifact_type: PRD
  layer: 2
---

# PRD-01: Sample

## 8. User Stories & User Roles
#### PRD.01.09.01: Sender initiates quote
"""

        fixed = ucc._apply_prd_output_guardrails(raw, output_path)

        assert "> **Layer Separation Note**: This section provides role definitions and story summaries." in fixed

    def test_output_contract_contains_target_id(self):
        """Ensure output contract binds generated content to target document ID."""
        ucc = UCCPhase()
        output_path = Path("docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md")

        contract = ucc._build_output_contract(DocType.PRD, output_path)

        assert "Target document ID: `PRD-01`" in contract
        assert "Frontmatter `doc_id` MUST equal `PRD-01`" in contract
        assert "All PRD element IDs MUST use `PRD.01.TT.SS`" in contract

    def test_save_prompt_uses_canonical_parent_folder(self, tmp_path):
        """Canonical slug path should save session prompt beside the file, not nested."""
        ucc = UCCPhase()
        output_path = (
            tmp_path
            / "docs"
            / "02_PRD"
            / "PRD-01_platform_architecture"
            / "PRD-01_platform_architecture.md"
        )

        saved = ucc._save_prompt_to_session(
            prompt="test",
            doc_type=DocType.PRD,
            output_path=output_path,
            from_upstream=None,
            from_ref=None,
            from_iplan=None,
        )

        assert saved.parent == output_path.parent / ".ucx_create_session"
        assert "/PRD-01_platform_architecture/PRD-01_platform_architecture/.ucx_create_session/" not in str(saved)

    def test_save_prompt_plain_slug_path_creates_slug_folder(self, tmp_path):
        """Plain slug filename should keep legacy behavior: session under parent/stem/.ucx_create_session."""
        ucc = UCCPhase()
        output_path = tmp_path / "docs" / "02_PRD" / "PRD-01_platform_architecture.md"

        saved = ucc._save_prompt_to_session(
            prompt="test",
            doc_type=DocType.PRD,
            output_path=output_path,
            from_upstream=None,
            from_ref=None,
            from_iplan=None,
        )

        expected = tmp_path / "docs" / "02_PRD" / "PRD-01_platform_architecture" / ".ucx_create_session"
        assert saved.parent == expected

    def test_normalize_slug_folder_path_to_canonical_file(self):
        """Slug folder input should resolve to the canonical file path inside that folder."""
        ucc = UCCPhase()
        output_path = Path("docs/02_PRD/PRD-01_platform_architecture")

        normalized = ucc._normalize_output_path(
            DocType.PRD,
            output_path,
            from_upstream=Path("docs/01_BRD/BRD-01_platform_architecture"),
        )

        assert normalized == Path(
            "docs/02_PRD/PRD-01_platform_architecture/PRD-01_platform_architecture.md"
        )

    def test_validate_and_score_prd_uses_ucr_validator_results(self, tmp_path, monkeypatch):
        """Create-time validation should use current UCR validator output and unified scores."""
        import ucx.api.review as review_module

        prd_file = tmp_path / "docs" / "02_PRD" / "PRD-01_platform_architecture" / "PRD-01_platform_architecture.md"
        prd_file.parent.mkdir(parents=True, exist_ok=True)
        prd_file.write_text("# PRD-01: Sample\n", encoding="utf-8")
        document = Document.from_path(prd_file)

        class FakeUnifiedResult:
            sys_ready_score = 91.5
            ears_ready_score = 88.0
            template_profile = "mvp"
            both_passed = True

            def format_report(self, doc_id: str, doc_type: str = "PRD", version: int = 1) -> str:
                return f"report:{doc_id}:{doc_type}:v{version}"

        class FakeValidator:
            unified_result = FakeUnifiedResult()

            def validate(self, doc_path):
                return ValidationResult(
                    status=ValidationStatus.PASSED,
                    errors=[],
                    warnings=[],
                    passes=[],
                )

        class FakeUCRPhase:
            def __init__(self, config):
                self.validator = FakeValidator()

            def validate(self, doc_type, doc_path):
                return self.validator.validate(doc_path)

            def _get_validator(self, doc_type):
                return self.validator

        monkeypatch.setattr(review_module, "UCRPhase", FakeUCRPhase)

        ucc = UCCPhase()
        ucc._validate_and_score_prd(document)

        assert document.metadata["validation_status"] == "passed"
        assert document.metadata["sys_ready_score"] == 91.5
        assert document.metadata["ears_ready_score"] == 88.0
        assert document.metadata["template_profile"] == "mvp"
        assert document.metadata["readiness_status"] == "PASS"
        report_text = prd_file.parent.joinpath("PRD-01.UCX_validation_report_v001.md").read_text(encoding="utf-8")
        assert "report:PRD-01:PRD:v1" in report_text
        assert "title: 'UCX Validation Report: PRD-01'" in report_text

