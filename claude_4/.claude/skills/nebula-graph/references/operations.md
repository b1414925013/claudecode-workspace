# NebulaGraph 运维命令

## BALANCE

```ngql
BALANCE DATA;                    -- 均衡数据
BALANCE DATA ZONE;               -- 跨 Zone 均衡
SHOW BALANCE RESULT;             -- 查看进度
BALANCE STOP;                    -- 停止均衡
```

---

## JOB 管理

```ngql
SUBMIT JOB COMPACT;              -- 触发 Compaction
SUBMIT JOB FLUSH;                -- 刷新内存
SUBMIT JOB STATS;                -- 更新统计信息
SHOW JOB <job_id>;               -- 查看 JOB 状态
```

---

## 存储相关

```ngql
SHOW HOSTS;                      -- 查看存储主机
SHOW PARTS;                      -- 查看分片
SHOW SERVICES;                   -- 查看服务状态
```

---

## Compaction

```ngql
-- 全量 Compaction（会阻塞读写）
SUBMIT JOB COMPACT;

-- 查看 Compaction 状态
SHOW JOB <compaction_job_id>;

-- Compaction 日志位置
-- /usr/local/nebula/data/storage/nebula/{space}/data/LOG
```