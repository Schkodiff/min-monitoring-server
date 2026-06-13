import asyncio
import json
import os
import urllib.error
import urllib.request
from uuid import UUID

from config.database import SessionLocal
from config.messaging import EXCHANGE_NAME, EXCHANGE_TYPE, NOTIFICATIONS_QUEUE, QUEUE_BINDINGS, NULL_LOTTERY_ID
from config.rabbitmq import get_rabbitmq_connection
from models.enums import NotificationType
from models.notification import Notification

class NotificationWorker:
    def __init__(self, bot_notification_url: str | None = None):
        self.bot_notification_url = bot_notification_url or os.getenv(
            "BOT_NOTIFICATION_URL",
            "http://0.0.0.0:8080/api/status",
        )

    async def process_notification(self, notification_data: dict):
        """Process a notification from the queue"""
        notification_type = NotificationType(notification_data["type"])
        self.persist_incoming_notification(notification_data, notification_type)

        if notification_type == NotificationType.win:
            await self.send_win_notification(notification_data)
        elif notification_type == NotificationType.ticketBuyApproval:
            await self.send_ticket_approval(notification_data)
        elif notification_type == NotificationType.endOfLottery:
            await self.send_lottery_end_notification(notification_data)
        elif notification_type == NotificationType.lotteryStartsSoon:
            await self.send_lottery_starts_soon_notification(notification_data)
        elif notification_type == NotificationType.orgRegReqApproval:
            await self.send_org_registration_approval(notification_data)
        elif notification_type == NotificationType.orgRegReqRejection:
            await self.send_org_registration_rejection(notification_data)
        elif notification_type == NotificationType.ticketBuyRejection:
            await self.send_ticket_rejection(notification_data)
        elif notification_type == NotificationType.accountBan:
            await self.send_account_ban_notification(notification_data)
        elif notification_type == NotificationType.lotteryCancellation:
            await self.send_lottery_cancellation(notification_data)
        elif notification_type == NotificationType.postByOrg:
            await self.send_org_post_notification(notification_data)

        await self.forward_to_bot(notification_data)
        print(f"Processed notification: {notification_data}")

    def persist_incoming_notification(
        self,
        notification_data: dict,
        notification_type: NotificationType,
    ) -> None:
        if notification_data.get("id"):
            return

        session = SessionLocal()
        try:
            notification = Notification(
                type=notification_type,
                message=notification_data["message"],
                author=self.parse_uuid(notification_data.get("author")),
                receiver=UUID(notification_data["receiver"]),
                lottery_id=UUID(notification_data.get("lottery_id") or NULL_LOTTERY_ID),
            )
            session.add(notification)
            session.commit()
            session.refresh(notification)
            notification_data["id"] = str(notification.id)
            notification_data["created_at"] = notification.created_at.isoformat()
        except Exception as exc:
            session.rollback()
            print(f"Error storing notification event: {exc}")
        finally:
            session.close()

    @staticmethod
    def parse_uuid(value):
        if not value:
            return None
        return UUID(value)

    async def forward_to_bot(self, data: dict):
        """Forward notification payload to the Telegram bot HTTP endpoint."""
        if not self.bot_notification_url:
            return

        await asyncio.to_thread(self.post_to_bot, data)

    def post_to_bot(self, data: dict):
        body = json.dumps(data, default=str).encode("utf-8")
        request = urllib.request.Request(
            self.bot_notification_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                response_body = response.read().decode("utf-8", errors="replace")
                print(
                    "Forwarded notification to Telegram bot "
                    f"({response.status}): {response_body}"
                )
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            print(
                "Telegram bot notification failed "
                f"({exc.code}): {error_body}"
            )
        except Exception as exc:
            print(f"Telegram bot notification failed: {exc}")

    async def send_win_notification(self, data: dict):
        """Send win notification via email/SMS"""
        # TODO: Implement email/SMS sending logic here
        print(f"Sending win notification to {data['receiver']}: {data['message']}")

    async def send_ticket_approval(self, data: dict):
        """Send ticket approval notification"""
        print(f"Sending ticket approval to {data['receiver']}: {data['message']}")

    async def send_lottery_end_notification(self, data: dict):
        """Send lottery end notification"""
        print(f"Sending lottery end notification to {data['receiver']}: {data['message']}")

    async def send_lottery_starts_soon_notification(self, data: dict):
        """Send lottery starts soon notification"""
        print(f"Sending lottery starts soon notification to {data['receiver']}: {data['message']}")

    async def send_org_registration_approval(self, data: dict):
        """Send organization registration approval"""
        print(f"Sending org registration approval to {data['receiver']}: {data['message']}")

    async def send_org_registration_rejection(self, data: dict):
        """Send organization registration rejection"""
        print(f"Sending org registration rejection to {data['receiver']}: {data['message']}")

    async def send_ticket_rejection(self, data: dict):
        """Send ticket rejection notification"""
        print(f"Sending ticket rejection to {data['receiver']}: {data['message']}")

    async def send_account_ban_notification(self, data: dict):
        """Send account ban notification"""
        print(f"Sending account ban notification to {data['receiver']}: {data['message']}")

    async def send_lottery_cancellation(self, data: dict):
        """Send lottery cancellation notification"""
        print(f"Sending lottery cancellation to {data['receiver']}: {data['message']}")

    async def send_org_post_notification(self, data: dict):
        """Send organization post notification"""
        print(f"Sending org post notification to {data['receiver']}: {data['message']}")

    async def run(self):
        """Start the worker"""
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
            await channel.set_qos(prefetch_count=10)

            print("Notification worker started. Waiting for messages...")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            notification_data = json.loads(message.body.decode())
                            await self.process_notification(notification_data)
                        except Exception as e:
                            print(f"Error processing message: {e}")


if __name__ == "__main__":
    worker = NotificationWorker()
    asyncio.run(worker.run())
