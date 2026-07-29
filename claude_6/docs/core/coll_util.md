# CollUtil 集合工具

`pyhutool.core.CollUtil` 对齐 Hutool `cn.hutool.core.util.CollUtil`。

!!! note "与 Hutool 的差异"
    Python 内置 `list` / `set` / `dict` 已是首选容器，本工具不再提供 `newArrayList`，
    而聚焦容器之上的通用操作。

## 空判断 / 大小

```python
CollUtil.is_empty([])       # True
CollUtil.is_empty(None)     # True
CollUtil.size([1, 2, 3])   # 3
```

## 查找

```python
CollUtil.contains([1, 2, 3], 2)   # True
CollUtil.first([1, 2, 3])         # 1
CollUtil.last([1, 2, 3])          # 3
CollUtil.first([], default="x")   # "x"
```

## 变换

```python
CollUtil.reverse([1, 2, 3])                    # [3, 2, 1]
CollUtil.sort([3, 1, 2])                        # [1, 2, 3]
CollUtil.sort(["b", "a"])                       # ["a", "b"]
CollUtil.distinct([1, 2, 2, 3, 1])              # [1, 2, 3]
CollUtil.filter_([1, 2, 3, 4], lambda x: x % 2 == 0)  # [2, 4]
CollUtil.map_([1, 2, 3], lambda x: x * 2)       # [2, 4, 6]
CollUtil.flat_map([[1, 2], [3, 4]])             # [1, 2, 3, 4]
CollUtil.count([1, 2, 3], lambda x: x > 1)      # 2
```

!!! note "方法别名"
    `filter_` / `map_` / `zip_` 带下划线后缀，避免遮蔽 Python 内置 `filter` / `map` / `zip`。

## 分组 / 分页 / zip

```python
CollUtil.group_by([1, 2, 3, 4, 5], lambda x: x % 2)
# {0: [2, 4], 1: [1, 3, 5]}

CollUtil.page([1, 2, 3, 4, 5], 2, 2)   # [3, 4]  （1-based 页码）
CollUtil.zip_([1, 2, 3], ["a", "b"])   # [(1, "a"), (2, "b")]
CollUtil.join([1, 2, 3], "-")          # "1-2-3"
```

## 极值

```python
CollUtil.max([3, 1, 2])   # 3
CollUtil.min([3, 1, 2])   # 1
CollUtil.max([])          # None
```

## 集合运算

```python
CollUtil.union([1, 2, 3], [2, 3, 4])      # [1, 2, 3, 4]
CollUtil.intersect([1, 2, 3], [2, 3, 4])  # [2, 3]
CollUtil.subtract([1, 2, 3], [2])          # [1, 3]
```
