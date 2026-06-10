# 图书管理系统 — Docker / Kubernetes / Redis 技术说明文档

> 项目路径：`/Users/chaos/Documents/软件架构期末大作业增加技术栈/software-architecture-final-project`
>
> 项目简介：基于 FastAPI + Vue 3 的图书管理系统，集成 Elasticsearch 全文检索、RabbitMQ 异步消息、Redis 缓存、Prometheus 监控等中间件，通过 Docker 容器化部署，并支持 Kubernetes 编排。

---

## 一、Docker

### 1. 是什么

Docker 是一种**容器化平台**，它将应用程序及其所有依赖项（运行时、库、配置文件）打包到一个轻量级、可移植的**容器镜像（Image）**中。容器在宿主操作系统的内核上直接运行，无需像虚拟机那样启动完整的客户操作系统，因此启动速度秒级、资源开销极低。

**核心概念映射到本项目**：

| Docker 概念           | 本项目中的体现                                                                    |
| --------------------- | --------------------------------------------------------------------------------- |
| **Dockerfile**        | 定义两个镜像的构建步骤：前端（`Dockerfile`）和后端（`backbone/Dockerfile`）       |
| **Image（镜像）**     | `library-system-frontend:latest`、`library-system-backend:latest` 等 8 个容器镜像 |
| **Container（容器）** | 由 `docker-compose.yml` 编排的 8 个运行时容器实例                                 |
| **Volume（卷）**      | `pgdata`（PostgreSQL 持久化）、`prometheus-data`（监控数据持久化）                |
| **Network（网络）**   | Docker Compose 默认 bridge 网络，服务名即 DNS 主机名                              |

### 2. 为什么

| 优势               | 本项目的具体收益                                                                                                                  |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| **环境一致性**     | 团队成员在不同操作系统上运行 `docker compose up` 即可获得完全相同的运行环境，消除"在我机器上能跑"问题                             |
| **依赖隔离**       | PostgreSQL（含 pgvector 扩展）、Elasticsearch 8.x、RabbitMQ、Redis 7 等中间件无需在宿主机安装，各自运行在隔离容器中，版本冲突为零 |
| **一键部署**       | 一条 `docker compose up` 命令即可启动包含前端、后端、数据库、缓存、搜索、消息队列、监控在内的完整系统                             |
| **快速重建**       | 任何服务状态异常，`docker compose down -v && docker compose up` 即可恢复到干净初始状态                                            |
| **镜像分层与缓存** | Dockerfile 先复制 `requirements.txt` 再安装依赖，后复制源码——代码变更时不重新安装 Python 包，构建速度显著提升                     |
| **轻量级**         | 前端用 `nginx:1.27-alpine`（约 7MB）、Redis 用 `redis:7-alpine`（约 30MB），Alpine 镜像远小于完整发行版                           |

**为什么不用虚拟机**：本项目 8 个服务如果用虚拟机方式，至少需要 8 个 VM 实例，每个占用 GB 级内存和分钟级启动时间；Docker 容器共享宿主内核，总共仅需约 2-3GB 内存，启动时间秒级。

### 3. 怎么用

#### 3.1 两个 Dockerfile

**前端 Dockerfile**（根目录 `Dockerfile`）：

```dockerfile
FROM nginx:1.27-alpine                          # 1. 基础镜像：Nginx + Alpine Linux
COPY nginx.conf /etc/nginx/conf.d/default.conf  # 2. 复制反向代理配置
COPY dist /usr/share/nginx/html                 # 3. 复制 Vite 构建产物（静态资源）
EXPOSE 80                                       # 4. 声明监听端口
```

- **构建前提**：需先执行 `npm run build` 生成 `dist/` 目录
- **运行时行为**：Nginx 在 80 端口监听，`/api/*` 请求通过 `proxy_pass` 转发到后端，其他请求返回 SPA 静态文件

**后端 Dockerfile**（`backbone/Dockerfile`）：

```dockerfile
FROM python:3.11-slim                            # 1. 基础镜像：Python 3.11 精简版
WORKDIR /app                                     # 2. 设置工作目录
COPY backbone/requirements.txt /tmp/requirements.txt  # 3. 先复制依赖清单
RUN pip install --no-cache-dir -r /tmp/requirements.txt  # 4. 安装 Python 依赖
COPY backbone /app                               # 5. 再复制全部源码
EXPOSE 8000                                      # 6. 声明监听端口
```

- **同一镜像，两种入口**：该镜像同时用于 `backend`（启动命令 `uvicorn main:app`）和 `rabbitmq-worker`（启动命令 `python rabbitmq_worker.py`），通过 `docker-compose.yml` 中的 `command` 字段区分
- **分层优化**：先安装依赖后复制源码——源码频繁变更时，依赖层可从缓存复用，无需重新 `pip install`

#### 3.2 Docker Compose 编排

项目使用 `docker-compose.yml` 编排 **8 个服务**，整体架构如下：

```
┌─────────────────────────────────────────────────────────────────┐
│  Docker Compose 编排（8 个服务）                                  │
│                                                                 │
│  ┌───────────────┐    反向代理 + 负载均衡                         │
│  │   frontend    │────/api/*──→  backend:8000 (3副本轮询)        │
│  │ (Nginx:80)    │                                              │
│  │ 宿主机:8080   │                                              │
│  └───────────────┘                                              │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────┐                                              │
│  │   backend     │───FastAPI + uvicorn                          │
│  │ (Python:8000) │                                              │
│  └──┬────┬────┬──┴────┐                                        │
│     │    │    │       │                                         │
│     ▼    ▼    ▼       ▼                                         │
│  ┌────┐┌────┐┌──────┐┌────────┐                                │
│  │ db ││redis││  ES  ││RabbitMQ│──→ rabbitmq-worker             │
│  │5432││6379 ││ 9200 ││5672    │    (消费事件→写Redis)           │
│  └────┘└────┘└──────┘└────────┘                                │
│                                                                 │
│  ┌───────────────┐                                              │
│  │  prometheus   │── 每15s采集 backend:8000/metrics              │
│  │   :9090       │                                              │
│  └───────────────┘                                              │
│                                                                 │
│  持久化卷: pgdata (PostgreSQL) + prometheus-data                 │
└─────────────────────────────────────────────────────────────────┘
```

**8 个服务详情**：

| #   | 服务名            | 容器名                  | 镜像                            | 端口映射                   | 职责                          |
| --- | ----------------- | ----------------------- | ------------------------------- | -------------------------- | ----------------------------- |
| 1   | `frontend`        | `library-frontend`      | 构建（根 Dockerfile）           | `8080:80`                  | Nginx 静态资源托管 + 反向代理 |
| 2   | `backend`         | 自动命名                | 构建（backbone/Dockerfile）     | 8000（仅暴露）             | FastAPI 后端 API              |
| 3   | `rabbitmq-worker` | 自动命名                | 构建（backbone/Dockerfile）     | —                          | 消费 RabbitMQ 事件            |
| 4   | `db`              | `library-db`            | `pgvector/pgvector:pg17-trixie` | `5432:5432`                | PostgreSQL + 向量扩展         |
| 5   | `redis`           | `library-redis`         | `redis:7-alpine`                | 6379（仅暴露）             | 缓存 + 分析数据               |
| 6   | `elasticsearch`   | `library-elasticsearch` | `elasticsearch:8.15.2`          | `9200:9200`                | 全文检索引擎                  |
| 7   | `rabbitmq`        | `library-rabbitmq`      | `rabbitmq:3-management-alpine`  | `5672:5672`, `15672:15672` | 消息队列                      |
| 8   | `prometheus`      | `library-prometheus`    | `prom/prometheus:v2.54.1`       | `9090:9090`                | 监控指标采集                  |

**服务依赖与启动顺序**：

```
frontend ──► backend ──► db (condition: service_healthy)      # PostgreSQL 必须通过健康检查
                    ├──► redis (condition: service_started)    # 其余只需容器启动
                    ├──► elasticsearch (condition: service_started)
                    └──► rabbitmq (condition: service_started)

rabbitmq-worker ──► rabbitmq + redis
prometheus ──► backend
```

- **`service_healthy`**：仅 PostgreSQL 使用，通过 `pg_isready` 确保数据库完全就绪后端才启动
- **`service_started`**：Redis、ES、RabbitMQ 仅需容器启动即可——因为后端代码对这些中间件实现了连接超时和优雅降级（连不上就跳过，不阻塞启动）

**后端环境变量**：

| 变量名                  | 值                                             | 说明                   |
| ----------------------- | ---------------------------------------------- | ---------------------- |
| `PYTHONPATH`            | `/app`                                         | Python 模块搜索路径    |
| `DATABASE_URL`          | `postgresql://library:library@db:5432/library` | 数据库连接串           |
| `REDIS_URL`             | `redis://redis:6379/0`                         | Redis 连接串           |
| `ELASTICSEARCH_URL`     | `http://elasticsearch:9200`                    | ES 连接地址            |
| `RABBITMQ_URL`          | `amqp://guest:guest@rabbitmq:5672/%2F`         | RabbitMQ 连接串        |
| `CACHE_TTL_RECOMMENDED` | `300`                                          | 推荐图书缓存 TTL（秒） |
| `CACHE_TTL_SUGGESTIONS` | `180`                                          | 搜索建议缓存 TTL（秒） |

**持久化卷**：

| 卷名              | 挂载路径                   | 用途                  |
| ----------------- | -------------------------- | --------------------- |
| `pgdata`          | `/var/lib/postgresql/data` | PostgreSQL 数据持久化 |
| `prometheus-data` | `/prometheus`              | Prometheus TSDB 数据  |

**健康检查**（仅 db 服务定义）：

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U library"]
  interval: 5s
  timeout: 5s
  retries: 5
```

#### 3.3 日常使用命令

```bash
# 构建并启动所有服务
docker compose up --build

# 后台运行
docker compose up -d

# 查看运行状态
docker compose ps

# 查看后端日志
docker compose logs -f backend

# 停止并删除容器（保留数据卷）
docker compose down

# 完全重置（包括删除数据卷）
docker compose down -v

# 重新构建某个服务
docker compose build backend
```

#### 3.4 Nginx 反向代理配置

`nginx.conf` 在 Docker 容器中承担两个职责——静态资源托管和 API 反向代理：

```nginx
upstream backend_pool {
    server backend:8000;                # Docker DNS 解析到后端容器
}

server {
    listen 80;
    resolver 127.0.0.11 valid=30s;     # Docker 内置 DNS 解析器

    location /api/ {
        proxy_pass http://backend_pool/;    # /api/* 请求转发到后端
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /assets/ {
        try_files $uri =404;           # 静态资源直接返回
    }

    location / {
        try_files $uri $uri/ /index.html;  # SPA 路由回退
    }
}
```

- `resolver 127.0.0.11`：Docker 内置 DNS 服务器，每次请求重新解析 `backend` 主机名，实现多副本的轮询负载均衡
- 当后端扩展到多副本时，Nginx 自动将请求分发到不同后端实例

#### 3.5 .dockerignore

```
.git
.gitignore
.vscode
.idea
.DS_Store
node_modules
.venv
backbone/__pycache__
backbone/*.pyc
*.log
```

排除版本控制目录、IDE 配置、依赖包、Python 缓存和日志文件，减小构建上下文大小，加速构建。

---

## 二、Kubernetes（K8s）

### 1. 是什么

Kubernetes（简称 K8s）是 Google 开源的**容器编排平台**，用于自动化容器化应用的部署、扩缩、负载均衡和运维管理。它将多台物理/虚拟机抽象为一个统一的计算集群，以**声明式 YAML** 定义应用期望状态，K8s 控制平面持续将实际状态向期望状态收敛。

**核心概念映射到本项目**：

| K8s 概念       | 本项目中的体现                                                    |
| -------------- | ----------------------------------------------------------------- |
| **Deployment** | 8 个 Deployment 定义（后端 3 副本、Worker 1 副本、其余各 1 副本） |
| **Service**    | 7 个 ClusterIP Service，提供稳定的集群内 DNS 名和负载均衡         |
| **ConfigMap**  | 3 个 ConfigMap，集中管理后端环境变量、ES 配置、Prometheus 配置    |
| **PVC**        | 1 个 PersistentVolumeClaim，为 PostgreSQL 提供持久化存储          |
| **Pod**        | 最小调度单元，每个 Deployment 管理 Pod 副本                       |

### 2. 为什么

| 优势               | 本项目的具体收益                                                                                            |
| ------------------ | ----------------------------------------------------------------------------------------------------------- |
| **声明式部署**     | `kubectl apply -f k8s/` 一键部署全部 18 个资源，状态由 K8s 自动维护——与 Docker Compose 的命令式操作形成对比 |
| **自动负载均衡**   | 后端 3 副本通过 Service 自动实现轮询分发，无需像 Docker Compose 那样依赖 Nginx upstream + DNS resolver      |
| **自愈能力**       | 后端配置了 livenessProbe 和 readinessProbe（`/healthz`），Pod 崩溃或无响应时 K8s 自动重启/摘除，用户无感知  |
| **配置与代码分离** | ConfigMap 将数据库 URL、Redis URL 等配置从镜像中抽离，同一镜像可在不同环境使用不同配置                      |
| **弹性伸缩基础**   | 后端 3 副本验证了多实例无状态部署，为未来 HPA（水平自动扩缩）奠定基础                                       |
| **服务发现**       | Service 提供集群内 DNS 名称（如 `library-redis:6379`、`backend:8000`），服务间调用无需硬编码 IP             |

**为什么有了 Docker Compose 还要 K8s**：Docker Compose 适合单机开发/测试，但缺乏健康检查自愈、多副本负载均衡、声明式状态管理、滚动更新等生产级能力。K8s 提供了容器编排的工业标准方案，本项目通过 K8s 展示从开发环境到生产编排的架构演进能力。

**本项目定位**：根据 `K8s+Docker+Redis技术栈增加计划.md`，K8s 在本项目中被定位为**轻量化编排工具**，用于演示容器编排的架构能力，而非追求生产级集群平台。

### 3. 怎么用

#### 3.1 K8s 资源全览

项目 `k8s/` 目录包含 **18 个 YAML 文件**，定义了以下资源：

| 资源类型   | 数量 | 详情                                                                                                                 |
| ---------- | ---- | -------------------------------------------------------------------------------------------------------------------- |
| Deployment | 8    | backend(3副本)、rabbitmq-worker(1)、frontend(1)、postgres(1)、redis(1)、rabbitmq(1)、elasticsearch(1)、prometheus(1) |
| Service    | 7    | 全部 ClusterIP，仅集群内可访问                                                                                       |
| ConfigMap  | 3    | backend-config、elasticsearch-config、prometheus-config                                                              |
| PVC        | 1    | postgres-pvc（1Gi，ReadWriteOnce）                                                                                   |

**18 个文件清单**：

| 文件名                          | 资源类型              | 用途                                          |
| ------------------------------- | --------------------- | --------------------------------------------- |
| `backend-deployment.yaml`       | Deployment x2         | 后端 API（3 副本）+ RabbitMQ Worker（1 副本） |
| `backend-service.yaml`          | Service (ClusterIP)   | 后端服务暴露，端口 8000                       |
| `backend-configmap.yaml`        | ConfigMap             | 后端环境变量（6 个）                          |
| `frontend-deployment.yaml`      | Deployment            | 前端 Nginx 部署（1 副本）                     |
| `frontend-service.yaml`         | Service (ClusterIP)   | 前端服务暴露，端口 80                         |
| `postgres-deployment.yaml`      | Deployment            | PostgreSQL 数据库（1 副本）                   |
| `postgres-service.yaml`         | Service (ClusterIP)   | PostgreSQL 服务暴露，端口 5432                |
| `postgres-pvc.yaml`             | PersistentVolumeClaim | PostgreSQL 持久化存储（1Gi）                  |
| `redis-deployment.yaml`         | Deployment            | Redis 缓存（1 副本）                          |
| `redis-service.yaml`            | Service (ClusterIP)   | Redis 服务暴露，端口 6379                     |
| `elasticsearch-deployment.yaml` | Deployment            | Elasticsearch 搜索引擎（1 副本）              |
| `elasticsearch-service.yaml`    | Service (ClusterIP)   | ES 服务暴露，端口 9200                        |
| `elasticsearch-configmap.yaml`  | ConfigMap             | ES 配置（单节点、安全关闭）                   |
| `rabbitmq-deployment.yaml`      | Deployment            | RabbitMQ 消息队列（1 副本）                   |
| `rabbitmq-service.yaml`         | Service (ClusterIP)   | RabbitMQ 服务暴露，端口 5672+15672            |
| `prometheus-deployment.yaml`    | Deployment            | Prometheus 监控（1 副本）                     |
| `prometheus-service.yaml`       | Service (ClusterIP)   | Prometheus 服务暴露，端口 9090                |
| `prometheus-configmap.yaml`     | ConfigMap             | Prometheus 抓取配置                           |

#### 3.2 服务架构图

```
外部用户
  │
  │ kubectl port-forward svc/library-frontend 8080:80
  ▼
┌──────────────────────────────────────────────────────────┐
│  library-frontend (ClusterIP:80)                          │
│    Nginx → /api/* → proxy_pass http://backend:8000       │
└────────────┬─────────────────────────────────────────────┘
             │ K8s Service 负载均衡（自动轮询 3 个 Pod）
             ▼
┌──────────────────────────────────────────────────────────┐
│  backend (ClusterIP:8000)                                │
│    ┌─ Pod 1 (uvicorn main:app)                            │
│    ├─ Pod 2 (uvicorn main:app)     ← 3 副本自动轮询       │
│    └─ Pod 3 (uvicorn main:app)                            │
│    configMapRef: library-backend-config                    │
└──┬────────┬──────────┬──────────────┘
   │        │          │
   ▼        ▼          ▼
┌──────┐ ┌──────┐ ┌──────────┐  ┌───────────┐
│ PG   │ │Redis │ │    ES    │  │  RabbitMQ  │
│5432  │ │6379  │ │  9200    │  │5672+15672  │
│PVC   │ │      │ │          │  │            │
│1Gi   │ │      │ │          │  │     ↓      │
└──────┘ └──────┘ └──────────┘  │  Worker    │
                                │  (消费事件) │
                                └─────────────┘

┌──────────────────────┐
│  Prometheus :9090     │
│  采集 backend:8000    │
│  /metrics (15s间隔)   │
└──────────────────────┘
```

#### 3.3 关键 Deployment 详解

**后端 Deployment**（`k8s/backend-deployment.yaml`）——唯一配置了健康检查和多副本：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: library-backend
spec:
  replicas: 3 # 3 个副本实现高可用 + 负载均衡
  selector:
    matchLabels:
      app: library-backend
  template:
    spec:
      containers:
        - name: backend
          image: library-system-backend:latest
          envFrom:
            - configMapRef:
                name: library-backend-config # 配置从 ConfigMap 注入
          command:
            [
              "sh",
              "-c",
              "PYTHONPATH=/app uvicorn main:app --host 0.0.0.0 --port 8000",
            ]
          livenessProbe: # 存活探针：Pod 无响应则重启
            httpGet: { path: /healthz, port: 8000 }
            initialDelaySeconds: 10 # 启动后等 10s 才开始探测
            periodSeconds: 15 # 每 15s 探测一次
          readinessProbe: # 就绪探针：未就绪则从 Service 摘除
            httpGet: { path: /healthz, port: 8000 }
            initialDelaySeconds: 5
            periodSeconds: 10
```

- **livenessProbe**：检测到 `/healthz` 返回失败 → K8s 杀死并重启该 Pod
- **readinessProbe**：检测到 `/healthz` 返回失败 → 从 Service 的 Endpoints 中摘除该 Pod，不再向其发送流量
- 两者结合实现了**故障自愈**：坏掉的 Pod 被自动替换，期间流量只发往健康的 Pod

**RabbitMQ Worker Deployment**（同一文件，第二个 Deployment）：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: library-rabbitmq-worker
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: worker
          image: library-system-backend:latest # 与 backend 共用同一镜像
          command: ["sh", "-c", "PYTHONPATH=/app python rabbitmq_worker.py"] # 不同启动命令
```

- **一镜两用**：同一个 Python 镜像，通过不同的 `command` 启动不同进程（API 服务器 vs 消息消费者）
- 这是容器化的常见模式——镜像定义"能做什么"，启动命令决定"做什么"

#### 3.4 ConfigMap 配置管理

**后端 ConfigMap**（`k8s/backend-configmap.yaml`）：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: library-backend-config
data:
  DATABASE_URL: postgresql://library:library@library-postgres:5432/library
  REDIS_URL: redis://library-redis:6379/0
  ELASTICSEARCH_URL: http://library-elasticsearch:9200
  RABBITMQ_URL: amqp://guest:guest@library-rabbitmq:5672/%2F
  CACHE_TTL_RECOMMENDED: "300"
  CACHE_TTL_SUGGESTIONS: "180"
  PYTHONPATH: /app
```

- 注意 K8s 中服务间通过 **Service DNS 名称**通信（如 `library-postgres`、`library-redis`），而 Docker Compose 中使用 **Compose 服务名**（如 `db`、`redis`）
- Deployment 通过 `envFrom.configMapRef` 将所有环境变量一次性注入容器

**Elasticsearch ConfigMap**（`k8s/elasticsearch-configmap.yaml`）：

```yaml
data:
  elasticsearch.yml: |
    cluster.name: library-cluster
    node.name: library-node
    network.host: 0.0.0.0
    discovery.type: single-node
    xpack.security.enabled: false
```

**Prometheus ConfigMap**（`k8s/prometheus-configmap.yaml`）：

```yaml
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: library-backend
        metrics_path: /metrics
        static_configs:
          - targets:
              - backend:8000
```

#### 3.5 存储策略

| 组件           | 存储方式                                        | 说明                       |
| -------------- | ----------------------------------------------- | -------------------------- |
| **PostgreSQL** | **PersistentVolumeClaim**（1Gi，ReadWriteOnce） | 唯一持久化存储，数据不丢失 |
| Elasticsearch  | **emptyDir**（临时）                            | Pod 重启数据丢失           |
| RabbitMQ       | **emptyDir**（临时）                            | Pod 重启数据丢失           |
| Redis          | 无挂载卷                                        | 内存数据，无持久化         |
| Prometheus     | **emptyDir**（临时）                            | 监控数据不持久化           |

#### 3.6 服务类型与外部访问

**所有 Service 均为 ClusterIP**——仅集群内部可访问，不对外暴露端口。本地访问需通过 `kubectl port-forward`：

```bash
# 访问前端
kubectl port-forward svc/library-frontend 8080:80

# 访问 Prometheus 监控面板
kubectl port-forward svc/library-prometheus 9090:9090

# 访问 RabbitMQ 管理界面
kubectl port-forward svc/library-rabbitmq 15672:15672
```

#### 3.7 部署与清理命令

```bash
# 1. 构建镜像
docker build -t library-system-frontend:latest .
docker build -t library-system-backend:latest -f backbone/Dockerfile .

# 2. 将镜像加载到 K8s 集群（以 kind 为例）
kind load docker-image library-system-frontend:latest
kind load docker-image library-system-backend:latest

# 3. 部署所有资源
kubectl apply -f k8s/

# 4. 查看部署状态
kubectl get pods
kubectl get svc

# 5. 端口转发访问
kubectl port-forward svc/library-frontend 8080:80

# 6. 清理所有资源
kubectl delete -f k8s/
```

#### 3.8 容器镜像清单

| 服务              | 镜像                                                   | 类型                              |
| ----------------- | ------------------------------------------------------ | --------------------------------- |
| Frontend (Nginx)  | `library-system-frontend:latest`                       | 自定义构建（根 Dockerfile）       |
| Backend (FastAPI) | `library-system-backend:latest`                        | 自定义构建（backbone/Dockerfile） |
| RabbitMQ Worker   | `library-system-backend:latest`                        | 同后端镜像，不同启动命令          |
| PostgreSQL        | `pgvector/pgvector:pg17-trixie`                        | 公开镜像（含 pgvector 扩展）      |
| Redis             | `library-system-redis:latest`                          | 自定义构建                        |
| RabbitMQ          | `rabbitmq:3-management-alpine`                         | 公开镜像                          |
| Elasticsearch     | `docker.elastic.co/elasticsearch/elasticsearch:8.15.2` | 官方镜像                          |
| Prometheus        | `prom/prometheus:v2.54.1`                              | 官方镜像                          |

#### 3.9 与 Docker Compose 的对比

| 对比维度 | Docker Compose                        | Kubernetes                                            |
| -------- | ------------------------------------- | ----------------------------------------------------- |
| 部署方式 | `docker compose up`                   | `kubectl apply -f k8s/`                               |
| 服务发现 | Compose 服务名（`db`、`redis`）       | Service DNS 名（`library-postgres`、`library-redis`） |
| 负载均衡 | Nginx upstream + Docker DNS resolver  | Service 自动轮询（iptables/IPVS）                     |
| 健康检查 | 仅 PostgreSQL 有 `healthcheck`        | 后端有 livenessProbe + readinessProbe                 |
| 配置管理 | 环境变量直接写在 `docker-compose.yml` | ConfigMap 集中管理                                    |
| 持久化   | 命名卷（`pgdata`、`prometheus-data`） | PVC（仅 PostgreSQL）+ emptyDir                        |
| 外部访问 | 端口直接映射到宿主机                  | kubectl port-forward                                  |
| 副本管理 | 每服务 1 个容器                       | 后端 3 副本，可水平扩展                               |

---

## 三、Redis

### 1. 是什么

Redis（Remote Dictionary Server）是一个基于内存的**键值存储系统**，支持多种数据结构（字符串、哈希、列表、集合、有序集合等），以极高的读写性能（单线程每秒 10 万+操作）著称。它既可以作为数据库，也可以作为缓存和消息代理使用。

**核心概念映射到本项目**：

| Redis 概念             | 本项目中的体现                                                   |
| ---------------------- | ---------------------------------------------------------------- |
| **String + SETEX**     | 缓存 API 响应（推荐图书、搜索建议、搜索结果），设置 TTL 自动过期 |
| **Sorted Set（ZSET）** | 搜索热词排行榜（`analytics:search_terms`），按搜索频率排序       |
| **INCR 计数器**        | 登录成功/失败次数统计                                            |
| **数据库 0**           | 默认使用 DB 0（`redis://host:6379/0`）                           |
| **TTL 过期策略**       | 推荐图书 300s、搜索建议 180s、搜索热词 30 天                     |

### 2. 为什么

| 优势                      | 本项目的具体收益                                                                         |
| ------------------------- | ---------------------------------------------------------------------------------------- |
| **极速缓存**              | 内存操作微秒级延迟，推荐图书和搜索建议直接从 Redis 返回，响应时间从数十毫秒降至 1ms 以下 |
| **减轻数据库压力**        | 高频查询（推荐图书、搜索建议）被 Redis 拦截，PostgreSQL 不承受重复查询负载               |
| **Sorted Set 天然排行榜** | 搜索热词统计使用 `ZINCRBY` 原子递增 + `ZREVRANGE` 按分数倒序查询，无需额外排序逻辑       |
| **TTL 自动过期**          | 缓存数据自动过期，无需手动清理；推荐图书 5 分钟过期确保数据新鲜度                        |
| **优雅降级**              | Redis 不可用时，后端自动跳过缓存、直接查询数据库/ES，系统功能不受影响                    |
| **轻量部署**              | `redis:7-alpine` 镜像仅约 30MB，启动即用，无需复杂配置                                   |

**为什么选 Redis 而非 Memcached**：

| 对比维度   | Redis                                  | Memcached              |
| ---------- | -------------------------------------- | ---------------------- |
| 数据结构   | String、Hash、List、Set、Sorted Set 等 | 仅 String              |
| 持久化     | 支持 RDB/AOF                           | 纯内存，不支持         |
| 排行榜     | Sorted Set 原生支持                    | 不支持，需应用层实现   |
| 本项目需求 | 缓存 + 热词排行（ZSET）                | 仅缓存，排行需自行实现 |

本项目需要搜索热词排行榜功能，Redis 的 Sorted Set 是最合适的方案，Memcached 无法满足。

**本项目 Redis 的明确边界**（来自 `K8s+Docker+Redis技术栈增加计划.md`）：

> Redis 在本项目中的首版职责仅限于**缓存**和**分析数据**，不扩展到会话共享、消息队列或分布式锁。

### 3. 怎么用

#### 3.1 Redis 部署

**Docker Compose**：

```yaml
redis:
  container_name: library-redis
  image: redis:7-alpine # Redis 7, Alpine Linux
  expose:
    - "6379" # internal only
```

**Kubernetes**：

```yaml
# k8s/redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: library-redis
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: redis
          image: library-system-redis:latest
          ports:
            - containerPort: 6379
```

```yaml
# k8s/redis-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: library-redis
spec:
  type: ClusterIP
  ports:
    - port: 6379
      targetPort: 6379
```

**连接配置**：

| 环境           | REDIS_URL                      | 说明                              |
| -------------- | ------------------------------ | --------------------------------- |
| Docker Compose | `redis://redis:6379/0`         | `redis` 是 Compose 服务名         |
| Kubernetes     | `redis://library-redis:6379/0` | `library-redis` 是 Service DNS 名 |
| 本地开发       | `redis://127.0.0.1:6379/0`     | 默认回退值                        |

#### 3.2 Python 客户端初始化

项目使用 **redis-py** 库（`requirements.txt` 中声明 `redis`），在 `backbone/main.py` 中初始化：

```python
from redis import Redis
from redis.exceptions import RedisError

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CACHE_TTL_RECOMMENDED = int(os.getenv("CACHE_TTL_RECOMMENDED", "300"))   # 300s
CACHE_TTL_SUGGESTIONS = int(os.getenv("CACHE_TTL_SUGGESTIONS", "180"))   # 180s

_redis_client = None   # lazy singleton

def get_redis_client():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        client = Redis.from_url(
            REDIS_URL,
            decode_responses=True,        # auto decode bytes to str
            socket_connect_timeout=1,     # connect timeout 1s
            socket_timeout=1,             # read/write timeout 1s
        )
        client.ping()                     # verify connection
        _redis_client = client
        return _redis_client
    except (RedisError, ValueError):
        return None                       # connection failed -> graceful degradation
```

**关键设计决策**：

- **懒加载**：第一次调用 `get_redis_client()` 时才建立连接，避免启动时因 Redis 不可用而阻塞
- **单例模式**：全局 `_redis_client` 只创建一次，后续复用
- **超时限制**：连接和读写均为 1 秒，确保 Redis 异常不会拖慢整个请求
- **decode_responses=True**：自动将 Redis 返回的 bytes 解码为 Python str，省去手动解码

#### 3.3 缓存读写封装

```python
def read_cache(key: str):
    # 读取缓存。命中返回反序列化数据，未命中/异常返回 None
    client = get_redis_client()
    if client is None:
        return None
    try:
        payload = client.get(key)
        if payload:
            CACHE_OPERATION_COUNT.labels(cache_name="redis", operation="hit").inc()
            return json.loads(payload)             # JSON 反序列化
        CACHE_OPERATION_COUNT.labels(cache_name="redis", operation="miss").inc()
        return None
    except (RedisError, TypeError, json.JSONDecodeError):
        CACHE_OPERATION_COUNT.labels(cache_name="redis", operation="error").inc()
        return None

def write_cache(key: str, value, ttl: int):
    # 写入缓存。使用 SETEX 设置 TTL
    client = get_redis_client()
    if client is None:
        return
    try:
        client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
        CACHE_OPERATION_COUNT.labels(cache_name="redis", operation="store").inc()
    except RedisError:
        CACHE_OPERATION_COUNT.labels(cache_name="redis", operation="error").inc()
```

- **序列化方式**：JSON（`json.dumps` / `json.loads`），`ensure_ascii=False` 保留中文字符
- **写入命令**：`SETEX key ttl value` —— 原子操作，设置值的同时指定过期时间
- **可观测性**：每次操作都记录 Prometheus Counter（hit/miss/store/error）

#### 3.4 缓存使用场景（3 个 API 端点）

**场景 A：推荐图书缓存**

```python
@app.get("/books/recommended")
def recommended_books():
    cache_key = "books:recommended"
    cached = read_cache(cache_key)              # 1. 查缓存
    if cached is not None:
        return cached                           # 2. 命中 -> 直接返回
    data = get_recommended_books()              # 3. 未命中 -> 计算数据
    write_cache(cache_key, data, CACHE_TTL_RECOMMENDED)  # 4. 写入缓存（TTL 300s）
    return data
```

**场景 B：搜索建议缓存**

```python
@app.get("/search/suggestions")
def search_suggestions(q: str = Query(default="")):
    normalized_query = q.strip().lower()
    cache_key = f"search:suggestions:{normalized_query or 'default'}"
    cached = read_cache(cache_key)
    if cached is not None:
        return cached
    suggestions = get_search_suggestions(q)
    write_cache(cache_key, suggestions, CACHE_TTL_SUGGESTIONS)  # TTL 180s
    return suggestions
```

**场景 C：搜索结果缓存**

```python
@app.get("/books/search")
def search_books_api(q, category, only_available, limit):
    cache_key = f"books:search:{q}:{category}:{only_available}:{limit}"
    cached = read_cache(cache_key)
    if cached is not None:
        publish_event("search.books", {...})    # 缓存命中也记录搜索事件
        return cached
    results = search_books(query=q, ...)
    write_cache(cache_key, results, CACHE_TTL_RECOMMENDED)
    publish_event("search.books", {...})        # 搜索事件 -> RabbitMQ
    return results
```

#### 3.5 搜索热词排行榜（Sorted Set）

**写入端**（`backbone/rabbitmq_worker.py`）：

用户搜索时，后端将搜索事件发布到 RabbitMQ，Worker 消费后写入 Redis Sorted Set：

```python
def handle_message(ch, method, properties, body):
    message = json.loads(body)
    event_type = message.get("event_type")
    payload = message.get("payload", {})
    redis_client = get_redis_client()

    if redis_client is not None:
        try:
            if event_type == "search.books":
                query = str(payload.get("query", "")).strip().lower()
                if query:
                    redis_client.zincrby("analytics:search_terms", 1, query)   # 原子递增分数
                    redis_client.expire("analytics:search_terms", 60*60*24*30)  # 30 天过期
            elif event_type == "auth.login_success":
                redis_client.incr("analytics:login_success_total")   # 登录成功计数器 +1
            elif event_type == "auth.login_failed":
                redis_client.incr("analytics:login_failed_total")    # 登录失败计数器 +1
        except RedisError:
            pass
```

**读取端**（`backbone/main.py`）：

```python
@app.get("/analytics/search-trends")
def search_trends(limit: int = Query(default=10)):
    client = get_redis_client()
    if client is None:
        return [{"term": s, "count": 0} for s in DEFAULT_SUGGESTIONS[:limit]]

    try:
        trends = client.zrevrange("analytics:search_terms", 0, limit-1, withscores=True)
        if trends:
            return [{"term": term, "count": int(score)} for term, score in trends]
    except RedisError:
        pass

    return [{"term": s, "count": 0} for s in DEFAULT_SUGGESTIONS[:limit]]
```

#### 3.6 Redis Key 设计一览

| Redis Key                                | 数据类型       | 读写位置              | TTL      | 用途             |
| ---------------------------------------- | -------------- | --------------------- | -------- | ---------------- |
| `books:recommended`                      | String（JSON） | main.py 读写          | 300s     | 推荐图书缓存     |
| `search:suggestions:{query}`             | String（JSON） | main.py 读写          | 180s     | 搜索建议缓存     |
| `books:search:{q}:{cat}:{avail}:{limit}` | String（JSON） | main.py 读写          | 300s     | 搜索结果缓存     |
| `analytics:search_terms`                 | Sorted Set     | worker 写、main.py 读 | 30 天    | 搜索热词排行榜   |
| `analytics:login_success_total`          | String（INCR） | worker 写             | 永不过期 | 累计登录成功次数 |
| `analytics:login_failed_total`           | String（INCR） | worker 写             | 永不过期 | 累计登录失败次数 |

**Key 命名约定**：使用冒号 `:` 分隔的分层结构——`业务域:功能:参数`（如 `books:recommended`、`search:suggestions:keyword`、`analytics:search_terms`）。

#### 3.7 优雅降级机制

本项目对 Redis 实现了**三层降级保障**，确保 Redis 不可用时系统功能完全正常：

| 层级                | 机制                             | 代码实现                                       |
| ------------------- | -------------------------------- | ---------------------------------------------- |
| **1. 连接失败降级** | `get_redis_client()` 返回 `None` | `except (RedisError, ValueError): return None` |
| **2. 操作异常降级** | 捕获 `RedisError`，跳过当前操作  | `except RedisError: pass`                      |
| **3. 超时保护**     | 连接和读写均为 1 秒              | `socket_connect_timeout=1, socket_timeout=1`   |

**降级效果**：

- **缓存端点**：缓存未命中 → 直接查询 PostgreSQL/Elasticsearch（稍慢但功能完整）
- **热词排行**：返回硬编码的 `DEFAULT_SUGGESTIONS` 默认建议列表
- **健康检查**：`/healthz` 报告 `"redis": "degraded"`，不影响整体 `"status": "ok"`

#### 3.8 健康检查与可观测性

**健康检查端点**（`GET /healthz`）：

```python
@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "redis": "up" if get_redis_client() is not None else "degraded",
        "elasticsearch": "up" if get_elasticsearch_client() is not None else "degraded",
        "rabbitmq": "up" if is_rabbitmq_available() else "degraded",
    }
```

**Prometheus 指标**：

```python
CACHE_OPERATION_COUNT = Counter(
    "library_cache_operations_total",
    "Cache operations in the backend",
    ["cache_name", "operation"],
)
# 标签取值：cache_name="redis", operation in {hit, miss, store, error}
```

| 指标                                                                   | 标签值           | 含义                  |
| ---------------------------------------------------------------------- | ---------------- | --------------------- |
| `library_cache_operations_total{cache_name="redis",operation="hit"}`   | 缓存命中次数     | 请求直接从 Redis 返回 |
| `library_cache_operations_total{cache_name="redis",operation="miss"}`  | 缓存未命中次数   | 需查询数据库/ES       |
| `library_cache_operations_total{cache_name="redis",operation="store"}` | 缓存写入次数     | 新数据写入 Redis      |
| `library_cache_operations_total{cache_name="redis",operation="error"}` | 缓存操作异常次数 | Redis 连接或操作失败  |

Prometheus 每 15 秒从 `backend:8000/metrics` 采集一次，可在 Grafana 中构建缓存命中率面板。

#### 3.9 数据流完整链路

以一次"搜索图书"请求为例，展示 Redis 在完整链路中的作用：

```
用户搜索 "计算机"
  |
  v
Nginx 反向代理 -> K8s Service 负载均衡 -> Backend Pod
  |
  +-- 1. 查询 Redis 缓存 (books:search:计算机:all:all:12)
  |     |-- 命中 -> 直接返回 + 发布搜索事件到 RabbitMQ
  |     +-- 未命中 -> 查询 Elasticsearch
  |                   |-- ES 可用 -> 全文检索返回结果
  |                   +-- ES 不可用 -> 本地 Python 过滤回退
  |                 -> 写入 Redis 缓存 (TTL 300s)
  |                 -> 发布搜索事件到 RabbitMQ
  |
  v
RabbitMQ Worker 消费搜索事件
  |
  +-- ZINCRBY analytics:search_terms 1 "计算机"  -> 搜索热词 +1
  +-- EXPIRE analytics:search_terms 2592000      -> 重置 30 天过期
  |
  v
用户查看搜索热词 (/analytics/search-trends)
  |
  +-- ZREVRANGE analytics:search_terms 0 9 WITHSCORES -> 返回 Top 10 热词
  +-- Redis 不可用 -> 返回 DEFAULT_SUGGESTIONS 默认列表
```

---

## 附录：三项技术协同架构总览

```
+--------------------------------------------------------------------------+
|                                                                          |
|   Docker 提供容器化  -->  K8s 提供编排调度  -->  Redis 提供缓存+排行      |
|                                                                          |
|   +---------+      +------------------+      +--------------------+     |
|   | Docker  |      |   Kubernetes     |      |      Redis         |     |
|   +---------+      +------------------+      +--------------------+     |
|   - 镜像构建        - Deployment 管理         - API 响应缓存              |
|   - 容器运行        - Service 负载均衡        - 搜索热词排行(ZSET)        |
|   - Compose 编排    - ConfigMap 配置          - 登录计数(INCR)           |
|   - Volume 持久化   - PVC 存储               - 优雅降级                  |
|                    - 健康探针自愈             - Prometheus 指标          |
|                    - 声明式部署               - TTL 自动过期             |
+--------------------------------------------------------------------------+

协同工作流：
  Docker 打包应用 --> K8s 部署多副本 --> Service 负载均衡请求
  --> Backend 查 Redis 缓存 --> 命中直接返回/未命中查 DB+ES
  --> RabbitMQ 异步事件 --> Worker 写 Redis 排行榜
  --> Prometheus 采集 Redis 缓存指标 --> /healthz 检测 Redis 状态
```
