# RegexUtil 正则工具

`pyhutool.core.RegexUtil` 对齐 Hutool `cn.hutool.core.util.ReUtil`。

!!! note "匹配语义"
    `is_match` 要求**完全匹配**（对应 Java `Pattern.matches`）；
    `is_contains` 用于搜索匹配。

## 匹配

```python
RegexUtil.is_match(r"\d+", "12345")   # True（完全匹配）
RegexUtil.is_match(r"\d+", "12a45")   # False
RegexUtil.is_contains(r"\d+", "ab12")  # True
```

## 查找

```python
RegexUtil.find_first(r"\d+", "ab12cd34")   # "12"
RegexUtil.find_group(r"(\d+)-(\d+)", "12-34", 1)  # "12"
RegexUtil.find_all(r"\d+", "a1b22c333")    # ["1", "22", "333"]
RegexUtil.find_all_group(r"(\d+)-(\d+)", "1-2 and 3-4", 1)  # ["1", "3"]
```

## 提取

```python
RegexUtil.extract(r"user:(\w+)", "user:tom")   # "tom"
RegexUtil.extract_all(r"id=(\d+)", "id=1,id=2")  # ["1", "2"]
```

## 替换 / 删除

```python
RegexUtil.replace_all(r"\d+", "a1b2", "X")    # "aXbX"
RegexUtil.replace_first(r"\d+", "a1b2", "X")  # "aXb2"
RegexUtil.del_first(r"\d+", "a1b2")            # "ab2"
RegexUtil.del_all(r"\d+", "a1b2")              # "ab"
```

## 计数 / 分割

```python
RegexUtil.count(r"\d", "a1b2c3")      # 3
RegexUtil.split(r"[,\s]+", "a, b c")  # ["a", "b", "c"]
```

## 回调替换

```python
RegexUtil.replace_func(r"\d+", "a1b2", lambda m: str(int(m.group()) * 2))
# "a2b4"
```

所有方法同时接受预编译的 `re.Pattern` 对象。
