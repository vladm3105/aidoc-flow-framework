"""UCX Review (UCR) Phase API."""

from pathlib import Path
from typing import Optional, Union

from ucx.config.settings import UCXConfig
from ucx.config.layer_skills import get_skills_for_phase
from ucx.models.enums import DocType, ValidationStatus
from ucx.models.review import ReviewResult, ValidationResult
from ucx.exceptions import PromptError


class UCRPhase:
    """
    UCR (Unified Context Review) phase.

    Multi-persona document validation with integrated schema validation.

    Example:
        >>> from ucx import UCRPhase
        >>>
        >>> ucr = UCRPhase()
        >>> result = ucr.review("brd", "docs/01_BRD/BRD-01")
        >>> print(f"Score: {result.score}, Findings: {result.findings}")
    """

    def __init__(self, config: Optional[UCXConfig] = None):
        """
        Initialize UCR phase.

        Args:
            config: UCXConfig instance
        """
        self.config = config or UCXConfig()
        self._ai_client = None
        self._validators: dict[DocType, "BaseValidator"] = {}

    @property
    def ai_client(self):
        """Get AI client instance."""
        if self._ai_client is None:
            from ucx.ai.claude import ClaudeClient
            self._ai_client = ClaudeClient(model=self.config.model)
        return self._ai_client

    def review(
        self,
        doc_type: Union[str, DocType],
        doc_path: Union[str, Path],
        *,
        output_path: Optional[Path] = None,
        skip_validation: bool = False,
    ) -> ReviewResult:
        """
        Review a document.

        Args:
            doc_type: Document type (brd, prd, ears, etc.)
            doc_path: Path to document file or directory
            output_path: Custom output path for review report
            skip_validation: Skip validation phase

        Returns:
            ReviewResult with score, findings, and report path

        Raises:
            FileNotFoundError: If document not found
            PromptError: If prompt not found
        """
        # Normalize inputs
        if isinstance(doc_type, str):
            doc_type = DocType.from_string(doc_type)
        doc_path = Path(doc_path)

        if not doc_path.exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")

        # Set default output path
        if output_path is None:
            if doc_path.is_dir():
                output_path = doc_path / f"{doc_type.value.upper()}_UCR_REVIEW.md"
            else:
                output_path = doc_path.parent / f"{doc_type.value.upper()}_UCR_REVIEW.md"

        # Phase 1: Validation
        validation_result = ValidationResult(status=ValidationStatus.SKIPPED)
        if not skip_validation and not self.config.skip_validation:
            validation_result = self.validate(doc_type, doc_path)

        # Phase 2: Build prompt
        prompt = self._build_review_prompt(
            doc_type=doc_type,
            doc_path=doc_path,
            validation_result=validation_result,
        )

        # Phase 3: Run AI review
        review_content = self.ai_client.generate(prompt)

        # Write review report
        output_path.write_text(review_content, encoding="utf-8")

        # Parse results
        result = ReviewResult.from_report(output_path, doc_path)
        result.validation_status = validation_result.status

        return result

    def validate(
        self,
        doc_type: Union[str, DocType],
        doc_path: Union[str, Path],
    ) -> ValidationResult:
        """
        Run validation only (no AI review).

        Args:
            doc_type: Document type
            doc_path: Path to document

        Returns:
            ValidationResult with errors and warnings
        """
        if isinstance(doc_type, str):
            doc_type = DocType.from_string(doc_type)
        doc_path = Path(doc_path)

        validator = self._get_validator(doc_type)
        return validator.validate(doc_path)

    def _get_validator(self, doc_type: DocType) -> "BaseValidator":
        """Get or create validator for document type."""
        if doc_type not in self._validators:
            from ucx.validators.registry import get_validator
            self._validators[doc_type] = get_validator(doc_type)
        return self._validators[doc_type]

    def _build_review_prompt(
        self,
        doc_type: DocType,
        doc_path: Path,
        validation_result: ValidationResult,
    ) -> str:
        """Build complete review prompt."""
        parts = []

        # Load base prompt
        base_prompt = self._load_prompt(doc_type)
        parts.append(base_prompt)

        # Add validation results
        if validation_result.status != ValidationStatus.SKIPPED:
            parts.append("\n---\n\n## PRE-VALIDATION RESULTS\n\n")
            parts.append(f"**Status**: {validation_result.status.value}\n\n")

            if validation_result.errors:
                parts.append("**Errors**:\n")
                for error in validation_result.errors:
                    parts.append(f"- {error}\n")
                parts.append("\n")

            if validation_result.warnings:
                parts.append("**Warnings**:\n")
                for warning in validation_result.warnings:
                    parts.append(f"- {warning}\n")
                parts.append("\n")

            parts.append("> **Note**: Address validation failures as P0 findings.\n")

        # Add skills
        if self.config.load_skills:
            skills = get_skills_for_phase(doc_type, "ucr")
            skills_content = self._load_skills(skills)
            if skills_content:
                parts.append("\n---\n\n## PERSONA SKILL DEFINITIONS\n\n")
                parts.append(skills_content)

        # Add document content
        parts.append("\n---\n\n# DOCUMENT CONTENT\n\n")
        parts.append(self._load_document_content(doc_path))

        return "".join(parts)

    def _load_prompt(self, doc_type: DocType) -> str:
        """Load UCR prompt for document type."""
        prompt_dir = self.config.get_prompt_dir() / "ucr"

        candidates = [
            prompt_dir / f"UCR_PROMPT_{doc_type.value.upper()}_PROJECT.md",
            prompt_dir / f"UCR_PROMPT_{doc_type.value.upper()}.md",
        ]

        for path in candidates:
            if path.exists():
                return path.read_text(encoding="utf-8")

        raise PromptError(
            f"No UCR prompt found for {doc_type.value}",
            prompt_name=f"UCR_PROMPT_{doc_type.value.upper()}.md",
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

    def _load_document_content(self, doc_path: Path) -> str:
        """Load document content for review."""
        parts = []

        if doc_path.is_dir():
            for f in sorted(doc_path.glob("*.md")):
                # Exclude review/report files
                if "REVIEW" not in f.name and "REPORT" not in f.name:
                    parts.append(f"## File: {f.name}\n\n")
                    parts.append(f.read_text(encoding="utf-8"))
                    parts.append("\n\n")
        else:
            parts.append(f"## File: {doc_path.name}\n\n")
            parts.append(doc_path.read_text(encoding="utf-8"))
            parts.append("\n\n")

        return "".join(parts)
