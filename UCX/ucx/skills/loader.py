"""Skill/persona loader for UCX phases.

Loads skill definitions from markdown files in the personas directory.
"""

from pathlib import Path
from typing import Optional

from ucx.observability.logging import get_logger

logger = get_logger(__name__)


class SkillLoader:
    """
    Loads skill/persona definitions from the file system.

    Skills are markdown files containing persona descriptions, expertise,
    and behavioral guidelines that are injected into prompts.

    Directory structure:
        personas/
        ├── architect.md
        ├── auditor.md
        ├── product_owner.md
        └── ...
    """

    def __init__(
        self,
        skill_dir: Optional[Path] = None,
        cache_skills: bool = True,
    ) -> None:
        """
        Initialize the skill loader.

        Args:
            skill_dir: Directory containing skill files. Defaults to package personas.
            cache_skills: Whether to cache loaded skills.
        """
        if skill_dir is None:
            skill_dir = Path(__file__).parent / "personas"

        self._skill_dir = skill_dir
        self._cache_skills = cache_skills
        self._skill_cache: dict[str, str] = {}

        logger.debug("SkillLoader initialized", skill_dir=str(skill_dir))

    def load(self, skill_name: str) -> str:
        """
        Load a single skill by name.

        Args:
            skill_name: Name of the skill (without extension)

        Returns:
            Skill content

        Raises:
            FileNotFoundError: If skill file not found
        """
        # Check cache
        if self._cache_skills and skill_name in self._skill_cache:
            logger.debug("Skill cache hit", skill=skill_name)
            return self._skill_cache[skill_name]

        # Try to find skill file
        skill_path = self._skill_dir / f"{skill_name}.md"
        if not skill_path.exists():
            # Try with underscores/hyphens normalized
            normalized = skill_name.replace("-", "_").replace(" ", "_").lower()
            skill_path = self._skill_dir / f"{normalized}.md"

        if not skill_path.exists():
            logger.error("Skill not found", skill=skill_name)
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
        List available skill names.

        Returns:
            List of skill names (without extension)
        """
        if not self._skill_dir.exists():
            return []

        skills = []
        for skill_file in self._skill_dir.glob("*.md"):
            skills.append(skill_file.stem)

        return sorted(skills)

    def skill_exists(self, skill_name: str) -> bool:
        """
        Check if a skill exists.

        Args:
            skill_name: Name of the skill

        Returns:
            True if skill exists
        """
        skill_path = self._skill_dir / f"{skill_name}.md"
        if skill_path.exists():
            return True

        # Try normalized name
        normalized = skill_name.replace("-", "_").replace(" ", "_").lower()
        return (self._skill_dir / f"{normalized}.md").exists()

    def clear_cache(self) -> None:
        """Clear the skill cache."""
        self._skill_cache.clear()
        logger.debug("Skill cache cleared")

    def get_skill_path(self, skill_name: str) -> Optional[Path]:
        """
        Get the path to a skill file.

        Args:
            skill_name: Name of the skill

        Returns:
            Path to skill file or None if not found
        """
        skill_path = self._skill_dir / f"{skill_name}.md"
        if skill_path.exists():
            return skill_path

        normalized = skill_name.replace("-", "_").replace(" ", "_").lower()
        normalized_path = self._skill_dir / f"{normalized}.md"
        if normalized_path.exists():
            return normalized_path

        return None
