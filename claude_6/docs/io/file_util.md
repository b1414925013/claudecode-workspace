# FileUtil 文件工具

`pyhutool.io.FileUtil` 对齐 Hutool `cn.hutool.core.io.FileUtil`，
`AsyncFileUtil` 为异步等价版。所有路径参数均接受 `str | os.PathLike | pathlib.Path`。

## 基础信息

```python
from pyhutool.io import FileUtil

FileUtil.exists("/path/to/file")
FileUtil.is_file("/path/to/file")
FileUtil.is_directory("/path/to/dir")
FileUtil.size("/path/to/file")          # 字节数
FileUtil.get_temp_dir()                  # 系统临时目录
FileUtil.get_user_home()                 # 用户主目录
```

## 读

```python
FileUtil.read_utf8("a.txt")              # UTF-8 字符串
FileUtil.read_string("a.txt", "gbk")     # 指定字符集
FileUtil.read_bytes("a.bin")             # bytes
FileUtil.read_lines("a.txt")             # list[str]，去行尾换行
```

## 写

```python
FileUtil.write_utf8("hello", "a.txt")            # 覆盖
FileUtil.write_utf8("!", "a.txt", append=True)   # 追加
FileUtil.append_utf8("!", "a.txt")               # 等价于 append=True
FileUtil.write_bytes(b"\xff", "a.bin")
FileUtil.write_lines(["a", "b"], "a.txt")         # 自动追加 \n
```

写入会自动创建父目录。

## 创建 / 删除

```python
FileUtil.touch("a.txt")           # 创建空文件（含父目录），已存在则更新 mtime
FileUtil.mkdir("a/b/c")            # 递归创建目录，幂等

FileUtil.del_("a.txt")             # 删除文件，返回是否删除；不存在返回 False
FileUtil.del_("some_dir")         # 递归删除目录
FileUtil.clean("some_dir")         # 清空目录内容（保留目录本身），返回删除项数
```

## 复制 / 移动

```python
FileUtil.copy("src.txt", "dst.txt")               # 文件
FileUtil.copy("src.txt", "existing_dir/")         # 拷入目录下并保留原名
FileUtil.copy("src_dir", "dst_dir", replace_existing=True)

FileUtil.move("src.txt", "dst.txt")
FileUtil.rename("a.txt", "b.txt")                  # 仅改名，保留父目录
```

`replace_existing=False` 时若目标存在抛 `UtilError`。

## 列举

```python
FileUtil.list_files("some_dir")                 # list[Path]，不含子目录
FileUtil.list_files("some_dir", recursive=True)
FileUtil.list_dirs("some_dir")                  # 仅子目录
```

## 异步版

```python
from pyhutool.io import AsyncFileUtil

content = await AsyncFileUtil.read_utf8("a.txt")
await AsyncFileUtil.write_utf8("hello", "a.txt")
await AsyncFileUtil.touch("a.txt")
await AsyncFileUtil.copy("src.txt", "dst.txt")
await AsyncFileUtil.move("src.txt", "dst.txt")
files = await AsyncFileUtil.list_files("dir")
```

异步实现通过 `asyncio.to_thread` 在线程池中执行阻塞 I/O。
