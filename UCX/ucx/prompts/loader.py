"""Prompt template loader for UCX phases.

Loads prompts from project-specific directories. Framework templates are
ONLY used as references for creating project-specific prompts, never for
actual analysis.

CRITICAL: Project-specific prompts are REQUIRED. If not found, the loader
will raise an error. Framework prompts are NEVER used as fallback.
"""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ucx.observability.logging import get_logger
from ucx.exceptions import ConfigurationError

logger = get_logger(__name__)


class ProjectPromptNotFoundError(ConfigurationError):
    """Raised when project-specific prompt is not found."""

    def __init__(self, phase: str, doc_type: str, project_dir: Path):
        self.phase = phase
        self.doc_type = doc_type
        self.project_dir = project_dir
        super().__init__(
            f"Project-specific prompt not found for {phase}/{doc_type}. "
            f"Expected location: {project_dir}/docs/UCX/{phase}/ "
            f"Framework prompts cannot be used for analysis. "
            f"Create project-specific prompt first using framework template as reference."
        )


class PromptLoader:
    """
    Loads prompt templates from project-specific directories.

    ARCHITECTURE:
    - Project-specific prompts are REQUIRED for all phases
    - Framework prompts are TEMPLATES ONLY, never used for analysis
    - If project prompt not found, raise error (no fallback)

    Project prompt locations:
        {project_root}/docs/UCX/
        ├── review/
        │   ├── UCR_PROMPT_BRD_PROJECT.md   # Project-specific BRD review
        │   ├── UCR_PROMPT_PRD_PROJECT.md   # Project-specific PRD review
        │   └── personas/                    # Project-specific multi-turn personas
        │       ├── architect.md
        │       ├── auditor.md
        │       └── ...
        ├── creation/
        │   └── UCC_PROMPT_BRD_PROJECT.md
        └── remediation/
            └── UCRem_PROMPT_BRD_PROJECT.md

    Framework template locations (reference only):
        {framework}/ucx/prompts/templates/
        ├── ucr/
        │   └── UCR_PROMPT_BRD.md           # Template for creating project prompts
        └── ...
    """

    # Mapping from phase to UCX subdirectory
    PHASE_TO_DIR = {
        "ucc": "creation",
        "ucr": "review",
        "ucrem": "remediation",
    }

    # Mapping from phase to prompt file prefix
    PHASE_TO_PREFIX = {
        "ucc": "UCC_PROMPT",
        "ucr": "UCR_PROMPT",
        "ucrem": "UCRem_PROMPT",
    }

    def __init__(
        self,
        project_dir: Optional[Path] = None,
        framework_template_dir: Optional[Path] = None,
        cache_templates: bool = True,
    ) -> None:
        """
        Initialize the prompt loader.

        Args:
            project_dir: Project root directory containing docs/UCX/
            framework_template_dir: Framework templates (for reference only)
            cache_templates: Whether to cache loaded templates.
        """
        self._project_dir = project_dir
        self._framework_template_dir = framework_template_dir or (
            Path(__file__).parent / "templates"
        )
        self._cache_templates = cache_templates
        self._env: Optional[Environment] = None
        self._template_cache: dict[str, str] = {}

        logger.debug(
            "PromptLoader initialized",
            project_dir=str(project_dir) if project_dir else "None",
            framework_dir=str(self._framework_template_dir),
        )

    def set_project_dir(self, project_dir: Path) -> None:
        """Set or update the project directory."""
        self._project_dir = project_dir
        self._template_cache.clear()  # Clear cache when project changes
        logger.debug("Project directory set", project_dir=str(project_dir))

    def _get_project_prompt_dir(self, phase: str) -> Optional[Path]:
        """Get the project-specific prompt directory for a phase."""
        if self._project_dir is None:
            return None

        phase_dir = self.PHASE_TO_DIR.get(phase, phase)
        return self._project_dir / "docs" / "UCX" / phase_dir

    def _find_project_prompt(self, phase: str, doc_type: str) -> Optional[Path]:
        """
        Find project-specific prompt file.

        Searches for patterns like:
        - UCR_PROMPT_BRD_PROJECT.md
        - UCR_PROMPT_BRD_{PROJECT_NAME}.md
        - UCR_PROMPT_BRD_BEELOCAL.md
        """
        prompt_dir = self._get_project_prompt_dir(phase)
        if prompt_dir is None or not prompt_dir.exists():
            return None

        prefix = self.PHASE_TO_PREFIX.get(phase, f"{phase.upper()}_PROMPT")
        doc_type_upper = doc_type.upper()

        # Search patterns (in priority order)
        patterns = [
            f"{prefix}_{doc_type_upper}_PROJECT.md",
            f"{prefix}_{doc_type_upper}_*.md",  # Any project-specific suffix
        ]

        for pattern in patterns:
            # For exact match
            if "*" not in pattern:
                exact_path = prompt_dir / pattern
                if exact_path.exists():
                    return exact_path
            else:
                # For glob pattern, find non-symlink files (exclude framework symlinks)
                base_pattern = pattern.replace("*", "")
                for file in prompt_dir.glob(pattern):
                    # Skip symlinks to framework and the base framework prompt
                    if file.is_symlink():
                        continue
                    # Skip if it's exactly the framework prompt name
                    if file.name == f"{prefix}_{doc_type_upper}.md":
                        continue
                    return file

        return None

    def load(
        self,
        phase: str,
        doc_type: str,
        allow_framework_fallback: bool = False,
    ) -> str:
        """
        Load a project-specific prompt template.

        Args:
            phase: UCX phase (ucc, ucr, ucrem)
            doc_type: Document type (brd, prd, etc.)
            allow_framework_fallback: DEPRECATED - always False.
                Framework prompts are NEVER used for analysis.

        Returns:
            Template content

        Raises:
            ProjectPromptNotFoundError: If project-specific prompt not found
        """
        if allow_framework_fallback:
            logger.warning(
                "allow_framework_fallback is deprecated and ignored. "
                "Framework prompts are never used for analysis."
            )

        cache_key = f"{phase}/{doc_type}"

        # Check cache
        if self._cache_templates and cache_key in self._template_cache:
            logger.debug("Template cache hit", key=cache_key)
            return self._template_cache[cache_key]

        # Find project-specific prompt
        prompt_path = self._find_project_prompt(phase, doc_type)

        if prompt_path is None:
            if self._project_dir is None:
                raise ConfigurationError(
                    "Project directory not set. Call set_project_dir() or pass "
                    "project_dir to PromptLoader constructor."
                )
            raise ProjectPromptNotFoundError(phase, doc_type, self._project_dir)

        # Load the prompt
        content = prompt_path.read_text(encoding="utf-8")

        if self._cache_templates:
            self._template_cache[cache_key] = content

        logger.info(
            "Loaded project-specific prompt",
            phase=phase,
            doc_type=doc_type,
            path=str(prompt_path),
        )
        return content

    def load_framework_template(self, phase: str, doc_type: str) -> str:
        """
        Load a framework template (for reference/creating project prompts only).

        WARNING: This should ONLY be used when creating new project-specific
        prompts. Never use framework templates for actual analysis.

        Args:
            phase: UCX phase
            doc_type: Document type

        Returns:
            Framework template content
        """
        logger.warning(
            "Loading framework template - for reference only, not for analysis",
            phase=phase,
            doc_type=doc_type,
        )

        template_path = self._framework_template_dir / phase / f"{doc_type}.md.j2"
        if not template_path.exists():
            # Try non-Jinja2 version
            template_path = self._framework_template_dir / phase / f"UCR_PROMPT_{doc_type.upper()}.md"

        if not template_path.exists():
            raise FileNotFoundError(
                f"Framework template not found: {phase}/{doc_type}"
            )

        return template_path.read_text(encoding="utf-8")

    def load_personas(self, phase: str, doc_type: str) -> dict[str, str]:
        """
        Load project-specific persona prompts for multi-turn review.

        Args:
            phase: UCX phase (typically "ucr")
            doc_type: Document type

        Returns:
            Dict mapping persona name to prompt content

        Raises:
            ProjectPromptNotFoundError: If persona directory not found
        """
        prompt_dir = self._get_project_prompt_dir(phase)
        if prompt_dir is None:
            if self._project_dir is None:
                raise ConfigurationError(
                    "Project directory not set for persona loading."
                )
            raise ProjectPromptNotFoundError(phase, doc_type, self._project_dir)

        personas_dir = prompt_dir / "personas"

        if not personas_dir.exists():
            # Try alternative: personas in main prompt file as YAML/sections
            logger.warning(
                "Personas directory not found, checking for embedded personas",
                expected=str(personas_dir),
            )
            raise ProjectPromptNotFoundError(
                phase,
                f"{doc_type}/personas",
                self._project_dir
            )

        personas = {}
        for persona_file in personas_dir.glob("*.md"):
            if persona_file.is_symlink():
                continue  # Skip symlinks to framework
            persona_name = persona_file.stem  # e.g., "architect" from "architect.md"
            personas[persona_name] = persona_file.read_text(encoding="utf-8")
            logger.debug("Loaded persona", persona=persona_name, path=str(persona_file))

        if not personas:
            raise ProjectPromptNotFoundError(
                phase,
                f"{doc_type}/personas (empty)",
                self._project_dir
            )

        logger.info(
            "Loaded project-specific personas",
            phase=phase,
            count=len(personas),
            personas=list(personas.keys()),
        )
        return personas

    def has_project_prompt(self, phase: str, doc_type: str) -> bool:
        """Check if a project-specific prompt exists."""
        return self._find_project_prompt(phase, doc_type) is not None

    def has_project_personas(self, phase: str) -> bool:
        """Check if project-specific personas exist."""
        prompt_dir = self._get_project_prompt_dir(phase)
        if prompt_dir is None:
            return False
        personas_dir = prompt_dir / "personas"
        if not personas_dir.exists():
            return False
        # Check for at least one non-symlink persona file
        for f in personas_dir.glob("*.md"):
            if not f.is_symlink():
                return True
        return False

    def list_project_prompts(self) -> dict[str, list[str]]:
        """List all available project-specific prompts."""
        result = {}
        if self._project_dir is None:
            return result

        for phase, phase_dir in self.PHASE_TO_DIR.items():
            prompt_dir = self._project_dir / "docs" / "UCX" / phase_dir
            if prompt_dir.exists():
                prompts = []
                for f in prompt_dir.glob("*.md"):
                    if not f.is_symlink():
                        prompts.append(f.name)
                if prompts:
                    result[phase] = prompts

        return result

    def load_raw(self, template_path: str) -> str:
        """
        Load a template by raw path (deprecated - use load() instead).
        """
        logger.warning("load_raw is deprecated, use load() instead")
        full_path = self._framework_template_dir / template_path
        if not full_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        return full_path.read_text(encoding="utf-8")

    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._template_cache.clear()
        logger.debug("Template cache cleared")

    # Legacy Jinja2 support (for framework templates only)
    @property
    def env(self) -> Environment:
        """Get or create Jinja2 environment for framework templates."""
        if self._env is None:
            self._env = Environment(
                loader=FileSystemLoader(str(self._framework_template_dir)),
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True,
            )
            self._env.filters["indent_content"] = self._indent_content
            self._env.filters["truncate_smart"] = self._truncate_smart
        return self._env

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
        truncated = text[:max_length]
        last_para = truncated.rfind("\n\n")
        if last_para > max_length * 0.7:
            return truncated[:last_para] + "\n\n[Content truncated...]"
        last_sentence = truncated.rfind(". ")
        if last_sentence > max_length * 0.7:
            return truncated[:last_sentence + 1] + "\n\n[Content truncated...]"
        return truncated + "...[truncated]"
