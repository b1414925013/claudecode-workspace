# nGQL 命令参考

## 1. 索引操作

### 创建索引（用于 LOOKUP）
```ngql
CREATE [TAG | EDGE] INDEX [IF NOT EXISTS] <index_name> ON <tag_or_edge>(<prop_name>(<length>));
```

### 重建索引
```ngql
REBUILD [TAG | EDGE] INDEX <index_name>;
SHOW JOB <job_id>;
```

### 查看索引
```ngql
SHOW [TAG | EDGE] INDEXES;
```

---

## 2. 数据写入

### 插入点
```ngql
INSERT VERTEX [IF NOT EXISTS] [tag_props, ...]
VALUES <vid>: ([prop_value_list]);

-- 多 Tag
INSERT VERTEX player(name, age), team(name)
VALUES "player100":("Tim Duncan", 42, "Spurs");
```

### 插入边
```ngql
INSERT EDGE [IF NOT EXISTS] <edge_type>(prop_list)
VALUES <src_vid> -> <dst_vid>[@rank]: ([prop_values]);

-- 示例
INSERT EDGE follow(degree) VALUES "player100" -> "player101":(95);
INSERT EDGE serve(start_year, end_year) VALUES "player100" -> "team100"(1997, 2016);
```

### 批量删除
```ngql
DELETE VERTEX <vid> [WITH EDGE];
DELETE EDGE <edge_type> <src_vid> -> <dst_vid>[@rank];
```

---

## 3. 数据查询

### GO 语句（原生 nGQL）
```ngql
GO [1..N STEPS] FROM <vid> OVER <edge_type>
[WHERE <conditions>]
[YIELD [DISTINCT] <expressions>]
[ORDER BY <expr> [ASC | DESC]]
[LIMIT <n>];
```

### GO FROM ... OVER 多跳查询
```ngql
GO 2 STEPS FROM "player100" OVER follow
WHERE properties($$, "player").age > 35
YIELD dst(edge) AS id, properties($$).name AS name;
```

### FETCH 属性获取
```ngql
FETCH PROP ON <tag> <vid>;
FETCH PROP ON <edge_type> <src_vid> -> <dst_vid>;
FETCH PROP ON player "player100" YIELD player.name, player.age;
```

### LOOKUP（需要索引）
```ngql
LOOKUP ON <tag> WHERE <expression> YIELD <expressions>;
LOOKUP ON player WHERE player.name == "Tim Duncan" YIELD id(vertex);
```

### MATCH 查询
```ngql
-- 单点查询（需 LIMIT）
MATCH (v:player) RETURN v LIMIT 10;

-- 模式匹配
MATCH (v1:player)-[e:follow]->(v2:player)
WHERE v1.age > 35
RETURN v1.name, e.degree, v2.name
ORDER BY v1.name
LIMIT 20;

-- 变长模式
MATCH (v1:player)-[*1..3]->(v2)
WHERE v1.name == "Tim Duncan"
RETURN v2;
```

### 管道符 |
```ngql
-- 管道连接多个查询
GO FROM "player100" OVER follow YIELD dst(edge) AS id |
GO FROM $-.id OVER serve YIELD properties($$).name AS Team, properties($^).name AS Player;

-- 子查询
GO FROM "player100" OVER follow |
GO FROM $-.dst AS id OVER serve
WHERE properties($$).start_year > 2000
YIELD properties($$).name AS Team;
```

---

## 4. 聚合与分组

### 聚合函数
```ngql
RETURN COUNT(*), COUNT(DISTINCT v), SUM(e.degree), AVG(v.age), COLLECT(v.name);
```

### GROUP BY
```ngql
MATCH (v1:player)-[e:follow]->(v2:player)
RETURN v2.name AS team, COUNT(*) AS cnt, AVG(e.degree) AS avg_degree
ORDER BY cnt DESC;
```

### WITH 分组
```ngql
MATCH (v:player)-[]->(t:team)
WITH t.name AS team, COUNT(v) AS player_cnt
WHERE player_cnt > 2
RETURN team, player_cnt;
```

---

## 5. 内置函数

### 数学函数
```ngql
RETURN abs(-5), round(3.14, 1), sqrt(9), cbrt(27), pow(2, 3);
RETURN e(), pi(), floor(3.7), ceil(3.1);
```

### 字符串函数
```ngql
RETURN lower("NBA"), upper("nba"), length("abc");
RETURN substr("hello", 1, 3), trim(" abc ");
RETURN replace("a-b-c", "-", ":");
```

### 类型转换
```ngql
RETURN toInteger("123"), toFloat("3.14"), toString(123);
RETURN hash("abc"), now(), uuid();
```

### 日期时间
```ngql
RETURN now(), date(), time(), datetime();
RETURN year(date()), month(date()), day(date()), hour(datetime());
```