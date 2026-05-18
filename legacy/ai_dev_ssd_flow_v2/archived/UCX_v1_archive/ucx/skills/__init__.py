"""UCX Skills Module.

Provides skill/persona loading and injection for UCX phases.

Skills are markdown files containing persona definitions and expertise
that are injected into prompts to guide the AI's behavior.

Usage:
    from ucx.skills import SkillLoader, SkillInjector

    # Load skills
    loader = SkillLoader()
    skills = loader.load_skills(["architect", "auditor"])

    # Inject into prompt
    injector = SkillInjector()
    enriched_prompt = injector.inject(prompt, skills)
"""

from ucx.skills.loader import SkillLoader
from ucx.skills.injector import SkillInjector

__all__ = [
    "SkillLoader",
    "SkillInjector",
]
