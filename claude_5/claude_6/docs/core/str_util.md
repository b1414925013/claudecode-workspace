# StrUtil 字符串工具

`pyhutool.core.StrUtil` 对齐 Hutool `cn.hutool.core.util.StrUtil`。

## 空值判断

```python
StrUtil.is_blank(None)        # True
StrUtil.is_blank("   ")       # True
StrUtil.is_empty(" ")         # False  ← 与 is_blank 的区别
```

## 空值替换

```python
StrUtil.blank_to_default("", "x")      # "x"
StrUtil.empty_to_default(None, "x")    # "x"
StrUtil.null_to_default(None, "x")     # "x"
```

## 占位符格式化

```python
StrUtil.format("hello {}", "world")            # "hello world"
StrUtil.format("{}-{}", 1, 2)                  # "1-2"
StrUtil.format_with("a=?-b=?", "?", 1, 2)      # "a=1-b=2"
```

## 截取与前后缀

```python
StrUtil.sub_pre("hello", 3)              # "hel"
StrUtil.sub_suf("hello", 3)              # "llo"
StrUtil.remove_prefix("helloWorld", "hello")   # "World"
StrUtil.remove_suffix("a.txt", ".txt")         # "a"
StrUtil.remove_prefix_ignore_case("Hello", "hello")  # ""
```

## 大小写与命名转换

```python
StrUtil.upper_first("hello")              # "Hello"
StrUtil.lower_first("Hello")              # "hello"
StrUtil.to_underline_case("camelCase")    # "camel_case"
StrUtil.to_underline_case("HTTPSConnection")  # "https_connection"
StrUtil.to_camel_case("user_id")          # "userId"
```

## 比较与查找

```python
StrUtil.equals(None, None)                # True
StrUtil.equals_ignore_case("ABC", "abc")  # True
StrUtil.contains_ignore_case("Hello", "ELL")  # True
StrUtil.startswith(None, "x")            # False
```

## 重复 / 反转 / 裁剪

```python
StrUtil.repeat("ab", 3)        # "ababab"
StrUtil.reverse("hello")       # "olleh"
StrUtil.trim("  hi  ")         # "hi"
StrUtil.clean_blank("  h e ")  # "he"
```

## 填充

```python
StrUtil.fill("ab", "0", 5)                   # "ab000"
StrUtil.fill("ab", "0", 5, is_prefix=True)   # "000ab"
```

## 字符类别

```python
StrUtil.is_numeric("-1.5")   # True
StrUtil.is_alpha("abc")      # True
StrUtil.is_upper("ABC")      # True
```

## 拼接 / 分割

```python
StrUtil.concat("a", None, "b")          # "ab"
StrUtil.split("a,b,c", ",")              # ["a", "b", "c"]
StrUtil.split("a,b,c", ",", 2)           # ["a", "b,c"]
StrUtil.join(["a", None, "b"], "-")      # "a--b"
```

## UUID

```python
StrUtil.uuid()            # "xxxxxxxx-xxxx-4xxx-..."
StrUtil.uuid(bare=True)   # 32 位无连字符
```
