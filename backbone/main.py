# 导入FastAPI框架的核心组件
import json
import os
import time
from datetime import timedelta

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from redis.exceptions import RedisError
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from sqlalchemy.orm import Session
import models
import schemas
import database
from mock_data import BOOKS, DEFAULT_SUGGESTIONS
from message_queue import is_rabbitmq_available, publish_event
from search_index import (
    ensure_index,
    get_elasticsearch_client,
    search_books,
    suggest_books,
)
from auth import (
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from circuit_breaker import (
    redis_breaker,
    elasticsearch_breaker,
    rabbitmq_breaker,
    get_all_circuit_breaker_states,
)

# 限流配置
RATE_LIMIT_MAX_REQUESTS = 100
RATE_LIMIT_WINDOW_SECONDS = 60

# 创建数据库表
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


@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    client_ip = request.client.host if request.client else "unknown"

    if is_rate_limited(client_ip):
        return Response(
            content=json.dumps({"error": "请求过于频繁，请稍后再试"}),
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            media_type="application/json",
        )

    response = await call_next(request)
    return response


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
            CACHE_OPERATION_COUNT.labels(
                cache_name="redis", operation="hit"
            ).inc()
            return json.loads(payload)

        CACHE_OPERATION_COUNT.labels(
            cache_name="redis", operation="miss"
        ).inc()
        return None
    except (RedisError, TypeError, json.JSONDecodeError):
        CACHE_OPERATION_COUNT.labels(
            cache_name="redis", operation="error"
        ).inc()
        return None


def write_cache(key: str, value, ttl: int):
    client = get_redis_client()
    if client is None:
        return

    try:
        client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
        CACHE_OPERATION_COUNT.labels(
            cache_name="redis", operation="store"
        ).inc()
    except RedisError:
        CACHE_OPERATION_COUNT.labels(
            cache_name="redis", operation="error"
        ).inc()
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
                    hashed_password=get_password_hash(password),
                )
            )
            created_users.append(reader_id)

        if created_users:
            db.commit()
            print(f"初始化：已创建演示用户 {created_users}")

        try:
            if elasticsearch_breaker.call(ensure_index):
                print("初始化：Elasticsearch 图书索引已准备好")
            else:
                print("初始化：Elasticsearch 不可用，搜索将使用本地回退逻辑")
        except Exception as e:
            print(f"初始化：Elasticsearch 熔断触发，{e}")

    finally:
        db.close()


def is_rate_limited(client_ip: str) -> bool:
    """
    检查客户端是否超过限流阈值
    """
    client = get_redis_client()
    if client is None:
        return False

    try:
        key = f"ratelimit:{client_ip}"
        current = client.incr(key)
        if current == 1:
            client.expire(key, RATE_LIMIT_WINDOW_SECONDS)
        return current > RATE_LIMIT_MAX_REQUESTS
    except RedisError:
        return False


# 用户登录接口
@app.post("/login")
def login(
    user_data: schemas.UserLogin,
    db: Session = Depends(database.get_db),
):
    """
    用户登录接口，返回JWT访问令牌

    参数:
    - user_data: 包含 reader_id 和 password 的请求体
    - db: 数据库会话，由FastAPI自动注入

    返回:
    - 登录成功返回 access_token 和 token_type
    - 登录失败抛出 401 异常
    """
    user = authenticate_user(db, user_data.reader_id, user_data.password)
    if not user:
        try:
            rabbitmq_breaker.call(
                publish_event,
                "auth.login_failed",
                {"reader_id": user_data.reader_id},
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    try:
        rabbitmq_breaker.call(
            publish_event,
            "auth.login_success",
            {"reader_id": user.reader_id},
        )
    except Exception:
        pass

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.reader_id}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "reader_id": user.reader_id,
    }


# 用户注册接口
@app.post("/register")
def register(
    user_data: schemas.UserRegister,
    db: Session = Depends(database.get_db),
):
    """
    用户注册接口，创建新用户并返回读者证号

    参数:
    - user_data: 包含 reader_id 和 password 的请求体
    - db: 数据库会话，由FastAPI自动注入

    返回:
    - 注册成功返回 reader_id 和提示信息
    - 用户已存在抛出 409 异常
    """
    # 检查用户是否已存在
    existing_user = db.query(models.User).filter(
        models.User.reader_id == user_data.reader_id
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该读者证号已被注册",
        )

    # 创建新用户
    new_user = models.User(
        reader_id=user_data.reader_id,
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    try:
        rabbitmq_breaker.call(
            publish_event,
            "auth.register_success",
            {"reader_id": new_user.reader_id},
        )
    except Exception:
        pass

    return {
        "reader_id": new_user.reader_id,
        "message": "注册成功",
    }


@app.post("/token")
def login_for_access_token(
    user_data: schemas.UserLogin,
    db: Session = Depends(database.get_db),
):
    """
    OAuth2 token 端点，用于获取访问令牌
    """
    user = authenticate_user(db, user_data.reader_id, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.reader_id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    获取当前登录用户信息（需要认证）
    """
    return current_user


@app.get("/books/recommended")
def recommended_books():
    cache_key = "books:recommended"

    try:
        cached = redis_breaker.call(read_cache, cache_key)
        if cached is not None:
            return cached
    except Exception:
        pass

    data = get_recommended_books()

    try:
        redis_breaker.call(write_cache, cache_key, data, CACHE_TTL_RECOMMENDED)
    except Exception:
        pass

    return data


@app.get("/search/suggestions")
def search_suggestions(q: str = Query(default="", description="搜索关键词")):
    normalized_query = q.strip().lower()
    cache_key = f"search:suggestions:{normalized_query or 'default'}"

    try:
        cached = redis_breaker.call(read_cache, cache_key)
        if cached is not None:
            return cached
    except Exception:
        pass

    try:
        suggestions = elasticsearch_breaker.call(get_search_suggestions, q)
    except Exception:
        suggestions = suggest_books(q)

    try:
        redis_breaker.call(write_cache, cache_key, suggestions, CACHE_TTL_SUGGESTIONS)
    except Exception:
        pass

    return suggestions


@app.get("/books/search")
def search_books_api(
    q: str = Query(default="", description="搜索关键词"),
    category: str | None = Query(default=None, description="分类过滤"),
    only_available: bool = Query(default=False, description="仅看可借"),
    limit: int = Query(default=12, ge=1, le=20, description="返回数量"),
):
    cache_key = (
        f"books:search:{q.strip().lower() or 'default'}:"
        f"{category or 'all'}:"
        f"{'available' if only_available else 'all'}:{limit}"
    )

    try:
        cached = redis_breaker.call(read_cache, cache_key)
        if cached is not None:
            try:
                rabbitmq_breaker.call(
                    publish_event,
                    "search.books",
                    {
                        "query": q,
                        "category": category,
                        "only_available": only_available,
                        "result_count": len(cached),
                    },
                )
            except Exception:
                pass
            return cached
    except Exception:
        pass

    try:
        results = elasticsearch_breaker.call(
            search_books,
            query=q,
            category=category,
            only_available=only_available,
            limit=limit,
        )
    except Exception:
        results = search_books(
            query=q,
            category=category,
            only_available=only_available,
            limit=limit,
        )

    try:
        redis_breaker.call(write_cache, cache_key, results, CACHE_TTL_RECOMMENDED)
    except Exception:
        pass

    try:
        rabbitmq_breaker.call(
            publish_event,
            "search.books",
            {
                "query": q,
                "category": category,
                "only_available": only_available,
                "result_count": len(results),
            },
        )
    except Exception:
        pass

    return results


@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "redis": "up" if get_redis_client() is not None else "degraded",
        "elasticsearch": (
            "up" if get_elasticsearch_client() is not None else "degraded"
        ),
        "rabbitmq": "up" if is_rabbitmq_available() else "degraded",
        "circuit_breakers": get_all_circuit_breaker_states(),
    }


def _get_trends_from_redis(limit: int):
    """从 Redis 获取搜索热词趋势"""
    client = get_redis_client()
    if client is None:
        return None
    try:
        trends = client.zrevrange(
            "analytics:search_terms", 0, limit - 1, withscores=True
        )
        if trends:
            return [
                {"term": term, "count": int(score)}
                for term, score in trends
            ]
    except RedisError:
        return None
    return None


@app.get("/analytics/search-trends")
def search_trends(
    limit: int = Query(default=10, ge=1, le=20, description="返回数量")
):
    try:
        trends = redis_breaker.call(_get_trends_from_redis, limit)
        if trends is not None:
            return trends
    except Exception:
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
