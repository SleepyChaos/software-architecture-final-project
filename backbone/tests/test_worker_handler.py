"""
单元测试 - RabbitMQ Worker 消息处理
测试 rabbitmq_worker.py 中的 handle_message 函数
"""

import json
import logging
from unittest.mock import MagicMock, patch

import pytest

import rabbitmq_worker as worker_module
from rabbitmq_worker import handle_message

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestHandleMessageSearchBooks:
    """search.books 事件处理测试"""

    def test_search_event_writes_to_redis(self, mock_rabbitmq_channel, fake_redis):
        """search.books 事件应将搜索词写入 Redis sorted set"""
        ch, method, properties = mock_rabbitmq_channel
        message = json.dumps({
            "event_type": "search.books",
            "payload": {"query": "算法导论", "result_count": 3},
            "created_at": 1700000000,
        })

        with patch.object(worker_module, "get_redis_client", return_value=fake_redis):
            handle_message(ch, method, properties, message)

        score = fake_redis.zscore("analytics:search_terms", "算法导论")
        assert score == 1.0
        ch.basic_ack.assert_called_once()
        logger.info(f"search.books 事件写入 Redis: '算法导论' score={score}")

    def test_search_event_increments_on_repeat(self, mock_rabbitmq_channel, fake_redis):
        """同一搜索词多次触发应累加计数"""
        ch, method, properties = mock_rabbitmq_channel
        message = json.dumps({
            "event_type": "search.books",
            "payload": {"query": "红楼梦"},
            "created_at": 1700000000,
        })

        with patch.object(worker_module, "get_redis_client", return_value=fake_redis):
            handle_message(ch, method, properties, message)
            handle_message(ch, method, properties, message)
            handle_message(ch, method, properties, message)

        score = fake_redis.zscore("analytics:search_terms", "红楼梦")
        assert score == 3.0
        logger.info(f"搜索词'红楼梦'累加3次: score={score}")

    def test_search_event_skips_empty_query(self, mock_rabbitmq_channel, fake_redis):
        """空搜索词不应写入 Redis"""
        ch, method, properties = mock_rabbitmq_channel
        message = json.dumps({
            "event_type": "search.books",
            "payload": {"query": "   "},
            "created_at": 1700000000,
        })

        with patch.object(worker_module, "get_redis_client", return_value=fake_redis):
            handle_message(ch, method, properties, message)

        assert fake_redis.zcard("analytics:search_terms") == 0
        ch.basic_ack.assert_called_once()
        logger.info("空搜索词正确跳过")


@pytest.mark.unit
class TestHandleMessageAuthEvents:
    """auth 事件处理测试"""

    def test_login_success_increments_counter(self, mock_rabbitmq_channel, fake_redis):
        """auth.login_success 应增加登录成功计数"""
        ch, method, properties = mock_rabbitmq_channel
        message = json.dumps({
            "event_type": "auth.login_success",
            "payload": {"reader_id": "001"},
            "created_at": 1700000000,
        })

        with patch.object(worker_module, "get_redis_client", return_value=fake_redis):
            handle_message(ch, method, properties, message)

        count = int(fake_redis.get("analytics:login_success_total") or 0)
        assert count == 1
        ch.basic_ack.assert_called_once()
        logger.info(f"auth.login_success 计数: {count}")

    def test_login_failed_increments_counter(self, mock_rabbitmq_channel, fake_redis):
        """auth.login_failed 应增加登录失败计数"""
        ch, method, properties = mock_rabbitmq_channel
        message = json.dumps({
            "event_type": "auth.login_failed",
            "payload": {"reader_id": "bad_user"},
            "created_at": 1700000000,
        })

        with patch.object(worker_module, "get_redis_client", return_value=fake_redis):
            handle_message(ch, method, properties, message)

        count = int(fake_redis.get("analytics:login_failed_total") or 0)
        assert count == 1
        ch.basic_ack.assert_called_once()
        logger.info(f"auth.login_failed 计数: {count}")


@pytest.mark.unit
class TestHandleMessageEdgeCases:
    """边界情况测试"""

    def test_invalid_json_skipped(self, mock_rabbitmq_channel, fake_redis):
        """非法 JSON 消息应安全跳过并 ack"""
        ch, method, properties = mock_rabbitmq_channel

        with patch.object(worker_module, "get_redis_client", return_value=fake_redis):
            handle_message(ch, method, properties, "this-is-not-json{{{")

        ch.basic_ack.assert_called_once()
        logger.info("非法 JSON 消息安全跳过并 ack")

    def test_unknown_event_type_ack(self, mock_rabbitmq_channel, fake_redis):
        """未知事件类型应安全 ack"""
        ch, method, properties = mock_rabbitmq_channel
        message = json.dumps({
            "event_type": "unknown.event",
            "payload": {"data": 123},
            "created_at": 1700000000,
        })

        with patch.object(worker_module, "get_redis_client", return_value=fake_redis):
            handle_message(ch, method, properties, message)

        ch.basic_ack.assert_called_once()
        logger.info("未知事件类型安全 ack")

    def test_redis_unavailable_still_acks(self, mock_rabbitmq_channel):
        """Redis 不可用时仍应 ack 消息（不崩溃）"""
        ch, method, properties = mock_rabbitmq_channel
        message = json.dumps({
            "event_type": "search.books",
            "payload": {"query": "测试"},
            "created_at": 1700000000,
        })

        with patch.object(worker_module, "get_redis_client", return_value=None):
            handle_message(ch, method, properties, message)

        ch.basic_ack.assert_called_once()
        logger.info("Redis 不可用时仍正确 ack 消息")

    def test_missing_event_type_field(self, mock_rabbitmq_channel, fake_redis):
        """消息缺少 event_type 字段时不应崩溃"""
        ch, method, properties = mock_rabbitmq_channel
        message = json.dumps({
            "payload": {"data": 123},
            "created_at": 1700000000,
        })

        with patch.object(worker_module, "get_redis_client", return_value=fake_redis):
            handle_message(ch, method, properties, message)

        ch.basic_ack.assert_called_once()
        logger.info("缺少 event_type 字段时安全处理")

    def test_missing_payload_field(self, mock_rabbitmq_channel, fake_redis):
        """消息缺少 payload 字段时不应崩溃"""
        ch, method, properties = mock_rabbitmq_channel
        message = json.dumps({
            "event_type": "search.books",
            "created_at": 1700000000,
        })

        with patch.object(worker_module, "get_redis_client", return_value=fake_redis):
            handle_message(ch, method, properties, message)

        ch.basic_ack.assert_called_once()
        logger.info("缺少 payload 字段时安全处理")
