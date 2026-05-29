from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import os

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
                    "context": {}
                },
                timeout=30.0
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
