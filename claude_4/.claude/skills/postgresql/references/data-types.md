# 数据类型详解

PostgreSQL 18 支持丰富的数据类型。

## 数值类型

### 整数类型
| 类型 | 说明 | 范围 |
|------|------|------|
| SMALLINT | 2字节整数 | -32768 ~ 32767 |
| INTEGER | 4字节整数（常用） | -2147483648 ~ 2147483647 |
| BIGINT | 8字节整数 | -9223372036854775808 ~ 9223372036854775807 |

### 精确小数
| 类型 | 说明 |
|------|------|
| DECIMAL(p,s) | 精确小数，p=精度（总位数），s=小数位数 |
| NUMERIC(p,s) | 同 DECIMAL |

### 浮点数
| 类型 | 说明 | 精度 |
|------|------|------|
| REAL | 4字节浮点 | 约 6 位十进制 |
| DOUBLE PRECISION | 8字节浮点 | 约 15 位十进制 |

### 自增类型
| 类型 | 说明 |
|------|------|
| SERIAL | 4字节自增（1 ~ 2147483647） |
| BIGSERIAL | 8字节自增（1 ~ 9223372036854775807） |
| SMALLSERIAL | 2字节自增（1 ~ 32767） |

### 特殊数值
```sql
-- Infinity 和 NaN
SELECT 'Infinity'::float8, '-Infinity'::float8, 'NaN'::float8;

-- 数值比较
SELECT 'NaN'::float8 > 'Infinity'::float8;  -- true
SELECT 'NaN'::float8 = 'NaN'::float8;        -- true (PostgreSQL 特殊处理)
```

---

## 字符类型

| 类型 | 说明 | 存储 |
|------|------|------|
| VARCHAR(n) | 变长字符串，最大 n 字符 | 实际字符数 + 1 byte |
| CHAR(n) | 定长，不足补空格 | n 字节 |
| TEXT | 变长，无限长度 | 实际字符数 + 1 byte |
| BPCHAR | 定长，自动去除尾随空格 | - |

```sql
-- 长度超过处理
SELECT 'too long'::varchar(5);  -- 截断为 'too l'
SELECT 'too long'::char(5);      -- 补空格为 'too l'
```

---

## 日期时间类型

| 类型 | 说明 |
|------|------|
| DATE | 日期（年、月、日） |
| TIME | 时间（时、分、秒） |
| TIMESTAMP | 日期时间（无时区） |
| TIMESTAMPTZ | 日期时间（有时区） |
| INTERVAL | 时间间隔 |

### 特殊值
```sql
SELECT 'epoch'::timestamp;       -- 1970-01-01 00:00:00+00
SELECT 'infinity'::timestamp;    -- 无限远的未来
SELECT '-infinity'::timestamp;   -- 无限远的过去
SELECT 'now'::timestamp;          -- 当前时间戳
SELECT 'today'::date;             -- 当天午夜
SELECT 'tomorrow'::date;          -- 明天午夜
SELECT 'yesterday'::date;          -- 昨天午夜
```

### 日期计算
```sql
SELECT age(timestamp '1990-01-01');           -- 计算年龄
SELECT date_trunc('hour', now());                 -- 按小时截断
SELECT date_trunc('month', '2024-06-15'::date); -- 月初
SELECT EXTRACT(YEAR FROM now());                 -- 提取年份
SELECT to_char(now(), 'YYYY-MM-DD HH24:MI:SS'); -- 格式化
```

---

## 布尔类型

```sql
SELECT true, false, null;           -- 布尔字面量
SELECT boolean 'true', 'false', 't', 'f', 'yes', 'no', '1', '0';
```

---

## 货币类型

```sql
-- money 类型
CREATE TABLE products (price MONEY);
INSERT INTO products VALUES ('$19.99'), (20.50);

-- 转换
SELECT '52093.89'::money::numeric::float8;
```

---

## 网络地址类型

| 类型 | 说明 |
|------|------|
| INET | IPv4/IPv6 地址 + 子网掩码 |
| CIDR | 网络地址（无主机位） |
| MACADDR | MAC 地址 |
| MACADDR8 | EUI-64 格式 MAC 地址 |

```sql
CREATE TABLE hosts (
    id SERIAL,
    ip INET,
    mac MACADDR
);
INSERT INTO hosts VALUES (1, '192.168.1.100', '00:11:22:33:44:55');

-- 子网查询
SELECT * FROM hosts WHERE ip << '192.168.1.0/24';
```

---

## 范围类型

| 类型 | 说明 |
|------|------|
| INT4RANGE | 整数范围 |
| INT8RANGE | 8字节整数范围 |
| NUMRANGE | 数值范围 |
| DATERANGE | 日期范围 |
| TSRANGE | 时间戳范围（无时区） |
| TSTZRANGE | 时间戳范围（有时区） |

```sql
CREATE TABLE reservations (
    id SERIAL,
    room TEXT,
    period DATERANGE
);
INSERT INTO reservations VALUES (1, '101', '[2024-06-01, 2024-06-05)');

-- 包含查询
SELECT * FROM reservations WHERE period @> DATE '2024-06-02';
SELECT * FROM reservations WHERE period && '[2024-06-03,2024-06-07)'::daterange;
```

---

## 几何类型

| 类型 | 说明 |
|------|------|
| POINT | 点 |
| LINE | 直线 |
| LSEG | 线段 |
| BOX | 矩形 |
| POLYGON | 多边形 |
| CIRCLE | 圆 |

---

## JSON 类型

| 类型 | 说明 | 特点 |
|------|------|------|
| JSON | JSON 文本 | 每次访问解析，存储时校验 |
| JSONB | 二进制 JSON | 预解析，可建索引，存储稍大 |

### JSON 创建
```sql
-- 使用字符串
SELECT '{"name":"John","age":30}'::json;
SELECT '{"name":"John","age":30}'::jsonb;

-- 使用数组/对象构建函数
SELECT jsonb_build_object('name', 'John', 'age', 30);
SELECT jsonb_agg(column) FROM table;  -- 聚合
```

### JSON 查询
```sql
-- 获取字段
SELECT data->>'name' FROM table;  -- 返回文本
SELECT data->'name' FROM table;   -- 返回 JSON

-- 嵌套查询
SELECT data->'user'->>'name' FROM orders WHERE data->'status' = '"pending"';

-- 路径查询
SELECT jsonb_extract_path(data, 'user', 'name');
SELECT data#> '{user,name}' FROM table;
```

### JSON 修改
```sql
-- 设置字段
UPDATE orders SET data = jsonb_set(data, '{status}', '"completed"') WHERE id = 1;

-- 删除字段
UPDATE orders SET data = data - 'temp_field';

-- 追加到数组
UPDATE orders SET data = jsonb_insert(data, '{tags,0}', '"new"');
```

---

## 数组类型

### 创建数组列
```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name TEXT,
    skills TEXT[]
);
```

### 插入数组
```sql
INSERT INTO employees VALUES (1, 'John', ARRAY['Python', 'PostgreSQL']);
INSERT INTO employees VALUES (2, 'Jane', '{"Go", "Kubernetes"}');
```

### 数组查询
```sql
-- 包含元素
SELECT * FROM employees WHERE 'PostgreSQL' = ANY(skills);

-- 包含所有
SELECT * FROM employees WHERE skills @> ARRAY['Python', 'PostgreSQL'];

-- 数组重叠
SELECT * FROM employees WHERE skills && ARRAY['Python'];
```

### 数组操作
```sql
-- 展开数组
SELECT id, unnest(skills) AS skill FROM employees;

-- 数组长度
SELECT array_length(skills, 1) FROM employees;

-- 数组合并
SELECT array_cat(ARRAY['a','b'], ARRAY['c','d']);

-- 数组成员
SELECT array_dims(ARRAY[1,2,3]);  -- [1:3]
```

---

## UUID 类型

```sql
-- 生成 UUID
SELECT gen_random_uuid();         -- v4 (内置)
SELECT uuid_generate_v4();         -- v4 (需要 pgcrypto)

-- 使用 UUID 作为主键
CREATE TABLE t (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT
);
```

---

## XML 类型

```sql
-- 解析 XML
SELECT xmlparse(content '<root><item>test</item></root>');

-- XPath 查询
SELECT xpath('/root/item/text()', xmlcol) FROM table;

-- XML 生成
SELECT xmlelement(name "tag", xmlattributes('value' AS "attr"), 'content');
```

---

## 位串类型

| 类型 | 说明 |
|------|------|
| BIT(n) | 定长 n 位 |
| BIT VARYING(n) | 变长，最大 n 位 |

```sql
SELECT B'1010', X'FF';
SELECT '1010'::bit(4);
SELECT bit_length(B'1010');  -- 4
```

---

## 复合类型

### 创建复合类型
```sql
CREATE TYPE inventory_item AS (
    name TEXT,
    quantity INTEGER,
    price NUMERIC
);
```

### 使用复合类型
```sql
CREATE TABLE on_hand (
    item inventory_item,
    count INTEGER
);
INSERT INTO on_hand VALUES (ROW('widgets', 100, 9.99), 50);
SELECT item.name FROM on_hand WHERE (item).price > 9.0;
```