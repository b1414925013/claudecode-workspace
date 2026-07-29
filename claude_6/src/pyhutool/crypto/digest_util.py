"""摘要算法工具。

对齐 Hutool 的 ``cn.hutool.crypto.digest.DigestUtil``，提供 MD5/SHA1/SHA256/
SHA512 摘要与 HMAC-MD5/HMAC-SHA1/HMAC-SHA256/HMAC-SHA512 消息认证码。

设计说明
--------
- 底层基于标准库 ``hashlib`` 与 ``hmac``，**不依赖** ``cryptography``，
  因此 ``DigestUtil`` 可在仅安装核心包时使用；
- 输入 ``data`` 既可以是 ``bytes``，也可以是 ``str``（按 UTF-8 编码），
  对齐 Hutool ``DigestUtil.md5(String)`` 的便捷语义；
- ``*_hex`` 系列方法返回小写十六进制字符串，与 Hutool / Python ``hashlib.hexdigest``
  默认行为一致；
- ``digest(algorithm, data)`` 中的 ``algorithm`` 大小写不敏感，会规整为
  小写后再交给 ``hashlib.new``。
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Final

from pyhutool.core.exceptions import UtilError

__all__ = ["DigestUtil"]

_UTF8: Final[str] = "UTF-8"

# hashlib 接受小写无连字符算法名；这里把常见别名规整化。
# 例如 ``SHA-256`` -> ``sha256``、``SHA-512`` -> ``sha512``。
_DIGEST_ALIASES: Final[dict[str, str]] = {
    "sha-1": "sha1",
    "sha-224": "sha224",
    "sha-256": "sha256",
    "sha-384": "sha384",
    "sha-512": "sha512",
    "sha-512/224": "sha512_224",
    "sha-512/256": "sha512_256",
    "sha3-224": "sha3_224",
    "sha3-256": "sha3_256",
    "sha3-384": "sha3_384",
    "sha3-512": "sha3_512",
    "md5": "md5",
}


def _normalize_algorithm(algorithm: str) -> str:
    """把算法名规整为 ``hashlib`` / ``hmac`` 可识别的小写形式。"""
    lower = algorithm.lower()
    return _DIGEST_ALIASES.get(lower, lower)


def _to_bytes(data: bytes | str) -> bytes:
    """把 ``bytes | str`` 统一成 ``bytes``。``str`` 按 UTF-8 编码。"""
    if isinstance(data, str):
        return data.encode(_UTF8)
    return data


class DigestUtil:
    """摘要与 HMAC 工具类，全部为静态方法。

    对应 Hutool ``cn.hutool.crypto.digest.DigestUtil``。
    """

    # ------------------------------------------------------------------
    # 通用摘要
    # ------------------------------------------------------------------
    @staticmethod
    def digest(algorithm: str, data: bytes | str) -> bytes:
        """按指定算法计算摘要，返回原始字节。

        Parameters
        ----------
        algorithm:
            摘要算法名（大小写不敏感），如 ``"MD5"``/``"SHA-256"``/``"sha512"``。
            传给 ``hashlib.new`` 之前会先小写化。
        data:
            待摘要数据，``str`` 按 UTF-8 编码。

        Raises
        ------
        UtilError
            算法不存在或不被 ``hashlib`` 支持。
        """
        algo = _normalize_algorithm(algorithm)
        try:
            h = hashlib.new(algo)
        except ValueError as e:
            raise UtilError(f"不支持的摘要算法: {algorithm}", cause=e) from e
        h.update(_to_bytes(data))
        return h.digest()

    @staticmethod
    def digest_hex(algorithm: str, data: bytes | str) -> str:
        """按指定算法计算摘要，返回小写十六进制字符串。"""
        return DigestUtil.digest(algorithm, data).hex()

    # ------------------------------------------------------------------
    # MD5
    # ------------------------------------------------------------------
    @staticmethod
    def md5(data: bytes | str) -> bytes:
        """计算 MD5 摘要（128 位，16 字节）。"""
        return hashlib.md5(_to_bytes(data)).digest()

    @staticmethod
    def md5_hex(data: bytes | str) -> str:
        """计算 MD5 摘要，返回 32 字符小写十六进制字符串。"""
        return hashlib.md5(_to_bytes(data)).hexdigest()

    # ------------------------------------------------------------------
    # SHA-1
    # ------------------------------------------------------------------
    @staticmethod
    def sha1(data: bytes | str) -> bytes:
        """计算 SHA-1 摘要（160 位，20 字节）。"""
        return hashlib.sha1(_to_bytes(data)).digest()

    @staticmethod
    def sha1_hex(data: bytes | str) -> str:
        """计算 SHA-1 摘要，返回 40 字符小写十六进制字符串。"""
        return hashlib.sha1(_to_bytes(data)).hexdigest()

    # ------------------------------------------------------------------
    # SHA-256
    # ------------------------------------------------------------------
    @staticmethod
    def sha256(data: bytes | str) -> bytes:
        """计算 SHA-256 摘要（256 位，32 字节）。"""
        return hashlib.sha256(_to_bytes(data)).digest()

    @staticmethod
    def sha256_hex(data: bytes | str) -> str:
        """计算 SHA-256 摘要，返回 64 字符小写十六进制字符串。"""
        return hashlib.sha256(_to_bytes(data)).hexdigest()

    # ------------------------------------------------------------------
    # SHA-512
    # ------------------------------------------------------------------
    @staticmethod
    def sha512(data: bytes | str) -> bytes:
        """计算 SHA-512 摘要（512 位，64 字节）。"""
        return hashlib.sha512(_to_bytes(data)).digest()

    @staticmethod
    def sha512_hex(data: bytes | str) -> str:
        """计算 SHA-512 摘要，返回 128 字符小写十六进制字符串。"""
        return hashlib.sha512(_to_bytes(data)).hexdigest()

    # ------------------------------------------------------------------
    # HMAC 通用
    # ------------------------------------------------------------------
    @staticmethod
    def hmac(
        algorithm: str,
        key: bytes | str,
        data: bytes | str,
    ) -> bytes:
        """按指定摘要算法计算 HMAC，返回原始字节。

        Parameters
        ----------
        algorithm:
            摘要算法名（大小写不敏感），如 ``"MD5"``/``"SHA256"``。
        key:
            HMAC 密钥。``str`` 按 UTF-8 编码。
        data:
            待认证数据。

        Raises
        ------
        UtilError
            算法不支持。
        """
        algo = _normalize_algorithm(algorithm)
        try:
            return hmac.new(_to_bytes(key), _to_bytes(data), algo).digest()
        except ValueError as e:
            raise UtilError(f"不支持的 HMAC 算法: {algorithm}", cause=e) from e

    @staticmethod
    def hmac_hex(
        algorithm: str,
        key: bytes | str,
        data: bytes | str,
    ) -> str:
        """按指定算法计算 HMAC，返回小写十六进制字符串。"""
        return DigestUtil.hmac(algorithm, key, data).hex()

    # ------------------------------------------------------------------
    # HMAC-MD5
    # ------------------------------------------------------------------
    @staticmethod
    def hmac_md5(key: bytes | str, data: bytes | str) -> bytes:
        """计算 HMAC-MD5。"""
        return hmac.new(_to_bytes(key), _to_bytes(data), "md5").digest()

    @staticmethod
    def hmac_md5_hex(key: bytes | str, data: bytes | str) -> str:
        """计算 HMAC-MD5，返回 32 字符小写十六进制字符串。"""
        return hmac.new(_to_bytes(key), _to_bytes(data), "md5").hexdigest()

    # ------------------------------------------------------------------
    # HMAC-SHA1
    # ------------------------------------------------------------------
    @staticmethod
    def hmac_sha1(key: bytes | str, data: bytes | str) -> bytes:
        """计算 HMAC-SHA1。"""
        return hmac.new(_to_bytes(key), _to_bytes(data), "sha1").digest()

    @staticmethod
    def hmac_sha1_hex(key: bytes | str, data: bytes | str) -> str:
        """计算 HMAC-SHA1，返回 40 字符小写十六进制字符串。"""
        return hmac.new(_to_bytes(key), _to_bytes(data), "sha1").hexdigest()

    # ------------------------------------------------------------------
    # HMAC-SHA256
    # ------------------------------------------------------------------
    @staticmethod
    def hmac_sha256(key: bytes | str, data: bytes | str) -> bytes:
        """计算 HMAC-SHA256。"""
        return hmac.new(_to_bytes(key), _to_bytes(data), "sha256").digest()

    @staticmethod
    def hmac_sha256_hex(key: bytes | str, data: bytes | str) -> str:
        """计算 HMAC-SHA256，返回 64 字符小写十六进制字符串。"""
        return hmac.new(_to_bytes(key), _to_bytes(data), "sha256").hexdigest()

    # ------------------------------------------------------------------
    # HMAC-SHA512
    # ------------------------------------------------------------------
    @staticmethod
    def hmac_sha512(key: bytes | str, data: bytes | str) -> bytes:
        """计算 HMAC-SHA512。"""
        return hmac.new(_to_bytes(key), _to_bytes(data), "sha512").digest()

    @staticmethod
    def hmac_sha512_hex(key: bytes | str, data: bytes | str) -> str:
        """计算 HMAC-SHA512，返回 128 字符小写十六进制字符串。"""
        return hmac.new(_to_bytes(key), _to_bytes(data), "sha512").hexdigest()

    # ------------------------------------------------------------------
    # 文件摘要
    # ------------------------------------------------------------------
    @staticmethod
    def digest_file(algorithm: str, path: str | bytes) -> bytes:
        """对文件内容计算摘要，避免一次性读取大文件占内存。

        Parameters
        ----------
        algorithm:
            摘要算法名（大小写不敏感）。
        path:
            文件路径。

        Raises
        ------
        UtilError
            算法不支持或文件读取失败。
        """
        algo = _normalize_algorithm(algorithm)
        try:
            h = hashlib.new(algo)
        except ValueError as e:
            raise UtilError(f"不支持的摘要算法: {algorithm}", cause=e) from e
        chunk_size = 64 * 1024
        try:
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    h.update(chunk)
        except OSError as e:
            raise UtilError(f"读取文件失败: {path!r}", cause=e) from e
        return h.digest()

    @staticmethod
    def digest_file_hex(algorithm: str, path: str | bytes) -> str:
        """对文件内容计算摘要，返回小写十六进制字符串。"""
        return DigestUtil.digest_file(algorithm, path).hex()

    @staticmethod
    def md5_file(path: str | bytes) -> bytes:
        """对文件计算 MD5。"""
        return DigestUtil.digest_file("md5", path)

    @staticmethod
    def md5_file_hex(path: str | bytes) -> str:
        """对文件计算 MD5，返回 32 字符十六进制字符串。"""
        return DigestUtil.digest_file_hex("md5", path)

    @staticmethod
    def sha256_file(path: str | bytes) -> bytes:
        """对文件计算 SHA-256。"""
        return DigestUtil.digest_file("sha256", path)

    @staticmethod
    def sha256_file_hex(path: str | bytes) -> str:
        """对文件计算 SHA-256，返回 64 字符十六进制字符串。"""
        return DigestUtil.digest_file_hex("sha256", path)
