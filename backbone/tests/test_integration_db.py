"""
集成测试 - PostgreSQL 数据库
需要 docker-compose 运行的 PostgreSQL 服务
标记为 integration，通过 -m integration 执行
"""

import logging
import os

import pytest

logger = logging.getLogger(__name__)

# 真实 PostgreSQL 连接 URL（docker-compose 中的配置）
INTEGRATION_DB_URL = os.getenv(
    "INTEGRATION_DATABASE_URL",
    "postgresql://library:library@127.0.0.1:5432/library",
)


def _skip_if_no_db():
    """检测 PostgreSQL 是否可用"""
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(INTEGRATION_DB_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return False
    except Exception:
        return True


pytestmark = pytest.mark.integration


@pytest.fixture
def pg_engine():
    """创建真实 PostgreSQL 连接引擎"""
    if _skip_if_no_db():
        pytest.skip("PostgreSQL 不可用（请确保 docker-compose 已启动）")

    from sqlalchemy import create_engine
    engine = create_engine(INTEGRATION_DB_URL)
    logger.info(f"已连接 PostgreSQL: {INTEGRATION_DB_URL}")
    yield engine
    engine.dispose()


@pytest.fixture
def pg_session(pg_engine):
    """创建 PostgreSQL 会话"""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=pg_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


class TestIntegrationDatabase:
    """PostgreSQL 集成测试"""

    def test_connection_alive(self, pg_engine):
        """PostgreSQL 连接应保持活跃"""
        from sqlalchemy import text
        with pg_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
        logger.info("PostgreSQL 连接存活检查通过")

    def test_users_table_exists(self, pg_engine):
        """users 表应存在"""
        from sqlalchemy import inspect
        inspector = inspect(pg_engine)
        tables = inspector.get_table_names()
        assert "users" in tables, f"users 表不存在，当前表: {tables}"
        logger.info(f"users 表存在，当前所有表: {tables}")

    def test_create_and_query_user(self, pg_session):
        """创建用户并查询应成功"""
        from models import User

        # 插入测试用户
        test_id = "integration_test_001"
        user = pg_session.query(User).filter(User.reader_id == test_id).first()
        if not user:
            user = User(reader_id=test_id, password="testpass")
            pg_session.add(user)
            pg_session.commit()

        # 查询验证
        found = pg_session.query(User).filter(User.reader_id == test_id).first()
        assert found is not None
        assert found.reader_id == test_id
        logger.info(f"创建并查询用户成功: {found}")

        # 清理
        pg_session.delete(found)
        pg_session.commit()

    def test_concurrent_sessions_no_conflict(self, pg_engine):
        """并发会话不应冲突"""
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=pg_engine)

        sessions = [Session() for _ in range(3)]
        try:
            for i, session in enumerate(sessions):
                from sqlalchemy import text
                result = session.execute(text("SELECT 1"))
                assert result.scalar() == 1
            logger.info(f"{len(sessions)} 个并发会话均正常执行")
        finally:
            for s in sessions:
                s.close()
