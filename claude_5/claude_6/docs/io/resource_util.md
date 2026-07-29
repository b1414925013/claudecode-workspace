# ResourceUtil 资源加载

`pyhutool.io.ResourceUtil` 对齐 Hutool `cn.hutool.core.io.resource.ResourceUtil`。

与 Java 不同，Python 没有内置 ``classpath:`` 概念，``ResourceUtil`` 通过
``importlib.resources`` 以**包名 + 相对资源路径**方式定位资源。这让行为可移植，
且不依赖 ``__file__``。

## 读字符串

```python
from pyhutool.io import ResourceUtil

text = ResourceUtil.read_string("pyhutool.core", "messages/zh.txt")
# 等价于 Hutool: ResourceUtil.readUtf8Str("messages/zh.txt")
```

## 读字节

```python
payload = ResourceUtil.read_bytes("pyhutool.core", "data.bin")
```

## 判断存在

```python
ResourceUtil.exists("pyhutool.core", "messages/zh.txt")
```

## 获取资源 URL

```python
url = ResourceUtil.get_resource_url("pyhutool.core", "messages/zh.txt")
# 形如 "file:///.../messages/zh.txt"
```

资源位于 ZIP / wheel 内部时仍可正确解析（``importlib`` 会临时解包到本地）。

## 与 Hutool 的差异

| 方面 | Hutool (Java) | pyhutool (Python) |
|------|---------------|-------------------|
| 入参 | 单一 ``path`` | ``package`` + ``resource`` 两段式 |
| 解析 | 通过当前 ``ClassLoader`` | 通过 ``importlib.resources`` |
| 字符集 | 默认 UTF-8 | 默认 UTF-8，可显式指定 |
