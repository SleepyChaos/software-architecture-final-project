"""
功能测试 - 登录接口 POST /login
测试用户认证逻辑：正确凭据、错误密码、不存在用户等
"""

import logging

import pytest

from models import User

logger = logging.getLogger(__name__)


@pytest.fixture
def login_user(sqlite_session_factory):
    """通过 SQLite 会话工厂直接插入测试用户（与 TestClient 共享同一数据库）"""
    session = sqlite_session_factory()
    try:
        user = User(reader_id="login001", password="correctpass")
        session.merge(user)
        session.commit()
        logger.info("登录测试用户已创建: reader_id=login001")
        yield user
    finally:
        session.close()


@pytest.mark.api
class TestApiLoginSuccess:
    """登录成功场景"""

    def test_login_returns_200(self, client, login_user):
        """正确凭据应返回 200"""
        resp = client.post("/login", json={
            "reader_id": "login001",
            "password": "correctpass",
        })
        assert resp.status_code == 200
        logger.info(f"登录成功: status={resp.status_code}")

    def test_login_returns_reader_id(self, client, login_user):
        """响应体应包含 reader_id"""
        resp = client.post("/login", json={
            "reader_id": "login001",
            "password": "correctpass",
        })
        data = resp.json()
        assert data["reader_id"] == "login001"
        logger.info(f"登录响应 reader_id={data['reader_id']}")

    def test_login_response_no_password(self, client, login_user):
        """响应体不应包含密码字段（UserResponse 模型过滤）"""
        resp = client.post("/login", json={
            "reader_id": "login001",
            "password": "correctpass",
        })
        data = resp.json()
        assert "password" not in data
        logger.info("登录响应不包含密码字段")


@pytest.mark.api
class TestApiLoginFailure:
    """登录失败场景"""

    def test_wrong_password_returns_401(self, client, login_user):
        """错误密码应返回 401"""
        resp = client.post("/login", json={
            "reader_id": "login001",
            "password": "wrongpass",
        })
        assert resp.status_code == 401
        logger.info("错误密码正确返回 401")

    def test_nonexistent_user_returns_401(self, client):
        """不存在的用户应返回 401"""
        resp = client.post("/login", json={
            "reader_id": "nonexistent999",
            "password": "anypass",
        })
        assert resp.status_code == 401
        logger.info("不存在的用户正确返回 401")

    def test_error_detail_message(self, client, login_user):
        """错误响应应包含 detail 信息"""
        resp = client.post("/login", json={
            "reader_id": "login001",
            "password": "wrongpass",
        })
        data = resp.json()
        assert "detail" in data
        logger.info(f"错误详情: {data['detail']}")


@pytest.mark.api
class TestApiLoginValidation:
    """请求参数校验"""

    def test_missing_reader_id_returns_422(self, client):
        """缺少 reader_id 应返回 422"""
        resp = client.post("/login", json={"password": "anypass"})
        assert resp.status_code == 422
        logger.info("缺少 reader_id 返回 422")

    def test_missing_password_returns_422(self, client):
        """缺少 password 应返回 422"""
        resp = client.post("/login", json={"reader_id": "login001"})
        assert resp.status_code == 422
        logger.info("缺少 password 返回 422")

    def test_empty_body_returns_422(self, client):
        """空请求体应返回 422"""
        resp = client.post("/login", json={})
        assert resp.status_code == 422
        logger.info("空请求体返回 422")

    def test_content_type_json(self, client, login_user):
        """Content-Type 应为 application/json"""
        resp = client.post("/login", json={
            "reader_id": "login001",
            "password": "correctpass",
        })
        assert "application/json" in resp.headers.get("content-type", "")
        logger.info(f"Content-Type: {resp.headers.get('content-type')}")
