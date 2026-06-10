"""
单元测试 - Pydantic 模型校验
测试 schemas.py 中 UserLogin / UserResponse 的字段验证和序列化行为
"""

import logging

import pytest
from pydantic import ValidationError

from schemas import UserLogin, UserResponse

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestUserLogin:
    """UserLogin 模型测试"""

    def test_valid_login_data(self):
        """正常登录数据应通过验证"""
        user = UserLogin(reader_id="001", password="123456")
        assert user.reader_id == "001"
        assert user.password == "123456"
        logger.info("正常登录数据验证通过")

    def test_missing_reader_id(self):
        """缺少 reader_id 应抛出 ValidationError"""
        with pytest.raises(ValidationError):
            UserLogin(password="123456")
        logger.info("缺少 reader_id 正确抛出 ValidationError")

    def test_missing_password(self):
        """缺少 password 应抛出 ValidationError"""
        with pytest.raises(ValidationError):
            UserLogin(reader_id="001")
        logger.info("缺少 password 正确抛出 ValidationError")

    def test_empty_fields(self):
        """空字符串应通过验证（Pydantic 不校验空值）"""
        user = UserLogin(reader_id="", password="")
        assert user.reader_id == ""
        assert user.password == ""
        logger.info("空字符串字段验证通过")

    def test_from_dict(self):
        """从字典创建实例应正确"""
        data = {"reader_id": "test001", "password": "pass123"}
        user = UserLogin(**data)
        assert user.reader_id == "test001"
        assert user.password == "pass123"
        logger.info("字典创建 UserLogin 成功")

    def test_serialization(self):
        """序列化输出应包含所有字段"""
        user = UserLogin(reader_id="001", password="123456")
        data = user.model_dump()
        assert "reader_id" in data
        assert "password" in data
        logger.info("UserLogin 序列化输出正确")


@pytest.mark.unit
class TestUserResponse:
    """UserResponse 模型测试"""

    def test_valid_response(self):
        """正常响应数据应通过验证"""
        resp = UserResponse(reader_id="001")
        assert resp.reader_id == "001"
        logger.info("UserResponse 正常数据验证通过")

    def test_missing_reader_id(self):
        """缺少 reader_id 应抛出 ValidationError"""
        with pytest.raises(ValidationError):
            UserResponse()
        logger.info("UserResponse 缺少 reader_id 正确抛出 ValidationError")

    def test_from_attributes(self):
        """from_attributes 配置应支持 ORM 对象"""

        class FakeORM:
            reader_id = "orm001"

        resp = UserResponse.model_validate(FakeORM(), from_attributes=True)
        assert resp.reader_id == "orm001"
        logger.info("from_attributes ORM 对象转换成功")

    def test_serialization(self):
        """序列化应只包含 reader_id"""
        resp = UserResponse(reader_id="001")
        data = resp.model_dump()
        assert list(data.keys()) == ["reader_id"]
        logger.info("UserResponse 序列化仅含 reader_id 字段")
