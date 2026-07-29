# RandomUtil 随机工具

`pyhutool.core.RandomUtil` 对齐 Hutool `cn.hutool.core.util.RandomUtil`。

!!! note "实现差异"
    Hutool 使用 `ThreadLocalRandom`，pyhutool 使用 Python `random` 模块。
    `seed()` 返回独立 `random.Random` 实例，避免污染全局随机状态。

## 随机数

```python
RandomUtil.random_int(1, 10)        # [1, 10) 整数
RandomUtil.random_int_with_range(1, 3)  # [1, 3] 闭区间
RandomUtil.random_double(0, 1)      # [0, 1) 浮点
RandomUtil.random_boolean()         # True/False
RandomUtil.random_char("ABC")       # "A"/"B"/"C"
```

## 随机元素

```python
seq = ["a", "b", "c"]
RandomUtil.random_ele(seq)              # 随机一个
RandomUtil.random_els(seq, 5)          # 5 个（可重复）
RandomUtil.random_els_distinct(seq, 2) # 2 个（不重复）
```

## 随机字符串

```python
RandomUtil.random_string(10)         # 字母+数字
RandomUtil.random_lower_string(10)   # 小写字母+数字
RandomUtil.random_upper_string(10)   # 大写字母+数字
RandomUtil.random_numbers(8)         # 纯数字
```

## 可复现随机

```python
r1 = RandomUtil.seed(42)
r2 = RandomUtil.seed(42)
assert r1.randint(0, 1000) == r2.randint(0, 1000)
```
