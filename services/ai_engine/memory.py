import redis.asyncio as redis
import json
import os
from typing import List, Dict, Any
from datetime import datetime


class ConversationMemory:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = None
        self.ttl = 86400  # 24 hours

    async def _get_client(self):
        if not self.client:
            self.client = await redis.from_url(self.redis_url, decode_responses=True)
        return self.client

    async def get_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        client = await self._get_client()
        key = f"conversation:{conversation_id}:history"
        
        messages = await client.lrange(key, 0, -1)
        return [json.loads(msg) for msg in messages]

    async def add_message(self, conversation_id: str, role: str, content: str):
        client = await self._get_client()
        key = f"conversation:{conversation_id}:history"
        
        message = json.dumps({
            "role": role,
            "content": content,
            "timestamp": str(datetime.utcnow())
        })
        
        await client.rpush(key, message)
        await client.expire(key, self.ttl)

    async def clear_history(self, conversation_id: str):
        client = await self._get_client()
        key = f"conversation:{conversation_id}:history"
        await client.delete(key)

    async def get_context(self, conversation_id: str) -> Dict[str, Any]:
        client = await self._get_client()
        key = f"conversation:{conversation_id}:context"
        
        context = await client.get(key)
        return json.loads(context) if context else {}

    async def set_context(self, conversation_id: str, context: Dict[str, Any]):
        client = await self._get_client()
        key = f"conversation:{conversation_id}:context"
        
        await client.set(key, json.dumps(context), ex=self.ttl)
