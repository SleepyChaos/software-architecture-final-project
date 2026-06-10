# 导入FastAPI框架的核心组件
import json
import os
import time

from fastapi import FastAPI, Depends, HTTPException, Query, Response, status  # FastAPI主要依赖项
from fastapi.middleware.cors import CORSMiddleware  # CORS中间件，用于处理跨域请求
from redis import Redis
from redis.exceptions import RedisError
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy.orm import Session  # SQLAlchemy的数据库会话类型
import models, schemas, database  # 导入本地模块
from mock_data import BOOKS, DEFAULT_SUGGESTIONS
from message_queue import is_rabbitmq_available, publish_event
from search_index import ensure_index, get_elasticsearch_client, search_books, suggest_books

# 创建数据库表
# 在应用启动时，检查并创建所有定义在 models 中的表
# 这确保了数据库表结构与模型定义保持同步
models.Base.metadata.create_all(bind=database.engine)

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CACHE_TTL_RECOMMENDED = int(os.getenv("CACHE_TTL_RECOMMENDED", "300"))
CACHE_TTL_SUGGESTIONS = int(os.getenv("CACHE_TTL_SUGGESTIONS", "180"))
_redis_client = None

HTTP_REQUEST_COUNT = Counter(
    "library_http_requests_total",
    "Total HTTP requests received by the backend",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_LATENCY = Histogram(
    "library_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)

CACHE_OPERATION_COUNT = Counter(
    "library_cache_operations_total",
    "Cache operations in the backend",
    ["cache_name", "operation"],
)

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


@app.middleware("http")
async def prometheus_metrics_middleware(request, call_next):
    start_time = time.perf_counter()
    route = request.scope.get("route")
    endpoint = getattr(route, "path", request.url.path)
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        HTTP_REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=str(status_code),
        ).inc()
        HTTP_REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(time.perf_counter() - start_time)


def get_redis_client():
    """
    获取Redis客户端。
    如果Redis不可用，则返回None，接口会自动降级到本地计算逻辑。
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    try:
        client = Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        client.ping()
        _redis_client = client
        return _redis_client
    except (RedisError, ValueError):
        return None


def read_cache(key: str):
    client = get_redis_client()
    if client is None:
        return None

    try:
        payload = client.get(key)
        if payload:
            CACHE_OPERATION_COUNT.labels(cache_name="redis", operation="hit").inc()
            return json.loads(payload)

        CACHE_OPERATION_COUNT.labels(cache_name="redis", operation="miss").inc()
        return None
    except (RedisError, TypeError, json.JSONDecodeError):
        CACHE_OPERATION_COUNT.labels(cache_name="redis", operation="error").inc()
        return None


def write_cache(key: str, value, ttl: int):
    client = get_redis_client()
    if client is None:
        return

    try:
        client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
        CACHE_OPERATION_COUNT.labels(cache_name="redis", operation="store").inc()
    except RedisError:
        CACHE_OPERATION_COUNT.labels(cache_name="redis", operation="error").inc()
        return


def get_recommended_books():
    """
    获取推荐图书列表。
    """
    return [book for book in BOOKS if book["availableCopies"] > 0][:6]


def get_search_suggestions(query: str):
    """
    根据关键词生成搜索建议。
    """
    return suggest_books(query)

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
        seed_users = [
            ("001", "123456"),
            ("face-user", "face"),
        ]

        created_users = []
        for reader_id, password in seed_users:
            user = db.query(models.User).filter(models.User.reader_id == reader_id).first()
            if user:
                continue

            db.add(
                models.User(
                    reader_id=reader_id,
                    password=password,
                )
            )
            created_users.append(reader_id)

        if created_users:
            db.commit()
            print(f"初始化：已创建演示用户 {created_users}")

        if ensure_index():
            print("初始化：Elasticsearch 图书索引已准备好")
        else:
            print("初始化：Elasticsearch 不可用，搜索将使用本地回退逻辑")
    
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
        publish_event(
            "auth.login_failed",
            {
                "reader_id": user_data.reader_id,
            },
        )
        # 如果验证失败，抛出HTTP异常
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # 401未授权状态码
            detail="用户名或密码错误",  # 错误详细信息
        )

    publish_event(
        "auth.login_success",
        {
            "reader_id": user.reader_id,
        },
    )
    
    # 登录成功，返回用户信息
    # FastAPI会自动使用response_model参数指定的模型进行序列化
    return user


@app.get("/books/recommended")
def recommended_books():
    cache_key = "books:recommended"
    cached = read_cache(cache_key)
    if cached is not None:
        return cached

    data = get_recommended_books()
    write_cache(cache_key, data, CACHE_TTL_RECOMMENDED)
    return data


@app.get("/search/suggestions")
def search_suggestions(q: str = Query(default="", description="搜索关键词")):
    normalized_query = q.strip().lower()
    cache_key = f"search:suggestions:{normalized_query or 'default'}"
    cached = read_cache(cache_key)
    if cached is not None:
        return cached

    suggestions = get_search_suggestions(q)
    write_cache(cache_key, suggestions, CACHE_TTL_SUGGESTIONS)
    return suggestions


@app.get("/books/search")
def search_books_api(
    q: str = Query(default="", description="搜索关键词"),
    category: str | None = Query(default=None, description="分类过滤"),
    only_available: bool = Query(default=False, description="仅看可借"),
    limit: int = Query(default=12, ge=1, le=20, description="返回数量"),
):
    cache_key = f"books:search:{q.strip().lower() or 'default'}:{category or 'all'}:{'available' if only_available else 'all'}:{limit}"
    cached = read_cache(cache_key)
    if cached is not None:
        publish_event(
            "search.books",
            {
                "query": q,
                "category": category,
                "only_available": only_available,
                "result_count": len(cached),
            },
        )
        return cached

    results = search_books(
        query=q,
        category=category,
        only_available=only_available,
        limit=limit,
    )
    write_cache(cache_key, results, CACHE_TTL_RECOMMENDED)
    publish_event(
        "search.books",
        {
            "query": q,
            "category": category,
            "only_available": only_available,
            "result_count": len(results),
        },
    )
    return results


@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "redis": "up" if get_redis_client() is not None else "degraded",
        "elasticsearch": "up" if get_elasticsearch_client() is not None else "degraded",
        "rabbitmq": "up" if is_rabbitmq_available() else "degraded",
    }


@app.get("/analytics/search-trends")
def search_trends(limit: int = Query(default=10, ge=1, le=20, description="返回数量")):
    client = get_redis_client()
    if client is None:
        return [
            {"term": suggestion, "count": 0}
            for suggestion in DEFAULT_SUGGESTIONS[:limit]
        ]

    try:
        trends = client.zrevrange("analytics:search_terms", 0, limit - 1, withscores=True)
        if trends:
            return [
                {"term": term, "count": int(score)}
                for term, score in trends
            ]
    except RedisError:
        pass

    return [
        {"term": suggestion, "count": 0}
        for suggestion in DEFAULT_SUGGESTIONS[:limit]
    ]


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )

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
