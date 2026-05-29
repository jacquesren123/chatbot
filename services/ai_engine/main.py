from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.ai_engine.providers import AIProvider, OpenAIProvider, AnthropicProvider, OllamaProvider
from services.ai_engine.memory import ConversationMemory
from shared.queue import MessagePublisher, Event, EventType
from shared.models import Message, MessageRole

app = FastAPI(title="AI Engine Service")

publisher = MessagePublisher()


class ChatRequest(BaseModel):
    conversation_id: str
    tenant_id: str
    message: str
    context: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    should_escalate: bool = False
    metadata: Dict[str, Any] = {}


class AIEngine:
    def __init__(self):
        self.providers = {}
        self.memory = ConversationMemory()

    def _get_provider(self, provider_name: str) -> AIProvider:
        """Lazy-load providers only when needed"""
        if provider_name not in self.providers:
            if provider_name == "openai":
                self.providers[provider_name] = OpenAIProvider()
            elif provider_name == "anthropic":
                self.providers[provider_name] = AnthropicProvider()
            elif provider_name == "ollama":
                self.providers[provider_name] = OllamaProvider()
            else:
                raise ValueError(f"Unknown AI provider: {provider_name}")
        return self.providers[provider_name]

    async def process_message(
        self, conversation_id: str, tenant_id: str, message: str, context: Dict[str, Any], provider: str = "ollama"
    ) -> ChatResponse:
        ai_provider = self._get_provider(provider)

        history = await self.memory.get_history(conversation_id)
        
        system_prompt = self._build_system_prompt(context)
        
        response = await ai_provider.generate_response(
            message=message,
            history=history,
            system_prompt=system_prompt,
            context=context
        )

        await self.memory.add_message(conversation_id, MessageRole.USER, message)
        await self.memory.add_message(conversation_id, MessageRole.ASSISTANT, response["content"])

        should_escalate = self._detect_escalation(response["content"], context)

        return ChatResponse(
            response=response["content"],
            intent=response.get("intent"),
            should_escalate=should_escalate,
            metadata=response.get("metadata", {})
        )

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        return f"""You are an AI assistant for a business helping with lead qualification and appointment scheduling.

Business Context:
- Business Name: {context.get('business_name', 'Our Company')}
- Services: {context.get('services', 'Various services')}

Your goals:
1. Engage naturally and professionally via SMS
2. Qualify leads by understanding their needs
3. Answer common questions
4. Schedule appointments when appropriate
5. Escalate to human agents when needed

Keep responses concise (SMS-friendly, under 160 characters when possible).
"""

    def _detect_escalation(self, response: str, context: Dict[str, Any]) -> bool:
        escalation_keywords = ["speak to someone", "human", "agent", "representative", "manager"]
        return any(keyword in response.lower() for keyword in escalation_keywords)


engine = AIEngine()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await engine.process_message(
            conversation_id=request.conversation_id,
            tenant_id=request.tenant_id,
            message=request.message,
            context=request.context
        )

        if response.should_escalate:
            await publisher.publish(
                Event(
                    type=EventType.CONVERSATION_ESCALATED,
                    tenant_id=request.tenant_id,
                    payload={"conversation_id": request.conversation_id}
                ),
                routing_key="conversation.escalated"
            )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
