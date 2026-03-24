"""MCP Tool definitions for UCX Framework.

Defines all MCP tools exposed by the UCX server.
"""

from pathlib import Path
from typing import Any, Callable, Optional

from ucx.observability.logging import get_logger

logger = get_logger(__name__)


class UCXTools:
    """
    MCP Tool definitions for UCX.

    Provides tool registration methods for FastMCP.
    """

    def __init__(self, config: Any) -> None:
        """
        Initialize tools with config.

        Args:
            config: UCX configuration
        """
        self._config = config

    def register(self, mcp: Any) -> None:
        """
        Register all tools with MCP server.

        Args:
            mcp: FastMCP instance
        """
        self._register_autopilot(mcp)
        self._register_create(mcp)
        self._register_review(mcp)
        self._register_remediate(mcp)
        self._register_check_drift(mcp)
        self._register_validate(mcp)
        self._register_batch(mcp)
        self._register_status(mcp)

        logger.debug("All MCP tools registered", tool_count=8)

    def _register_autopilot(self, mcp: Any) -> None:
        """Register autopilot tool."""

        @mcp.tool()
        def ucx_autopilot(
            doc_type: str,
            target: str,
            from_ref: Optional[str] = None,
            from_upstream: Optional[str] = None,
            max_iterations: int = 3,
            min_score: int = 90,
        ) -> dict:
            """
            Run UCX autopilot workflow for document creation/review/remediation.

            Args:
                doc_type: Document type (brd, prd, ears, bdd, adr, sys, req, ctr, spec, tspec)
                target: Target document path
                from_ref: Reference documents directory
                from_upstream: Upstream artifact path
                max_iterations: Maximum review/fix cycles
                min_score: Minimum passing score

            Returns:
                AutopilotResult with status, score, and artifacts
            """
            from ucx.api.autopilot import UCXAutopilot

            pilot = UCXAutopilot(config=self._config)

            # Update config for this run
            self._config.max_iterations = max_iterations
            self._config.min_score = min_score

            result = pilot.run(
                doc_type=doc_type,
                target=Path(target),
                from_ref=Path(from_ref) if from_ref else None,
                from_upstream=Path(from_upstream) if from_upstream else None,
            )

            return {
                "status": result.status.value,
                "score": result.score,
                "iterations": result.iterations,
                "drift_detected": result.drift_detected,
                "review_report": str(result.review_report) if result.review_report else None,
                "fix_report": str(result.fix_report) if result.fix_report else None,
                "findings": result.findings,
            }

    def _register_create(self, mcp: Any) -> None:
        """Register create tool."""

        @mcp.tool()
        def ucx_create(
            doc_type: str,
            output_path: str,
            from_ref: Optional[str] = None,
            from_upstream: Optional[str] = None,
        ) -> dict:
            """
            Create a new document using UCX UCC phase.

            Args:
                doc_type: Document type
                output_path: Output document path
                from_ref: Reference documents directory
                from_upstream: Upstream artifact path

            Returns:
                Created document information
            """
            from ucx.api.creation import UCCPhase

            ucc = UCCPhase(config=self._config)
            doc = ucc.create(
                doc_type=doc_type,
                output_path=Path(output_path),
                from_ref=Path(from_ref) if from_ref else None,
                from_upstream=Path(from_upstream) if from_upstream else None,
            )

            return {
                "path": str(doc.path),
                "doc_id": doc.doc_id,
                "doc_type": doc.doc_type.value,
                "created": True,
            }

    def _register_review(self, mcp: Any) -> None:
        """Register review tool."""

        @mcp.tool()
        def ucx_review(
            doc_type: str,
            doc_path: str,
        ) -> dict:
            """
            Review a document using UCX UCR phase.

            Args:
                doc_type: Document type
                doc_path: Document path to review

            Returns:
                Review result with score and findings
            """
            from ucx.api.review import UCRPhase

            ucr = UCRPhase(config=self._config)
            result = ucr.review(doc_type=doc_type, doc_path=Path(doc_path))

            return {
                "score": result.score,
                "status": result.status.value,
                "findings": result.findings,
                "has_critical": result.has_critical,
                "report_path": str(result.report_path),
            }

    def _register_remediate(self, mcp: Any) -> None:
        """Register remediate tool."""

        @mcp.tool()
        def ucx_remediate(
            doc_type: str,
            doc_path: str,
            review_report: str,
        ) -> dict:
            """
            Generate fixes using UCX UCRem phase.

            Args:
                doc_type: Document type
                doc_path: Document path to remediate
                review_report: Path to review report

            Returns:
                Fix proposals with confidence levels
            """
            from ucx.api.remediation import UCRemPhase

            ucrem = UCRemPhase(config=self._config)
            fixes = ucrem.generate_fixes(
                review_report=Path(review_report),
                doc_path=Path(doc_path),
            )

            return {
                "fix_count": len(fixes),
                "fixes": [
                    {
                        "fix_id": f.fix_id,
                        "priority": f.priority.value,
                        "confidence": f.confidence.value,
                        "target_section": f.target_section,
                        "can_auto_apply": f.can_auto_apply,
                    }
                    for f in fixes
                ],
            }

    def _register_check_drift(self, mcp: Any) -> None:
        """Register check drift tool."""

        @mcp.tool()
        def ucx_check_drift(doc_path: str, upstream_path: Optional[str] = None) -> dict:
            """
            Check document for upstream drift.

            Args:
                doc_path: Document path to check
                upstream_path: Optional specific upstream to check

            Returns:
                Drift detection result
            """
            from ucx.core.drift import DriftMonitor

            monitor = DriftMonitor(self._config)
            doc_path = Path(doc_path)
            upstream = Path(upstream_path) if upstream_path else None

            has_drift, changed = monitor.check(doc_path, upstream)

            return {
                "has_drift": has_drift,
                "changed_files": changed,
                "doc_path": str(doc_path),
            }

    def _register_validate(self, mcp: Any) -> None:
        """Register validate tool."""

        @mcp.tool()
        def ucx_validate(
            doc_type: str,
            doc_path: str,
        ) -> dict:
            """
            Validate document structure.

            Args:
                doc_type: Document type
                doc_path: Document path to validate

            Returns:
                Validation result with errors/warnings
            """
            from ucx.models.enums import DocType
            from ucx.validators.registry import get_validator

            dtype = DocType.from_string(doc_type)
            validator = get_validator(dtype)
            result = validator.validate(Path(doc_path))

            return {
                "status": result.status.value,
                "errors": result.errors,
                "warnings": result.warnings,
                "passes": result.passes,
                "error_count": len(result.errors),
                "warning_count": len(result.warnings),
            }

    def _register_batch(self, mcp: Any) -> None:
        """Register batch processing tool."""

        @mcp.tool()
        def ucx_batch(
            doc_type: str,
            directory: str,
            operation: str = "review",
            pattern: str = "*.md",
        ) -> dict:
            """
            Run batch operation on multiple documents.

            Args:
                doc_type: Document type
                directory: Directory containing documents
                operation: Operation type (review, validate)
                pattern: File pattern to match

            Returns:
                Batch operation results
            """
            from ucx.core.batch import BatchProcessor

            processor = BatchProcessor(self._config)
            results = processor.process(
                doc_type=doc_type,
                directory=Path(directory),
                operation=operation,
                pattern=pattern,
            )

            return {
                "total": results.total,
                "passed": results.passed,
                "failed": results.failed,
                "errors": results.errors,
                "items": [
                    {
                        "path": str(item.path),
                        "status": item.status.value,
                        "score": item.score,
                    }
                    for item in results.items
                ],
            }

    def _register_status(self, mcp: Any) -> None:
        """Register status tool."""

        @mcp.tool()
        def ucx_status(doc_path: str) -> dict:
            """
            Get document status from drift cache.

            Args:
                doc_path: Document path

            Returns:
                Document status information
            """
            from ucx.models.drift_cache import DriftCache

            doc_path = Path(doc_path)
            cache_path = doc_path.parent / ".drift_cache.json"

            if cache_path.exists():
                cache = DriftCache.load(cache_path)
                latest = cache.latest_review

                return {
                    "exists": True,
                    "document_id": cache.document_id,
                    "upstream_mode": cache.upstream_mode,
                    "last_reviewed": cache.last_reviewed.isoformat(),
                    "latest_score": cache.latest_score,
                    "latest_status": latest.status if latest else None,
                    "review_count": len(cache.review_history),
                    "tracked_upstreams": list(cache.upstream_documents.keys()),
                }
            else:
                return {
                    "exists": False,
                    "message": "No drift cache found for document",
                }
