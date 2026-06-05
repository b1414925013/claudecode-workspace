# 性能优化指南

## 1. EXPLAIN 分析

### 基本使用
```sql
EXPLAIN SELECT * FROM users WHERE id = 1;
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 1;
```

### 输出格式
```sql
EXPLAIN (FORMAT JSON) SELECT * FROM users WHERE id = 1;
EXPLAIN (FORMAT YAML) SELECT * FROM users WHERE id = 1;
EXPLAIN (COSTS OFF) SELECT * FROM users WHERE id = 1;
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE id = 1;
```

### 解读执行计划
```
Seq Scan on users  (cost=0.00..35.50 rows=10 width=97)
  Filter: ((id)::integer = 1)
  Rows Removed by Filter: 990
```

- `Seq Scan`: 全表扫描
- `cost=0.00..35.50`: 启动成本..总成本
- `rows=10`: 估计返回行数
- `Buffers`: 缓存命中

---

## 2. 索引优化

### 创建合适的索引
```sql
-- 单列索引
CREATE INDEX idx_users_email ON users(email);

-- 多列索引（顺序重要）
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- 唯一索引
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- 表达式索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- 部分索引
CREATE INDEX idx_users_active ON users(email) WHERE status = 'active';

-- 覆盖索引（避免回表）
CREATE INDEX idx_users_email_name ON users(email) INCLUDE (name, age);

-- GIN 索引（JSONB、数组、全文搜索）
CREATE INDEX idx_data ON table USING GIN (data jsonb_path_ops);
```

### 索引类型选择
| 类型 | 适用场景 |
|------|----------|
| B-tree | 默认，适用于等值和范围查询 |
| Hash | 仅适用于等值查询 |
| GiST | 几何、全文搜索、范围 |
| GIN | JSONB、数组、全文搜索 |
| BRIN | 大表顺序扫描（如日志表） |

---

## 3. 查询优化技巧

### 避免全表扫描
```sql
-- 不用
SELECT * FROM users WHERE LOWER(email) = 'test';

-- 用（创建表达式索引后）
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
SELECT * FROM users WHERE LOWER(email) = 'test';
```

### 使用 LIMIT 限制
```sql
-- 添加 LIMIT
SELECT * FROM big_table WHERE status = 'active' LIMIT 100;
```

### 批量操作
```sql
-- 批量插入（使用 COPY 最快）
COPY big_table FROM '/path/to/data.csv' WITH (FORMAT CSV);

-- 批量更新
UPDATE orders SET status = 'shipped' WHERE id IN (SELECT id FROM temp_ids);
```

### 避免 N+1 查询
```sql
-- 不用（多次查询）
SELECT * FROM orders;
-- 然后循环查询每个订单的用户

-- 用（JOIN 一次查询）
SELECT o.*, u.name, u.email
FROM orders o
JOIN users u ON o.user_id = u.id;
```

---

## 4. VACUUM 和 ANALYZE

### VACUUM 清理
```sql
-- 清理表
VACUUM users;

-- 详细输出
VACUUM VERBOSE users;

-- 清理并分析
VACUUM ANALYZE users;

-- 冻结元组
VACUUM FREEZE users;

-- 禁用垃圾回收优化
VACUUM FULL users;  -- 需要排他锁，慎用
```

### ANALYZE 更新统计
```sql
ANALYZE users;
ANALYZE VERBOSE users;
```

### 自动清理配置
```sql
-- postgresql.conf 配置
autovacuum = on                    -- 自动 vacuum
autovacuum_vacuum_threshold = 50    -- 触发阈值
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.2  -- 表大小比例
```

---

## 5. 配置参数调优

### 内存参数
```sql
-- 共享缓冲区（建议为系统内存的 25%）
ALTER SYSTEM SET shared_buffers = '4GB';

-- 工作内存（建议为共享缓冲区的 1/16 到 1/4）
ALTER SYSTEM SET work_mem = '256MB';

-- 维护内存（建议 1-2GB）
ALTER SYSTEM SET maintenance_work_mem = '2GB';

-- 临时内存
ALTER SYSTEM SET temp_buffers = '64MB';

-- 生效配置
SELECT pg_reload_conf();
```

### 连接参数
```sql
-- 最大连接数
ALTER SYSTEM SET max_connections = '200';

-- 准备语句
ALTER SYSTEM SET max_prepared_connections = '50';
```

### 写入性能
```sql
-- WAL 写入优化
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET wal_writer_delay = '200ms';

-- 同步策略
ALTER SYSTEM SET synchronous_commit = 'off';  -- 异步提交，提高性能
ALTER SYSTEM SET fsync = 'off';  -- 禁用同步写入（危险！）
ALTER SYSTEM SET full_page_writes = 'off';  -- 禁用全页写入（危险！）
```

### 查询规划
```sql
-- 随机页面访问成本
ALTER SYSTEM SET random_page_cost = 1.1;  -- SSD 用较低值

-- 序列扫描成本
ALTER SYSTEM SET seq_page_cost = 1.0;

-- 并行查询
ALTER SYSTEM SET max_worker_processes = 8;
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
```

---

## 6. 慢查询诊断

### 启用统计收集
```sql
-- 需要在 postgresql.conf 中启用
-- shared_preload_libraries = 'pg_stat_statements'
-- pg_stat_statements.track = all

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

### 查看慢查询
```sql
-- 最慢查询
SELECT query, calls, total_exec_time, mean_exec_time, rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 最常调用
SELECT query, calls, total_exec_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;

-- IO 最慢
SELECT query, calls, total_exec_time, shared_blks_hit, shared_blks_read
FROM pg_stat_statements
ORDER BY shared_blks_read DESC
LIMIT 10;
```

### 查看等待事件
```sql
SELECT wait_event_type, wait_event, COUNT(*)
FROM pg_stat_activity
WHERE state != 'idle'
GROUP BY wait_event_type, wait_event
ORDER BY COUNT(*) DESC;
```

---

## 7. 连接池和压力测试

### pgBouncer 配置
```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction
max_client_conn = 200
default_pool_size = 20
```

### 压力测试
```bash
# 使用 pgbench
pgbench -h localhost -U user -d mydb -c 10 -j 4 -T 60

# 自定义测试
pgbench -h localhost -U user -d mydb -c 10 -j 4 -T 60 -f custom.sql
```

---

## 8. 分区表优化

### 分区策略
```sql
-- 按范围分区
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE NOT NULL,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (sale_date);

-- 按列表分区
CREATE TABLE customers (
    id SERIAL,
    region VARCHAR(50) NOT NULL
) PARTITION BY LIST (region);

CREATE TABLE customers_north PARTITION OF customers
    FOR VALUES IN ('north');
```

### 分区裁剪
```sql
-- 自动裁剪（PostgreSQL 11+）
SET enable_partition_pruning = on;

-- 检查分区裁剪
EXPLAIN SELECT * FROM sales WHERE sale_date = '2024-06-01';
```

---

## 9. 并行查询

### 启用并行
```sql
-- postgresql.conf
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
parallel_leader_participation = on

-- 查询级别
SET max_parallel_workers_per_gather = 4;
```

### 查看并行计划
```sql
EXPLAIN (ANALYZE) SELECT SUM(amount) FROM sales GROUP BY region;
```

---

## 10. 监控视图

### 实时监控
```sql
-- 当前连接
SELECT pid, usename, application_name, state, query_start
FROM pg_stat_activity
WHERE state != 'idle';

-- 表使用统计
SELECT relname, seq_scan, idx_scan, n_tup_ins, n_tup_upd, n_tup_del, n_live_tup, n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- 索引使用统计
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0;  -- 未使用的索引

-- 缓存命中率
SELECT sum(heap_blks_read) as heap_read,
       sum(heap_blks_hit)  as heap_hit,
       sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```