"""Drift monitoring for upstream document changes.

Detects when upstream documents have changed since last review.
"""

from pathlib import Path
from typing import Optional

from ucx.config.settings import UCXConfig
from ucx.models.drift_cache import DriftCache
from ucx.observability.logging import get_logger
from ucx.observability.metrics import get_metrics

logger = get_logger(__name__)


class DriftMonitor:
    """
    Monitors upstream documents for drift.

    Tracks hash values of upstream documents and detects
    when they have changed since the last review.
    """

    def __init__(self, config: Optional[UCXConfig] = None) -> None:
        """
        Initialize the drift monitor.

        Args:
            config: UCX configuration
        """
        self._config = config or UCXConfig()
        self._metrics = get_metrics()

        logger.debug("DriftMonitor initialized")

    def check(
        self,
        target: Path,
        upstream: Optional[Path] = None,
    ) -> tuple[bool, list[str]]:
        """
        Check for drift in upstream documents.

        Args:
            target: Target document path
            upstream: Optional specific upstream path to check

        Returns:
            Tuple of (has_drift, list of changed files)
        """
        cache_path = target.parent / ".drift_cache.json"

        # Load or create cache
        if cache_path.exists():
            cache = DriftCache.load(cache_path)
        else:
            cache = DriftCache(document_id=target.stem)

        # Check specific upstream
        if upstream and upstream.exists():
            has_drift, changed = cache.check_drift(upstream)
        else:
            # No upstream specified - check if any tracked upstreams exist
            # If no cache or no tracked upstreams, no drift possible
            if not cache.upstream_documents:
                has_drift, changed = False, []
            else:
                # Check all tracked upstreams by iterating over them
                has_drift = False
                changed = []
                for upstream_name in cache.upstream_documents:
                    upstream_path = target.parent / upstream_name
                    if upstream_path.exists():
                        drift, files = cache.check_drift(upstream_path)
                        if drift:
                            has_drift = True
                            changed.extend(files)

        # Record metrics
        self._metrics.record_drift_check(
            doc_type=self._detect_doc_type(target),
            drift_found=has_drift,
        )

        if has_drift:
            logger.info(
                "Drift detected",
                target=str(target),
                changed_files=changed,
            )

        return has_drift, changed

    def track(
        self,
        target: Path,
        upstream: Path,
    ) -> None:
        """
        Track an upstream document for drift detection.

        Args:
            target: Target document path
            upstream: Upstream document to track
        """
        cache_path = target.parent / ".drift_cache.json"

        # Load or create cache
        if cache_path.exists():
            cache = DriftCache.load(cache_path)
        else:
            cache = DriftCache(document_id=target.stem)

        # Track the upstream
        cache.track_upstream(upstream)
        cache.save(cache_path)

        logger.debug(
            "Upstream tracked",
            target=str(target),
            upstream=str(upstream),
        )

    def record_review(
        self,
        target: Path,
        score: int,
        status: str,
    ) -> None:
        """
        Record a review in the drift cache.

        Args:
            target: Target document path
            score: Review score
            status: Review status
        """
        cache_path = target.parent / ".drift_cache.json"

        if cache_path.exists():
            cache = DriftCache.load(cache_path)
        else:
            cache = DriftCache(document_id=target.stem)

        cache.add_review(score, status, drift_detected=False)
        cache.save(cache_path)

        logger.debug(
            "Review recorded",
            target=str(target),
            score=score,
            status=status,
        )

    def clear_cache(self, target: Path) -> None:
        """
        Clear drift cache for a target.

        Args:
            target: Target document path
        """
        cache_path = target.parent / ".drift_cache.json"

        if cache_path.exists():
            cache_path.unlink()
            logger.debug("Drift cache cleared", target=str(target))

    def _detect_doc_type(self, path: Path) -> str:
        """Detect document type from path."""
        name = path.stem.upper()

        doc_types = ["BRD", "PRD", "EARS", "BDD", "ADR", "SYS", "REQ", "CTR", "SPEC", "TSPEC"]
        for dtype in doc_types:
            if dtype in name:
                return dtype.lower()

        return "unknown"
