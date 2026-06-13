"""Shared RabbitMQ topology constants (keep in sync across all microservices)."""

EXCHANGE_NAME = "diplom_exchange"
EXCHANGE_TYPE = "topic"
NOTIFICATIONS_QUEUE = "notifications_queue"

NULL_LOTTERY_ID = "00000000-0000-0000-0000-000000000000"

SERVICE_ROUTING_KEYS = {
    "lottery": "lottery.notification",
    "organizers": "organizers.notification",
    "users": "users.notification",
    "notifications": "notifications.notification",
}

QUEUE_BINDINGS = list(SERVICE_ROUTING_KEYS.values())


def routing_key_for(service: str) -> str:
    key = SERVICE_ROUTING_KEYS.get(service)
    if not key:
        raise ValueError(f"Unknown service: {service}")
    return key
