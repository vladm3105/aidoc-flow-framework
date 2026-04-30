#!/usr/bin/env python3
"""Verify Haystack RAG service health and connectivity."""

import sys
from pathlib import Path

import httpx

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def check_hayhooks(host: str = "localhost", port: int = 1416) -> bool:
    """Check Hayhooks server health."""
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"  Hayhooks error: {e}")
        return False


def check_postgres(conn_str: str | None = None) -> bool:
    """Check PostgreSQL connectivity."""
    try:
        import psycopg2
        from haystack_rag.config import get_pg_connection_string

        conn_str = conn_str or get_pg_connection_string()
        conn = psycopg2.connect(conn_str, connect_timeout=5)

        # Check schema exists
        cur = conn.cursor()
        cur.execute("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.schemata
                WHERE schema_name = 'haystack_docs'
            )
        """)
        schema_exists = cur.fetchone()[0]

        conn.close()
        return schema_exists
    except Exception as e:
        print(f"  PostgreSQL error: {e}")
        return False


def check_document_count() -> int:
    """Get document count from store."""
    try:
        from haystack_rag.pipelines import create_document_store

        store = create_document_store()
        return store.count_documents()
    except Exception as e:
        print(f"  Document store error: {e}")
        return -1


def main():
    print("Haystack RAG Health Check")
    print("=" * 40)

    all_healthy = True

    # Check PostgreSQL
    print("\nPostgreSQL:")
    if check_postgres():
        print("  ✓ Connected, schema exists")
    else:
        print("  ✗ Connection failed")
        all_healthy = False

    # Check document count
    print("\nDocument Store:")
    count = check_document_count()
    if count >= 0:
        print(f"  ✓ {count} documents indexed")
    else:
        print("  ✗ Could not access store")
        all_healthy = False

    # Check Hayhooks
    print("\nHayhooks Server:")
    if check_hayhooks():
        print("  ✓ Healthy")
    else:
        print("  ✗ Not responding")
        all_healthy = False

    print("\n" + "=" * 40)
    if all_healthy:
        print("✓ All checks passed")
        return 0
    else:
        print("✗ Some checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
