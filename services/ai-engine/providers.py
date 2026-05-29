from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os
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
            model="claude-3-sonnet-20240229",
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
