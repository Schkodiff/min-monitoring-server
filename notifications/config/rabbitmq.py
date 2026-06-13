import os
from dotenv import load_dotenv
from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection

# Load environment variables
load_dotenv()

# RabbitMQ settings
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

async def get_rabbitmq_connection() -> AbstractRobustConnection:
    """Get RabbitMQ connection"""
    return await connect_robust(RABBITMQ_URL)
