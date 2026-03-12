"""UCX Remediation (UCRem) Phase API."""

from pathlib import Path
from typing import Optional, Union
import re

from ucx.config.settings import UCXConfig
from ucx.config.layer_skills import FIXER_SKILLS
from ucx.models.enums import DocType, Confidence
from ucx.models.fix import FixProposal
from ucx.exceptions import PromptError


class UCRemPhase:
    """
    UCRem (Unified Context Remediation) phase.

    Multi-persona fix proposal generation with confidence levels.

    Example:
        >>> from ucx import UCRemPhase
        >>>
        >>> ucrem = UCRemPhase()
        >>> fixes = ucrem.generate_fixes(
        ...     review_report="docs/BRD-01.UCR_review_report_v001.md",
        ...     doc_path="docs/01_BRD/BRD-01"
        ... )
        >>> for fix in fixes:
        ...     if fix.confidence == Confidence.AUTO_SAFE:
        ...         fix.apply()
    """

    def __init__(self, config: Optional[UCXConfig] = None):
        """
        Initialize UCRem phase.

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

    def generate_fixes(
        self,
        review_report: Union[str, Path],
        doc_path: Union[str, Path],
        *,
        output_path: Optional[Path] = None,
    ) -> tuple[list[FixProposal], Path]:
        """
        Generate fix proposals from review report.

        Args:
            review_report: Path to UCR review report
            doc_path: Path to original document
            output_path: Custom output path for fix report

        Returns:
            Tuple of (list of FixProposal instances, output path where report was written)

        Raises:
            FileNotFoundError: If inputs not found
            PromptError: If prompt not found
        """
        review_report = Path(review_report)
        doc_path = Path(doc_path)

        if not review_report.exists():
            raise FileNotFoundError(f"Review report not found: {review_report}")
        if not doc_path.exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")

        # Detect document type from report name
        doc_type = self._detect_doc_type(review_report)

        # Set default output path - write to document folder, not review report folder
        if output_path is None:
            # Extract doc_id from doc_path (e.g., BRD-01 from BRD-01_platform_architecture)
            doc_id = self._extract_doc_id(doc_path, doc_type)
            if doc_path.is_dir():
                output_path = doc_path / f"{doc_id}.UCRem_report.md"
            else:
                output_path = doc_path.parent / f"{doc_id}.UCRem_report.md"

        # Build prompt
        prompt = self._build_remediation_prompt(doc_type, review_report, doc_path)

        # Generate fixes
        fix_content = self.ai_client.generate(prompt)

        # Write fix report
        output_path.write_text(fix_content, encoding="utf-8")

        # Parse fix proposals and return with output path
        fixes = self._parse_fixes(fix_content, doc_path)
        return fixes, output_path

    def apply_fix(
        self,
        fix: FixProposal,
        *,
        dry_run: bool = False,
    ) -> bool:
        """
        Apply a single fix.

        Args:
            fix: FixProposal to apply
            dry_run: Show what would be done without applying

        Returns:
            True if fix was applied successfully
        """
        return fix.apply(dry_run=dry_run)

    def apply_auto_safe(
        self,
        fixes: list[FixProposal],
        *,
        dry_run: bool = False,
    ) -> list[FixProposal]:
        """
        Apply all auto-safe fixes.

        Args:
            fixes: List of fix proposals
            dry_run: Show what would be done without applying

        Returns:
            List of successfully applied fixes
        """
        applied = []
        for fix in fixes:
            if fix.confidence == Confidence.AUTO_SAFE:
                if fix.apply(dry_run=dry_run):
                    applied.append(fix)
        return applied

    def _detect_doc_type(self, report_path: Path) -> DocType:
        """Detect document type from report filename."""
        name = report_path.stem.upper()

        type_patterns = [
            (r"BRD", DocType.BRD),
            (r"PRD", DocType.PRD),
            (r"EARS", DocType.EARS),
            (r"BDD", DocType.BDD),
            (r"ADR", DocType.ADR),
            (r"SYS", DocType.SYS),
            (r"REQ", DocType.REQ),
            (r"CTR", DocType.CTR),
            (r"TSPEC", DocType.TSPEC),  # Check TSPEC before SPEC
            (r"SPEC", DocType.SPEC),
        ]

        for pattern, doc_type in type_patterns:
            if re.search(pattern, name):
                return doc_type

        return DocType.BRD  # Default

    def _extract_doc_id(self, doc_path: Path, doc_type: DocType) -> str:
        """Extract document ID from path.

        Examples:
            BRD-01_platform_architecture -> BRD-01
            PRD-02.md -> PRD-02
            docs/01_BRD/BRD-01/ -> BRD-01
        """
        # Get the relevant name (directory name or file stem)
        name = doc_path.name if doc_path.is_dir() else doc_path.stem

        # Try to extract doc_id pattern (e.g., BRD-01, PRD-02)
        doc_type_upper = doc_type.value.upper()
        pattern = rf"({doc_type_upper}-\d+)"
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        # Fallback: use directory/file name up to first underscore
        if "_" in name:
            return name.split("_")[0].upper()

        return name.upper()

    def _build_remediation_prompt(
        self,
        doc_type: DocType,
        review_report: Path,
        doc_path: Path,
    ) -> str:
        """Build complete remediation prompt."""
        parts = []

        # Load base prompt
        base_prompt = self._load_prompt(doc_type)
        parts.append(base_prompt)

        # Add fixer skills
        if self.config.load_skills:
            skills_content = self._load_fixer_skills()
            if skills_content:
                parts.append("\n---\n\n## FIXER PERSONA SKILL DEFINITIONS\n\n")
                parts.append(skills_content)

        # Add UCR report
        parts.append("\n---\n\n# UCR REVIEW REPORT\n\n")
        parts.append(review_report.read_text(encoding="utf-8"))

        # Add document content
        parts.append("\n---\n\n# ORIGINAL DOCUMENT CONTENT\n\n")
        parts.append(self._load_document_content(doc_path))

        return "".join(parts)

    def _load_prompt(self, doc_type: DocType) -> str:
        """Load UCRem prompt for document type.

        Search order:
        1. Project-specific: {project_dir}/docs/UCX/remediation/UCRem_PROMPT_{TYPE}_PROJECT.md
        2. Project BEELOCAL: {project_dir}/docs/UCX/remediation/UCRem_PROMPT_{TYPE}_BEELOCAL.md
        3. Framework: {prompt_dir}/ucrem/UCRem_PROMPT_{TYPE}.md
        """
        candidates = []
        doc_type_upper = doc_type.value.upper()

        # Check project-specific prompts first
        project_dir = self.config.get_project_dir()
        if project_dir:
            remediation_dir = project_dir / "docs" / "UCX" / "remediation"
            candidates.extend([
                remediation_dir / f"UCRem_PROMPT_{doc_type_upper}_PROJECT.md",
                remediation_dir / f"UCRem_PROMPT_{doc_type_upper}_BEELOCAL.md",
                remediation_dir / f"UCRem_PROMPT_{doc_type_upper}.md",
            ])

        # Framework prompts as fallback
        prompt_dir = self.config.get_prompt_dir() / "ucrem"
        candidates.extend([
            prompt_dir / f"UCRem_PROMPT_{doc_type_upper}_PROJECT.md",
            prompt_dir / f"UCRem_PROMPT_{doc_type_upper}.md",
        ])

        for path in candidates:
            if path.exists():
                return path.read_text(encoding="utf-8")

        # Build helpful error message
        searched_paths = "\n  - ".join(str(p) for p in candidates)
        raise PromptError(
            f"No UCRem prompt found for {doc_type.value}\n\nSearched:\n  - {searched_paths}",
            prompt_name=f"UCRem_PROMPT_{doc_type_upper}.md",
        )

    def _load_fixer_skills(self) -> str:
        """Load fixer persona skills.

        Checks project-specific skills first, then framework skills.
        """
        parts = []

        fixer_names = {
            "architect": "Architect Fixer",
            "auditor": "Auditor Fixer",
            "qa_lead": "QA Fixer",
            "integration_lead": "Integration Fixer",
            "devils_advocate": "Devil's Advocate",
        }

        # Skill directories to check (project-specific first)
        skill_dirs = []
        project_dir = self.config.get_project_dir()
        if project_dir:
            skill_dirs.append(project_dir / "docs" / "UCX" / "skills")
        skill_dirs.append(self.config.get_skill_dir())

        for skill in FIXER_SKILLS:
            # Find skill in first available directory
            for skill_dir in skill_dirs:
                skill_path = skill_dir / f"{skill}.md"
                if skill_path.exists():
                    title = fixer_names.get(skill, skill.replace("_", " ").title())
                    parts.append(f"### Skill: {title}\n\n")
                    parts.append(skill_path.read_text(encoding="utf-8"))
                    parts.append("\n\n")
                    break  # Found, move to next skill

        return "".join(parts)

    def _load_document_content(self, doc_path: Path) -> str:
        """Load document content."""
        parts = []

        if doc_path.is_dir():
            for f in sorted(doc_path.glob("*.md")):
                if "REVIEW" not in f.name and "REPORT" not in f.name:
                    parts.append(f"## File: {f.name}\n\n")
                    parts.append(f.read_text(encoding="utf-8"))
                    parts.append("\n\n")
        else:
            parts.append(f"## File: {doc_path.name}\n\n")
            parts.append(doc_path.read_text(encoding="utf-8"))
            parts.append("\n\n")

        return "".join(parts)

    def _parse_fixes(self, content: str, doc_path: Path) -> list[FixProposal]:
        """
        Parse fix proposals from UCRem output.

        Looks for YAML blocks with fix_id, confidence, etc.
        """
        fixes = []

        # Find YAML blocks
        yaml_pattern = r"```yaml\s*(fix_id:.*?)```"
        matches = re.findall(yaml_pattern, content, re.DOTALL)

        for yaml_str in matches:
            try:
                fix = FixProposal.from_yaml(yaml_str)
                # Resolve relative target paths
                if not fix.target_file.is_absolute():
                    if doc_path.is_dir():
                        fix.target_file = doc_path / fix.target_file
                    else:
                        fix.target_file = doc_path.parent / fix.target_file
                fixes.append(fix)
            except Exception:
                # Skip malformed YAML blocks
                continue

        return fixes
