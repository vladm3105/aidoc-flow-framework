"""Neo4j graph layer for trading knowledge."""

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable

from .exceptions import GraphUnavailableError, SchemaError
from .models import GraphStats

# Load .env file for credentials
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

log = logging.getLogger(__name__)

# Module-level flag to track if we've warned about empty graph
_empty_graph_warned = False


class TradingGraph:
    """Neo4j graph layer for trading knowledge."""

    def __init__(
        self,
        uri: str | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str = "neo4j",
    ):
        """Initialize connection parameters from config or args."""
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7688")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASS", "")
        self.database = database
        self._driver = None

    def __enter__(self) -> "TradingGraph":
        """Context manager entry - connect to Neo4j."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()

    def connect(self) -> None:
        """Establish Neo4j connection."""
        try:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
            )
            # Verify connection
            self._driver.verify_connectivity()
            log.debug(f"Connected to Neo4j at {self.uri}")
        except (ServiceUnavailable, AuthError) as e:
            raise GraphUnavailableError(f"Failed to connect to Neo4j: {e}")

    def close(self) -> None:
        """Close Neo4j connection."""
        if self._driver:
            self._driver.close()
            self._driver = None
            log.debug("Closed Neo4j connection")

    def health_check(self) -> bool:
        """Check if Neo4j is reachable."""
        try:
            if not self._driver:
                return False
            self._driver.verify_connectivity()
            return True
        except Exception:
            return False

    def is_populated(self) -> bool:
        """
        Check if the graph has any data.

        Returns True if at least one node exists in the graph.
        This is used to determine if queries will return useful context.
        """
        try:
            with self._driver.session(database=self.database) as session:
                # Simple count of all nodes - doesn't trigger label warnings
                result = session.run("MATCH (n) RETURN count(n) AS cnt LIMIT 1")
                record = result.single()
                return record and record["cnt"] > 0
        except Exception:
            return False

    def get_status(self) -> dict:
        """
        Get graph status summary for diagnostics.

        Returns:
            Dict with connection status, node counts, and population status
        """
        global _empty_graph_warned

        status = {
            "connected": False,
            "populated": False,
            "node_count": 0,
            "edge_count": 0,
            "message": "Unknown",
        }

        if not self.health_check():
            status["message"] = "Neo4j not reachable"
            return status

        status["connected"] = True

        try:
            with self._driver.session(database=self.database) as session:
                # Get total counts
                result = session.run("MATCH (n) RETURN count(n) AS nodes")
                record = result.single()
                status["node_count"] = record["nodes"] if record else 0

                result = session.run("MATCH ()-[r]->() RETURN count(r) AS edges")
                record = result.single()
                status["edge_count"] = record["edges"] if record else 0

            status["populated"] = status["node_count"] > 0

            if not status["populated"]:
                status["message"] = "Graph is empty - run 'python orchestrator.py graph init' and index some documents"
                if not _empty_graph_warned:
                    log.warning(f"Knowledge graph is empty. {status['message']}")
                    _empty_graph_warned = True
            else:
                status["message"] = f"Graph has {status['node_count']} nodes and {status['edge_count']} edges"

        except Exception as e:
            status["message"] = f"Error checking graph status: {e}"

        return status

    # --- Schema Management ---

    def init_schema(self) -> None:
        """Run all constraints and indexes from neo4j_schema.cypher."""
        schema_path = Path(__file__).parent.parent / "db" / "neo4j_schema.cypher"
        if not schema_path.exists():
            raise SchemaError(f"Schema file not found: {schema_path}")

        with open(schema_path) as f:
            schema_content = f.read()

        # Split into individual statements (skip comments and empty lines)
        statements = []
        current_stmt = []

        for line in schema_content.split("\n"):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            current_stmt.append(line)
            if line.endswith(";"):
                statements.append(" ".join(current_stmt))
                current_stmt = []

        # Execute each statement
        with self._driver.session(database=self.database) as session:
            for stmt in statements:
                try:
                    session.run(stmt)
                    log.debug(f"Executed: {stmt[:80]}...")
                except Exception as e:
                    # Ignore "already exists" errors
                    if "already exists" in str(e).lower():
                        continue
                    log.warning(f"Schema statement failed: {e}")

        log.info(f"Schema initialized with {len(statements)} statements")

    def reset_schema(self) -> None:
        """Drop all nodes and relationships (dev only)."""
        with self._driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
        log.warning("Graph reset: all nodes and relationships deleted")

    def migrate(self, target_version: str) -> None:
        """Run migration scripts to target version."""
        migrations_dir = Path(__file__).parent / "migrations"
        if not migrations_dir.exists():
            log.info("No migrations directory found")
            return

        # Find and execute migration scripts
        migration_files = sorted(migrations_dir.glob("*.cypher"))
        for migration_file in migration_files:
            log.info(f"Running migration: {migration_file.name}")
            with open(migration_file) as f:
                migration_content = f.read()
            with self._driver.session(database=self.database) as session:
                for stmt in migration_content.split(";"):
                    stmt = stmt.strip()
                    if stmt:
                        session.run(stmt)

    # --- Node Operations ---

    def merge_node(self, label: str, key_prop: str, props: dict) -> int | None:
        """
        MERGE node with properties. Returns node element ID.

        Example:
            merge_node("Ticker", "symbol", {"symbol": "NVDA", "name": "NVIDIA"})
        """
        query = f"""
        MERGE (n:{label} {{{key_prop}: $key_value}})
        SET n += $props
        RETURN elementId(n) as id
        """
        key_value = props.get(key_prop)
        if key_value is None:
            log.warning(f"Key property '{key_prop}' not in props: {props}")
            return None

        with self._driver.session(database=self.database) as session:
            result = session.run(query, key_value=key_value, props=props)
            record = result.single()
            return record["id"] if record else None

    def get_node(self, label: str, key_prop: str, key_value: Any) -> dict | None:
        """Get node by label and key property."""
        query = f"""
        MATCH (n:{label} {{{key_prop}: $key_value}})
        RETURN n
        """
        with self._driver.session(database=self.database) as session:
            result = session.run(query, key_value=key_value)
            record = result.single()
            return dict(record["n"]) if record else None

    # --- Relationship Operations ---

    def merge_relation(
        self,
        from_node: tuple[str, str, Any],  # (label, key_prop, key_value)
        rel_type: str,
        to_node: tuple[str, str, Any],
        props: dict | None = None,
    ) -> None:
        """
        MERGE relationship between nodes.

        Example:
            merge_relation(
                ("Company", "name", "NVIDIA"),
                "ISSUED",
                ("Ticker", "symbol", "NVDA")
            )
        """
        from_label, from_key, from_value = from_node
        to_label, to_key, to_value = to_node

        query = f"""
        MATCH (a:{from_label} {{{from_key}: $from_value}})
        MATCH (b:{to_label} {{{to_key}: $to_value}})
        MERGE (a)-[r:{rel_type}]->(b)
        """
        if props:
            query += " SET r += $props"

        with self._driver.session(database=self.database) as session:
            session.run(
                query,
                from_value=from_value,
                to_value=to_value,
                props=props or {},
            )

    # --- Query Operations ---

    def find_related(self, symbol: str, depth: int = 2) -> list[dict]:
        """Find all nodes within N hops of a ticker."""
        # Neo4j doesn't support parameterized relationship depth, so we use string formatting
        # Limit depth to prevent expensive queries (max 3 hops)
        safe_depth = min(max(1, depth), 3)
        query = f"""
        MATCH path = (t:Ticker {{symbol: $symbol}})-[*1..{safe_depth}]-(n)
        RETURN DISTINCT labels(n) as labels, properties(n) as props
        LIMIT 100
        """
        with self._driver.session(database=self.database) as session:
            result = session.run(query, symbol=symbol)
            return [{"labels": r["labels"], "props": r["props"]} for r in result]

    def get_sector_peers(self, symbol: str) -> list[dict]:
        """Get tickers in the same sector."""
        query = """
        MATCH (t1:Ticker {symbol: $symbol})<-[:ISSUED]-(c1:Company)-[:IN_SECTOR]->(s:Sector),
              (c2:Company)-[:IN_SECTOR]->(s), (c2)-[:ISSUED]->(t2:Ticker)
        WHERE t1 <> t2
        RETURN t2.symbol AS peer, c2.name AS company, s.name AS sector
        """
        with self._driver.session(database=self.database) as session:
            result = session.run(query, symbol=symbol)
            return [dict(r) for r in result]

    def get_competitors(self, symbol: str) -> list[dict]:
        """Get companies that compete with this ticker's company."""
        query = """
        MATCH (c1:Company)-[:ISSUED]->(t:Ticker {symbol: $symbol}),
              (c1)-[:COMPETES_WITH]-(c2:Company)-[:ISSUED]->(t2:Ticker)
        RETURN c2.name AS competitor, t2.symbol AS ticker
        """
        with self._driver.session(database=self.database) as session:
            result = session.run(query, symbol=symbol)
            return [dict(r) for r in result]

    def get_risks(self, symbol: str) -> list[dict]:
        """Get all risks threatening this ticker."""
        query = """
        MATCH (r:Risk)-[:THREATENS]->(t:Ticker {symbol: $symbol})
        RETURN r.name AS risk, COALESCE(r.description, '') AS description
        """
        with self._driver.session(database=self.database) as session:
            result = session.run(query, symbol=symbol)
            return [dict(r) for r in result]

    def get_bias_history(self, bias_name: str | None = None) -> list[dict]:
        """Get bias occurrences across trades.

        Returns empty list if no Trade nodes exist (sparse graph).
        """
        # Check if Trade nodes exist to avoid warning spam
        with self._driver.session(database=self.database) as session:
            check = session.run("MATCH (t:Trade) RETURN count(t) AS cnt LIMIT 1")
            record = check.single()
            if not record or record["cnt"] == 0:
                return []

        if bias_name:
            query = """
            MATCH (b:Bias {name: $bias_name})-[:DETECTED_IN]->(t:Trade)
            RETURN b.name AS bias, t.id AS trade_id, t.outcome AS outcome
            """
            params = {"bias_name": bias_name}
        else:
            query = """
            MATCH (b:Bias)-[:DETECTED_IN]->(t:Trade)
            RETURN b.name AS bias, count(t) AS occurrences
            ORDER BY occurrences DESC
            """
            params = {}

        with self._driver.session(database=self.database) as session:
            result = session.run(query, **params)
            return [dict(r) for r in result]

    def get_strategy_performance(self, strategy_name: str | None = None) -> list[dict]:
        """Get strategy win rates by ticker."""
        if strategy_name:
            query = """
            MATCH (s:Strategy {name: $strategy_name})-[r:WORKS_FOR]->(tk:Ticker)
            RETURN tk.symbol AS ticker, r.win_rate AS win_rate, r.sample_size AS sample_size
            ORDER BY r.win_rate DESC
            """
            params = {"strategy_name": strategy_name}
        else:
            query = """
            MATCH (s:Strategy)-[r:WORKS_FOR]->(tk:Ticker)
            RETURN s.name AS strategy, avg(r.win_rate) AS avg_win_rate, sum(r.sample_size) AS total_trades
            ORDER BY avg_win_rate DESC
            """
            params = {}

        with self._driver.session(database=self.database) as session:
            result = session.run(query, **params)
            return [dict(r) for r in result]

    def get_learning_loop(self, bias_name: str) -> list[dict]:
        """Bias → Trade → Learning path.

        Returns empty list if no Trade or Learning nodes exist (sparse graph).
        """
        # Check if Trade nodes exist to avoid warning spam
        with self._driver.session(database=self.database) as session:
            check = session.run("MATCH (t:Trade) RETURN count(t) AS cnt LIMIT 1")
            record = check.single()
            if not record or record["cnt"] == 0:
                return []

        query = """
        MATCH path = (b:Bias {name: $bias_name})-[:DETECTED_IN]->(t:Trade)<-[:DERIVED_FROM]-(l:Learning)
        RETURN b.name AS bias, t.id AS trade, l.id AS learning_id, l.rule AS lesson
        """
        with self._driver.session(database=self.database) as session:
            result = session.run(query, bias_name=bias_name)
            return [dict(r) for r in result]

    def get_supply_chain(self, symbol: str) -> list[dict]:
        """Get suppliers and customers for a company."""
        query = """
        MATCH (c1:Company)-[:ISSUED]->(t:Ticker {symbol: $symbol})
        OPTIONAL MATCH (c2:Company)-[:SUPPLIES_TO]->(c1)
        OPTIONAL MATCH (c3:Company)-[:CUSTOMER_OF]->(c1)
        RETURN collect(DISTINCT c2.name) AS suppliers, collect(DISTINCT c3.name) AS customers
        """
        with self._driver.session(database=self.database) as session:
            result = session.run(query, symbol=symbol)
            record = result.single()
            return (
                {
                    "suppliers": [s for s in record["suppliers"] if s],
                    "customers": [c for c in record["customers"] if c],
                }
                if record
                else {"suppliers": [], "customers": []}
            )

    def get_ticker_context(self, symbol: str) -> dict:
        """
        Get comprehensive context for a ticker:
        - Sector peers
        - Competitors
        - Known risks
        - Strategies that work
        - Past biases in trades

        Returns empty context with status message if graph is not populated.
        """
        # Check if graph has data before running queries (prevents noisy warnings)
        if not self.is_populated():
            status = self.get_status()
            return {
                "symbol": symbol,
                "peers": [],
                "competitors": [],
                "risks": [],
                "strategies": [],
                "supply_chain": {"suppliers": [], "customers": []},
                "_status": "empty",
                "_message": status.get("message", "Graph is empty"),
            }

        return {
            "symbol": symbol,
            "peers": self.get_sector_peers(symbol),
            "competitors": self.get_competitors(symbol),
            "risks": self.get_risks(symbol),
            "strategies": self.get_strategy_performance(),
            "supply_chain": self.get_supply_chain(symbol),
        }

    # Allowed Cypher query patterns for security validation
    # Only these patterns are permitted in run_cypher when called externally
    SAFE_QUERY_PATTERNS = frozenset(
        [
            # Read-only patterns
            "MATCH",
            "RETURN",
            "WHERE",
            "WITH",
            "ORDER BY",
            "LIMIT",
            "OPTIONAL MATCH",
            "UNION",
            "CALL",
        ]
    )

    DANGEROUS_KEYWORDS = frozenset(
        [
            "DELETE",
            "DETACH DELETE",
            "REMOVE",
            "DROP",
            "CREATE CONSTRAINT",
            "CREATE INDEX",
            "SET",  # Only dangerous without MERGE context
        ]
    )

    def _validate_cypher_query(self, query: str, allow_writes: bool = False) -> bool:
        """
        Validate Cypher query for security.

        Args:
            query: The Cypher query to validate
            allow_writes: If True, allow MERGE/CREATE operations

        Returns:
            True if query is safe, False otherwise
        """
        query_upper = query.upper().strip()

        # Check for dangerous keywords
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in query_upper:
                # Allow SET only after MERGE
                if keyword == "SET" and "MERGE" in query_upper:
                    continue
                if not allow_writes:
                    log.warning(f"Blocked dangerous Cypher keyword: {keyword}")
                    return False

        return True

    def run_cypher(
        self,
        query: str,
        params: dict | None = None,
        allow_writes: bool = False,
        _internal: bool = False,
    ) -> list[dict]:
        """
        Execute Cypher query with security validation.

        Args:
            query: Cypher query to execute
            params: Query parameters (use for all user-supplied values)
            allow_writes: Allow MERGE/CREATE operations (default: False)
            _internal: Skip validation for internal calls (default: False)

        Returns:
            List of result dictionaries

        Raises:
            ValueError: If query contains dangerous operations

        Security:
            - All user-supplied values MUST be passed via params
            - DELETE, DROP, REMOVE operations are blocked by default
            - Use _internal=True only for trusted internal operations
        """
        if not _internal and not self._validate_cypher_query(query, allow_writes):
            raise ValueError(
                "Query contains potentially dangerous operations. "
                "Use allow_writes=True for MERGE/CREATE or _internal=True for trusted queries."
            )

        with self._driver.session(database=self.database) as session:
            result = session.run(query, **(params or {}))
            return [dict(r) for r in result]

    # --- Maintenance ---

    def get_stats(self) -> GraphStats:
        """Get node/edge counts by type."""
        # Node counts
        node_query = """
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
        """
        # Edge counts
        edge_query = """
        MATCH ()-[r]->()
        RETURN type(r) AS relationship, count(r) AS count
        ORDER BY count DESC
        """
        # Last extraction
        # Use Document label (actual label used) instead of Analysis
        # Property is extracted_at (not created_at)
        last_extract_query = """
        MATCH (d:Document)
        RETURN max(d.extracted_at) AS last_extraction
        """

        with self._driver.session(database=self.database) as session:
            node_result = session.run(node_query)
            node_counts = {r["label"]: r["count"] for r in node_result if r["label"]}

            edge_result = session.run(edge_query)
            edge_counts = {r["relationship"]: r["count"] for r in edge_result if r["relationship"]}

            extract_result = session.run(last_extract_query)
            record = extract_result.single()
            last_extraction = record["last_extraction"] if record else None

        return GraphStats(
            node_counts=node_counts,
            edge_counts=edge_counts,
            total_nodes=sum(node_counts.values()),
            total_edges=sum(edge_counts.values()),
            last_extraction=last_extraction,
        )

    def prune_old(self, days: int = 365) -> int:
        """Archive Document nodes older than N days (relabel to :Archived)."""
        query = """
        MATCH (d:Document)
        WHERE d.extracted_at < datetime() - duration({days: $days})
        SET d:Archived
        REMOVE d:Document
        RETURN count(d) AS archived
        """
        with self._driver.session(database=self.database) as session:
            result = session.run(query, days=days)
            record = result.single()
            return record["archived"] if record else 0

    def dedupe_entities(self) -> int:
        """Merge duplicate entities based on normalization rules."""
        # This is a placeholder - full implementation would use APOC merge procedures
        log.info("Deduplication would run here (requires APOC procedures)")
        return 0

    def validate_constraints(self) -> list[str]:
        """Check for constraint violations."""
        issues = []
        # Check for orphaned nodes (Analysis without Ticker)
        orphan_query = """
        MATCH (a:Analysis)
        WHERE NOT (a)-[:ANALYZES]->(:Ticker)
        RETURN count(a) AS orphaned
        """
        with self._driver.session(database=self.database) as session:
            result = session.run(orphan_query)
            record = result.single()
            if record and record["orphaned"] > 0:
                issues.append(
                    f"Found {record['orphaned']} Analysis nodes without ANALYZES relationship"
                )

        return issues
