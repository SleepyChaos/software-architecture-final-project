# 图书管理系统

软件架构期末项目，实现了一个基于 Vue 3 + FastAPI + PostgreSQL 的图书管理系统，支持 Docker Compose 和 Kubernetes 容器化部署。

## 技术栈

| 类别              | 技术                                             |
| ----------------- | ------------------------------------------------ |
| 前端              | Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS |
| 后端              | FastAPI (Python) + SQLAlchemy                    |
| 数据库            | PostgreSQL (pgvector)                            |
| 缓存              | Redis                                            |
| 搜索引擎          | Elasticsearch                                    |
| 消息队列          | RabbitMQ                                         |
| 可视化            | ECharts                                          |
| 监控              | Prometheus                                       |
| 反向代理/负载均衡 | Nginx (upstream + Docker DNS resolver)           |
| 容器化            | Docker + Docker Compose                          |
| 编排              | Kubernetes                                       |

## 测试账号

| 读者证号  | 密码   | 说明         |
| --------- | ------ | ------------ |
| 001       | 123456 | 普通登录     |
| face-user | face   | 人脸模拟登录 |

## 快速开始

### 原生开发

```bash
# 1. 启动 PostgreSQL（需要提前安装或启动 Docker 容器）
# 2. 后端
cd backbone
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. 前端
npm install
npm run dev
```

### Docker Compose

```bash
npm install
npm run build
docker compose build
docker compose up -d --scale backend=3
```

访问 [http://localhost:8080](http://localhost:8080)

Prometheus 访问 [http://localhost:9090](http://localhost:9090)。后端指标地址是 `http://localhost:8000/metrics`，在 Compose 网络里由 `backend:8000/metrics` 采集。

### Kubernetes

```bash
npm install && npm run build
docker build -t library-system-frontend:latest .
docker build -t library-system-backend:latest -f backbone/Dockerfile .
kubectl apply -f k8s/
kubectl port-forward svc/library-frontend 8080:80
```

Prometheus 在 K8s 中通过 `library-prometheus` 服务访问，执行 `kubectl port-forward svc/library-prometheus 9090:9090` 即可打开控制台。

## 项目结构

```
├── backbone/                 # 后端 FastAPI
│   ├── main.py               # 应用入口 + API 路由
│   ├── database.py           # SQLAlchemy 数据库配置
│   ├── models.py             # ORM 模型 (User)
│   ├── schemas.py            # Pydantic 数据验证
│   └── mock_data.py          # 模拟图书数据
├── src/                      # 前端 Vue 3
│   ├── views/                # 页面组件
│   │   ├── Home.vue          # PC 首页
│   │   ├── Statistics.vue    # ECharts 数据统计
│   │   └── mobile/           # 移动端页面
│   ├── stores/               # Pinia 状态管理
│   ├── router/               # Vue Router 路由
│   └── components/           # 共享组件
├── k8s/                      # Kubernetes 清单
├── docker-compose.yml        # Docker Compose 编排
├── nginx.conf                # Nginx 配置 (反向代理 + 负载均衡)
├── Dockerfile                # 前端 Docker 镜像
└── .npmrc                    # npm 淘宝镜像配置
```

## 服务组成

| 服务                 | 端口         | 说明                             |
| -------------------- | ------------ | -------------------------------- |
| frontend (Nginx)     | 8080         | 静态资源 + API 代理 + 负载均衡   |
| backend (FastAPI) x3 | 8000 (内部)  | 多副本，Nginx upstream 轮询分发  |
| PostgreSQL           | 5432         | 用户数据持久化                   |
| Redis                | 6379 (内部)  | 缓存推荐图书 + 搜索建议          |
| Elasticsearch        | 9200         | 图书搜索索引与检索               |
| RabbitMQ             | 5672 / 15672 | 搜索事件异步投递 + 管理控制台    |
| Prometheus           | 9090         | 采集后端请求量、延迟和缓存命中率 |

## API 接口

| 端点                     | 方法 | 说明                                                |
| ------------------------ | ---- | --------------------------------------------------- |
| /login                   | POST | 用户登录                                            |
| /books/recommended       | GET  | 推荐图书 (Redis 缓存)                               |
| /books/search            | GET  | Elasticsearch 图书检索 (Redis 缓存 + RabbitMQ 事件) |
| /search/suggestions      | GET  | 搜索建议 (Redis 缓存)                               |
| /analytics/search-trends | GET  | RabbitMQ 异步统计的搜索热词                         |
| /healthz                 | GET  | 健康检查                                            |
| /metrics                 | GET  | Prometheus 指标                                     |

## 环境变量

### 前端

- `VITE_API_BASE_URL`：后端 API 地址（开发环境 `.env.development`：`http://127.0.0.1:8000`，生产构建 `.env.production`：`/api`）

### 后端

- `DATABASE_URL`：PostgreSQL 连接字符串（默认 `postgresql://library:library@127.0.0.1:5432/library`）
- `REDIS_URL`：Redis 连接地址
- `ELASTICSEARCH_URL`：Elasticsearch 连接地址
- `RABBITMQ_URL`：RabbitMQ 连接地址
- `CACHE_TTL_RECOMMENDED`：推荐缓存 TTL（默认 300s）
- `CACHE_TTL_SUGGESTIONS`：搜索建议缓存 TTL（默认 180s）

### Elasticsearch

- 启动后会把 `mock_data.py` 里的图书数据自动写入 `library-books` 索引
- 搜索页面调用 `/books/search` 时，优先走 Elasticsearch，失败时自动降级到本地过滤

### RabbitMQ

- `/books/search` 每次请求都会投递一条搜索事件到 `library.events` 队列
- `backbone/rabbitmq_worker.py` 会消费队列，并把热词统计写入 Redis 的 `analytics:search_terms`
- 统计页通过 `/analytics/search-trends` 展示热词排行

### Prometheus

- `prometheus.yml`：Prometheus 抓取配置，默认采集 `backend:8000/metrics`
- 如果你把后端直接跑在本机而不是 Compose/K8s 里，把 `prometheus.yml` 里的目标改成 `host.docker.internal:8000`
