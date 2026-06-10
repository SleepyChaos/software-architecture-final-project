"""
功能测试 - 图书搜索接口 GET /books/search
测试搜索 API 的关键词搜索、分类过滤、可借过滤、limit 参数
"""

import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestApiSearchBasic:
    """基础搜索测试"""

    def test_search_returns_200(self, client):
        """GET /books/search 应返回 200"""
        resp = client.get("/books/search")
        assert resp.status_code == 200
        logger.info("GET /books/search 返回 200")

    def test_search_returns_list(self, client):
        """响应应为列表"""
        resp = client.get("/books/search")
        assert isinstance(resp.json(), list)
        logger.info("搜索响应为列表类型")

    def test_empty_query_returns_books(self, client):
        """空查询应返回图书列表"""
        resp = client.get("/books/search?q=")
        data = resp.json()
        assert len(data) > 0
        logger.info(f"空查询返回 {len(data)} 本图书")

    def test_keyword_search(self, client):
        """关键词搜索应返回匹配结果"""
        resp = client.get("/books/search?q=红楼梦")
        data = resp.json()
        assert len(data) >= 1
        titles = [b["title"] for b in data]
        assert "红楼梦" in titles
        logger.info(f"关键词'红楼梦'匹配: {titles}")

    def test_no_match_returns_empty(self, client):
        """无匹配关键词应返回空列表"""
        resp = client.get("/books/search?q=xyznonexistent123")
        data = resp.json()
        assert data == []
        logger.info("无匹配关键词返回空列表")


@pytest.mark.api
class TestApiSearchCategoryFilter:
    """分类过滤测试"""

    def test_category_filter(self, client):
        """category 参数应过滤结果"""
        resp = client.get("/books/search?category=科技")
        data = resp.json()
        for book in data:
            assert book["category"] == "科技"
        logger.info(f"category=科技 返回 {len(data)} 本")

    def test_category_with_keyword(self, client):
        """分类 + 关键词组合"""
        resp = client.get("/books/search?q=算法&category=科技")
        data = resp.json()
        for book in data:
            assert book["category"] == "科技"
        titles = [b["title"] for b in data]
        assert any("算法" in t for t in titles)
        logger.info(f"category=科技 + q=算法 结果: {titles}")


@pytest.mark.api
class TestApiSearchAvailabilityFilter:
    """可借状态过滤测试"""

    def test_only_available(self, client):
        """only_available=true 应只返回可借图书"""
        resp = client.get("/books/search?only_available=true")
        data = resp.json()
        for book in data:
            assert book["availableCopies"] > 0
        logger.info(f"only_available=true 返回 {len(data)} 本可借图书")

    def test_only_available_excludes_unavailable(self, client):
        """only_available=true 应排除百年孤独"""
        resp = client.get("/books/search?only_available=true")
        data = resp.json()
        titles = [b["title"] for b in data]
        assert "百年孤独" not in titles
        logger.info("only_available=true 排除了百年孤独")


@pytest.mark.api
class TestApiSearchLimit:
    """Limit 参数测试"""

    def test_default_limit(self, client):
        """默认 limit=12"""
        resp = client.get("/books/search")
        data = resp.json()
        assert len(data) <= 12
        logger.info(f"默认 limit 返回 {len(data)} 本")

    def test_custom_limit(self, client):
        """自定义 limit 参数"""
        resp = client.get("/books/search?limit=2")
        data = resp.json()
        assert len(data) <= 2
        logger.info(f"limit=2 返回 {len(data)} 本")

    def test_limit_below_minimum_returns_422(self, client):
        """limit < 1 应返回 422"""
        resp = client.get("/books/search?limit=0")
        assert resp.status_code == 422
        logger.info("limit=0 返回 422")

    def test_limit_above_maximum_returns_422(self, client):
        """limit > 20 应返回 422"""
        resp = client.get("/books/search?limit=21")
        assert resp.status_code == 422
        logger.info("limit=21 返回 422")


@pytest.mark.api
class TestApiSearchContentType:
    """响应格式测试"""

    def test_content_type_json(self, client):
        """Content-Type 应为 application/json"""
        resp = client.get("/books/search?q=test")
        assert "application/json" in resp.headers.get("content-type", "")
        logger.info(f"Content-Type: {resp.headers.get('content-type')}")

    def test_book_fields(self, client):
        """返回图书应包含核心字段"""
        resp = client.get("/books/search?q=红楼梦")
        data = resp.json()
        if data:
            book = data[0]
            for field in ["id", "title", "author", "category", "availableCopies"]:
                assert field in book, f"图书缺少字段: {field}"
            logger.info("搜索结果图书包含核心字段")
