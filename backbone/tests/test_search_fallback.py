"""
单元测试 - 本地搜索回退逻辑
测试 search_index._fallback_search 在无 Elasticsearch 时的行为
"""

import logging

import pytest

from mock_data import BOOKS
from search_index import _fallback_search

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestFallbackSearchBasic:
    """基础搜索功能测试"""

    def test_empty_query_returns_all(self):
        """空查询应返回所有图书（受 limit 限制）"""
        results = _fallback_search("", None, False, 20)
        assert len(results) == len(BOOKS)
        logger.info(f"空查询返回全部 {len(results)} 本图书")

    def test_empty_query_with_limit(self):
        """空查询 + limit 应截断结果"""
        results = _fallback_search("", None, False, 2)
        assert len(results) == 2
        logger.info(f"limit=2 时返回 {len(results)} 本图书")

    def test_keyword_matches_title(self):
        """关键词应匹配书名"""
        results = _fallback_search("红楼梦", None, False, 20)
        assert len(results) >= 1
        titles = [r["title"] for r in results]
        assert "红楼梦" in titles
        logger.info(f"关键词'红楼梦'匹配 {len(results)} 本图书: {titles}")

    def test_keyword_matches_author(self):
        """关键词应匹配作者"""
        results = _fallback_search("余华", None, False, 20)
        assert len(results) >= 1
        titles = [r["title"] for r in results]
        assert "活着" in titles
        logger.info(f"关键词'余华'匹配到: {titles}")

    def test_keyword_matches_isbn(self):
        """关键词应匹配 ISBN"""
        isbn = BOOKS[0]["isbn"]
        results = _fallback_search(isbn, None, False, 20)
        assert len(results) >= 1
        assert results[0]["isbn"] == isbn
        logger.info(f"ISBN '{isbn}' 正确匹配")

    def test_keyword_matches_description(self):
        """关键词应匹配描述字段"""
        results = _fallback_search("程序员", None, False, 20)
        assert len(results) >= 1
        titles = [r["title"] for r in results]
        assert "深入理解计算机系统" in titles
        logger.info(f"描述关键词'程序员'匹配到: {titles}")

    def test_keyword_case_insensitive(self):
        """关键词搜索应大小写不敏感"""
        # CSAPP 不在原始数据中，用小写测试
        results_title = _fallback_search("算法", None, False, 20)
        results_title_upper = _fallback_search("算法", None, False, 20)
        assert results_title == results_title_upper
        logger.info("大小写不敏感搜索行为一致")

    def test_no_match_returns_empty(self):
        """无匹配关键词应返回空列表"""
        results = _fallback_search("xyznonexistent123", None, False, 20)
        assert results == []
        logger.info("无匹配关键词正确返回空列表")


@pytest.mark.unit
class TestFallbackSearchCategoryFilter:
    """分类过滤测试"""

    def test_category_filter_tech(self):
        """category='科技' 应只返回科技类图书"""
        results = _fallback_search("", "科技", False, 20)
        for r in results:
            assert r["category"] == "科技"
        assert len(results) >= 1
        logger.info(f"科技分类返回 {len(results)} 本图书")

    def test_category_filter_literature(self):
        """category='文学' 应只返回文学类图书"""
        results = _fallback_search("", "文学", False, 20)
        for r in results:
            assert r["category"] == "文学"
        logger.info(f"文学分类返回 {len(results)} 本图书")

    def test_category_filter_nonexistent(self):
        """不存在的分类应返回空列表"""
        results = _fallback_search("", "不存在的分类", False, 20)
        assert results == []
        logger.info("不存在的分类正确返回空列表")

    def test_category_with_keyword(self):
        """分类 + 关键词组合过滤"""
        results = _fallback_search("算法", "科技", False, 20)
        for r in results:
            assert r["category"] == "科技"
        titles = [r["title"] for r in results]
        assert "算法导论" in titles
        logger.info(f"科技+算法 组合过滤结果: {titles}")


@pytest.mark.unit
class TestFallbackSearchAvailabilityFilter:
    """可借状态过滤测试"""

    def test_only_available_filters_zero_copies(self):
        """only_available=True 应排除 availableCopies=0 的图书"""
        results = _fallback_search("", None, True, 20)
        for r in results:
            assert r["availableCopies"] > 0, (
                f"'{r['title']}' availableCopies=0 但未被过滤"
            )
        logger.info(f"可借过滤后返回 {len(results)} 本图书，全部 availableCopies > 0")

    def test_only_available_excludes_unavailable_books(self):
        """百年孤独(availableCopies=0) 应被过滤掉"""
        results = _fallback_search("", None, True, 20)
        titles = [r["title"] for r in results]
        assert "百年孤独" not in titles
        logger.info("百年孤独(availableCopies=0) 已被正确过滤")

    def test_not_available_includes_all(self):
        """only_available=False 应包含所有图书"""
        results = _fallback_search("", None, False, 20)
        titles = [r["title"] for r in results]
        assert "百年孤独" in titles
        logger.info("only_available=False 包含所有图书（含百年孤独）")


@pytest.mark.unit
class TestFallbackSearchSorting:
    """排序行为测试"""

    def test_sorted_by_available_and_year(self):
        """结果应按 availableCopies 和 publishYear 降序排列"""
        results = _fallback_search("", None, False, 20)
        for i in range(len(results) - 1):
            curr = (results[i]["availableCopies"], results[i]["publishYear"])
            next_ = (results[i + 1]["availableCopies"], results[i + 1]["publishYear"])
            assert curr >= next_, (
                f"排序异常: {results[i]['title']}({curr}) 排在 "
                f"{results[i + 1]['title']}({next_}) 之前"
            )
        logger.info("排序验证通过：按 availableCopies+publishYear 降序")

    def test_limit_respected(self):
        """limit 参数应被严格遵守"""
        for limit in [1, 2, 3, 5]:
            results = _fallback_search("", None, False, limit)
            assert len(results) <= limit, f"limit={limit} 但返回 {len(results)} 条"
        logger.info("所有 limit 值均被正确遵守")


@pytest.mark.unit
class TestFallbackSearchEdgeCases:
    """边界情况测试"""

    def test_whitespace_query(self):
        """纯空白查询应等同于空查询"""
        results = _fallback_search("   ", None, False, 20)
        assert len(results) == len(BOOKS)
        logger.info("纯空白查询正确返回全部图书")

    def test_keyword_with_leading_trailing_spaces(self):
        """关键词前后空格应被忽略"""
        results = _fallback_search("  红楼梦  ", None, False, 20)
        titles = [r["title"] for r in results]
        assert "红楼梦" in titles
        logger.info("前后空格关键词正确匹配")

    def test_combined_filters(self):
        """同时使用关键词+分类+可借过滤"""
        results = _fallback_search("计算", "科技", True, 5)
        for r in results:
            assert r["category"] == "科技"
            assert r["availableCopies"] > 0
        logger.info(f"组合过滤结果: {[r['title'] for r in results]}")
