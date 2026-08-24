-- ============================================
-- 告警设备拓扑关系模型 - NebulaGraph Schema
-- ============================================

-- 创建图空间
CREATE SPACE IF NOT EXISTS alarm_topology(partition_num = 10, replica_factor = 1, vid_type = FIXED_STRING(64));

-- 使用图空间
USE alarm_topology;

-- ============================================
-- 创建 Tag (节点类型) - 单行格式
-- ============================================

-- 告警节点
CREATE TAG IF NOT EXISTS alarm(name string NOT NULL COMMENT "告警名称", level string COMMENT "告警级别: critical/warning/info", occur_time timestamp COMMENT "发生时间", content string COMMENT "告警内容");

-- 网元节点
CREATE TAG IF NOT EXISTS ne(name string NOT NULL COMMENT "网元名称", type string COMMENT "网元类型: router/switch/firewall等", ip string COMMENT "管理IP");

-- 单板节点
CREATE TAG IF NOT EXISTS board(name string NOT NULL COMMENT "单板名称", slot_id int COMMENT "槽位号");

-- 端口节点
CREATE TAG IF NOT EXISTS port(name string NOT NULL COMMENT "端口名称", speed string COMMENT "端口速率: 1G/10G/100G", status string COMMENT "端口状态: up/down");

-- ============================================
-- 创建 Edge Type (边类型) - 单行格式
-- ============================================

-- 告警间关系: trigger (告警触发/衍生)
CREATE EDGE IF NOT EXISTS trigger(relation_type string DEFAULT "derived" COMMENT "关联类型: derived/related", weight double DEFAULT 1.0 COMMENT "关联权重");

-- 设备间连接: link (横向同层连接)
CREATE EDGE IF NOT EXISTS link(bandwidth string COMMENT "链路带宽", media_type string COMMENT "介质类型: fiber/copper");

-- 设备父子关系: leave (纵向父子从属)
CREATE EDGE IF NOT EXISTS leave(relation string DEFAULT "parent" COMMENT "父子关系: parent/child");

-- 告警到直接故障设备: happen
CREATE EDGE IF NOT EXISTS happen(reason string COMMENT "故障原因", is_root int DEFAULT 1 COMMENT "是否根因: 1是/0否");

-- 告警到直接故障设备的子设备: enhance
CREATE EDGE IF NOT EXISTS enhance(impact_level int DEFAULT 1 COMMENT "影响级别");

-- ============================================
-- 创建索引 (用于查询) - 单行格式
-- ============================================

CREATE TAG INDEX IF NOT EXISTS alarm_name ON alarm(name(64));
CREATE TAG INDEX IF NOT EXISTS alarm_level ON alarm(level(32));
CREATE TAG INDEX IF NOT EXISTS ne_name ON ne(name(64));
CREATE TAG INDEX IF NOT EXISTS board_name ON board(name(64));
CREATE TAG INDEX IF NOT EXISTS port_name ON port(name(64));

-- ============================================
-- 数据插入示例 - 单行格式
-- ============================================

-- 插入告警
INSERT VERTEX alarm(name, level, occur_time, content) VALUES "alarm_001":("网络中断告警", "critical", TIMESTAMP(), "核心路由器连接中断");
INSERT VERTEX alarm(name, level, occur_time, content) VALUES "alarm_002":("端口DOWN", "warning", TIMESTAMP(), "端口状态异常");
-- 测试单网元多告警故障组：在同一网元上添加新告警
INSERT VERTEX alarm(name, level, occur_time, content) VALUES "alarm_003":("CPU告警", "warning", TIMESTAMP(), "CPU使用率过高");

-- 插入网元
INSERT VERTEX ne(name, type, ip) VALUES "ne_001":("核心路由器R1", "router", "192.168.1.1");
INSERT VERTEX ne(name, type, ip) VALUES "ne_002":("汇聚交换机S1", "switch", "192.168.1.2");

-- 插入单板
INSERT VERTEX board(name, slot_id) VALUES "board_001":("主控板", 1);
INSERT VERTEX board(name, slot_id) VALUES "board_002":("业务板A", 2);

-- 插入端口
INSERT VERTEX port(name, speed, status) VALUES "port_001":("万兆光口1", "10G", "up");
INSERT VERTEX port(name, speed, status) VALUES "port_002":("万兆光口2", "10G", "down");

-- ============================================
-- 边插入示例 - 单行格式
-- ============================================

-- 告警间 trigger 关系
INSERT EDGE trigger(relation_type, weight) VALUES "alarm_001" -> "alarm_002":("derived", 0.9);

-- 设备父子关系 (leave)
INSERT EDGE leave() VALUES "ne_001" -> "board_001":();
INSERT EDGE leave() VALUES "board_001" -> "port_001":();
INSERT EDGE leave() VALUES "ne_002" -> "board_002":();
INSERT EDGE leave() VALUES "board_002" -> "port_002":();

-- 设备间连接 (link)
INSERT EDGE link(bandwidth, media_type) VALUES "port_001" -> "port_002":("10G", "fiber");

-- 告警到直接故障设备 (happen)
INSERT EDGE happen(reason, is_root) VALUES "alarm_001" -> "port_001":("光纤断裂", 1);
INSERT EDGE happen(reason, is_root) VALUES "alarm_002" -> "port_002":("端口损坏", 1);
INSERT EDGE happen() VALUES "alarm_003" -> "port_001":();
INSERT EDGE happen() VALUES "alarm_003" -> "board_001":();

-- 告警到子设备 (enhance)
INSERT EDGE enhance(impact_level) VALUES "alarm_001" -> "board_001":(2);
INSERT EDGE enhance(impact_level) VALUES "alarm_002" -> "board_002":(2);

-- ============================================
-- 常用查询语句
-- ============================================

-- 查看所有空间
SHOW SPACES;

-- 查看当前空间的 Tag
SHOW TAGS;

-- 查看当前空间的 Edge Type
SHOW EDGES;

-- 查询所有告警
MATCH (a:alarm) RETURN id(a), a.alarm.name, a.alarm.level, a.alarm.content;

-- 查询告警的触发关联 (trigger)
MATCH (a1:alarm)-[:trigger]->(a2:alarm) RETURN id(a1), a1.alarm.name AS source, id(a2), a2.alarm.name AS target;

-- 查询告警的根因设备 (happen)
MATCH (a:alarm)-[:happen]->(d) RETURN id(a), a.alarm.name AS alarm, id(d), d.port.name AS device;

-- 查询设备的父子关系 (leave) - 需要分别查询不同类型
-- 网元 -> 单板
MATCH (parent:ne)-[:leave]->(child:board) RETURN id(parent), parent.ne.name AS parent, id(child), child.board.name AS child;
-- 单板 -> 端口
MATCH (parent:board)-[:leave]->(child:port) RETURN id(parent), parent.board.name AS parent, id(child), child.port.name AS child;

-- 查询设备间的连接 (link)
MATCH (d1:port)-[:link]->(d2:port) RETURN id(d1), d1.port.name AS source, id(d2), d2.port.name AS target;

-- 单网元多告警故障组查询 (leave 边方向: parent -> child，所以 port<-leave-board<-leave-ne)
MATCH (a:alarm)-[:happen]->(p:port)<-[:leave]-(b:board)<-[:leave]-(n:ne) WITH n, collect(a) AS alarms WHERE size(alarms) >= 2 RETURN n.ne.name AS ne_name, size(alarms) AS alarm_count;

-- 统计各类型节点数量
MATCH (n:ne) RETURN count(n) AS ne_count;
MATCH (b:board) RETURN count(b) AS board_count;
MATCH (p:port) RETURN count(p) AS port_count;
MATCH (a:alarm) RETURN count(a) AS alarm_count;

-- 统计各级别告警数量
MATCH (a:alarm) RETURN a.alarm.level AS level, count(a) AS count ORDER BY count DESC;

-- 统计每个网元的告警数量 (leave 边方向: parent -> child，所以 port<-leave-board<-leave-ne)
MATCH (a:alarm)-[:happen]->(p:port)<-[:leave]-(b:board)<-[:leave]-(n:ne) RETURN n.ne.name AS ne_name, count(a) AS alarm_count ORDER BY alarm_count DESC;