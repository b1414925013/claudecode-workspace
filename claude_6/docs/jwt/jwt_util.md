# JWTUtil / JWT 签发与验证

`pyhutool.jwt` 对齐 Hutool `cn.hutool.jwt`，基于
[PyJWT](https://pyjwt.readthedocs.io) 提供 JWT 签发、解析、验签能力。

## 安装

```bash
pip install "pyhutool[jwt]"
```

未安装 `pyjwt` 时调用任何方法都会抛 `UtilError` 提示安装。

## 快速签发

builder 模式（链式 setter，对齐 Hutool `JWT`）：

```python
from pyhutool.jwt import JWTUtil

token = (
    JWTUtil.create()
    .set_issuer("pyhutool")
    .set_subject("user-1")
    .set_audience("my-app")
    .set_expires_at(1735689600)         # Unix 时间戳
    .set_key(b"super-secret-key-at-least-32-bytes!!")
    .sign()
)
# 'xxxxx.yyyyy.zzzzz'
```

`set_expires_at` / `set_not_before` / `set_issued_at` 也接受 `datetime`：

```python
from datetime import datetime, timedelta, timezone

exp = datetime.now(timezone.utc) + timedelta(hours=1)
token = JWTUtil.create().set_expires_at(exp).set_key(key).sign()
```

## 一次性编码

```python
payload = {"sub": "user-1", "name": "Alice"}
token = JWTUtil.encode(payload, key, algorithm="HS256")
```

## 解析与验证

```python
# 解析（不验签），返回 JWT 对象
jwt_obj = JWTUtil.parse(token)
jwt_obj.get_payload()    # {"sub": "user-1", "name": "Alice"}
jwt_obj.get_header()      # {"alg": "HS256", "typ": "JWT"}

# 验证签名（不检查 exp/nbf）
JWTUtil.verify(token, key)        # -> True / False

# 验证签名 + 检查 exp/nbf 时间约束
JWTUtil.validate(token, key)      # -> True / False

# 仅解码 payload（不验签）
JWTUtil.decode(token, verify=False)

# 验签并解码
JWTUtil.decode(token, key)
```

## JWT 对象方法

```python
jwt_obj = JWTUtil.parse(token)

# 验签（用 builder 已设置的 key，或临时传入）
jwt_obj.verify(key)
jwt_obj.validate(key)

# 访问
jwt_obj.get_payload()
jwt_obj.get_header()
jwt_obj.get_token()
```

## 算法支持

`algorithm` 参数对齐 PyJWT 支持的算法：

| 算法 | key 类型 | 说明 |
|------|---------|------|
| HS256 / HS384 / HS512 | `bytes` / `str` | HMAC-SHA（默认） |
| RS256 / RS384 / RS512 | PEM `str` | RSA 签名 |
| ES256 / ES384 / ES512 | PEM `str` | ECDSA |
| PS256 / PS384 / PS512 | PEM `str` | RSA-PSS |
| EdDSA | PEM `str` | Ed25519 |

```python
# RSA 示例
private_pem = """-----BEGIN RSA PRIVATE KEY-----..."""
public_pem = """-----BEGIN PUBLIC KEY-----..."""
token = JWTUtil.encode(payload, private_pem, algorithm="RS256")
JWTUtil.verify(token, public_pem, algorithm="RS256")
```

## 与 Hutool 的差异

| 方面 | Hutool (Java) | pyhutool (Python) |
|------|---------------|-------------------|
| 底层 | `io.jsonwebtoken` / `jjwt` | PyJWT |
| builder | `JWT.of(...)` / `JWT.create()` | `JWTUtil.create()` |
| 时间字段 | `java.util.Date` | `int` Unix 时间戳 或 `datetime` |
| 默认算法 | HS256 | HS256 |
| 依赖 | 内置 | `pyjwt` (extras) |

## 安全提示

- HMAC-SHA256 推荐密钥长度 ≥ 32 字节（PyJWT 会发出
  `InsecureKeyLengthWarning`）；
- 不要在客户端存储长期有效的 token；
- 生产环境优先考虑 RS256/ES256 而非 HS256，便于密钥分离。
