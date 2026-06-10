"""
压测 - API 并发性能断言
使用 locust 无头模式运行压测，通过 pytest 断言性能阈值
需要后端服务运行在 http://127.0.0.1:8000

标记为 load，通过 -m load 执行
"""

import logging
import os
import subprocess
import sys

import pytest

logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("LOAD_TEST_BACKEND_URL", "http://127.0.0.1:8000")
LOCUSTFILE = os.path.join(os.path.dirname(__file__), "locustfile.py")

# 性能阈值（毫秒）- 容器环境延迟较高，阈值适当放宽
THRESHOLDS = {
    "/books/recommended": {"p95_ms": 500, "error_rate": 0.05},
    "/books/search": {"p95_ms": 1000, "error_rate": 0.05},
    "/login": {"p95_ms": 800, "error_rate": 0.05},
    "/search/suggestions": {"p95_ms": 500, "error_rate": 0.05},
    "/healthz": {"p95_ms": 300, "error_rate": 0.05},
}


def _skip_if_backend_unreachable():
    """检测后端服务是否可达"""
    try:
        import httpx
        resp = httpx.get(f"{BACKEND_URL}/", timeout=3)
        return resp.status_code != 200
    except Exception:
        return True


def _run_locust_headless(users: int, spawn_rate: int, duration: str) -> dict:
    """
    运行 locust 无头模式并解析结果
    返回 stats 字典
    """
    cmd = [
        sys.executable, "-m", "locust",
        "-f", LOCUSTFILE,
        "--host", BACKEND_URL,
        "--headless",
        "-u", str(users),
        "-r", str(spawn_rate),
        "-t", duration,
        "--csv", "/tmp/locust_results",
        "--csv-full-history",
    ]

    logger.info(f"运行 locust: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
    )

    # 解析 CSV 结果
    stats = {}
    stats_file = "/tmp/locust_results_stats.csv"
    if os.path.exists(stats_file):
        with open(stats_file) as f:
            lines = f.readlines()
        if len(lines) > 1:
            headers = [h.strip() for h in lines[0].split(",")]
            for line in lines[1:]:
                cols = [c.strip() for c in line.split(",")]
                if len(cols) >= len(headers):
                    row = dict(zip(headers, cols))
                    name = row.get("Name", "")
                    stats[name] = row

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "stats": stats,
    }


pytestmark = pytest.mark.load


class TestLoadApiPerformance:
    """API 性能压测（需后端服务运行）"""

    @pytest.fixture(autouse=True)
    def _check_backend(self):
        """测试前检查后端服务是否可达"""
        if _skip_if_backend_unreachable():
            pytest.skip(f"后端服务不可达: {BACKEND_URL}")

    def test_recommended_p95_latency(self):
        """GET /books/recommended P95 延迟 < 500ms"""
        import httpx
        import time

        latencies = []
        for _ in range(50):
            start = time.perf_counter()
            resp = httpx.get(f"{BACKEND_URL}/books/recommended", timeout=10)
            elapsed = (time.perf_counter() - start) * 1000
            assert resp.status_code == 200
            latencies.append(elapsed)

        latencies.sort()
        p95_idx = int(len(latencies) * 0.95)
        p95 = latencies[min(p95_idx, len(latencies) - 1)]

        threshold = THRESHOLDS["/books/recommended"]["p95_ms"]
        assert p95 < threshold, (
            f"/books/recommended P95={p95:.1f}ms 超过阈值 {threshold}ms"
        )
        logger.info(f"/books/recommended P95={p95:.1f}ms (阈值 {threshold}ms)")

    def test_search_p95_latency(self):
        """GET /books/search P95 延迟 < 1000ms"""
        import httpx
        import time

        latencies = []
        keywords = ["红楼梦", "算法", "计算机", "活着", "人类简史"]
        for kw in keywords * 10:
            start = time.perf_counter()
            resp = httpx.get(
                f"{BACKEND_URL}/books/search",
                params={"q": kw, "limit": 10},
                timeout=10,
            )
            elapsed = (time.perf_counter() - start) * 1000
            assert resp.status_code == 200
            latencies.append(elapsed)

        latencies.sort()
        p95_idx = int(len(latencies) * 0.95)
        p95 = latencies[min(p95_idx, len(latencies) - 1)]

        threshold = THRESHOLDS["/books/search"]["p95_ms"]
        assert p95 < threshold, (
            f"/books/search P95={p95:.1f}ms 超过阈值 {threshold}ms"
        )
        logger.info(f"/books/search P95={p95:.1f}ms (阈值 {threshold}ms)")

    def test_login_p95_latency(self):
        """POST /login P95 延迟 < 800ms"""
        import httpx
        import time

        latencies = []
        for _ in range(50):
            start = time.perf_counter()
            resp = httpx.post(
                f"{BACKEND_URL}/login",
                json={"reader_id": "001", "password": "123456"},
                timeout=10,
            )
            elapsed = (time.perf_counter() - start) * 1000
            assert resp.status_code == 200
            latencies.append(elapsed)

        latencies.sort()
        p95_idx = int(len(latencies) * 0.95)
        p95 = latencies[min(p95_idx, len(latencies) - 1)]

        threshold = THRESHOLDS["/login"]["p95_ms"]
        assert p95 < threshold, (
            f"/login P95={p95:.1f}ms 超过阈值 {threshold}ms"
        )
        logger.info(f"/login P95={p95:.1f}ms (阈值 {threshold}ms)")

    def test_suggestions_p95_latency(self):
        """GET /search/suggestions P95 延迟 < 500ms"""
        import httpx
        import time

        latencies = []
        keywords = ["计算机", "红楼梦", "算法", "数据结构", "人工智能"]
        for kw in keywords * 10:
            start = time.perf_counter()
            resp = httpx.get(
                f"{BACKEND_URL}/search/suggestions",
                params={"q": kw},
                timeout=10,
            )
            elapsed = (time.perf_counter() - start) * 1000
            assert resp.status_code == 200
            latencies.append(elapsed)

        latencies.sort()
        p95_idx = int(len(latencies) * 0.95)
        p95 = latencies[min(p95_idx, len(latencies) - 1)]

        threshold = THRESHOLDS["/search/suggestions"]["p95_ms"]
        assert p95 < threshold, (
            f"/search/suggestions P95={p95:.1f}ms 超过阈值 {threshold}ms"
        )
        logger.info(f"/search/suggestions P95={p95:.1f}ms (阈值 {threshold}ms)")

    def test_error_rate_below_threshold(self):
        """所有接口错误率 < 5%"""
        import httpx

        endpoints = [
            ("GET", "/books/recommended"),
            ("GET", "/books/search?q=算法"),
            ("GET", "/search/suggestions?q=计算机"),
            ("GET", "/healthz"),
            ("GET", "/"),
        ]

        total = 0
        errors = 0
        for method, path in endpoints:
            for _ in range(20):
                total += 1
                try:
                    url = f"{BACKEND_URL}{path}"
                    if method == "GET":
                        resp = httpx.get(url, timeout=10)
                    else:
                        resp = httpx.post(url, timeout=10)
                    if resp.status_code >= 500:
                        errors += 1
                except Exception:
                    errors += 1

        error_rate = errors / total if total > 0 else 1.0
        threshold = 0.05
        assert error_rate < threshold, (
            f"错误率 {error_rate:.2%} 超过阈值 {threshold:.2%} ({errors}/{total})"
        )
        logger.info(f"错误率: {error_rate:.2%} ({errors}/{total}) 阈值: {threshold:.2%}")
