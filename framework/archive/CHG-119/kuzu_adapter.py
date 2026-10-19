"""Embedded Kùzu Acceleration Adapter for SDD Graphs.

Provides in-process, high-performance openCypher execution backed by Kùzu.
Governed by framework/governance/SDD_GRAPH_SCHEMA_SPECIFICATION.md and
docs/FEDERATED_READ_LAKE_PATTERN.md (CHG-110, GD-97).

Engine Neutrality (Decision D-0013):
Kùzu is an optional acceleration layer. If kuzu is not installed in the
Python environment, is_available() returns False and the framework operates
with zero degradation using pure-Python SddGraph graph traversals.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sdd_doc_lint.graph_engine import SddGraph

logger = logging.getLogger(__name__)

# Dynamic import guard for zero mandatory pip dependencies (Decision D-0013)
try:
    import kuzu

    KUZU_AVAILABLE = True
except ImportError:
    kuzu = None
    KUZU_AVAILABLE = False


# Canonical DDL for SDD Node Tables
NODE_TABLE_SCHEMAS: dict[str, str] = {
    "seed_intent": (
        "CREATE NODE TABLE IF NOT EXISTS seed_intent("
        "id STRING, title STRING, statement STRING, PRIMARY KEY (id))"
    ),
    "system_container": (
        "CREATE NODE TABLE IF NOT EXISTS system_container("
        "id STRING, title STRING, context STRING, "
        "container_archetype STRING, trust_boundary STRING, data_classification STRING, "
        "PRIMARY KEY (id))"
    ),
    "business_objective": (
        "CREATE NODE TABLE IF NOT EXISTS business_objective("
        "id STRING, title STRING, statement STRING, priority STRING, PRIMARY KEY (id))"
    ),
    "product_capability": (
        "CREATE NODE TABLE IF NOT EXISTS product_capability("
        "id STRING, title STRING, statement STRING, persona STRING, PRIMARY KEY (id))"
    ),
    "formal_requirement": (
        "CREATE NODE TABLE IF NOT EXISTS formal_requirement("
        "id STRING, title STRING, statement STRING, pattern STRING, PRIMARY KEY (id))"
    ),
    "acceptance_scenario": (
        "CREATE NODE TABLE IF NOT EXISTS acceptance_scenario("
        "id STRING, title STRING, given STRING, when_clause STRING, then_clause STRING, PRIMARY KEY (id))"
    ),
    "architectural_decision": (
        "CREATE NODE TABLE IF NOT EXISTS architectural_decision("
        "id STRING, title STRING, context STRING, decision STRING, status STRING, PRIMARY KEY (id))"
    ),
    "component_contract": (
        "CREATE NODE TABLE IF NOT EXISTS component_contract("
        "id STRING, title STRING, target_file STRING, protocol STRING, PRIMARY KEY (id))"
    ),
    "test_fixture": (
        "CREATE NODE TABLE IF NOT EXISTS test_fixture("
        "id STRING, title STRING, target_file STRING, command STRING, PRIMARY KEY (id))"
    ),
    "task_action": (
        "CREATE NODE TABLE IF NOT EXISTS task_action("
        "id STRING, title STRING, action STRING, target_file STRING, PRIMARY KEY (id))"
    ),
    "change_request": (
        "CREATE NODE TABLE IF NOT EXISTS change_request("
        "id STRING, title STRING, status STRING, authorized_by STRING, PRIMARY KEY (id))"
    ),
    "evaluation_suite": (
        "CREATE NODE TABLE IF NOT EXISTS evaluation_suite("
        "id STRING, title STRING, statement STRING, PRIMARY KEY (id))"
    ),
}

# Canonical DDL for SDD Rel Tables
REL_TABLE_SCHEMAS: dict[str, str] = {
    "decomposes_to": (
        "CREATE REL TABLE IF NOT EXISTS decomposes_to("
        "FROM seed_intent TO system_container, "
        "FROM seed_intent TO product_capability, "
        "FROM system_container TO component_contract, "
        "FROM system_container TO product_capability)"
    ),
    "realizes": (
        "CREATE REL TABLE IF NOT EXISTS realizes("
        "FROM product_capability TO business_objective, "
        "FROM formal_requirement TO product_capability, "
        "FROM formal_requirement TO business_objective)"
    ),
    "verifies": (
        "CREATE REL TABLE IF NOT EXISTS verifies(FROM acceptance_scenario TO formal_requirement)"
    ),
    "proves": ("CREATE REL TABLE IF NOT EXISTS proves(FROM test_fixture TO acceptance_scenario)"),
    "constrains": (
        "CREATE REL TABLE IF NOT EXISTS constrains("
        "FROM architectural_decision TO component_contract, "
        "FROM architectural_decision TO system_container, "
        "FROM system_container TO system_container)"
    ),
    "implements": (
        "CREATE REL TABLE IF NOT EXISTS implements("
        "FROM task_action TO component_contract, "
        "FROM task_action TO test_fixture)"
    ),
    "compensated_by": (
        "CREATE REL TABLE IF NOT EXISTS compensated_by(FROM task_action TO task_action)"
    ),
    "authorized_by": (
        "CREATE REL TABLE IF NOT EXISTS authorized_by("
        "FROM formal_requirement TO change_request, "
        "FROM component_contract TO change_request, "
        "FROM task_action TO change_request)"
    ),
    "supersedes": (
        "CREATE REL TABLE IF NOT EXISTS supersedes("
        "FROM formal_requirement TO formal_requirement, "
        "FROM acceptance_scenario TO acceptance_scenario, "
        "FROM architectural_decision TO architectural_decision)"
    ),
}


class KuzuGraphAdapter:
    """Embedded Kùzu graph execution adapter with openCypher querying."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        """Initialize Kùzu database instance (in-memory if path is None or empty)."""
        if not KUZU_AVAILABLE:
            self._db = None
            self._conn = None
            self._db_path = None
            return

        if db_path is None or db_path == ":memory:" or str(db_path) == "":
            self._db = kuzu.Database("")  # in-memory database
            self._db_path = ":memory:"
        else:
            p = Path(db_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            self._db = kuzu.Database(str(p))
            self._db_path = str(p)

        self._conn = kuzu.Connection(self._db)

    @classmethod
    def is_available(cls) -> bool:
        """Check if Kùzu is installed in the current Python environment."""
        return KUZU_AVAILABLE

    @property
    def is_connected(self) -> bool:
        """Check if active connection to Kùzu database exists."""
        return self._conn is not None

    def init_schema(self) -> None:
        """Create canonical SDD node and relationship tables in Kùzu."""
        self._assert_available()
        for _, ddl in NODE_TABLE_SCHEMAS.items():
            try:
                self._conn.execute(ddl)
            except Exception as e:
                logger.debug("Node table creation notice: %s", e)

        for _, ddl in REL_TABLE_SCHEMAS.items():
            try:
                self._conn.execute(ddl)
            except Exception as e:
                logger.debug("Rel table creation notice: %s", e)

    def ingest_graph(self, graph: SddGraph) -> dict[str, int]:
        """Ingest nodes and edges from an SddGraph instance into Kùzu tables."""
        self._assert_available()
        self.init_schema()

        nodes_inserted = 0
        edges_inserted = 0

        # Ingest nodes
        for nid, node in graph.nodes.items():
            ntype = node.get("type", "")
            if ntype not in NODE_TABLE_SCHEMAS:
                continue

            title = str(node.get("title", ""))
            statement = str(node.get("statement", ""))
            props = node.get("properties", {}) or {}

            try:
                if ntype == "seed_intent":
                    self._conn.execute(
                        "CREATE (n:seed_intent {id: $id, title: $title, statement: $statement})",
                        {"id": nid, "title": title, "statement": statement},
                    )
                elif ntype == "system_container":
                    context = str(node.get("context", ""))
                    container_archetype = str(props.get("container_archetype", "api_service"))
                    trust_boundary = str(props.get("trust_boundary", "Internal"))
                    data_classification = str(props.get("data_classification", "INTERNAL"))
                    self._conn.execute(
                        "CREATE (n:system_container {"
                        "id: $id, title: $title, context: $context, "
                        "container_archetype: $container_archetype, "
                        "trust_boundary: $trust_boundary, "
                        "data_classification: $data_classification"
                        "})",
                        {
                            "id": nid,
                            "title": title,
                            "context": context,
                            "container_archetype": container_archetype,
                            "trust_boundary": trust_boundary,
                            "data_classification": data_classification,
                        },
                    )
                elif ntype == "business_objective":
                    priority = str(props.get("priority", "P1"))
                    self._conn.execute(
                        "CREATE (n:business_objective {id: $id, title: $title, statement: $statement, priority: $priority})",
                        {"id": nid, "title": title, "statement": statement, "priority": priority},
                    )
                elif ntype == "product_capability":
                    persona = str(props.get("persona", "User"))
                    self._conn.execute(
                        "CREATE (n:product_capability {id: $id, title: $title, statement: $statement, persona: $persona})",
                        {"id": nid, "title": title, "statement": statement, "persona": persona},
                    )
                elif ntype == "formal_requirement":
                    pattern = str(node.get("pattern", "ubiquitous"))
                    self._conn.execute(
                        "CREATE (n:formal_requirement {id: $id, title: $title, statement: $statement, pattern: $pattern})",
                        {"id": nid, "title": title, "statement": statement, "pattern": pattern},
                    )
                elif ntype == "acceptance_scenario":
                    given = str(node.get("given", ""))
                    when_c = str(node.get("when", ""))
                    then_c = str(node.get("then", ""))
                    self._conn.execute(
                        "CREATE (n:acceptance_scenario {id: $id, title: $title, given: $given, when_clause: $when, then_clause: $then})",
                        {"id": nid, "title": title, "given": given, "when": when_c, "then": then_c},
                    )
                elif ntype == "architectural_decision":
                    ctx = str(node.get("context", ""))
                    dec = str(node.get("decision", ""))
                    stat = str(node.get("status", "Accepted"))
                    self._conn.execute(
                        "CREATE (n:architectural_decision {id: $id, title: $title, context: $context, decision: $decision, status: $status})",
                        {
                            "id": nid,
                            "title": title,
                            "context": ctx,
                            "decision": dec,
                            "status": stat,
                        },
                    )
                elif ntype == "component_contract":
                    target_file = str(node.get("target_file", ""))
                    proto = str(props.get("protocol", "http"))
                    self._conn.execute(
                        "CREATE (n:component_contract {id: $id, title: $title, target_file: $target, protocol: $protocol})",
                        {"id": nid, "title": title, "target": target_file, "protocol": proto},
                    )
                elif ntype == "test_fixture":
                    target_file = str(node.get("target_file", ""))
                    cmd = str(node.get("command", ""))
                    self._conn.execute(
                        "CREATE (n:test_fixture {id: $id, title: $title, target_file: $target, command: $command})",
                        {"id": nid, "title": title, "target": target_file, "command": cmd},
                    )
                elif ntype == "task_action":
                    action = str(node.get("action", "apply_patch"))
                    target_file = str(node.get("target_file", ""))
                    self._conn.execute(
                        "CREATE (n:task_action {id: $id, title: $title, action: $action, target_file: $target})",
                        {"id": nid, "title": title, "action": action, "target": target_file},
                    )
                elif ntype == "change_request":
                    status = str(node.get("status", "Active"))
                    auth = str(node.get("authorized_by", ""))
                    self._conn.execute(
                        "CREATE (n:change_request {id: $id, title: $title, status: $status, authorized_by: $auth})",
                        {"id": nid, "title": title, "status": status, "auth": auth},
                    )
                elif ntype == "evaluation_suite":
                    self._conn.execute(
                        "CREATE (n:evaluation_suite {id: $id, title: $title, statement: $statement})",
                        {"id": nid, "title": title, "statement": statement},
                    )
                nodes_inserted += 1
            except Exception as e:
                logger.warning("Failed to insert node %s: %s", nid, e)

        # Ingest edges
        for edge in graph.edges:
            rel = edge["relation"]
            if rel not in REL_TABLE_SCHEMAS:
                continue

            from_id = edge["from"]
            to_id = edge["to"]

            from_node = graph.nodes.get(from_id)
            to_node = graph.nodes.get(to_id)
            if not from_node or not to_node:
                continue

            from_type = from_node.get("type", "")
            to_type = to_node.get("type", "")

            query = (
                f"MATCH (a:{from_type}), (b:{to_type}) "
                f"WHERE a.id = $from_id AND b.id = $to_id "
                f"CREATE (a)-[r:{rel}]->(b)"
            )
            try:
                self._conn.execute(query, {"from_id": from_id, "to_id": to_id})
                edges_inserted += 1
            except Exception as e:
                logger.warning("Failed to insert rel (%s)-[%s]->(%s): %s", from_id, rel, to_id, e)

        return {"nodes": nodes_inserted, "edges": edges_inserted}

    def query(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute an openCypher query against Kùzu and return dictionary rows."""
        self._assert_available()
        response = self._conn.execute(cypher, params or {})
        results: list[dict[str, Any]] = []

        cols = response.get_column_names()
        while response.has_next():
            row = response.get_next()
            row_dict = {cols[i]: row[i] for i in range(len(cols))}
            results.append(row_dict)

        return results

    def _assert_available(self) -> None:
        """Raise informative RuntimeError if Kùzu is not installed."""
        if not KUZU_AVAILABLE or self._conn is None:
            raise RuntimeError(
                "Kùzu graph engine is not installed or available in this environment. "
                "To enable openCypher acceleration, install Kùzu: 'pip install kuzu'. "
                "Alternatively, use pure-Python SddGraph methods which require zero external dependencies."
            )
