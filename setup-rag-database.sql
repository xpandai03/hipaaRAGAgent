-- PostgreSQL setup script for RAG documents
-- Run this in your Render PostgreSQL database

-- Create documents table for simple text search
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    tenant_id VARCHAR(50) DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster text search
CREATE INDEX IF NOT EXISTS idx_documents_content ON documents USING gin(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_documents_tenant ON documents(tenant_id);

-- Insert sample medical documents for testing
INSERT INTO documents (content, metadata, tenant_id) VALUES
('Patient presents with persistent headache lasting 3 days. Recommended ibuprofen 400mg every 6 hours and follow-up if symptoms persist beyond 5 days.', '{"type": "clinical_note", "specialty": "general"}', 'default'),
('Mental health assessment: Patient reports anxiety and difficulty sleeping. Started on sertraline 50mg daily with follow-up in 2 weeks.', '{"type": "clinical_note", "specialty": "mental-health"}', 'amanda'),
('Dermatology consultation: Acne vulgaris diagnosed. Prescribed tretinoin 0.025% cream nightly and benzoyl peroxide 2.5% in morning.', '{"type": "clinical_note", "specialty": "dermatology"}', 'emmer'),
('Post-procedure care: Botox injection completed. Patient advised to avoid lying down for 4 hours and strenuous exercise for 24 hours.', '{"type": "procedure_note", "specialty": "med-spa"}', 'robbie'),
('Diabetes management: HbA1c at 7.2%. Increased metformin to 1000mg twice daily. Diet and exercise counseling provided.', '{"type": "clinical_note", "specialty": "endocrinology"}', 'default');

-- Create table for vector storage (for advanced workflow)
CREATE TABLE IF NOT EXISTS documents_vectors (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(3072), -- Azure text-embedding-3-large dimensions
    metadata JSONB DEFAULT '{}',
    tenant_id VARCHAR(50) DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_documents_vectors_embedding ON documents_vectors USING ivfflat (embedding vector_cosine_ops);