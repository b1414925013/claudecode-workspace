# PostgreSQL 错误代码参考

## 1. 常见错误代码

### 连接错误
| 错误代码 | 说明 | 解决方法 |
|----------|------|----------|
| `28P01` | 密码认证失败 | 检查密码是否正确，或修改 pg_hba.conf 认证方式 |
| `FATAL: 28P01: password authentication failed for user "xxx"` | 用户名或密码错误 | 确认用户名密码，或使用正确的连接方式 |
| `28000` | 无效的认证机制 | 检查 pg_hba.conf 中的认证方法配置 |
| `08P01` | 协议版本不匹配 | 客户端和服务端版本不兼容，尝试升级客户端 |

### 连接拒绝
| 错误代码 | 说明 | 解决方法 |
|----------|------|----------|
| `ECONNREFUSED` | 连接被拒绝 | 检查 postgresql.conf 中的 listen_addresses 配置 |
| `08001` | 无法连接 | 确认 PostgreSQL 服务正在运行，端口正确 |
| `08006` | 连接超时 | 检查网络连通性，确认防火墙未阻止 |

---

## 2. 语法错误

| 错误代码 | 说明 | 解决方法 |
|----------|------|----------|
| `42601` | 语法错误 | 检查 SQL 语句语法，确保关键字正确 |
| `42000` | 语法错误或无效的 SQL 语句 | 确认 SQL 语句符合 PostgreSQL 语法 |
| `SF0001` | 函数不存在 | 检查函数名是否正确，是否安装了扩展 |

---

## 3. 约束冲突

### 主键/唯一约束
| 错误代码 | 说明 | 解决方法 |
|----------|------|----------|
| `23505` | 违反唯一约束 | 检查插入的数据是否与现有数据冲突 |
| `23503` | 违反外键约束 | 确认引用的父表记录存在 |
| `23502` | 违反非空约束 | 检查是否向 NOT NULL 列插入了 NULL 值 |

### 外键约束
```
ERROR: 23503: foreign key constraint "orders_user_id_fkey" is violated
```
解决方法：先插入父表记录，或更新外键值为有效值

### 检查约束
```
ERROR: 23514: new row for relation "orders" violates check constraint "orders_total_check"
```
解决方法：确保数据满足 CHECK 约束条件

---

## 4. 数据类型错误

| 错误代码 | 说明 | 解决方法 |
|----------|------|----------|
| `22P02` | 字符转数值失败 | 检查字符串是否为有效的数值格式 |
| `22007` | 日期/时间格式错误 | 使用正确的日期时间格式 |
| `22021` | 字符集转换失败 | 检查字符编码是否匹配 |
| `22018` | 类型转换失败 | 使用显式类型转换（:: 或 CAST） |

### 示例
```sql
-- 错误
SELECT 'abc'::integer;

-- 正确（使用函数验证）
SELECT NULLIF('abc', 'abc')::integer;  -- 返回 NULL 而非报错
```

---

## 5. 权限错误

| 错误代码 | 说明 | 解决方法 |
|----------|------|----------|
| `42501` | 权限被拒绝 | 使用 GRANT 授予相应权限 |
| `42000` | 权限不足 | 以超级用户或拥有者身份执行 |

### 常见权限问题
```sql
-- 表权限不足
ERROR: permission denied for table "users"

-- 授予权限
GRANT SELECT, INSERT ON users TO username;

-- 序列权限不足
ERROR: permission denied for sequence "users_id_seq"
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO username;
```

---

## 6. 事务错误

### 死锁
```
ERROR: 40P01: deadlock detected
```
解决方法：重试事务，或调整事务顺序

### 序列化失败
```
ERROR: 40001: could not serialize access due to concurrent update
```
解决方法：重试事务，利用 PostgreSQL 的重试机制

### 事务回滚
```
ERROR: 25P02: current transaction is aborted
```
解决方法：新开事务（当前事务已被自动回滚）

---

## 7. 表/索引错误

### 表不存在
| 错误代码 | 说明 | 解决方法 |
|----------|------|----------|
| `42P01` | 关系不存在 | 检查表名是否正确，确认 schema |
| `42703` | 列不存在 | 检查列名是否正确 |

### 索引问题
```sql
-- 索引不存在
ERROR: 42704: index "idx_name" does not exist

-- 索引已存在
ERROR: 42710: duplicate key value in index "idx_name"
```

### 触发器错误
```
ERROR: 42704: trigger "trigger_name" does not exist
```

---

## 8. 数据库操作错误

### 无法删除
```sql
-- 无法删除正在使用的数据库
ERROR: 55006: database "mydb" is being accessed by other users

-- 解决方法：先断开所有连接
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'mydb';
```

### 无法删除表
```
ERROR: 2BP01: cannot drop table "orders" because other objects depend on it
```
解决方法：使用 CASCADE 级联删除，或先删除依赖对象

---

## 9. 存储/配置错误

### 磁盘空间
```
ERROR: 53100: could not extend file "base/12345/56789": No space left on device
```
解决方法：清理磁盘空间，或扩展存储

### 事务日志
```
ERROR: 53100: could not write to file "pg_wal/xxx": No space left on device
```

### 内存不足
```
ERROR: 53200: out of memory
```
解决方法：调整 work_mem 或 shared_buffers 配置

---

## 10. 并发控制错误

### 锁等待超时
```
ERROR: 55P03: lock not available
```
解决方法：增加 max_locks_per_transaction，或优化事务

### 混合事务
```
ERROR: 40P01: deadlock detected
```

---

## 11. 复制错误

### 流复制
```
ERROR: 57P01: the database system is shutting down
```

### 同步复制
```
ERROR: 57P03: could not receive data from WAL stream
```

---

## 12. SQLSTATE 快速查询

```sql
-- 查询最近错误
SELECT * FROM pg_log ORDER BY log_time DESC LIMIT 10;

-- 通过 SQLSTATE 查找错误类型
SELECT sqlstate, unnest(string_to_array(message, E'\n')) as msg
FROM pg_log
WHERE sqlstate IN ('23505', '23503', '23502');
```

### 常用 SQLSTATE 分类
| 前缀 | 类别 |
|------|------|
| 00 | 成功完成 |
| 08 | 连接异常 |
| 22 | 数据异常 |
| 23 | 约束冲突 |
| 25 | 事务问题 |
| 40 | 事务回滚 |
| 42 | 语法/对象问题 |
| 53 | 资源不足 |
| 55 | 锁问题 |
| 57 | 复制/控制流 |

---

## 13. 日志查看

```bash
# 默认日志位置
# Linux: /var/log/postgresql/
# Windows: %PROGRAMDATA%\PostgreSQL\logs\

# 查看最近错误
SELECT pid, usename, datname, state, query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND query_start < now() - interval '10 minutes';
```

---

## 14. 错误处理函数

```sql
-- 获取详细错误信息
SELECT * FROM pg_read_file('postgresql.conf');

-- 检查连接状态
SELECT pg_isready();

-- 测试连接
SELECT current_user, current_database();

-- 查看活动连接
SELECT pid, usename, application_name, state
FROM pg_stat_activity
WHERE datname = 'mydb';
```
