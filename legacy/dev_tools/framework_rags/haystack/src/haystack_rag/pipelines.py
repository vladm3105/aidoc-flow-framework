"""Haystack pipeline builders for indexing and querying."""

from typing import Any

from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.converters import MarkdownToDocument
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.joiners import DocumentJoiner
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.components.writers import DocumentWriter
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from .components.metadata_enricher import MetadataEnricher
from .config import get_pg_connection_string, load_config


def create_document_store(config: dict[str, Any] | None = None) -> PgvectorDocumentStore:
    """Create PgvectorDocumentStore instance.

    Args:
        config: Configuration dictionary.

    Returns:
        Configured document store.
    """
    if config is None:
        config = load_config()

    vs_config = config.get("vector_store", {})
    embedding_config = config.get("embedding", {})

    return PgvectorDocumentStore(
        connection_string=get_pg_connection_string(),
        schema_name=vs_config.get("schema", "haystack_docs"),
        table_name=vs_config.get("table", "documents"),
        embedding_dimension=embedding_config.get("dimensions", 1536),
        vector_function="cosine_similarity",
        recreate_table=vs_config.get("recreate_table", False),
        search_strategy="hnsw",
        hnsw_recreate_index_if_exists=False,
        hnsw_index_creation_kwargs={
            "m": vs_config.get("hnsw", {}).get("m", 16),
            "ef_construction": vs_config.get("hnsw", {}).get("ef_construction", 256),
        },
    )


def create_indexing_pipeline(config: dict[str, Any] | None = None) -> Pipeline:
    """Create document indexing pipeline.

    Pipeline: Markdown → Clean → Split → Enrich Metadata → Embed → Write

    Args:
        config: Configuration dictionary.

    Returns:
        Configured indexing pipeline.
    """
    if config is None:
        config = load_config()

    split_config = config.get("splitting", {})
    embedding_config = config.get("embedding", {})
    clean_config = config.get("cleaning", {})

    # Create components
    converter = MarkdownToDocument()

    cleaner = DocumentCleaner(
        remove_empty_lines=clean_config.get("remove_empty_lines", True),
        remove_extra_whitespaces=clean_config.get("remove_extra_whitespace", True),
    )

    splitter = DocumentSplitter(
        split_by=split_config.get("split_by", "sentence"),
        split_length=split_config.get("split_length", 10),
        split_overlap=split_config.get("split_overlap", 3),
    )

    metadata_enricher = MetadataEnricher(
        extract_fields=config.get("metadata", {}).get("extract_fields", [])
    )

    embedder = OpenAIDocumentEmbedder(
        model=embedding_config.get("model", "text-embedding-3-small"),
    )

    document_store = create_document_store(config)
    writer = DocumentWriter(document_store=document_store)

    # Build pipeline
    pipeline = Pipeline()
    pipeline.add_component("converter", converter)
    pipeline.add_component("cleaner", cleaner)
    pipeline.add_component("splitter", splitter)
    pipeline.add_component("metadata_enricher", metadata_enricher)
    pipeline.add_component("embedder", embedder)
    pipeline.add_component("writer", writer)

    # Connect components
    pipeline.connect("converter", "cleaner")
    pipeline.connect("cleaner", "splitter")
    pipeline.connect("splitter", "metadata_enricher")
    pipeline.connect("metadata_enricher", "embedder")
    pipeline.connect("embedder", "writer")

    return pipeline


def create_query_pipeline(config: dict[str, Any] | None = None) -> Pipeline:
    """Create document query pipeline.

    Pipeline: Query → [Embed + BM25] → Join (RRF) → Rerank → Prompt → Generate

    Args:
        config: Configuration dictionary.

    Returns:
        Configured query pipeline.
    """
    if config is None:
        config = load_config()

    retrieval_config = config.get("retrieval", {})
    generation_config = config.get("generation", {})
    embedding_config = config.get("embedding", {})

    document_store = create_document_store(config)

    # Create components
    text_embedder = OpenAITextEmbedder(
        model=embedding_config.get("model", "text-embedding-3-small"),
    )

    vector_retriever = PgvectorEmbeddingRetriever(
        document_store=document_store,
        top_k=retrieval_config.get("vector_top_k", 20),
    )

    # Document joiner with Reciprocal Rank Fusion
    joiner = DocumentJoiner(
        join_mode="reciprocal_rank_fusion",
    )

    # Prompt builder
    prompt_template = """
    Answer the question based on the provided context.

    Context:
    {% for doc in documents %}
    ---
    Source: {{ doc.meta.get('file_path', 'Unknown') }}
    {{ doc.content }}
    {% endfor %}
    ---

    Question: {{ query }}

    Answer:
    """

    prompt_builder = PromptBuilder(template=prompt_template)

    # LLM generator
    generator = OpenAIGenerator(
        model=generation_config.get("model", "gpt-4o-mini"),
        generation_kwargs={
            "max_tokens": generation_config.get("max_tokens", 1024),
            "temperature": generation_config.get("temperature", 0.1),
        },
    )

    # Build pipeline
    pipeline = Pipeline()
    pipeline.add_component("text_embedder", text_embedder)
    pipeline.add_component("vector_retriever", vector_retriever)
    pipeline.add_component("joiner", joiner)
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("generator", generator)

    # Connect components
    pipeline.connect("text_embedder.embedding", "vector_retriever.query_embedding")
    pipeline.connect("vector_retriever.documents", "joiner.documents")
    pipeline.connect("joiner.documents", "prompt_builder.documents")
    pipeline.connect("prompt_builder", "generator")

    return pipeline


def create_hybrid_query_pipeline(config: dict[str, Any] | None = None) -> Pipeline:
    """Create hybrid query pipeline with BM25 + Vector search.

    Note: BM25 requires additional setup with PostgreSQL full-text search.
    This is a placeholder for the full hybrid implementation.

    Args:
        config: Configuration dictionary.

    Returns:
        Configured hybrid query pipeline.
    """
    # For now, return the vector-only pipeline
    # Full BM25 integration requires custom BM25Retriever component
    return create_query_pipeline(config)
