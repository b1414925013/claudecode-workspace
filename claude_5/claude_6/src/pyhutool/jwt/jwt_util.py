"""JWT 工具。

对齐 Hutool 的 ``cn.hutool.jwt.JWTUtil`` 与 ``cn.hutool.jwt.JWT``，基于
[PyJWT](https://pyjwt.readthedocs.io) 提供签发 / 解析 / 验证 JWT 的能力。

设计说明
--------
- ``pyjwt`` 是可选依赖；未安装时调用任何方法抛 ``UtilError``；
- 同时支持 builder 模式（``JWT`` 类，链式 set）与静态工具（``JWTUtil``）；
- ``datetime`` 时间字段会自动转 Unix 时间戳（秒）；
- 默认算法 ``HS256``，密钥 ``bytes`` / ``str`` 都可，``str`` 按 UTF-8 编码；
- ``verify=False`` 模式仅解码不验签，用于查看 token 内容；正式验证须传 ``key``。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Final, cast

from pyhutool.core.exceptions import UtilError

__all__ = ["JWT", "JWTUtil"]

_DEFAULT_ALG: Final[str] = "HS256"


def _require_jwt() -> Any:
    """惰性导入 ``jwt``（PyJWT）；未安装时抛 ``UtilError``。"""
    try:
        import jwt as pyjwt
    except ImportError as e:
        raise UtilError(
            "pyhutool.jwt 需要 pyjwt 支持，请运行：pip install 'pyhutool[jwt]'",
            cause=e,
        ) from e
    return pyjwt


def _to_unix_timestamp(value: int | datetime) -> int:
    """``int`` 视为 Unix 时间戳；``datetime`` 转 Unix 时间戳（秒）。

    naive ``datetime`` 视为本地时区；aware ``datetime`` 用其时区。
    """
    if isinstance(value, int):
        return value
    if isinstance(value.tzinfo, type(None)):
        # naive → 视为本地时间
        return int(value.timestamp())
    return int(value.timestamp())


def _to_key_bytes(key: bytes | str) -> bytes | str:
    """``str`` key 保留原样（PyJWT 内部会处理），``bytes`` 直接返回。

    PyJWT 对 HS* 算法接受 ``str`` 或 ``bytes``；对 RS*/ES* 需要 PEM 格式 ``str``。
    这里不做强制转换，让 PyJWT 自行决定。
    """
    return key


class JWT:
    """JWT 对象，builder + 载体。

    对应 Hutool ``cn.hutool.jwt.JWT``。链式 setter 风格，最后调用
    :meth:`sign` 生成 token 字符串。

    也可以通过 :meth:`JWTUtil.parse` 从已有 token 构造，此时 payload /
    header 已填充，可以 :meth:`verify` 验签或 :meth:`get_payload` 读取。
    """

    def __init__(self) -> None:
        """初始化空 JWT。"""
        self._payload: dict[str, Any] = {}
        self._header: dict[str, Any] = {}
        self._key: bytes | str | None = None
        self._algorithm: str = _DEFAULT_ALG
        self._token: str | None = None

    # ------------------------------------------------------------------
    # Payload 标准 claim
    # ------------------------------------------------------------------
    def set_payload(self, name: str, value: Any) -> JWT:
        """设置任意 claim。链式调用。"""
        self._payload[name] = value
        return self

    def set_issuer(self, iss: str) -> JWT:
        """设置 ``iss`` (issuer)。"""
        self._payload["iss"] = iss
        return self

    def set_subject(self, sub: str) -> JWT:
        """设置 ``sub`` (subject)。"""
        self._payload["sub"] = sub
        return self

    def set_audience(self, aud: str) -> JWT:
        """设置 ``aud`` (audience)。"""
        self._payload["aud"] = aud
        return self

    def set_expires_at(self, exp: int | datetime) -> JWT:
        """设置 ``exp`` (expiration time)。``datetime`` 会转 Unix 时间戳。"""
        self._payload["exp"] = _to_unix_timestamp(exp)
        return self

    def set_not_before(self, nbf: int | datetime) -> JWT:
        """设置 ``nbf`` (not before)。"""
        self._payload["nbf"] = _to_unix_timestamp(nbf)
        return self

    def set_issued_at(self, iat: int | datetime) -> JWT:
        """设置 ``iat`` (issued at)。"""
        self._payload["iat"] = _to_unix_timestamp(iat)
        return self

    def set_jwt_id(self, jti: str) -> JWT:
        """设置 ``jti`` (JWT ID)。"""
        self._payload["jti"] = jti
        return self

    # ------------------------------------------------------------------
    # Header / 算法 / 密钥
    # ------------------------------------------------------------------
    def set_algorithm(self, algorithm: str) -> JWT:
        """设置签名算法（默认 ``HS256``）。"""
        self._algorithm = algorithm
        self._header["alg"] = algorithm
        return self

    def set_key(self, key: bytes | str) -> JWT:
        """设置签名密钥。HS* 接受 ``bytes``/``str``；RS*/ES* 接受 PEM ``str``。"""
        self._key = key
        return self

    def set_header(self, name: str, value: Any) -> JWT:
        """设置自定义 header 字段（如 ``kid``）。"""
        self._header[name] = value
        return self

    # ------------------------------------------------------------------
    # 签发 / 验证
    # ------------------------------------------------------------------
    def sign(self) -> str:
        """按当前 payload + key + algorithm 签发 token，返回字符串。

        Raises
        ------
        UtilError
            未设置 key，或 PyJWT 签发失败。
        """
        if self._key is None:
            raise UtilError("JWT 签发前必须调用 set_key 设置密钥")
        pyjwt = _require_jwt()
        try:
            token = pyjwt.encode(
                self._payload,
                _to_key_bytes(self._key),
                algorithm=self._algorithm,
                headers=self._header or None,
            )
        except Exception as e:
            raise UtilError(f"JWT 签发失败: {e}", cause=e) from e
        # PyJWT 2.x 返回 str，1.x 返回 bytes；统一成 str
        if isinstance(token, bytes):
            token = token.decode("UTF-8")
        self._token = token
        return cast(str, token)

    def verify(self, key: bytes | str | None = None) -> bool:
        """验证当前 token 的签名。

        Parameters
        ----------
        key:
            验证密钥。``None`` 时使用 :meth:`set_key` 设置的密钥。

        Returns
        -------
        bool
            签名通过返回 ``True``，否则返回 ``False``。

        Raises
        ------
        UtilError
            token 未签发或密钥未设置。
        """
        if self._token is None:
            raise UtilError("当前 JWT 没有 token，无法验证")
        actual_key = key if key is not None else self._key
        if actual_key is None:
            raise UtilError("验签前必须提供密钥")
        pyjwt = _require_jwt()
        try:
            pyjwt.decode(
                self._token,
                _to_key_bytes(actual_key),
                algorithms=[self._algorithm],
                options={"verify_exp": False, "verify_nbf": False,
                         "verify_aud": False},
            )
            return True
        except pyjwt.PyJWTError:
            return False

    def validate(self, key: bytes | str | None = None) -> bool:
        """验证签名 + 检查 ``exp`` / ``nbf`` 时间约束。"""
        if self._token is None:
            raise UtilError("当前 JWT 没有 token，无法验证")
        actual_key = key if key is not None else self._key
        if actual_key is None:
            raise UtilError("验签前必须提供密钥")
        pyjwt = _require_jwt()
        try:
            pyjwt.decode(
                self._token,
                _to_key_bytes(actual_key),
                algorithms=[self._algorithm],
                options={"verify_aud": False},
            )
            return True
        except pyjwt.PyJWTError:
            return False

    # ------------------------------------------------------------------
    # 访问器
    # ------------------------------------------------------------------
    def get_payload(self) -> dict[str, Any]:
        """返回 payload 字典。"""
        return dict(self._payload)

    def get_header(self) -> dict[str, Any]:
        """返回 header 字典。"""
        return dict(self._header)

    def get_token(self) -> str | None:
        """返回已签发的 token；未签发返回 ``None``。"""
        return self._token

    def __repr__(self) -> str:
        """返回 JWT 可打印表示。"""
        return f"<JWT alg={self._algorithm!r} payload_keys={list(self._payload)}>"


class JWTUtil:
    """JWT 工具类，全部为静态方法。

    对应 Hutool ``cn.hutool.jwt.JWTUtil``。
    """

    # ------------------------------------------------------------------
    # 创建
    # ------------------------------------------------------------------
    @staticmethod
    def create() -> JWT:
        """创建空 JWT 对象，用于 builder 模式。"""
        return JWT()

    @staticmethod
    def encode(
        payload: dict[str, Any],
        key: bytes | str,
        algorithm: str = _DEFAULT_ALG,
    ) -> str:
        """把 payload 直接编码为 token，等价于 PyJWT ``jwt.encode``。"""
        pyjwt = _require_jwt()
        try:
            token = pyjwt.encode(
                payload,
                _to_key_bytes(key),
                algorithm=algorithm,
            )
        except Exception as e:
            raise UtilError(f"JWT 编码失败: {e}", cause=e) from e
        if isinstance(token, bytes):
            token = token.decode("UTF-8")
        return cast(str, token)

    # ------------------------------------------------------------------
    # 解析
    # ------------------------------------------------------------------
    @staticmethod
    def parse(token: str) -> JWT:
        """解析 token，返回填充了 payload / header 的 ``JWT`` 对象。

        不验签。要验签请用 :meth:`verify` 或 :meth:`validate`。
        """
        pyjwt = _require_jwt()
        try:
            # 不验签
            decoded = pyjwt.decode(
                token,
                options={"verify_signature": False},
            )
            header = pyjwt.get_unverified_header(token)
        except pyjwt.PyJWTError as e:
            raise UtilError(f"JWT 解析失败: {e}", cause=e) from e

        jwt_obj = JWT()
        jwt_obj._payload = cast(dict[str, Any], decoded)
        jwt_obj._header = cast(dict[str, Any], header)
        alg = str(header.get("alg", _DEFAULT_ALG))
        jwt_obj._algorithm = alg
        jwt_obj._token = token
        return jwt_obj

    @staticmethod
    def decode(
        token: str,
        key: bytes | str | None = None,
        *,
        verify: bool = True,
        algorithm: str = _DEFAULT_ALG,
    ) -> dict[str, Any]:
        """解码 token，返回 payload 字典。

        Parameters
        ----------
        token:
            JWT 字符串。
        key:
            验签密钥。``verify=False`` 时可不传。
        verify:
            是否验签。``False`` 时仅解码。
        algorithm:
            期望的算法，默认 ``HS256``。
        """
        pyjwt = _require_jwt()
        if not verify:
            try:
                return cast(
                    dict[str, Any],
                    pyjwt.decode(token, options={"verify_signature": False}),
                )
            except pyjwt.PyJWTError as e:
                raise UtilError(f"JWT 解码失败: {e}", cause=e) from e
        if key is None:
            raise UtilError("verify=True 时必须提供 key")
        try:
            return cast(
                dict[str, Any],
                pyjwt.decode(
                    token,
                    _to_key_bytes(key),
                    algorithms=[algorithm],
                    options={"verify_aud": False},
                ),
            )
        except pyjwt.PyJWTError as e:
            raise UtilError(f"JWT 验签/解码失败: {e}", cause=e) from e

    # ------------------------------------------------------------------
    # 验证
    # ------------------------------------------------------------------
    @staticmethod
    def verify(token: str, key: bytes | str, algorithm: str = _DEFAULT_ALG) -> bool:
        """验证签名是否有效，不检查 ``exp``/``nbf`` 时间。"""
        pyjwt = _require_jwt()
        try:
            pyjwt.decode(
                token,
                _to_key_bytes(key),
                algorithms=[algorithm],
                options={
                    "verify_exp": False,
                    "verify_nbf": False,
                    "verify_aud": False,
                },
            )
            return True
        except pyjwt.PyJWTError:
            return False

    @staticmethod
    def validate(
        token: str,
        key: bytes | str,
        algorithm: str = _DEFAULT_ALG,
    ) -> bool:
        """验证签名 + 检查 ``exp`` / ``nbf`` 时间约束。"""
        pyjwt = _require_jwt()
        try:
            pyjwt.decode(
                token,
                _to_key_bytes(key),
                algorithms=[algorithm],
                options={"verify_aud": False},
            )
            return True
        except pyjwt.PyJWTError:
            return False
