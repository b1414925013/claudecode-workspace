# SQL 命令参考

## 1. 数据库操作

### 创建数据库
```sql
CREATE DATABASE db_name
    WITH [ENCODING = 'UTF8']
         [OWNER = owner_name]
         [TEMPLATE = template]
         [CONNECTION LIMIT = n];
```

### 修改数据库
```sql
ALTER DATABASE db_name RENAME TO new_name;
ALTER DATABASE db_name SET parameter = value;
```

### 删除数据库
```sql
DROP DATABASE [IF EXISTS] db_name;
```

### 查看数据库
```sql
\l                              -- 列出所有数据库
\l+                             -- 列出所有数据库（详细信息）
SELECT datname FROM pg_database;
```

---

## 2. Schema 操作

### 创建 Schema
```sql
CREATE SCHEMA schema_name;
CREATE SCHEMA schema_name AUTHORIZATION user_name;
```

### 修改/删除 Schema
```sql
ALTER SCHEMA schema_name RENAME TO new_name;
DROP SCHEMA [IF EXISTS] schema_name [CASCADE];
```

### 查看 Schema
```sql
SELECT schema_name FROM information_schema.schemata;
\dn                              -- 列出所有 schema
```

---

## 3. 表操作

### 创建表
```sql
CREATE TABLE table_name (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    age INTEGER DEFAULT 18,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status BOOLEAN DEFAULT true,
    data JSONB
);

-- 带约束
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total DECIMAL(10,2) CHECK (total >= 0),
    status VARCHAR(20) DEFAULT 'pending',
    UNIQUE (user_id, order_date)
);
```

### 修改表结构
```sql
-- 添加列
ALTER TABLE table_name ADD COLUMN col_name data_type;
ALTER TABLE table_name ADD COLUMN col_name data_type DEFAULT default_value;

-- 修改列
ALTER TABLE table_name ALTER COLUMN col_name TYPE new_type;
ALTER TABLE table_name ALTER COLUMN col_name SET DEFAULT value;
ALTER TABLE table_name ALTER COLUMN col_name DROP DEFAULT;

-- 重命名列/表
ALTER TABLE table_name RENAME COLUMN col_name TO new_name;
ALTER TABLE table_name RENAME TO new_table_name;

-- 删除列
ALTER TABLE table_name DROP COLUMN col_name;
ALTER TABLE table_name DROP COLUMN IF EXISTS col_name;
```

### 删除表
```sql
DROP TABLE [IF EXISTS] table_name [CASCADE];
```

### 查看表
```sql
\d                              -- 列出所有表
\d table_name                    -- 查看表结构
\d+ table_name                  -- 查看表详细信息
```

---

## 4. 索引操作

### 创建索引
```sql
-- 单列索引
CREATE INDEX idx_name ON table_name (column);

-- 多列索引
CREATE INDEX idx_name ON table_name (col1, col2);

-- 唯一索引
CREATE UNIQUE INDEX idx_name ON table_name (column);

-- 表达式索引
CREATE INDEX idx_name ON table_name (LOWER(email));

-- 部分索引
CREATE INDEX idx_name ON table_name (column) WHERE column IS NOT NULL;

-- GIN 索引（用于 JSONB、数组、全文搜索）
CREATE INDEX idx_name ON table_name USING GIN (data);
```

### 修改/删除索引
```sql
-- 重命名
ALTER INDEX idx_name RENAME TO new_idx_name;

-- 删除
DROP INDEX [IF EXISTS] idx_name;
```

### 查看索引
```sql
\di                              -- 列出所有索引
SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public';
```

---

## 5. 数据操作 (CRUD)

### INSERT 插入
```sql
-- 单行插入
INSERT INTO table_name (col1, col2) VALUES (value1, value2);
INSERT INTO table_name VALUES (value1, value2);

-- 多行插入
INSERT INTO table_name (col1, col2) VALUES
    (value1, value2),
    (value3, value4);

-- 从查询结果插入
INSERT INTO table_name (col1, col2)
SELECT col1, col2 FROM other_table WHERE condition;

-- Upsert (ON CONFLICT)
INSERT INTO table_name (id, name) VALUES (1, 'John')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
```

### SELECT 查询
```sql
-- 基本查询
SELECT col1, col2 FROM table_name;

-- 别名
SELECT col1 AS alias_name FROM table_name;

-- 去重
SELECT DISTINCT column FROM table_name;

-- 条件查询
SELECT * FROM table_name WHERE condition;

-- 排序
SELECT * FROM table_name ORDER BY col1 ASC, col2 DESC;

-- 分页
SELECT * FROM table_name LIMIT 10 OFFSET 20;

-- 聚合
SELECT COUNT(*), SUM(col), AVG(col), MIN(col), MAX(col) FROM table_name;

-- 分组
SELECT col1, COUNT(*) FROM table_name GROUP BY col1 HAVING COUNT(*) > 1;
```

### UPDATE 更新
```sql
UPDATE table_name SET col1 = value1, col2 = value2 WHERE condition;

-- 使用子查询
UPDATE table_name SET col1 = (SELECT col FROM other_table WHERE id = table_name.id);
```

### DELETE 删除
```sql
DELETE FROM table_name WHERE condition;

-- 删除返回
DELETE FROM table_name WHERE condition RETURNING *;
```

---

## 6. 连接查询 (JOIN)

### 各种 JOIN
```sql
-- INNER JOIN
SELECT * FROM a INNER JOIN b ON a.id = b.a_id;

-- LEFT JOIN
SELECT * FROM a LEFT JOIN b ON a.id = b.a_id;

-- RIGHT JOIN
SELECT * FROM a RIGHT JOIN b ON a.id = b.a_id;

-- FULL OUTER JOIN
SELECT * FROM a FULL OUTER JOIN b ON a.id = b.a_id;

-- CROSS JOIN
SELECT * FROM a CROSS JOIN b;

-- 多表连接
SELECT * FROM a
    JOIN b ON a.id = b.a_id
    JOIN c ON b.id = c.b_id;
```

### 子查询
```sql
-- IN
SELECT * FROM table WHERE id IN (SELECT id FROM other_table);

-- EXISTS
SELECT * FROM table WHERE EXISTS (SELECT 1 FROM other_table WHERE condition);

-- 标量子查询
SELECT (SELECT COUNT(*) FROM table) AS total_count;
```

---

## 7. 视图

### 创建视图
```sql
CREATE VIEW view_name AS
SELECT col1, col2 FROM table_name WHERE condition;

-- 可更新视图
CREATE VIEW view_name AS SELECT * FROM table_name;
```

### 修改/删除视图
```sql
CREATE OR REPLACE VIEW view_name AS new_query;
DROP VIEW [IF EXISTS] view_name;
```

---

## 8. 物化视图

```sql
-- 创建
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT date_trunc('month', sale_date) AS month, SUM(amount) AS total
FROM sales GROUP BY month;

-- 刷新
REFRESH MATERIALIZED VIEW monthly_sales;
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales;  -- 并发刷新

-- 创建唯一物化视图索引（支持并发刷新）
CREATE UNIQUE INDEX ON monthly_sales (month);
```

---

## 9. 存储过程与函数

### 创建函数
```sql
-- 返回表
CREATE FUNCTION get_user(id INTEGER)
RETURNS TABLE(name VARCHAR, email VARCHAR) AS $$
BEGIN
    RETURN QUERY SELECT username, email FROM users WHERE users.id = get_user.id;
END;
$$ LANGUAGE plpgsql;

-- 返回单值
CREATE FUNCTION add_numbers(a INTEGER, b INTEGER)
RETURNS INTEGER AS $$
BEGIN
    RETURN a + b;
END;
$$ LANGUAGE plpgsql;

-- 过程
CREATE PROCEDURE insert_user(name VARCHAR, email VARCHAR) AS $$
BEGIN
    INSERT INTO users (name, email) VALUES (name, email);
END;
$$ LANGUAGE plpgsql;
```

### 调用函数/过程
```sql
SELECT get_user(1);
CALL insert_user('John', 'john@example.com');
```

---

## 10. 触发器

### 创建触发器
```sql
-- 创建触发器函数
CREATE FUNCTION trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_name
    BEFORE INSERT OR UPDATE ON table_name
    FOR EACH ROW EXECUTE FUNCTION trigger_function();

-- 条件触发器
CREATE TRIGGER trigger_name
    AFTER INSERT ON table_name
    REFERENCING NEW TABLE AS NEW_T
    FOR EACH STATEMENT EXECUTE FUNCTION procedure_name();
```

---

## 11. 事务控制

### 事务语法
```sql
BEGIN;
-- SQL 语句
COMMIT;                          -- 提交

BEGIN;
-- SQL 语句
ROLLBACK;                        -- 回滚

-- 保存点
BEGIN;
SAVEPOINT sp1;
ROLLBACK TO SAVEPOINT sp1;
COMMIT;
```

### 隔离级别
```sql
SET TRANSACTION ISOLATION LEVEL {
    READ COMMITTED
    | READ UNCOMMITTED
    | REPEATABLE READ
    | SERIALIZABLE
};
```

---

## 12. 序列 (Sequence)

### 创建序列
```sql
CREATE SEQUENCE seq_name
    START WITH 1
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 10000
    CACHE 1;

-- 使用序列
SELECT NEXTVAL('seq_name');
SELECT CURRVAL('seq_name');
SELECT LASTVAL();
```

### 绑定到列
```sql
CREATE TABLE table_name (
    id SERIAL PRIMARY KEY,        -- 自动创建序列
    ...
);

-- 或显式绑定
CREATE TABLE table_name (
    id BIGINT DEFAULT NEXTVAL('seq_name') PRIMARY KEY
);
```

---

## 13. 约束

### 约束类型
```sql
-- 主键
PRIMARY KEY (col1, col2)

-- 唯一
UNIQUE (col1, col2)

-- 非空
NOT NULL

-- 检查
CHECK (col > 0 AND col < 100)

-- 外键
FOREIGN KEY (col) REFERENCES other_table(col)
    ON DELETE CASCADE
    ON UPDATE SET NULL

-- 排除
EXCLUDE USING gist (
    col WITH =
) WHERE (col IS NOT NULL);
```

### 约束管理
```sql
-- 添加约束
ALTER TABLE table_name ADD CONSTRAINT constraint_name PRIMARY KEY (id);

-- 删除约束
ALTER TABLE table_name DROP CONSTRAINT constraint_name;
```

---

## 14. 分区表 (Partitioning)

### 创建分区表
```sql
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE NOT NULL,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (sale_date);

-- 创建月度分区
CREATE TABLE sales_2024_01 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE sales_2024_02 PARTITION OF sales
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 继承方式分区（传统方式）
```sql
CREATE TABLE measurement_y2024m01 (
    CHECK (logdate >= DATE '2024-01-01' AND logdate < DATE '2024-02-01')
) INHERITS (measurement);

-- 创建触发器自动路由
CREATE OR REPLACE FUNCTION measurement_insert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.logdate >= DATE '2024-01-01' AND NEW.logdate < DATE '2024-02-01') THEN
        INSERT INTO measurement_y2024m01 VALUES (NEW.*);
    ELSIF (...) THEN
        INSERT INTO measurement_y2024m02 VALUES (NEW.*);
    ELSE
        RAISE EXCEPTION 'Date out of range';
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

---

## 15. MERGE 语句

MERGE 可以同时执行 INSERT、UPDATE、DELETE 操作。

```sql
MERGE INTO target_table AS t
USING source_table AS s
ON t.id = s.id
WHEN MATCHED AND t.amount != s.amount THEN
    UPDATE SET amount = s.amount, updated_at = NOW()
WHEN MATCHED AND s.deleted = true THEN
    DELETE
WHEN NOT MATCHED THEN
    INSERT (id, name, amount, created_at)
    VALUES (s.id, s.name, s.amount, NOW());
```

### MERGE vs ON CONFLICT

| 特性 | MERGE | ON CONFLICT |
|------|-------|------------|
| SQL 标准 | 是 | 否（PostgreSQL 扩展） |
| UPDATE + DELETE | 支持 | 不支持 |
| 多表数据源 | 支持 | 不支持 |

---

## 16. 权限管理

### 授权
```sql
-- 授予权限
GRANT SELECT, INSERT ON table_name TO user_name;
GRANT ALL PRIVILEGES ON table_name TO user_name;
GRANT ALL PRIVILEGES ON DATABASE db_name TO user_name;

-- 授予角色
GRANT role_name TO user_name;
```

### 撤销权限
```sql
REVOKE SELECT, INSERT ON table_name FROM user_name;
REVOKE ALL PRIVILEGES ON table_name FROM user_name;
REVOKE role_name FROM user_name;
```

---

## 17. 导入导出

### COPY 导入导出
```sql
-- 导出到 CSV
COPY table_name TO '/path/to/file.csv' WITH (FORMAT CSV, HEADER, DELIMITER ',');

-- 从 CSV 导入
COPY table_name FROM '/path/to/file.csv' WITH (FORMAT CSV, HEADER, DELIMITER ',');

-- 导出查询结果
COPY (SELECT * FROM table_name WHERE condition) TO '/path/to/file.csv';

-- 二进制格式
COPY table_name TO '/path/to/file.dump' WITH (FORMAT BINARY);
```

### pg_dump 备份
```bash
# 备份单个数据库
pg_dump -U username -h localhost -d dbname -F c -b -v -f backup.dump

# 备份所有数据库
pg_dumpall -U username -h localhost -f all_databases.sql

# 仅备份表结构
pg_dump -U username -s -f schema.sql dbname
```

### pg_restore 恢复
```bash
pg_restore -U username -h localhost -d dbname -v backup.dump
```