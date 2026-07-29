# DigestUtil 摘要与 HMAC

`pyhutool.crypto.DigestUtil` 对齐 Hutool `cn.hutool.crypto.digest.DigestUtil`，
提供 MD5 / SHA-1 / SHA-256 / SHA-512 摘要与 HMAC-MD5 / HMAC-SHA1 /
HMAC-SHA256 / HMAC-SHA512 消息认证码。

## 特性

- **零外部依赖**：基于标准库 `hashlib` + `hmac`，无需安装 `cryptography`；
- 输入 `data` 既可以是 `bytes` 也可以是 `str`（按 UTF-8 编码）；
- `*_hex` 系列返回小写十六进制字符串；
- 算法名大小写不敏感，自动把 `SHA-256` 规整为 `sha256`。

## 摘要

```python
from pyhutool.crypto import DigestUtil

# 便捷方法
DigestUtil.md5_hex("abc")          # 900150983cd24fb0d6963f7d28e17f72
DigestUtil.sha1_hex("abc")         # a9993e364706816aba3e25717850c26c9cd0d89d
DigestUtil.sha256_hex("abc")
DigestUtil.sha512_hex("abc")

# 字节返回
DigestUtil.md5("abc")              # b'\x90\x01P...'
DigestUtil.sha256(b"abc")          # 32 字节

# 通用接口
DigestUtil.digest_hex("sha256", "abc")
DigestUtil.digest("SHA-256", b"abc")
```

## HMAC

```python
DigestUtil.hmac_md5_hex(b"secret", b"hello")
DigestUtil.hmac_sha256_hex("secret", "hello")  # str key/data 走 UTF-8
DigestUtil.hmac_sha512_hex(b"k", b"d")

# 通用接口
DigestUtil.hmac_hex("sha256", b"key", b"data")
```

## 文件摘要

按 64KiB 分块读取，避免一次性把大文件读入内存：

```python
DigestUtil.md5_file_hex("large.iso")
DigestUtil.sha256_file_hex("/path/to/file")
DigestUtil.digest_file_hex("sha1", "data.bin")
```

## 与 Hutool 的差异

| 方面 | Hutool (Java) | pyhutool (Python) |
|------|---------------|-------------------|
| 底层 | BouncyCastle | `hashlib` + `hmac` |
| 文件流式 | 是 | 是（64KiB 分块） |
| 算法大小写 | 严格 | 大小写不敏感 |
| 依赖 | 内置 | 标准库（无需 cryptography） |
