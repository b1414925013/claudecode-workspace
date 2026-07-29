# IoUtil 流工具

`pyhutool.io.IoUtil` 对齐 Hutool `cn.hutool.core.io.IoUtil`，
`AsyncIoUtil` 为异步等价版。

## 拷贝流

```python
import io
from pyhutool.io import IoUtil

src = io.BytesIO(b"hello")
dst = io.BytesIO()
n = IoUtil.copy(src, dst)   # 5
dst.getvalue()               # b"hello"

# 字符流
IoUtil.copy_reader(io.StringIO("hi"), io.StringIO())
```

## 读取

```python
IoUtil.read_bytes(io.BytesIO(b"abc"))            # b"abc"
IoUtil.read_utf8(io.BytesIO("你好".encode()))     # "你好"
IoUtil.read_lines(io.StringIO("a\nb\n"))          # ["a", "b"]
```

## 写入

```python
dst = io.BytesIO()
IoUtil.write(dst, "你好")               # 写入 UTF-8 字节，返回 6
IoUtil.write(dst, b"\x00", charset="ascii")

IoUtil.write_lines(io.StringIO(), ["a", "b"])   # 2
```

## 关闭与刷新

```python
IoUtil.close(None)              # 静默跳过
IoUtil.close(some_stream)       # 异常被吞掉，等价 Hutool closeQuietly
IoUtil.flush(stream)
```

## 对象序列化（pickle）

```python
buf = io.BytesIO()
IoUtil.write_obj(buf, {"a": 1})
buf.seek(0)
obj = IoUtil.read_obj(buf)     # {"a": 1}
```

!!! warning "安全提示"
    `read_obj` 内部使用 `pickle`，反序列化等价于执行任意代码，仅用于受信任数据。

## 异步版

```python
from pyhutool.io import AsyncIoUtil

n = await AsyncIoUtil.copy(src, dst)
text = await AsyncIoUtil.read_utf8(stream)
await AsyncIoUtil.write_lines(dst, ["a", "b"])
await AsyncIoUtil.close(stream)
```

异步实现通过 `asyncio.to_thread` 在线程池中执行阻塞 I/O，足以应对大多数文件场景；
如需更高吞吐可后续提供基于 `aiofiles` 的扩展。
