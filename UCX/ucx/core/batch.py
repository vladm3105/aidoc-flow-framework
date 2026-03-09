"""Batch processing for multiple documents.

Provides parallel document processing with progress tracking.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from ucx.config.settings import UCXConfig
from ucx.core.orchestrator import Orchestrator, OrchestratorResult
from ucx.observability.logging import get_logger

logger = get_logger(__name__)


@dataclass
class BatchResult:
    """Result from batch processing."""

    total: int
    completed: int
    passed: int
    failed: int
    results: list[OrchestratorResult] = field(default_factory=list)
    errors: list[tuple[Path, str]] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.completed == 0:
            return 0.0
        return self.passed / self.completed


class BatchProcessor:
    """
    Processes multiple documents in batch.

    Supports:
    - Parallel processing with configurable workers
    - Progress callbacks
    - Chunked processing for memory management
    - Error collection and continuation
    """

    def __init__(
        self,
        config: UCXConfig,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> None:
        """
        Initialize the batch processor.

        Args:
            config: UCX configuration
            progress_callback: Optional callback(current, total, status)
        """
        self._config = config
        self._progress_callback = progress_callback

        logger.debug(
            "BatchProcessor initialized",
            max_workers=config.max_workers,
            batch_size=config.batch_size,
        )

    def process(
        self,
        doc_type: str,
        targets: list[Path],
        from_ref: Optional[Path] = None,
        from_upstream: Optional[Path] = None,
    ) -> BatchResult:
        """
        Process multiple documents synchronously.

        Args:
            doc_type: Document type
            targets: List of target document paths
            from_ref: Reference documents directory
            from_upstream: Upstream artifact path

        Returns:
            BatchResult with all results
        """
        result = BatchResult(
            total=len(targets),
            completed=0,
            passed=0,
            failed=0,
        )

        # Process in chunks
        for i, chunk in enumerate(self._chunk(targets, self._config.batch_size)):
            logger.info(
                "Processing batch chunk",
                chunk=i + 1,
                size=len(chunk),
                total=len(targets),
            )

            chunk_results = self._process_chunk(
                doc_type, chunk, from_ref, from_upstream
            )

            for target, orchestrator_result in chunk_results:
                result.completed += 1
                result.results.append(orchestrator_result)

                if orchestrator_result.status.value == "passed":
                    result.passed += 1
                elif orchestrator_result.status.value == "failed":
                    result.failed += 1

                self._report_progress(
                    result.completed,
                    result.total,
                    f"{target.name}: {orchestrator_result.status.value}",
                )

        logger.info(
            "Batch processing complete",
            total=result.total,
            passed=result.passed,
            failed=result.failed,
            success_rate=f"{result.success_rate:.1%}",
        )

        return result

    async def process_async(
        self,
        doc_type: str,
        targets: list[Path],
        from_ref: Optional[Path] = None,
        from_upstream: Optional[Path] = None,
    ) -> BatchResult:
        """
        Process multiple documents asynchronously.

        Args:
            doc_type: Document type
            targets: List of target document paths
            from_ref: Reference documents directory
            from_upstream: Upstream artifact path

        Returns:
            BatchResult with all results
        """
        result = BatchResult(
            total=len(targets),
            completed=0,
            passed=0,
            failed=0,
        )

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self._config.max_workers)

        async def process_one(target: Path) -> tuple[Path, OrchestratorResult]:
            async with semaphore:
                return await asyncio.to_thread(
                    self._process_single,
                    doc_type,
                    target,
                    from_ref,
                    from_upstream,
                )

        # Process all concurrently
        tasks = [process_one(target) for target in targets]

        for coro in asyncio.as_completed(tasks):
            target, orchestrator_result = await coro

            result.completed += 1
            result.results.append(orchestrator_result)

            if orchestrator_result.status.value == "passed":
                result.passed += 1
            elif orchestrator_result.status.value == "failed":
                result.failed += 1

            self._report_progress(
                result.completed,
                result.total,
                f"{target.name}: {orchestrator_result.status.value}",
            )

        return result

    def _process_chunk(
        self,
        doc_type: str,
        targets: list[Path],
        from_ref: Optional[Path],
        from_upstream: Optional[Path],
    ) -> list[tuple[Path, OrchestratorResult]]:
        """Process a chunk of documents using thread pool."""
        results = []

        with ThreadPoolExecutor(max_workers=self._config.max_workers) as executor:
            futures = {
                executor.submit(
                    self._process_single,
                    doc_type,
                    target,
                    from_ref,
                    from_upstream,
                ): target
                for target in targets
            }

            for future in futures:
                target = futures[future]
                try:
                    result = future.result()
                    results.append((target, result))
                except Exception as e:
                    logger.error(
                        "Failed to process document",
                        target=str(target),
                        error=str(e),
                    )
                    # Create failed result
                    from ucx.models.enums import DocType, Status
                    failed_result = OrchestratorResult(
                        status=Status.FAILED,
                        doc_type=DocType.from_string(doc_type),
                        target_path=target,
                        errors=[str(e)],
                    )
                    results.append((target, failed_result))

        return results

    def _process_single(
        self,
        doc_type: str,
        target: Path,
        from_ref: Optional[Path],
        from_upstream: Optional[Path],
    ) -> tuple[Path, OrchestratorResult]:
        """Process a single document."""
        orchestrator = Orchestrator(self._config)
        result = orchestrator.run(
            doc_type=doc_type,
            target=target,
            from_ref=from_ref,
            from_upstream=from_upstream,
        )
        return target, result

    def _chunk(self, items: list, size: int) -> list[list]:
        """Split list into chunks."""
        return [items[i:i + size] for i in range(0, len(items), size)]

    def _report_progress(self, current: int, total: int, status: str) -> None:
        """Report progress via callback."""
        if self._progress_callback:
            self._progress_callback(current, total, status)
