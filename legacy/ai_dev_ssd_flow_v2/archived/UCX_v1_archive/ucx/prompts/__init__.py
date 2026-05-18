"""UCX Prompts Module.

Provides prompt loading, Jinja2 rendering, context management,
and prompt inspection toolset for UCX phases.

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

Prompt Inspection Toolset (v1.14.0):
    from ucx.prompts import (
        DocumentLoader,
        PromptInspector,
        TokenAnalyzer,
        SectionMapper,
    )

    # Load document and analyze
    loader = DocumentLoader()
    content, sections, tokens = loader.load(Path("docs/01_BRD/BRD-01/"), "brd")

    # Analyze tokens
    analyzer = TokenAnalyzer(sections)
    result = analyzer.analyze(Path("docs/01_BRD/BRD-01/"), "brd")

    # Build section matrix
    mapper = SectionMapper(sections)
    matrix = mapper.build_matrix(Path("docs/01_BRD/BRD-01/"), "brd")
"""

from ucx.prompts.schema import UCCContext, UCRContext, UCRemContext
from ucx.prompts.loader import PromptLoader
from ucx.prompts.renderer import PromptRenderer

# Prompt inspection toolset (v1.14.0)
from ucx.prompts.models import (
    PromptSection,
    InspectionResult,
    PersonaTokens,
    TokenAnalysis,
    SectionMatrix,
    CheckResult,
    GeneratedPrompt,
    GenerationResult,
    PromptMetadata,
)
from ucx.prompts.exceptions import (
    PromptInspectionError,
    DocumentNotFoundError,
    InvalidDocumentTypeError,
    PromptFileNotFoundError,
    MetadataNotFoundError,
    PersonaNotFoundError,
    TokenBudgetExceededError,
    ConfigurationError,
    PromptGenerationError,
    validate_doc_type,
    validate_persona,
    validate_personas,
)
from ucx.prompts.document import DocumentLoader
from ucx.prompts.inspector import PromptInspector
from ucx.prompts.analyzer import TokenAnalyzer
from ucx.prompts.mapper import SectionMapper
from ucx.prompts.api import UCPromptPhase

__all__ = [
    # Existing exports
    "UCCContext",
    "UCRContext",
    "UCRemContext",
    "PromptLoader",
    "PromptRenderer",
    # Prompt inspection models
    "PromptSection",
    "InspectionResult",
    "PersonaTokens",
    "TokenAnalysis",
    "SectionMatrix",
    "CheckResult",
    "GeneratedPrompt",
    "GenerationResult",
    "PromptMetadata",
    # Prompt inspection exceptions
    "PromptInspectionError",
    "DocumentNotFoundError",
    "InvalidDocumentTypeError",
    "PromptFileNotFoundError",
    "MetadataNotFoundError",
    "PersonaNotFoundError",
    "TokenBudgetExceededError",
    "ConfigurationError",
    "PromptGenerationError",
    "validate_doc_type",
    "validate_persona",
    "validate_personas",
    # Prompt inspection classes
    "DocumentLoader",
    "PromptInspector",
    "TokenAnalyzer",
    "SectionMapper",
    # Main API
    "UCPromptPhase",
]
