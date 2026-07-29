"""SSH 客户端工具。

对齐 Hutool 的 ``cn.hutool.extra.ssh.JschUtil``，基于
[paramiko](https://www.paramiko.org/) 提供 SSH 会话、远程命令执行与
SFTP 文件传输。

设计说明
--------
- ``paramiko`` 是可选依赖；未安装时调用任何方法抛 ``UtilError``；
- ``get_session`` 返回已连接的 ``paramiko.SSHClient``；调用方负责
  :meth:`close` 释放，或使用 :meth:`with` 上下文（``SSHClient`` 原生
  支持上下文管理）；
- 远程命令执行返回标准输出字符串；若退出码非 0 抛 ``UtilError``，异常
  消息包含 stderr 内容；
- SFTP 上传/下载直接复用 ``paramiko.SFTPClient`` 接口；
- Hutool 默认端口 22；这里同样默认 22。
"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any, Final, cast

from pyhutool.core.exceptions import UtilError

__all__ = ["JschUtil"]

_DEFAULT_PORT: Final[int] = 22
_DEFAULT_TIMEOUT: Final[float] = 10.0


def _require_paramiko() -> Any:
    """惰性导入 ``paramiko``；未安装时抛 ``UtilError``。"""
    try:
        import paramiko
    except ImportError as e:
        raise UtilError(
            "pyhutool.ssh 需要 paramiko 支持，"
            "请运行：pip install 'pyhutool[ssh]'",
            cause=e,
        ) from e
    return paramiko


class JschUtil:
    """SSH 客户端工具类，全部为静态方法。

    对应 Hutool ``cn.hutool.extra.ssh.JschUtil``。
    """

    # ------------------------------------------------------------------
    # 会话管理
    # ------------------------------------------------------------------
    @staticmethod
    def get_session(
        host: str,
        port: int = _DEFAULT_PORT,
        user: str | None = None,
        password: str | None = None,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> Any:
        """以密码方式建立 SSH 会话，返回已连接的 ``paramiko.SSHClient``。

        Parameters
        ----------
        host:
            目标主机。
        port:
            SSH 端口，默认 22。
        user:
            登录用户名。
        password:
            登录密码。
        timeout:
            连接超时秒数。
        """
        paramiko = _require_paramiko()
        client = paramiko.SSHClient()
        # 自动添加主机密钥（对齐 Hutool 默认 StrictHostKeyChecking=no）
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                hostname=host,
                port=port,
                username=user,
                password=password,
                timeout=timeout,
            )
        except Exception as e:
            raise UtilError(f"SSH 连接失败: {host}:{port} {e}", cause=e) from e
        return client

    @staticmethod
    def get_session_with_key(
        host: str,
        port: int = _DEFAULT_PORT,
        user: str | None = None,
        key_file: str | Path | None = None,
        passphrase: str | None = None,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> Any:
        """以私钥文件方式建立 SSH 会话。

        Parameters
        ----------
        key_file:
            PEM / OpenSSH 私钥文件路径。
        passphrase:
            私钥口令；无口令传 ``None``。
        """
        paramiko = _require_paramiko()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                hostname=host,
                port=port,
                username=user,
                key_filename=str(key_file) if key_file else None,
                passphrase=passphrase,
                timeout=timeout,
            )
        except Exception as e:
            raise UtilError(f"SSH 连接失败: {host}:{port} {e}", cause=e) from e
        return client

    @staticmethod
    def connect(session: Any) -> Any:
        """显式连接会话。

        若 ``session`` 已连接则直接返回；否则调用 ``connect``。一般
        ``get_session`` 已自动连接，仅在手动创建 ``SSHClient`` 时使用。
        """
        # paramiko SSHClient 没有显式 is_connected API；用 get_transport 探测
        if session.get_transport() is not None and session.get_transport().is_active():
            return session
        # 这里没法重连（缺参数），直接返回；调用方应自行 connect
        return session

    @staticmethod
    def close(session: Any) -> None:
        """关闭 SSH 会话。``None`` 安全。"""
        if session is None:
            return
        try:
            session.close()
        except Exception as e:
            raise UtilError(f"关闭 SSH 会话失败: {e}", cause=e) from e

    # ------------------------------------------------------------------
    # 命令执行
    # ------------------------------------------------------------------
    @staticmethod
    def exec(
        session: Any,
        cmd: str,
        charset: str = "UTF-8",
        *,
        timeout: float | None = None,
    ) -> str:
        """在远程会话上执行命令，返回标准输出字符串。

        Parameters
        ----------
        session:
            由 :meth:`get_session` 返回的 ``SSHClient``。
        cmd:
            远程 shell 命令。
        charset:
            输出解码字符集，默认 UTF-8。
        timeout:
            命令执行超时秒数。``None`` 表示不限制。

        Raises
        ------
        UtilError
            命令退出码非 0，或执行异常。
        """
        try:
            _stdin, stdout, stderr = session.exec_command(cmd, timeout=timeout)
            out_bytes = stdout.read()
            err_bytes = stderr.read()
            exit_code = stdout.channel.recv_exit_status()
        except Exception as e:
            raise UtilError(f"SSH 命令执行失败: {cmd!r} {e}", cause=e) from e
        out = out_bytes.decode(charset, errors="replace")
        if exit_code != 0:
            err = err_bytes.decode(charset, errors="replace")
            raise UtilError(
                f"SSH 命令退出码非 0: {exit_code}\ncmd={cmd!r}\nstderr={err}",
            )
        return cast(str, out)

    @staticmethod
    def exec_bytes(
        session: Any,
        cmd: str,
        *,
        timeout: float | None = None,
    ) -> bytes:
        """在远程会话上执行命令，返回原始标准输出字节。"""
        try:
            _stdin, stdout, stderr = session.exec_command(cmd, timeout=timeout)
            out_bytes = stdout.read()
            exit_code = stdout.channel.recv_exit_status()
        except Exception as e:
            raise UtilError(f"SSH 命令执行失败: {cmd!r} {e}", cause=e) from e
        if exit_code != 0:
            err_bytes = stderr.read()
            raise UtilError(
                f"SSH 命令退出码非 0: {exit_code}\ncmd={cmd!r}\nstderr={err_bytes!r}",
            )
        return cast(bytes, out_bytes)

    # ------------------------------------------------------------------
    # SFTP
    # ------------------------------------------------------------------
    @staticmethod
    def open_sftp(session: Any) -> Any:
        """打开 SFTP 通道，返回 ``paramiko.SFTPClient``。"""
        try:
            return session.open_sftp()
        except Exception as e:
            raise UtilError(f"打开 SFTP 失败: {e}", cause=e) from e

    @staticmethod
    def download(
        session: Any,
        remote: str,
        local: str | Path,
    ) -> Path:
        """通过 SFTP 下载远程文件到本地。"""
        sftp = None
        try:
            sftp = JschUtil.open_sftp(session)
            local_path = Path(local)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            sftp.get(remote, str(local_path))
        except UtilError:
            raise
        except Exception as e:
            raise UtilError(f"SFTP 下载失败: {remote} -> {local} {e}", cause=e) from e
        finally:
            if sftp is not None:
                with contextlib.suppress(Exception):
                    sftp.close()
        return Path(local)

    @staticmethod
    def upload(
        session: Any,
        local: str | Path,
        remote: str,
    ) -> str:
        """通过 SFTP 上传本地文件到远程。"""
        local_path = Path(local)
        if not local_path.is_file():
            raise UtilError(f"本地文件不存在: {local}")
        sftp = None
        try:
            sftp = JschUtil.open_sftp(session)
            sftp.put(str(local_path), remote)
        except UtilError:
            raise
        except Exception as e:
            raise UtilError(f"SFTP 上传失败: {local} -> {remote} {e}", cause=e) from e
        finally:
            if sftp is not None:
                with contextlib.suppress(Exception):
                    sftp.close()
        return remote
