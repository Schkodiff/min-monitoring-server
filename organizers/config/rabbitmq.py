import os

from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


async def get_rabbitmq_connection() -> AbstractRobustConnection:
    return await connect_robust(RABBITMQ_URL)
