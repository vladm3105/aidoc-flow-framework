"""Skill injection for UCX prompts.

Injects skill/persona content into prompts for multi-persona AI interactions.
"""

from typing import Optional

from ucx.observability.logging import get_logger

logger = get_logger(__name__)


class SkillInjector:
    """
    Injects skill content into UCX prompts.

    Supports multiple injection strategies:
    - Prepend: Add skills before the main prompt
    - Append: Add skills after the main prompt
    - Section: Insert skills at a marked section
    - Replace: Replace placeholders with skill content
    """

    # Skill section markers
    SKILL_SECTION_START = "<!-- SKILLS_START -->"
    SKILL_SECTION_END = "<!-- SKILLS_END -->"
    SKILL_PLACEHOLDER = "{{ skills }}"

    def __init__(
        self,
        strategy: str = "prepend",
        skill_header: str = "## Expert Personas\n\n",
        skill_separator: str = "\n---\n\n",
    ) -> None:
        """
        Initialize the skill injector.

        Args:
            strategy: Injection strategy (prepend, append, section, replace)
            skill_header: Header text before skills section
            skill_separator: Separator between individual skills
        """
        self._strategy = strategy
        self._skill_header = skill_header
        self._skill_separator = skill_separator

        logger.debug("SkillInjector initialized", strategy=strategy)

    def inject(
        self,
        prompt: str,
        skills: dict[str, str],
        strategy: Optional[str] = None,
    ) -> str:
        """
        Inject skills into a prompt.

        Args:
            prompt: Original prompt text
            skills: Dictionary of skill_name -> skill_content
            strategy: Override injection strategy

        Returns:
            Prompt with skills injected
        """
        if not skills:
            logger.debug("No skills to inject")
            return prompt

        strategy = strategy or self._strategy

        # Format skills section
        skills_text = self._format_skills(skills)

        # Apply injection strategy
        if strategy == "prepend":
            result = self._inject_prepend(prompt, skills_text)
        elif strategy == "append":
            result = self._inject_append(prompt, skills_text)
        elif strategy == "section":
            result = self._inject_section(prompt, skills_text)
        elif strategy == "replace":
            result = self._inject_replace(prompt, skills_text)
        else:
            logger.warning("Unknown strategy, using prepend", strategy=strategy)
            result = self._inject_prepend(prompt, skills_text)

        logger.info(
            "Skills injected",
            skill_count=len(skills),
            strategy=strategy,
            original_len=len(prompt),
            result_len=len(result),
        )

        return result

    def inject_by_role(
        self,
        prompt: str,
        skills: dict[str, str],
        role_markers: dict[str, str],
    ) -> str:
        """
        Inject skills at role-specific markers.

        Useful for multi-turn prompts where different personas
        speak at different points.

        Args:
            prompt: Original prompt text
            skills: Dictionary of skill_name -> skill_content
            role_markers: Dictionary of skill_name -> marker_text

        Returns:
            Prompt with skills injected at markers
        """
        result = prompt

        for skill_name, marker in role_markers.items():
            if skill_name in skills:
                skill_content = skills[skill_name]
                formatted = self._format_single_skill(skill_name, skill_content)
                result = result.replace(marker, formatted)

        return result

    def _format_skills(self, skills: dict[str, str]) -> str:
        """Format multiple skills into a single text block."""
        if not skills:
            return ""

        parts = [self._skill_header]

        for name, content in skills.items():
            formatted = self._format_single_skill(name, content)
            parts.append(formatted)

        return self._skill_separator.join(parts)

    def _format_single_skill(self, name: str, content: str) -> str:
        """Format a single skill with its name as header."""
        # Clean up the skill name for display
        display_name = name.replace("_", " ").replace("-", " ").title()

        # Check if content already has a header
        if content.strip().startswith("#"):
            # Content has its own header, use as-is
            return content.strip()

        # Add a header
        return f"### {display_name}\n\n{content.strip()}"

    def _inject_prepend(self, prompt: str, skills_text: str) -> str:
        """Inject skills at the beginning of the prompt."""
        return f"{skills_text}\n\n{prompt}"

    def _inject_append(self, prompt: str, skills_text: str) -> str:
        """Inject skills at the end of the prompt."""
        return f"{prompt}\n\n{skills_text}"

    def _inject_section(self, prompt: str, skills_text: str) -> str:
        """Inject skills at marked section."""
        if self.SKILL_SECTION_START in prompt:
            # Replace between markers
            start_idx = prompt.find(self.SKILL_SECTION_START)
            end_idx = prompt.find(self.SKILL_SECTION_END)

            if end_idx > start_idx:
                before = prompt[:start_idx]
                after = prompt[end_idx + len(self.SKILL_SECTION_END):]
                return f"{before}{self.SKILL_SECTION_START}\n{skills_text}\n{self.SKILL_SECTION_END}{after}"

        # Fallback to prepend if markers not found
        logger.debug("Section markers not found, using prepend")
        return self._inject_prepend(prompt, skills_text)

    def _inject_replace(self, prompt: str, skills_text: str) -> str:
        """Replace placeholder with skills."""
        if self.SKILL_PLACEHOLDER in prompt:
            return prompt.replace(self.SKILL_PLACEHOLDER, skills_text)

        # Check for Jinja2 style placeholder
        jinja_placeholder = "{{ skill_content }}"
        if jinja_placeholder in prompt:
            return prompt.replace(jinja_placeholder, skills_text)

        # Fallback to prepend if placeholder not found
        logger.debug("Placeholder not found, using prepend")
        return self._inject_prepend(prompt, skills_text)

    def extract_skills_section(self, prompt: str) -> tuple[str, str]:
        """
        Extract skills section from a prompt.

        Args:
            prompt: Prompt text with skills

        Returns:
            Tuple of (prompt_without_skills, skills_section)
        """
        if self.SKILL_SECTION_START in prompt:
            start_idx = prompt.find(self.SKILL_SECTION_START)
            end_idx = prompt.find(self.SKILL_SECTION_END)

            if end_idx > start_idx:
                before = prompt[:start_idx]
                skills = prompt[
                    start_idx + len(self.SKILL_SECTION_START):end_idx
                ].strip()
                after = prompt[end_idx + len(self.SKILL_SECTION_END):]
                return (before + after).strip(), skills

        return prompt, ""
