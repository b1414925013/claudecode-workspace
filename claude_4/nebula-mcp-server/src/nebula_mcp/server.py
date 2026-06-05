"""
NebulaGraph MCP 服务器

通过 SSH 跳板机连接 NebulaGraph 数据库，执行 nGQL 语句。

连接流程：
1. 先检测目标服务器是否能直接连接
2. 如果能直连 → 直接连接目标服务器
3. 如果不能直连 → 通过跳板机连接
4. su -root 切换到管理员
5. docker exec 进入 nebula 容器
6. cd /opt/tmp
7. nebula-console -h -a 连接数据库
8. 输入密码
9. 执行 nGQL 语句
"""

import os
import sys
import json
import time
import re
import socket
from typing import Any, Optional
from pathlib import Path

import paramiko
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, Resource


# ============================================
# 配置管理
# ============================================

class Config:
    """配置管理类，支持从多个路径加载配置"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径，如果为 None 则自动查找
        """
        self.config_path = config_path
        self._load_config()

    def _find_config_file(self) -> Optional[str]:
        """
        查找配置文件
        优先级：
        1. NEBULA_CONFIG_PATH 环境变量指定的路径
        2. 当前工作目录下的 nebula.env 文件
        3. 当前工作目录下的 .env 文件
        """
        # 1. 检查环境变量
        env_path = os.getenv("NEBULA_CONFIG_PATH")
        if env_path and Path(env_path).exists():
            print(f"[Nebula MCP] 使用环境变量指定的配置: {env_path}", file=sys.stderr)
            return env_path

        # 2. 检查当前工作目录
        cwd = os.getcwd()
        if cwd:
            # 首选 nebula.env
            nebula_env_file = Path(cwd) / "nebula.env"
            if nebula_env_file.exists():
                print(f"[Nebula MCP] 使用项目配置: {nebula_env_file}", file=sys.stderr)
                return str(nebula_env_file)

            # 次选 .env
            env_file = Path(cwd) / ".env"
            if env_file.exists():
                print(f"[Nebula MCP] 使用项目配置: {env_file}", file=sys.stderr)
                return str(env_file)

        return None

    def _load_config(self):
        """从文件加载配置"""
        # 确定配置文件路径
        config_file = self.config_path or self._find_config_file()

        if config_file and Path(config_file).exists():
            print(f"[Nebula MCP] 加载配置文件: {config_file}", file=sys.stderr)
            load_dotenv(config_file, override=True)
        else:
            print(f"[Nebula MCP] 未找到配置文件，将使用环境变量", file=sys.stderr)

        # 跳板机配置（可选）
        self.bastion_host = os.getenv("BASTION_HOST", "")
        self.bastion_port = int(os.getenv("BASTION_PORT", "22"))
        self.bastion_username = os.getenv("BASTION_USERNAME", "")
        self.bastion_password = os.getenv("BASTION_PASSWORD", "")
        self.bastion_key_path = os.getenv("BASTION_KEY_PATH", "")

        # 目标服务器配置
        self.target_host = os.getenv("TARGET_HOST", "")
        self.target_port = int(os.getenv("TARGET_PORT", "22"))
        self.target_username = os.getenv("TARGET_USERNAME", "")
        self.target_password = os.getenv("TARGET_PASSWORD", "")
        self.target_key_path = os.getenv("TARGET_KEY_PATH", "")

        # Nebula 配置
        self.nebula_space = os.getenv("NEBULA_SPACE", "")
        self.nebula_password = os.getenv("NEBULA_PASSWORD", "")
        self.nebula_hosts = os.getenv("NEBULA_HOSTS", "")

        # Docker 容器名
        self.docker_container = os.getenv("DOCKER_CONTAINER", "nebula")

        # 工作目录（用于日志）
        self.working_dir = os.getcwd()

    def reload(self):
        """重新加载配置"""
        self._load_config()

    def has_bastion_config(self) -> bool:
        """检查是否配置了跳板机"""
        return bool(self.bastion_host and self.bastion_username)

    def validate(self) -> list[str]:
        """验证配置是否完整，返回缺失的配置项列表"""
        missing = []
        if not self.target_host:
            missing.append("TARGET_HOST")
        if not self.target_username:
            missing.append("TARGET_USERNAME")
        if not self.nebula_space:
            missing.append("NEBULA_SPACE")
        if not self.nebula_password:
            missing.append("NEBULA_PASSWORD")
        return missing

    def validate_with_bastion(self) -> list[str]:
        """验证配置是否完整（包括跳板机）"""
        missing = self.validate()
        if self.has_bastion_config():
            if not self.bastion_host:
                missing.append("BASTION_HOST")
            if not self.bastion_username:
                missing.append("BASTION_USERNAME")
        return missing


# ============================================
# SSH 连接管理器
# ============================================

class SSHConnectionManager:
    """SSH 连接管理器，处理直连或跳板机连接"""

    def __init__(self, config: Config):
        self.config = config
        self.bastion_client = None
        self.target_client = None
        self.target_channel = None
        self.connected = False
        self.used_bastion = False  # 标记是否使用了跳板机

    def _can_direct_connect(self, host: str, port: int, timeout: float = 5.0) -> tuple[bool, str]:
        """
        检测是否能直接连接到目标服务器的 SSH 端口
        返回: (是否能直连, 原因)
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                return True, "端口可达"
            else:
                return False, f"端口不可达 (errno: {result})"
        except socket.timeout:
            return False, "连接超时"
        except socket.gaierror as e:
            return False, f"主机名解析失败: {e}"
        except Exception as e:
            return False, f"检测失败: {e}"

    def _create_ssh_client(self, host: str, port: int, username: str,
                           password: str = "", key_path: str = "") -> paramiko.SSHClient:
        """创建 SSH 客户端"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs = {
            "hostname": host,
            "port": port,
            "username": username,
            "look_for_keys": True,
            "allow_agent": True,
        }

        if password:
            connect_kwargs["password"] = password

        if key_path:
            connect_kwargs["key_filename"] = key_path

        client.connect(**connect_kwargs)
        return client

    def _create_interactive_channel(self, client: paramiko.SSHClient) -> paramiko.channel.Channel:
        """创建交互式 channel"""
        transport = client.get_transport()
        if transport is None:
            raise Exception("无法获取传输通道")

        channel = transport.open_session()
        channel.set_environment_variable("TERM", "xterm-256color")
        channel.invoke_shell()
        return channel

    def connect(self) -> tuple[bool, str]:
        """
        建立 SSH 连接并进入 Nebula console
        优先尝试直连，跳板机配置仅在直连失败时使用
        返回: (是否成功, 消息)
        """
        try:
            # Step 0: 检测是否能直连目标服务器
            print(f"[Nebula MCP] 检测目标服务器 {self.config.target_host} 可达性...", file=sys.stderr)
            can_direct, direct_reason = self._can_direct_connect(
                self.config.target_host,
                self.config.target_port
            )

            if can_direct:
                print(f"[Nebula MCP] 目标服务器可直接连接，尝试直连...", file=sys.stderr)
                success, message = self._connect_direct()
                if success:
                    return success, message
                # 直连失败，且没有配置跳板机，则返回失败
                if not self.config.has_bastion_config():
                    return False, f"直连失败: {message}，且未配置跳板机无法跳转"
                # 直连失败，有跳板机配置，尝试跳板机
                print(f"[Nebula MCP] 直连失败，尝试使用跳板机...", file=sys.stderr)

            elif self.config.has_bastion_config():
                print(f"[Nebula MCP] 目标服务器无法直连 ({direct_reason})，使用跳板机...", file=sys.stderr)
                self.used_bastion = True
                return self._connect_via_bastion()
            else:
                return False, f"目标服务器不可达 ({direct_reason})，且未配置跳板机"

        except Exception as e:
            return False, f"连接失败: {str(e)}"

    def _connect_direct(self) -> tuple[bool, str]:
        """直接连接目标服务器（不通过跳板机）"""
        try:
            # 直接 SSH 到目标服务器
            if self.config.target_key_path:
                self.target_client = self._create_ssh_client(
                    self.config.target_host,
                    self.config.target_port,
                    self.config.target_username,
                    key_path=self.config.target_key_path
                )
            else:
                self.target_client = self._create_ssh_client(
                    self.config.target_host,
                    self.config.target_port,
                    self.config.target_username,
                    password=self.config.target_password
                )

            self.target_channel = self._create_interactive_channel(self.target_client)
            time.sleep(1)
            print(f"[Nebula MCP] 已直连到目标服务器 {self.config.target_host}", file=sys.stderr)

            return self._enter_nebula_console()

        except Exception as e:
            return False, f"直连失败: {str(e)}"

    def _connect_via_bastion(self) -> tuple[bool, str]:
        """通过跳板机连接目标服务器"""
        try:
            # Step 1: 连接跳板机
            print(f"[Nebula MCP] 正在连接跳板机 {self.config.bastion_host}...", file=sys.stderr)

            if self.config.bastion_key_path:
                self.bastion_client = self._create_ssh_client(
                    self.config.bastion_host,
                    self.config.bastion_port,
                    self.config.bastion_username,
                    key_path=self.config.bastion_key_path
                )
            else:
                self.bastion_client = self._create_ssh_client(
                    self.config.bastion_host,
                    self.config.bastion_port,
                    self.config.bastion_username,
                    password=self.config.bastion_password
                )

            print(f"[Nebula MCP] 跳板机连接成功，正在跳转到目标服务器...", file=sys.stderr)

            # Step 2: 通过跳板机 SSH 到目标服务器
            bastion_transport = self.bastion_client.get_transport()
            if bastion_transport is None:
                return False, "跳板机传输通道创建失败"

            # 构建 SSH 命令
            ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
            ssh_cmd += f" -p {self.config.target_port} {self.config.target_username}@{self.config.target_host}"

            # 打开 channel 用于交互式会话
            self.target_channel = bastion_transport.open_session()
            self.target_channel.set_environment_variable("TERM", "xterm-256color")
            self.target_channel.invoke_shell()

            # 发送 SSH 命令到目标服务器
            self._send_command(ssh_cmd, wait_for="password:")
            time.sleep(0.5)
            self._send_command(self.config.target_password, wait_for=None)
            time.sleep(1)

            print(f"[Nebula MCP] 已通过跳板机连接到目标服务器 {self.config.target_host}", file=sys.stderr)

            return self._enter_nebula_console()

        except Exception as e:
            return False, f"跳板机连接失败: {str(e)}"

    def _enter_nebula_console(self) -> tuple[bool, str]:
        """进入 Nebula console 的公共逻辑"""
        try:
            # Step 3: 切换到 root
            print(f"[Nebula MCP] 正在切换到 root...", file=sys.stderr)
            self._send_command("su -root", wait_for="Password:")
            time.sleep(0.5)
            self._send_command(self.config.target_password, wait_for="#")
            time.sleep(1)

            # Step 4: 进入 nebula 容器
            print(f"[Nebula MCP] 正在进入 Nebula 容器...", file=sys.stderr)
            self._send_command(f"docker exec -it {self.config.docker_container} bash", wait_for="root@")
            time.sleep(1)

            # Step 5: 切换到工作目录
            self._send_command("cd /opt/tmp", wait_for="#")
            time.sleep(0.5)

            # Step 6: 连接 Nebula console
            print(f"[Nebula MCP] 正在连接 Nebula console...", file=sys.stderr)
            console_cmd = f"nebula-console -h {self.config.nebula_hosts} -a"
            self._send_command(console_cmd, wait_for="password:")
            time.sleep(0.5)
            self._send_command(self.config.nebula_password, wait_for="nebula>")
            time.sleep(1)

            # Step 7: 选择 space
            if self.config.nebula_space:
                self._send_command(f"use {self.config.nebula_space};", wait_for="nebula>")
                time.sleep(0.5)

            self.connected = True
            connection_type = "直连" if not self.used_bastion else "跳板机"
            print(f"[Nebula MCP] NebulaGraph 连接成功！[{connection_type}] Space: {self.config.nebula_space}", file=sys.stderr)
            return True, f"连接成功 [{connection_type}]，已选择 space: {self.config.nebula_space}"

        except Exception as e:
            return False, f"进入 Nebula console 失败: {str(e)}"

    def _send_command(self, command: str, wait_for: str = None, timeout: float = 5.0) -> str:
        """发送命令并等待响应"""
        if self.target_channel is None:
            return ""

        self.target_channel.send(command + "\n")
        time.sleep(0.3)

        output = ""
        start_time = time.time()

        while True:
            if self.target_channel.recv_ready():
                chunk = self.target_channel.recv(4096).decode("utf-8", errors="ignore")
                output += chunk

                if wait_for and wait_for in output:
                    break

                if "ermission denied" in output.lower():
                    break

            if time.time() - start_time > timeout:
                break

            if not self.target_channel.active:
                break

            time.sleep(0.1)

        return output

    def exec_ngql(self, ngql: str) -> tuple[bool, str]:
        """
        执行 nGQL 语句
        返回: (是否成功, 输出结果)
        """
        if not self.connected or self.target_channel is None:
            return False, "未连接到 NebulaGraph，请先调用 connect_nebula"

        try:
            # 清理之前的输出
            while self.target_channel.recv_ready():
                self.target_channel.recv(4096)

            # 发送 nGQL 语句
            self.target_channel.send(ngql + "\n")
            time.sleep(0.5)

            # 等待结果
            output = ""
            start_time = time.time()
            prompt_count = 0

            while True:
                if self.target_channel.recv_ready():
                    chunk = self.target_channel.recv(4096).decode("utf-8", errors="ignore")
                    output += chunk

                    prompt_count = output.count("nebula>")

                    if prompt_count >= 2 or (ngql.strip().endswith(";") and prompt_count >= 1):
                        break

                if time.time() - start_time > 30.0:
                    break

                time.sleep(0.1)

            # 清理输出，只保留结果部分
            lines = output.split("\n")
            result_lines = []
            in_result = False

            for line in lines:
                if line.strip().startswith(ngql.strip()):
                    continue
                if "nebula>" in line and not in_result:
                    in_result = True
                    continue
                if line.strip() == "nebula>":
                    continue

                if in_result:
                    result_lines.append(line)

            result = "\n".join(result_lines).strip()

            if "SyntaxError" in output or "失败" in output or "error" in output.lower():
                return False, result if result else output

            return True, result if result else "执行成功（无返回数据）"

        except Exception as e:
            return False, f"执行失败: {str(e)}"

    def disconnect(self) -> tuple[bool, str]:
        """断开连接"""
        try:
            if self.target_channel:
                self.target_channel.close()
            if self.target_client:
                self.target_client.close()
            if self.bastion_client:
                self.bastion_client.close()

            self.connected = False
            self.target_channel = None
            self.target_client = None
            self.bastion_client = None

            print("[Nebula MCP] 连接已断开", file=sys.stderr)
            return True, "连接已断开"

        except Exception as e:
            return False, f"断开连接时出错: {str(e)}"


# ============================================
# 全局变量
# ============================================

config: Optional[Config] = None
connection_manager: Optional[SSHConnectionManager] = None


def get_config() -> Config:
    """获取或创建配置对象（每次调用都重新加载）"""
    global config
    # 每次获取配置时都重新加载，以获取最新的配置
    config = Config()
    return config


# ============================================
# MCP 服务器
# ============================================

server = Server(
    name="nebula-mcp-server",
    version="1.0.0",
)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="connect_nebula",
            description="连接到 NebulaGraph 数据库。优先尝试直连目标服务器，如果不可达则使用跳板机（如果配置了跳板机）。配置从当前项目根目录的 .env 文件读取。",
            inputSchema={
                "type": "object",
                "properties": {
                    "force_reconnect": {
                        "type": "boolean",
                        "description": "是否强制重新连接（如果已连接则断开后重连）",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="reload_config",
            description="重新加载配置文件，从当前项目根目录重新读取 .env 配置。",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="exec_ngql",
            description="执行 nGQL 语句。必须先调用 connect_nebula 建立连接后才能执行查询。",
            inputSchema={
                "type": "object",
                "properties": {
                    "ngql": {
                        "type": "string",
                        "description": "nGQL 语句，例如: MATCH (n) RETURN n LIMIT 10",
                    },
                },
                "required": ["ngql"],
            },
        ),
        Tool(
            name="disconnect_nebula",
            description="断开与 NebulaGraph 数据库的连接。",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_connection_status",
            description="获取当前 NebulaGraph 连接状态。",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用请求"""
    global connection_manager

    if name == "reload_config":
        # 重新加载配置
        cfg = get_config()
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "reloaded",
                        "config_file": cfg._find_config_file() or "环境变量",
                        "target_host": cfg.target_host or "未配置",
                        "nebula_space": cfg.nebula_space or "未配置",
                        "working_dir": cfg.working_dir,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            )
        ]

    if name == "connect_nebula":
        # 检查是否已连接
        if connection_manager and connection_manager.connected:
            force_reconnect = arguments.get("force_reconnect", False)
            if not force_reconnect:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"status": "already_connected", "message": "已连接到 NebulaGraph"},
                            ensure_ascii=False,
                            indent=2,
                        ),
                    )
                ]
            else:
                connection_manager.disconnect()

        # 获取最新配置（从当前工作目录加载）
        cfg = get_config()

        # 验证配置
        missing_config = cfg.validate_with_bastion()
        if missing_config:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "config_error",
                            "message": f"配置不完整，缺少: {', '.join(missing_config)}",
                            "hint": f"请在项目根目录的 .env 文件或环境变量中配置这些项",
                            "working_dir": cfg.working_dir,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    is_error=True,
                )
            ]

        # 建立连接
        connection_manager = SSHConnectionManager(cfg)
        success, message = connection_manager.connect()

        if success:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"status": "connected", "message": message},
                        ensure_ascii=False,
                        indent=2,
                    ),
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"status": "error", "message": message},
                        ensure_ascii=False,
                        indent=2,
                    ),
                    is_error=True,
                )
            ]

    elif name == "exec_ngql":
        if not connection_manager or not connection_manager.connected:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"status": "not_connected", "message": "请先调用 connect_nebula 建立连接"},
                        ensure_ascii=False,
                        indent=2,
                    ),
                    is_error=True,
                )
            ]

        ngql = arguments.get("ngql", "")
        if not ngql:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"status": "error", "message": "ngql 参数不能为空"},
                        ensure_ascii=False,
                        indent=2,
                    ),
                    is_error=True,
                )
            ]

        success, result = connection_manager.exec_ngql(ngql)

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "success" if success else "error",
                        "ngql": ngql,
                        "result": result,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                is_error=not success,
            )
        ]

    elif name == "disconnect_nebula":
        if not connection_manager:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"status": "not_connected", "message": "当前没有活跃连接"},
                        ensure_ascii=False,
                        indent=2,
                    ),
                )
            ]

        success, message = connection_manager.disconnect()
        connection_manager = None

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"status": "disconnected", "message": message},
                    ensure_ascii=False,
                    indent=2,
                ),
            )
        ]

    elif name == "get_connection_status":
        if connection_manager and connection_manager.connected:
            cfg = get_config()
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "connected",
                            "space": config.nebula_space if config else "",
                            "target_host": config.target_host if config else "",
                            "nebula_hosts": config.nebula_hosts if config else "",
                            "used_bastion": connection_manager.used_bastion,
                            "working_dir": config.working_dir if config else "",
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                )
            ]
        else:
            cfg = get_config()
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "disconnected",
                            "working_dir": cfg.working_dir,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                )
            ]

    else:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"status": "error", "message": f"未知工具: {name}"},
                    ensure_ascii=False,
                    indent=2,
                ),
                is_error=True,
            )
        ]


# ============================================
# Resources（资源）
# ============================================

@server.list_resources()
async def list_resources() -> list[Resource]:
    """列出所有可用的资源"""
    return [
        Resource(
            uri="nebula://status",
            name="nebula-status",
            description="当前 NebulaGraph 连接状态",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """读取资源内容"""
    if uri == "nebula://status":
        if connection_manager and connection_manager.connected:
            return json.dumps(
                {
                    "status": "connected",
                    "space": config.nebula_space if config else "",
                    "target_host": config.target_host if config else "",
                    "nebula_hosts": config.nebula_hosts if config else "",
                    "used_bastion": connection_manager.used_bastion,
                },
                ensure_ascii=False,
                indent=2,
            )
        else:
            return json.dumps({"status": "disconnected"})

    return json.dumps({"error": f"未知资源 URI: {uri}"})


# ============================================
# 启动服务器
# ============================================

async def main():
    """主函数"""
    print("[Nebula MCP Server] 启动中...", file=sys.stderr)
    print("[Nebula MCP Server] 等待连接请求...", file=sys.stderr)
    print("[Nebula MCP Server] 提示: 配置将从当前项目根目录的 .env 文件自动加载", file=sys.stderr)

    # 预加载一次配置用于显示
    cfg = get_config()
    config_file = cfg._find_config_file()
    if config_file:
        print(f"[Nebula MCP Server] 检测到配置文件: {config_file}", file=sys.stderr)
    else:
        print(f"[Nebula MCP Server] 未检测到配置文件，将使用环境变量", file=sys.stderr)

    # 使用 stdio 传输层
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
