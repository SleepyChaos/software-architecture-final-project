"""
单元测试 - Redis 缓存逻辑
测试 main.py 中的 read_cache / write_cache / get_redis_client 行为
"""

import json
import logging
from unittest.mock import MagicMock, patch

import pytest
from redis.exceptions import RedisError

import main as main_module
from main import read_cache, write_cache

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# read_cache 测试
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestReadCache:
    """read_cache 函数测试"""

    def test_returns_none_when_redis_unavailable(self, fake_redis):
        """Redis 不可用时应返回 None"""
        with patch.object(main_module, "get_redis_client", return_value=None):
            result = read_cache("any_key")
            assert result is None
            logger.info("Redis 不可用时 read_cache 正确返回 None")

    def test_returns_cached_value(self, fake_redis):
        """缓存命中时应返回 JSON 解码后的值"""
        key = "test:cache:key"
        value = {"data": [1, 2, 3], "name": "测试"}
        fake_redis.setex(key, 300, json.dumps(value, ensure_ascii=False))

        with patch.object(main_module, "get_redis_client", return_value=fake_redis):
            result = read_cache(key)
            assert result == value
            logger.info(f"缓存命中: key={key}, value={result}")

    def test_returns_none_on_cache_miss(self, fake_redis):
        """缓存未命中时应返回 None"""
        with patch.object(main_module, "get_redis_client", return_value=fake_redis):
            result = read_cache("nonexistent:key")
            assert result is None
            logger.info("缓存未命中正确返回 None")

    def test_handles_invalid_json(self, fake_redis):
        """非法 JSON 值应安全返回 None"""
        key = "test:invalid:json"
        fake_redis.set(key, "this-is-not-json{{{")

        with patch.object(main_module, "get_redis_client", return_value=fake_redis):
            result = read_cache(key)
            assert result is None
            logger.info("非法 JSON 值安全返回 None")

    def test_handles_redis_error(self, fake_redis):
        """Redis 操作异常时应返回 None"""
        fake_redis_with_error = MagicMock()
        fake_redis_with_error.get.side_effect = RedisError("Redis error")

        with patch.object(main_module, "get_redis_client", return_value=fake_redis_with_error):
            result = read_cache("any:key")
            assert result is None
            logger.info("Redis 异常时安全返回 None")


# ---------------------------------------------------------------------------
# write_cache 测试
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestWriteCache:
    """write_cache 函数测试"""

    def test_writes_value_to_redis(self, fake_redis):
        """正常写入应可从 Redis 中读取"""
        key = "test:write:key"
        value = {"books": [1, 2, 3]}
        ttl = 300

        with patch.object(main_module, "get_redis_client", return_value=fake_redis):
            write_cache(key, value, ttl)
            stored = fake_redis.get(key)
            assert json.loads(stored) == value
            logger.info(f"写入成功: key={key}, stored_value={stored}")

    def test_ttl_is_set(self, fake_redis):
        """TTL 应被正确设置"""
        key = "test:ttl:key"
        value = {"data": "test"}
        ttl = 180

        with patch.object(main_module, "get_redis_client", return_value=fake_redis):
            write_cache(key, value, ttl)
            stored_ttl = fake_redis.ttl(key)
            assert stored_ttl > 0
            assert stored_ttl <= ttl
            logger.info(f"TTL 已设置: key={key}, ttl={stored_ttl}")

    def test_does_nothing_when_redis_unavailable(self):
        """Redis 不可用时不应报错"""
        with patch.object(main_module, "get_redis_client", return_value=None):
            # 不应抛出任何异常
            write_cache("any:key", {"data": 1}, 300)
            logger.info("Redis 不可用时 write_cache 静默返回（无异常）")

    def test_handles_redis_error_on_write(self):
        """Redis 写入异常时不应崩溃"""
        fake_redis_with_error = MagicMock()
        fake_redis_with_error.setex.side_effect = RedisError("Redis write error")

        with patch.object(main_module, "get_redis_client", return_value=fake_redis_with_error):
            # 不应抛出任何异常
            write_cache("any:key", {"data": 1}, 300)
            logger.info("Redis 写入异常时安全处理（无崩溃）")

    def test_unicode_values(self, fake_redis):
        """中文/Unicode 值应正确存储和读取"""
        key = "test:unicode:key"
        value = {"书名": "深入理解计算机系统", "作者": "Randal E. Bryant"}

        with patch.object(main_module, "get_redis_client", return_value=fake_redis):
            write_cache(key, value, 300)
            stored = fake_redis.get(key)
            decoded = json.loads(stored)
            assert decoded["书名"] == "深入理解计算机系统"
            logger.info(f"Unicode 值正确存储: {decoded}")


# ---------------------------------------------------------------------------
# get_redis_client 测试
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetRedisClient:
    """get_redis_client 函数测试"""

    def test_returns_none_on_connection_error(self):
        """连接失败时应返回 None"""
        original = main_module._redis_client
        try:
            main_module._redis_client = None

            with patch.object(main_module, "Redis") as mock_redis_cls:
                mock_redis_cls.from_url.side_effect = RedisError("Connection refused")
                result = main_module.get_redis_client()
                assert result is None
                logger.info("Redis 连接失败时正确返回 None")
        finally:
            main_module._redis_client = original

    def test_returns_cached_client(self):
        """已有缓存连接时应直接返回"""
        fake_client = MagicMock()
        original = main_module._redis_client
        try:
            main_module._redis_client = fake_client

            result = main_module.get_redis_client()
            assert result is fake_client
            logger.info("缓存客户端直接返回")
        finally:
            main_module._redis_client = original
