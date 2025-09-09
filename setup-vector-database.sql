-- Setup pgvector extension and document chunks table for RAG

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create document chunks table with embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL, -- Clerk user ID
    document_id UUID NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(3072), -- Azure OpenAI text-embedding-3-large dimensions
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes for performance
    CONSTRAINT unique_chunk UNIQUE(document_id, chunk_index)
);

-- Create indexes for fast retrieval
CREATE INDEX IF NOT EXISTS idx_chunks_user_id ON document_chunks(user_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Function to search similar chunks
CREATE OR REPLACE FUNCTION search_similar_chunks(
    p_user_id VARCHAR(255),
    p_query_embedding vector(3072),
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    chunk_id UUID,
    chunk_text TEXT,
    similarity FLOAT,
    document_id UUID,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        id as chunk_id,
        document_chunks.chunk_text,
        1 - (embedding <=> p_query_embedding) as similarity,
        document_chunks.document_id,
        document_chunks.metadata
    FROM document_chunks
    WHERE user_id = p_user_id
    ORDER BY embedding <=> p_query_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Update the UploadedFile table to track vector processing
ALTER TABLE "UploadedFile" 
ADD COLUMN IF NOT EXISTS chunks_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS embeddings_generated BOOLEAN DEFAULT false;

-- Grant permissions (adjust as needed)
GRANT ALL ON document_chunks TO CURRENT_USER;