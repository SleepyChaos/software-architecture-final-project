"""
功能测试 - 搜索趋势接口 GET /analytics/search-trends
测试搜索趋势分析 API
"""

import logging

import pytest

from mock_data import DEFAULT_SUGGESTIONS

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestApiAnalyticsSearchTrends:
    """搜索趋势 API 测试"""

    def test_returns_200(self, client):
        """GET /analytics/search-trends 应返回 200"""
        resp = client.get("/analytics/search-trends")
        assert resp.status_code == 200
        logger.info("GET /analytics/search-trends 返回 200")

    def test_returns_list(self, client):
        """响应应为列表"""
        resp = client.get("/analytics/search-trends")
        assert isinstance(resp.json(), list)
        logger.info("响应为列表类型")

    def test_default_limit_10(self, client):
        """默认 limit=10，结果不超过10条"""
        resp = client.get("/analytics/search-trends")
        data = resp.json()
        assert len(data) <= 10
        logger.info(f"默认 limit 返回 {len(data)} 条趋势数据")

    def test_custom_limit(self, client):
        """自定义 limit 参数"""
        resp = client.get("/analytics/search-trends?limit=3")
        data = resp.json()
        assert len(data) <= 3
        logger.info(f"limit=3 返回 {len(data)} 条")

    def test_limit_below_minimum_returns_422(self, client):
        """limit < 1 应返回 422"""
        resp = client.get("/analytics/search-trends?limit=0")
        assert resp.status_code == 422
        logger.info("limit=0 返回 422")

    def test_limit_above_maximum_returns_422(self, client):
        """limit > 20 应返回 422"""
        resp = client.get("/analytics/search-trends?limit=21")
        assert resp.status_code == 422
        logger.info("limit=21 返回 422")

    def test_fallback_returns_default_suggestions(self, client):
        """Redis 不可用时应降级返回 DEFAULT_SUGGESTIONS"""
        resp = client.get("/analytics/search-trends")
        data = resp.json()
        # Mock 环境下 Redis 不可用，应返回 DEFAULT_SUGGESTIONS
        terms = [item["term"] for item in data]
        for suggestion in DEFAULT_SUGGESTIONS[:10]:
            assert suggestion in terms, (
                f"降级结果缺少 '{suggestion}'"
            )
        logger.info(f"Redis 不可用时降级返回 DEFAULT_SUGGESTIONS: {terms}")

    def test_fallback_items_have_count_zero(self, client):
        """降级返回的项 count 应为 0"""
        resp = client.get("/analytics/search-trends")
        data = resp.json()
        for item in data:
            assert item["count"] == 0
            assert "term" in item
        logger.info("降级返回的搜索趋势 count 均为 0")

    def test_item_structure(self, client):
        """每项应包含 term 和 count 字段"""
        resp = client.get("/analytics/search-trends")
        data = resp.json()
        for item in data:
            assert "term" in item
            assert "count" in item
        logger.info("趋势项包含 term 和 count 字段")

    def test_content_type_json(self, client):
        """Content-Type 应为 application/json"""
        resp = client.get("/analytics/search-trends")
        assert "application/json" in resp.headers.get("content-type", "")
        logger.info(f"Content-Type: {resp.headers.get('content-type')}")
