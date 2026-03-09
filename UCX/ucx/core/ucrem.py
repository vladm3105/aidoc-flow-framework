"""UCRem (Unified Context Remediation) Engine.

Internal implementation for document remediation phase.
"""

import re
from pathlib import Path
from typing import Optional

from ucx.config.settings import UCXConfig
from ucx.models.enums import DocType, Priority, Confidence, FixType
from ucx.models.review import ReviewResult
from ucx.models.fix import FixProposal, FixAction
from ucx.ai.base import BaseAIClient
from ucx.ai.claude import ClaudeClient
from ucx.prompts.loader import PromptLoader
from ucx.prompts.renderer import PromptRenderer
from ucx.prompts.schema import UCRemContext
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


class UCRemEngine:
    """
    UCRem (Unified Context Remediation) engine.

    Handles document remediation by:
    1. Parsing review findings
    2. Generating fix proposals via LLM
    3. Categorizing fixes by confidence
    4. Applying auto-safe fixes
    5. Producing remediation report
    """

    def __init__(
        self,
        config: UCXConfig,
        ai_client: Optional[BaseAIClient] = None,
    ) -> None:
        """
        Initialize the UCRem engine.

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

        logger.debug("UCRemEngine initialized", model=config.model)

    def generate_fixes(
        self,
        review_result: ReviewResult,
        doc_path: Path,
        iteration: int = 1,
    ) -> list[FixProposal]:
        """
        Generate fix proposals from review findings.

        Args:
            review_result: Review result with findings
            doc_path: Path to document to fix
            iteration: Current iteration number

        Returns:
            List of FixProposal objects
        """
        with create_span("ucrem.generate_fixes", attributes={
            "doc_path": str(doc_path),
            "score": review_result.score,
            "iteration": iteration,
        }) as span:
            import time
            start_time = time.perf_counter()

            # Load document content
            content = doc_path.read_text(encoding="utf-8")
            doc_type = self._detect_doc_type(doc_path)

            # Build context
            context = self._build_context(
                doc_type, doc_path, content, review_result, iteration
            )

            # Load and render prompt
            template = self._prompt_loader.load("ucrem", doc_type.value)
            skills = self._skill_loader.load_for_phase("ucrem", doc_type.value)

            prompt_result = self._renderer.render_with_skills(
                template, context, skills
            )

            # Call LLM
            request = LLMRequest(
                model=self._config.model,
                prompt=prompt_result.prompt,
                max_tokens=self._config.tokens.max_output_tokens,
                phase="ucrem",
                doc_type=doc_type.value,
                iteration=iteration,
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

            # Parse fix proposals
            fixes = self._parse_fixes(response["content"], doc_path)

            # Save report
            self._save_report(doc_path, response["content"], iteration)

            logger.info(
                "Fixes generated",
                doc_path=str(doc_path),
                fix_count=len(fixes),
                auto_safe=sum(1 for f in fixes if f.can_auto_apply),
            )

            return fixes

    def apply_fix(
        self,
        fix: FixProposal,
        dry_run: bool = False,
    ) -> bool:
        """
        Apply a single fix to the target file.

        Args:
            fix: Fix proposal to apply
            dry_run: If True, don't actually modify the file

        Returns:
            True if fix was applied successfully
        """
        if dry_run:
            logger.debug("Dry run - would apply fix", fix_id=fix.fix_id)
            return True

        try:
            return fix.apply(dry_run=dry_run)
        except Exception as e:
            logger.error("Failed to apply fix", fix_id=fix.fix_id, error=str(e))
            return False

    def apply_auto_safe(
        self,
        fixes: list[FixProposal],
        dry_run: bool = False,
    ) -> list[FixProposal]:
        """
        Apply all auto-safe fixes.

        Args:
            fixes: List of fix proposals
            dry_run: If True, don't actually modify files

        Returns:
            List of successfully applied fixes
        """
        applied = []

        for fix in fixes:
            if fix.can_auto_apply:
                if self.apply_fix(fix, dry_run=dry_run):
                    applied.append(fix)

        logger.info(
            "Auto-safe fixes applied",
            total=len([f for f in fixes if f.can_auto_apply]),
            applied=len(applied),
        )

        return applied

    def _detect_doc_type(self, doc_path: Path) -> DocType:
        """Detect document type from path or content."""
        name = doc_path.stem.upper()

        for dtype in DocType:
            if dtype.value.upper() in name:
                return dtype

        # Default to generic
        return DocType.BRD

    def _build_context(
        self,
        doc_type: DocType,
        doc_path: Path,
        content: str,
        review_result: ReviewResult,
        iteration: int,
    ) -> UCRemContext:
        """Build UCRem context."""
        return UCRemContext(
            doc_type=doc_type.value,
            document_content=content,
            document_path=str(doc_path),
            review_report=review_result.raw_content,
            review_score=review_result.score,
            findings_p0=review_result.finding_details.get("P0", []),
            findings_p1=review_result.finding_details.get("P1", []),
            findings_p2=review_result.finding_details.get("P2", []),
            iteration=iteration,
            max_iterations=self._config.max_iterations,
            model=self._config.model,
        )

    def _parse_fixes(
        self,
        response_content: str,
        doc_path: Path,
    ) -> list[FixProposal]:
        """Parse fix proposals from LLM response."""
        fixes = []

        # Look for YAML fix blocks
        yaml_blocks = re.findall(
            r"```yaml\s*(fix_id:.*?)```",
            response_content,
            re.DOTALL | re.IGNORECASE,
        )

        for i, block in enumerate(yaml_blocks):
            try:
                fix = FixProposal.from_yaml(block)
                fix.target_file = doc_path
                fixes.append(fix)
            except Exception as e:
                logger.warning(
                    "Failed to parse fix block",
                    block_index=i,
                    error=str(e),
                )

        return fixes

    def _save_report(
        self,
        doc_path: Path,
        content: str,
        iteration: int,
    ) -> Path:
        """Save remediation report."""
        report_name = f"{doc_path.stem}_UCRem_REPORT_iter{iteration}.md"
        report_path = doc_path.parent / report_name
        report_path.write_text(content, encoding="utf-8")
        return report_path
