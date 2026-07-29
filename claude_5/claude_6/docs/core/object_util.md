# ObjectUtil 对象工具

`pyhutool.core.ObjectUtil` 对齐 Hutool `cn.hutool.core.util.ObjectUtil`。

## null 判断与默认值

```python
ObjectUtil.is_null(None)                  # True
ObjectUtil.is_not_null(0)                # True
ObjectUtil.default_if_null(None, "x")     # "x"
```

## 判等与哈希

```python
ObjectUtil.equal("a", "a")      # True
ObjectUtil.equal(None, None)    # True
ObjectUtil.hash_code(None)      # 0
ObjectUtil.to_string(None)     # ""
```

## 空判断

```python
ObjectUtil.is_empty(None)     # True
ObjectUtil.is_empty("")       # True
ObjectUtil.is_empty([])       # True
ObjectUtil.is_empty({})       # True
ObjectUtil.is_empty(0)        # False  ← 非容器视为非空
```

## 基础类型与克隆

```python
ObjectUtil.is_basic_type(1)       # True
ObjectUtil.is_basic_type([1])     # False

obj = {"a": [1, 2, 3]}
cloned = ObjectUtil.clone(obj)    # 深拷贝
```
