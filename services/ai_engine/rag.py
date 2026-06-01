"""
RAG (Retrieval Augmented Generation) Module
Handles document ingestion, chunking, embedding, and retrieval
"""

import os
from typing import List, Dict, Any
import json
import redis

# Use Redis for shared storage across processes
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))


class SimpleRAG:
    """Simple RAG implementation using Redis for cross-process storage
    
    This implementation uses:
    - Redis for persistent storage (shared between API Gateway and AI Engine)
    - Keyword-based search with relevance scoring
    - 500-char chunks with 50-char overlap
    - Multi-tenant isolation via UUID-based keys
    
    Future upgrades:
    - Vector embeddings (OpenAI text-embedding-3-small)
    - Semantic search (Pinecone or Chroma)
    - Hybrid search (keyword + semantic)
    """
    
    def __init__(self):
        self.chunk_size = 500
        self.chunk_overlap = 50
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - self.chunk_overlap
        
        return chunks
    
    def ingest_document(self, tenant_id: str, doc_id: str, filename: str, content: str):
        """Ingest a document into the RAG knowledge base
        
        Args:
            tenant_id: UUID string for tenant isolation
            doc_id: Unique document identifier
            filename: Original filename
            content: Extracted text content
            
        Returns:
            Number of chunks created
            
        Storage: Redis key pattern: rag:{tenant_id}:{doc_id}
        """
        chunks = self.chunk_text(content)
        
        doc_data = {
            "filename": filename,
            "chunks": chunks,
            "chunk_count": len(chunks)
        }
        
        # Store in Redis
        key = f"rag:{tenant_id}:{doc_id}"
        redis_client.set(key, json.dumps(doc_data))
        
        return len(chunks)
    
    def search(self, tenant_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant document chunks using keyword matching
        
        Args:
            tenant_id: UUID string for tenant isolation
            query: User's search query
            top_k: Number of top results to return (default: 5)
            
        Returns:
            List of dicts with: content, source, doc_id, chunk_id, score
            
        Note: This is keyword-based. Upgrade to vector search for semantic understanding.
        """
        results = []
        query_lower = query.lower()
        query_words = [w for w in query_lower.split() if len(w) > 2]  # Filter short words
        
        # Get all documents for this tenant from Redis
        pattern = f"rag:{tenant_id}:*"
        for key in redis_client.scan_iter(match=pattern):
            doc_data_json = redis_client.get(key)
            if not doc_data_json:
                continue
            
            doc_data = json.loads(doc_data_json)
            doc_id = key.decode().split(':')[-1]
            
            for idx, chunk in enumerate(doc_data["chunks"]):
                chunk_lower = chunk.lower()
                # Count matching words
                matches = sum(1 for word in query_words if word in chunk_lower)
                if matches > 0:
                    score = matches / len(query_words) if query_words else 0
                    results.append({
                        "content": chunk,
                        "source": doc_data["filename"],
                        "doc_id": doc_id,
                        "chunk_id": idx,
                        "score": score
                    })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def get_context(self, tenant_id: str, query: str) -> str:
        """Get relevant context for a query"""
        results = self.search(tenant_id, query, top_k=5)
        
        if not results:
            return ""
        
        context_parts = []
        for r in results:
            context_parts.append(r['content'])
        
        return "\n\n".join(context_parts)
    
    def list_documents(self, tenant_id: str) -> List[Dict[str, Any]]:
        """List all documents for a tenant"""
        documents = []
        pattern = f"rag:{tenant_id}:*"
        
        for key in redis_client.scan_iter(match=pattern):
            doc_data_json = redis_client.get(key)
            if not doc_data_json:
                continue
            
            doc_data = json.loads(doc_data_json)
            doc_id = key.decode().split(':')[-1]
            
            documents.append({
                "doc_id": doc_id,
                "filename": doc_data["filename"],
                "chunks": doc_data["chunk_count"]
            })
        
        return documents
    
    def delete_document(self, tenant_id: str, doc_id: str):
        """Delete a document"""
        key = f"rag:{tenant_id}:{doc_id}"
        return redis_client.delete(key) > 0


# Global RAG instance
rag = SimpleRAG()


def process_pdf(file_path: str) -> str:
    """Extract text from PDF"""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except ImportError:
        return "PyPDF2 not installed. Install with: pip install pypdf2"
    except Exception as e:
        return f"Error processing PDF: {str(e)}"


def process_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error processing TXT: {str(e)}"


def process_docx(file_path: str) -> str:
    """Extract text from DOCX"""
    try:
        import docx
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except ImportError:
        return "python-docx not installed. Install with: pip install python-docx"
    except Exception as e:
        return f"Error processing DOCX: {str(e)}"
