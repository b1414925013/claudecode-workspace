"""JschUtil 单元测试。

无真实 SSH 服务器，全部基于 ``unittest.mock`` 模拟 ``paramiko.SSHClient`` 与
``paramiko.SFTPClient``。
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pyhutool.core.exceptions import UtilError
from pyhutool.extra.ssh import JschUtil

# 模块级跳过：若环境未装 paramiko，跳过所有用例
paramiko_available = True
try:
    import paramiko  # noqa: F401
except ImportError:
    paramiko_available = False

pytestmark = pytest.mark.skipif(
    not paramiko_available, reason="需要 paramiko"
)


# ---------------------------------------------------------------------
# Mock 工厂
# ---------------------------------------------------------------------
def _make_mock_client() -> MagicMock:
    """构造一个模拟 SSHClient，已连接状态。"""
    client = MagicMock()
    # get_transport().is_active() -> True
    transport = MagicMock()
    transport.is_active.return_value = True
    client.get_transport.return_value = transport
    # exec_command 返回 (stdin, stdout, stderr)
    stdout = MagicMock()
    stdout.read.return_value = b"hello\n"
    stdout.channel.recv_exit_status.return_value = 0
    stderr = MagicMock()
    stderr.read.return_value = b""
    stdin = MagicMock()
    client.exec_command.return_value = (stdin, stdout, stderr)
    # open_sftp 返回 mock SFTPClient
    sftp = MagicMock()
    client.open_sftp.return_value = sftp
    return client


# ---------------------------------------------------------------------
# get_session
# ---------------------------------------------------------------------
class TestGetSession:
    @patch("paramiko.SSHClient")
    def test_get_session_password(self, mock_ssh_cls: MagicMock) -> None:
        mock_client = _make_mock_client()
        mock_ssh_cls.return_value = mock_client
        # 因 _require_paramiko 内部 import paramiko，需用 patch 整个 paramiko
        # 但这里 mock_ssh_cls 已是 SSHClient 类，client.set_missing_host_key_policy
        # 也会被 mock，OK
        session = JschUtil.get_session("host", 22, "user", "pwd")
        assert session is mock_client
        mock_client.connect.assert_called_once()
        kwargs = mock_client.connect.call_args.kwargs
        assert kwargs["hostname"] == "host"
        assert kwargs["port"] == 22
        assert kwargs["username"] == "user"
        assert kwargs["password"] == "pwd"

    @patch("paramiko.SSHClient")
    def test_get_session_default_port(self, mock_ssh_cls: MagicMock) -> None:
        mock_client = _make_mock_client()
        mock_ssh_cls.return_value = mock_client
        JschUtil.get_session("host", user="u", password="p")
        kwargs = mock_client.connect.call_args.kwargs
        assert kwargs["port"] == 22

    @patch("paramiko.SSHClient")
    def test_get_session_connect_failure_raises(self, mock_ssh_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.connect.side_effect = OSError("connection refused")
        mock_ssh_cls.return_value = mock_client
        with pytest.raises(UtilError):
            JschUtil.get_session("host", 22, "u", "p")

    @patch("paramiko.SSHClient")
    def test_get_session_with_key(self, mock_ssh_cls: MagicMock) -> None:
        mock_client = _make_mock_client()
        mock_ssh_cls.return_value = mock_client
        session = JschUtil.get_session_with_key(
            "host", 22, "user", key_file="/path/to/key", passphrase="phrase"
        )
        assert session is mock_client
        kwargs = mock_client.connect.call_args.kwargs
        assert kwargs["key_filename"] == "/path/to/key"
        assert kwargs["passphrase"] == "phrase"


# ---------------------------------------------------------------------
# connect / close
# ---------------------------------------------------------------------
class TestConnectClose:
    def test_close_none_safe(self) -> None:
        # 不应抛错
        JschUtil.close(None)

    def test_close_calls_close(self) -> None:
        client = _make_mock_client()
        JschUtil.close(client)
        client.close.assert_called_once()

    def test_close_failure_raises(self) -> None:
        client = MagicMock()
        client.close.side_effect = OSError("oops")
        with pytest.raises(UtilError):
            JschUtil.close(client)

    def test_connect_already_active(self) -> None:
        client = _make_mock_client()
        result = JschUtil.connect(client)
        # 已激活时不应该再次 connect
        assert result is client
        client.connect.assert_not_called()


# ---------------------------------------------------------------------
# exec
# ---------------------------------------------------------------------
class TestExec:
    def test_exec_returns_stdout_str(self) -> None:
        client = _make_mock_client()
        out = JschUtil.exec(client, "ls -la")
        assert out == "hello\n"

    def test_exec_with_charset(self) -> None:
        client = _make_mock_client()
        # 默认 UTF-8
        JschUtil.exec(client, "echo hi")
        args, _ = client.exec_command.call_args
        assert args[0] == "echo hi"

    def test_exec_nonzero_exit_raises(self) -> None:
        client = _make_mock_client()
        # 修改 stdout.exit_status 为非 0
        client.exec_command.return_value[1].channel.recv_exit_status.return_value = 1
        with pytest.raises(UtilError):
            JschUtil.exec(client, "false")

    def test_exec_exception_wrapped(self) -> None:
        client = MagicMock()
        client.exec_command.side_effect = OSError("ssh broken")
        with pytest.raises(UtilError):
            JschUtil.exec(client, "ls")

    def test_exec_bytes_returns_bytes(self) -> None:
        client = _make_mock_client()
        out = JschUtil.exec_bytes(client, "ls")
        assert out == b"hello\n"

    def test_exec_bytes_nonzero_raises(self) -> None:
        client = _make_mock_client()
        client.exec_command.return_value[1].channel.recv_exit_status.return_value = 2
        with pytest.raises(UtilError):
            JschUtil.exec_bytes(client, "false")


# ---------------------------------------------------------------------
# SFTP
# ---------------------------------------------------------------------
class TestSftp:
    def test_open_sftp(self) -> None:
        client = _make_mock_client()
        sftp = JschUtil.open_sftp(client)
        assert sftp is client.open_sftp.return_value

    def test_open_sftp_failure_raises(self) -> None:
        client = MagicMock()
        client.open_sftp.side_effect = OSError("no sftp")
        with pytest.raises(UtilError):
            JschUtil.open_sftp(client)

    def test_download(self, tmp_path: Path) -> None:
        client = _make_mock_client()
        local = tmp_path / "out.txt"
        # 父目录已存在，确保 mkdir 不会失败
        result = JschUtil.download(client, "/remote/file.txt", local)
        assert result == local
        sftp = client.open_sftp.return_value
        sftp.get.assert_called_once_with("/remote/file.txt", str(local))

    def test_download_creates_parent_dir(self, tmp_path: Path) -> None:
        client = _make_mock_client()
        local = tmp_path / "subdir" / "out.txt"
        JschUtil.download(client, "/remote/x", local)
        assert local.parent.exists()
        sftp = client.open_sftp.return_value
        sftp.get.assert_called_once()

    def test_download_failure_raises(self, tmp_path: Path) -> None:
        client = _make_mock_client()
        client.open_sftp.return_value.get.side_effect = OSError("no file")
        with pytest.raises(UtilError):
            JschUtil.download(client, "/remote/x", tmp_path / "out.txt")

    def test_upload(self, tmp_path: Path) -> None:
        client = _make_mock_client()
        local = tmp_path / "in.txt"
        local.write_bytes(b"data")
        result = JschUtil.upload(client, local, "/remote/in.txt")
        assert result == "/remote/in.txt"
        sftp = client.open_sftp.return_value
        sftp.put.assert_called_once_with(str(local), "/remote/in.txt")

    def test_upload_missing_local_raises(self, tmp_path: Path) -> None:
        client = _make_mock_client()
        local = tmp_path / "nope.txt"
        with pytest.raises(UtilError):
            JschUtil.upload(client, local, "/remote/x")

    def test_upload_failure_raises(self, tmp_path: Path) -> None:
        client = _make_mock_client()
        local = tmp_path / "in.txt"
        local.write_bytes(b"data")
        client.open_sftp.return_value.put.side_effect = OSError("denied")
        with pytest.raises(UtilError):
            JschUtil.upload(client, local, "/remote/x")

    def test_download_closes_sftp(self, tmp_path: Path) -> None:
        """下载完成后应关闭 sftp 通道。"""
        client = _make_mock_client()
        local = tmp_path / "out.txt"
        JschUtil.download(client, "/remote/x", local)
        sftp = client.open_sftp.return_value
        sftp.close.assert_called_once()

    def test_upload_closes_sftp(self, tmp_path: Path) -> None:
        """上传完成后应关闭 sftp 通道。"""
        client = _make_mock_client()
        local = tmp_path / "in.txt"
        local.write_bytes(b"data")
        JschUtil.upload(client, local, "/remote/x")
        sftp = client.open_sftp.return_value
        sftp.close.assert_called_once()


# ---------------------------------------------------------------------
# 边界场景
# ---------------------------------------------------------------------
class TestEdgeCases:
    def test_exec_with_timeout(self) -> None:
        client = _make_mock_client()
        JschUtil.exec(client, "ls", timeout=5.0)
        kwargs = client.exec_command.call_args.kwargs
        assert kwargs["timeout"] == 5.0
