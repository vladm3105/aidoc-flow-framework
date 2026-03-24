"""MCP Resource providers for UCX Framework.

Defines all MCP resources exposed by the UCX server.
"""

from pathlib import Path
from typing import Any, Optional

from ucx.observability.logging import get_logger
from ucx.version import __version__

logger = get_logger(__name__)


class UCXResources:
    """
    MCP Resource definitions for UCX.

    Provides resource registration methods for FastMCP.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize resources with config.

        Args:
            config: UCX configuration
        """
        self._config = config

    def register(self, mcp: Any) -> None:
        """
        Register all resources with MCP server.

        Args:
            mcp: FastMCP instance
        """
        self._register_config(mcp)
        self._register_doc_types(mcp)
        self._register_health(mcp)
        self._register_version(mcp)
        self._register_skills(mcp)
        self._register_templates(mcp)
        self._register_validators(mcp)

        logger.debug("All MCP resources registered", resource_count=7)

    def _register_config(self, mcp: Any) -> None:
        """Register config resource."""

        @mcp.resource("ucx://config")
        def get_config() -> str:
            """Get current UCX configuration."""
            import yaml

            return yaml.dump(self._config.model_dump(), default_flow_style=False)

    def _register_doc_types(self, mcp: Any) -> None:
        """Register doc types resource."""

        @mcp.resource("ucx://doc-types")
        def get_doc_types() -> str:
            """Get supported document types."""
            from ucx.models.enums import DocType

            lines = []
            for dt in DocType:
                lines.append(f"{dt.value}: {dt.display_name} (Layer {dt.layer})")
            return "\n".join(lines)

    def _register_health(self, mcp: Any) -> None:
        """Register health resource."""

        @mcp.resource("ucx://health")
        def get_health() -> str:
            """Get server health status."""
            import json

            status = {
                "status": "healthy",
                "version": __version__,
                "config_loaded": self._config is not None,
            }
            return json.dumps(status, indent=2)

    def _register_version(self, mcp: Any) -> None:
        """Register version resource."""

        @mcp.resource("ucx://version")
        def get_version() -> str:
            """Get UCX version."""
            return f"UCX Framework v{__version__}"

    def _register_skills(self, mcp: Any) -> None:
        """Register skills resource."""

        @mcp.resource("ucx://skills")
        def get_skills() -> str:
            """Get available UCX skills/personas."""
            from ucx.skills.loader import SkillLoader

            loader = SkillLoader()
            skills = loader.list_skills()
            return "\n".join(f"- {skill}" for skill in skills)

        @mcp.resource("ucx://skills/{skill_name}")
        def get_skill(skill_name: str) -> str:
            """Get a specific skill/persona definition."""
            from ucx.skills.loader import SkillLoader

            loader = SkillLoader()
            try:
                return loader.load(skill_name)
            except FileNotFoundError:
                return f"Skill not found: {skill_name}"

    def _register_templates(self, mcp: Any) -> None:
        """Register templates resource."""

        @mcp.resource("ucx://templates")
        def get_templates() -> str:
            """Get available prompt templates."""
            from ucx.prompts.loader import PromptLoader

            loader = PromptLoader()
            templates = loader.list_templates()

            lines = []
            for phase, doc_types in templates.items():
                lines.append(f"{phase}:")
                for dt in doc_types:
                    lines.append(f"  - {dt}")
            return "\n".join(lines)

        @mcp.resource("ucx://templates/{phase}/{doc_type}")
        def get_template(phase: str, doc_type: str) -> str:
            """Get a specific prompt template."""
            from ucx.prompts.loader import PromptLoader

            loader = PromptLoader()
            try:
                return loader.load(phase, doc_type)
            except FileNotFoundError:
                return f"Template not found: {phase}/{doc_type}"

    def _register_validators(self, mcp: Any) -> None:
        """Register validators resource."""

        @mcp.resource("ucx://validators")
        def get_validators() -> str:
            """Get available document validators."""
            from ucx.validators.registry import VALIDATOR_REGISTRY

            lines = []
            for doc_type, validator_class in VALIDATOR_REGISTRY.items():
                lines.append(f"{doc_type.value}: {validator_class.__name__}")
            return "\n".join(lines)

        @mcp.resource("ucx://validators/{doc_type}/rules")
        def get_validator_rules(doc_type: str) -> str:
            """Get validation rules for a document type."""
            from ucx.models.enums import DocType
            from ucx.validators.registry import get_validator

            try:
                dtype = DocType.from_string(doc_type)
                validator = get_validator(dtype)
                rules = validator.get_rules()

                lines = [f"Validation rules for {doc_type.upper()}:", ""]
                for rule in rules:
                    lines.append(f"- [{rule.severity}] {rule.rule_id}: {rule.description}")
                return "\n".join(lines)
            except (ValueError, KeyError):
                return f"Unknown document type: {doc_type}"
