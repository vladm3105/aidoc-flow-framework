"""pgvector schema initialization."""

import logging
import os
from pathlib import Path

import psycopg

from .exceptions import RAGUnavailableError

log = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get database URL from environment or config."""
    # Check DATABASE_URL first
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")

    # Build from individual PG_* variables
    user = os.getenv("PG_USER", "lightrag")
    password = os.getenv("PG_PASS", "lightrag")
    host = os.getenv("PG_HOST", "localhost")
    port = os.getenv("PG_PORT", "5433")
    db = os.getenv("PG_DB", "lightrag")

    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def init_schema() -> None:
    """
    Initialize pgvector schema from schema file.

    Creates nexus schema and RAG tables if they don't exist.
    """
    schema_path = Path(__file__).parent.parent / "db" / "rag_schema.sql"

    if not schema_path.exists():
        raise RAGUnavailableError(f"Schema file not found: {schema_path}")

    with open(schema_path) as f:
        schema_sql = f.read()

    try:
        with psycopg.connect(get_database_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()
        log.info("RAG schema initialized successfully")
    except Exception as e:
        raise RAGUnavailableError(f"Failed to initialize schema: {e}")


def reset_schema(confirm: bool = False) -> None:
    """
    Drop and recreate RAG tables (dev only).

    Args:
        confirm: Must be True to proceed
    """
    if not confirm:
        raise ValueError("Must set confirm=True to reset schema")

    try:
        with psycopg.connect(get_database_url()) as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS nexus.rag_embed_log CASCADE")
                cur.execute("DROP TABLE IF EXISTS nexus.rag_chunks CASCADE")
                cur.execute("DROP TABLE IF EXISTS nexus.rag_documents CASCADE")
            conn.commit()
        log.warning("RAG tables dropped")

        # Reinitialize
        init_schema()
    except Exception as e:
        raise RAGUnavailableError(f"Failed to reset schema: {e}")


def verify_schema() -> dict:
    """
    Verify that pgvector schema is properly initialized.

    Returns:
        dict with verification results
    """
    results = {
        "pgvector_enabled": False,
        "schema_exists": False,
        "tables": [],
        "indexes": [],
    }

    try:
        with psycopg.connect(get_database_url()) as conn:
            with conn.cursor() as cur:
                # Check pgvector extension
                cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                results["pgvector_enabled"] = cur.fetchone() is not None

                # Check schema exists
                cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name = 'nexus'")
                results["schema_exists"] = cur.fetchone() is not None

                # List tables
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'nexus' AND table_name LIKE 'rag_%'
                """)
                results["tables"] = [row[0] for row in cur.fetchall()]

                # List indexes
                cur.execute("""
                    SELECT indexname
                    FROM pg_indexes
                    WHERE schemaname = 'nexus' AND indexname LIKE 'idx_rag_%'
                """)
                results["indexes"] = [row[0] for row in cur.fetchall()]

    except Exception as e:
        results["error"] = str(e)

    return results


def health_check() -> bool:
    """Check if pgvector database is reachable."""
    try:
        with psycopg.connect(get_database_url()) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.execute("SELECT vector_dims('[1,2,3]'::vector)")
        return True
    except Exception:
        return False


def get_db_stats() -> dict | None:
    """Get RAG database statistics (document and chunk counts)."""
    try:
        schema = get_config().get("database", {}).get("schema", "nexus")
        with psycopg.connect(get_database_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {schema}.rag_documents")
                documents = cur.fetchone()[0]
                cur.execute(f"SELECT COUNT(*) FROM {schema}.rag_chunks")
                chunks = cur.fetchone()[0]
                return {"documents": documents, "chunks": chunks}
    except Exception:
        return None


def run_migrations() -> None:
    """
    Run all pending database migrations.

    Migrations are SQL files in db/migrations/ directory.
    Tracks applied migrations in nexus.rag_migrations table.
    """
    migrations_dir = Path(__file__).parent.parent / "db" / "migrations"

    if not migrations_dir.exists():
        log.info("No migrations directory found")
        return

    try:
        with psycopg.connect(get_database_url()) as conn:
            with conn.cursor() as cur:
                # Create migrations tracking table if not exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS nexus.rag_migrations (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL UNIQUE,
                        applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                """)

                # Get list of applied migrations
                cur.execute("SELECT filename FROM nexus.rag_migrations")
                applied = {row[0] for row in cur.fetchall()}

                # Find and run pending migrations
                migration_files = sorted(migrations_dir.glob("*.sql"))
                for migration_file in migration_files:
                    if migration_file.name in applied:
                        log.debug(f"Skipping already applied: {migration_file.name}")
                        continue

                    log.info(f"Applying migration: {migration_file.name}")
                    with open(migration_file) as f:
                        migration_sql = f.read()

                    cur.execute(migration_sql)
                    cur.execute(
                        "INSERT INTO nexus.rag_migrations (filename) VALUES (%s)",
                        (migration_file.name,),
                    )
                    log.info(f"Applied migration: {migration_file.name}")

            conn.commit()
    except Exception as e:
        raise RAGUnavailableError(f"Migration failed: {e}")


def has_hybrid_search() -> bool:
    """Check if hybrid search (full-text) is available."""
    try:
        with psycopg.connect(get_database_url()) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'nexus'
                    AND table_name = 'rag_chunks'
                    AND column_name = 'content_tsv'
                """)
                return cur.fetchone() is not None
    except Exception:
        return False
