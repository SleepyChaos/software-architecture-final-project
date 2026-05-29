import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://library:library@127.0.0.1:5432/library",
)

engine = create_engine(DATABASE_URL)

# 创建数据库会话工厂
# sessionmaker是一个工厂函数，用于创建数据库会话类
# autocommit=False: 不自动提交事务，需要手动commit，这是推荐设置
# autoflush=False: 不自动刷新会话，可以手动控制刷新时机
SessionLocal = sessionmaker(
    autocommit=False,  # 禁用自动提交
    autoflush=False,   # 禁用自动刷新
    bind=engine        # 绑定到指定的数据库引擎
)

# 创建Base类，所有的模型类都继承自这个类
# Base类提供了SQLAlchemy ORM的基础功能，包括表映射等
Base = declarative_base()

# 获取数据库会话的依赖函数
# 这是一个生成器函数，用于FastAPI的依赖注入系统
def get_db():
    """
    获取数据库会话的依赖函数
    在请求处理前创建会话，请求处理后关闭会话
    使用yield关键字使得这个函数可以作为上下文管理器使用
    """
    # 创建一个新的数据库会话
    db = SessionLocal()
    try:
        # 将会话对象yield给调用者
        yield db
    finally:
        # 无论是否发生异常，最后都要关闭会话
        # 这是非常重要的资源清理步骤，防止数据库连接泄露
        db.close()
