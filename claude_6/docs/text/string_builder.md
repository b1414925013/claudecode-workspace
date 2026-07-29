# StringBuilder 字符串构建器

`pyhutool.text.StringBuilder` 对齐 Hutool `cn.hutool.core.text.StrBuilder`。
Python 字符串本身不可变，本类提供链式 API 与可变语义，便于从 Java 迁移或对
字符串进行多次插入/删除操作。底层用 `list[str]` 累积片段，`to_string` 时一次
`join`，避免 O(n²) 拷贝。

## 创建

```python
from pyhutool.text import StringBuilder

sb = StringBuilder()                # 空
sb = StringBuilder("hello")         # 初始字符串
sb = StringBuilder(["a", "b"])      # 从可迭代对象构造
```

## 链式追加

```python
sb = StringBuilder("Hello")
sb.append(", ").append("World").append_line("!")
# "Hello, World!\n"

sb.append_lines(["a", "b"])
# 在末尾追加 "a\nb\n"
```

## 插入 / 删除 / 替换

```python
sb = StringBuilder("HelloWorld")
sb.insert(5, ", ")                  # "Hello, World"
sb.delete(5, 7)                     # "HelloWorld"
sb.delete_char_at(0)                # "elloWorld"
sb.replace(0, 5, "Hi")              # "HiWorld"
sb.reverse()                        # "dlroWiH"
sb.clear()                          # ""
```

`insert` 支持负数索引（与 Python 切片语义一致）。

## 查询

```python
sb = StringBuilder("Hello, World")
sb.length()                # 12
len(sb)                    # 12  __len__
sb.char_at(0)              # "H"
sb.index_of("World")       # 7
sb.index_of("xyz")         # -1
sb.is_empty()              # False
```

## 输出与比较

```python
sb.to_string()
str(sb)                    # 等价 to_string
sb == "Hello, World"       # 与字符串比较
sb == other_sb              # 与另一 StringBuilder 比较
repr(sb)                    # "StringBuilder('Hello, World')"
list(sb)                    # 按字符迭代
```
