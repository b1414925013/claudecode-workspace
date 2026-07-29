"""JWTUtil / JWT 单元测试。"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from pyhutool.core.exceptions import UtilError
from pyhutool.jwt import JWT, JWTUtil

# 模块级跳过：若环境未装 pyjwt，跳过所有用例
pyjwt_available = True
try:
    import jwt as _pyjwt  # noqa: F401
except ImportError:
    pyjwt_available = False

pytestmark = pytest.mark.skipif(not pyjwt_available, reason="需要 pyjwt")


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def secret_key() -> bytes:
    return b"super-secret-key-for-test-32-bytes!"


@pytest.fixture
def wrong_key() -> bytes:
    return b"another-wrong-key-also-32-bytes!!"


@pytest.fixture
def sample_payload() -> dict[str, Any]:
    return {"sub": "1234567890", "name": "Alice", "admin": True}


# ---------------------------------------------------------------------
# JWTUtil.encode / decode
# ---------------------------------------------------------------------
class TestEncodeDecode:
    def test_encode_decode_roundtrip(self, secret_key: bytes, sample_payload: dict) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        assert isinstance(token, str)
        decoded = JWTUtil.decode(token, secret_key)
        assert decoded["sub"] == "1234567890"
        assert decoded["name"] == "Alice"
        assert decoded["admin"] is True

    def test_encode_with_str_key(self, sample_payload: dict) -> None:
        token = JWTUtil.encode(sample_payload, "str-key-at-least-32-bytes-long!!")
        decoded = JWTUtil.decode(token, "str-key-at-least-32-bytes-long!!")
        assert decoded["sub"] == "1234567890"

    def test_encode_invalid_algorithm_raises(self, secret_key: bytes, sample_payload: dict) -> None:
        with pytest.raises(UtilError):
            JWTUtil.encode(sample_payload, secret_key, algorithm="NOT-REAL-ALG")

    def test_decode_without_key_when_verify_true_raises(self, sample_payload: dict, secret_key: bytes) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        with pytest.raises(UtilError):
            JWTUtil.decode(token, verify=True)

    def test_decode_no_verify(self, sample_payload: dict, secret_key: bytes) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        decoded = JWTUtil.decode(token, verify=False)
        assert decoded["name"] == "Alice"

    def test_decode_with_wrong_key_raises(self, secret_key: bytes, wrong_key: bytes, sample_payload: dict) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        with pytest.raises(UtilError):
            JWTUtil.decode(token, wrong_key)

    def test_decode_invalid_token_raises(self, secret_key: bytes) -> None:
        with pytest.raises(UtilError):
            JWTUtil.decode("not.a.valid.jwt", secret_key)


# ---------------------------------------------------------------------
# JWTUtil.parse / verify / validate
# ---------------------------------------------------------------------
class TestParseVerify:
    def test_parse_returns_jwt_with_payload(self, secret_key: bytes, sample_payload: dict) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        jwt_obj = JWTUtil.parse(token)
        assert isinstance(jwt_obj, JWT)
        assert jwt_obj.get_payload()["name"] == "Alice"
        assert jwt_obj.get_header()["alg"] == "HS256"
        assert jwt_obj.get_token() == token

    def test_parse_invalid_token_raises(self) -> None:
        with pytest.raises(UtilError):
            JWTUtil.parse("garbage")

    def test_verify_valid(self, secret_key: bytes, sample_payload: dict) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        assert JWTUtil.verify(token, secret_key) is True

    def test_verify_wrong_key(self, secret_key: bytes, wrong_key: bytes, sample_payload: dict) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        assert JWTUtil.verify(token, wrong_key) is False

    def test_validate_valid(self, secret_key: bytes, sample_payload: dict) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        assert JWTUtil.validate(token, secret_key) is True

    def test_validate_expired(self, secret_key: bytes) -> None:
        # exp 在过去
        payload = {"sub": "x", "exp": int(time.time()) - 3600}
        token = JWTUtil.encode(payload, secret_key)
        assert JWTUtil.validate(token, secret_key) is False

    def test_validate_not_before_future(self, secret_key: bytes) -> None:
        # nbf 在未来
        payload = {"sub": "x", "nbf": int(time.time()) + 3600}
        token = JWTUtil.encode(payload, secret_key)
        assert JWTUtil.validate(token, secret_key) is False

    def test_validate_wrong_key(self, secret_key: bytes, wrong_key: bytes, sample_payload: dict) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        assert JWTUtil.validate(token, wrong_key) is False


# ---------------------------------------------------------------------
# JWT builder
# ---------------------------------------------------------------------
class TestJWTBuilder:
    def test_builder_sign_and_verify(self, secret_key: bytes) -> None:
        token = (
            JWTUtil.create()
            .set_subject("user-1")
            .set_issuer("pyhutool")
            .set_key(secret_key)
            .sign()
        )
        assert isinstance(token, str)
        assert JWTUtil.verify(token, secret_key) is True

    def test_builder_without_key_raises(self) -> None:
        jwt_obj = JWTUtil.create().set_subject("x")
        with pytest.raises(UtilError):
            jwt_obj.sign()

    def test_builder_set_expires_at_int(self, secret_key: bytes) -> None:
        exp = int(time.time()) + 3600
        token = (
            JWTUtil.create()
            .set_payload("sub", "u")
            .set_expires_at(exp)
            .set_key(secret_key)
            .sign()
        )
        decoded = JWTUtil.decode(token, secret_key)
        assert decoded["exp"] == exp

    def test_builder_set_expires_at_datetime(self, secret_key: bytes) -> None:
        exp_dt = datetime.now(UTC) + timedelta(hours=1)
        token = (
            JWTUtil.create()
            .set_payload("sub", "u")
            .set_expires_at(exp_dt)
            .set_key(secret_key)
            .sign()
        )
        decoded = JWTUtil.decode(token, secret_key)
        # 时区 aware datetime → Unix 时间戳（秒），允许 1 秒抖动
        assert abs(decoded["exp"] - int(exp_dt.timestamp())) <= 1

    def test_builder_set_naive_datetime(self, secret_key: bytes) -> None:
        # naive datetime 视为本地时区
        exp_dt = datetime.now() + timedelta(hours=1)
        token = (
            JWTUtil.create()
            .set_payload("sub", "u")
            .set_expires_at(exp_dt)
            .set_key(secret_key)
            .sign()
        )
        decoded = JWTUtil.decode(token, secret_key)
        assert abs(decoded["exp"] - int(exp_dt.timestamp())) <= 1

    def test_builder_set_not_before(self, secret_key: bytes) -> None:
        nbf = int(time.time()) - 10
        token = (
            JWTUtil.create()
            .set_payload("sub", "u")
            .set_not_before(nbf)
            .set_key(secret_key)
            .sign()
        )
        assert JWTUtil.validate(token, secret_key) is True

    def test_builder_set_issued_at(self, secret_key: bytes) -> None:
        iat = int(time.time())
        token = (
            JWTUtil.create()
            .set_payload("sub", "u")
            .set_issued_at(iat)
            .set_key(secret_key)
            .sign()
        )
        decoded = JWTUtil.decode(token, secret_key)
        assert decoded["iat"] == iat

    def test_builder_set_jwt_id(self, secret_key: bytes) -> None:
        token = (
            JWTUtil.create()
            .set_jwt_id("abc-123")
            .set_key(secret_key)
            .sign()
        )
        decoded = JWTUtil.decode(token, secret_key)
        assert decoded["jti"] == "abc-123"

    def test_builder_set_audience(self, secret_key: bytes) -> None:
        token = (
            JWTUtil.create()
            .set_audience("my-app")
            .set_key(secret_key)
            .sign()
        )
        decoded = JWTUtil.decode(token, secret_key)
        assert decoded["aud"] == "my-app"

    def test_builder_set_issuer(self, secret_key: bytes) -> None:
        token = (
            JWTUtil.create()
            .set_issuer("pyhutool")
            .set_key(secret_key)
            .sign()
        )
        decoded = JWTUtil.decode(token, secret_key)
        assert decoded["iss"] == "pyhutool"

    def test_builder_set_algorithm(self) -> None:
        # HS512 推荐 ≥64 字节密钥
        key_512 = b"a" * 64
        token = (
            JWTUtil.create()
            .set_algorithm("HS512")
            .set_payload("sub", "u")
            .set_key(key_512)
            .sign()
        )
        jwt_obj = JWTUtil.parse(token)
        assert jwt_obj.get_header()["alg"] == "HS512"

    def test_builder_set_header_custom(self, secret_key: bytes) -> None:
        token = (
            JWTUtil.create()
            .set_header("kid", "my-key-id")
            .set_payload("sub", "u")
            .set_key(secret_key)
            .sign()
        )
        jwt_obj = JWTUtil.parse(token)
        assert jwt_obj.get_header()["kid"] == "my-key-id"

    def test_builder_chaining(self, secret_key: bytes) -> None:
        jwt_obj = JWTUtil.create()
        # 链式调用全部返回 self
        assert jwt_obj.set_subject("x") is jwt_obj
        assert jwt_obj.set_key(secret_key) is jwt_obj
        assert jwt_obj.set_algorithm("HS256") is jwt_obj

    def test_builder_get_payload_returns_copy(self, secret_key: bytes) -> None:
        jwt_obj = JWTUtil.create().set_payload("a", 1)
        payload = jwt_obj.get_payload()
        payload["a"] = 999
        assert jwt_obj.get_payload()["a"] == 1

    def test_builder_verify_method(self, secret_key: bytes) -> None:
        token = (
            JWTUtil.create()
            .set_subject("x")
            .set_key(secret_key)
            .sign()
        )
        jwt_obj = JWTUtil.parse(token)
        assert jwt_obj.verify(secret_key) is True
        assert jwt_obj.verify(b"wrong-but-long-enough-32-bytes!!") is False

    def test_builder_validate_method(self, secret_key: bytes) -> None:
        token = (
            JWTUtil.create()
            .set_subject("x")
            .set_key(secret_key)
            .sign()
        )
        jwt_obj = JWTUtil.parse(token)
        assert jwt_obj.validate(secret_key) is True

    def test_builder_verify_without_token_raises(self, secret_key: bytes) -> None:
        jwt_obj = JWTUtil.create()
        with pytest.raises(UtilError):
            jwt_obj.verify(secret_key)

    def test_builder_verify_without_key_raises(self, secret_key: bytes) -> None:
        token = (
            JWTUtil.create()
            .set_subject("x")
            .set_key(secret_key)
            .sign()
        )
        jwt_obj = JWTUtil.parse(token)
        with pytest.raises(UtilError):
            jwt_obj.verify(key=None)

    def test_builder_repr(self, secret_key: bytes) -> None:
        jwt_obj = JWTUtil.create().set_subject("x").set_algorithm("HS256")
        s = repr(jwt_obj)
        assert "HS256" in s
        assert "sub" in s


# ---------------------------------------------------------------------
# 边界场景
# ---------------------------------------------------------------------
class TestEdgeCases:
    def test_parse_token_with_invalid_signature(self, secret_key: bytes, wrong_key: bytes, sample_payload: dict) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        jwt_obj = JWTUtil.parse(token)
        # parse 不验签，可以读取 payload
        assert jwt_obj.get_payload()["name"] == "Alice"
        # verify 验签失败
        assert jwt_obj.verify(wrong_key) is False

    def test_token_has_three_parts(self, secret_key: bytes, sample_payload: dict) -> None:
        token = JWTUtil.encode(sample_payload, secret_key)
        assert token.count(".") == 2
