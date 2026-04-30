"""UCX Phase Orchestrator.

Coordinates the UCC → UCR → UCRem workflow.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from ucx.config.settings import UCXConfig
from ucx.models.enums import DocType, Status
from ucx.models.document import Document
from ucx.models.review import ReviewResult
from ucx.models.fix import FixProposal
from ucx.core.ucc import UCCEngine
from ucx.core.ucr import UCREngine
from ucx.core.ucrem import UCRemEngine
from ucx.core.drift import DriftMonitor
from ucx.observability.logging import get_logger
from ucx.observability.tracing import create_span
from ucx.observability.metrics import get_metrics

logger = get_logger(__name__)


@dataclass
class OrchestratorResult:
    """Result from orchestrator run."""

    status: Status
    doc_type: DocType
    target_path: Path
    score: int = 0
    iterations: int = 0
    drift_detected: bool = False
    document: Optional[Document] = None
    review_result: Optional[ReviewResult] = None
    fixes_applied: list[FixProposal] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class Orchestrator:
    """
    Orchestrates the UCX workflow phases.

    Manages the flow: UCC (Create) → UCR (Review) → UCRem (Remediate)
    with iteration control and drift monitoring.
    """

    def __init__(
        self,
        config: UCXConfig,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> None:
        """
        Initialize the orchestrator.

        Args:
            config: UCX configuration
            progress_callback: Optional callback(phase, iteration, score)
        """
        self._config = config
        self._progress_callback = progress_callback

        # Initialize engines
        self._ucc = UCCEngine(config)
        self._ucr = UCREngine(config)
        self._ucrem = UCRemEngine(config)
        self._drift = DriftMonitor(config)

        self._metrics = get_metrics()
        logger.debug("Orchestrator initialized")

    def run(
        self,
        doc_type: str,
        target: Path,
        from_ref: Optional[Path] = None,
        from_upstream: Optional[Path] = None,
        skip_creation: bool = False,
    ) -> OrchestratorResult:
        """
        Run the full UCX workflow.

        Args:
            doc_type: Document type (brd, prd, etc.)
            target: Target document path
            from_ref: Reference documents directory
            from_upstream: Upstream artifact path
            skip_creation: Skip UCC phase if document exists

        Returns:
            OrchestratorResult with final status
        """
        dtype = DocType.from_string(doc_type)

        with create_span("orchestrator.run", attributes={
            "doc_type": doc_type,
            "target": str(target),
        }) as span:
            result = OrchestratorResult(
                status=Status.PENDING,
                doc_type=dtype,
                target_path=target,
            )

            try:
                # Phase 1: Drift Check
                if not self._config.skip_drift:
                    drift_detected = self._check_drift(target, from_upstream)
                    result.drift_detected = drift_detected

                # Phase 2: Creation (UCC)
                if not skip_creation and not target.exists():
                    self._report_progress("ucc", 0, 0)
                    document = self._create_document(
                        dtype, target, from_ref, from_upstream
                    )
                    result.document = document
                else:
                    result.document = Document.from_path(target)

                # Phase 3-4: Review/Remediation Loop
                for iteration in range(1, self._config.max_iterations + 1):
                    result.iterations = iteration

                    # Review (UCR)
                    self._report_progress("ucr", iteration, result.score)
                    review_result = self._review_document(dtype, target)
                    result.review_result = review_result
                    result.score = review_result.score

                    # Check if passed
                    if review_result.score >= self._config.min_score:
                        result.status = Status.PASSED
                        span.set_attribute("final_score", result.score)
                        logger.info(
                            "Orchestration completed - PASSED",
                            score=result.score,
                            iterations=iteration,
                        )
                        break

                    # Remediation (UCRem) if not last iteration
                    if iteration < self._config.max_iterations:
                        self._report_progress("ucrem", iteration, result.score)
                        fixes = self._remediate_document(
                            dtype, target, review_result
                        )
                        result.fixes_applied.extend(fixes)

                else:
                    # Max iterations reached without passing
                    result.status = Status.NEEDS_MANUAL
                    logger.warning(
                        "Orchestration completed - NEEDS_MANUAL",
                        score=result.score,
                        iterations=self._config.max_iterations,
                    )

                # Record metrics
                self._metrics.record_autopilot_run(
                    doc_type=doc_type,
                    iterations=result.iterations,
                    success=result.status == Status.PASSED,
                    final_score=result.score,
                )

            except Exception as e:
                result.status = Status.FAILED
                result.errors.append(str(e))
                logger.error("Orchestration failed", error=str(e))
                raise

            return result

    def _check_drift(
        self,
        target: Path,
        upstream: Optional[Path],
    ) -> bool:
        """Check for upstream drift."""
        if upstream and upstream.exists():
            has_drift, changed = self._drift.check(target, upstream)
            if has_drift:
                logger.info("Drift detected", changed_files=changed)
            return has_drift
        return False

    def _create_document(
        self,
        doc_type: DocType,
        target: Path,
        from_ref: Optional[Path],
        from_upstream: Optional[Path],
    ) -> Document:
        """Create a new document."""
        return self._ucc.create(
            doc_type=doc_type,
            output_path=target,
            from_ref=from_ref,
            from_upstream=from_upstream,
        )

    def _review_document(
        self,
        doc_type: DocType,
        target: Path,
    ) -> ReviewResult:
        """Review a document."""
        return self._ucr.review(
            doc_type=doc_type,
            doc_path=target,
        )

    def _remediate_document(
        self,
        doc_type: DocType,
        target: Path,
        review_result: ReviewResult,
    ) -> list[FixProposal]:
        """Generate and apply fixes."""
        fixes = self._ucrem.generate_fixes(
            review_result=review_result,
            doc_path=target,
        )

        # Apply auto-safe fixes
        applied = []
        for fix in fixes:
            if fix.can_auto_apply:
                success = self._ucrem.apply_fix(fix, dry_run=False)
                if success:
                    applied.append(fix)

        return applied

    def _report_progress(self, phase: str, iteration: int, score: int) -> None:
        """Report progress via callback."""
        if self._progress_callback:
            self._progress_callback(phase, iteration, score)
