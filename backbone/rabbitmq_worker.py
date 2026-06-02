import json
import os
import time

try:
    import pika
except ImportError:  # pragma: no cover - 依赖缺失时自动降级
    pika = None

from redis import Redis
from redis.exceptions import RedisError


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@127.0.0.1:5672/%2F")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "library.events")
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")


def get_redis_client():
    try:
        client = Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        client.ping()
        return client
    except (RedisError, ValueError):
        return None


def handle_message(ch, method, properties, body):
    try:
        message = json.loads(body)
    except json.JSONDecodeError:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    event_type = message.get("event_type")
    payload = message.get("payload", {})
    redis_client = get_redis_client()

    if redis_client is not None:
        try:
            if event_type == "search.books":
                query = str(payload.get("query", "")).strip().lower()
                if query:
                    redis_client.zincrby("analytics:search_terms", 1, query)
                    redis_client.expire("analytics:search_terms", 60 * 60 * 24 * 30)
            elif event_type == "auth.login_success":
                redis_client.incr("analytics:login_success_total")
            elif event_type == "auth.login_failed":
                redis_client.incr("analytics:login_failed_total")
        except RedisError:
            pass

    print(f"RabbitMQ event consumed: {event_type} -> {payload}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def run_worker():
    if pika is None:
        raise RuntimeError("pika is not installed")

    while True:
        connection = None
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=handle_message)
            print("RabbitMQ worker started")
            channel.start_consuming()
        except Exception as exc:
            print(f"RabbitMQ worker error: {exc}")
            time.sleep(3)
        finally:
            if connection is not None and connection.is_open:
                try:
                    connection.close()
                except Exception:
                    pass


if __name__ == "__main__":
    run_worker()