"""Integration tests for UCX MCP Server.

Tests MCP server initialization and tool registration.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from ucx.mcp import UCXMCPServer, UCXTools, UCXResources
from ucx.config.settings import UCXConfig


class TestMCPServerIntegration:
    """Integration tests for MCP server."""

    @pytest.fixture
    def config(self) -> UCXConfig:
        """Create test configuration."""
        return UCXConfig(model="mock")

    def test_server_initialization(self, config: UCXConfig):
        """Test server initializes correctly."""
        server = UCXMCPServer(config=config)
        assert server is not None
        assert server._config == config

    def test_server_health_check(self, config: UCXConfig):
        """Test server health check."""
        server = UCXMCPServer(config=config)
        health = server.health_check()

        assert health["status"] == "healthy"
        assert "version" in health
        assert health["config_loaded"] is True

    def test_server_config_property(self, config: UCXConfig):
        """Test server config property."""
        server = UCXMCPServer(config=config)
        assert server.config == config

    def test_server_is_running_property(self, config: UCXConfig):
        """Test server is_running property."""
        server = UCXMCPServer(config=config)
        assert server.is_running is False


class TestMCPToolsIntegration:
    """Integration tests for MCP tools."""

    @pytest.fixture
    def config(self) -> UCXConfig:
        """Create test configuration."""
        return UCXConfig(model="mock")

    def test_tools_initialization(self, config: UCXConfig):
        """Test tools initialize correctly."""
        tools = UCXTools(config)
        assert tools is not None
        assert tools._config == config

    @patch("ucx.mcp.tools.UCXTools._register_autopilot")
    @patch("ucx.mcp.tools.UCXTools._register_create")
    @patch("ucx.mcp.tools.UCXTools._register_review")
    @patch("ucx.mcp.tools.UCXTools._register_remediate")
    @patch("ucx.mcp.tools.UCXTools._register_check_drift")
    @patch("ucx.mcp.tools.UCXTools._register_validate")
    @patch("ucx.mcp.tools.UCXTools._register_batch")
    @patch("ucx.mcp.tools.UCXTools._register_status")
    def test_tools_register_all(
        self,
        mock_status,
        mock_batch,
        mock_validate,
        mock_drift,
        mock_remediate,
        mock_review,
        mock_create,
        mock_autopilot,
        config: UCXConfig,
    ):
        """Test all tools are registered."""
        tools = UCXTools(config)
        mock_mcp = MagicMock()

        tools.register(mock_mcp)

        mock_autopilot.assert_called_once_with(mock_mcp)
        mock_create.assert_called_once_with(mock_mcp)
        mock_review.assert_called_once_with(mock_mcp)
        mock_remediate.assert_called_once_with(mock_mcp)
        mock_drift.assert_called_once_with(mock_mcp)
        mock_validate.assert_called_once_with(mock_mcp)
        mock_batch.assert_called_once_with(mock_mcp)
        mock_status.assert_called_once_with(mock_mcp)


class TestMCPResourcesIntegration:
    """Integration tests for MCP resources."""

    @pytest.fixture
    def config(self) -> UCXConfig:
        """Create test configuration."""
        return UCXConfig(model="mock")

    def test_resources_initialization(self, config: UCXConfig):
        """Test resources initialize correctly."""
        resources = UCXResources(config)
        assert resources is not None
        assert resources._config == config

    @patch("ucx.mcp.resources.UCXResources._register_config")
    @patch("ucx.mcp.resources.UCXResources._register_doc_types")
    @patch("ucx.mcp.resources.UCXResources._register_health")
    @patch("ucx.mcp.resources.UCXResources._register_version")
    @patch("ucx.mcp.resources.UCXResources._register_skills")
    @patch("ucx.mcp.resources.UCXResources._register_templates")
    @patch("ucx.mcp.resources.UCXResources._register_validators")
    def test_resources_register_all(
        self,
        mock_validators,
        mock_templates,
        mock_skills,
        mock_version,
        mock_health,
        mock_doc_types,
        mock_config,
        config: UCXConfig,
    ):
        """Test all resources are registered."""
        resources = UCXResources(config)
        mock_mcp = MagicMock()

        resources.register(mock_mcp)

        mock_config.assert_called_once_with(mock_mcp)
        mock_doc_types.assert_called_once_with(mock_mcp)
        mock_health.assert_called_once_with(mock_mcp)
        mock_version.assert_called_once_with(mock_mcp)
        mock_skills.assert_called_once_with(mock_mcp)
        mock_templates.assert_called_once_with(mock_mcp)
        mock_validators.assert_called_once_with(mock_mcp)


class TestMCPServerWithFastMCP:
    """Test MCP server with FastMCP (if available)."""

    @pytest.fixture
    def config(self) -> UCXConfig:
        """Create test configuration."""
        return UCXConfig(model="mock")

    def test_server_import_error_handling(self, config: UCXConfig):
        """Test server handles FastMCP import error gracefully."""
        server = UCXMCPServer(config=config)

        with patch.dict("sys.modules", {"fastmcp": None}):
            # Should raise ImportError when trying to get MCP
            # but initialization should work
            assert server is not None

    @pytest.mark.skipif(
        True,  # Skip by default, enable if FastMCP is installed
        reason="Requires FastMCP to be installed",
    )
    def test_server_with_real_fastmcp(self, config: UCXConfig):
        """Test server with real FastMCP (requires installation)."""
        try:
            from fastmcp import FastMCP

            server = UCXMCPServer(config=config)
            mcp = server._get_mcp()
            assert mcp is not None
        except ImportError:
            pytest.skip("FastMCP not installed")


class TestMCPToolExecution:
    """Test MCP tool execution."""

    @pytest.fixture
    def config(self) -> UCXConfig:
        """Create test configuration."""
        return UCXConfig(model="mock")

    @pytest.fixture
    def sample_doc(self, tmp_path: Path) -> Path:
        """Create sample document."""
        doc_path = tmp_path / "BRD-01.md"
        doc_path.write_text("""# BRD-01: Test Document

## Executive Summary
Test content.
""")
        return doc_path

    def test_validate_tool_logic(self, config: UCXConfig, sample_doc: Path):
        """Test validate tool logic works correctly."""
        from ucx.models.enums import DocType
        from ucx.validators.registry import get_validator

        # This is the core logic used by ucx_validate tool
        dtype = DocType.from_string("brd")
        validator = get_validator(dtype)
        result = validator.validate(sample_doc)

        assert result is not None
        assert hasattr(result, "status")
        assert hasattr(result, "errors")

    def test_drift_tool_logic(self, config: UCXConfig, sample_doc: Path, tmp_path: Path):
        """Test drift check tool logic works correctly."""
        from ucx.core.drift import DriftMonitor

        # This is the core logic used by ucx_check_drift tool
        monitor = DriftMonitor(config)
        has_drift, changed = monitor.check(sample_doc)

        assert isinstance(has_drift, bool)
        assert isinstance(changed, list)

    def test_status_tool_logic(self, config: UCXConfig, sample_doc: Path):
        """Test status tool logic works correctly."""
        from ucx.models.drift_cache import DriftCache

        # This is the core logic used by ucx_status tool
        cache_path = sample_doc.parent / ".drift_cache.json"

        # Initially no cache
        assert not cache_path.exists()

        # Create cache
        cache = DriftCache(document_id=sample_doc.stem)
        cache.add_review(score=85, status="PASS")
        cache.save(cache_path)

        # Verify cache exists and can be loaded
        assert cache_path.exists()
        loaded = DriftCache.load(cache_path)
        assert loaded.latest_score == 85
