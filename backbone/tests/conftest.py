"""
测试公共 fixtures
提供数据库、TestClient、外部服务 mock 等共享资源
"""

import logging
import os
import sys

import pytest

# 将 backbone 目录加入 sys.path，确保 import models/schemas/database 正常工作
_BACKBONE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKBONE_DIR not in sys.path:
    sys.path.insert(0, _BACKBONE_DIR)

# 设置测试环境变量（避免连接真实外部服务）
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379/0")
os.environ.setdefault("ELASTICSEARCH_URL", "http://127.0.0.1:9200")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@127.0.0.1:5672/%2F")

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SQLite 内存数据库 fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def sqlite_engine():
    """创建 SQLite 内存数据库引擎（session 级别复用）"""
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    logger.info("SQLite 内存数据库引擎已创建（StaticPool 共享连接）")
    yield engine
    engine.dispose()
    logger.info("SQLite 内存数据库引擎已关闭")


@pytest.fixture(scope="session")
def sqlite_session_factory(sqlite_engine):
    """创建 SQLite 会话工厂（session 级别复用）"""
    from sqlalchemy.orm import sessionmaker
    from models import Base

    Base.metadata.create_all(bind=sqlite_engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)
    logger.info("SQLite 表已创建，会话工厂已就绪")
    yield factory
    Base.metadata.drop_all(bind=sqlite_engine)


@pytest.fixture
def db_session(sqlite_session_factory):
    """每个测试独立的数据库会话（自动回滚）"""
    session = sqlite_session_factory()
    yield session
    session.rollback()
    session.close()


# ---------------------------------------------------------------------------
# FastAPI TestClient fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def test_app(sqlite_engine, sqlite_session_factory):
    """
    创建测试用 FastAPI 应用（每个测试独立 setup/teardown）
    替换数据库依赖为 SQLite，mock 所有外部服务
    """
    from unittest.mock import patch

    import database as db_module
    import models
    import main as main_module

    # 替换数据库引擎和会话工厂
    original_engine = db_module.engine
    original_session = db_module.SessionLocal

    db_module.engine = sqlite_engine
    db_module.SessionLocal = sqlite_session_factory

    # 创建 get_db 覆盖函数
    def override_get_db():
        session = sqlite_session_factory()
        try:
            yield session
        finally:
            session.close()

    # Mock 外部服务 - function scope 确保每个测试后 patch 清理
    with patch.object(main_module, "get_redis_client", return_value=None), \
         patch.object(main_module, "publish_event", return_value=True), \
         patch.object(main_module, "is_rabbitmq_available", return_value=False), \
         patch.object(main_module, "get_elasticsearch_client", return_value=None):

        # 覆盖 FastAPI 依赖
        main_module.app.dependency_overrides[db_module.get_db] = override_get_db

        logger.info("测试 FastAPI 应用已初始化（SQLite + Mock 外部服务）")
        yield main_module.app

        # 清理
        main_module.app.dependency_overrides.clear()
        db_module.engine = original_engine
        db_module.SessionLocal = original_session
        logger.info("测试 FastAPI 应用已清理")


@pytest.fixture
def client(test_app):
    """FastAPI TestClient（每个测试独立创建）"""
    from fastapi.testclient import TestClient
    with TestClient(test_app) as c:
        logger.info("TestClient 已就绪")
        yield c


# ---------------------------------------------------------------------------
# 种子数据 fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def seed_user(db_session):
    """在 SQLite 中插入测试用户"""
    from models import User

    user = User(reader_id="test001", password="testpass")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    logger.info(f"测试用户已创建: reader_id={user.reader_id}")
    yield user
    db_session.delete(user)
    db_session.commit()


# ---------------------------------------------------------------------------
# Mock Redis fixture（可选使用 fakeredis）
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_redis():
    """提供 fakeredis 实例用于测试缓存逻辑"""
    import fakeredis
    client = fakeredis.FakeRedis(decode_responses=True)
    logger.info("FakeRedis 实例已创建")
    yield client
    client.flushall()


# ---------------------------------------------------------------------------
# Mock RabbitMQ channel/method fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_rabbitmq_channel():
    """提供 mock 的 RabbitMQ channel 和 method 对象"""
    from unittest.mock import MagicMock
    ch = MagicMock()
    method = MagicMock()
    method.delivery_tag = 1
    properties = MagicMock()
    logger.info("Mock RabbitMQ channel 已创建")
    return ch, method, properties
