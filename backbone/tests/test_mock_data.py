"""
单元测试 - Mock 数据完整性校验
确保 mock_data.py 中 BOOKS 和 DEFAULT_SUGGESTIONS 的数据结构一致且合法
"""

import logging

import pytest

from mock_data import BOOKS, DEFAULT_SUGGESTIONS

logger = logging.getLogger(__name__)

REQUIRED_BOOK_FIELDS = [
    "id", "isbn", "title", "author", "publisher", "publishYear",
    "category", "coverImageUrl", "location", "totalCopies",
    "availableCopies", "barcodes", "description",
]


@pytest.mark.unit
class TestBooksDataIntegrity:
    """BOOKS 数据结构完整性测试"""

    def test_books_not_empty(self):
        """BOOKS 列表不应为空"""
        assert len(BOOKS) > 0, "BOOKS 列表为空"
        logger.info(f"BOOKS 包含 {len(BOOKS)} 本图书")

    def test_all_fields_present(self):
        """每本书应包含所有必填字段"""
        for i, book in enumerate(BOOKS):
            for field in REQUIRED_BOOK_FIELDS:
                assert field in book, f"BOOKS[{i}] 缺少字段: {field}"
        logger.info("所有图书均包含必填字段")

    def test_unique_ids(self):
        """图书 ID 应唯一"""
        ids = [book["id"] for book in BOOKS]
        assert len(ids) == len(set(ids)), f"图书 ID 存在重复: {ids}"
        logger.info("图书 ID 均唯一")

    def test_unique_isbns(self):
        """ISBN 应唯一"""
        isbns = [book["isbn"] for book in BOOKS]
        assert len(isbns) == len(set(isbns)), f"ISBN 存在重复: {isbns}"
        logger.info("图书 ISBN 均唯一")

    def test_available_copies_within_total(self):
        """可借数量不应超过总数量"""
        for book in BOOKS:
            assert book["availableCopies"] <= book["totalCopies"], (
                f"'{book['title']}': availableCopies({book['availableCopies']}) "
                f"> totalCopies({book['totalCopies']})"
            )
        logger.info("所有图书可借数量 <= 总数量")

    def test_available_copies_non_negative(self):
        """可借数量应非负"""
        for book in BOOKS:
            assert book["availableCopies"] >= 0, f"'{book['title']}': availableCopies < 0"
        logger.info("所有图书可借数量非负")

    def test_total_copies_positive(self):
        """总数量应为正数"""
        for book in BOOKS:
            assert book["totalCopies"] > 0, f"'{book['title']}': totalCopies <= 0"
        logger.info("所有图书总数量为正数")

    def test_publish_year_reasonable(self):
        """出版年份应在合理范围内（1900-当前年份+1）"""
        for book in BOOKS:
            year = book["publishYear"]
            assert 1900 <= year <= 2100, (
                f"'{book['title']}': publishYear={year} 超出合理范围"
            )
        logger.info("所有图书出版年份在合理范围内")

    def test_barcodes_type(self):
        """barcodes 应为列表类型"""
        for book in BOOKS:
            assert isinstance(book["barcodes"], list), (
                f"'{book['title']}': barcodes 不是列表类型"
            )
        logger.info("所有图书 barcodes 均为列表类型")

    def test_category_not_empty(self):
        """分类字段不应为空字符串"""
        for book in BOOKS:
            assert book["category"], f"'{book['title']}': category 为空"
        logger.info("所有图书分类字段非空")

    def test_categories_covered(self):
        """应包含多个不同分类"""
        categories = set(book["category"] for book in BOOKS)
        assert len(categories) >= 2, f"分类种类过少: {categories}"
        logger.info(f"包含 {len(categories)} 个不同分类: {categories}")


@pytest.mark.unit
class TestDefaultSuggestions:
    """DEFAULT_SUGGESTIONS 数据测试"""

    def test_not_empty(self):
        """默认搜索建议不应为空"""
        assert len(DEFAULT_SUGGESTIONS) > 0, "DEFAULT_SUGGESTIONS 为空"
        logger.info(f"DEFAULT_SUGGESTIONS 包含 {len(DEFAULT_SUGGESTIONS)} 条建议")

    def test_all_strings(self):
        """所有建议项应为字符串"""
        for item in DEFAULT_SUGGESTIONS:
            assert isinstance(item, str), f"建议项非字符串: {item}"
        logger.info("所有建议项均为字符串")

    def test_no_empty_strings(self):
        """不应包含空字符串"""
        for item in DEFAULT_SUGGESTIONS:
            assert item.strip(), f"建议项为空字符串或仅含空白: '{item}'"
        logger.info("所有建议项非空")

    def test_no_duplicates(self):
        """不应包含重复建议"""
        assert len(DEFAULT_SUGGESTIONS) == len(set(DEFAULT_SUGGESTIONS)), (
            "DEFAULT_SUGGESTIONS 存在重复项"
        )
        logger.info("DEFAULT_SUGGESTIONS 无重复项")
