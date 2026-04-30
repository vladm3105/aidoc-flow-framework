"""Query classification for agentic RAG routing.

Classifies queries to determine optimal retrieval strategy:
- RETRIEVAL: Standard semantic similarity search
- RELATIONSHIP: Graph traversal for entity relationships
- TREND: Time-filtered search for historical patterns
- COMPARISON: Multi-ticker comparison queries
- GLOBAL: Cross-document aggregation queries

Inspired by Memgraph's Agentic GraphRAG architecture.
"""

import re
from dataclasses import dataclass
from enum import Enum


class QueryType(Enum):
    """Query types for routing decisions."""

    RETRIEVAL = "retrieval"  # Semantic similarity search
    RELATIONSHIP = "relationship"  # Graph traversal needed
    TREND = "trend"  # Time-series, historical patterns
    COMPARISON = "comparison"  # Multi-ticker comparison
    GLOBAL = "global"  # Cross-document aggregation


@dataclass
class QueryAnalysis:
    """Result of query classification."""

    query_type: QueryType
    confidence: float  # 0.0 - 1.0
    tickers: list[str]  # Extracted ticker symbols
    time_constraint: str | None  # "recent", "Q4-2024", etc.
    suggested_strategy: str  # "vector", "hybrid", "graph", "combined"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query_type": self.query_type.value,
            "confidence": round(self.confidence, 2),
            "tickers": self.tickers,
            "time_constraint": self.time_constraint,
            "suggested_strategy": self.suggested_strategy,
        }


class QueryClassifier:
    """
    Rule-based query classifier with pattern matching.

    Analyzes query text to determine:
    1. Query type (retrieval, relationship, trend, etc.)
    2. Confidence score based on pattern matches
    3. Extracted entities (tickers, time constraints)
    4. Suggested retrieval strategy
    """

    # Pattern definitions for each query type
    RELATIONSHIP_PATTERNS = [
        r"relat(ed|ionship|e)",
        r"connect(ed|ion|s)",
        r"compet(e|itor|ition|ing)",
        r"supplier|customer|partner",
        r"peer|sector|industry",
        r"link|chain|network",
        r"who (supplies|buys|works with)",
        r"supply chain",
    ]

    TREND_PATTERNS = [
        r"trend|pattern|history",
        r"over time|historical|past",
        r"last \d+ (day|week|month|quarter|year)",
        r"Q[1-4](-?20\d{2})?",
        r"FY\d{2,4}",
        r"YoY|QoQ|MoM",
        r"recent|latest|newest",
        r"since|before|after",
        r"growth|decline|change",
    ]

    COMPARISON_PATTERNS = [
        r"\bvs\.?\b|\bversus\b",
        r"compar(e|ison|ing|ed)",
        r"better|worse|stronger|weaker",
        r"which (is|one|stock|company)",
        r"differ(ence|ent)",
        r"(\w{1,5})\s+(and|or|vs)\s+(\w{1,5})",  # NVDA vs AMD
        r"between .+ and",
    ]

    GLOBAL_PATTERNS = [
        r"\ball\b|\bevery\b|\bentire\b",
        r"across|portfolio|watchlist",
        r"summary|overview|aggregate",
        r"how many|count|total",
        r"average|mean|median",
        r"list (all|my)|show (all|every)",
    ]

    # Common financial ticker patterns (to avoid false positives)
    TICKER_PATTERN = re.compile(r"\b[A-Z]{1,5}\b")
    COMMON_WORDS = {
        "I",
        "A",
        "THE",
        "AND",
        "OR",
        "VS",
        "FOR",
        "IN",
        "ON",
        "AT",
        "TO",
        "OF",
        "IS",
        "IT",
        "BY",
        "AS",
        "BE",
        "IF",
        "SO",
        "UP",
        "MY",
        "ALL",
        "HOW",
        "WHO",
        "WHY",
        "EPS",
        "PE",
        "PB",
        "ROE",
        "ROA",
        "YOY",
        "QOQ",
        "MOM",
        "IPO",
        "CEO",
        "CFO",
        "CTO",
        "ETF",
        "SEC",
        "FDA",
        "FED",
        "GDP",
        "CPI",
        "PPI",
    }

    def classify(self, query: str) -> QueryAnalysis:
        """
        Classify query and suggest retrieval strategy.

        Args:
            query: User's search query

        Returns:
            QueryAnalysis with type, confidence, and suggested strategy
        """
        query_lower = query.lower()

        # Extract potential tickers
        tickers = self._extract_tickers(query)

        # Score each query type
        scores = {
            QueryType.RELATIONSHIP: self._pattern_score(
                query_lower, self.RELATIONSHIP_PATTERNS
            ),
            QueryType.TREND: self._pattern_score(query_lower, self.TREND_PATTERNS),
            QueryType.COMPARISON: self._pattern_score(
                query_lower, self.COMPARISON_PATTERNS
            ),
            QueryType.GLOBAL: self._pattern_score(query_lower, self.GLOBAL_PATTERNS),
            QueryType.RETRIEVAL: 0.3,  # Default baseline
        }

        # Boost comparison if multiple tickers detected
        if len(tickers) >= 2:
            scores[QueryType.COMPARISON] = max(scores[QueryType.COMPARISON], 0.6)

        # Boost retrieval if no strong signals
        max_score = max(scores.values())
        if max_score < 0.5:
            scores[QueryType.RETRIEVAL] = 0.6

        # Determine winning type
        query_type = max(scores, key=scores.get)
        confidence = scores[query_type]

        # Select retrieval strategy
        strategy = self._select_strategy(query_type, len(tickers))

        # Extract time constraint
        time_constraint = self._extract_time_constraint(query_lower)

        return QueryAnalysis(
            query_type=query_type,
            confidence=confidence,
            tickers=tickers,
            time_constraint=time_constraint,
            suggested_strategy=strategy,
        )

    def _pattern_score(self, text: str, patterns: list[str]) -> float:
        """
        Score based on pattern matches.

        Each pattern match adds 0.25, capped at 1.0.
        """
        matches = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
        return min(matches * 0.25, 1.0)

    def _select_strategy(self, query_type: QueryType, ticker_count: int) -> str:
        """
        Select retrieval strategy based on query type.

        Returns one of: "vector", "hybrid", "graph", "combined"
        """
        if query_type == QueryType.RELATIONSHIP:
            return "graph"
        elif query_type == QueryType.COMPARISON:
            return "graph" if ticker_count >= 2 else "hybrid"
        elif query_type == QueryType.TREND:
            return "vector"  # Time-filtered vector search
        elif query_type == QueryType.GLOBAL:
            return "hybrid"  # Needs both keyword and semantic
        else:
            return "hybrid"  # Default to hybrid for best coverage

    def _extract_tickers(self, query: str) -> list[str]:
        """
        Extract potential ticker symbols from query.

        Filters out common words and financial abbreviations.
        """
        candidates = self.TICKER_PATTERN.findall(query)
        return [t for t in candidates if t not in self.COMMON_WORDS and len(t) >= 2]

    def _extract_time_constraint(self, query: str) -> str | None:
        """Extract time constraints from query."""
        # Check for relative time
        if re.search(r"recent|latest|newest|last week|this month", query):
            return "recent"

        # Check for quarter reference
        quarter_match = re.search(r"Q[1-4][-\s]?(20\d{2})?", query, re.IGNORECASE)
        if quarter_match:
            return quarter_match.group().upper()

        # Check for fiscal year
        fy_match = re.search(r"FY\s?(\d{2,4})", query, re.IGNORECASE)
        if fy_match:
            return f"FY{fy_match.group(1)}"

        # Check for specific time ranges
        if re.search(r"last \d+ (day|week|month|quarter|year)", query):
            return re.search(r"last \d+ (day|week|month|quarter|year)", query).group()

        return None


# =============================================================================
# Singleton Management
# =============================================================================

_classifier: QueryClassifier | None = None


def get_classifier() -> QueryClassifier:
    """Get singleton classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = QueryClassifier()
    return _classifier


def classify_query(query: str) -> QueryAnalysis:
    """
    Convenience function to classify a query.

    Args:
        query: User's search query

    Returns:
        QueryAnalysis with classification results
    """
    return get_classifier().classify(query)
