---
name: nebula-graph
description: Use when user asks about NebulaGraph, nGQL queries, creating graph spaces, tags, edge types, data import/export,运维管理, or encounters nGQL syntax errors.
---

# NebulaGraph Assistant

帮助用户使用 NebulaGraph 图数据库，生成 nGQL 查询语句，修复语法错误，处理数据导入导出和运维管理。

## Quick Reference

```ngql
-- 连接数据库
USE <space_name>;

-- 查看 Schema
SHOW TAGS;
SHOW EDGES;
DESC TAG <tag_name>;

-- 插入数据
INSERT VERTEX player(name, age) VALUES "player100":("Tim Duncan", 42);
INSERT EDGE follow(degree) VALUES "player100" -> "player101":(95);

-- 查询数据
GO FROM "player100" OVER follow;
MATCH (v:player) RETURN v LIMIT 10;
LOOKUP ON player WHERE player.name == "Tim Duncan";
```

---

## 文件结构

本技能拆分为多个参考文件，方便按需查阅：

- [核心概念](references/core-concepts.md) - 图空间、Tag、Edge Type、VID
- [nGQL 命令](references/ngql-commands.md) - 索引、DML、DQL、聚合函数
- [数据类型](references/data-types.md) - 数值、字符串、布尔、NULL
- [运维管理](references/operations.md) - BALANCE、JOB、Compaction
- [数据导入](references/data-import.md) - Importer、Exchange、全文索引
- [性能优化](references/performance.md) - EXPLAIN/PROFILE、常见错误
- [nGQL vs openCypher](references/ngql-vs-opencypher.md) - 语法差异、客户端连接

---

## References

- NebulaGraph 官方文档: https://docs.nebula-graph.com.cn/