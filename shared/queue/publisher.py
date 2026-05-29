import aio_pika
import json
import os
from typing import Dict, Any
from .events import Event


class MessagePublisher:
    def __init__(self):
        self.rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://chatbot:chatbot_dev@localhost:5672")
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()

    async def publish(self, event: Event, routing_key: str = "events"):
        if not self.channel:
            await self.connect()

        exchange = await self.channel.declare_exchange(
            "chatbot_events", aio_pika.ExchangeType.TOPIC, durable=True
        )

        message = aio_pika.Message(
            body=event.model_dump_json().encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await exchange.publish(message, routing_key=routing_key)

    async def close(self):
        if self.connection:
            await self.connection.close()
