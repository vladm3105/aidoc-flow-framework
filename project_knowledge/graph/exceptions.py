"""Exceptions for graph operations."""


class GraphError(Exception):
    """Base exception for graph operations."""

    pass


class GraphUnavailableError(GraphError):
    """Neo4j is not reachable."""

    pass


class ExtractionError(GraphError):
    """Entity/relationship extraction failed."""

    pass


class NormalizationError(GraphError):
    """Entity normalization failed."""

    pass


class SchemaError(GraphError):
    """Schema initialization or migration failed."""

    pass
