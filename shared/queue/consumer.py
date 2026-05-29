import aio_pika
import json
import os
from typing import Callable, List
from .events import Event


class MessageConsumer:
    def __init__(self, queue_name: str, routing_keys: List[str]):
        self.rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://chatbot:chatbot_dev@localhost:5672")
        self.queue_name = queue_name
        self.routing_keys = routing_keys
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)

    async def consume(self, callback: Callable):
        if not self.channel:
            await self.connect()

        exchange = await self.channel.declare_exchange(
            "chatbot_events", aio_pika.ExchangeType.TOPIC, durable=True
        )

        queue = await self.channel.declare_queue(self.queue_name, durable=True)

        for routing_key in self.routing_keys:
            await queue.bind(exchange, routing_key=routing_key)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    event_data = json.loads(message.body.decode())
                    event = Event(**event_data)
                    await callback(event)

    async def close(self):
        if self.connection:
            await self.connection.close()
