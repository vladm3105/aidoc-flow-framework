"""UCC (Unified Context Creation) Engine.

Internal implementation for document creation phase.
"""

from pathlib import Path
from typing import Optional

from ucx.config.settings import UCXConfig
from ucx.models.enums import DocType
from ucx.models.document import Document
from ucx.ai.base import BaseAIClient
from ucx.ai.claude import ClaudeClient
from ucx.prompts.loader import PromptLoader
from ucx.prompts.renderer import PromptRenderer
from ucx.prompts.schema import UCCContext
from ucx.skills.loader import SkillLoader
from ucx.skills.injector import SkillInjector
from ucx.observability.logging import get_logger
from ucx.observability.tracing import create_span
from ucx.observability.metrics import get_metrics
from ucx.observability.llm_instrumentation import (
    LLMInstrumentation,
    LLMRequest,
    LLMResponse,
)

logger = get_logger(__name__)


class UCCEngine:
    """
    UCC (Unified Context Creation) engine.

    Handles document creation by:
    1. Loading reference/upstream content
    2. Loading and injecting skills/personas
    3. Rendering prompt templates
    4. Calling LLM for generation
    5. Saving generated document
    """

    def __init__(
        self,
        config: UCXConfig,
        ai_client: Optional[BaseAIClient] = None,
    ) -> None:
        """
        Initialize the UCC engine.

        Args:
            config: UCX configuration
            ai_client: Optional AI client (defaults to Claude)
        """
        self._config = config
        self._client = ai_client or ClaudeClient(model=config.model)
        self._prompt_loader = PromptLoader(config.get_prompt_dir())
        self._renderer = PromptRenderer()
        self._skill_loader = SkillLoader(config.get_skill_dir())
        self._skill_injector = SkillInjector()
        self._instrumentation = LLMInstrumentation(
            capture_content=config.otel.llm_capture_content
        )
        self._metrics = get_metrics()

        logger.debug("UCCEngine initialized", model=config.model)

    def create(
        self,
        doc_type: DocType,
        output_path: Path,
        from_ref: Optional[Path] = None,
        from_upstream: Optional[Path] = None,
        from_iplan: Optional[Path] = None,
    ) -> Document:
        """
        Create a new document.

        Args:
            doc_type: Document type to create
            output_path: Path for output document
            from_ref: Reference documents directory
            from_upstream: Upstream artifact path
            from_iplan: Implementation plan path

        Returns:
            Created Document
        """
        with create_span("ucc.create", attributes={
            "doc_type": doc_type.value,
            "output_path": str(output_path),
        }) as span:
            import time
            start_time = time.perf_counter()

            # Build context
            context = self._build_context(
                doc_type, output_path, from_ref, from_upstream, from_iplan
            )

            # Load and render prompt
            template = self._prompt_loader.load("ucc", doc_type.value)
            skills = self._skill_loader.load_for_phase("ucc", doc_type.value)

            prompt_result = self._renderer.render_with_skills(
                template, context, skills
            )

            # Call LLM
            request = LLMRequest(
                model=self._config.model,
                prompt=prompt_result.prompt,
                max_tokens=self._config.tokens.max_output_tokens,
                phase="ucc",
                doc_type=doc_type.value,
            )

            with self._instrumentation.span(request) as llm_span:
                response = self._client.generate(
                    prompt=prompt_result.prompt,
                    max_tokens=self._config.tokens.max_output_tokens,
                )

                llm_response = LLMResponse(
                    content=response["content"],
                    model=response.get("model", self._config.model),
                    response_id=response.get("id", "unknown"),
                    input_tokens=response.get("input_tokens", 0),
                    output_tokens=response.get("output_tokens", 0),
                    latency_ms=(time.perf_counter() - start_time) * 1000,
                )
                self._instrumentation.record_response(llm_span, llm_response)

            # Save document
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(response["content"], encoding="utf-8")

            # Create Document instance
            document = Document.from_path(output_path)

            # Record metrics
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._metrics.record_document_created(doc_type.value, duration_ms)

            logger.info(
                "Document created",
                doc_type=doc_type.value,
                path=str(output_path),
                tokens=llm_response.total_tokens,
            )

            return document

    def _build_context(
        self,
        doc_type: DocType,
        output_path: Path,
        from_ref: Optional[Path],
        from_upstream: Optional[Path],
        from_iplan: Optional[Path],
    ) -> UCCContext:
        """Build UCC context from sources."""
        context = UCCContext(
            doc_type=doc_type.value,
            target_path=str(output_path),
            model=self._config.model,
            max_tokens=self._config.tokens.max_output_tokens,
        )

        # Load reference content
        if from_ref and from_ref.exists():
            ref_content = self._load_directory_content(from_ref)
            context.reference_content = ref_content

        # Load upstream content
        if from_upstream and from_upstream.exists():
            context.upstream_content = from_upstream.read_text(encoding="utf-8")

        # Load IPLAN content
        if from_iplan and from_iplan.exists():
            context.iplan_content = from_iplan.read_text(encoding="utf-8")

        return context

    def _load_directory_content(self, directory: Path) -> str:
        """Load content from all markdown files in a directory."""
        content_parts = []

        for md_file in sorted(directory.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            content_parts.append(f"## {md_file.name}\n\n{content}")

        return "\n\n---\n\n".join(content_parts)
