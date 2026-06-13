import asyncio
import json
from typing import Any, Dict, Optional

from aio_pika import DeliveryMode, Message

from config.messaging import (
    EXCHANGE_NAME,
    EXCHANGE_TYPE,
    NOTIFICATIONS_QUEUE,
    QUEUE_BINDINGS,
    routing_key_for,
)
from config.rabbitmq import get_rabbitmq_connection


class MessagePublisher:
    def __init__(self, source_service: str = "users"):
        self.source_service = source_service

    async def publish_notification(
        self,
        notification_data: Dict[str, Any],
        routing_key: Optional[str] = None,
    ) -> None:
        routing_key = routing_key or routing_key_for(self.source_service)
        payload = {**notification_data, "source": self.source_service}

        connection = await get_rabbitmq_connection()
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                EXCHANGE_NAME,
                type=EXCHANGE_TYPE,
                durable=True,
            )
            queue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)
            for binding in QUEUE_BINDINGS:
                await queue.bind(exchange, binding)

            message = Message(
                json.dumps(payload, default=str).encode("utf-8"),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
                headers={"source": self.source_service},
            )
            await exchange.publish(message, routing_key=routing_key)

    async def publish_notification_safe(
        self,
        notification_data: Dict[str, Any],
        routing_key: Optional[str] = None,
    ) -> None:
        try:
            await self.publish_notification(notification_data, routing_key)
        except Exception as exc:
            print(f"Failed to publish notification event from {self.source_service}: {exc}")

    def publish_notification_background(
        self,
        notification_data: Dict[str, Any],
        routing_key: Optional[str] = None,
    ) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self.publish_notification_safe(notification_data, routing_key))
        else:
            loop.create_task(self.publish_notification_safe(notification_data, routing_key))


def get_message_publisher() -> MessagePublisher:
    return MessagePublisher()
