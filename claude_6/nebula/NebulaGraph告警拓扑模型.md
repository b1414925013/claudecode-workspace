# NebulaGraph 告警设备拓扑关系模型

## 一、模型概述

本模型用于描述告警与设备之间的拓扑关系，支持以下功能：
- 告警之间的触发/衍生关系
- 设备层级结构（网元 → 单板 → 端口）
- 设备间的连接关系
- 告警与故障设备的关联定位

## 二、节点类型 (Tag)

| 节点类型 | 说明 | 示例 |
|---------|------|------|
| **alarm** | 告警节点 | 网络中断告警、端口DOWN告警 |
| **ne** | 网元（顶层设备） | 路由器、交换机、防火墙 |
| **board** | 单板（中间层设备） | 主控板、业务板 |
| **port** | 端口（底层设备） | 光口、电口 |

## 三、边类型 (Edge)

| 边类型 | 连接对象 | 含义 | 方向 |
|--------|---------|------|------|
| **trigger** | alarm → alarm | 告警触发/衍生关系 | 告警间 |
| **link** | 设备 ↔ 设备 | 设备间同层横向连接 | 双向 |
| **leave** | 父设备 → 子设备 | 设备父子从属关系 | 单向 |
| **happen** | alarm → 设备 | 告警直接发生在该设备（直接故障源） | 单向 |
| **enhance** | alarm → 设备 | 告警关联到直接故障设备的子设备 | 单向 |

## 四、拓扑关系图

```
告警拓扑模型
═══════════════════════════════════════════════════

节点 (Tag):
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ alarm   │  │   ne    │  │  board  │  │  port   │
└─────────┘  └─────────┘  └─────────┘  └─────────┘

边 (Edge Type):
┌──────────┐ 告警→告警    trigger    告警触发/衍生关系
┌──────────┐ 设备↔设备    link       设备间横向连接
┌──────────┐ 设备→设备    leave      设备父子从属关系
┌──────────┐ 告警→设备    happen     告警→直接故障设备
┌──────────┐ 告警→设备    enhance    告警→直接故障设备子设备

示例拓扑:
─────────────────────────────────────────────────

     告警A ──trigger──→ 告警B
        │
      happen
        │
     端口1 ←──link──→ 端口2
        │               │
      leave            leave
        │               │
     单板1             单板2
        │               │
      leave            leave
        │               │
      网元NE1 ←────────┘
         │
      happen / enhance
        │
     告警C
```

## 五、Schema 创建语句

```sql
-- ============================================
-- 告警设备拓扑关系模型 - NebulaGraph Schema
-- ============================================

-- 创建图空间
CREATE SPACE IF NOT EXISTS alarm_topology
(partition_num = 10, replica_factor = 1, vid_type = FIXED_STRING(64));

-- 使用图空间
USE alarm_topology;

-- ============================================
-- 创建 Tag (节点类型)
-- ============================================

-- 告警节点
CREATE TAG IF NOT EXISTS alarm(
    name string NOT NULL COMMENT "告警名称",
    level string COMMENT "告警级别: critical/warning/info",
    occur_time timestamp COMMENT "发生时间",
    content string COMMENT "告警内容"
);

-- 网元节点
CREATE TAG IF NOT EXISTS ne(
    name string NOT NULL COMMENT "网元名称",
    type string COMMENT "网元类型: router/switch/firewall等",
    ip string COMMENT "管理IP"
);

-- 单板节点
CREATE TAG IF NOT EXISTS board(
    name string NOT NULL COMMENT "单板名称",
    slot_id int COMMENT "槽位号"
);

-- 端口节点
CREATE TAG IF NOT EXISTS port(
    name string NOT NULL COMMENT "端口名称",
    speed string COMMENT "端口速率: 1G/10G/100G",
    status string COMMENT "端口状态: up/down"
);

-- ============================================
-- 创建 Edge Type (边类型)
-- ============================================

-- 告警间关系: trigger (告警触发/衍生)
CREATE EDGE IF NOT EXISTS trigger(
    relation_type string DEFAULT "derived" COMMENT "关联类型: derived/related",
    weight double DEFAULT 1.0 COMMENT "关联权重"
);

-- 设备间连接: link (横向同层连接)
CREATE EDGE IF NOT EXISTS link(
    bandwidth string COMMENT "链路带宽",
    media_type string COMMENT "介质类型: fiber/copper"
);

-- 设备父子关系: leave (纵向父子从属)
CREATE EDGE IF NOT EXISTS leave(
    relation string DEFAULT "parent" COMMENT "父子关系: parent/child"
);

-- 告警到直接故障设备: happen
CREATE EDGE IF NOT EXISTS happen(
    reason string COMMENT "故障原因",
    is_root int DEFAULT 1 COMMENT "是否根因: 1是/0否"
);

-- 告警到直接故障设备的子设备: enhance
CREATE EDGE IF NOT EXISTS enhance(
    impact_level int DEFAULT 1 COMMENT "影响级别"
);

-- ============================================
-- 创建索引 (用于查询)
-- ============================================

CREATE TAG INDEX IF NOT EXISTS alarm_name ON alarm(name(64));
CREATE TAG INDEX IF NOT EXISTS alarm_level ON alarm(level(32));
CREATE TAG INDEX IF NOT EXISTS ne_name ON ne(name(64));
CREATE TAG INDEX IF NOT EXISTS board_name ON board(name(64));
CREATE TAG INDEX IF NOT EXISTS port_name ON port(name(64));
```

## 六、数据插入语句

```sql
-- ============================================
-- 节点插入示例
-- ============================================

-- 插入告警
INSERT VERTEX alarm(name, level, occur_time, content) VALUES
    "alarm_001":("网络中断告警", "critical", TIMESTAMP(), "核心路由器连接中断"),
    "alarm_002":("端口DOWN", "warning", TIMESTAMP(), "端口状态异常"),
    "alarm_003":("CPU过载", "warning", TIMESTAMP(), "CPU使用率超过80%");

-- 插入网元
INSERT VERTEX ne(name, type, ip) VALUES 
    "ne_001":("核心路由器R1", "router", "192.168.1.1"),
    "ne_002":("汇聚交换机S1", "switch", "192.168.1.2"),
    "ne_003":("边缘路由器R2", "router", "192.168.1.3");

-- 插入单板
INSERT VERTEX board(name, slot_id) VALUES 
    "board_001":("主控板", 1),
    "board_002":("业务板A", 2),
    "board_003":("业务板B", 3);

-- 插入端口
INSERT VERTEX port(name, speed, status) VALUES 
    "port_001":("万兆光口1", "10G", "up"),
    "port_002":("万兆光口2", "10G", "down"),
    "port_003":("千兆电口1", "1G", "up"),
    "port_004":("千兆电口2", "1G", "up");

-- ============================================
-- 边插入示例
-- ============================================

-- 告警间 trigger 关系
INSERT EDGE trigger(relation_type, weight) VALUES 
    "alarm_001" -> "alarm_002":("derived", 0.9),
    "alarm_002" -> "alarm_003":("related", 0.5);

-- 设备父子关系 (leave)
INSERT EDGE leave() VALUES 
    "ne_001" -> "board_001":(),
    "ne_001" -> "board_002":(),
    "ne_002" -> "board_003":(),
    "board_001" -> "port_001":(),
    "board_002" -> "port_002":(),
    "board_003" -> "port_003":(),
    "board_003" -> "port_004":();

-- 设备间连接 (link)
INSERT EDGE link(bandwidth, media_type) VALUES 
    "port_001" -> "port_002":("10G", "fiber"),
    "port_003" -> "port_004":("1G", "copper");

-- 告警到直接故障设备 (happen)
INSERT EDGE happen(reason, is_root) VALUES
    "alarm_001" -> "port_001":("光纤断裂", 1),
    "alarm_002" -> "port_002":("端口损坏", 1),
    "alarm_003" -> "port_001":(),  -- alarm_003 与 alarm_001 在同一网元，测试单网元多告警故障组
    "alarm_003" -> "board_001":();

-- 告警到子设备 (enhance)
INSERT EDGE enhance(impact_level) VALUES
    "alarm_001" -> "board_001":(2),
    "alarm_002" -> "board_002":(2);
```

## 七、常用查询语句

### 7.1 基础查询

```sql
-- 查看所有空间
SHOW SPACES;

-- 查看当前空间的 Tag
SHOW TAGS;

-- 查看当前空间的 Edge Type
SHOW EDGES;

-- 查看索引
SHOW TAG INDEXES;
SHOW EDGE INDEXES;
```

### 7.2 节点查询

```sql
-- 查询所有告警 (NebulaGraph 需要指定 Tag 前缀)
MATCH (a:alarm) RETURN id(a), a.alarm.name, a.alarm.level, a.alarm.content;

-- 查询所有网元
MATCH (n:ne) RETURN id(n), n.ne.name, n.ne.type;

-- 查询所有单板
MATCH (b:board) RETURN id(b), b.board.name, b.board.slot_id;

-- 查询所有端口
MATCH (p:port) RETURN id(p), p.port.name, p.port.speed, p.port.status;
```

### 7.3 边关系查询

```sql
-- 查询告警的触发关联 (trigger)
MATCH (a1:alarm)-[:trigger]->(a2:alarm)
RETURN id(a1), a1.alarm.name AS source, id(a2), a2.alarm.name AS target;

-- 查询告警的根因设备 (happen)
MATCH (a:alarm)-[:happen]->(d)
RETURN id(a), a.alarm.name AS alarm, id(d), d.port.name AS device;

-- 查询告警增强关联 (enhance)
MATCH (a:alarm)-[:enhance]->(d)
RETURN id(a), a.alarm.name AS alarm, id(d), d.board.name AS child_device;

-- 查询设备的父子关系 (leave) - 需要分别查询不同类型
-- 网元 -> 单板
MATCH (parent:ne)-[:leave]->(child:board)
RETURN id(parent), parent.ne.name AS parent, id(child), child.board.name AS child;
-- 单板 -> 端口
MATCH (parent:board)-[:leave]->(child:port)
RETURN id(parent), parent.board.name AS parent, id(child), child.port.name AS child;

-- 查询设备间的连接 (link)
MATCH (d1:port)-[:link]->(d2:port)
RETURN id(d1), d1.port.name AS source, id(d2), d2.port.name AS target;
```

### 7.4 故障组查询

```sql
-- ============================================
-- 单网元多告警故障组
-- 查询同一网元上有2个及以上告警的情况
-- ============================================
MATCH (a:alarm)-[:happen]->(p:port)-[:leave*1..2]->(n:ne)
WITH n, collect(a) AS alarms
WHERE size(alarms) >= 2
RETURN n.ne.name AS ne_name, size(alarms) AS alarm_count;

-- ============================================
-- U型故障组
-- 查询两个网元各有1个告警，且网元间有link连接的情况
-- ============================================
MATCH (a1:alarm)-[:happen]->(p1:port)-[:leave*]->(n1:ne)
MATCH (a2:alarm)-[:happen]->(p2:port)-[:leave*]->(n2:ne)
WHERE n1 <> n2
MATCH (p1)-[:link]->(p2) OR (p1)<-[:link]-(p2)
RETURN n1.ne.name AS ne1, a1.alarm.name AS alarm1,
       n2.ne.name AS ne2, a2.alarm.name AS alarm2;

-- ============================================
-- C型故障组
-- 查询三个网元链式相连，首尾网元各有1个告警的情况
-- ============================================
MATCH (a1:alarm)-[:happen]->(p1:port)-[:leave*]->(n1:ne)
MATCH (a2:alarm)-[:happen]->(p3:port)-[:leave*]->(n3:ne)
WHERE n1 <> n3
MATCH (n1)-[:leave*0..1]->(b1:board)-[:leave*0..1]->(p1)
MATCH (n2:ne)-[:leave*0..1]->(b2:board)-[:leave*0..1]->(p2)
MATCH (n3)-[:leave*0..1]->(b3:board)-[:leave*0..1]->(p3)
WHERE n1 <> n2 AND n2 <> n3
MATCH (p1)-[:link]->(p2)
MATCH (p2)-[:link]->(p3)
RETURN n1.ne.name AS ne_start, a1.alarm.name AS alarm_start,
       n2.ne.name AS ne_middle,
       n3.ne.name AS ne_end, a2.alarm.name AS alarm_end;
```

### 7.5 路径查询

```sql
-- 查询告警到根因设备的完整路径
MATCH p=(a:alarm)-[:happen|enhance|leave*]->(root)
WHERE a.alarm.name = "网络中断告警"
RETURN p;

-- 查询设备拓扑路径
MATCH p=(n1:ne)-[:leave*]->(p1:port)-[:link]->(p2:port)<-[:leave*]-(n2:ne)
RETURN n1.ne.name AS ne1, p1.port.name AS port1, p2.port.name AS port2, n2.ne.name AS ne2;

-- 查询两个设备间的所有路径
MATCH p=(n1:ne)-[:leave|link*]->(n2:ne)
WHERE n1.ne.name = "核心路由器R1" AND n2.ne.name = "汇聚交换机S1"
RETURN p;
```

### 7.6 统计查询

```sql
-- 统计各类型设备数量
MATCH (n:ne) RETURN count(n) AS ne_count;
MATCH (b:board) RETURN count(b) AS board_count;
MATCH (p:port) RETURN count(p) AS port_count;

-- 统计各级别告警数量
MATCH (a:alarm) 
RETURN a.level AS level, count(a) AS count 
ORDER BY count DESC;

-- 统计每个网元的告警数量
MATCH (a:alarm)-[:happen]->(p:port)-[:leave*]->(n:ne)
RETURN n.name AS ne_name, count(a) AS alarm_count
ORDER BY alarm_count DESC;

-- 统计 trigger 关系数量
MATCH ()-[r:trigger]->() RETURN count(r) AS trigger_count;
```

### 7.7 更新和删除

```sql
-- 更新告警状态
UPDATE VERTEX ON alarm "alarm_001" SET level = "resolved", 
    content = "故障已恢复" WHERE alarm.level = "critical";

-- 删除边
DELETE EDGE trigger "alarm_001" -> "alarm_002";

-- 删除顶点 (需先删除关联边)
DELETE VERTEX "alarm_003" WITH EDGE;

-- 批量删除边
GO FROM "alarm_001" OVER trigger YIELD src(edge) AS src, dst(edge) AS dst |
DELETE EDGE trigger $-.src -> $-.dst;
```

## 八、连接方式

### 8.1 使用 Nebula Studio (Web UI)

```
http://localhost:7001
```

### 8.2 使用 nebula-console

```bash
# 进入客户端容器
docker exec -it nebula-console sh

# 连接 NebulaGraph 服务
nebula-console -addr nebula-graphd -port 9669 -u root -p nebula

# 或使用 IP 地址
nebula-console -addr <your-ip> -port 9669 -u root -p nebula
```

### 8.3 使用 Python 连接

```bash
pip install nebula3-python
```

```python
from nebula3.gclient.net import ConnectionPool

# 初始化连接池
connection_pool = ConnectionPool()
connection_pool.init([("localhost", 9669)])

with connection_pool.session("root", "nebula") as session:
    # 执行查询
    result = session.execute("USE alarm_topology")
    result = session.execute("MATCH (a:alarm) RETURN a")
    print(result)
```

## 九、文件说明

| 文件 | 说明 |
|------|------|
| `NebulaGraph告警拓扑模型.md` | 本文档 |
| `alarm_topology.sql` | Schema 创建脚本 |
