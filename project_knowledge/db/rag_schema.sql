-- ============================================================
-- PROJECT KNOWLEDGE RAG SCHEMA (pgvector)
-- Version: 1.0.0
-- ============================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS nexus;

-- ============================================================
-- DOCUMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS nexus.rag_documents (
    id              SERIAL PRIMARY KEY,
    doc_id          VARCHAR(100) NOT NULL UNIQUE,    -- _meta.id (e.g., "EA-NVDA-Q4-2024")
    file_path       VARCHAR(500) NOT NULL,           -- Relative path from project root
    doc_type        VARCHAR(50) NOT NULL,            -- earnings-analysis, stock-analysis, etc.
    ticker          VARCHAR(10),                     -- Primary ticker (NULL for research/macro)

    -- Temporal
    doc_date        DATE,                            -- Analysis/trade date
    quarter         VARCHAR(20),                     -- Q4-FY2025 (for earnings)

    -- Processing state
    chunk_count     INTEGER DEFAULT 0,
    embed_version   VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    embed_model     VARCHAR(50) NOT NULL DEFAULT 'nomic-embed-text',

    -- Source tracking
    file_hash       VARCHAR(64),                     -- SHA-256 of source file

    tags            TEXT[],

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- CHUNKS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS nexus.rag_chunks (
    id              BIGSERIAL PRIMARY KEY,
    doc_id          INTEGER NOT NULL REFERENCES nexus.rag_documents(id) ON DELETE CASCADE,

    -- Chunk identity
    section_path    VARCHAR(200) NOT NULL,           -- YAML key path
    section_label   VARCHAR(100) NOT NULL,           -- Human-readable label
    chunk_index     SMALLINT NOT NULL DEFAULT 0,     -- For split sections

    -- Content
    content         TEXT NOT NULL,                   -- Flattened text
    content_tokens  INTEGER,                         -- Token count

    -- Full-text search (BM25)
    content_tsv     tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,

    -- Embedding (1536 for pgvector index compatibility)
    embedding       vector(1536) NOT NULL,           -- OpenAI text-embedding-3-large with truncation

    -- Denormalized for filtered search (avoids JOINs)
    doc_type        VARCHAR(50) NOT NULL,
    ticker          VARCHAR(10),
    doc_date        DATE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- EMBEDDING LOG
-- ============================================================
CREATE TABLE IF NOT EXISTS nexus.rag_embed_log (
    id              BIGSERIAL PRIMARY KEY,
    doc_id          INTEGER REFERENCES nexus.rag_documents(id),
    file_path       VARCHAR(500),
    action          VARCHAR(20) NOT NULL,            -- 'embed', 'reembed', 'delete'
    chunks_created  INTEGER DEFAULT 0,
    duration_ms     INTEGER,
    embed_model     VARCHAR(50),
    embed_version   VARCHAR(20),
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Document lookups
CREATE INDEX IF NOT EXISTS idx_rag_docs_type ON nexus.rag_documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_rag_docs_ticker ON nexus.rag_documents(ticker);
CREATE INDEX IF NOT EXISTS idx_rag_docs_date ON nexus.rag_documents(doc_date);
CREATE INDEX IF NOT EXISTS idx_rag_docs_tags ON nexus.rag_documents USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_rag_docs_version ON nexus.rag_documents(embed_version);

-- Vector similarity (HNSW - works well for any dataset size)
CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding
    ON nexus.rag_chunks USING hnsw (embedding vector_cosine_ops);

-- Filtered search
CREATE INDEX IF NOT EXISTS idx_rag_chunks_doc ON nexus.rag_chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_ticker ON nexus.rag_chunks(ticker);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_type ON nexus.rag_chunks(doc_type);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_section ON nexus.rag_chunks(section_label);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_date ON nexus.rag_chunks(doc_date);

-- Unique constraint
CREATE UNIQUE INDEX IF NOT EXISTS idx_rag_chunks_unique
    ON nexus.rag_chunks(doc_id, section_path, chunk_index);

-- Full-text search (BM25)
CREATE INDEX IF NOT EXISTS idx_rag_chunks_fts
    ON nexus.rag_chunks USING gin(content_tsv);

-- ============================================================
-- INDEX TUNING THRESHOLDS
-- ============================================================
-- < 10,000 chunks:    IVFFlat with lists = 50 (current)
-- 10,000 - 100,000:   IVFFlat with lists = 100
-- > 100,000:          Switch to HNSW with m = 16, ef_construction = 64
--
-- To upgrade to HNSW:
-- DROP INDEX IF EXISTS nexus.idx_rag_chunks_embedding;
-- CREATE INDEX idx_rag_chunks_embedding
--     ON nexus.rag_chunks USING hnsw (embedding vector_cosine_ops)
--     WITH (m = 16, ef_construction = 64);

-- ============================================================
-- HELPER FUNCTION: Update timestamp trigger
-- ============================================================
CREATE OR REPLACE FUNCTION nexus.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER rag_documents_updated_at
    BEFORE UPDATE ON nexus.rag_documents
    FOR EACH ROW
    EXECUTE FUNCTION nexus.update_updated_at();
