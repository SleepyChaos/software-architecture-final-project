# Prometheus 查询说明

这个项目里的 Prometheus 主要监控后端 FastAPI 和 Redis 缓存行为。打开地址：`http://localhost:9090`。

## 1. 可以查询哪些指标

### 1.1 HTTP 请求总量

- 指标名：`library_http_requests_total`
- 作用：统计后端收到的请求总数
- 标签：`method`、`endpoint`、`status`

常用示例：

```promql
library_http_requests_total
sum by (endpoint) (library_http_requests_total)
sum by (status) (library_http_requests_total)
rate(library_http_requests_total[5m])
```

### 1.2 接口耗时

- 指标名：`library_http_request_duration_seconds`
- 作用：统计接口请求耗时
- 类型：Histogram
- 标签：`method`、`endpoint`

常用示例：

```promql
library_http_request_duration_seconds
rate(library_http_request_duration_seconds_sum[5m])
rate(library_http_request_duration_seconds_count[5m])
histogram_quantile(0.95, sum by (le, endpoint) (rate(library_http_request_duration_seconds_bucket[5m])))
```

### 1.3 Redis 缓存操作

- 指标名：`library_cache_operations_total`
- 作用：统计缓存命中、未命中、写入和错误
- 标签：`cache_name`、`operation`

常用示例：

```promql
library_cache_operations_total
sum by (operation) (library_cache_operations_total)
rate(library_cache_operations_total[5m])
```

## 2. 在页面里怎么查

1. 打开 `http://localhost:9090`
2. 在上方 Expression 输入框里输入查询语句
3. 点击右侧 Execute
4. 切换 Table 或 Graph 查看结果

## 3. 建议先看的内容

- `library_http_requests_total`：看请求有没有进来
- `sum by (endpoint) (library_http_requests_total)`：看哪个接口最常被访问
- `sum by (operation) (library_cache_operations_total)`：看 Redis 命中和未命中情况
- `histogram_quantile(0.95, sum by (le, endpoint) (rate(library_http_request_duration_seconds_bucket[5m])))`：看接口 P95 延迟

## 4. 适合答辩展示的说法

- Prometheus 监控后端请求量和响应耗时
- Redis 指标可以展示缓存是否生效
- `/metrics` 由后端自动暴露，Prometheus 定时抓取
