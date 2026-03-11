"""Skill/persona loader for UCX phases.

Loads skill definitions from markdown files in the skills directory.

Skill loading priority:
1. Project-specific skills ({project_dir}/docs/UCX/skills/)
2. Framework skills (/UCX/skills/)
"""

from pathlib import Path
from typing import Optional

from ucx.observability.logging import get_logger

logger = get_logger(__name__)


# Default skill directory (framework /UCX/skills/)
DEFAULT_SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"


def get_project_skills_dir(project_dir: Path) -> Path:
    """
    Get the project-specific skills directory.

    Args:
        project_dir: Project root directory

    Returns:
        Path to project skills directory ({project_dir}/docs/UCX/skills/)
    """
    return project_dir / "docs" / "UCX" / "skills"


class SkillLoader:
    """
    Loads skill/persona definitions from the file system.

    Skills are markdown files containing persona descriptions, expertise,
    domain knowledge, and behavioral guidelines that are injected into prompts.

    Skill loading priority:
    1. Project-specific skills ({project_dir}/docs/UCX/skills/) - if project_dir provided
    2. Framework skills (/UCX/skills/) - fallback

    Default directory structure (project root):
        /UCX/skills/
        ├── architect.md
        ├── auditor.md
        ├── product_owner.md
        └── ...

    Project-specific structure:
        {project}/docs/UCX/skills/
        ├── architect.md      # Domain-tuned version
        ├── auditor.md        # Domain-tuned version
        └── ...
    """

    def __init__(
        self,
        skill_dir: Optional[Path] = None,
        project_dir: Optional[Path] = None,
        cache_skills: bool = True,
    ) -> None:
        """
        Initialize the skill loader.

        Args:
            skill_dir: Directory containing skill files. Defaults to /UCX/skills/.
            project_dir: Project root for project-specific skills (takes priority).
            cache_skills: Whether to cache loaded skills.
        """
        if skill_dir is None:
            skill_dir = DEFAULT_SKILLS_DIR

        self._skill_dir = skill_dir
        self._project_dir = project_dir
        self._project_skills_dir = get_project_skills_dir(project_dir) if project_dir else None
        self._cache_skills = cache_skills
        self._skill_cache: dict[str, str] = {}

        logger.debug(
            "SkillLoader initialized",
            skill_dir=str(skill_dir),
            project_dir=str(project_dir) if project_dir else None,
            project_skills_dir=str(self._project_skills_dir) if self._project_skills_dir else None,
        )

    def _find_skill_in_dir(self, skill_name: str, skill_dir: Path) -> Optional[Path]:
        """
        Find a skill file in a specific directory.

        Args:
            skill_name: Name of the skill (without extension)
            skill_dir: Directory to search

        Returns:
            Path to skill file or None if not found
        """
        if not skill_dir or not skill_dir.exists():
            return None

        # Try exact match
        skill_path = skill_dir / f"{skill_name}.md"
        if skill_path.exists():
            return skill_path

        # Try with underscores/hyphens normalized
        normalized = skill_name.replace("-", "_").replace(" ", "_").lower()
        skill_path = skill_dir / f"{normalized}.md"
        if skill_path.exists():
            return skill_path

        return None

    def load(self, skill_name: str) -> str:
        """
        Load a single skill by name.

        Priority order:
        1. Project-specific skills (if project_dir was provided)
        2. Framework skills (fallback)

        Args:
            skill_name: Name of the skill (without extension)

        Returns:
            Skill content

        Raises:
            FileNotFoundError: If skill file not found in any location
        """
        # Check cache
        if self._cache_skills and skill_name in self._skill_cache:
            logger.debug("Skill cache hit", skill=skill_name)
            return self._skill_cache[skill_name]

        skill_path = None

        # Priority 1: Project-specific skills
        if self._project_skills_dir:
            skill_path = self._find_skill_in_dir(skill_name, self._project_skills_dir)
            if skill_path:
                logger.info(
                    "Loaded project-specific skill",
                    skill=skill_name,
                    path=str(skill_path),
                )

        # Priority 2: Framework skills (fallback)
        if not skill_path:
            skill_path = self._find_skill_in_dir(skill_name, self._skill_dir)
            if skill_path:
                logger.debug(
                    "Loaded framework skill (fallback)",
                    skill=skill_name,
                    path=str(skill_path),
                )

        if not skill_path:
            logger.error("Skill not found in any location", skill=skill_name)
            raise FileNotFoundError(f"Skill not found: {skill_name}")

        content = skill_path.read_text(encoding="utf-8")

        if self._cache_skills:
            self._skill_cache[skill_name] = content

        logger.debug("Loaded skill", skill=skill_name, size=len(content))
        return content

    def load_skills(self, skill_names: list[str]) -> dict[str, str]:
        """
        Load multiple skills by name.

        Args:
            skill_names: List of skill names to load

        Returns:
            Dictionary of skill_name -> skill_content
        """
        skills = {}
        for name in skill_names:
            try:
                skills[name] = self.load(name)
            except FileNotFoundError:
                logger.warning("Skill not found, skipping", skill=name)

        logger.info("Loaded skills", count=len(skills), requested=len(skill_names))
        return skills

    def load_for_phase(
        self,
        phase: str,
        doc_type: str,
    ) -> dict[str, str]:
        """
        Load skills appropriate for a UCX phase and document type.

        Uses the layer_skills configuration to determine which skills to load.

        Args:
            phase: UCX phase (ucc, ucr, ucrem)
            doc_type: Document type (brd, prd, etc.)

        Returns:
            Dictionary of skill_name -> skill_content
        """
        from ucx.config.layer_skills import get_skills_for_phase
        from ucx.models.enums import DocType

        # Convert string to DocType enum
        try:
            dtype = DocType.from_string(doc_type)
        except (ValueError, KeyError):
            logger.warning("Unknown doc_type, using empty skill list", doc_type=doc_type)
            return {}

        # Get skill list using the helper function
        skill_list = get_skills_for_phase(dtype, phase)

        logger.debug(
            "Loading phase skills",
            phase=phase,
            doc_type=doc_type,
            skill_count=len(skill_list),
        )

        return self.load_skills(skill_list)

    def list_skills(self) -> list[str]:
        """
        List available skill names from all sources.

        Returns:
            List of skill names (without extension), project skills first
        """
        skills = set()

        # Project-specific skills first
        if self._project_skills_dir and self._project_skills_dir.exists():
            for skill_file in self._project_skills_dir.glob("*.md"):
                if skill_file.stem != "README":
                    skills.add(skill_file.stem)

        # Framework skills
        if self._skill_dir.exists():
            for skill_file in self._skill_dir.glob("*.md"):
                if skill_file.stem != "README":
                    skills.add(skill_file.stem)

        return sorted(skills)

    def list_project_skills(self) -> list[str]:
        """
        List only project-specific skills.

        Returns:
            List of project skill names (without extension)
        """
        if not self._project_skills_dir or not self._project_skills_dir.exists():
            return []

        skills = []
        for skill_file in self._project_skills_dir.glob("*.md"):
            if skill_file.stem != "README":
                skills.append(skill_file.stem)

        return sorted(skills)

    def has_project_skills(self) -> bool:
        """
        Check if project-specific skills exist.

        Returns:
            True if project skills directory exists and has skill files
        """
        if not self._project_skills_dir or not self._project_skills_dir.exists():
            return False
        return any(
            f.suffix == ".md" and f.stem != "README"
            for f in self._project_skills_dir.iterdir()
        )

    def skill_exists(self, skill_name: str) -> bool:
        """
        Check if a skill exists in any location.

        Args:
            skill_name: Name of the skill

        Returns:
            True if skill exists in project or framework directory
        """
        # Check project skills first
        if self._project_skills_dir:
            if self._find_skill_in_dir(skill_name, self._project_skills_dir):
                return True

        # Check framework skills
        return self._find_skill_in_dir(skill_name, self._skill_dir) is not None

    def clear_cache(self) -> None:
        """Clear the skill cache."""
        self._skill_cache.clear()
        logger.debug("Skill cache cleared")

    def get_skill_path(self, skill_name: str) -> Optional[Path]:
        """
        Get the path to a skill file.

        Priority: project skills > framework skills

        Args:
            skill_name: Name of the skill

        Returns:
            Path to skill file or None if not found
        """
        # Check project skills first
        if self._project_skills_dir:
            path = self._find_skill_in_dir(skill_name, self._project_skills_dir)
            if path:
                return path

        # Framework skills
        return self._find_skill_in_dir(skill_name, self._skill_dir)
