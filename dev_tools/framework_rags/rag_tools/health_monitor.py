#!/usr/bin/env python3
"""Health monitor for all RAG services."""

import argparse
import sys
from typing import NamedTuple

import httpx
import psycopg2


class ServiceStatus(NamedTuple):
    """Service health status."""
    name: str
    healthy: bool
    message: str


def check_postgres(host: str = "localhost", port: int = 5432) -> ServiceStatus:
    """Check PostgreSQL health."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user="raguser",
            password="ragpass",
            database="ragdb",
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


def check_haystack(host: str = "localhost", port: int = 1416) -> ServiceStatus:
    """Check Haystack health."""
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=10)
        if response.status_code == 200:
            return ServiceStatus("Haystack", True, f"Healthy at {host}:{port}")
        return ServiceStatus("Haystack", False, f"HTTP {response.status_code}")
    except Exception as e:
        return ServiceStatus("Haystack", False, str(e))


def check_lightrag(host: str = "localhost", port: int = 9621) -> ServiceStatus:
    """Check LightRAG health."""
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=10)
        if response.status_code == 200:
            return ServiceStatus("LightRAG", True, f"Healthy at {host}:{port}")
        return ServiceStatus("LightRAG", False, f"HTTP {response.status_code}")
    except Exception as e:
        return ServiceStatus("LightRAG", False, str(e))


def check_all(verbose: bool = False) -> list[ServiceStatus]:
    """Check all services."""
    statuses = [
        check_postgres(),
        check_neo4j(),
        check_haystack(),
        check_lightrag(),
    ]

    print("\nRAG Services Health Check")
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
