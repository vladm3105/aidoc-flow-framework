"""UCR (Unified Context Review) Engine.

Internal implementation for document review phase.
"""

import re
from pathlib import Path
from typing import Optional

from ucx.config.settings import UCXConfig
from ucx.models.enums import DocType, Status, ValidationStatus
from ucx.models.document import Document
from ucx.models.review import ReviewResult, ValidationResult
from ucx.validators.registry import get_validator
from ucx.ai.base import BaseAIClient
from ucx.ai.claude import ClaudeClient
from ucx.prompts.loader import PromptLoader
from ucx.prompts.renderer import PromptRenderer
from ucx.prompts.schema import UCRContext
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


class UCREngine:
    """
    UCR (Unified Context Review) engine.

    Handles document review by:
    1. Running structural validation
    2. Loading and injecting review personas
    3. Calling LLM for content review
    4. Extracting score and findings
    5. Generating review report
    """

    def __init__(
        self,
        config: UCXConfig,
        ai_client: Optional[BaseAIClient] = None,
    ) -> None:
        """
        Initialize the UCR engine.

        Args:
            config: UCX configuration
            ai_client: Optional AI client (defaults to Claude)
        """
        self._config = config
        self._client = ai_client or ClaudeClient(model=config.model)
        self._prompt_loader = PromptLoader(
            project_dir=config.get_project_dir(),
            framework_template_dir=config.get_prompt_dir(),
        )
        self._renderer = PromptRenderer()
        self._skill_loader = SkillLoader(
            skill_dir=config.get_skill_dir(),
            project_dir=config.get_project_dir(),
            strict_project_only=True,
        )
        self._skill_injector = SkillInjector()
        self._instrumentation = LLMInstrumentation(
            capture_content=config.otel.llm_capture_content
        )
        self._metrics = get_metrics()

        logger.debug("UCREngine initialized", model=config.model)

    def review(
        self,
        doc_type: DocType,
        doc_path: Path,
        upstream_path: Optional[Path] = None,
    ) -> ReviewResult:
        """
        Review a document.

        Args:
            doc_type: Document type
            doc_path: Path to document to review
            upstream_path: Optional upstream document for traceability

        Returns:
            ReviewResult with score and findings
        """
        with create_span("ucr.review", attributes={
            "doc_type": doc_type.value,
            "doc_path": str(doc_path),
        }) as span:
            import time
            start_time = time.perf_counter()

            # Load document
            document = Document.from_path(doc_path)
            content = document.read_content()

            # Run structural validation
            validation_result = self._run_validation(doc_type, doc_path)

            # Build context
            context = self._build_context(
                doc_type, document, content, validation_result, upstream_path
            )

            # Load and render prompt
            template = self._prompt_loader.load("ucr", doc_type.value)
            skills = self._skill_loader.load_for_phase("ucr", doc_type.value)

            prompt_result = self._renderer.render_with_skills(
                template, context, skills
            )

            # Call LLM
            request = LLMRequest(
                model=self._config.model,
                prompt=prompt_result.prompt,
                max_tokens=self._config.tokens.max_output_tokens,
                phase="ucr",
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

            # Parse review result
            review_result = self._parse_review(
                response["content"],
                doc_path,
                validation_result,
            )

            # Save report
            report_path = self._save_report(doc_path, doc_type, response["content"])
            review_result.report_path = report_path

            # Record metrics
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._metrics.record_document_reviewed(
                doc_type.value,
                review_result.score,
                duration_ms,
            )

            logger.info(
                "Document reviewed",
                doc_type=doc_type.value,
                score=review_result.score,
                findings=review_result.total_findings,
            )

            return review_result

    def _run_validation(
        self,
        doc_type: DocType,
        doc_path: Path,
    ) -> ValidationResult:
        """Run structural validation."""
        if self._config.skip_validation:
            return ValidationResult(
                status=ValidationStatus.SKIPPED,
                errors=[],
                warnings=[],
                passes=[],
            )

        validator = get_validator(doc_type)
        result = validator.validate(doc_path)

        self._metrics.record_validation(
            doc_type.value,
            len(result.errors),
            0 if result.errors else 100,
        )

        return result

    def _build_context(
        self,
        doc_type: DocType,
        document: Document,
        content: str,
        validation_result: ValidationResult,
        upstream_path: Optional[Path],
    ) -> UCRContext:
        """Build UCR context."""
        context = UCRContext(
            doc_type=doc_type.value,
            doc_id=document.doc_id,
            document_content=content,
            document_path=str(document.path),
            validation_errors=validation_result.errors,
            validation_warnings=validation_result.warnings,
            min_score=self._config.min_score,
            model=self._config.model,
        )

        if upstream_path and upstream_path.exists():
            context.upstream_content = upstream_path.read_text(encoding="utf-8")

        return context

    def _parse_review(
        self,
        review_content: str,
        doc_path: Path,
        validation_result: ValidationResult,
    ) -> ReviewResult:
        """Parse LLM review into structured result."""
        # Extract score
        score = self._extract_score(review_content)

        # Extract findings
        findings = self._extract_findings(review_content)

        # Determine status
        if score >= self._config.min_score:
            status = Status.PASSED
        elif findings.get("P0", 0) > 0:
            status = Status.FAILED
        else:
            status = Status.NEEDS_MANUAL

        return ReviewResult(
            doc_path=doc_path,
            report_path=doc_path,  # Will be updated
            score=score,
            status=status,
            validation_status=validation_result.status.value,
            findings=findings,
            finding_details={},  # TODO: Extract detailed findings
            raw_content=review_content,
            tokens_used=0,
        )

    def _extract_score(self, content: str) -> int:
        """Extract score from review content."""
        # Look for "Score: XX/100" or similar patterns
        patterns = [
            r"Score:\s*(\d+)\s*/\s*100",
            r"Score:\s*(\d+)",
            r"(\d+)\s*/\s*100\s*$",
            r"Final Score:\s*(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                return int(match.group(1))

        # Default score if not found
        logger.warning("Could not extract score from review")
        return 50

    def _extract_findings(self, content: str) -> dict[str, int]:
        """Extract finding counts from review content."""
        findings = {"P0": 0, "P1": 0, "P2": 0}

        # Count P0/P1/P2 findings
        for priority in findings:
            pattern = rf"{priority}[-_]?\d+"
            matches = re.findall(pattern, content, re.IGNORECASE)
            findings[priority] = len(matches)

        return findings

    def _save_report(self, doc_path: Path, doc_type: DocType, content: str) -> Path:
        """Save review report with versioned naming."""
        # Extract doc_id from path (e.g., BRD-01 from BRD-01_platform_architecture)
        doc_id_match = re.search(
            rf"({doc_type.value.upper()}-\d+)",
            str(doc_path),
            re.IGNORECASE
        )
        doc_id = doc_id_match.group(1).upper() if doc_id_match else f"{doc_type.value.upper()}-XX"

        # Find next version number
        search_dir = doc_path if doc_path.is_dir() else doc_path.parent
        version = 1
        for file in search_dir.glob(f"{doc_id}.UCR_review_report_v*.md"):
            match = re.search(r"_v(\d{3})\.md$", file.name)
            if match:
                version = max(version, int(match.group(1)) + 1)

        # New naming format: {DOC_ID}.UCR_review_report_v{NNN}.md
        report_name = f"{doc_id}.UCR_review_report_v{version:03d}.md"
        report_path = search_dir / report_name
        report_path.write_text(content, encoding="utf-8")
        return report_path
