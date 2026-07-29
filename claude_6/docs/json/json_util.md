# JsonUtil JSON 工具

`pyhutool.json.JsonUtil` 对齐 Hutool `cn.hutool.json.JSONUtil`，底层基于
[orjson](https://github.com/ijl/orjson) 实现高性能序列化/反序列化。

## 安装

```bash
pip install "pyhutool[json]"
```

未安装 ``orjson`` 时调用任何方法都会抛 ``UtilError`` 提示安装。

## 解析

```python
from pyhutool.json import JsonUtil

JsonUtil.parse('{"a": 1, "b": [1, 2]}')   # {"a": 1, "b": [1, 2]}
JsonUtil.parse_obj('{"a": 1}')             # {"a": 1}（非对象抛错）
JsonUtil.parse_array('[1, 2, 3]')           # [1, 2, 3]（非数组抛错）
```

支持 ``str`` / ``bytes`` 输入；中文不转义。

## 序列化

```python
JsonUtil.to_json_str({"name": "张三", "age": 30})
# '{"name":"张三","age":30}'   ← 默认中文不转义

JsonUtil.to_json_str({"b": 1, "a": 2}, indent=2, sort_keys=True)
# 带 2 空格缩进且按键名排序

JsonUtil.pretty_format('{"a":1,"b":[1,2]}')   # 美化已存在的 JSON 字符串
```

`datetime`、`Decimal`、`dataclass` 等类型 orjson 原生支持；自定义类退化为
其 `__dict__`。

## 文件读写

```python
JsonUtil.write_json_file({"name": "alice"}, "user.json")
JsonUtil.write_json_file(data, "data.json", indent=2)
JsonUtil.write_json_file({"b": 2}, "data.json", append=True)  # 追加

obj = JsonUtil.read_json_file("user.json")
```

文件 I/O 委托给 `pyhutool.io.FileUtil`，自动创建父目录、统一异常包装。

## 类型判断

```python
JsonUtil.is_json('{"a": 1}')        # True
JsonUtil.is_json("[1, 2]")          # True
JsonUtil.is_json("42")              # False  ← 标量不算
JsonUtil.is_json_object('{"a": 1}')  # True
JsonUtil.is_json_array("[1, 2]")    # True
```

## 转义

```python
JsonUtil.escape('hello "world"\n')     # 'hello \\"world"\\n'
JsonUtil.unescape('hello \\"world\\"') # 'hello "world"'
JsonUtil.quote("hello")                # '"hello"'
JsonUtil.quote(None)                  # 'null'
```

转义覆盖：``"`` ``\\`` ``\n`` ``\r`` ``\t`` ``\b`` ``\f`` 以及 0x00–0x1F
控制字符（``\\uXXXX`` 形式）。

## 与 Hutool 的差异

| 方面 | Hutool (Java) | pyhutool (Python) |
|------|---------------|-------------------|
| 解析结果 | ``JSONObject``/``JSONArray`` 包装 | 直接返回 ``dict``/``list`` |
| 中文转义 | 可选 | 默认不转义（与 orjson 一致） |
| 缩进参数 | 任意数字 | 仅 ``2``（orjson 限制） |
| 类型支持 | 自定义 ``JSONBeanParser`` | orjson 原生 + ``__dict__`` 退化 |
| 依赖 | 内置 | ``orjson`` (extras) |
