# 常用函数参考

## 1. 字符串函数

```sql
-- 长度
SELECT length('hello');                    -- 5
SELECT char_length('你好');                 -- 2（字符数）
SELECT bit_length('hello');                -- 40（位数）

-- 大小写
SELECT lower('HELLO');                      -- hello
SELECT upper('hello');                      -- HELLO
SELECT initcap('hello world');              -- Hello World

-- 字符串操作
SELECT substr('hello', 2, 3);              -- ell
SELECT substring('hello' FROM 2 FOR 3);    -- ell
SELECT trim('  hello  ');                   -- hello
SELECT trim(LEADING FROM '  hello  ');      -- hello  (去首部)
SELECT trim(TRAILING FROM '  hello  ');    --   hello (去尾部)
SELECT ltrim('  hello  ');                  -- hello
SELECT rtrim('  hello  ');                  --   hello
SELECT btrim('  hello  ');                  -- hello

-- 字符串替换/拼接
SELECT replace('hello', 'l', 'x');         -- hexxo
SELECT overlay('hello' PLACING 'xx' FROM 2 FOR 3);  -- hexxo
SELECT concat('a', 'b', 'c', NULL, 'd');   -- abcd (忽略 NULL)
SELECT concat_ws('-', 'a', 'b', 'c');      -- a-b-c
SELECT string_agg(name, ',') FROM users;    -- 聚合为字符串
SELECT string_agg(DISTINCT name, ',' ORDER BY name) FROM users;

-- 字符串拆分/定位
SELECT split_part('a,b,c', ',', 2);        -- b
SELECT split_to_array('a,b,c', ',');      -- {a,b,c}
SELECT position('ell' IN 'hello');          -- 2
SELECT locate('ell', 'hello');             -- 2

-- 字符串格式化
SELECT format('Hello %s, you have %s messages', 'John', 3);
SELECT format('%% %%');                     -- % %

-- 正则替换
SELECT regexp_replace('hello', 'l', 'x', 'g');  -- hexxo
SELECT regexp_matches('hello', 'l+');     -- {l}
SELECT regexp_split_to_table('hello', 'l'); -- 返返: he, o
SELECT regexp_split_to_array('hello', 'l'); -- {he,o}
```

---

## 2. 日期时间函数

```sql
-- 当前时间
SELECT now();                             -- 2024-06-03 10:30:00+08
SELECT current_timestamp;                   -- 同 now()
SELECT current_date;                       -- 2024-06-03
SELECT current_time;                       -- 10:30:00+08
SELECT transaction_timestamp();             -- 事务开始时间
SELECT statement_timestamp();              -- 语句开始时间

-- 日期计算
SELECT age(timestamp '1990-01-01', now()); -- 计算年龄差
SELECT age(now(), timestamp '1990-01-01');
SELECT date_trunc('hour', now());          -- 2024-06-03 10:00:00
SELECT date_trunc('day', now());           -- 2024-06-03 00:00:00
SELECT date_trunc('month', '2024-06-15'::date); -- 2024-06-01

-- 日期提取
SELECT EXTRACT(YEAR FROM now());           -- 2024
SELECT EXTRACT(MONTH FROM now());           -- 6
SELECT EXTRACT(DAY FROM now());            -- 3
SELECT EXTRACT(DOW FROM now());            -- 1 (0=周日, 1=周一)
SELECT EXTRACT(QUARTER FROM now());        -- 2
SELECT EXTRACT(WEEK FROM now());           -- 第几周
SELECT date_part('hour', now());           -- 10

-- 日期构造
SELECT make_date(2024, 6, 3);             -- 2024-06-03
SELECT make_time(10, 30, 0);               -- 10:30:00
SELECT make_timestamptz(2024, 6, 3, 10, 30, 0, '+08'); -- 带时区
SELECT make_interval(years => 2, months => 3); -- 2年3月

-- 日期运算
SELECT '2024-06-01'::date + INTERVAL '7 days';    -- 2024-06-08
SELECT '2024-06-01'::date - '2024-05-01'::date;  -- 31 days
SELECT now() + INTERVAL '1 hour';
SELECT now() - INTERVAL '1 month';

-- 时区转换
SELECT now() AT TIME ZONE 'UTC';           -- 转为 UTC 时间
SELECT timezone('UTC', now());             -- 同上
SELECT timezone('America/New_York', now());

-- 格式化
SELECT to_char(now(), 'YYYY-MM-DD HH24:MI:SS');
SELECT to_char(now(), 'FMMonth DD, YYYY'); -- June 3, 2024
SELECT to_char(1234.56, '9999.99');       -- " 1234.56"
SELECT to_char(1234.56, '9999.99');       -- " 1234.56"
SELECT to_char(1234.56, 'FM9999.99');    -- "1234.56"
```

---

## 3. 数学函数

```sql
-- 基础
SELECT abs(-5);                           -- 5
SELECT sign(-5);                           -- -1
SELECT sqrt(9);                            -- 3
SELECT cbrt(27);                           -- 3
SELECT pow(2, 3);                          -- 8
SELECT power(2, 3);                        -- 8
SELECT exp(1);                             -- 2.718...
SELECT ln(2.718);                          -- 1
SELECT log(100);                           -- 2
SELECT log(10, 100);                       -- 2
SELECT log2(8);                            -- 3
SELECT factorial(5);                       -- 120

-- 舍入
SELECT round(3.14159, 2);                  -- 3.14
SELECT trunc(3.14159, 2);                  -- 3.14
SELECT floor(3.7);                         -- 3
SELECT ceil(3.1);                          -- 4
SELECT round(3.5);                         -- 4 (四舍五入)
SELECT round(2.5);                         -- 3 (四舍五入到偶数)

-- 三角函数
SELECT pi();                              -- 3.14159265358979
SELECT degrees(pi());                     -- 180
SELECT radians(180);                      -- 3.14159...
SELECT sin(0);                             -- 0
SELECT cos(0);                             -- 1
SELECT tan(pi()/4);                        -- 1
SELECT atan(1);                            -- 0.785...
SELECT asin(1);                            -- 1.570...
SELECT acos(1);                            -- 0

-- 随机数
SELECT random();                           -- 0-1 之间的随机数
SELECT setseed(0.5);                       -- 设置随机种子
SELECT floor(random() * 100) + 1;         -- 1-100 随机整数
```

---

## 4. 聚合函数

```sql
-- 基础聚合
SELECT COUNT(*), COUNT(col), COUNT(DISTINCT col) FROM t;
SELECT SUM(col), AVG(col), MIN(col), MAX(col) FROM t;
SELECT json_agg(col), jsonb_agg(col) FROM t;  -- 聚合为 JSON
SELECT array_agg(col) FROM t;                 -- 聚合为数组

-- 字符串聚合
SELECT string_agg(name, ',') FROM users;
SELECT string_agg(DISTINCT name, ',' ORDER BY name) FROM users;

-- 统计聚合
SELECT stddev(col), stddev_pop(col) FROM t;  -- 标准差
SELECT variance(col) FROM t;                  -- 方差
SELECT var_pop(col) FROM t;                  -- 总体方差

-- 聚合 FILTER
SELECT COUNT(*) FILTER (WHERE status = 'active') FROM users;
SELECT SUM(amount) FILTER (WHERE date > '2024-01-01') FROM orders;

-- WITHIN GROUP
SELECT string_agg(name, ',') WITHIN GROUP (ORDER BY name) FROM users;
SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY salary) FROM employees;
```

---

## 5. 窗口函数（聚合类）

```sql
-- 累计聚合
SELECT date, value,
    SUM(value) OVER (ORDER BY date) AS cumulative_sum,
    AVG(value) OVER (ORDER BY date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg
FROM daily_sales;

-- FIRST/LAST
SELECT first_value(col) OVER (ORDER BY date),
    last_value(col) OVER (ORDER BY date) FROM t;

-- NTH_VALUE
SELECT nth_value(col, 2) OVER (ORDER BY date) FROM t;
```

---

## 6. 条件函数

```sql
SELECT NULLIF(a, b);           -- a=b 时返回 NULL
SELECT NULLIF(5, 5);          -- NULL
SELECT NULLIF(5, 10);         -- 5

SELECT COALESCE(a, b, c);      -- 返回第一个非 NULL
SELECT COALESCE(NULL, 'default');  -- 'default'

SELECT GREATEST(a, b, c);      -- 返回最大值
SELECT LEAST(a, b, c);        -- 返回最小值

SELECT CASE WHEN condition THEN result1 ELSE result2 END;
SELECT CASE WHEN a > b THEN 'a greater' WHEN a < b THEN 'b greater' ELSE 'equal' END FROM t;

-- DECODE (Oracle 兼容)
SELECT decode(col, 'a', 1, 'b', 2, 3) FROM t;
```

---

## 7. JSON/JSONB 函数

```sql
-- JSON 创建
SELECT jsonb_build_object('name', 'John', 'age', 30);
SELECT jsonb_build_array(1, 2, 3);
SELECT jsonb_insert('{"a":[1,2,3]}', '{a,1}', 99);  -- 插入到指定位置

-- JSON 查询
SELECT data->>'name';           -- 获取文本（返回 text）
SELECT data->'name';           -- 获取 JSON（返回 json）
SELECT data#> '{a,b}';         -- 深层获取
SELECT jsonb_path_exists(data, '$.user.name');
SELECT jsonb_path_match(data, '$.active == true');

-- JSON 修改
SELECT jsonb_set(data, '{name}', '"new_value"');
SELECT jsonb_set(data, '{name}', '"new_value"', false);  -- 不存在时不创建
SELECT jsonb_insert(data, '{tags,0}', '"new"');
SELECT data - 'field';          -- 删除字段
SELECT data || '{"a":1}';       -- 合并
SELECT jsonb_concat('{"a":1}'::jsonb, '{"b":2}'::jsonb);

-- JSON 展开
SELECT jsonb_array_elements('[1,2,3]');  -- 展开为多行
SELECT jsonb_object_keys('{"a":1,"b":2}'); -- 获取所有键
```

---

## 8. 数组函数

```sql
-- 数组构建
SELECT array[1,2,3];
SELECT ARRAY[1,2,3];
SELECT array_append(ARRAY[1,2], 3);
SELECT array_prepend(0, ARRAY[1,2]);
SELECT array_cat(ARRAY[1,2], ARRAY[3,4]);
SELECT array_remove(ARRAY[1,2,2,3], 2);  -- 移除所有 2
SELECT array_replace(ARRAY[1,2,3], 2, 99); -- 替换所有 2

-- 数组查询
SELECT unnest(ARRAY[1,2,3]);              -- 展开为多行
SELECT array_dims(ARRAY[1,2,3]);         -- [1:3]
SELECT array_length(ARRAY[1,2,3], 1);    -- 3
SELECT array_lower('[0:2]={1,2,3}'::integer[], 1); -- 0
SELECT array_upper('[0:2]={1,2,3}'::integer[], 1); -- 2

-- 数组包含
SELECT ARRAY[1,2,3] @> ARRAY[1,2];        -- 包含
SELECT ARRAY[1,2] <@ ARRAY[1,2,3];        -- 被包含
SELECT ARRAY[1,2] && ARRAY[2,3];          -- 重叠
SELECT 'hello' = ANY(ARRAY['hello','world']);
```

---

## 9. 范围函数

```sql
-- 范围构造
SELECT int4range(1, 10);
SELECT int8range(1, 10);
SELECT daterange('2024-01-01', '2024-06-01');
SELECT tsrange('2024-01-01 00:00'::timestamp, '2024-06-01 00:00'::timestamp);

-- 范围操作
SELECT int4range(1, 10) @> 5;            -- 包含
SELECT int4range(1, 10) @> int4range(2, 3); -- 包含范围
SELECT int4range(1, 10) && int4range(5, 15); -- 重叠
SELECT int4range(1, 10) - int4range(5, 15); -- 差
SELECT range_merge(int4range(1,5), int4range(3,10)); -- 合并
```

---

## 10. UUID 函数

```sql
SELECT gen_random_uuid();                 -- v4
SELECT uuid_generate_v4();               -- v4 (需 extension)
SELECT uuid_generate_v1();                -- v1 (需 extension)
SELECT uuid_nil();                        -- 全零 UUID
SELECT uuid_in('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11');
SELECT uuid_out(uuid_in('...'));          -- 转换
```

---

## 11. 加密/哈希函数

```sql
-- 需要 extension: pgcrypto

-- 哈希
SELECT md5('test');
SELECT sha256('test');
SELECT crypt('password', gen_salt('md5'));
SELECT crypt('password', '$1$xxxx');      -- 验证密码

-- 加密
SELECT encrypt('data', 'key', 'aes');
SELECT decrypt(data, 'key', 'aes');

-- 密码哈希
SELECT hash_password('password');
SELECT hash_login('password');
```

---

## 12. 系统信息函数

```sql
-- 数据库信息
SELECT current_database();
SELECT current_schema();
SELECT current_schemas();                 -- 包括 search_path

-- 用户信息
SELECT current_user;
SELECT session_user;
SELECT inet_client_addr();
SELECT inet_server_addr();

-- 版本
SELECT version();
SELECT current_setting('server_version_num');
SELECT pg_restart.global_pid;

-- 配置
SELECT current_setting('max_connections');
SELECT set_config('max_connections', '100', false);
```

---

## 13. 类型转换函数

```sql
-- 类型转换
SELECT '123'::integer;
SELECT cast('123' AS integer);
SELECT to_char(123, '999');               -- 转字符串
SELECT to_number('123', '999');           -- 字符串转数字
SELECT to_date('2024-06-03', 'YYYY-MM-DD');
SELECT to_timestamp('2024-06-03', 'YYYY-MM-DD');
SELECT to_tsvector('english', 'hello world');
SELECT to_tsquery('english', 'hello & world');

-- 二进制转换
SELECT encode('test'::bytea, 'hex');
SELECT decode('74657374', 'hex');         -- hex 解码为 bytea
```

---

## 14. 事务/锁函数

```sql
-- 事务 ID
SELECT txid_current();
SELECT txid_current_snapshot();
SELECT txid_visible_in_snapshot(txid, snapshot);

-- 事务状态
SELECT pg_current_xact_id();
SELECT pg_xact_status('0/12345');

-- 锁
SELECT pg_advisory_lock(key);
SELECT pg_advisory_unlock(key);
SELECT pg_try_advisory_lock(key);         -- 非阻塞
SELECT pg_advisory_unlock_all();

-- 两阶段提交
SELECT pg_prepared_xacts();
```

---

## 15. 触发器函数

```sql
-- 返回 NEW/OLD
-- TG_OP: INSERT, UPDATE, DELETE, TRUNCATE
-- NEW: 新行 (INSERT/UPDATE)
-- OLD: 旧行 (UPDATE/DELETE)

CREATE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, operation, old_data, new_data, timestamp)
    VALUES (TG_TABLE_NAME, TG_OP, OLD.*, NEW.*, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```