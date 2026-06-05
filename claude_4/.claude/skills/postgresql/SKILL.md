---
name: postgresql
description: Use when user asks about PostgreSQL database operations, SQL queries, database administration, performance tuning, data migration, or troubleshooting PostgreSQL errors.
---

# PostgreSQL Assistant

帮助用户使用 PostgreSQL 数据库，编写 SQL 查询，执行数据库管理，性能调优，以及故障排查。

## When to Use

- 用户询问 PostgreSQL 基本操作
- 需要编写 SQL 查询（SELECT、INSERT、UPDATE、DELETE）
- 需要创建/修改数据库对象（表、索引、视图、序列）
- 数据库性能问题诊断和优化
- 数据导入/导出、迁移
- 遇到 SQL 错误需要修复
- 数据库备份恢复

## When NOT to Use

- 用户询问 NoSQL 数据库（如 MongoDB、Redis）
- 需要图数据库查询（应使用 nebula-graph）
- 特定的云数据库服务配置

## 技能文件结构

本技能包含以下子文件，完整覆盖 PostgreSQL 18 所有功能：

| 文件 | 内容 |
|------|------|
| `references/sql-commands.md` | SQL 命令参考（DDL/DML/DCL） |
| `references/data-types.md` | 数据类型详解 |
| `references/advanced-queries.md` | 高级查询（窗口函数、CTE、分区） |
| `references/functions.md` | 常用函数参考 |
| `references/performance.md` | 性能优化指南 |
| `references/error-codes.md` | 常见错误代码 |

## 快速参考

### 常用 SQL

```sql
-- 创建数据库
CREATE DATABASE dbname;

-- 创建表
CREATE TABLE t (id SERIAL PRIMARY KEY, name TEXT);

-- 插入
INSERT INTO t (name) VALUES ('test');

-- 查询
SELECT * FROM t WHERE id = 1;

-- 更新
UPDATE t SET name = 'new' WHERE id = 1;

-- 删除
DELETE FROM t WHERE id = 1;
```

### 常用系统命令

```bash
# 连接数据库
psql -U username -h localhost -d dbname

# 备份
pg_dump -U username -h localhost -d dbname -f backup.sql

# 恢复
psql -U username -h localhost -d dbname -f backup.sql
```

## Integration

- 配合 `brainstorming` 分析数据模型设计
- 配合 `verification-before-completion` 验证 SQL 正确性
- 配合 `systematic-debugging` 排查数据库问题

## References

- PostgreSQL 官方文档: https://www.postgresql.org/docs/
- PostgreSQL Wiki: https://wiki.postgresql.org/wiki/Main_Page