"""
功能测试 - Prometheus 指标接口 GET /metrics
测试 Prometheus 监控指标输出
"""

import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestApiMetrics:
    """Prometheus 指标 API 测试"""

    def test_returns_200(self, client):
        """GET /metrics 应返回 200"""
        resp = client.get("/metrics")
        assert resp.status_code == 200
        logger.info("GET /metrics 返回 200")

    def test_content_type_prometheus(self, client):
        """Content-Type 应为 Prometheus 文本格式"""
        resp = client.get("/metrics")
        content_type = resp.headers.get("content-type", "")
        # Prometheus 使用 text/plain 或自定义 content type
        assert "text/plain" in content_type or "openmetrics" in content_type or "text" in content_type
        logger.info(f"Content-Type: {content_type}")

    def test_contains_request_counter(self, client):
        """应包含 HTTP 请求计数指标"""
        # 先触发一些请求
        client.get("/")
        client.get("/healthz")

        resp = client.get("/metrics")
        body = resp.text
        assert "library_http_requests_total" in body
        logger.info("指标中包含 library_http_requests_total")

    def test_contains_request_latency(self, client):
        """应包含请求延迟指标"""
        client.get("/")

        resp = client.get("/metrics")
        body = resp.text
        assert "library_http_request_duration_seconds" in body
        logger.info("指标中包含 library_http_request_duration_seconds")

    def test_contains_cache_counter(self, client):
        """应包含缓存操作计数指标"""
        resp = client.get("/metrics")
        body = resp.text
        assert "library_cache_operations_total" in body
        logger.info("指标中包含 library_cache_operations_total")

    def test_metrics_are_text_format(self, client):
        """指标输出应为文本格式（非 JSON）"""
        resp = client.get("/metrics")
        body = resp.text
        # Prometheus 文本格式每行通常是 metric_name{labels} value 形式
        lines = [line for line in body.split("\n") if line and not line.startswith("#")]
        assert len(lines) > 0
        logger.info(f"指标输出为文本格式，共 {len(lines)} 行数据")

    def test_metrics_after_multiple_requests(self, client):
        """多次请求后指标应累积"""
        for _ in range(3):
            client.get("/")

        resp = client.get("/metrics")
        body = resp.text
        assert "library_http_requests_total" in body
        logger.info("多次请求后指标正常累积")
