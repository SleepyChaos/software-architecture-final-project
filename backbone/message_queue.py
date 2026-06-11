import json
import os
import time
from typing import Any

try:
    import pika
except ImportError:  # pragma: no cover - 依赖缺失时自动降级
    pika = None


RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://guest:guest@127.0.0.1:5672/%2F"
)
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "library.events")


def publish_event(event_type: str, payload: dict[str, Any]) -> bool:
    if pika is None:
        return False

    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(
                {
                    "event_type": event_type,
                    "payload": payload,
                    "created_at": time.time(),
                },
                ensure_ascii=False,
            ),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
        return True
    except Exception:
        return False


def is_rabbitmq_available() -> bool:
    if pika is None:
        return False

    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        connection.close()
        return True
    except Exception:
        return False
