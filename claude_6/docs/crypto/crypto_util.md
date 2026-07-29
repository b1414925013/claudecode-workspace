# CryptoUtil 对称加密

`pyhutool.crypto.CryptoUtil` 对齐 Hutool `cn.hutool.crypto.symmetric` 包下的
`AES` / `DES` / `DESede`，基于 [cryptography](https://cryptography.io) 提供
对称加解密。

## 安装

```bash
pip install "pyhutool[crypto]"
```

未安装 `cryptography` 时调用任何方法都会抛 `UtilError` 提示安装。

## 快速开始

```python
import os
from pyhutool.crypto import CryptoUtil

key = os.urandom(32)               # AES-256
ciphertext = CryptoUtil.aes_encrypt(key, b"hello")
# 返回值 = IV(16) + 密文，便于一次性打包
plain = CryptoUtil.aes_decrypt(key, ciphertext)
assert plain == b"hello"
```

## 分组模式

默认 `CBC` + PKCS7 填充，也支持 `ECB` / `CFB` / `OFB` / `CTR`：

```python
# CBC + 显式 IV（返回值仅密文）
iv = os.urandom(16)
ct = CryptoUtil.aes_encrypt(key, b"data", iv=iv)
plain = CryptoUtil.aes_decrypt(key, ct, iv=iv)

# ECB（不需要 IV，但 ECB 不安全，仅兼容旧系统）
ct = CryptoUtil.aes_encrypt(key, b"16-byte message!", mode="ECB")

# CFB / OFB / CTR（流密码模式，仍走 PKCS7）
ct = CryptoUtil.aes_encrypt(key, b"data", iv=iv, mode="CFB")
```

| 模式 | 是否需要 IV | 自动 IV 时返回值 |
|------|------------|------------------|
| CBC  | 是 | `iv + 密文` |
| ECB  | 否 | 仅密文 |
| CFB  | 是 | `iv + 密文` |
| OFB  | 是 | `iv + 密文` |
| CTR  | 是 | `iv + 密文` |

## 通用接口

```python
# 通过 algorithm 参数选择算法
CryptoUtil.encrypt("AES", key, data)
CryptoUtil.encrypt("TripleDES", key3, data)
CryptoUtil.decrypt("AES", key, ciphertext)
```

## 便捷方法

```python
# AES
CryptoUtil.aes_encrypt(key, data, iv=iv, mode="CBC")
CryptoUtil.aes_decrypt(key, data, iv=iv)

# DES（已弃用，内部等价于 TripleDES(KKK)）
CryptoUtil.des_encrypt(key8, data)
CryptoUtil.des_decrypt(key8, data)

# TripleDES / 3DES / DESede
CryptoUtil.des3_encrypt(key24, data)
CryptoUtil.des3_decrypt(key24, data)
```

## 密钥与 IV 生成

```python
CryptoUtil.gen_key("AES", 256)         # 32 字节
CryptoUtil.gen_key("DES", 64)          # 8 字节
CryptoUtil.gen_key("TripleDES", 192)   # 24 字节
CryptoUtil.gen_iv()                    # 16 字节（AES）
CryptoUtil.gen_iv(8)                   # 8 字节（DES/3DES）
```

## 关于 DES 的兼容性说明

`cryptography` 39.0 起弃用、44.0 起彻底移除了 `algorithms.DES`，因为单 DES
已不安全。pyhutool 为保持 Hutool API 对齐，仍提供 `des_encrypt` /
`des_decrypt`，但内部把 8 字节 DES 密钥扩展为 `KKK`（24 字节）后调用
`TripleDES`，数学上与单 DES 等价。

## 与 Hutool 的差异

| 方面 | Hutool (Java) | pyhutool (Python) |
|------|---------------|-------------------|
| 底层 | BouncyCastle | `cryptography` |
| IV 自动生成 | 否（用户传入） | 是（默认随机生成并拼接到密文前） |
| DES | 原生支持 | 用 TripleDES(KKK) 等价模拟 |
| 模式 | CBC/ECB/CFB/OFB/CTR | 同 |
| 依赖 | 内置 | `cryptography` (extras) |
