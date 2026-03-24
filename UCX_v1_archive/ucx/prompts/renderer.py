"""Jinja2 prompt renderer for UCX templates.

Renders prompt templates with context variables and skill injection.
"""

from pathlib import Path
from typing import Any, Optional, Union

from jinja2 import Environment, BaseLoader, TemplateError

from ucx.prompts.schema import (
    BasePromptContext,
    UCCContext,
    UCRContext,
    UCRemContext,
    PromptResult,
)
from ucx.observability.logging import get_logger

logger = get_logger(__name__)


class StringLoader(BaseLoader):
    """Jinja2 loader for string templates."""

    def get_source(
        self, environment: Environment, template: str
    ) -> tuple[str, Optional[str], Any]:
        return template, None, lambda: True


class PromptRenderer:
    """
    Renders Jinja2 templates with UCX context.

    Supports:
    - Variable substitution
    - Skill content injection
    - Content truncation for token limits
    - Template includes
    """

    def __init__(self) -> None:
        """Initialize the renderer."""
        self._env = Environment(
            loader=StringLoader(),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Add custom filters
        self._env.filters["indent"] = self._indent
        self._env.filters["truncate_smart"] = self._truncate_smart
        self._env.filters["count_tokens"] = self._estimate_tokens
        self._env.filters["format_list"] = self._format_list
        self._env.filters["format_findings"] = self._format_findings

        # Add custom globals
        self._env.globals["now"] = self._now

    def render(
        self,
        template: str,
        context: Union[dict[str, Any], BasePromptContext],
        max_tokens: Optional[int] = None,
    ) -> PromptResult:
        """
        Render a template with context.

        Args:
            template: Jinja2 template string
            context: Context variables (dict or Pydantic model)
            max_tokens: Optional maximum token limit for output

        Returns:
            PromptResult with rendered prompt and metadata
        """
        # Convert Pydantic model to dict if needed
        if isinstance(context, BasePromptContext):
            context_dict = context.model_dump()
        else:
            context_dict = context

        try:
            # Render template
            jinja_template = self._env.from_string(template)
            rendered = jinja_template.render(**context_dict)

            # Estimate tokens
            tokens = self._estimate_tokens(rendered)

            # Truncate if needed
            if max_tokens and tokens > max_tokens:
                rendered = self._truncate_to_tokens(rendered, max_tokens)
                tokens = self._estimate_tokens(rendered)

            logger.debug(
                "Template rendered",
                tokens=tokens,
                doc_type=context_dict.get("doc_type"),
            )

            return PromptResult(
                prompt=rendered,
                context=context_dict,
                template_name=context_dict.get("doc_type", "unknown"),
                tokens_estimated=tokens,
            )

        except TemplateError as e:
            logger.error("Template rendering failed", error=str(e))
            raise

    def render_with_skills(
        self,
        template: str,
        context: Union[dict[str, Any], BasePromptContext],
        skills: dict[str, str],
        max_tokens: Optional[int] = None,
    ) -> PromptResult:
        """
        Render a template with skill content injected.

        Args:
            template: Jinja2 template string
            context: Context variables
            skills: Dict of skill name -> skill content
            max_tokens: Optional maximum token limit

        Returns:
            PromptResult with rendered prompt
        """
        # Inject skill content into context
        if isinstance(context, BasePromptContext):
            context.skill_content = skills
            context_dict = context.model_dump()
        else:
            context_dict = {**context, "skill_content": skills}

        return self.render(template, context_dict, max_tokens)

    def validate_template(self, template: str) -> tuple[bool, Optional[str]]:
        """
        Validate a template for syntax errors.

        Args:
            template: Template string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self._env.from_string(template)
            return True, None
        except TemplateError as e:
            return False, str(e)

    def get_template_variables(self, template: str) -> set[str]:
        """
        Extract variable names from a template.

        Args:
            template: Template string

        Returns:
            Set of variable names used in template
        """
        from jinja2 import meta

        ast = self._env.parse(template)
        return meta.find_undeclared_variables(ast)

    # Custom filters

    @staticmethod
    def _indent(text: str, width: int = 4, first: bool = False) -> str:
        """Indent text by specified width."""
        indent = " " * width
        lines = text.split("\n")
        if first:
            return "\n".join(indent + line for line in lines)
        return lines[0] + "\n" + "\n".join(indent + line for line in lines[1:])

    @staticmethod
    def _truncate_smart(text: str, max_length: int = 5000) -> str:
        """Truncate text at sensible boundary."""
        if len(text) <= max_length:
            return text

        truncated = text[:max_length]

        # Try paragraph boundary
        last_para = truncated.rfind("\n\n")
        if last_para > max_length * 0.7:
            return truncated[:last_para] + "\n\n[Content truncated...]"

        # Try sentence boundary
        last_sentence = truncated.rfind(". ")
        if last_sentence > max_length * 0.7:
            return truncated[:last_sentence + 1] + "\n\n[Content truncated...]"

        return truncated + "...[truncated]"

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Simple estimation: ~4 characters per token for English
        return len(text) // 4

    @staticmethod
    def _format_list(items: list[str], style: str = "bullet") -> str:
        """Format a list of items."""
        if not items:
            return ""

        if style == "numbered":
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
        else:  # bullet
            return "\n".join(f"- {item}" for item in items)

    @staticmethod
    def _format_findings(findings: list[str], priority: str = "P1") -> str:
        """Format findings with priority prefix."""
        if not findings:
            return f"No {priority} findings."

        return "\n".join(f"- {priority}-{i+1}: {f}" for i, f in enumerate(findings))

    @staticmethod
    def _now() -> str:
        """Return current ISO timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to approximately max_tokens."""
        # Rough conversion: 4 chars per token
        max_chars = max_tokens * 4
        return self._truncate_smart(text, max_chars)
