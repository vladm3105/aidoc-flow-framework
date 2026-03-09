"""UCX Autopilot API - High-level orchestration."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union, Callable
import time

from ucx.config.settings import UCXConfig
from ucx.models.enums import DocType, Status
from ucx.models.drift_cache import DriftCache


@dataclass
class AutopilotResult:
    """Result of autopilot execution."""

    status: Status
    score: int
    iterations: int
    drift_detected: bool
    review_report: Path
    fix_report: Optional[Path] = None
    findings: dict[str, int] = field(default_factory=lambda: {"P0": 0, "P1": 0, "P2": 0})
    elapsed_time: float = 0.0
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """Check if autopilot succeeded."""
        return self.status == Status.PASS

    @property
    def needs_manual(self) -> bool:
        """Check if manual intervention is needed."""
        return self.status == Status.NEEDS_MANUAL


class UCXAutopilot:
    """
    High-level autopilot for document lifecycle management.

    Orchestrates UCC → UCR → UCRem phases automatically with:
    - Smart document detection (create vs review)
    - Drift monitoring
    - Iterative fix cycles
    - Progress callbacks

    Example:
        >>> from ucx import UCXAutopilot, UCXConfig
        >>>
        >>> config = UCXConfig(model="opus", max_iterations=3)
        >>> autopilot = UCXAutopilot(config)
        >>>
        >>> # Generate new document from reference
        >>> result = autopilot.run(
        ...     doc_type="brd",
        ...     target="docs/01_BRD/BRD-01",
        ...     from_ref="docs/00_REF/"
        ... )
        >>> print(f"Status: {result.status}, Score: {result.score}")

        >>> # Review existing document (auto-detected)
        >>> result = autopilot.run(
        ...     doc_type="brd",
        ...     target="docs/01_BRD/BRD-01"
        ... )
    """

    def __init__(
        self,
        config: Optional[UCXConfig] = None,
        *,
        model: str = "opus",
        max_iterations: int = 3,
        min_score: int = 90,
        skip_drift: bool = False,
        skill_dir: Optional[Path] = None,
        prompt_dir: Optional[Path] = None,
    ):
        """
        Initialize autopilot.

        Args:
            config: UCXConfig instance (takes precedence over kwargs)
            model: AI model to use (opus, sonnet, haiku)
            max_iterations: Maximum review/fix cycles
            min_score: Minimum passing score (0-100)
            skip_drift: Disable drift monitoring
            skill_dir: Custom skill definitions directory
            prompt_dir: Custom prompt templates directory
        """
        if config:
            self.config = config
        else:
            self.config = UCXConfig(
                model=model,
                max_iterations=max_iterations,
                min_score=min_score,
                skip_drift=skip_drift,
                skill_dir=skill_dir,
                prompt_dir=prompt_dir,
            )

        # Lazy import to avoid circular dependencies
        self._ucc: Optional["UCCPhase"] = None
        self._ucr: Optional["UCRPhase"] = None
        self._ucrem: Optional["UCRemPhase"] = None

    @property
    def ucc(self) -> "UCCPhase":
        """Get UCC phase instance."""
        if self._ucc is None:
            from ucx.api.creation import UCCPhase
            self._ucc = UCCPhase(self.config)
        return self._ucc

    @property
    def ucr(self) -> "UCRPhase":
        """Get UCR phase instance."""
        if self._ucr is None:
            from ucx.api.review import UCRPhase
            self._ucr = UCRPhase(self.config)
        return self._ucr

    @property
    def ucrem(self) -> "UCRemPhase":
        """Get UCRem phase instance."""
        if self._ucrem is None:
            from ucx.api.remediation import UCRemPhase
            self._ucrem = UCRemPhase(self.config)
        return self._ucrem

    def run(
        self,
        doc_type: Union[str, DocType],
        target: Union[str, Path],
        *,
        from_ref: Optional[Union[str, Path]] = None,
        from_upstream: Optional[Union[str, Path]] = None,
        from_iplan: Optional[Union[str, Path]] = None,
        dry_run: bool = False,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> AutopilotResult:
        """
        Execute autopilot workflow.

        Args:
            doc_type: Document type (brd, prd, ears, etc.)
            target: Target document path
            from_ref: Reference documents directory
            from_upstream: Upstream artifact path
            from_iplan: Implementation plan path
            dry_run: Show actions without executing
            progress_callback: Optional callback for progress updates
                               Signature: (phase: str, iteration: int) -> None

        Returns:
            AutopilotResult with status, score, and artifacts

        Raises:
            UCXError: On validation or execution failure
            FileNotFoundError: If required files are missing
        """
        start_time = time.time()

        # Normalize inputs
        if isinstance(doc_type, str):
            doc_type = DocType.from_string(doc_type)
        target = Path(target)

        from_ref = Path(from_ref) if from_ref else None
        from_upstream = Path(from_upstream) if from_upstream else None
        from_iplan = Path(from_iplan) if from_iplan else None

        # Initialize tracking
        drift_detected = False
        review_report = target.parent / f"{doc_type.value.upper()}_UCR_REVIEW.md"
        fix_report: Optional[Path] = None

        # Smart detection: create or review?
        action = self.detect_action(target)

        if progress_callback:
            progress_callback(f"Detected action: {action}", 0)

        # Phase 1: Create (if needed)
        if action == "create":
            if progress_callback:
                progress_callback("UCC: Creating document", 0)

            if not dry_run:
                self.ucc.create(
                    doc_type=doc_type,
                    output_path=target,
                    from_ref=from_ref,
                    from_upstream=from_upstream,
                    from_iplan=from_iplan,
                )

                # Initialize drift cache
                if not self.config.skip_drift and from_ref:
                    self._create_drift_cache(target, from_ref)

        # Phase 2-5: Review/Fix loop
        score = 0
        findings = {"P0": 0, "P1": 0, "P2": 0}
        status = Status.IN_PROGRESS

        for iteration in range(1, self.config.max_iterations + 1):
            if progress_callback:
                progress_callback(f"UCR: Review iteration {iteration}", iteration)

            # Check drift
            if not self.config.skip_drift:
                cache_path = self._get_drift_cache_path(target)
                if cache_path.exists() and from_ref:
                    cache = DriftCache.load(cache_path)
                    drift_detected, _ = cache.check_drift(from_ref)

            # Run review
            if not dry_run:
                review_result = self.ucr.review(
                    doc_type=doc_type,
                    doc_path=target,
                    output_path=review_report,
                )
                score = review_result.score
                findings = review_result.findings

                # Update drift cache
                if not self.config.skip_drift:
                    self._update_drift_cache(target, score, "REVIEWED", drift_detected)

                # Check if we've reached target score
                if score >= self.config.min_score and findings["P0"] == 0:
                    status = Status.PASS
                    break

            # Run remediation
            if progress_callback:
                progress_callback(f"UCRem: Generating fixes", iteration)

            if not dry_run:
                fix_report = target.parent / f"{doc_type.value.upper()}_UCRem_REPORT.md"
                fixes = self.ucrem.generate_fixes(
                    review_report=review_report,
                    doc_path=target,
                    output_path=fix_report,
                )

                # Check for manual-required fixes
                manual_required = any(f.needs_review for f in fixes)
                if manual_required:
                    status = Status.NEEDS_MANUAL
                    break

                # Apply auto-safe fixes
                self.ucrem.apply_auto_safe(fixes)

        else:
            # Loop completed without reaching target
            status = Status.FAIL

        elapsed = time.time() - start_time

        # Final drift cache update
        if not dry_run and not self.config.skip_drift:
            self._update_drift_cache(target, score, status.value, drift_detected)

        return AutopilotResult(
            status=status,
            score=score,
            iterations=iteration if not dry_run else 0,
            drift_detected=drift_detected,
            review_report=review_report,
            fix_report=fix_report,
            findings=findings,
            elapsed_time=elapsed,
        )

    def run_batch(
        self,
        doc_type: Union[str, DocType],
        targets: list[Union[str, Path]],
        *,
        chunk_size: int = 3,
        parallel: bool = False,
        **kwargs,
    ) -> list[AutopilotResult]:
        """
        Process multiple documents.

        Args:
            doc_type: Document type for all targets
            targets: List of target paths
            chunk_size: Number of documents per chunk
            parallel: Enable parallel processing (not yet implemented)
            **kwargs: Additional arguments passed to run()

        Returns:
            List of AutopilotResult for each target
        """
        results = []

        # Process in chunks
        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i + chunk_size]
            for target in chunk:
                result = self.run(doc_type=doc_type, target=target, **kwargs)
                results.append(result)

        return results

    def detect_action(self, target: Path) -> str:
        """
        Detect whether to create or review.

        Args:
            target: Target document path

        Returns:
            "create" if target doesn't exist or is empty
            "review" if target exists with content
        """
        if not target.exists():
            return "create"

        if target.is_dir():
            # Check for document files in directory
            md_files = list(target.glob("*.md"))
            # Exclude review/report files
            doc_files = [f for f in md_files if "REVIEW" not in f.name and "REPORT" not in f.name]
            if not doc_files:
                return "create"
            return "review"

        # Single file
        if target.stat().st_size == 0:
            return "create"

        return "review"

    def _get_drift_cache_path(self, target: Path) -> Path:
        """Get drift cache path for target."""
        if target.is_dir():
            return target / ".drift_cache.json"
        return target.parent / ".drift_cache.json"

    def _create_drift_cache(self, target: Path, from_ref: Path) -> None:
        """Create initial drift cache."""
        cache = DriftCache(
            document_id=target.stem,
            upstream_mode="ref",
        )

        # Track upstream files
        if from_ref.is_dir():
            for f in from_ref.glob("*"):
                if f.is_file():
                    cache.track_upstream(f)
        else:
            cache.track_upstream(from_ref)

        cache.save(self._get_drift_cache_path(target))

    def _update_drift_cache(
        self,
        target: Path,
        score: int,
        status: str,
        drift_detected: bool,
    ) -> None:
        """Update drift cache with review results."""
        cache_path = self._get_drift_cache_path(target)

        if cache_path.exists():
            cache = DriftCache.load(cache_path)
        else:
            cache = DriftCache(document_id=target.stem)

        cache.add_review(score, status, drift_detected)
        cache.save(cache_path)
