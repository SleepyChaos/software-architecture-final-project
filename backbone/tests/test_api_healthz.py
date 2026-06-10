"""
功能测试 - 健康检查接口 GET /healthz
测试服务健康状态报告
"""

import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestApiHealthz:
    """健康检查 API 测试"""

    def test_returns_200(self, client):
        """GET /healthz 应返回 200"""
        resp = client.get("/healthz")
        assert resp.status_code == 200
        logger.info("GET /healthz 返回 200")

    def test_returns_status_ok(self, client):
        """status 字段应为 'ok'"""
        resp = client.get("/healthz")
        data = resp.json()
        assert data["status"] == "ok"
        logger.info(f"status={data['status']}")

    def test_contains_redis_status(self, client):
        """应包含 redis 状态字段"""
        resp = client.get("/healthz")
        data = resp.json()
        assert "redis" in data
        assert data["redis"] in ("up", "degraded")
        logger.info(f"redis={data['redis']}")

    def test_contains_elasticsearch_status(self, client):
        """应包含 elasticsearch 状态字段"""
        resp = client.get("/healthz")
        data = resp.json()
        assert "elasticsearch" in data
        assert data["elasticsearch"] in ("up", "degraded")
        logger.info(f"elasticsearch={data['elasticsearch']}")

    def test_contains_rabbitmq_status(self, client):
        """应包含 rabbitmq 状态字段"""
        resp = client.get("/healthz")
        data = resp.json()
        assert "rabbitmq" in data
        assert data["rabbitmq"] in ("up", "degraded")
        logger.info(f"rabbitmq={data['rabbitmq']}")

    def test_degraded_when_services_mocked(self, client):
        """Mock 环境下所有外部服务应为 degraded"""
        resp = client.get("/healthz")
        data = resp.json()
        # 在测试环境中 Redis/ES/RabbitMQ 全部被 mock 为 None
        assert data["redis"] == "degraded"
        assert data["elasticsearch"] == "degraded"
        assert data["rabbitmq"] == "degraded"
        logger.info("Mock 环境下所有外部服务状态为 degraded（符合预期）")

    def test_content_type_json(self, client):
        """Content-Type 应为 application/json"""
        resp = client.get("/healthz")
        assert "application/json" in resp.headers.get("content-type", "")
        logger.info(f"Content-Type: {resp.headers.get('content-type')}")

    def test_all_required_fields(self, client):
        """响应应包含全部5个字段"""
        resp = client.get("/healthz")
        data = resp.json()
        required = {"status", "redis", "elasticsearch", "rabbitmq", "circuit_breakers"}
        assert required == set(data.keys())
        logger.info(f"响应字段完整: {set(data.keys())}")
