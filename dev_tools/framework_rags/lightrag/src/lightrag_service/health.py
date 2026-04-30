"""Health monitoring for LightRAG service."""

import os
from dataclasses import dataclass
from typing import Any

import httpx
from neo4j import GraphDatabase


@dataclass
class HealthStatus:
    """Health check result."""
    service: str
    healthy: bool
    message: str
    details: dict[str, Any] | None = None


def check_neo4j() -> HealthStatus:
    """Check Neo4j connectivity and status."""
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    username = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "neo4jpass")

    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]

        driver.close()
        return HealthStatus(
            service="Neo4j",
            healthy=True,
            message=f"Connected, {count} nodes",
            details={"node_count": count, "uri": uri}
        )
    except Exception as e:
        return HealthStatus(
            service="Neo4j",
            healthy=False,
            message=str(e)
        )


def check_postgres() -> HealthStatus:
    """Check PostgreSQL connectivity."""
    try:
        import psycopg2

        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", "5432")),
            user=os.environ.get("POSTGRES_USER", "raguser"),
            password=os.environ.get("POSTGRES_PASSWORD", "ragpass"),
            database=os.environ.get("POSTGRES_DATABASE", "ragdb"),
            connect_timeout=5,
        )

        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM lightrag.kv_store")
        kv_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM lightrag.vector_store")
        vector_count = cur.fetchone()[0]

        conn.close()

        return HealthStatus(
            service="PostgreSQL",
            healthy=True,
            message=f"Connected, {kv_count} KV entries, {vector_count} vectors",
            details={"kv_count": kv_count, "vector_count": vector_count}
        )
    except Exception as e:
        return HealthStatus(
            service="PostgreSQL",
            healthy=False,
            message=str(e)
        )


def check_lightrag_api(host: str = "localhost", port: int = 9621) -> HealthStatus:
    """Check LightRAG API health."""
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=10)
        if response.status_code == 200:
            return HealthStatus(
                service="LightRAG API",
                healthy=True,
                message="Healthy",
                details=response.json() if response.headers.get("content-type", "").startswith("application/json") else None
            )
        return HealthStatus(
            service="LightRAG API",
            healthy=False,
            message=f"HTTP {response.status_code}"
        )
    except Exception as e:
        return HealthStatus(
            service="LightRAG API",
            healthy=False,
            message=str(e)
        )


def get_graph_statistics() -> dict[str, Any]:
    """Get Neo4j graph statistics."""
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    username = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "neo4jpass")

    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        with driver.session() as session:
            # Node count
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = node_result.single()["count"]

            # Relationship count
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = rel_result.single()["count"]

            # Node types
            type_result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(*) as count
                ORDER BY count DESC
                LIMIT 10
            """)
            node_types = {r["type"]: r["count"] for r in type_result}

        driver.close()

        return {
            "nodes": node_count,
            "relationships": rel_count,
            "node_types": node_types,
        }
    except Exception as e:
        return {"error": str(e)}


def check_all() -> list[HealthStatus]:
    """Run all health checks."""
    return [
        check_postgres(),
        check_neo4j(),
        check_lightrag_api(),
    ]
