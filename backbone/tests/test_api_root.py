"""
功能测试 - 根路由 GET /
测试 FastAPI 应用的基础路由
"""

import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestApiRoot:
    """根路由 API 测试"""

    def test_root_returns_200(self, client):
        """GET / 应返回 200"""
        resp = client.get("/")
        assert resp.status_code == 200
        logger.info(f"GET / 返回 {resp.status_code}")

    def test_root_returns_message(self, client):
        """响应体应包含 message 字段"""
        resp = client.get("/")
        data = resp.json()
        assert "message" in data
        assert "Backend is running" in data["message"]
        logger.info(f"根路由响应: {data['message']}")

    def test_root_content_type(self, client):
        """Content-Type 应为 application/json"""
        resp = client.get("/")
        assert "application/json" in resp.headers.get("content-type", "")
        logger.info(f"Content-Type: {resp.headers.get('content-type')}")
