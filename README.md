# 图书管理系统

当前项目已完成以下技术栈增强：

- 部署主线：Docker + Kubernetes
- 中间件增强：Redis
- 原有业务基础：Vue 3 + TypeScript + Vite + FastAPI + SQLite

## 当前架构

项目目前由三个核心运行单元组成：

- `frontend`：前端静态资源，由 Nginx 托管
- `backend`：FastAPI 后端服务，提供登录、推荐图书、搜索建议、健康检查接口
- `redis`：缓存组件，用于首页推荐和搜索建议缓存

其中：

- 登录链路已切换为本地可配置后端接口
- 首页推荐与搜索建议优先走后端接口，并由 Redis 做缓存
- 借阅、续借、预约等大部分业务仍保留前端本地模拟逻辑

## 测试账号

- 读者证登录：`001 / 123456`
- 人脸模拟登录：`face-user / face`

## 环境变量

前端：

- 开发环境使用 `.env.development`
- 生产构建使用 `.env.production`
- 关键变量：`VITE_API_BASE_URL`

后端：

- `REDIS_URL`
- `CACHE_TTL_RECOMMENDED`
- `CACHE_TTL_SUGGESTIONS`

## 原生运行

### 1. 启动后端

```bash
cd backbone
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动 PC 端前端

```bash
npm install
npm run dev
```

### 3. 启动移动端前端

```bash
npm install
npm run dev:mobile
```

默认情况下：

- 前端通过 `VITE_API_BASE_URL=http://127.0.0.1:8000` 访问本地后端
- 若本地未启动 Redis，推荐和搜索建议接口会自动降级，不影响页面基本使用

## Docker Compose 运行

### 1. 启动服务

由于当前目录名会影响默认项目名解析，建议显式指定项目名：

```bash
docker compose -p library-system up --build
```

### 2. 访问入口

- PC / 统一入口：[http://localhost:8080](http://localhost:8080)
- 移动端入口：[http://localhost:8080/mobile.html](http://localhost:8080/mobile.html)

Docker Compose 启动后：

- 前端走 Nginx 静态托管
- `/api` 会被代理到 FastAPI
- 后端通过环境变量连接 Redis
- SQLite 数据保存到命名卷 `library-system_sqlite_data`

## Kubernetes 本地部署

### 1. 构建镜像

```bash
docker build -t library-system-frontend:latest .
docker build -t library-system-backend:latest -f backbone/Dockerfile .
docker build -t library-system-redis:latest -f redis.Dockerfile .
```

如果你使用的是隔离镜像环境的本地集群，例如 `minikube`、`kind`、`k3d`，还需要将镜像加载到集群中。

以 `kind` 为例：

```bash
kind load docker-image library-system-frontend:latest --name library-system
kind load docker-image library-system-backend:latest --name library-system
kind load docker-image library-system-redis:latest --name library-system
```

### 2. 应用清单

```bash
kubectl apply -f k8s/
```

### 3. 本地访问

```bash
kubectl port-forward svc/library-frontend 8080:80
```

如果本机 `8080` 端口已经被 Docker Compose 或其他服务占用，可以改成：

```bash
kubectl port-forward svc/library-frontend 8081:80
```

访问地址：

- PC / 统一入口：[http://localhost:8080](http://localhost:8080)
- 移动端入口：[http://localhost:8080/mobile.html](http://localhost:8080/mobile.html)

K8s 清单包含：

- `frontend-deployment.yaml`
- `frontend-service.yaml`
- `backend-deployment.yaml`
- `backend-service.yaml`
- `redis-deployment.yaml`
- `redis-service.yaml`
- `backend-configmap.yaml`
- `backend-pvc.yaml`

## Redis 功能说明

Redis 在本项目中的首版职责仅限于缓存：

- `GET /books/recommended`
  - 为首页推荐图书提供缓存
- `GET /search/suggestions?q=关键词`
  - 为搜索建议提供缓存

缓存策略：

- 推荐图书：`CACHE_TTL_RECOMMENDED`
- 搜索建议：`CACHE_TTL_SUGGESTIONS`

降级策略：

- 如果 Redis 可用，优先读取缓存
- 如果 Redis 不可用，后端自动回退到本地 mock 数据计算结果

## 当前接口

后端当前对外提供：

- `POST /login`
- `GET /books/recommended`
- `GET /search/suggestions?q=关键词`
- `GET /healthz`

## 当前限制

当前方案仍有明确边界，这些内容在实验报告中建议如实说明：

- 后端数据库仍为 SQLite，因此 Kubernetes 部署阶段仍采用单副本后端
- Redis 目前只承担缓存职责，不做会话共享、分布式锁或消息队列
- 图书详情、借阅、续借、预约等大部分业务仍未完整后移到后端
- K8s 当前主要用于容器编排展示和部署骨架搭建，而非生产级高可用部署

## 后续扩展方向

后续如果继续扩展，可以优先考虑：

1. 将 SQLite 升级为支持多实例共享的数据库
2. 将借阅、预约、续借等业务接口后移到 FastAPI
3. 为前端增加更多后端真实数据来源
4. 在容器基础上继续增加监控或搜索型中间件
