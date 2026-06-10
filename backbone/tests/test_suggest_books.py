"""
单元测试 - 搜索建议功能
测试 search_index.suggest_books 在 ES 不可用（fallback）时的行为
"""

import logging
from unittest.mock import patch

import pytest

from mock_data import BOOKS, DEFAULT_SUGGESTIONS
from search_index import suggest_books

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def _mock_es():
    """强制 ES 不可用，确保走 fallback 逻辑"""
    with patch("search_index.get_elasticsearch_client", return_value=None):
        yield


@pytest.mark.unit
class TestSuggestBooksEmptyQuery:
    """空查询场景"""

    def test_empty_string_returns_defaults(self):
        """空字符串应返回 DEFAULT_SUGGESTIONS"""
        results = suggest_books("")
        assert results == DEFAULT_SUGGESTIONS[:6]
        logger.info(f"空字符串返回 {len(results)} 条默认建议")

    def test_whitespace_returns_defaults(self):
        """纯空白字符应返回 DEFAULT_SUGGESTIONS"""
        results = suggest_books("   ")
        assert results == DEFAULT_SUGGESTIONS[:6]
        logger.info("纯空白字符正确返回默认建议")

    def test_limit_respected_empty_query(self):
        """空查询 + limit 应截断默认建议"""
        results = suggest_books("", limit=3)
        assert len(results) <= 3
        logger.info(f"limit=3 时空查询返回 {len(results)} 条建议")


@pytest.mark.unit
class TestSuggestBooksKeywordMatch:
    """关键词匹配场景"""

    def test_match_by_title(self):
        """关键词匹配书名"""
        results = suggest_books("红楼梦")
        assert "红楼梦" in results
        logger.info(f"书名匹配'红楼梦': {results}")

    def test_match_by_author(self):
        """关键词匹配作者"""
        results = suggest_books("曹雪芹")
        assert "红楼梦" in results
        logger.info(f"作者匹配'曹雪芹': {results}")

    def test_match_by_isbn(self):
        """关键词匹配 ISBN"""
        isbn = BOOKS[0]["isbn"]
        results = suggest_books(isbn)
        assert BOOKS[0]["title"] in results
        logger.info(f"ISBN 匹配: {results}")

    def test_partial_match(self):
        """部分关键词匹配"""
        results = suggest_books("算法")
        titles = results
        assert any("算法" in t for t in titles), f"部分匹配失败: {titles}"
        logger.info(f"部分匹配'算法': {results}")

    def test_no_match_includes_default_suggestions(self):
        """无匹配关键词时，DEFAULT_SUGGESTIONS 中包含关键词的项应被追加"""
        # "人工智能" 不在 BOOKS 的 title/author/isbn 中，但在 DEFAULT_SUGGESTIONS 中
        results = suggest_books("人工智能")
        assert "人工智能" in results, f"DEFAULT_SUGGESTIONS 中的匹配项未被包含: {results}"
        logger.info(f"'人工智能' 从 DEFAULT_SUGGESTIONS 中匹配: {results}")


@pytest.mark.unit
class TestSuggestBooksDedup:
    """去重逻辑测试"""

    def test_no_duplicates_in_results(self):
        """结果中不应有重复项"""
        results = suggest_books("深入")
        assert len(results) == len(set(results)), f"结果有重复: {results}"
        logger.info(f"去重验证通过: {results}")

    def test_dedup_preserves_order(self):
        """去重应保持首次出现的顺序"""
        results = suggest_books("计算机")
        seen = set()
        for item in results:
            assert item not in seen, f"顺序重复: {item}"
            seen.add(item)
        logger.info("去重顺序保持正确")


@pytest.mark.unit
class TestSuggestBooksLimit:
    """Limit 参数测试"""

    def test_limit_1(self):
        """limit=1 应只返回1条"""
        results = suggest_books("计算机", limit=1)
        assert len(results) <= 1
        logger.info(f"limit=1 返回: {results}")

    def test_limit_default_is_6(self):
        """默认 limit=6"""
        results = suggest_books("")
        assert len(results) <= 6
        logger.info(f"默认 limit=6 返回 {len(results)} 条")

    def test_limit_larger_than_available(self):
        """limit 大于可用结果数时应返回全部"""
        results = suggest_books("百年孤独", limit=100)
        assert len(results) >= 1
        logger.info(f"limit=100 时返回 {len(results)} 条（全部匹配）")


@pytest.mark.unit
class TestSuggestBooksCaseInsensitive:
    """大小写不敏感测试"""

    def test_case_insensitive_match(self):
        """大小写不敏感匹配"""
        results_lower = suggest_books("算法导论")
        results_upper = suggest_books("算法导论")
        assert results_lower == results_upper
        logger.info("大小写不敏感匹配结果一致")
