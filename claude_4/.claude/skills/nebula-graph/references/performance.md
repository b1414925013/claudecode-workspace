# NebulaGraph 查询性能分析

## EXPLAIN / PROFILE

```ngql
EXPLAIN format="row" <query>;
PROFILE format="row" <query>;
```

输出说明：
- **id**: operator ID
- **name**: operator 名称
- **dependencies**: 依赖的 operator
- **profiling data**: execTime, totalTime, rows

---

## 性能优化建议

1. 使用索引加速 LOOKUP
2. 避免全表扫描，使用 WHERE 条件
3. 合理使用 LIMIT 限制结果集
4. 使用管道符优化子查询

---

## 常见错误处理

### VID 类型不匹配
```
原因: VID 类型与写入值不匹配
解决: 检查 SPACE 的 vid_type 设置
```

### Tag/Edge type 不存在
```
原因: 使用前未创建 Tag/Edge type
解决: 先 CREATE TAG 或 CREATE EDGE
```

### 属性值类型错误
```
原因: 写入值类型与 Schema 定义不符
解决: 检查属性类型定义
```

### Syntax error
```
原因: nGQL 语法与 openCypher 混淆
解决:
  - 相等用 == 不是 =
  - 幂运算用 pow(x, y) 不是 ^
  - 边有 @rank 概念
  - 有强 Schema 要求
```