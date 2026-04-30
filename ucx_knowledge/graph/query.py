"""Preset query patterns for CLI commands."""

# Cypher query templates
QUERIES = {
    "biases_for_ticker": """
        MATCH (t:Trade)-[:TRADED]->(tk:Ticker {symbol: $symbol}),
              (b:Bias)-[:DETECTED_IN]->(t)
        RETURN b.name AS bias, count(t) AS occurrences
        ORDER BY occurrences DESC
    """,
    "strategies_for_earnings": """
        MATCH (s:Strategy)-[:WORKS_FOR]->(tk:Ticker),
              (tk)-[:AFFECTED_BY]->(c:Catalyst {type: 'earnings'})
        RETURN s.name AS strategy, collect(DISTINCT tk.symbol) AS tickers, count(*) AS uses
    """,
    "competitive_landscape": """
        MATCH (c1:Company)-[:ISSUED]->(t:Ticker {symbol: $symbol}),
              (c1)-[:COMPETES_WITH]-(c2:Company)-[:ISSUED]->(t2:Ticker)
        RETURN c2.name AS competitor, t2.symbol AS ticker
    """,
    "risks_open_positions": """
        MATCH (r:Risk)-[:THREATENS]->(tk:Ticker)<-[:TRADED]-(t:Trade)
        WHERE t.status = 'open'
        RETURN r.name AS risk, collect(DISTINCT tk.symbol) AS exposed_tickers
    """,
    "learning_loop": """
        MATCH path = (b:Bias)-[:DETECTED_IN]->(t:Trade)<-[:DERIVED_FROM]-(l:Learning)
        RETURN b.name AS bias, t.id AS trade, l.id AS learning_id, l.rule AS lesson
    """,
    "supply_chain": """
        MATCH (c1:Company)-[:ISSUED]->(t:Ticker {symbol: $symbol}),
              (c2:Company)-[:SUPPLIES_TO]->(c1)
        RETURN 'supplier' AS type, c2.name AS company
        UNION
        MATCH (c1:Company)-[:ISSUED]->(t:Ticker {symbol: $symbol}),
              (c2:Company)-[:CUSTOMER_OF]->(c1)
        RETURN 'customer' AS type, c2.name AS company
    """,
    "learnings_for_bias": """
        MATCH (b:Bias {name: $bias_name})<-[:ADDRESSES]-(l:Learning)
        RETURN l.id AS learning_id, l.rule AS rule, l.category AS category
    """,
    "sector_peers": """
        MATCH (t1:Ticker {symbol: $symbol})<-[:ISSUED]-(c1:Company)-[:IN_SECTOR]->(s:Sector),
              (c2:Company)-[:IN_SECTOR]->(s), (c2)-[:ISSUED]->(t2:Ticker)
        WHERE t1 <> t2
        RETURN t2.symbol AS peer, c2.name AS company, s.name AS sector
    """,
    "node_counts": """
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
    """,
    "edge_counts": """
        MATCH ()-[r]->()
        RETURN type(r) AS relationship, count(r) AS count
        ORDER BY count DESC
    """,
    "recent_extractions": """
        MATCH (d:Document)
        RETURN d.id AS doc_id, d.doc_type AS type, d.extracted_at AS extracted_at
        ORDER BY d.extracted_at DESC
        LIMIT 10
    """,
    "entities_needing_review": """
        MATCH (n)
        WHERE n.needs_review = true
        RETURN labels(n)[0] AS type, n.name AS name, n.symbol AS symbol
        LIMIT 50
    """,
    "pattern_by_ticker": """
        MATCH (p:Pattern)-[:OBSERVED_IN]->(t:Ticker {symbol: $symbol})
        RETURN p.name AS pattern, count(*) AS observations
        ORDER BY observations DESC
    """,
    "strategy_win_rates": """
        MATCH (s:Strategy)-[r:WORKS_FOR]->(t:Ticker)
        WHERE r.sample_size >= 3
        RETURN s.name AS strategy, t.symbol AS ticker,
               r.win_rate AS win_rate, r.sample_size AS trades
        ORDER BY r.win_rate DESC
    """,
    "catalyst_impact": """
        MATCH (c:Catalyst)-[:AFFECTED_BY]-(t:Ticker)
        RETURN c.type AS catalyst_type, collect(DISTINCT t.symbol) AS tickers, count(*) AS count
        ORDER BY count DESC
    """,
    "macro_exposure": """
        MATCH (m:MacroEvent)-[:EXPOSED_TO]-(t:Ticker)
        RETURN m.name AS event, collect(DISTINCT t.symbol) AS exposed_tickers
    """,
}


def get_query(name: str) -> str | None:
    """Get a preset query by name."""
    return QUERIES.get(name)


def list_queries() -> list[str]:
    """List all available preset query names."""
    return list(QUERIES.keys())


def run_preset_query(name: str, params: dict | None = None) -> list[dict]:
    """Run a preset query by name."""
    from .layer import TradingGraph

    query = get_query(name)
    if not query:
        raise ValueError(f"Unknown query: {name}")

    with TradingGraph() as graph:
        return graph.run_cypher(query, params or {})
