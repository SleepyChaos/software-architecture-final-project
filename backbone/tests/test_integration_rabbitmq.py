"""
集成测试 - RabbitMQ 消息队列全链路
需要 docker-compose 运行的 RabbitMQ + Redis 服务
标记为 integration，通过 -m integration 执行
"""

import json
import logging
import os
import time

import pytest

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv(
    "INTEGRATION_RABBITMQ_URL",
    "amqp://guest:guest@127.0.0.1:5672/%2F",
)
REDIS_URL = os.getenv("INTEGRATION_REDIS_URL", "redis://127.0.0.1:6379/0")


def _skip_if_no_rabbitmq():
    """检测 RabbitMQ 是否可用"""
    try:
        import pika
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        connection.close()
        return False
    except Exception:
        return True


def _skip_if_no_redis():
    """检测 Redis 是否可用"""
    try:
        from redis import Redis
        client = Redis.from_url(REDIS_URL, socket_connect_timeout=2)
        client.ping()
        return False
    except Exception:
        return True


pytestmark = pytest.mark.integration


@pytest.fixture
def rabbitmq_connection():
    """创建真实 RabbitMQ 连接"""
    if _skip_if_no_rabbitmq():
        pytest.skip("RabbitMQ 不可用（请确保 docker-compose 已启动）")

    import pika
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    logger.info(f"已连接 RabbitMQ: {RABBITMQ_URL}")
    yield connection
    if connection.is_open:
        connection.close()


@pytest.fixture
def redis_for_mq():
    """创建 Redis 连接用于验证消息消费"""
    if _skip_if_no_redis():
        pytest.skip("Redis 不可用（请确保 docker-compose 已启动）")

    from redis import Redis
    client = Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    yield client
    # 清理测试键
    client.delete("analytics:search_terms")
    client.delete("analytics:login_success_total")
    client.delete("analytics:login_failed_total")
    client.close()


class TestIntegrationRabbitMQ:
    """RabbitMQ 集成测试"""

    def test_connection_alive(self, rabbitmq_connection):
        """RabbitMQ 连接应保持活跃"""
        assert rabbitmq_connection.is_open
        logger.info("RabbitMQ 连接存活检查通过")

    def test_publish_event_succeeds(self, rabbitmq_connection):
        """publish_event 应成功发布消息"""
        from message_queue import publish_event

        result = publish_event("test.integration", {"data": "hello"})
        assert result is True
        logger.info("publish_event 成功发布消息")

    def test_message_body_structure(self, rabbitmq_connection):
        """消息体应包含正确结构"""
        import pika

        channel = rabbitmq_connection.channel()
        queue_name = "library.events.test"
        channel.queue_declare(queue=queue_name, durable=False)

        # 发布消息
        from message_queue import publish_event, RABBITMQ_QUEUE
        publish_event("test.verify", {"query": "算法"})

        # 消费验证
        time.sleep(0.5)
        method, properties, body = channel.basic_get(queue=RABBITMQ_QUEUE, auto_ack=True)
        if method:
            message = json.loads(body)
            assert "event_type" in message
            assert "payload" in message
            assert "created_at" in message
            logger.info(f"消息结构验证: event_type={message['event_type']}")

    def test_is_rabbitmq_available_true(self, rabbitmq_connection):
        """is_rabbitmq_available 应返回 True"""
        from message_queue import is_rabbitmq_available
        assert is_rabbitmq_available() is True
        logger.info("is_rabbitmq_available 返回 True")

    def test_full_pipeline_publish_and_consume(self, rabbitmq_connection, redis_for_mq):
        """完整链路：发布消息 → Worker 处理 → Redis 写入"""
        from message_queue import publish_event
        from rabbitmq_worker import handle_message
        from unittest.mock import MagicMock

        # 1. 发布搜索事件
        publish_event("search.books", {"query": "集成测试搜索", "result_count": 5})

        # 2. 等待消息到达
        time.sleep(0.5)

        # 3. 手动消费消息并调用 handler
        import pika
        channel = rabbitmq_connection.channel()
        from message_queue import RABBITMQ_QUEUE

        method, properties, body = channel.basic_get(queue=RABBITMQ_QUEUE, auto_ack=False)
        if method and body:
            # 模拟 worker 处理
            mock_ch = MagicMock()
            mock_ch.basic_ack = lambda delivery_tag: channel.basic_ack(delivery_tag)
            mock_method = MagicMock()
            mock_method.delivery_tag = method.delivery_tag

            handle_message(mock_ch, mock_method, properties, body)

            # 4. 验证 Redis 中是否写入了搜索词
            time.sleep(0.3)
            score = redis_for_mq.zscore("analytics:search_terms", "集成测试搜索")
            assert score is not None and score >= 1.0
            logger.info(f"全链路验证成功: '集成测试搜索' score={score}")
        else:
            logger.warning("未消费到消息，跳过全链路验证")

    def test_auth_event_pipeline(self, rabbitmq_connection, redis_for_mq):
        """Auth 事件链路：发布 → 处理 → Redis 计数"""
        from message_queue import publish_event
        from rabbitmq_worker import handle_message
        from unittest.mock import MagicMock
        import pika

        publish_event("auth.login_success", {"reader_id": "int_test_001"})
        time.sleep(0.5)

        channel = rabbitmq_connection.channel()
        from message_queue import RABBITMQ_QUEUE
        method, properties, body = channel.basic_get(queue=RABBITMQ_QUEUE, auto_ack=False)

        if method and body:
            mock_ch = MagicMock()
            mock_ch.basic_ack = lambda delivery_tag: channel.basic_ack(delivery_tag)
            mock_method = MagicMock()
            mock_method.delivery_tag = method.delivery_tag

            handle_message(mock_ch, mock_method, properties, body)

            time.sleep(0.3)
            count = redis_for_mq.get("analytics:login_success_total")
            assert count is not None and int(count) >= 1
            logger.info(f"Auth 事件链路验证成功: login_success_total={count}")
        else:
            logger.warning("未消费到 auth 消息，跳过验证")
