#!/usr/bin/env python3
"""Health monitor for ucx_knowledge prerequisites."""

import argparse
import os
import sys
from pathlib import Path
from typing import NamedTuple

import httpx
import psycopg2
from dotenv import load_dotenv

_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


class ServiceStatus(NamedTuple):
    """Service health status."""
    name: str
    healthy: bool
    message: str


def check_postgres(
    host: str = "localhost",
    port: int = 5433,
    user: str = "lightrag",
    password: str = "lightrag",
    database: str = "lightrag",
) -> ServiceStatus:
    """Check PostgreSQL health."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=5,
        )
        conn.close()
        return ServiceStatus("PostgreSQL", True, f"Connected to {host}:{port}")
    except Exception as e:
        return ServiceStatus("PostgreSQL", False, str(e))


def check_neo4j(host: str = "localhost", port: int = 7474) -> ServiceStatus:
    """Check Neo4j health."""
    try:
        response = httpx.get(f"http://{host}:{port}", timeout=5)
        if response.status_code == 200:
            return ServiceStatus("Neo4j", True, f"HTTP OK at {host}:{port}")
        return ServiceStatus("Neo4j", False, f"HTTP {response.status_code}")
    except Exception as e:
        return ServiceStatus("Neo4j", False, str(e))


def check_ucx_knowledge_mcp(host: str = "localhost", port: int = 8101) -> ServiceStatus:
    """Check optional ucx_knowledge MCP endpoint health."""
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=10)
        if response.status_code == 200:
            return ServiceStatus("ProjectKnowledge-MCP", True, f"Healthy at {host}:{port}")
        return ServiceStatus("ProjectKnowledge-MCP", False, f"HTTP {response.status_code}")
    except Exception as e:
        return ServiceStatus("ProjectKnowledge-MCP", False, str(e))


def check_python_package() -> ServiceStatus:
    """Check if ucx_knowledge package is importable."""
    try:
        __import__("ucx_knowledge")
        return ServiceStatus("PythonPackage", True, "ucx_knowledge import OK")
    except Exception as e:
        return ServiceStatus("PythonPackage", False, str(e))


def check_all(verbose: bool = False) -> list[ServiceStatus]:
    """Check all services."""
    pg_host = os.getenv("PG_HOST", os.getenv("PK_PG_HOST", "localhost"))
    pg_port = int(os.getenv("PG_PORT", os.getenv("PK_PG_PORT", "5433")))
    pg_user = os.getenv("PG_USER", "lightrag")
    pg_pass = os.getenv("PG_PASS", "lightrag")
    pg_db = os.getenv("PG_DB", "lightrag")
    neo4j_host = os.getenv("PK_NEO4J_HOST", "localhost")
    neo4j_port = int(os.getenv("PK_DB_NEO4J_HTTP_PORT", os.getenv("PK_NEO4J_HTTP_PORT", "7475")))
    mcp_host = os.getenv("PK_MCP_HOST", "localhost")
    mcp_port = int(os.getenv("PK_MCP_PORT", "8101"))

    statuses = [
        check_python_package(),
        check_postgres(
            host=pg_host,
            port=pg_port,
            user=pg_user,
            password=pg_pass,
            database=pg_db,
        ),
        check_neo4j(host=neo4j_host, port=neo4j_port),
        check_ucx_knowledge_mcp(host=mcp_host, port=mcp_port),
    ]

    print("\nUCX Knowledge Health Check")
    print("=" * 50)

    all_healthy = True
    for status in statuses:
        icon = "✓" if status.healthy else "✗"
        color = "\033[32m" if status.healthy else "\033[31m"
        reset = "\033[0m"

        print(f"{color}{icon}{reset} {status.name}: ", end="")
        if status.healthy:
            print(f"{color}Healthy{reset}")
        else:
            print(f"{color}Unhealthy{reset}")
            all_healthy = False

        if verbose:
            print(f"  {status.message}")

    print("=" * 50)

    if all_healthy:
        print("\033[32mAll services healthy!\033[0m")
    else:
        print("\033[31mSome services are unhealthy.\033[0m")

    return statuses


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check RAG services health")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    statuses = check_all(verbose=args.verbose)

    # Exit with error if any service unhealthy
    if not all(s.healthy for s in statuses):
        sys.exit(1)


if __name__ == "__main__":
    main()
