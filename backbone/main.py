# 导入FastAPI框架的核心组件
from fastapi import FastAPI, Depends, HTTPException, status  # FastAPI主要依赖项
from fastapi.middleware.cors import CORSMiddleware  # CORS中间件，用于处理跨域请求
from sqlalchemy.orm import Session  # SQLAlchemy的数据库会话类型
import models, schemas, database  # 导入本地模块

# 创建数据库表
# 在应用启动时，检查并创建所有定义在 models 中的表
# 这确保了数据库表结构与模型定义保持同步
models.Base.metadata.create_all(bind=database.engine)

# 创建FastAPI应用实例
# title参数设置API文档的标题
# description参数设置API文档的描述信息
app = FastAPI(
    title="Library Backend",  # API文档标题
    description="简单的图书馆后台系统"  # API文档描述
)

# 配置 CORS (跨域资源共享)
# CORS中间件允许前端应用从不同的域名访问后端接口
# 这对于前后端分离的开发模式是必需的
app.add_middleware(
    CORSMiddleware,  # CORS中间件类
    allow_origins=["*"],  # 允许所有来源，生产环境应限制为特定域名
    allow_credentials=True,  # 允许携带认证信息（如cookies）
    allow_methods=["*"],  # 允许所有HTTP方法（GET, POST, PUT, DELETE等）
    allow_headers=["*"],  # 允许所有请求头
)

# 依赖注入函数
# 这个函数用于FastAPI的依赖注入系统，提供数据库会话
def get_db():
    """
    获取数据库会话的依赖函数
    这个函数是对database.get_db()的包装，用于FastAPI的依赖注入
    """
    # 调用database模块中的get_db函数，获取数据库会话生成器
    return database.get_db()

# 应用启动事件处理函数
# 这个函数在FastAPI应用启动时自动执行
@app.on_event("startup")
def startup_event():
    """
    应用启动时的初始化操作
    这里我们预置一个测试用户，方便测试登录功能
    """
    # 创建数据库会话
    db = database.SessionLocal()
    try:
        # 检查是否已有用户
        # 使用first()方法获取查询结果的第一条记录，如果没有记录则返回None
        user = db.query(models.User).first()
        
        # 如果没有找到用户，创建一个默认用户
        if not user:
            # 创建测试用户对象
            # 读者号: 001, 密码: 123456
            test_user = models.User(
                reader_id="001",  # 设置读者ID
                password="123456"  # 设置密码（注意：生产环境应该加密存储）
            )
            
            # 将用户对象添加到数据库会话
            db.add(test_user)
            
            # 提交事务，将数据持久化到数据库
            db.commit()
            
            # 打印日志信息，确认用户创建成功
            print("初始化：已创建测试用户 (reader_id='001', password='123456')")
    
    # finally块确保无论是否发生异常都会执行
    finally:
        # 关闭数据库会话，释放资源
        db.close()

# 用户登录接口
# 使用POST方法接收用户登录凭据
# response_model参数指定响应数据的模型
@app.post("/login", response_model=schemas.UserResponse)
def login(user_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    """
    用户登录接口
    
    参数:
    - user_data: 包含 reader_id 和 password 的请求体
    - db: 数据库会话，由FastAPI自动注入
    
    返回:
    - 登录成功返回用户信息
    - 登录失败抛出 401 异常
    """
    # 在数据库中查找对应 reader_id 的用户
    # filter()方法添加查询条件，first()方法获取第一条匹配的记录
    user = db.query(models.User).filter(models.User.reader_id == user_data.reader_id).first()
    
    # 验证用户是否存在以及密码是否匹配
    # not user: 检查用户是否存在
    # user.password != user_data.password: 检查密码是否匹配
    # 注意：实际生产环境中密码应该加密存储（如使用 bcrypt），这里仅作演示使用明文
    if not user or user.password != user_data.password:
        # 如果验证失败，抛出HTTP异常
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # 401未授权状态码
            detail="用户名或密码错误",  # 错误详细信息
        )
    
    # 登录成功，返回用户信息
    # FastAPI会自动使用response_model参数指定的模型进行序列化
    return user

# 根路由
# 用于测试服务是否正常运行
@app.get("/")
def read_root():
    """
    根路由，用于测试服务是否运行正常
    访问这个路由会返回服务的基本信息
    """
    # 返回服务运行状态信息
    return {
        "message": "Backend is running. Go to /docs for API documentation."
    }
