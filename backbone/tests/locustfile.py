"""
Locust 压测脚本
定义模拟用户行为：登录 → 搜索 → 查看推荐 → 获取建议

使用方式：
  命令行: locust -f locustfile.py --host http://127.0.0.1:8000
  Web UI: 浏览器打开 http://127.0.0.1:8089
  无头模式: locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u 50 -r 5 -t 30s
"""

import logging
import random

from locust import HttpUser, between, task

logger = logging.getLogger(__name__)

# 搜索关键词池
SEARCH_KEYWORDS = [
    "红楼梦", "活着", "算法", "计算机", "人类简史",
    "百年孤独", "数据结构", "人工智能", "曹雪芹", "余华",
]

# 分类池
CATEGORIES = ["科技", "文学", "历史"]

# 测试凭据
TEST_CREDENTIALS = [
    {"reader_id": "001", "password": "123456"},
    {"reader_id": "face-user", "password": "face"},
]


class LibraryUser(HttpUser):
    """模拟图书馆系统用户"""

    # 请求间隔：0.5-2秒随机延迟
    wait_time = between(0.5, 2)

    def on_start(self):
        """用户启动时执行登录"""
        creds = random.choice(TEST_CREDENTIALS)
        with self.client.post(
            "/login",
            json=creds,
            catch_response=True,
            name="/login",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
                logger.info(f"用户登录成功: {creds['reader_id']}")
            else:
                resp.failure(f"登录失败: {resp.status_code}")

    @task(3)
    def search_books(self):
        """搜索图书（权重3：高频操作）"""
        keyword = random.choice(SEARCH_KEYWORDS)
        limit = random.choice([5, 10, 12, 20])
        self.client.get(
            f"/books/search?q={keyword}&limit={limit}",
            name="/books/search",
        )

    @task(2)
    def search_with_category(self):
        """带分类的搜索（权重2）"""
        keyword = random.choice(SEARCH_KEYWORDS)
        category = random.choice(CATEGORIES)
        self.client.get(
            f"/books/search?q={keyword}&category={category}",
            name="/books/search (category)",
        )

    @task(2)
    def search_available_only(self):
        """仅可借图书搜索（权重2）"""
        keyword = random.choice(SEARCH_KEYWORDS)
        self.client.get(
            f"/books/search?q={keyword}&only_available=true",
            name="/books/search (available)",
        )

    @task(4)
    def get_recommended(self):
        """获取推荐图书（权重4：最高频操作）"""
        self.client.get("/books/recommended", name="/books/recommended")

    @task(3)
    def get_suggestions(self):
        """获取搜索建议（权重3）"""
        keyword = random.choice(SEARCH_KEYWORDS)
        self.client.get(
            f"/search/suggestions?q={keyword}",
            name="/search/suggestions",
        )

    @task(1)
    def get_search_trends(self):
        """获取搜索趋势（权重1：低频操作）"""
        limit = random.choice([5, 10])
        self.client.get(
            f"/analytics/search-trends?limit={limit}",
            name="/analytics/search-trends",
        )

    @task(1)
    def health_check(self):
        """健康检查（权重1）"""
        self.client.get("/healthz", name="/healthz")

    @task(1)
    def login_retry(self):
        """重新登录（权重1：模拟用户重新认证）"""
        creds = random.choice(TEST_CREDENTIALS)
        self.client.post(
            "/login",
            json=creds,
            name="/login (retry)",
        )

    @task(1)
    def root_page(self):
        """访问根路由（权重1）"""
        self.client.get("/", name="/")
