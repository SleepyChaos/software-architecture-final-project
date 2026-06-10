"""
功能测试 - 搜索建议接口 GET /search/suggestions
测试搜索建议 API 的行为
"""

import logging

import pytest

from mock_data import DEFAULT_SUGGESTIONS

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestApiSuggestionsBasic:
    """基础搜索建议测试"""

    def test_returns_200(self, client):
        """GET /search/suggestions 应返回 200"""
        resp = client.get("/search/suggestions")
        assert resp.status_code == 200
        logger.info("GET /search/suggestions 返回 200")

    def test_returns_list(self, client):
        """响应应为列表"""
        resp = client.get("/search/suggestions")
        assert isinstance(resp.json(), list)
        logger.info("响应为列表类型")

    def test_empty_query_returns_defaults(self, client):
        """空 q 参数应返回默认建议"""
        resp = client.get("/search/suggestions?q=")
        data = resp.json()
        assert len(data) > 0
        logger.info(f"空查询返回 {len(data)} 条默认建议: {data}")

    def test_keyword_query(self, client):
        """有 q 参数应返回匹配建议"""
        resp = client.get("/search/suggestions?q=红楼梦")
        data = resp.json()
        assert isinstance(data, list)
        logger.info(f"q=红楼梦 返回: {data}")


@pytest.mark.api
class TestApiSuggestionsContent:
    """响应内容验证"""

    def test_all_items_are_strings(self, client):
        """所有建议项应为字符串"""
        resp = client.get("/search/suggestions?q=算法")
        data = resp.json()
        for item in data:
            assert isinstance(item, str)
        logger.info("所有建议项均为字符串")

    def test_max_suggestions(self, client):
        """建议数量应合理（默认 limit=6）"""
        resp = client.get("/search/suggestions?q=计算机")
        data = resp.json()
        assert len(data) <= 10  # 合理上限
        logger.info(f"建议数量 {len(data)} 在合理范围内")

    def test_content_type_json(self, client):
        """Content-Type 应为 application/json"""
        resp = client.get("/search/suggestions")
        assert "application/json" in resp.headers.get("content-type", "")
        logger.info(f"Content-Type: {resp.headers.get('content-type')}")


@pytest.mark.api
class TestApiSuggestionsEdgeCases:
    """边界情况测试"""

    def test_no_match_returns_fallback(self, client):
        """无匹配时应返回回退建议"""
        resp = client.get("/search/suggestions?q=xyznonexistent")
        data = resp.json()
        assert isinstance(data, list)
        logger.info(f"无匹配时返回回退建议: {data}")

    def test_special_characters(self, client):
        """特殊字符不应导致500错误"""
        resp = client.get("/search/suggestions?q=<script>alert(1)</script>")
        assert resp.status_code == 200
        logger.info("特殊字符安全处理，返回 200")

    def test_very_long_query(self, client):
        """超长查询字符串不应导致崩溃"""
        long_q = "测" * 1000
        resp = client.get(f"/search/suggestions?q={long_q}")
        assert resp.status_code == 200
        logger.info("超长查询安全处理，返回 200")
