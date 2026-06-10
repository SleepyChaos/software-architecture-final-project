"""
集成测试 - Elasticsearch 搜索引擎
需要 docker-compose 运行的 Elasticsearch 服务
标记为 integration，通过 -m integration 执行
"""

import logging
import os

import pytest

logger = logging.getLogger(__name__)

ES_URL = os.getenv("INTEGRATION_ES_URL", "http://127.0.0.1:9200")


def _skip_if_no_es():
    """检测 Elasticsearch 是否可用"""
    try:
        from elasticsearch import Elasticsearch
        client = Elasticsearch(ES_URL, request_timeout=3)
        return not client.ping()
    except Exception:
        return True


pytestmark = pytest.mark.integration


@pytest.fixture
def es_client():
    """创建真实 Elasticsearch 连接"""
    if _skip_if_no_es():
        pytest.skip("Elasticsearch 不可用（请确保 docker-compose 已启动）")

    from elasticsearch import Elasticsearch
    client = Elasticsearch(ES_URL, request_timeout=5)
    logger.info(f"已连接 Elasticsearch: {ES_URL}")
    yield client


class TestIntegrationElasticsearch:
    """Elasticsearch 集成测试"""

    def test_ping(self, es_client):
        """ES PING 应返回 True"""
        assert es_client.ping() is True
        logger.info("Elasticsearch PING 成功")

    def test_cluster_health(self, es_client):
        """集群健康状态应为可用"""
        health = es_client.cluster.health()
        assert health["status"] in ("green", "yellow")
        logger.info(f"集群状态: {health['status']}")

    def test_ensure_index_creates_mapping(self, es_client):
        """ensure_index 应创建正确的索引映射"""
        from search_index import ensure_index, ELASTICSEARCH_INDEX

        result = ensure_index()
        assert result is True

        # 验证索引存在
        assert es_client.indices.exists(index=ELASTICSEARCH_INDEX)

        # 验证映射
        mapping = es_client.indices.get_mapping(index=ELASTICSEARCH_INDEX)
        properties = mapping[ELASTICSEARCH_INDEX]["mappings"]["properties"]
        assert "title" in properties
        assert "author" in properties
        assert "category" in properties
        assert "availableCopies" in properties
        logger.info(f"索引 '{ELASTICSEARCH_INDEX}' 映射验证成功")

    def test_search_returns_results(self, es_client):
        """搜索应返回图书结果"""
        from search_index import search_books

        results = search_books("红楼梦")
        assert len(results) >= 1
        titles = [r["title"] for r in results]
        assert "红楼梦" in titles
        logger.info(f"ES 搜索'红楼梦'返回: {titles}")

    def test_search_empty_query(self, es_client):
        """空查询应返回所有图书"""
        from search_index import search_books

        results = search_books("")
        assert len(results) > 0
        logger.info(f"ES 空查询返回 {len(results)} 本图书")

    def test_search_with_category_filter(self, es_client):
        """分类过滤应生效"""
        from search_index import search_books

        results = search_books("", category="科技")
        for r in results:
            assert r["category"] == "科技"
        logger.info(f"ES category='科技' 返回 {len(results)} 本")

    def test_search_with_availability_filter(self, es_client):
        """可借过滤应排除 availableCopies=0 的图书"""
        from search_index import search_books

        results = search_books("", only_available=True)
        for r in results:
            assert r["availableCopies"] > 0
        titles = [r["title"] for r in results]
        assert "百年孤独" not in titles
        logger.info(f"ES only_available=True 返回 {len(results)} 本可借图书")

    def test_suggest_books(self, es_client):
        """suggest_books 应返回建议列表"""
        from search_index import suggest_books

        suggestions = suggest_books("计算机")
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        logger.info(f"ES suggest_books('计算机') 返回: {suggestions}")

    def test_get_elasticsearch_client_returns_client(self, es_client):
        """get_elasticsearch_client 应返回真实客户端"""
        from search_index import get_elasticsearch_client
        import search_index

        # 重置缓存
        original = search_index._es_client
        search_index._es_client = None

        client = get_elasticsearch_client()
        assert client is not None
        logger.info("get_elasticsearch_client 返回真实 ES 客户端")

        # 恢复
        search_index._es_client = original
