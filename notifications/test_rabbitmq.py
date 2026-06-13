#!/usr/bin/env python3
"""
Test script to demonstrate RabbitMQ integration
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.message_publisher import MessagePublisher
from workers.notification_worker import NotificationWorker

async def test_rabbitmq():
    """Test RabbitMQ publishing and consuming"""
    print("Testing RabbitMQ integration...")

    # Test data
    test_notification = {
        "type": "win",
        "message": "Congratulations! You won the lottery!",
        "receiver": "00000000-0000-0000-0000-000000000001",
        "lottery_id": "00000000-0000-0000-0000-000000000002",
        "created_at": "2024-01-01T12:00:00"
    }

    # Publish message
    print("Publishing test notification...")
    await MessagePublisher().publish_notification(test_notification)

    print("Test completed. The notification should be processed by the worker.")

if __name__ == "__main__":
    asyncio.run(test_rabbitmq())
