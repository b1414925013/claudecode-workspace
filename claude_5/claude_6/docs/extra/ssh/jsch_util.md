# JschUtil SSH/SFTP

`pyhutool.extra.ssh.JschUtil` 对齐 Hutool `cn.hutool.extra.ssh.JschUtil`，
基于 [paramiko](https://www.paramiko.org/) 提供 SSH 会话、远程命令执行
与 SFTP 文件传输。

## 安装

```bash
pip install "pyhutool[ssh]"
```

未安装 `paramiko` 时调用任何方法都会抛 `UtilError` 提示安装。

## 建立会话

### 密码登录

```python
from pyhutool.extra.ssh import JschUtil

client = JschUtil.get_session(
    host="192.168.1.10",
    port=22,
    user="root",
    password="pwd",
    timeout=10.0,
)
# client 是已连接的 paramiko.SSHClient
```

### 私钥登录

```python
client = JschUtil.get_session_with_key(
    host="192.168.1.10",
    user="root",
    key_file="~/.ssh/id_rsa",
    passphrase=None,
)
```

## 执行命令

```python
# 返回标准输出字符串
out = JschUtil.exec(client, "uname -a")

# 指定字符集
out = JschUtil.exec(client, "ls", charset="GBK")

# 返回原始字节
raw = JschUtil.exec_bytes(client, "cat /etc/hostname")

# 设置超时
out = JschUtil.exec(client, "long_task", timeout=30.0)
```

退出码非 0 时抛 `UtilError`，异常消息含 stderr。

## SFTP 文件传输

```python
# 下载
JschUtil.download(client, "/var/log/syslog", "./local.log")

# 上传
JschUtil.upload(client, "./local.txt", "/tmp/remote.txt")

# 直接打开 SFTP 通道（多次操作时复用）
sftp = JschUtil.open_sftp(client)
sftp.listdir("/tmp")
sftp.stat("/etc/passwd")
sftp.close()
```

## 关闭会话

```python
JschUtil.close(client)   # None 安全
```

`paramiko.SSHClient` 也支持 `with` 上下文：

```python
with JschUtil.get_session(host=..., user=..., password=...) as client:
    JschUtil.exec(client, "ls")
```

## API 参考

| 方法 | 说明 |
|------|------|
| `get_session(host, port=22, user, password, *, timeout=10)` | 密码会话 |
| `get_session_with_key(host, port=22, user, key_file, passphrase=None, *, timeout=10)` | 私钥会话 |
| `connect(session)` | 显式连接（已连接则幂等） |
| `close(session)` | 关闭会话（None 安全） |
| `exec(session, cmd, charset="UTF-8", *, timeout=None)` | 执行命令，返回字符串 |
| `exec_bytes(session, cmd, *, timeout=None)` | 执行命令，返回字节 |
| `open_sftp(session)` | 打开 SFTP 通道 |
| `download(session, remote, local)` | 下载文件 |
| `upload(session, local, remote)` | 上传文件 |

## 与 Hutool 的差异

| 方面 | Hutool (Java) | pyhutool (Python) |
|------|---------------|-------------------|
| 底层 | JSch | paramiko |
| 主机密钥策略 | 默认 `yes` | 默认 `AutoAddPolicy`（自动接受） |
| 命令返回 | `String` | `str` 或 `bytes` |
| 退出码处理 | 调用方检查 | 非 0 自动抛 `UtilError` |
| SFTP 关闭 | 手动 | `download`/`upload` 自动关闭 |
| 依赖 | 内置 | `paramiko` (extras) |

## 安全提示

- `AutoAddPolicy` 会自动接受未知主机密钥，生产环境请改用
  `RejectPolicy` 或预先部署 `known_hosts`；
- 私钥请使用强口令保护，避免明文存储；
- 长连接会话注意设置 `keepalive`（paramiko `Transport.set_keepalive`）。
