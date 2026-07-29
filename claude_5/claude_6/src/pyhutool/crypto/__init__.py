"""pyhutool.crypto - 加密与摘要模块。

- ``DigestUtil``：基于标准库 ``hashlib`` + ``hmac``，**零外部依赖**，
  提供 MD5/SHA1/SHA256/SHA512 摘要与 HMAC-MD5/HMAC-SHA1/HMAC-SHA256/
  HMAC-SHA512 消息认证码；
- ``CryptoUtil``：基于 ``cryptography`` 库，提供 AES/DES/TripleDES 对称
  加解密。``cryptography`` 为可选依赖，未安装时调用抛 ``UtilError``。

对应 Hutool ``cn.hutool.crypto`` 包。
"""

from pyhutool.crypto.crypto_util import CryptoUtil
from pyhutool.crypto.digest_util import DigestUtil

__all__ = ["CryptoUtil", "DigestUtil"]
