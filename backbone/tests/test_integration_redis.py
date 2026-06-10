"""
集成测试 - Redis 缓存链路
需要 docker-compose 运行的 Redis 服务
标记为 integration，通过 -m integration 执行
"""

import json
import logging
import os

import pytest

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("INTEGRATION_REDIS_URL", "redis://127.0.0.1:6379/0")


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
def redis_client():
    """创建真实 Redis 连接"""
    if _skip_if_no_redis():
        pytest.skip("Redis 不可用（请确保 docker-compose 已启动）")

    from redis import Redis
    client = Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    logger.info(f"已连接 Redis: {REDIS_URL}")
    yield client
    # 清理测试键
    client.delete("test:integration:key")
    client.close()


class TestIntegrationRedis:
    """Redis 集成测试"""

    def test_ping(self, redis_client):
        """Redis PING 应返回 True"""
        assert redis_client.ping() is True
        logger.info("Redis PING 成功")

    def test_set_and_get(self, redis_client):
        """SET/GET 操作应正确"""
        redis_client.set("test:integration:key", "hello")
        value = redis_client.get("test:integration:key")
        assert value == "hello"
        logger.info("Redis SET/GET 操作成功")

    def test_cache_write_read_cycle(self, redis_client):
        """完整缓存写入-读取周期"""
        key = "test:integration:key"
        value = {"books": [{"id": "1", "title": "测试图书"}], "count": 1}
        ttl = 60

        # 写入
        redis_client.setex(key, ttl, json.dumps(value, ensure_ascii=False))

        # 读取
        stored = redis_client.get(key)
        assert stored is not None
        decoded = json.loads(stored)
        assert decoded == value

        # TTL 验证
        stored_ttl = redis_client.ttl(key)
        assert 0 < stored_ttl <= ttl
        logger.info(f"缓存写入-读取周期验证: TTL={stored_ttl}s")

    def test_cache_miss_returns_none(self, redis_client):
        """未命中缓存应返回 None"""
        result = redis_client.get("test:integration:nonexistent:key:xyz")
        assert result is None
        logger.info("缓存未命中返回 None")

    def test_ttl_expiration_simulation(self, redis_client):
        """TTL 过期模拟（设置1秒 TTL 并等待）"""
        key = "test:integration:ttl:expire"
        redis_client.setex(key, 1, "expires_soon")

        import time
        time.sleep(1.5)

        result = redis_client.get(key)
        assert result is None
        redis_client.delete(key)
        logger.info("TTL 过期验证成功")

    def test_unicode_values(self, redis_client):
        """Unicode/中文值应正确存取"""
        key = "test:integration:unicode"
        value = {"书名": "深入理解计算机系统", "作者": "Randal E. Bryant"}
        redis_client.setex(key, 60, json.dumps(value, ensure_ascii=False))

        stored = redis_client.get(key)
        decoded = json.loads(stored)
        assert decoded["书名"] == "深入理解计算机系统"
        redis_client.delete(key)
        logger.info("Unicode 值正确存取")

    def test_sorted_set_operations(self, redis_client):
        """有序集合操作（用于搜索趋势统计）"""
        key = "test:integration:sorted:set"
        redis_client.zincrby(key, 1, "算法")
        redis_client.zincrby(key, 2, "算法")
        redis_client.zincrby(key, 1, "数据结构")

        score = redis_client.zscore(key, "算法")
        assert score == 3.0

        top = redis_client.zrevrange(key, 0, -1, withscores=True)
        assert top[0][0] == "算法"

        redis_client.delete(key)
        logger.info(f"有序集合操作成功: top={top}")
