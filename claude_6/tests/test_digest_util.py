"""DigestUtil 单元测试。"""

from __future__ import annotations

import hashlib
import hmac as stdlib_hmac
from pathlib import Path

import pytest

from pyhutool.core.exceptions import UtilError
from pyhutool.crypto import DigestUtil

# 已知答案（来自 hashlib / RFC 1321 / RFC 3174 等）
_KNOWN_MD5_EMPTY = "d41d8cd98f00b204e9800998ecf8427e"
_KNOWN_MD5_ABC = "900150983cd24fb0d6963f7d28e17f72"
_KNOWN_SHA1_ABC = "a9993e364706816aba3e25717850c26c9cd0d89d"
_KNOWN_SHA256_ABC = (
    "ba7816bf8f01cfea414140de5dae2223"
    "b00361a396177a9cb410ff61f20015ad"
)
_KNOWN_SHA512_ABC = (
    "ddaf35a193617abacc417349ae204131"
    "12e6fa4e89a97ea20a9eeee64b55d39a"
    "2192992a274fc1a836ba3c23a3feebbd"
    "454d4423643ce80e2a9ac94fa54ca49f"
)


class TestDigestBasic:
    """基础摘要。"""

    def test_md5_empty(self) -> None:
        assert DigestUtil.md5_hex("") == _KNOWN_MD5_EMPTY

    def test_md5_abc(self) -> None:
        assert DigestUtil.md5_hex("abc") == _KNOWN_MD5_ABC

    def test_md5_bytes(self) -> None:
        assert DigestUtil.md5(b"abc") == bytes.fromhex(_KNOWN_MD5_ABC)

    def test_sha1_abc(self) -> None:
        assert DigestUtil.sha1_hex("abc") == _KNOWN_SHA1_ABC

    def test_sha256_abc(self) -> None:
        assert DigestUtil.sha256_hex("abc") == _KNOWN_SHA256_ABC

    def test_sha512_abc(self) -> None:
        assert DigestUtil.sha512_hex("abc") == _KNOWN_SHA512_ABC

    def test_md5_returns_bytes_of_length_16(self) -> None:
        assert len(DigestUtil.md5("x")) == 16

    def test_sha256_returns_bytes_of_length_32(self) -> None:
        assert len(DigestUtil.sha256("x")) == 32

    def test_sha512_returns_bytes_of_length_64(self) -> None:
        assert len(DigestUtil.sha512("x")) == 64


class TestDigestGeneric:
    """通用 digest / digest_hex 接口。"""

    def test_digest_md5(self) -> None:
        assert DigestUtil.digest_hex("MD5", "abc") == _KNOWN_MD5_ABC

    def test_digest_case_insensitive(self) -> None:
        assert DigestUtil.digest_hex("sha256", "abc") == _KNOWN_SHA256_ABC
        assert DigestUtil.digest_hex("SHA-256", "abc") == _KNOWN_SHA256_ABC

    def test_digest_bytes_input(self) -> None:
        assert DigestUtil.digest_hex("md5", b"abc") == _KNOWN_MD5_ABC

    def test_digest_unknown_algorithm_raises(self) -> None:
        with pytest.raises(UtilError):
            DigestUtil.digest("not-a-real-algo", "x")

    def test_digest_hex_unknown_algorithm_raises(self) -> None:
        with pytest.raises(UtilError):
            DigestUtil.digest_hex("nope", "x")

    def test_digest_matches_hashlib(self) -> None:
        # 跟标准库对齐
        for algo in ("md5", "sha1", "sha256", "sha512"):
            data = b"some random bytes \x00\x01"
            assert DigestUtil.digest_hex(algo, data) == hashlib.new(algo, data).hexdigest()


class TestHmac:
    """HMAC。"""

    def test_hmac_md5(self) -> None:
        key = b"secret"
        data = b"hello"
        expected = stdlib_hmac.new(key, data, "md5").hexdigest()
        assert DigestUtil.hmac_md5_hex(key, data) == expected
        assert DigestUtil.hmac_md5(key, data) == bytes.fromhex(expected)

    def test_hmac_sha1_str_key(self) -> None:
        # str key/data 走 UTF-8 编码路径
        expected = stdlib_hmac.new(b"secret", b"hello", "sha1").hexdigest()
        assert DigestUtil.hmac_sha1_hex("secret", "hello") == expected

    def test_hmac_sha256(self) -> None:
        key = b"k"
        data = b"d"
        expected = stdlib_hmac.new(key, data, "sha256").hexdigest()
        assert DigestUtil.hmac_sha256_hex(key, data) == expected

    def test_hmac_sha512(self) -> None:
        key = b"k"
        data = b"d"
        expected = stdlib_hmac.new(key, data, "sha512").hexdigest()
        assert DigestUtil.hmac_sha512_hex(key, data) == expected

    def test_hmac_generic(self) -> None:
        assert DigestUtil.hmac_hex("sha256", b"k", b"d") == DigestUtil.hmac_sha256_hex(b"k", b"d")

    def test_hmac_unknown_algorithm_raises(self) -> None:
        with pytest.raises(UtilError):
            DigestUtil.hmac("not-a-real-algo", b"k", b"d")


class TestFileDigest:
    """文件摘要。"""

    def test_md5_file(self, tmp_path: Path) -> None:
        p = tmp_path / "data.bin"
        payload = b"abc" * 1000
        # 关键：用 write_bytes 避免 Windows newline 翻译
        p.write_bytes(payload)
        expected = hashlib.md5(payload).hexdigest()
        assert DigestUtil.md5_file_hex(str(p)) == expected
        assert DigestUtil.md5_file(str(p)) == bytes.fromhex(expected)

    def test_sha256_file(self, tmp_path: Path) -> None:
        p = tmp_path / "data.bin"
        payload = b"some big content " * 4096
        p.write_bytes(payload)
        expected = hashlib.sha256(payload).hexdigest()
        assert DigestUtil.sha256_file_hex(str(p)) == expected

    def test_digest_file_unknown_algorithm(self, tmp_path: Path) -> None:
        p = tmp_path / "x.bin"
        p.write_bytes(b"abc")
        with pytest.raises(UtilError):
            DigestUtil.digest_file("not-a-real-algo", str(p))

    def test_digest_file_missing_file(self, tmp_path: Path) -> None:
        p = tmp_path / "nope.bin"
        with pytest.raises(UtilError):
            DigestUtil.md5_file_hex(str(p))

    def test_digest_file_path_bytes(self, tmp_path: Path) -> None:
        # 路径用 bytes 形式传
        p = tmp_path / "x.bin"
        p.write_bytes(b"abc")
        expected = hashlib.md5(b"abc").hexdigest()
        assert DigestUtil.md5_file_hex(str(p).encode()) == expected
