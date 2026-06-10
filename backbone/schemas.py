# 从pydantic导入BaseModel基类
# Pydantic是一个数据验证和设置管理库，用于数据验证和序列化
from pydantic import BaseModel


class UserLogin(BaseModel):
    """
    用户登录请求模型
    用于接收前端发送的登录数据
    这个模型定义了登录接口所需的请求数据结构
    """
    reader_id: str  # 读者号码，作为用户的唯一标识
    password: str   # 密码，用户的登录凭证

    class Config:
        """
        Pydantic模型的配置类
        用于配置模型的行为
        """
        from_attributes = True  # 允许从ORM对象的属性创建模型实例


class UserResponse(BaseModel):
    """
    用户响应模型
    用于返回用户信息（不包含密码）
    这个模型定义了登录接口返回的数据结构
    出于安全考虑，响应模型不包含密码信息
    """
    reader_id: str  # 读者号码，作为用户的唯一标识

    class Config:
        """
        Pydantic模型的配置类
        用于配置模型的行为
        """
        from_attributes = True  # 允许从ORM对象的属性创建模型实例
