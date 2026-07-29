# UnicodeUtil Unicode 转义

`pyhutool.text.UnicodeUtil` 对齐 Hutool `cn.hutool.core.util.UnicodeUtil`，
提供 `\uXXXX` 转义形式与原字符串之间的双向转换。

## 转义

```python
from pyhutool.text import UnicodeUtil

UnicodeUtil.to_unicode("你好")          # "\\u4f60\\u597d"
UnicodeUtil.to_unicode("Hello, World!")  # ASCII 保持原样
UnicodeUtil.to_unicode("a你b")            # "a\\u4f60b"
UnicodeUtil.to_unicode(None)             # ""
```

BMP 之外字符（如 emoji）自动使用代理对：

```python
UnicodeUtil.to_unicode("😀")
# "\\ud83d\\ude00"
```

`escape` 是 `to_unicode` 的别名。

## 解码

```python
UnicodeUtil.to_string("\\u4f60\\u597d")  # "你好"
UnicodeUtil.to_string("Hello")            # 无转义序列，原样返回
UnicodeUtil.to_string("\\u12")            # 不完整转义，原样返回 "\\u12"
UnicodeUtil.to_string(None)              # ""
```

`unescape` 是 `to_string` 的别名。

## 往返转换

```python
original = "Hello, 你好，😀 emoji"
assert UnicodeUtil.to_string(UnicodeUtil.to_unicode(original)) == original
```

## 与 Hutool 的差异

| 方面 | Hutool (Java) | pyhutool (Python) |
|------|---------------|-------------------|
| 实现机制 | char 数组遍历 | 按码点遍历，BMP+ 代理对 |
| 大小写 | 输出大写 ``\\uXXXX`` | 输出小写 ``\\uXXXX`` |
| 解码容错 | 严格匹配 | 长度不足的转义原样返回 |
