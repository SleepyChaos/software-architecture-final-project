# 图书管理系统

软件架构课程作品，以图书查询与借还界面为业务载体，实践 Vue 3 + FastAPI 前后端分离，以及数据库、缓存、搜索、消息队列、监控和容器编排。

这是课程演示系统。图书样本来自 `backbone/mock_data.py`，登录包含预置账号与人脸模拟账号；各页面和中间件集成的范围以源码和下面的 API 表为准，不将演示登录解释为真实人脸识别能力。

## 从哪里开始

- 想完整体验：按 [Docker Compose](#docker-compose) 启动全部服务，访问 `http://localhost:8080`。
- 想读代码：先看 `src/router/`、`src/views/` 与 `backbone/main.py`，再看 [项目结构](#项目结构)。
- 想了解架构取舍：阅读 [项目技术栈说明](项目技术栈应用说明文档.md)、[代码结构图](代码结构图.md) 和 [Prometheus 查询说明](Prometheus查询说明.md)。

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

需要 Node.js/npm、Python 3.11（与后端镜像一致）和 PostgreSQL。若要体验完整搜索、缓存及热词链路，还需要 Redis、Elasticsearch 和 RabbitMQ；推荐直接使用下方 Compose 方式准备这些服务。

后端终端，从仓库根目录执行：

```bash
python -m venv .venv
# macOS / Linux：
source .venv/bin/activate
# Windows PowerShell 改用：.\.venv\Scripts\Activate.ps1
python -m pip install -r backbone/requirements.txt
cd backbone
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

另开一个终端，从仓库根目录启动前端：

```bash
npm ci
npm run dev
```

前端地址以 Vite 输出为准（默认 `http://localhost:5173`），移动端入口为 `/mobile.html`，也可运行 `npm run dev:mobile`。本地开发的 API 地址由 `.env.development` 指定；后端连接变量见 [环境变量](#环境变量)。后端单独启动不会同时启动 `rabbitmq_worker.py`，需要热词异步统计时另行启动 Worker，或使用 Compose。

### Docker Compose

需要已启动的 Docker Engine / Docker Desktop 与 Docker Compose。前端 Dockerfile 复制本地 `dist/`，因此先构建前端，再构建镜像：

```bash
npm ci
npm run build
docker compose build
docker compose up -d --scale backend=3
docker compose ps
```

首次运行需要下载数据库、搜索和消息队列等镜像；Elasticsearch 也需要一定内存。检查问题时执行 `docker compose logs --tail=100 backend rabbitmq-worker`。停止执行 `docker compose down`，该命令保留数据库和监控卷；`down -v` 会删除这些卷中的数据。

访问 [http://localhost:8080](http://localhost:8080)

Prometheus 访问 [http://localhost:9090](http://localhost:9090)。后端指标地址是 `http://localhost:8000/metrics`，在 Compose 网络里由 `backend:8000/metrics` 采集。

### Kubernetes

需要已配置的 Kubernetes 集群，并确保集群节点可以读取下方构建的镜像；镜像导入或推送方式取决于所用的本地集群/镜像仓库。

```bash
npm ci
npm run build
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


## 开发检查与体验流程

在仓库根目录执行前端检查：

```bash
npm ci
npm run check
npm run lint
npm run build
```

启动服务后，依次检查普通账号登录、图书查询、搜索建议、搜索热词和统计页面。通过 `GET /healthz` 检查后端，通过 Prometheus 查看指标。搜索失败时的本地过滤降级不等于 Elasticsearch 已正常工作，热词更新则依赖 RabbitMQ Worker 与 Redis。

## 演示边界

- 预置账号、默认数据库账号和模拟人脸登录服务于本地课程演示，未包含完整的生产身份与权限方案。
- 页面包含借还与历史展示；后端实际提供的服务以 [API 表](#api-接口) 为准，不将每个前端交互都视为已实现的持久化 API。
- PostgreSQL 数据与 Prometheus 数据使用 Compose 卷；Redis、搜索索引及演示样本的生命周期与之不同。
- Python 依赖目前列于 `backbone/requirements.txt`，并非全部精确锁定；复现遇到版本差异时应记录实际依赖版本。

## 授权说明

仓库目前未提供独立的项目许可证；第三方依赖和示例素材遵循各自许可证。
