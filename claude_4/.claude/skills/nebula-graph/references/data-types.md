# NebulaGraph 数据类型详解

## 数值类型

| 类型 | 说明 |
|------|------|
| INT | 64位整数 |
| INT8/16/32 | 8/16/32位整数 |
| FLOAT/DOUBLE | 浮点数 |
| TIMESTAMP | 时间戳 |

**注意**：
- nGQL 不支持 INT8 作为 VID 类型
- 支持十进制(123)、十六进制(0x1e240)、八进制(0361100)
- FLOAT 插入 INT 会四舍五入

---

## 字符串类型

```ngql
STRING          -- 变长字符串
FIXED_STRING(N) -- 定长字符串，N 为长度

-- 超过定长会截断（属性）或报错（VID）
```

---

## 布尔类型

```ngql
BOOL -- true 或 false
```

---

## NULL 处理

```ngql
RETURN null IS NULL, null == null, null != null;
-- 结果: true, __NULL__, __NULL__
```

---

## 比较符与逻辑运算

### 比较符
```ngql
==, !=, >, <, >=, <=
IS [NOT] NULL

-- 注意：nGQL 用 == 而不是 =
```

### 逻辑运算
```ngql
AND, OR, NOT

WHERE v.age > 30 AND v.name != "Tim"
WHERE v.name == "A" OR v.name == "B"
```