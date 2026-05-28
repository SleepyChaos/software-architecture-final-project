# 导入SQLAlchemy核心组件
from sqlalchemy import create_engine  # 用于创建数据库引擎
from sqlalchemy.ext.declarative import declarative_base  # 用于创建模型基类
from sqlalchemy.orm import sessionmaker  # 用于创建数据库会话工厂

# 数据库文件路径，使用SQLite
# SQLite是一个轻量级文件数据库，适合开发和测试环境
# connect_args={"check_same_thread": False} 是SQLite必须的配置，因为SQLite默认只允许单线程访问
# 这个参数允许多线程访问同一个数据库连接，是FastAPI等异步框架必需的
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 创建数据库引擎
# 数据库引擎是SQLAlchemy的核心，负责管理数据库连接
# echo=True 表示会打印SQL语句，方便调试（当前设置为False，不打印SQL语句）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # 数据库连接字符串
    connect_args={"check_same_thread": False}  # SQLite多线程配置
)

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
