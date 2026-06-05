# NebulaGraph 核心概念

NebulaGraph 是一个高性能、可扩展的分布式图数据库，使用 nGQL 作为查询语言。nGQL 结合了原生图查询和部分 openCypher 兼容语法。

## 图空间 (Graph Space)

NebulaGraph 中的顶级数据组织单元，类似于数据库概念。

```ngql
-- 创建图空间
CREATE SPACE [IF NOT EXISTS] <space_name>(
    partition_num = <num>,      -- 分片数
    replica_factor = <num>,      -- 副本数
    vid_type = {FIXED_STRING(<length>) | INT64},
    charset = utf8,
    collate = utf8_bin
) comment = "<description>";

-- 克隆图空间
CREATE SPACE [IF NOT EXISTS] <new_space> AS <old_space>;

-- 查看/删除图空间
SHOW SPACES;
SHOW CREATE SPACE <space_name>;
DROP SPACE [IF EXISTS] <space_name>;
```

---

## Tag（标签）

定义点的类型和属性，类似于 openCypher 的 Label，但必须先创建并定义属性类型。

```ngql
-- 创建 Tag
CREATE TAG [IF NOT EXISTS] <tag_name>(
    <prop_name> <data_type> [NULL | NOT NULL] [DEFAULT <value>],
    ...
);

-- 修改 Tag
ALTER TAG <tag_name> ADD (col1 type, ...);
ALTER TAG <tag_name> CHANGE (col1 new_type, ...);
ALTER TAG <tag_name> DROP (col1, ...);

-- 查看 Tag
SHOW TAGS;
DESC TAG <tag_name>;
```

---

## Edge Type（边类型）

定义边的类型和属性，有方向性，支持 Rank。

```ngql
-- 创建 Edge Type
CREATE EDGE [IF NOT EXISTS] <edge_type>(
    <prop_name> <data_type> [NULL | NOT NULL] [DEFAULT <value>],
    ...
);

-- 修改 Edge Type
ALTER EDGE <edge_type> ADD (...) ;
ALTER EDGE <edge_type> CHANGE (...) ;
ALTER EDGE <edge_type> DROP (...) ;

-- 查看 Edge Type
SHOW EDGES;
DESC EDGE <edge_type>;
```

---

## VID (Vertex ID)

点的唯一标识符，支持 INT64 或 FIXED_STRING。

```ngql
-- VID 类型在创建图空间时指定
CREATE SPACE my_space(vid_type = INT64);

-- 或 FIXED_STRING
CREATE SPACE my_space(vid_type = FIXED_STRING(32));
```

---

## When to Use

- 用户询问 NebulaGraph 基本操作
- 需要创建图空间、Tag、Edge type
- 需要编写 nGQL 查询（INSERT、MATCH、GO、FETCH 等）
- 遇到 nGQL 语法错误需要修复
- 需要导入/导出数据
- 需要运维管理（BALANCE、Compaction、JOB 等）

## When NOT to Use

- 用户询问其他图数据库（如 Neo4j、TigerGraph）
- 需要 SPARQL 或 GraphQL 查询
- 需要 RDF 数据处理

---

## Integration

- 配合 `brainstorming` 分析数据模型设计
- 配合 `verification-before-completion` 验证查询正确性

## References

- NebulaGraph 官方文档: https://docs.nebula-graph.com.cn/