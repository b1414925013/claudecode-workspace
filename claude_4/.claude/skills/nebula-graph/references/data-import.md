# NebulaGraph 数据导入

## NebulaGraph Importer

```yaml
# yaml 配置示例
version: v3
description: Import CSV to NebulaGraph

client:
  address: "192.168.1.100:9669"
  username: "root"
  password: "password"
  concurrency: 10

log:
  level: info

data:
  path: "/path/to/data.csv"
  schema:
    type: vertex
    vertex:
      id: ":ID"
      tags:
        - name: player
          props:
            - name: name
              type: string
            - name: age
              type: int

files:
  - path: /path/to/player.csv
    schema:
      type: vertex
      vertex:
        id: ":ID"
        tags:
          - name: player
            props:
              - name: name
                type: string
              - name: age
                type: int
    csv:
      with_header: true
      delimiter: ","
```

---

## NebulaGraph Exchange

将 Neo4j、Hive、HBase 等数据源迁移到 NebulaGraph。

```scala
// Spark Exchange 配置示例
spark: {
  app = "nebula-exchange"
  master = "local"
}

nebula: {
  address = "192.168.1.100:9669"
  user = "root"
  pass = "password"
  space = "basketballplayer"
}

tags: [
  {
    name = player
    type = vertex
    mapping = ...
  }
]

edges: [
  {
    name = follow
    type = edge
    mapping = ...
  }
]
```

---

## 全文索引

```ngql
-- 登录 Elasticsearch
SIGN IN TEXT SERVICE (127.0.0.1:9200, HTTP);

-- 创建全文索引（名称以 nebula_ 开头）
CREATE FULLTEXT INDEX ON player(name);

-- 搜索全文
SHOW TEXT SEARCH CLIENTS;
USE <space>;
LOOKUP ON player WHERE PREFIX(player.name, "Tim");
```