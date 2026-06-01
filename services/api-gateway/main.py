from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
import sys
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.database import get_db
from shared.models import ConversationModel, MessageModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from services.ai_engine.rag import rag, process_pdf, process_txt, process_docx

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://localhost:8001")
SMS_GATEWAY_URL = os.getenv("SMS_GATEWAY_URL", "http://localhost:8002")
QUALIFICATION_ENGINE_URL = os.getenv("QUALIFICATION_ENGINE_URL", "http://localhost:8003")
SCHEDULING_SERVICE_URL = os.getenv("SCHEDULING_SERVICE_URL", "http://localhost:8004")


async def verify_tenant(x_tenant_id: str = Header(...)):
    """Verify tenant authentication"""
    # In production: validate API key, check tenant exists, etc.
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing tenant ID")
    return x_tenant_id


class ChatRequest(BaseModel):
    phone_number: str
    message: str
    provider: Optional[str] = "ollama"  # ollama, openai, anthropic


class SendSMSRequest(BaseModel):
    to: str
    message: str


@app.post("/api/v1/chat")
async def chat(request: ChatRequest, tenant_id: str = Depends(verify_tenant)):
    """Route chat request to AI Engine"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AI_ENGINE_URL}/chat",
                json={
                    "conversation_id": request.phone_number,
                    "tenant_id": tenant_id,
                    "message": request.message,
                    "context": {},
                    "provider": request.provider
                },
                timeout=60.0
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"AI Engine unavailable: {str(e)}")


@app.post("/api/v1/sms/send")
async def send_sms(request: SendSMSRequest, tenant_id: str = Depends(verify_tenant)):
    """Route SMS send request to SMS Gateway"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SMS_GATEWAY_URL}/send",
                json={
                    "to": request.to,
                    "message": request.message,
                    "tenant_id": tenant_id
                },
                timeout=10.0
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"SMS Gateway unavailable: {str(e)}")


@app.get("/api/v1/availability")
async def get_availability(
    start_date: str,
    end_date: str,
    tenant_id: str = Depends(verify_tenant)
):
    """Route availability request to Scheduling Service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SCHEDULING_SERVICE_URL}/availability",
                json={
                    "tenant_id": tenant_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "duration_minutes": 30
                },
                timeout=10.0
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Scheduling Service unavailable: {str(e)}")


@app.get("/api/v1/conversations")
async def get_conversations(tenant_id: str = Depends(verify_tenant), db: Session = Depends(get_db)):
    """Get all conversations for a tenant"""
    try:
        tenant_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, tenant_id)
        
        conversations = db.query(ConversationModel).filter_by(tenant_id=tenant_uuid).all()
        
        result = []
        for conv in conversations:
            message_count = db.query(func.count(MessageModel.id)).filter_by(conversation_id=conv.id).scalar()
            last_message = db.query(MessageModel).filter_by(conversation_id=conv.id).order_by(MessageModel.created_at.desc()).first()
            
            result.append({
                "id": str(conv.id),
                "phone_number": conv.phone_number,
                "status": conv.status.value,
                "created_at": conv.created_at.isoformat(),
                "message_count": message_count,
                "last_message": last_message.content[:100] if last_message else None
            })
        
        return {"conversations": result, "total": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, tenant_id: str = Depends(verify_tenant), db: Session = Depends(get_db)):
    """Get all messages for a conversation"""
    try:
        conv_uuid = uuid.UUID(conversation_id)
        
        messages = db.query(MessageModel).filter_by(conversation_id=conv_uuid).order_by(MessageModel.created_at).all()
        
        return {
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role.value,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Depends(verify_tenant)
):
    """Upload and process a document for RAG knowledge base"""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.txt', '.docx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file temporarily
        upload_dir = "./uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        doc_id = str(uuid.uuid4())
        file_path = os.path.join(upload_dir, f"{doc_id}{file_ext}")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract text based on file type
        if file_ext == '.pdf':
            text = process_pdf(file_path)
        elif file_ext == '.txt':
            text = process_txt(file_path)
        elif file_ext == '.docx':
            text = process_docx(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Convert tenant_id to consistent format for RAG
        try:
            tenant_uuid = uuid.UUID(tenant_id)
            rag_tenant_id = str(tenant_uuid)
        except ValueError:
            # If not a UUID, create deterministic UUID from string
            tenant_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, tenant_id)
            rag_tenant_id = str(tenant_uuid)
        
        # Ingest into RAG
        chunks_count = rag.ingest_document(rag_tenant_id, doc_id, file.filename, text)
        
        # Clean up temp file
        os.remove(file_path)
        
        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "status": "processed",
            "chunks": chunks_count,
            "message": f"Document processed successfully with {chunks_count} chunks"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/documents")
async def list_documents(tenant_id: str = Depends(verify_tenant)):
    """List all documents in knowledge base"""
    try:
        try:
            tenant_uuid = uuid.UUID(tenant_id)
            rag_tenant_id = str(tenant_uuid)
        except ValueError:
            tenant_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, tenant_id)
            rag_tenant_id = str(tenant_uuid)
        
        documents = rag.list_documents(rag_tenant_id)
        return {"documents": documents, "total": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/documents/{doc_id}")
async def delete_document(doc_id: str, tenant_id: str = Depends(verify_tenant)):
    """Delete a document from knowledge base"""
    try:
        try:
            tenant_uuid = uuid.UUID(tenant_id)
            rag_tenant_id = str(tenant_uuid)
        except ValueError:
            tenant_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, tenant_id)
            rag_tenant_id = str(tenant_uuid)
        
        success = rag.delete_document(rag_tenant_id, doc_id)
        if success:
            return {"status": "deleted", "doc_id": doc_id}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/documents/search")
async def search_documents(query: str, tenant_id: str = Depends(verify_tenant)):
    """Test RAG search directly"""
    try:
        try:
            tenant_uuid = uuid.UUID(tenant_id)
            rag_tenant_id = str(tenant_uuid)
        except ValueError:
            tenant_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, tenant_id)
            rag_tenant_id = str(tenant_uuid)
        
        results = rag.search(rag_tenant_id, query, top_k=5)
        context = rag.get_context(rag_tenant_id, query)
        
        return {
            "query": query,
            "tenant_id": rag_tenant_id,
            "results_count": len(results),
            "results": results,
            "context_length": len(context),
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics")
async def get_analytics(tenant_id: str = Depends(verify_tenant), db: Session = Depends(get_db)):
    """Get analytics for a tenant"""
    try:
        tenant_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, tenant_id)
        
        total_conversations = db.query(func.count(ConversationModel.id)).filter_by(tenant_id=tenant_uuid).scalar()
        active_conversations = db.query(func.count(ConversationModel.id)).filter_by(tenant_id=tenant_uuid, status='ACTIVE').scalar()
        total_messages = db.query(func.count(MessageModel.id)).join(ConversationModel).filter(ConversationModel.tenant_id == tenant_uuid).scalar()
        
        avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
        
        return {
            "total_conversations": total_conversations,
            "active_conversations": active_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": round(avg_messages, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    services = {
        "ai_engine": AI_ENGINE_URL,
        "sms_gateway": SMS_GATEWAY_URL,
        "qualification_engine": QUALIFICATION_ENGINE_URL,
        "scheduling_service": SCHEDULING_SERVICE_URL
    }
    
    status = {"gateway": "healthy", "services": {}}
    
    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f"{url}/health", timeout=5.0)
                status["services"][service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                status["services"][service_name] = "unreachable"
    
    return status


@app.get("/")
async def root():
    return {
        "service": "AI Conversational Platform API Gateway",
        "version": "1.0.0",
        "docs": "/docs"
    }
