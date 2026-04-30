"""Combined vector + graph context builder.

Provides hybrid RAG context by combining:
- Vector search (semantic similarity)
- Graph search (structural relationships)
- Adaptive routing based on query classification
"""

import logging
from pathlib import Path

import yaml

from .models import HybridContext, SearchResult
from .search import get_learnings_for_topic, get_similar_analyses, semantic_search

log = logging.getLogger(__name__)

# Load config for feature flags
_config_path = Path(__file__).parent / "config.yaml"
_config: dict = {}
if _config_path.exists():
    with open(_config_path) as f:
        _config = yaml.safe_load(f) or {}

_features = _config.get("features", {})
ADAPTIVE_RETRIEVAL_ENABLED = _features.get("adaptive_retrieval", True)


def get_hybrid_context(
    ticker: str,
    query: str,
    analysis_type: str | None = None,
    exclude_doc_id: str | None = None,
) -> HybridContext:
    """
    Combine vector search + graph context for Claude.

    Steps:
    1. Vector search: past analyses for this ticker
    2. Vector search: similar analyses for peer tickers (from graph)
    3. Vector search: relevant learnings and biases
    4. Graph search: structural context (peers, competitors, risks, strategies)
    5. Format into context block

    Args:
        ticker: Ticker symbol
        query: Search query
        analysis_type: Optional analysis type filter
        exclude_doc_id: Document ID to exclude (prevents self-retrieval)

    Returns:
        HybridContext with combined results
    """
    ticker = ticker.upper()

    # Vector search results
    vector_results = []

    # Track excluded doc_id to prevent self-retrieval
    excluded_ids = {exclude_doc_id} if exclude_doc_id else set()

    # 1. Past analyses for this ticker
    ticker_results = get_similar_analyses(ticker, analysis_type, top_k=3)
    for r in ticker_results:
        if r.doc_id not in excluded_ids:
            vector_results.append(r)

    # 2. Query-based search
    query_results = semantic_search(
        query=query,
        ticker=ticker,
        top_k=3,
    )
    # Dedupe against ticker results and excluded docs
    seen_ids = {r.doc_id for r in vector_results} | excluded_ids
    for r in query_results:
        if r.doc_id not in seen_ids:
            vector_results.append(r)
            seen_ids.add(r.doc_id)

    # 3. Relevant learnings
    learning_results = get_learnings_for_topic(query, top_k=2)
    for r in learning_results:
        if r.doc_id not in seen_ids:
            vector_results.append(r)
            seen_ids.add(r.doc_id)

    # 4. Graph context (import here to avoid circular dependency)
    graph_context = {}
    try:
        from ucx_knowledge.graph.layer import TradingGraph
        with TradingGraph() as graph:
            if graph.health_check():
                graph_context = graph.get_ticker_context(ticker)
    except Exception as e:
        log.warning(f"Graph context unavailable: {e}")

    # 5. Format combined context
    formatted = format_context(vector_results, graph_context, ticker)

    return HybridContext(
        ticker=ticker,
        vector_results=vector_results,
        graph_context=graph_context,
        formatted=formatted,
    )


def get_hybrid_context_adaptive(
    ticker: str,
    query: str,
    analysis_type: str | None = None,
    exclude_doc_id: str | None = None,
) -> HybridContext:
    """
    Adaptive hybrid context using query classification.

    Routes to optimal retrieval strategy based on query type:
    - RETRIEVAL: Standard vector search
    - RELATIONSHIP: Graph-first, then related tickers
    - COMPARISON: Multi-ticker search via graph peers
    - TREND: Time-filtered search
    - GLOBAL: Broad hybrid search

    Args:
        ticker: Ticker symbol
        query: Search query
        analysis_type: Optional analysis type filter
        exclude_doc_id: Document ID to exclude

    Returns:
        HybridContext with combined results
    """
    from .query_classifier import QueryType, classify_query

    ticker = ticker.upper()
    analysis = classify_query(query)

    log.debug(
        f"Query classified as {analysis.query_type.value} "
        f"(confidence: {analysis.confidence:.2f}, strategy: {analysis.suggested_strategy})"
    )

    vector_results = []
    excluded_ids = {exclude_doc_id} if exclude_doc_id else set()
    seen_ids = set(excluded_ids)

    # Get graph context first (needed for some strategies)
    graph_context = _get_graph_context(ticker)

    # Route based on query type and suggested strategy
    if analysis.suggested_strategy == "graph":
        # Graph-first: search across related tickers
        vector_results = _graph_first_retrieval(
            ticker, query, analysis_type, graph_context, seen_ids
        )

    elif analysis.query_type == QueryType.COMPARISON and len(analysis.tickers) >= 2:
        # Multi-ticker comparison: search each ticker
        vector_results = _comparison_retrieval(
            analysis.tickers, query, analysis_type, seen_ids
        )

    elif analysis.query_type == QueryType.TREND:
        # Trend queries: use time-filtered search
        vector_results = _trend_retrieval(
            ticker, query, analysis_type, analysis.time_constraint, seen_ids
        )

    else:
        # Default: use reranking if available
        vector_results = _default_retrieval(
            ticker, query, analysis_type, seen_ids
        )

    # Always add learnings
    learning_results = get_learnings_for_topic(query, top_k=2)
    for r in learning_results:
        if r.doc_id not in seen_ids:
            vector_results.append(r)
            seen_ids.add(r.doc_id)

    # Format combined context
    formatted = format_context(vector_results, graph_context, ticker)

    return HybridContext(
        ticker=ticker,
        vector_results=vector_results,
        graph_context=graph_context,
        formatted=formatted,
    )


def _get_graph_context(ticker: str) -> dict:
    """Get graph context for a ticker."""
    graph_context = {}
    try:
        from ucx_knowledge.graph.layer import TradingGraph
        with TradingGraph() as graph:
            if graph.health_check():
                graph_context = graph.get_ticker_context(ticker)
    except Exception as e:
        log.debug(f"Graph context unavailable: {e}")
    return graph_context


def _extract_related_tickers(graph_context: dict) -> list[str]:
    """Extract related ticker symbols from graph context."""
    related = []

    # Get peers
    for peer in graph_context.get("peers", []):
        if isinstance(peer, dict):
            symbol = peer.get("peer") or peer.get("symbol")
            if symbol:
                related.append(symbol)
        elif isinstance(peer, str):
            related.append(peer)

    # Get competitors
    for comp in graph_context.get("competitors", []):
        if isinstance(comp, dict):
            symbol = comp.get("competitor") or comp.get("symbol")
            if symbol:
                related.append(symbol)
        elif isinstance(comp, str):
            related.append(comp)

    return [t for t in related if t]


def _graph_first_retrieval(
    ticker: str,
    query: str,
    analysis_type: str | None,
    graph_context: dict,
    seen_ids: set,
) -> list[SearchResult]:
    """Graph-first retrieval: search primary ticker and related tickers."""
    results = []

    # Get related tickers from graph
    related_tickers = _extract_related_tickers(graph_context)

    # Search primary ticker and top 3 related
    tickers_to_search = [ticker] + related_tickers[:3]

    for t in tickers_to_search:
        ticker_results = get_similar_analyses(t, analysis_type, top_k=2)
        for r in ticker_results:
            if r.doc_id not in seen_ids:
                results.append(r)
                seen_ids.add(r.doc_id)

    return results


def _comparison_retrieval(
    tickers: list[str],
    query: str,
    analysis_type: str | None,
    seen_ids: set,
) -> list[SearchResult]:
    """Multi-ticker comparison retrieval."""
    results = []

    for ticker in tickers[:4]:  # Limit to 4 tickers
        ticker_results = get_similar_analyses(ticker.upper(), analysis_type, top_k=2)
        for r in ticker_results:
            if r.doc_id not in seen_ids:
                results.append(r)
                seen_ids.add(r.doc_id)

    return results


def _trend_retrieval(
    ticker: str,
    query: str,
    analysis_type: str | None,
    time_constraint: str | None,
    seen_ids: set,
) -> list[SearchResult]:
    """Time-aware retrieval for trend queries."""
    from datetime import date, timedelta

    # Determine date filter based on time constraint
    date_from = None
    if time_constraint == "recent":
        date_from = date.today() - timedelta(days=30)
    elif time_constraint and time_constraint.startswith("last"):
        # Parse "last N days/weeks/months"
        import re

        match = re.search(r"last (\d+) (day|week|month)", time_constraint)
        if match:
            n = int(match.group(1))
            unit = match.group(2)
            if unit == "day":
                date_from = date.today() - timedelta(days=n)
            elif unit == "week":
                date_from = date.today() - timedelta(weeks=n)
            elif unit == "month":
                date_from = date.today() - timedelta(days=n * 30)

    # Search with date filter
    results = semantic_search(
        query=query,
        ticker=ticker,
        doc_type=analysis_type,
        date_from=date_from,
        top_k=5,
    )

    return [r for r in results if r.doc_id not in seen_ids]


def _default_retrieval(
    ticker: str,
    query: str,
    analysis_type: str | None,
    seen_ids: set,
) -> list[SearchResult]:
    """Default retrieval with reranking if available."""
    results = []

    # Try reranked search first
    try:
        from .search import search_with_rerank

        reranked_results = search_with_rerank(
            query=query,
            ticker=ticker,
            doc_type=analysis_type,
            top_k=5,
        )
        for r in reranked_results:
            if r.doc_id not in seen_ids:
                results.append(r)
                seen_ids.add(r.doc_id)
    except Exception as e:
        log.debug(f"Reranking unavailable: {e}, using standard search")

        # Fallback to standard search
        ticker_results = get_similar_analyses(ticker, analysis_type, top_k=3)
        for r in ticker_results:
            if r.doc_id not in seen_ids:
                results.append(r)
                seen_ids.add(r.doc_id)

        query_results = semantic_search(query=query, ticker=ticker, top_k=3)
        for r in query_results:
            if r.doc_id not in seen_ids:
                results.append(r)
                seen_ids.add(r.doc_id)

    return results


def build_analysis_context(ticker: str, analysis_type: str) -> str:
    """
    Build pre-analysis context for Claude skills.

    Includes:
    - Past analyses for this ticker (top 3)
    - Similar analyses for peer tickers (top 2)
    - Relevant learnings (top 3)
    - Graph structural context

    Args:
        ticker: Ticker symbol
        analysis_type: Type of analysis being performed

    Returns:
        Formatted context string
    """
    context = get_hybrid_context(
        ticker=ticker,
        query=f"{analysis_type} for {ticker}",
        analysis_type=analysis_type,
    )
    return context.formatted


def format_context(
    vector_results: list[SearchResult],
    graph_context: dict,
    ticker: str,
) -> str:
    """Format hybrid context as markdown for Claude."""
    sections = []

    # Header
    sections.append(f"## Context for {ticker}\n")

    # Graph context
    if graph_context:
        graph_sections = []

        # Check for empty graph status
        if graph_context.get("_status") == "empty":
            sections.append("### Knowledge Graph\n")
            sections.append("*Graph context unavailable - no data indexed yet.*")
            sections.append(f"*Tip: {graph_context.get('_message', 'Run graph extraction on analysis documents')}*")
            sections.append("")
        else:
            # Peers
            peers = graph_context.get("peers", [])
            if peers:
                peer_list = ", ".join([p.get("peer", "") for p in peers[:5]])
                graph_sections.append(f"**Sector Peers**: {peer_list}")

            # Competitors
            competitors = graph_context.get("competitors", [])
            if competitors:
                comp_list = ", ".join([c.get("competitor", "") for c in competitors[:5]])
                graph_sections.append(f"**Competitors**: {comp_list}")

            # Risks
            risks = graph_context.get("risks", [])
            if risks:
                risk_list = ", ".join([r.get("risk", "") for r in risks[:5]])
                graph_sections.append(f"**Known Risks**: {risk_list}")

            # Supply chain
            supply = graph_context.get("supply_chain", {})
            if supply.get("suppliers"):
                graph_sections.append(f"**Suppliers**: {', '.join(supply['suppliers'][:5])}")
            if supply.get("customers"):
                graph_sections.append(f"**Customers**: {', '.join(supply['customers'][:5])}")

            if graph_sections:
                sections.append("### Knowledge Graph\n")
                sections.append("\n".join(graph_sections))
                sections.append("")
            elif graph_context.get("symbol"):
                # Graph has data but nothing for this specific ticker
                sections.append("### Knowledge Graph\n")
                sections.append(f"*No relationships found for {ticker} in the knowledge graph.*")
                sections.append("")

    # Vector search results
    if vector_results:
        sections.append("### Past Analyses\n")

        for result in vector_results[:5]:
            sections.append(f"**{result.doc_id}** ({result.doc_type})")
            sections.append(f"*Section: {result.section_label}*")
            sections.append(f"Similarity: {result.similarity:.2f}")
            # Truncate content
            content = result.content[:500]
            if len(result.content) > 500:
                content += "..."
            sections.append(f"```\n{content}\n```")
            sections.append("")

    return "\n".join(sections)


def get_bias_warnings(ticker: str) -> list[dict]:
    """
    Get bias warnings for a ticker based on past trades.

    Args:
        ticker: Ticker symbol

    Returns:
        List of bias warnings with context
    """
    warnings = []

    try:
        from ucx_knowledge.graph.layer import TradingGraph
        with TradingGraph() as graph:
            # Skip queries if no Trade nodes exist (avoid label warnings on sparse graph)
            if graph.health_check() and graph.is_populated():
                # Check if Trade nodes exist before querying
                trade_check = graph.run_cypher(
                    "MATCH (t:Trade) RETURN count(t) AS cnt LIMIT 1", {}, _internal=True
                )
                if not trade_check:
                    return warnings  # No trades yet, return empty
                if "cnt" in trade_check[0] and trade_check[0].get("cnt", 0) == 0:
                    return warnings  # No trades yet, return empty

                # Get biases detected in trades for this ticker
                bias_history = graph.run_cypher(
                    """
                    MATCH (b:Bias)-[:DETECTED_IN]->(t:Trade)-[:TRADED]->(tk:Ticker {symbol: $symbol})
                    RETURN b.name AS bias, t.outcome AS outcome, count(*) AS occurrences
                    ORDER BY occurrences DESC
                """,
                    {"symbol": ticker.upper()},
                )

                for row in bias_history:
                    warnings.append(
                        {
                            "bias": row["bias"],
                            "occurrences": row["occurrences"],
                            "last_outcome": row["outcome"],
                        }
                    )

    except Exception as e:
        log.warning(f"Could not get bias warnings: {e}")

    return warnings


def get_strategy_recommendations(ticker: str) -> list[dict]:
    """
    Get strategy recommendations for a ticker based on historical performance.

    Args:
        ticker: Ticker symbol

    Returns:
        List of strategy recommendations
    """
    recommendations = []

    try:
        from ucx_knowledge.graph.layer import TradingGraph
        with TradingGraph() as graph:
            # Skip queries on empty graph to avoid label warnings
            if graph.health_check() and graph.is_populated():
                strategies = graph.run_cypher(
                    """
                    MATCH (s:Strategy)-[r:WORKS_FOR]->(tk:Ticker {symbol: $symbol})
                    WHERE r.sample_size >= 3
                    RETURN s.name AS strategy, r.win_rate AS win_rate, r.sample_size AS trades
                    ORDER BY r.win_rate DESC
                """,
                    {"symbol": ticker.upper()},
                )

                for row in strategies:
                    recommendations.append(
                        {
                            "strategy": row["strategy"],
                            "win_rate": row["win_rate"],
                            "trades": row["trades"],
                        }
                    )

    except Exception as e:
        log.warning(f"Could not get strategy recommendations: {e}")

    return recommendations
