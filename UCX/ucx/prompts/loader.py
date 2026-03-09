"""Prompt template loader for UCX phases.

Loads Jinja2 templates from the templates directory with caching.
"""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ucx.observability.logging import get_logger

logger = get_logger(__name__)


class PromptLoader:
    """
    Loads prompt templates from the file system.

    Templates are organized by phase (ucc, ucr, ucrem) and document type.

    Directory structure:
        templates/
        ├── ucc/
        │   ├── base.md.j2
        │   ├── brd.md.j2
        │   └── ...
        ├── ucr/
        │   ├── base.md.j2
        │   └── review.md.j2
        └── ucrem/
            ├── base.md.j2
            └── fix.md.j2
    """

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        cache_templates: bool = True,
    ) -> None:
        """
        Initialize the prompt loader.

        Args:
            template_dir: Directory containing templates. Defaults to package templates.
            cache_templates: Whether to cache loaded templates.
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"

        self._template_dir = template_dir
        self._cache_templates = cache_templates
        self._env: Optional[Environment] = None
        self._template_cache: dict[str, str] = {}

        logger.debug("PromptLoader initialized", template_dir=str(template_dir))

    @property
    def env(self) -> Environment:
        """Get or create Jinja2 environment."""
        if self._env is None:
            self._env = Environment(
                loader=FileSystemLoader(str(self._template_dir)),
                autoescape=False,  # Templates are markdown, not HTML
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
            )
            # Add custom filters
            self._env.filters["indent_content"] = self._indent_content
            self._env.filters["truncate_smart"] = self._truncate_smart

        return self._env

    def load(
        self,
        phase: str,
        doc_type: str,
        fallback_to_base: bool = True,
    ) -> str:
        """
        Load a prompt template for a phase and document type.

        Args:
            phase: UCX phase (ucc, ucr, ucrem)
            doc_type: Document type (brd, prd, etc.)
            fallback_to_base: Use base template if specific one not found

        Returns:
            Template content

        Raises:
            FileNotFoundError: If template not found and no fallback
        """
        cache_key = f"{phase}/{doc_type}"

        # Check cache
        if self._cache_templates and cache_key in self._template_cache:
            logger.debug("Template cache hit", key=cache_key)
            return self._template_cache[cache_key]

        # Try specific template first
        template_name = f"{phase}/{doc_type}.md.j2"
        try:
            template = self.env.get_template(template_name)
            content = template.module.__loader__.get_source(self.env, template_name)[0]

            if self._cache_templates:
                self._template_cache[cache_key] = content

            logger.debug("Loaded template", template=template_name)
            return content

        except TemplateNotFound:
            if fallback_to_base:
                # Try base template
                base_template_name = f"{phase}/base.md.j2"
                try:
                    template = self.env.get_template(base_template_name)
                    content = template.module.__loader__.get_source(
                        self.env, base_template_name
                    )[0]

                    if self._cache_templates:
                        self._template_cache[cache_key] = content

                    logger.debug(
                        "Loaded base template",
                        template=base_template_name,
                        requested=template_name,
                    )
                    return content

                except TemplateNotFound:
                    pass

            logger.error("Template not found", template=template_name)
            raise FileNotFoundError(f"Template not found: {template_name}")

    def load_raw(self, template_path: str) -> str:
        """
        Load a template by raw path.

        Args:
            template_path: Path relative to template directory

        Returns:
            Template content
        """
        full_path = self._template_dir / template_path
        if not full_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        return full_path.read_text(encoding="utf-8")

    def list_templates(self, phase: Optional[str] = None) -> list[str]:
        """
        List available templates.

        Args:
            phase: Filter by phase (ucc, ucr, ucrem)

        Returns:
            List of template paths
        """
        templates = []

        search_path = self._template_dir
        if phase:
            search_path = search_path / phase

        if search_path.exists():
            for template_file in search_path.rglob("*.md.j2"):
                relative = template_file.relative_to(self._template_dir)
                templates.append(str(relative))

        return sorted(templates)

    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._template_cache.clear()
        logger.debug("Template cache cleared")

    @staticmethod
    def _indent_content(text: str, spaces: int = 4) -> str:
        """Indent content by specified spaces."""
        indent = " " * spaces
        lines = text.split("\n")
        return "\n".join(indent + line if line.strip() else line for line in lines)

    @staticmethod
    def _truncate_smart(text: str, max_length: int = 5000) -> str:
        """Truncate text at a sensible boundary."""
        if len(text) <= max_length:
            return text

        # Try to truncate at paragraph boundary
        truncated = text[:max_length]
        last_para = truncated.rfind("\n\n")
        if last_para > max_length * 0.7:
            return truncated[:last_para] + "\n\n[Content truncated...]"

        # Fall back to sentence boundary
        last_sentence = truncated.rfind(". ")
        if last_sentence > max_length * 0.7:
            return truncated[:last_sentence + 1] + "\n\n[Content truncated...]"

        return truncated + "...[truncated]"
