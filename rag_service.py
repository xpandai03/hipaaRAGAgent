from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np
from openai import AzureOpenAI
import os
import json
import asyncio
from datetime import datetime

app = FastAPI(title="Medical RAG Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VectorStore:
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.metadata = []
    
    def add_document(self, text: str, embedding: List[float], metadata: dict):
        self.documents.append(text)
        self.embeddings.append(np.array(embedding))
        self.metadata.append(metadata)
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        if not self.embeddings:
            return []
        
        query_vec = np.array(query_embedding)
        scores = []
        
        for emb in self.embeddings:
            score = np.dot(query_vec, emb) / (np.linalg.norm(query_vec) * np.linalg.norm(emb))
            scores.append(score)
        
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                "content": self.documents[idx],
                "score": float(scores[idx]),
                "metadata": self.metadata[idx]
            })
        
        return results

vector_store = VectorStore()

# Initialize Azure clients for chat and embeddings
# Chat client (GPT-5-mini)
azure_chat_client = None
try:
    azure_chat_client = AzureOpenAI(
        api_key=os.getenv("AZURE_CHAT_API_KEY", "your_chat_api_key_here"),
        api_version="2024-08-01-preview",
        azure_endpoint="https://adavi-mf694jmx-eastus2.cognitiveservices.azure.com"
    )
    print("✅ Azure Chat Client initialized")
except Exception as e:
    print(f"Warning: Could not initialize Azure Chat client: {e}")
    azure_chat_client = None

# Embeddings client (text-embedding-3-large)
azure_embeddings_client = None
try:
    azure_embeddings_client = AzureOpenAI(
        api_key=os.getenv("AZURE_EMBEDDINGS_API_KEY", "your_embeddings_api_key_here"),
        api_version="2023-05-15",
        azure_endpoint="https://rag-project-tfc.cognitiveservices.azure.com"
    )
    print("✅ Azure Embeddings Client initialized")
except Exception as e:
    print(f"Warning: Could not initialize Azure Embeddings client: {e}")
    azure_embeddings_client = None

# For backward compatibility
azure_client = azure_chat_client

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Simple text chunking by character count with overlap"""
    chunks = []
    words = text.split()
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1
        if current_size + word_size > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = current_chunk[-10:]  # Keep last 10 words for overlap
            current_size = sum(len(w) + 1 for w in current_chunk)
        
        current_chunk.append(word)
        current_size += word_size
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def generate_embedding(text: str) -> List[float]:
    """Generate embeddings using Azure OpenAI text-embedding-3-large"""
    if azure_embeddings_client:
        try:
            response = azure_embeddings_client.embeddings.create(
                model="text-embedding-3-large",  # Use the deployment name
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
    
    # Return random embedding for testing if Azure is not configured
    # text-embedding-3-large has 3072 dimensions
    np.random.seed(hash(text) % (2**32))  # Consistent embeddings for same text
    return np.random.randn(3072).tolist()

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    stream: bool = True
    use_rag: bool = True
    model: str = "gpt-5-mini"

class UploadResponse(BaseModel):
    message: str
    chunks_created: int
    filename: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """Upload and process a document for RAG"""
    try:
        content = await file.read()
        
        # Try to decode as text, handle binary files like PDFs
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            # Handle PDF files
            if file.content_type == 'application/pdf' or file.filename.lower().endswith('.pdf'):
                import io
                import PyPDF2
                
                try:
                    # Extract text from PDF
                    pdf_file = io.BytesIO(content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text() + "\n"
                    
                    if not text.strip():
                        text = f"[PDF file with no extractable text: {file.filename}]"
                except Exception as e:
                    print(f"Error extracting PDF text: {e}")
                    text = f"[Error processing PDF: {file.filename}]"
            else:
                # For other binary files
                text = f"[Binary file: {file.filename}]\nContent type: {file.content_type}\nSize: {len(content)} bytes"
        
        # Chunk the document
        chunks = chunk_text(text)
        
        # Generate embeddings and store
        for i, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)
            metadata = {
                "filename": file.filename,
                "chunk_index": i,
                "upload_time": datetime.now().isoformat()
            }
            vector_store.add_document(chunk, embedding, metadata)
        
        return UploadResponse(
            message="Document processed successfully",
            chunks_created=len(chunks),
            filename=file.filename
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: dict):
    """Chat endpoint with RAG support - accepts both ChatRequest and dict formats"""
    try:
        # Handle both request formats
        if hasattr(request, 'messages'):
            messages = request.messages
            use_rag = request.use_rag
            stream = request.stream
        else:
            # Handle dict format from /api/chat/fastapi
            query = request.get("query", "")
            session_id = request.get("session_id", "")
            max_tokens = request.get("max_tokens", 1000)
            temperature = request.get("temperature", 1)
            top_k = request.get("top_k", 5)
            stream = request.get("stream", True)
            use_rag = top_k > 0
            
            # Get system prompt from request or use default
            system_prompt = request.get("system_prompt")
            if not system_prompt:
                system_prompt = "You are HIPAA GPT, a helpful medical AI assistant. Provide clear, accurate, and professional responses."
            
            # Build messages for Azure format
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        
        # If RAG is enabled, enhance the last user message with context
        citations = []
        if use_rag and messages:
            last_message = messages[-1]["content"]
            
            # Generate embedding for the query
            query_embedding = generate_embedding(last_message)
            
            # Search for relevant documents
            results = vector_store.search(query_embedding, top_k=3)
            
            if results:
                context_parts = []
                for i, r in enumerate(results):
                    context_parts.append(f"[{i+1}] {r['content']}")
                    citations.append({
                        "index": i+1,
                        "filename": r["metadata"].get("filename", "Unknown"),
                        "chunk_index": r["metadata"].get("chunk_index", 0),
                        "score": r["score"]
                    })
                
                context = "\n\n".join(context_parts)
                enhanced_message = f"""Use the following context to answer the question. When referencing information from the context, include citation numbers like [1], [2], etc.

Context:
{context}

Question: {last_message}"""
                
                messages[-1]["content"] = enhanced_message
        
        # Generate response
        if not azure_client:
            # Return a mock response if Azure is not configured
            mock_response = "Azure OpenAI is not configured. This is a test response. "
            if use_rag and results:
                mock_response += f"Found {len(results)} relevant documents in the knowledge base."
            
            if stream:
                async def generate():
                    for word in mock_response.split():
                        yield f"data: {json.dumps({'content': word + ' '})}\n\n"
                        await asyncio.sleep(0.05)  # Simulate streaming
                    yield "data: [DONE]\n\n"
                return StreamingResponse(generate(), media_type="text/event-stream")
            else:
                return {"content": mock_response}
        
        if stream:
            async def generate():
                try:
                    # Send citations first if available
                    if citations:
                        citations_data = {
                            "choices": [{
                                "delta": {
                                    "content": "",
                                    "citations": citations
                                }
                            }]
                        }
                        yield f"data: {json.dumps(citations_data)}\n\n"
                    
                    stream = azure_client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=messages,
                        temperature=1,
                        max_completion_tokens=2000,
                        stream=True
                    )
                    
                    for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta.content:
                            # Format response to match Azure OpenAI SSE format
                            response_data = {
                                "choices": [{
                                    "delta": {
                                        "content": chunk.choices[0].delta.content
                                    }
                                }]
                            }
                            yield f"data: {json.dumps(response_data)}\n\n"
                    
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            response = azure_client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                temperature=1,
                max_completion_tokens=2000
            )
            return {"content": response.choices[0].message.content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "documents_count": len(vector_store.documents),
        "service": "Medical RAG Service",
        "azure_chat_configured": azure_chat_client is not None,
        "azure_embeddings_configured": azure_embeddings_client is not None
    }

@app.get("/documents/count")
async def document_count():
    """Get count of stored documents"""
    return {
        "total_chunks": len(vector_store.documents),
        "unique_files": len(set(m["filename"] for m in vector_store.metadata if "filename" in m))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)