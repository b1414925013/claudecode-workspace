"""对称加密工具。

对齐 Hutool 的 ``cn.hutool.crypto.symmetric.SymmetricCrypto`` /
``cn.hutool.crypto.symmetric.AES`` / ``DES`` / ``DESede`` 系列，基于
``cryptography`` 库提供 AES / DES / 3DES (TripleDES) 加解密。

设计说明
--------
- ``cryptography`` 是可选依赖；未安装时调用任何方法抛 ``UtilError``；
- 所有加密方法默认使用 ``CBC`` 模式 + PKCS7 填充；
- ``iv`` 缺省时由方法自动生成（CBC/CFB/OFB/CTR 模式需要 IV），
  并与密文一并返回（前 16/8 字节为 IV，剩余为密文），便于一次性打包；
  若调用方显式传入 ``iv``，则返回值仅为密文；
- ECB 模式不需要 IV，但 ECB 不安全，建议仅用于兼容旧系统；
- Hutool 默认行为也是 PKCS7 + CBC（详见 ``cn.hutool.crypto.symmetric``）。

返回值约定
----------
- 显式传 ``iv``：返回值 = 密文（bytes）。
- 未传 ``iv`` 且模式需要 IV：返回值 = ``iv + 密文``（bytes），便于解密时取回 IV。
"""

from __future__ import annotations

import os
from typing import Any, Final, cast

from pyhutool.core.exceptions import UtilError

__all__ = ["CryptoUtil"]

_BLOCK_SIZE_AES: Final[int] = 16  # AES 块大小固定 16 字节
_BLOCK_SIZE_DES: Final[int] = 8   # DES / 3DES 块大小固定 8 字节


def _require_cryptography() -> Any:
    """惰性导入 ``cryptography``；未安装时抛 ``UtilError``。

    说明：``cryptography`` 48+ 把已弃用的 TripleDES 从
    ``cryptography.hazmat.primitives.ciphers.algorithms`` 移到
    ``cryptography.hazmat.decrepit.ciphers.algorithms``。这里做兼容处理：
    优先用 ``decrepit`` 中的版本，找不到则回退到 ``primitives``。
    """
    try:
        from cryptography.hazmat.primitives import ciphers, padding
        from cryptography.hazmat.primitives.ciphers import algorithms, modes
    except ImportError as e:
        raise UtilError(
            "pyhutool.crypto 需要 cryptography 支持，"
            "请运行：pip install 'pyhutool[crypto]'",
            cause=e,
        ) from e

    # TripleDES 在 cryptography 48 之后挪到 decrepit 子包
    try:
        from cryptography.hazmat.decrepit.ciphers import (
            algorithms as decrepit_algorithms,
        )

        triple_des_cls = decrepit_algorithms.TripleDES
    except ImportError:
        triple_des_cls = algorithms.TripleDES

    return {
        "ciphers": ciphers,
        "padding": padding,
        "algorithms": algorithms,
        "modes": modes,
        "triple_des": triple_des_cls,
    }


def _build_cipher(
    mods: dict[str, Any],
    algorithm_name: str,
    key: bytes,
    iv: bytes | None,
    mode_name: str,
    block_size: int,
) -> tuple[Any, bytes | None]:
    """构造 ``cryptography`` 的 ``Cipher`` 对象，返回 (cipher, iv)。

    若 ``iv`` 为 ``None`` 且模式需要 IV，则自动生成 ``block_size`` 字节 IV。
    """
    algorithms = mods["algorithms"]
    modes = mods["modes"]
    ciphers = mods["ciphers"]

    algo_cls_map: dict[str, Any] = {
        "AES": algorithms.AES,
        "TRIPLEDES": mods["triple_des"],
    }
    algo_cls = algo_cls_map.get(algorithm_name.upper())
    if algo_cls is None:
        raise UtilError(f"不支持的算法: {algorithm_name}")

    mode_name_upper = mode_name.upper()
    mode_map: dict[str, Any] = {
        "CBC": modes.CBC,
        "ECB": modes.ECB,
        "CFB": modes.CFB,
        "OFB": modes.OFB,
        "CTR": modes.CTR,
    }
    mode_cls = mode_map.get(mode_name_upper)
    if mode_cls is None:
        raise UtilError(f"不支持的模式: {mode_name}")

    # ECB 不需要 IV
    if mode_cls is modes.ECB:
        try:
            cipher = ciphers.Cipher(algo_cls(key), mode_cls())
        except ValueError as e:
            raise UtilError(f"密钥长度不合法: {e}", cause=e) from e
        return cipher, None

    # 其余模式需要 IV
    if iv is None:
        iv = os.urandom(block_size)
    elif len(iv) != block_size:
        raise UtilError(
            f"IV 长度必须为 {block_size} 字节，实际为 {len(iv)}"
        )

    try:
        cipher = ciphers.Cipher(algo_cls(key), mode_cls(iv))
    except ValueError as e:
        raise UtilError(f"密钥长度不合法: {e}", cause=e) from e
    return cipher, iv


def _pad_unpad_pkcs7(
    mods: dict[str, Any],
    block_size: int,
) -> tuple[Any, Any]:
    """返回 PKCS7 padder / unpadder 工厂。"""
    padding = mods["padding"]
    padder = padding.PKCS7(block_size * 8).padder()
    unpadder = padding.PKCS7(block_size * 8).unpadder()
    return padder, unpadder


class CryptoUtil:
    """对称加密工具类，全部为静态方法。

    对应 Hutool ``cn.hutool.crypto.symmetric`` 包下的 ``AES`` / ``DES`` /
    ``DESede``。统一通过 ``encrypt`` / ``decrypt`` 配合 ``algorithm`` 参数
    选择具体算法，便于扩展。
    """

    # ------------------------------------------------------------------
    # 通用 encrypt / decrypt
    # ------------------------------------------------------------------
    @staticmethod
    def encrypt(
        algorithm: str,
        key: bytes,
        data: bytes,
        *,
        iv: bytes | None = None,
        mode: str = "CBC",
    ) -> bytes:
        """通用对称加密。

        Parameters
        ----------
        algorithm:
            算法名（大小写不敏感）：``"AES"`` / ``"DES"`` / ``"TripleDES"``。
        key:
            密钥字节。AES 支持 16/24/32 字节；DES 8 字节；TripleDES 16/24 字节。
        data:
            明文字节。
        iv:
            初始向量；``None`` 表示自动生成（CBC/CFB/OFB/CTR）。
        mode:
            分组模式（大小写不敏感）：``"CBC"``/``"ECB"``/``"CFB"``/``"OFB"``
            /``"CTR"``。默认 ``"CBC"``。

        Returns
        -------
        bytes
            若 ``iv`` 为 ``None`` 且模式需要 IV，返回 ``iv + 密文``；
            否则只返回密文。
        """
        mods = _require_cryptography()
        algo_upper = algorithm.upper()
        block_size = _BLOCK_SIZE_AES if algo_upper == "AES" else _BLOCK_SIZE_DES

        cipher, actual_iv = _build_cipher(mods, algo_upper, key, iv, mode, block_size)
        padder, _ = _pad_unpad_pkcs7(mods, block_size)

        try:
            encryptor = cipher.encryptor()
            padded = padder.update(data) + padder.finalize()
            ciphertext = encryptor.update(padded) + encryptor.finalize()
        except Exception as e:
            raise UtilError(f"加密失败: {e}", cause=e) from e

        # cryptography 无 stub，返回值被推断为 Any，需显式 cast 保证
        # ``mypy --strict`` 通过。
        ct = cast(bytes, ciphertext)
        if actual_iv is not None and iv is None:
            return actual_iv + ct
        return ct

    @staticmethod
    def decrypt(
        algorithm: str,
        key: bytes,
        data: bytes,
        *,
        iv: bytes | None = None,
        mode: str = "CBC",
    ) -> bytes:
        """通用对称解密。

        Parameters
        ----------
        algorithm:
            算法名，与 :meth:`encrypt` 一致。
        key:
            密钥字节。
        data:
            密文字节。若 ``iv`` 为 ``None`` 且模式需要 IV，应传入
            ``encrypt`` 返回的 ``iv + 密文`` 形式。
        iv:
            初始向量。``None`` 表示从 ``data`` 头部 ``block_size`` 字节中取。
        mode:
            分组模式，需与加密时一致。

        Returns
        -------
        bytes
            解密后的明文。
        """
        mods = _require_cryptography()
        algo_upper = algorithm.upper()
        block_size = _BLOCK_SIZE_AES if algo_upper == "AES" else _BLOCK_SIZE_DES

        # 若未显式传 iv 且模式需要 IV，则从 data 头部切出
        mode_upper = mode.upper()
        if iv is None and mode_upper != "ECB":
            if len(data) < block_size:
                raise UtilError(
                    f"密文长度不足 {block_size} 字节，无法提取 IV"
                )
            iv = data[:block_size]
            data = data[block_size:]

        cipher, _ = _build_cipher(mods, algo_upper, key, iv, mode, block_size)
        _, unpadder = _pad_unpad_pkcs7(mods, block_size)

        try:
            decryptor = cipher.decryptor()
            padded = decryptor.update(data) + decryptor.finalize()
            plain = unpadder.update(padded) + unpadder.finalize()
        except Exception as e:
            raise UtilError(f"解密失败: {e}", cause=e) from e
        return cast(bytes, plain)

    # ------------------------------------------------------------------
    # AES 便捷方法
    # ------------------------------------------------------------------
    @staticmethod
    def aes_encrypt(
        key: bytes,
        data: bytes,
        *,
        iv: bytes | None = None,
        mode: str = "CBC",
    ) -> bytes:
        """AES 加密。``key`` 长度 16/24/32 对应 AES-128/192/256。"""
        return CryptoUtil.encrypt("AES", key, data, iv=iv, mode=mode)

    @staticmethod
    def aes_decrypt(
        key: bytes,
        data: bytes,
        *,
        iv: bytes | None = None,
        mode: str = "CBC",
    ) -> bytes:
        """AES 解密。"""
        return CryptoUtil.decrypt("AES", key, data, iv=iv, mode=mode)

    # ------------------------------------------------------------------
    # DES 便捷方法
    # ------------------------------------------------------------------
    # 注意：``cryptography`` 39.0 起弃用、44.0 起移除 ``algorithms.DES``，
    # 因为 DES 已不安全。但 Hutool 仍保留 DES API；为了行为对齐，
    # 这里把 8 字节 DES key 扩展为 ``KKK``（24 字节）后调用 ``TripleDES``，
    # 数学上等价于单 DES。
    @staticmethod
    def des_encrypt(
        key: bytes,
        data: bytes,
        *,
        iv: bytes | None = None,
        mode: str = "CBC",
    ) -> bytes:
        """DES 加密。``key`` 长度必须为 8 字节。

        实现上等价于 ``TripleDES(key * 3)``（即 ``KKK``），与单 DES 数值相同。
        """
        if len(key) != 8:
            raise UtilError(f"DES key 长度必须为 8 字节，实际为 {len(key)}")
        return CryptoUtil.encrypt("TripleDES", key * 3, data, iv=iv, mode=mode)

    @staticmethod
    def des_decrypt(
        key: bytes,
        data: bytes,
        *,
        iv: bytes | None = None,
        mode: str = "CBC",
    ) -> bytes:
        """DES 解密。"""
        if len(key) != 8:
            raise UtilError(f"DES key 长度必须为 8 字节，实际为 {len(key)}")
        return CryptoUtil.decrypt("TripleDES", key * 3, data, iv=iv, mode=mode)

    # ------------------------------------------------------------------
    # 3DES (TripleDES / DESede) 便捷方法
    # ------------------------------------------------------------------
    @staticmethod
    def des3_encrypt(
        key: bytes,
        data: bytes,
        *,
        iv: bytes | None = None,
        mode: str = "CBC",
    ) -> bytes:
        """3DES 加密。``key`` 长度 16/24 字节。"""
        return CryptoUtil.encrypt("TripleDES", key, data, iv=iv, mode=mode)

    @staticmethod
    def des3_decrypt(
        key: bytes,
        data: bytes,
        *,
        iv: bytes | None = None,
        mode: str = "CBC",
    ) -> bytes:
        """3DES 解密。"""
        return CryptoUtil.decrypt("TripleDES", key, data, iv=iv, mode=mode)

    # ------------------------------------------------------------------
    # 密钥生成
    # ------------------------------------------------------------------
    @staticmethod
    def gen_key(algorithm: str = "AES", key_size: int = 256) -> bytes:
        """生成对称密钥。

        Parameters
        ----------
        algorithm:
            算法名（大小写不敏感）。``AES`` 时 ``key_size`` 必须是 128/192/256；
            ``DES`` 固定 64 bit（8 字节，实际有效 56 bit）；
            ``TripleDES`` 支持 64/128/192 bit。
        key_size:
            密钥位数（bit）。默认 256（AES-256）。

        Returns
        -------
        bytes
            随机密钥字节。
        """
        algo_upper = algorithm.upper()
        if algo_upper == "AES":
            if key_size not in (128, 192, 256):
                raise UtilError("AES key_size 必须为 128/192/256")
        elif algo_upper == "DES":
            if key_size != 64:
                raise UtilError("DES key_size 必须为 64")
        elif algo_upper in ("TRIPLEDES", "DESEDE", "3DES"):
            if key_size not in (64, 128, 192):
                raise UtilError("TripleDES key_size 必须为 64/128/192")
        else:
            raise UtilError(f"不支持的算法: {algorithm}")

        return os.urandom(key_size // 8)

    @staticmethod
    def gen_iv(block_size: int = 16) -> bytes:
        """生成随机 IV。AES 默认 16 字节，DES/3DES 8 字节。"""
        if block_size not in (8, 16):
            raise UtilError("block_size 必须为 8 或 16")
        return os.urandom(block_size)
