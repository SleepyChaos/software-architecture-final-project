# 从SQLAlchemy导入列类型和数据库基类
from sqlalchemy import Column, String  # Column定义列，String定义数据类型
from database import Base  # 从database模块导入Base基类


class User(Base):
    """
    用户数据模型类
    对应数据库中的 users 表
    这个类继承自Base，使用SQLAlchemy ORM进行数据库操作
    """
    # 指定数据库表名
    # __tablename__是SQLAlchemy的特殊属性，定义模型对应的数据库表名
    __tablename__ = "users"

    # 定义列
    # reader_id: 读者号码，作为主键，字符串类型
    # Column()定义这是一个数据库列
    # String表示字符串类型
    # primary_key=True设置为主键
    # index=True创建索引以提高查询性能
    # comment="读者号码"是数据库列注释
    reader_id = Column(String, primary_key=True, index=True, comment="读者号码")

    # password: 密码，字符串类型
    # nullable=False表示这个字段不能为空
    # 在实际生产环境中，密码应该加密存储，这里为了演示使用明文存储
    password = Column(String, nullable=False, comment="密码")

    def __repr__(self):
        """
        定义对象的字符串表示形式
        当打印User对象时，会返回这个格式的字符串
        这有助于调试和日志记录
        """
        return f"<User(reader_id={self.reader_id})>"
