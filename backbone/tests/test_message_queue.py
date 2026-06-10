"""
单元测试 - RabbitMQ 消息发布
测试 message_queue.py 中的 publish_event 和 is_rabbitmq_available
"""

import json
import logging
from unittest.mock import MagicMock, patch

import pytest

import message_queue as mq_module
from message_queue import is_rabbitmq_available, publish_event

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# publish_event 测试
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPublishEvent:
    """publish_event 函数测试"""

    def test_returns_false_when_pika_missing(self):
        """pika 模块缺失时应返回 False"""
        original_pika = mq_module.pika
        mq_module.pika = None

        result = publish_event("test.event", {"key": "value"})
        assert result is False
        logger.info("pika 缺失时 publish_event 返回 False")

        mq_module.pika = original_pika

    def test_returns_true_on_success(self):
        """成功发布消息时应返回 True"""
        mock_pika = MagicMock()
        mock_connection = MagicMock()
        mock_channel = MagicMock()

        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        with patch.object(mq_module, "pika", mock_pika):
            result = publish_event("auth.login_success", {"reader_id": "001"})

        assert result is True
        mock_channel.basic_publish.assert_called_once()
        mock_connection.close.assert_called_once()
        logger.info("成功发布消息，返回 True")

    def test_message_body_structure(self):
        """消息体应包含 event_type, payload, created_at"""
        mock_pika = MagicMock()
        mock_connection = MagicMock()
        mock_channel = MagicMock()

        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        with patch.object(mq_module, "pika", mock_pika):
            publish_event("search.books", {"query": "算法", "result_count": 5})

        # 解析发送的消息体
        call_args = mock_channel.basic_publish.call_args
        body_str = call_args.kwargs.get("body") or call_args[1].get("body")
        body = json.loads(body_str)

        assert body["event_type"] == "search.books"
        assert body["payload"]["query"] == "算法"
        assert body["payload"]["result_count"] == 5
        assert "created_at" in body
        logger.info(f"消息体结构正确: event_type={body['event_type']}, payload={body['payload']}")

    def test_returns_false_on_connection_error(self):
        """连接异常时应返回 False"""
        mock_pika = MagicMock()
        mock_pika.BlockingConnection.side_effect = ConnectionRefusedError("Connection refused")

        with patch.object(mq_module, "pika", mock_pika):
            result = publish_event("test.event", {"data": 1})

        assert result is False
        logger.info("连接异常时 publish_event 返回 False")

    def test_returns_false_on_publish_error(self):
        """发布消息异常时应返回 False"""
        mock_pika = MagicMock()
        mock_connection = MagicMock()
        mock_channel = MagicMock()

        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        mock_channel.basic_publish.side_effect = Exception("Channel error")

        with patch.object(mq_module, "pika", mock_pika):
            result = publish_event("test.event", {"data": 1})

        assert result is False
        logger.info("发布异常时 publish_event 返回 False")

    def test_queue_declare_called(self):
        """发布前应声明队列"""
        mock_pika = MagicMock()
        mock_connection = MagicMock()
        mock_channel = MagicMock()

        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        with patch.object(mq_module, "pika", mock_pika):
            publish_event("test.event", {"data": 1})

        mock_channel.queue_declare.assert_called_once_with(
            queue=mq_module.RABBITMQ_QUEUE, durable=True
        )
        logger.info("队列声明调用正确")

    def test_unicode_payload(self):
        """中文 payload 应正确序列化"""
        mock_pika = MagicMock()
        mock_connection = MagicMock()
        mock_channel = MagicMock()

        mock_pika.BlockingConnection.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel

        with patch.object(mq_module, "pika", mock_pika):
            result = publish_event("search.books", {"query": "深入理解计算机系统"})

        assert result is True
        call_args = mock_channel.basic_publish.call_args
        body_str = call_args.kwargs.get("body") or call_args[1].get("body")
        body = json.loads(body_str)
        assert body["payload"]["query"] == "深入理解计算机系统"
        logger.info("中文 payload 序列化正确")


# ---------------------------------------------------------------------------
# is_rabbitmq_available 测试
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestIsRabbitMQAvailable:
    """is_rabbitmq_available 函数测试"""

    def test_returns_false_when_pika_missing(self):
        """pika 缺失时应返回 False"""
        original_pika = mq_module.pika
        mq_module.pika = None

        result = is_rabbitmq_available()
        assert result is False
        logger.info("pika 缺失时 is_rabbitmq_available 返回 False")

        mq_module.pika = original_pika

    def test_returns_true_on_success(self):
        """连接成功时应返回 True"""
        mock_pika = MagicMock()
        mock_connection = MagicMock()
        mock_pika.BlockingConnection.return_value = mock_connection

        with patch.object(mq_module, "pika", mock_pika):
            result = is_rabbitmq_available()

        assert result is True
        mock_connection.close.assert_called_once()
        logger.info("连接成功时 is_rabbitmq_available 返回 True")

    def test_returns_false_on_connection_error(self):
        """连接失败时应返回 False"""
        mock_pika = MagicMock()
        mock_pika.BlockingConnection.side_effect = ConnectionRefusedError("Connection refused")

        with patch.object(mq_module, "pika", mock_pika):
            result = is_rabbitmq_available()

        assert result is False
        logger.info("连接失败时 is_rabbitmq_available 返回 False")
