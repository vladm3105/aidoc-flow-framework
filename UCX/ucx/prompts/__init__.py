"""UCX Prompts Module.

Provides prompt loading, Jinja2 rendering, and context management for UCX phases.

Usage:
    from ucx.prompts import PromptLoader, PromptRenderer, UCCContext

    # Load and render a prompt
    loader = PromptLoader()
    renderer = PromptRenderer()

    context = UCCContext(
        doc_type="brd",
        reference_content="...",
        skills=["architect", "auditor"],
    )

    prompt = renderer.render(
        loader.load("ucc", "brd"),
        context.model_dump(),
    )
"""

from ucx.prompts.schema import UCCContext, UCRContext, UCRemContext
from ucx.prompts.loader import PromptLoader
from ucx.prompts.renderer import PromptRenderer

__all__ = [
    "UCCContext",
    "UCRContext",
    "UCRemContext",
    "PromptLoader",
    "PromptRenderer",
]
