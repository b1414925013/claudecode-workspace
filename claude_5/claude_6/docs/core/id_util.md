# IdUtil ID 生成工具

`pyhutool.core.IdUtil` 对齐 Hutool `cn.hutool.core.util.IdUtil`。

## UUID

```python
IdUtil.random_uuid()    # "xxxxxxxx-xxxx-4xxx-..." （36 位带连字符）
IdUtil.simple_uuid()    # 32 位无连字符（Hutool simpleUUID）
IdUtil.fast_uuid()      # 32 位无连字符（Hutool fastUUID）
IdUtil.ordered_uuid()   # UUIDv1，可排序
```

## ObjectId（MongoDB 风格）

```python
IdUtil.object_id()   # 24 位十六进制
# 结构：4 字节时间戳 + 5 字节随机 + 3 字节自增计数器
```

## NanoId

```python
IdUtil.nano_id()         # 默认 21 位，URL 安全
IdUtil.nano_id(10)       # 自定义长度
```

## 雪花 ID（简化版）

```python
IdUtil.snowflake_id(worker_id=0, data_center_id=0)
# 64 位整数：1 符号 + 41 时间戳 + 5 dataCenter + 5 worker + 12 序列号
# 单机内线程安全
```
