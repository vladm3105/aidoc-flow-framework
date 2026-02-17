-- =============================================================================
-- RAG Database Initialization Script
-- Creates schemas and extensions for Haystack and LightRAG
-- =============================================================================

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for fuzzy text search (BM25 enhancement)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =============================================================================
-- Haystack Schema (Service 1: Project Documentation)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS haystack_docs;

-- Documents table for Haystack
CREATE TABLE IF NOT EXISTS haystack_docs.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(1536),
    meta JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- HNSW index for fast vector similarity search
CREATE INDEX IF NOT EXISTS idx_haystack_embedding_hnsw
ON haystack_docs.documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 256);

-- GIN index for JSONB metadata queries
CREATE INDEX IF NOT EXISTS idx_haystack_meta
ON haystack_docs.documents
USING GIN (meta);

-- Full-text search index for BM25
CREATE INDEX IF NOT EXISTS idx_haystack_content_fts
ON haystack_docs.documents
USING GIN (to_tsvector('english', content));

-- Trigram index for fuzzy matching
CREATE INDEX IF NOT EXISTS idx_haystack_content_trgm
ON haystack_docs.documents
USING GIN (content gin_trgm_ops);

-- =============================================================================
-- LightRAG Schema (Service 2: Research & Analysis)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS lightrag;

-- KV Store for LightRAG cache
CREATE TABLE IF NOT EXISTS lightrag.kv_store (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector store for LightRAG embeddings
CREATE TABLE IF NOT EXISTS lightrag.vector_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- HNSW index for LightRAG vectors
CREATE INDEX IF NOT EXISTS idx_lightrag_embedding_hnsw
ON lightrag.vector_store
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 256);

-- Document status tracking
CREATE TABLE IF NOT EXISTS lightrag.doc_status (
    doc_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending',
    chunks_processed INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for status queries
CREATE INDEX IF NOT EXISTS idx_lightrag_doc_status
ON lightrag.doc_status (status);

-- =============================================================================
-- Grants
-- =============================================================================

GRANT ALL ON SCHEMA haystack_docs TO raguser;
GRANT ALL ON SCHEMA lightrag TO raguser;
GRANT ALL ON ALL TABLES IN SCHEMA haystack_docs TO raguser;
GRANT ALL ON ALL TABLES IN SCHEMA lightrag TO raguser;
GRANT ALL ON ALL SEQUENCES IN SCHEMA haystack_docs TO raguser;
GRANT ALL ON ALL SEQUENCES IN SCHEMA lightrag TO raguser;

-- =============================================================================
-- Utility Functions
-- =============================================================================

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for haystack documents
DROP TRIGGER IF EXISTS trigger_haystack_updated_at ON haystack_docs.documents;
CREATE TRIGGER trigger_haystack_updated_at
    BEFORE UPDATE ON haystack_docs.documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Trigger for lightrag kv_store
DROP TRIGGER IF EXISTS trigger_lightrag_kv_updated_at ON lightrag.kv_store;
CREATE TRIGGER trigger_lightrag_kv_updated_at
    BEFORE UPDATE ON lightrag.kv_store
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Trigger for lightrag doc_status
DROP TRIGGER IF EXISTS trigger_lightrag_status_updated_at ON lightrag.doc_status;
CREATE TRIGGER trigger_lightrag_status_updated_at
    BEFORE UPDATE ON lightrag.doc_status
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- Verification
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE 'RAG database initialization complete';
    RAISE NOTICE 'Schemas created: haystack_docs, lightrag';
    RAISE NOTICE 'Extensions enabled: vector, pg_trgm';
END $$;
