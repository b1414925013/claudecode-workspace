"""CryptoUtil 单元测试。"""

from __future__ import annotations

import os

import pytest

from pyhutool.core.exceptions import UtilError
from pyhutool.crypto import CryptoUtil

# 模块级跳过：若环境未装 cryptography，跳过所有用例
cryptography_available = True
try:
    import cryptography  # noqa: F401
except ImportError:
    cryptography_available = False

pytestmark = pytest.mark.skipif(
    not cryptography_available, reason="需要 cryptography"
)


class TestAES:
    """AES。"""

    def test_aes_cbc_roundtrip_auto_iv(self) -> None:
        key = os.urandom(32)  # AES-256
        data = b"hello world, this is a test message"
        ciphertext = CryptoUtil.aes_encrypt(key, data)
        # IV 自动生成时返回值 = IV(16) + ciphertext
        assert len(ciphertext) >= 16 + len(data)
        plaintext = CryptoUtil.aes_decrypt(key, ciphertext)
        assert plaintext == data

    def test_aes_cbc_roundtrip_explicit_iv(self) -> None:
        key = os.urandom(16)  # AES-128
        iv = os.urandom(16)
        data = b"payload \x00\x01"
        ciphertext = CryptoUtil.aes_encrypt(key, data, iv=iv)
        # 显式传 IV 时返回值仅为密文
        assert len(ciphertext) == 16  # 16 字节明文 + PKCS7 → 32 字节，但这里 8 字节明文 + 8 padding = 16
        plaintext = CryptoUtil.aes_decrypt(key, ciphertext, iv=iv)
        assert plaintext == data

    def test_aes_ecb_roundtrip(self) -> None:
        key = os.urandom(16)
        data = b"16-byte message!"  # 必须 16 字节倍数
        ciphertext = CryptoUtil.aes_encrypt(key, data, mode="ECB")
        assert len(ciphertext) == 32  # 16 明文 + 16 padding
        plaintext = CryptoUtil.aes_decrypt(key, ciphertext, mode="ECB")
        assert plaintext == data

    def test_aes_cfb_roundtrip(self) -> None:
        key = os.urandom(32)
        iv = os.urandom(16)
        data = b"cfb mode no padding needed"
        # CFB/OFB/CTR 是流密码模式，无需 padding
        # 但我们的实现仍走 PKCS7，会补 padding
        ciphertext = CryptoUtil.aes_encrypt(key, data, iv=iv, mode="CFB")
        plaintext = CryptoUtil.aes_decrypt(key, ciphertext, iv=iv, mode="CFB")
        assert plaintext == data

    def test_aes_ctr_roundtrip(self) -> None:
        key = os.urandom(16)
        iv = os.urandom(16)
        data = b"ctr mode test data"
        ciphertext = CryptoUtil.aes_encrypt(key, data, iv=iv, mode="CTR")
        plaintext = CryptoUtil.aes_decrypt(key, ciphertext, iv=iv, mode="CTR")
        assert plaintext == data

    def test_aes_wrong_key_raises(self) -> None:
        key = os.urandom(16)
        wrong = os.urandom(16)
        iv = os.urandom(16)
        data = b"secret"
        ciphertext = CryptoUtil.aes_encrypt(key, data, iv=iv)
        with pytest.raises(UtilError):
            CryptoUtil.aes_decrypt(wrong, ciphertext, iv=iv)

    def test_aes_invalid_iv_length(self) -> None:
        key = os.urandom(16)
        data = b"x"
        with pytest.raises(UtilError):
            CryptoUtil.aes_encrypt(key, data, iv=b"short")

    def test_aes_invalid_key_length(self) -> None:
        # cryptography 自身会校验，被包装为 UtilError
        with pytest.raises(UtilError):
            CryptoUtil.aes_encrypt(b"too-short", b"data")

    def test_aes_unsupported_mode(self) -> None:
        key = os.urandom(16)
        with pytest.raises(UtilError):
            CryptoUtil.aes_encrypt(key, b"data", mode="WRONG")


class TestDES:
    """DES / 3DES。"""

    def test_des_roundtrip(self) -> None:
        key = os.urandom(8)
        data = b"des test payload"
        ciphertext = CryptoUtil.des_encrypt(key, data)
        # 8 字节 IV + 密文
        assert len(ciphertext) >= 8 + len(data)
        plaintext = CryptoUtil.des_decrypt(key, ciphertext)
        assert plaintext == data

    def test_des3_roundtrip(self) -> None:
        key = os.urandom(24)  # 3DES-192
        data = b"3des test payload"
        ciphertext = CryptoUtil.des3_encrypt(key, data)
        plaintext = CryptoUtil.des3_decrypt(key, ciphertext)
        assert plaintext == data

    def test_des3_128_key(self) -> None:
        # 16 字节 key 也会被 cryptography 接受
        key = os.urandom(16)
        data = b"3des-128"
        ciphertext = CryptoUtil.des3_encrypt(key, data)
        plaintext = CryptoUtil.des3_decrypt(key, ciphertext)
        assert plaintext == data

    def test_des_invalid_key(self) -> None:
        with pytest.raises(UtilError):
            CryptoUtil.des_encrypt(b"too-short", b"data")


class TestGenericEncrypt:
    """通用接口。"""

    def test_encrypt_decrypt_aes(self) -> None:
        key = os.urandom(16)
        iv = os.urandom(16)
        data = b"generic interface"
        ciphertext = CryptoUtil.encrypt("AES", key, data, iv=iv)
        plain = CryptoUtil.decrypt("AES", key, ciphertext, iv=iv)
        assert plain == data

    def test_encrypt_decrypt_triple_des(self) -> None:
        key = os.urandom(24)
        iv = os.urandom(8)
        data = b"triple"
        ciphertext = CryptoUtil.encrypt("TripleDES", key, data, iv=iv)
        plain = CryptoUtil.decrypt("TripleDES", key, ciphertext, iv=iv)
        assert plain == data

    def test_encrypt_unsupported_algorithm(self) -> None:
        with pytest.raises(UtilError):
            CryptoUtil.encrypt("Blowfish", b"k" * 8, b"data")

    def test_decrypt_short_data_auto_iv(self) -> None:
        # 自动 IV 提取：data 比 block_size 还短
        key = os.urandom(16)
        with pytest.raises(UtilError):
            CryptoUtil.aes_decrypt(key, b"short")


class TestKeyGen:
    """密钥生成。"""

    def test_gen_key_aes_128(self) -> None:
        key = CryptoUtil.gen_key("AES", 128)
        assert len(key) == 16

    def test_gen_key_aes_256(self) -> None:
        key = CryptoUtil.gen_key("AES", 256)
        assert len(key) == 32

    def test_gen_key_des(self) -> None:
        key = CryptoUtil.gen_key("DES", 64)
        assert len(key) == 8

    def test_gen_key_3des(self) -> None:
        key = CryptoUtil.gen_key("TripleDES", 192)
        assert len(key) == 24

    def test_gen_key_invalid_aes_size(self) -> None:
        with pytest.raises(UtilError):
            CryptoUtil.gen_key("AES", 100)

    def test_gen_key_invalid_des_size(self) -> None:
        with pytest.raises(UtilError):
            CryptoUtil.gen_key("DES", 128)

    def test_gen_key_invalid_3des_size(self) -> None:
        with pytest.raises(UtilError):
            CryptoUtil.gen_key("TripleDES", 100)

    def test_gen_key_unknown_algorithm(self) -> None:
        with pytest.raises(UtilError):
            CryptoUtil.gen_key("Blowfish", 128)

    def test_gen_iv_default(self) -> None:
        iv = CryptoUtil.gen_iv()
        assert len(iv) == 16

    def test_gen_iv_des(self) -> None:
        iv = CryptoUtil.gen_iv(8)
        assert len(iv) == 8

    def test_gen_iv_invalid(self) -> None:
        with pytest.raises(UtilError):
            CryptoUtil.gen_iv(7)


class TestMissingDependency:
    """cryptography 未安装时（在已安装环境下不可直接模拟，留接口测试）。"""

    def test_dependency_marker_set(self) -> None:
        # 这个测试只确保 pytestmark 正常工作
        assert cryptography_available is True
