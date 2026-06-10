"""
功能测试 - 推荐图书接口 GET /books/recommended
测试推荐图书 API 的行为
"""

import logging
from unittest.mock import patch

import pytest

from mock_data import BOOKS

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestApiBooksRecommended:
    """推荐图书 API 测试"""

    def test_returns_200(self, client):
        """GET /books/recommended 应返回 200"""
        resp = client.get("/books/recommended")
        assert resp.status_code == 200
        logger.info(f"GET /books/recommended 返回 {resp.status_code}")

    def test_returns_list(self, client):
        """响应应为列表类型"""
        resp = client.get("/books/recommended")
        data = resp.json()
        assert isinstance(data, list)
        logger.info(f"推荐图书返回 {len(data)} 本")

    def test_max_6_books(self, client):
        """最多返回6本推荐图书"""
        resp = client.get("/books/recommended")
        data = resp.json()
        assert len(data) <= 6
        logger.info(f"推荐图书数量 {len(data)} <= 6")

    def test_all_books_available(self, client):
        """推荐图书应全部 availableCopies > 0"""
        resp = client.get("/books/recommended")
        data = resp.json()
        for book in data:
            assert book["availableCopies"] > 0, (
                f"'{book['title']}' availableCopies=0 但出现在推荐列表"
            )
        logger.info("所有推荐图书 availableCopies > 0")

    def test_book_has_required_fields(self, client):
        """每本图书应包含必要字段"""
        required_fields = ["id", "isbn", "title", "author", "category"]
        resp = client.get("/books/recommended")
        data = resp.json()
        for book in data:
            for field in required_fields:
                assert field in book, f"图书缺少字段: {field}"
        logger.info("所有推荐图书包含必要字段")

    def test_excludes_unavailable_books(self, client):
        """百年孤独(availableCopies=0) 不应出现在推荐列表"""
        resp = client.get("/books/recommended")
        data = resp.json()
        titles = [b["title"] for b in data]
        assert "百年孤独" not in titles
        logger.info("百年孤独(availableCopies=0) 不在推荐列表中")

    def test_content_type_json(self, client):
        """Content-Type 应为 application/json"""
        resp = client.get("/books/recommended")
        assert "application/json" in resp.headers.get("content-type", "")
        logger.info(f"Content-Type: {resp.headers.get('content-type')}")
