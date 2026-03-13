"""UCX Creation (UCC) Phase API."""

from pathlib import Path
from typing import Optional, Union

from ucx.config.settings import UCXConfig
from ucx.config.layer_skills import get_skills_for_phase
from ucx.models.document import Document
from ucx.models.enums import DocType
from ucx.exceptions import UCXError, PromptError
from ucx.validators.common.file_utils import sort_section_files


class UCCPhase:
    """
    UCC (Unified Context Creation) phase.

    Multi-persona document authoring with skill injection.

    Example:
        >>> from ucx import UCCPhase, UCXConfig
        >>>
        >>> ucc = UCCPhase(UCXConfig())
        >>> doc = ucc.create(
        ...     doc_type="brd",
        ...     output_path="docs/01_BRD/BRD-01",
        ...     from_ref="docs/00_REF/"
        ... )
        >>> print(f"Created: {doc.path}")
    """

    def __init__(self, config: Optional[UCXConfig] = None):
        """
        Initialize UCC phase.

        Args:
            config: UCXConfig instance
        """
        self.config = config or UCXConfig()
        self._ai_client = None

    @property
    def ai_client(self):
        """Get AI client instance based on config (CLI or API mode)."""
        if self._ai_client is None:
            self._ai_client = self.config.get_ai_client()
        return self._ai_client

    def create(
        self,
        doc_type: Union[str, DocType],
        output_path: Union[str, Path],
        *,
        from_ref: Optional[Path] = None,
        from_upstream: Optional[Path] = None,
        from_iplan: Optional[Path] = None,
        template: Optional[Path] = None,
        multi_file: bool = False,
    ) -> Document:
        """
        Create a new document.

        Args:
            doc_type: Document type (brd, prd, ears, etc.)
            output_path: Path to output file or directory
            from_ref: Reference documents directory
            from_upstream: Upstream artifact path
            from_iplan: Implementation plan path
            template: Custom template path
            multi_file: Generate multi-file output

        Returns:
            Created Document instance

        Raises:
            UCXError: On creation failure
            PromptError: If prompt not found
        """
        # Normalize inputs
        if isinstance(doc_type, str):
            doc_type = DocType.from_string(doc_type)
        output_path = Path(output_path)

        # Build prompt
        prompt = self.get_prompt(
            doc_type=doc_type,
            include_skills=self.config.load_skills,
            include_template=True,
            template_path=template,
        )

        # Add reference content
        if from_ref:
            prompt += self._load_reference_content(from_ref)

        # Add upstream content
        if from_upstream:
            prompt += self._load_upstream_content(from_upstream)

        # Add IPLAN content
        if from_iplan:
            prompt += self._load_iplan_content(from_iplan)

        # Create output directory if needed
        if multi_file:
            output_path.mkdir(parents=True, exist_ok=True)
            actual_output = output_path / f"{doc_type.value.upper()}_CREATED.md"
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            actual_output = output_path

        # Generate document
        content = self.ai_client.generate(prompt)

        # Write output
        actual_output.write_text(content, encoding="utf-8")

        return Document.from_path(actual_output)

    def get_prompt(
        self,
        doc_type: Union[str, DocType],
        *,
        include_skills: bool = True,
        include_template: bool = True,
        template_path: Optional[Path] = None,
    ) -> str:
        """
        Get assembled prompt without execution.

        Args:
            doc_type: Document type
            include_skills: Include persona skills
            include_template: Include document template

        Returns:
            Assembled prompt string
        """
        if isinstance(doc_type, str):
            doc_type = DocType.from_string(doc_type)

        prompt_parts = []

        # Load base prompt
        base_prompt = self._load_prompt(doc_type)
        prompt_parts.append(base_prompt)

        # Add skills
        if include_skills:
            skills = get_skills_for_phase(doc_type, "ucc")
            skills_content = self._load_skills(skills)
            if skills_content:
                prompt_parts.append("\n---\n\n## AUTHOR PERSONA SKILL DEFINITIONS\n")
                prompt_parts.append(skills_content)

        # Add template
        if include_template:
            template_content = self._load_template(doc_type, template_path)
            if template_content:
                prompt_parts.append("\n---\n\n# DOCUMENT TEMPLATE\n\n")
                prompt_parts.append("Follow this template structure exactly:\n\n")
                prompt_parts.append(template_content)

        return "\n".join(prompt_parts)

    def _load_prompt(self, doc_type: DocType) -> str:
        """Load UCC prompt for document type."""
        prompt_dir = self.config.get_prompt_dir() / "ucc"

        # Try project-specific first
        candidates = [
            prompt_dir / f"UCC_PROMPT_{doc_type.value.upper()}_PROJECT.md",
            prompt_dir / f"UCC_PROMPT_{doc_type.value.upper()}.md",
        ]

        for path in candidates:
            if path.exists():
                return path.read_text(encoding="utf-8")

        raise PromptError(
            f"No UCC prompt found for {doc_type.value}",
            prompt_name=f"UCC_PROMPT_{doc_type.value.upper()}.md",
        )

    def _load_skills(self, skill_names: list[str]) -> str:
        """Load skill content for personas."""
        skill_dir = self.config.get_skill_dir()
        parts = []

        for name in skill_names:
            skill_path = skill_dir / f"{name}.md"
            if skill_path.exists():
                title = name.replace("_", " ").title()
                parts.append(f"### Skill: {title}\n\n")
                parts.append(skill_path.read_text(encoding="utf-8"))
                parts.append("\n\n")

        return "".join(parts)

    def _load_template(
        self,
        doc_type: DocType,
        custom_path: Optional[Path] = None,
    ) -> str:
        """Load document template."""
        if custom_path and custom_path.exists():
            return custom_path.read_text(encoding="utf-8")

        template_dir = self.config.get_template_dir()

        # Try MVP template first
        candidates = [
            template_dir / f"{doc_type.value.upper()}-MVP-TEMPLATE.md",
            template_dir / f"{doc_type.value.upper()}-MVP-TEMPLATE.feature",
            template_dir / f"{doc_type.value.upper()}-TEMPLATE.md",
        ]

        for path in candidates:
            if path.exists():
                return path.read_text(encoding="utf-8")

        return ""

    def _load_reference_content(self, ref_path: Path) -> str:
        """Load reference documents."""
        parts = ["\n---\n\n# REFERENCE DOCUMENTS\n\n"]

        if ref_path.is_dir():
            for f in sorted(ref_path.glob("*")):
                if f.is_file() and f.suffix in (".md", ".txt"):
                    parts.append(f"## Reference: {f.name}\n\n")
                    parts.append(f.read_text(encoding="utf-8"))
                    parts.append("\n\n")
        elif ref_path.is_file():
            parts.append(f"## Reference: {ref_path.name}\n\n")
            parts.append(ref_path.read_text(encoding="utf-8"))
            parts.append("\n\n")

        return "".join(parts)

    def _load_upstream_content(self, upstream_path: Path) -> str:
        """Load upstream artifact content.

        Section files (e.g., BRD-01.0_index.md) are sorted numerically.
        """
        parts = ["\n---\n\n# UPSTREAM ARTIFACT\n\n"]

        if upstream_path.is_dir():
            all_files = list(upstream_path.glob("*.md"))
            for f in sort_section_files(all_files):
                parts.append(f"## File: {f.name}\n\n")
                parts.append(f.read_text(encoding="utf-8"))
                parts.append("\n\n")
        elif upstream_path.is_file():
            parts.append(f"## File: {upstream_path.name}\n\n")
            parts.append(upstream_path.read_text(encoding="utf-8"))
            parts.append("\n\n")

        return "".join(parts)

    def _load_iplan_content(self, iplan_path: Path) -> str:
        """Load implementation plan content."""
        # Resolve IPLAN-NNN pattern
        resolved = self._resolve_iplan(iplan_path)
        if not resolved:
            return ""

        parts = ["\n---\n\n# IMPLEMENTATION PLAN\n\n"]
        parts.append(resolved.read_text(encoding="utf-8"))
        return "".join(parts)

    def _resolve_iplan(self, iplan_input: Path) -> Optional[Path]:
        """Resolve IPLAN path from input."""
        if iplan_input.exists():
            return iplan_input

        # Try IPLAN-NNN pattern
        iplan_name = iplan_input.stem
        search_dirs = [
            Path("work_plans"),
            Path("governance/plans"),
            Path("docs/IPLAN"),
        ]

        for search_dir in search_dirs:
            if search_dir.exists():
                matches = list(search_dir.glob(f"{iplan_name}*.md"))
                if matches:
                    return matches[0]

        return None
