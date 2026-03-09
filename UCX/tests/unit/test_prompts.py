"""Unit tests for prompts module."""

import pytest
from pathlib import Path

from ucx.prompts.schema import UCCContext, UCRContext, UCRemContext
from ucx.prompts.loader import PromptLoader
from ucx.prompts.renderer import PromptRenderer


class TestUCCContext:
    """Tests for UCC context schema."""

    def test_ucc_context_creation(self):
        """Test creating a UCC context."""
        context = UCCContext(
            doc_type="brd",
            doc_id="BRD-01",
            target_path="/path/to/doc.md",
            model="claude-3-opus",
        )
        assert context.doc_type == "brd"
        assert context.doc_id == "BRD-01"

    def test_ucc_context_with_upstream(self):
        """Test UCC context with upstream content."""
        context = UCCContext(
            doc_type="prd",
            doc_id="PRD-01",
            target_path="/path/to/doc.md",
            model="claude-3-opus",
            upstream_content="Upstream document content",
        )
        assert context.upstream_content is not None

    def test_ucc_context_model_dump(self):
        """Test UCC context serialization."""
        context = UCCContext(
            doc_type="brd",
            doc_id="BRD-01",
            target_path="/path/to/doc.md",
            model="claude-3-opus",
        )
        data = context.model_dump()
        assert "doc_type" in data
        assert data["doc_type"] == "brd"


class TestUCRContext:
    """Tests for UCR context schema."""

    def test_ucr_context_creation(self):
        """Test creating a UCR context."""
        context = UCRContext(
            doc_type="brd",
            doc_id="BRD-01",
            document_content="# BRD Document",
            document_path="/path/to/doc.md",
            min_score=85,
            model="claude-3-opus",
        )
        assert context.doc_type == "brd"
        assert context.min_score == 85

    def test_ucr_context_with_validation(self):
        """Test UCR context with validation results."""
        context = UCRContext(
            doc_type="prd",
            doc_id="PRD-01",
            document_content="# PRD Document",
            document_path="/path/to/doc.md",
            min_score=85,
            model="claude-3-opus",
            validation_errors=["Missing section"],
            validation_warnings=["Format issue"],
        )
        assert len(context.validation_errors) == 1
        assert len(context.validation_warnings) == 1


class TestUCRemContext:
    """Tests for UCRem context schema."""

    def test_ucrem_context_creation(self):
        """Test creating a UCRem context."""
        context = UCRemContext(
            doc_type="brd",
            document_content="# BRD Document",
            document_path="/path/to/doc.md",
            review_report="Review report content",
            review_score=75,
            iteration=1,
            max_iterations=3,
            model="claude-3-opus",
        )
        assert context.doc_type == "brd"
        assert context.review_score == 75
        assert context.iteration == 1

    def test_ucrem_context_with_findings(self):
        """Test UCRem context with findings."""
        context = UCRemContext(
            doc_type="prd",
            document_content="# PRD Document",
            document_path="/path/to/doc.md",
            review_report="Review report",
            review_score=60,
            iteration=2,
            max_iterations=3,
            model="claude-3-opus",
            findings_p0=["Critical issue"],
            findings_p1=["Major issue 1", "Major issue 2"],
            findings_p2=["Minor issue"],
        )
        assert len(context.findings_p0) == 1
        assert len(context.findings_p1) == 2


class TestPromptLoader:
    """Tests for prompt loader."""

    def test_loader_initialization(self, tmp_path: Path):
        """Test prompt loader initialization."""
        loader = PromptLoader(tmp_path)
        assert loader is not None

    def test_loader_load_nonexistent(self, tmp_path: Path):
        """Test loading nonexistent template."""
        loader = PromptLoader(tmp_path)
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent", "brd")


class TestPromptRenderer:
    """Tests for prompt renderer."""

    def test_renderer_initialization(self):
        """Test prompt renderer initialization."""
        renderer = PromptRenderer()
        assert renderer is not None

    def test_render_simple_template(self):
        """Test rendering a simple template."""
        renderer = PromptRenderer()
        template = "Hello {{ name }}!"
        result = renderer.render(template, {"name": "World"})
        assert result.prompt == "Hello World!"

    def test_render_with_missing_variable(self):
        """Test rendering with missing variable."""
        renderer = PromptRenderer()
        template = "Hello {{ name }}!"
        # Should not raise, undefined becomes empty
        result = renderer.render(template, {})
        assert "Hello" in result.prompt
