#!/usr/bin/env python3
"""
Script to run the notification worker
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workers.notification_worker import NotificationWorker
import asyncio

if __name__ == "__main__":
    print("Starting notification worker...")
    worker = NotificationWorker()
    asyncio.run(worker.run())