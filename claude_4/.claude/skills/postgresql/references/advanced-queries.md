# 高级查询

## 1. 窗口函数 (Window Functions)

窗口函数在不做分组的情况下，对一组行进行计算并返回结果。

### 窗口函数语法
```sql
SELECT col1,
    aggregate_function(col2) OVER (PARTITION BY col3 ORDER BY col4) AS result,
    rank() OVER (ORDER BY col5 DESC) AS rank_val,
    row_number() OVER (PARTITION BY col1 ORDER BY col2) AS row_num
FROM table_name;
```

### 常用窗口函数

| 函数 | 说明 |
|------|------|
| `ROW_NUMBER()` | 行号（1, 2, 3...） |
| `RANK()` | 排名（有间隙，如 1, 2, 2, 4） |
| `DENSE_RANK()` | 排名（无间隙，如 1, 2, 2, 3） |
| `PERCENT_RANK()` | 百分比排名 |
| `NTILE(n)` | 将数据分成 n 组 |
| `LAG(col, n)` | 前 n 行值 |
| `LEAD(col, n)` | 后 n 行值 |
| `FIRST_VALUE(col)` | 组内第一个值 |
| `LAST_VALUE(col)` | 组内最后一个值 |
| `NTH_VALUE(col, n)` | 组内第 n 个值 |

### 示例
```sql
-- 按部门工资排名
SELECT name, department, salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank,
    SUM(salary) OVER (PARTITION BY department) AS dept_total,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg
FROM employees;

-- 前后行访问
SELECT id, created_at,
    LAG(created_at, 1) OVER (ORDER BY created_at) AS prev_time,
    LEAD(created_at, 1) OVER (ORDER BY created_at) AS next_time
FROM events;

-- 累计计算
SELECT date, value,
    SUM(value) OVER (ORDER BY date) AS cumulative,
    AVG(value) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg
FROM daily_sales;
```

### 窗口 Frame
```sql
-- 默认 frame (RANGE UNBOUNDED PRECEDING)
SELECT id,
    SUM(val) OVER (ORDER BY id ROWS UNBOUNDED PRECEDING) AS cumulative
FROM t;

-- 指定 frame 范围
SELECT id,
    AVG(val) OVER (ORDER BY id ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING) AS moving_avg
FROM t;

-- 使用 RANGE
SELECT id,
    SUM(val) OVER (ORDER BY id RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative
FROM t;
```

---

## 2. CTE (Common Table Expression)

CTE（公用表表达式）是临时命名的结果集，可在查询中引用。

### 非递归 CTE
```sql
WITH temp AS (
    SELECT id, name FROM users WHERE status = 'active'
),
stats AS (
    SELECT COUNT(*) as cnt FROM temp
)
SELECT * FROM temp, stats WHERE temp.id > stats.cnt / 2;
```

### 递归 CTE（树形结构）
```sql
-- 递归查询组织架构
WITH RECURSIVE org_tree AS (
    SELECT id, name, manager_id, 1 AS level
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, ot.level + 1
    FROM employees e
    JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT * FROM org_tree ORDER BY level;

-- 路径追踪
WITH RECURSIVE path AS (
    SELECT id, name, ARRAY[name] AS path FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, p.path || e.name
    FROM employees e
    JOIN path p ON e.manager_id = p.id
)
SELECT * FROM path;
```

### CTE 用于数据修改
```sql
-- 将删除的数据插入日志表
WITH deleted_rows AS (
    DELETE FROM products WHERE date >= '2020-10-01' AND date < '2020-11-01'
    RETURNING *
)
INSERT INTO products_log SELECT * FROM deleted_rows;

-- 多表操作
WITH
    updated AS (UPDATE t SET val = val + 1 RETURNING *),
    deleted AS (DELETE FROM t2 WHERE id IN (SELECT id FROM updated) RETURNING *)
INSERT INTO t3 SELECT * FROM deleted;
```

### NOT MATERIALIZED
```sql
-- 强制内联（避免物化）
WITH w AS NOT MATERIALIZED (
    SELECT * FROM big_table
)
SELECT * FROM w AS w1 JOIN w AS w2 ON w1.key = w2.ref;
```

---

## 3. GROUP BY 扩展

### GROUPING SETS
```sql
SELECT brand, size, sum(sales) FROM items_sold
GROUP BY GROUPING SETS ((brand), (size), ());

-- 结果：
-- brand | size | sum
-- Foo   | NULL | 30   (按 brand 汇总)
-- NULL  | L    | 15   (按 size 汇总)
-- NULL  | NULL | 50   (总计)
```

### ROLLUP
```sql
-- 等同于 GROUPING SETS ((a,b,c), (a,b), (a), ())
SELECT brand, size, sum(sales) FROM items_sold
GROUP BY ROLLUP (brand, size);
```

### CUBE
```sql
-- 等同于 GROUPING SETS ((a,b,c), (a,b), (a,c), (b,c), (a), (b), (c), ())
SELECT brand, size, sum(sales) FROM items_sold
GROUP BY CUBE (brand, size);
```

---

## 4. LATERAL 子查询

LATERAL 允许子查询引用主表中的列。

```sql
-- 为每个员工获取最新订单
SELECT e.name, o.order_info
FROM employees e
CROSS JOIN LATERAL (
    SELECT order_id, info AS order_info
    FROM orders
    WHERE employee_id = e.id
    ORDER BY created_at DESC
    LIMIT 3
) AS o;

-- 集合返回函数
SELECT p.id, v.vertex_data
FROM polygons p
CROSS JOIN LATERAL vertices(p.poly) AS v;
```

---

## 5. VALUES

```sql
-- VALUES 列表
SELECT * FROM (VALUES (1, 'a'), (2, 'b'), (3, 'c')) AS t(id, name);

-- CTE 中使用 VALUES
WITH data AS (
    VALUES (1, 'first'), (2, 'second'), (3, 'third')
)
SELECT * FROM data;
```

---

## 6. UNION / INTERSECT / EXCEPT

```sql
-- UNION: 并集（去重）
SELECT name FROM table1 UNION SELECT name FROM table2;

-- UNION ALL: 并集（不去重）
SELECT name FROM table1 UNION ALL SELECT name FROM table2;

-- INTERSECT: 交集
SELECT name FROM table1 INTERSECT SELECT name FROM table2;

-- EXCEPT: 差集
SELECT name FROM table1 EXCEPT SELECT name FROM table2;
```

---

## 7. LIMIT 和 NULLS

```sql
-- 分页查询
SELECT * FROM table_name
ORDER BY id
LIMIT 10 OFFSET 20;

-- NULLS LAST/FIRST
SELECT * FROM table_name ORDER BY col NULLS LAST;
SELECT * FROM table_name ORDER BY col NULLS FIRST;

-- FETCH FIRST (SQL 标准)
SELECT * FROM table_name ORDER BY id FETCH FIRST 10 ROWS ONLY;
```

---

## 8. 条件表达式

```sql
-- NULLIF
SELECT NULLIF(a, 0);  -- a 为 0 时返回 NULL，否则返回 a

-- COALESCE
SELECT COALESCE(col1, col2, col3, 'default');  -- 返回第一个非 NULL

-- GREATEST / LEAST
SELECT GREATEST(1, 2, 3);  -- 3
SELECT LEAST(1, 2, 3);   -- 1
SELECT GREATEST(ARRAY[3,1,2]);  -- 3

-- 多行返回
INSERT INTO users (name, email) VALUES
    ('A', 'a@test.com'),
    ('B', 'b@test.com')
RETURNING id, name;
```

---

## 9. 生成列 (Generated Columns)

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    price DECIMAL(10,2),
    quantity INTEGER,
    total DECIMAL(10,2) GENERATED ALWAYS AS (price * quantity) STORED
);
```

---

## 10. 标识列 (Identity Columns)

```sql
-- 标准语法
CREATE TABLE t (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT
);

-- 覆盖自增值
INSERT INTO t OVERRIDING SYSTEM VALUE VALUES (100, 'test');
INSERT INTO t OVERRIDING USER VALUE VALUES (200, 'test2');
```

---

## 11. 模式匹配 (LIKE / SIMILAR TO / ~)

```sql
-- LIKE
SELECT * FROM table WHERE name LIKE '%John%';
SELECT * FROM table WHERE name LIKE 'J_hn';  -- _ 匹配任意字符

-- ILIKE (不区分大小写)
SELECT * FROM table WHERE name ILIKE '%john%';

-- SIMILAR TO (SQL 标准正则)
SELECT * FROM table WHERE name SIMILAR TO '%(John|Jane)%';

-- POSIX 正则
SELECT * FROM table WHERE name ~ '^J.*';
SELECT * FROM table WHERE name ~* '^j.*';  -- 不区分大小写
SELECT * FROM table WHERE name !~ 'test';
```

---

## 12. 数组查询

```sql
-- ANY / ALL
SELECT * FROM t WHERE 'a' = ANY(array_col);
SELECT * FROM t WHERE 'a' = ALL(ARRAY['a','b','c']);

-- 数组切片
SELECT array_col[1:3] FROM t;

-- 数组包含
SELECT * FROM t WHERE array_col @> ARRAY['a','b'];
SELECT * FROM t WHERE array_col <@ ARRAY['a','b','c','d'];
```