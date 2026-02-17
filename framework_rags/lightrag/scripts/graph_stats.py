#!/usr/bin/env python3
"""Display Neo4j graph statistics for LightRAG."""

import argparse
import os
import sys

from neo4j import GraphDatabase


def get_connection():
    """Get Neo4j driver connection."""
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    username = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "neo4jpass")
    return GraphDatabase.driver(uri, auth=(username, password))


def print_overview(session):
    """Print graph overview statistics."""
    print("Graph Overview")
    print("=" * 50)

    # Node count
    result = session.run("MATCH (n) RETURN count(n) as count")
    print(f"Total nodes: {result.single()['count']}")

    # Relationship count
    result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
    print(f"Total relationships: {result.single()['count']}")


def print_node_types(session, limit: int = 20):
    """Print node type distribution."""
    print("\nNode Types")
    print("=" * 50)

    result = session.run(f"""
        MATCH (n)
        RETURN labels(n)[0] as type, count(*) as count
        ORDER BY count DESC
        LIMIT {limit}
    """)

    for record in result:
        print(f"  {record['type']}: {record['count']}")


def print_relationship_types(session, limit: int = 20):
    """Print relationship type distribution."""
    print("\nRelationship Types")
    print("=" * 50)

    result = session.run(f"""
        MATCH ()-[r]->()
        RETURN type(r) as type, count(*) as count
        ORDER BY count DESC
        LIMIT {limit}
    """)

    for record in result:
        print(f"  {record['type']}: {record['count']}")


def print_top_entities(session, entity_type: str | None = None, limit: int = 10):
    """Print top entities by relationship count."""
    print(f"\nTop Entities{' (' + entity_type + ')' if entity_type else ''}")
    print("=" * 50)

    if entity_type:
        query = f"""
            MATCH (n:{entity_type})-[r]-()
            RETURN n.name as name, count(r) as connections
            ORDER BY connections DESC
            LIMIT {limit}
        """
    else:
        query = f"""
            MATCH (n)-[r]-()
            RETURN n.name as name, labels(n)[0] as type, count(r) as connections
            ORDER BY connections DESC
            LIMIT {limit}
        """

    result = session.run(query)

    for record in result:
        if entity_type:
            print(f"  {record['name']}: {record['connections']} connections")
        else:
            print(f"  [{record['type']}] {record['name']}: {record['connections']} connections")


def find_duplicates(session, limit: int = 20):
    """Find potential duplicate entities."""
    print("\nPotential Duplicates (similar names)")
    print("=" * 50)

    result = session.run(f"""
        MATCH (n)
        WHERE n.name IS NOT NULL
        WITH toLower(n.name) as lowername, collect(n) as nodes
        WHERE size(nodes) > 1
        RETURN lowername, size(nodes) as count, [n in nodes | n.name] as names
        ORDER BY count DESC
        LIMIT {limit}
    """)

    found = False
    for record in result:
        found = True
        print(f"  '{record['lowername']}' appears {record['count']} times:")
        for name in record['names']:
            print(f"    - {name}")

    if not found:
        print("  No duplicates found")


def main():
    parser = argparse.ArgumentParser(description="Display Neo4j graph statistics")
    parser.add_argument("--entity-type", help="Filter by entity type")
    parser.add_argument("--limit", type=int, default=10, help="Limit results")
    parser.add_argument("--duplicates", action="store_true", help="Show potential duplicates")
    args = parser.parse_args()

    try:
        driver = get_connection()
        with driver.session() as session:
            print_overview(session)
            print_node_types(session)
            print_relationship_types(session)
            print_top_entities(session, args.entity_type, args.limit)

            if args.duplicates:
                find_duplicates(session, args.limit)

        driver.close()
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
