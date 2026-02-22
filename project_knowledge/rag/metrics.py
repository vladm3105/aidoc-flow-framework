"""RAG metrics for quality measurement.

Provides infrastructure to track search operations, measure latency,
and collect feedback for continuous improvement.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class SearchMetrics:
    """Metrics for a single search operation."""

    query: str
    query_type: str | None
    strategy: str  # "vector", "hybrid", "rerank", "expansion"
    retrieval_count: int
    reranked: bool
    top_similarity: float | None
    latency_ms: int
    timestamp: str
    ticker: str | None = None
    expanded_queries: int = 0  # Number of query variations used
    relevance_feedback: int | None = None  # 1-5 user rating (future)
    context_used: bool | None = None  # Was context actually used? (future)


@dataclass
class MetricsSummary:
    """Aggregate metrics summary."""

    total_searches: int = 0
    avg_latency_ms: float = 0.0
    avg_results: float = 0.0
    avg_top_similarity: float = 0.0
    strategy_distribution: dict[str, int] = field(default_factory=dict)
    query_type_distribution: dict[str, int] = field(default_factory=dict)
    rerank_rate: float = 0.0
    period_days: int = 7


class MetricsCollector:
    """Collect and persist RAG metrics."""

    def __init__(self, log_path: str = "logs/rag_metrics.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record_search(
        self,
        query: str,
        strategy: str,
        results: list,
        latency_ms: int,
        query_type: str | None = None,
        reranked: bool = False,
        ticker: str | None = None,
        expanded_queries: int = 0,
    ) -> SearchMetrics:
        """Record a search operation."""
        # Get top similarity safely
        top_similarity = None
        if results:
            if hasattr(results[0], "similarity"):
                top_similarity = results[0].similarity
            elif isinstance(results[0], dict):
                top_similarity = results[0].get("similarity")

        metrics = SearchMetrics(
            query=query,
            query_type=query_type,
            strategy=strategy,
            retrieval_count=len(results),
            reranked=reranked,
            top_similarity=top_similarity,
            latency_ms=latency_ms,
            timestamp=datetime.now(UTC).isoformat(),
            ticker=ticker,
            expanded_queries=expanded_queries,
        )
        self._persist(metrics)
        return metrics

    def _persist(self, metrics: SearchMetrics) -> None:
        """Append metrics to JSONL log."""
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(asdict(metrics)) + "\n")
        except Exception as e:
            log.warning(f"Failed to persist metrics: {e}")

    def get_summary(self, days: int = 7) -> MetricsSummary:
        """Get summary statistics for recent searches."""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        total_searches = 0
        total_latency = 0
        total_results = 0
        total_similarity = 0
        similarity_count = 0
        rerank_count = 0
        strategy_dist: dict[str, int] = {}
        query_type_dist: dict[str, int] = {}

        if not self.log_path.exists():
            return MetricsSummary(period_days=days)

        try:
            with open(self.log_path) as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("timestamp", "") < cutoff_str:
                            continue

                        total_searches += 1
                        total_latency += entry.get("latency_ms", 0)
                        total_results += entry.get("retrieval_count", 0)

                        if entry.get("top_similarity") is not None:
                            total_similarity += entry["top_similarity"]
                            similarity_count += 1

                        if entry.get("reranked"):
                            rerank_count += 1

                        strategy = entry.get("strategy", "unknown")
                        strategy_dist[strategy] = strategy_dist.get(strategy, 0) + 1

                        qtype = entry.get("query_type") or "unclassified"
                        query_type_dist[qtype] = query_type_dist.get(qtype, 0) + 1

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            log.warning(f"Failed to read metrics: {e}")
            return MetricsSummary(period_days=days)

        return MetricsSummary(
            total_searches=total_searches,
            avg_latency_ms=total_latency / total_searches if total_searches else 0,
            avg_results=total_results / total_searches if total_searches else 0,
            avg_top_similarity=total_similarity / similarity_count if similarity_count else 0,
            strategy_distribution=strategy_dist,
            query_type_distribution=query_type_dist,
            rerank_rate=rerank_count / total_searches if total_searches else 0,
            period_days=days,
        )

    def get_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent search metrics."""
        if not self.log_path.exists():
            return []

        entries = []
        try:
            with open(self.log_path) as f:
                for line in f:
                    try:
                        entries.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            log.warning(f"Failed to read metrics: {e}")
            return []

        return entries[-limit:]


# Singleton
_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get singleton metrics collector."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


def record_search(
    query: str,
    strategy: str,
    results: list,
    latency_ms: int,
    **kwargs,
) -> SearchMetrics:
    """Convenience function to record search metrics."""
    return get_metrics_collector().record_search(
        query=query,
        strategy=strategy,
        results=results,
        latency_ms=latency_ms,
        **kwargs,
    )
