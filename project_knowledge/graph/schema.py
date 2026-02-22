"""Neo4j schema initialization and management."""

import logging

from .exceptions import SchemaError
from .layer import TradingGraph

log = logging.getLogger(__name__)


def init_schema(graph: TradingGraph | None = None) -> None:
    """
    Initialize Neo4j schema from schema file.

    Args:
        graph: Optional TradingGraph instance. Creates new one if not provided.
    """
    if graph:
        graph.init_schema()
    else:
        with TradingGraph() as g:
            g.init_schema()


def reset_schema(graph: TradingGraph | None = None, confirm: bool = False) -> None:
    """
    Reset (drop all data from) the graph database.

    Args:
        graph: Optional TradingGraph instance.
        confirm: Must be True to proceed with reset.
    """
    if not confirm:
        raise SchemaError("Must set confirm=True to reset schema")

    if graph:
        graph.reset_schema()
    else:
        with TradingGraph() as g:
            g.reset_schema()


def get_schema_version() -> str:
    """Get current schema version from graph metadata."""
    try:
        with TradingGraph() as g:
            result = g.run_cypher(
                "MATCH (m:_Metadata {key: 'schema_version'}) RETURN m.value AS version"
            )
            if result:
                return result[0]["version"]
    except Exception:
        pass
    return "unknown"


def set_schema_version(version: str) -> None:
    """Set schema version in graph metadata."""
    with TradingGraph() as g:
        g.run_cypher(
            """
            MERGE (m:_Metadata {key: 'schema_version'})
            SET m.value = $version
            """,
            {"version": version},
        )


def verify_schema() -> dict:
    """
    Verify that schema is properly initialized.

    Returns:
        dict with verification results
    """
    results = {
        "constraints": [],
        "indexes": [],
        "missing": [],
    }

    expected_constraints = [
        "ticker_symbol",
        "company_name",
        "sector_name",
        "industry_name",
        "product_name",
        "strategy_name",
        "pattern_name",
        "bias_name",
        "analysis_id",
        "trade_id",
        "document_id",
    ]

    try:
        with TradingGraph() as g:
            # Get existing constraints
            constraint_result = g.run_cypher("SHOW CONSTRAINTS")
            existing_constraints = [c.get("name", "") for c in constraint_result]

            results["constraints"] = existing_constraints

            for expected in expected_constraints:
                if expected not in existing_constraints:
                    results["missing"].append(f"constraint:{expected}")

            # Get existing indexes
            index_result = g.run_cypher("SHOW INDEXES")
            results["indexes"] = [i.get("name", "") for i in index_result]

    except Exception as e:
        results["error"] = str(e)

    return results
