from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os
import httpx
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage, SystemMessage


class AIProvider(ABC):
    @abstractmethod
    async def generate_response(
        self, message: str, history: List[Dict], system_prompt: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass


class OpenAIProvider(AIProvider):
    def __init__(self):
        self.client = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )

    async def generate_response(
        self, message: str, history: List[Dict], system_prompt: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        messages = [SystemMessage(content=system_prompt)]
        
        for msg in history[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=message))
        
        response = await self.client.ainvoke(messages)
        
        return {
            "content": response.content,
            "intent": self._extract_intent(message),
            "metadata": {"model": "gpt-4-turbo-preview"}
        }

    def _extract_intent(self, message: str) -> str:
        message_lower = message.lower()
        if any(word in message_lower for word in ["book", "schedule", "appointment"]):
            return "schedule_appointment"
        elif any(word in message_lower for word in ["price", "cost", "how much"]):
            return "pricing_inquiry"
        elif any(word in message_lower for word in ["help", "support", "agent"]):
            return "request_help"
        return "general_inquiry"


class AnthropicProvider(AIProvider):
    def __init__(self):
        self.client = ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0.7,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    async def generate_response(
        self, message: str, history: List[Dict], system_prompt: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        messages = [SystemMessage(content=system_prompt)]
        
        for msg in history[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=message))
        
        response = await self.client.ainvoke(messages)
        
        return {
            "content": response.content,
            "intent": None,
            "metadata": {"model": "claude-3-sonnet"}
        }


class OllamaProvider(AIProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")

    async def generate_response(
        self, message: str, history: List[Dict], system_prompt: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Build conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        messages.append({"role": "user", "content": message})
        
        # Call Ollama API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                }
            )
            
            result = response.json()
            content = result["message"]["content"]
        
        return {
            "content": content,
            "intent": self._extract_intent(message),
            "metadata": {"model": self.model}
        }

    def _extract_intent(self, message: str) -> str:
        message_lower = message.lower()
        if any(word in message_lower for word in ["book", "schedule", "appointment"]):
            return "schedule_appointment"
        elif any(word in message_lower for word in ["price", "cost", "how much"]):
            return "pricing_inquiry"
        elif any(word in message_lower for word in ["help", "support", "agent"]):
            return "request_help"
        return "general_inquiry"
