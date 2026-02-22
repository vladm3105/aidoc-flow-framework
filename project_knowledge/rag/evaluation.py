"""RAG evaluation using RAGAS framework.

Provides metrics to evaluate RAG quality:
- context_precision: How relevant is retrieved context?
- context_recall: Did we retrieve all relevant context?
- faithfulness: Is the answer grounded in context?
- answer_relevancy: Does the answer address the query?

Reference: https://docs.ragas.io/
"""

import logging
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class RAGEvalResult:
    """Evaluation result for a single RAG response."""

    query: str
    context_precision: float  # 0.0 - 1.0
    context_recall: float  # 0.0 - 1.0
    faithfulness: float  # 0.0 - 1.0
    answer_relevancy: float  # 0.0 - 1.0
    overall_score: float  # Weighted average

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "context_precision": round(self.context_precision, 4),
            "context_recall": round(self.context_recall, 4),
            "faithfulness": round(self.faithfulness, 4),
            "answer_relevancy": round(self.answer_relevancy, 4),
            "overall_score": round(self.overall_score, 4),
        }


@dataclass
class RAGEvalSummary:
    """Aggregate evaluation metrics."""

    sample_count: int
    avg_context_precision: float
    avg_context_recall: float
    avg_faithfulness: float
    avg_answer_relevancy: float
    avg_overall_score: float

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "sample_count": self.sample_count,
            "avg_context_precision": round(self.avg_context_precision, 4),
            "avg_context_recall": round(self.avg_context_recall, 4),
            "avg_faithfulness": round(self.avg_faithfulness, 4),
            "avg_answer_relevancy": round(self.avg_answer_relevancy, 4),
            "avg_overall_score": round(self.avg_overall_score, 4),
        }


class RAGEvaluator:
    """
    Evaluate RAG quality using RAGAS metrics.

    RAGAS (Retrieval-Augmented Generation Assessment) provides
    reference-free evaluation using LLMs to assess quality.

    Metrics:
    - context_precision: Ranking quality of retrieved context
    - context_recall: Coverage of relevant information
    - faithfulness: Factual accuracy of generated answer
    - answer_relevancy: How well answer addresses the query
    """

    def __init__(self):
        self._ragas = None
        self._metrics = None

    @property
    def ragas(self):
        """Lazy-load RAGAS components."""
        if self._ragas is None:
            try:
                from ragas import evaluate
                from ragas.metrics import (
                    answer_relevancy,
                    context_precision,
                    context_recall,
                    faithfulness,
                )

                self._ragas = evaluate
                self._metrics = [
                    context_precision,
                    context_recall,
                    faithfulness,
                    answer_relevancy,
                ]
                log.info("RAGAS evaluation framework loaded")
            except ImportError:
                log.warning(
                    "RAGAS not installed. Install with: pip install ragas datasets"
                )
                return None
            except Exception as e:
                log.warning(f"Failed to load RAGAS: {e}")
                return None
        return self._ragas

    def evaluate_single(
        self,
        query: str,
        contexts: list[str],
        answer: str,
        ground_truth: str | None = None,
    ) -> RAGEvalResult | None:
        """
        Evaluate a single RAG response.

        Args:
            query: User's question
            contexts: Retrieved context chunks
            answer: Generated answer
            ground_truth: Optional ground truth answer

        Returns:
            RAGEvalResult or None if RAGAS unavailable
        """
        if self.ragas is None:
            return None

        try:
            from datasets import Dataset

            # Build dataset
            data = {
                "question": [query],
                "contexts": [contexts],
                "answer": [answer],
            }
            if ground_truth:
                data["ground_truth"] = [ground_truth]

            dataset = Dataset.from_dict(data)

            # Run evaluation
            result = self.ragas(
                dataset,
                metrics=self._metrics,
            )

            # Extract scores
            return RAGEvalResult(
                query=query,
                context_precision=float(result.get("context_precision", 0) or 0),
                context_recall=float(result.get("context_recall", 0) or 0),
                faithfulness=float(result.get("faithfulness", 0) or 0),
                answer_relevancy=float(result.get("answer_relevancy", 0) or 0),
                overall_score=float(result.get("ragas_score", 0) or 0),
            )

        except Exception as e:
            log.error(f"RAGAS evaluation failed: {e}")
            return None

    def evaluate_batch(
        self,
        samples: list[dict[str, Any]],
    ) -> RAGEvalSummary | None:
        """
        Evaluate a batch of RAG responses.

        Each sample should have:
        - query: str
        - contexts: list[str]
        - answer: str
        - ground_truth: str (optional)

        Args:
            samples: List of sample dictionaries

        Returns:
            RAGEvalSummary with aggregate metrics
        """
        if self.ragas is None or not samples:
            return None

        try:
            from datasets import Dataset

            # Build dataset
            data = {
                "question": [s["query"] for s in samples],
                "contexts": [s["contexts"] for s in samples],
                "answer": [s["answer"] for s in samples],
            }

            # Add ground truth if available
            if all("ground_truth" in s for s in samples):
                data["ground_truth"] = [s["ground_truth"] for s in samples]

            dataset = Dataset.from_dict(data)

            # Run evaluation
            result = self.ragas(
                dataset,
                metrics=self._metrics,
            )

            return RAGEvalSummary(
                sample_count=len(samples),
                avg_context_precision=float(result.get("context_precision", 0) or 0),
                avg_context_recall=float(result.get("context_recall", 0) or 0),
                avg_faithfulness=float(result.get("faithfulness", 0) or 0),
                avg_answer_relevancy=float(result.get("answer_relevancy", 0) or 0),
                avg_overall_score=float(result.get("ragas_score", 0) or 0),
            )

        except Exception as e:
            log.error(f"RAGAS batch evaluation failed: {e}")
            return None

    def is_available(self) -> bool:
        """Check if RAGAS is available."""
        return self.ragas is not None


# =============================================================================
# Singleton Management
# =============================================================================

_evaluator: RAGEvaluator | None = None


def get_evaluator() -> RAGEvaluator:
    """Get singleton evaluator instance."""
    global _evaluator
    if _evaluator is None:
        _evaluator = RAGEvaluator()
    return _evaluator


def evaluate_rag(
    query: str,
    contexts: list[str],
    answer: str,
    ground_truth: str | None = None,
) -> RAGEvalResult | None:
    """
    Convenience function to evaluate a RAG response.

    Args:
        query: User's question
        contexts: Retrieved context chunks
        answer: Generated answer
        ground_truth: Optional ground truth answer

    Returns:
        RAGEvalResult or None if RAGAS unavailable
    """
    return get_evaluator().evaluate_single(query, contexts, answer, ground_truth)


def is_ragas_available() -> bool:
    """Check if RAGAS evaluation is available."""
    return get_evaluator().is_available()
