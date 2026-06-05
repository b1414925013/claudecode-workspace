# NebulaGraph MCP 服务器

通过 SSH 跳板机连接 NebulaGraph 数据库的 MCP 服务器工具。

## 功能概述

| 工具 | 说明 |
|------|------|
| `connect_nebula` | 建立连接，自动从项目 .env 读取配置 |
| `reload_config` | 重新加载配置 |
| `exec_ngql` | 执行 nGQL 语句（需先建立连接） |
| `disconnect_nebula` | 断开连接 |
| `get_connection_status` | 查看当前连接状态 |

## 连接逻辑

```
1. 检测目标服务器 SSH 端口是否可达
   ├─ 可达 → 直连目标服务器
   └─ 不可达 → 检查跳板机配置
                ├─ 已配置跳板机 → 通过跳板机连接
                └─ 未配置跳板机 → 返回错误
2. su -root 切换到管理员
3. docker exec 进入 nebula 容器
4. nebula-console 连接数据库
5. 执行 nGQL 语句
```

## 项目结构

```
nebula-mcp-server/
├── src/
│   └── nebula_mcp/
│       ├── __init__.py
│       └── server.py          # 主入口文件
├── pyproject.toml
├── .env.example               # 配置模板
└── README.md
```

## 安装方式

### 方式一：直接运行（推荐开发测试用）

```bash
cd D:/develop/claudecode-workspace/claude_4/nebula-mcp-server
uv sync
uv run nebula-mcp-server
```

### 方式二：全局安装为 CLI 工具

```bash
cd D:/develop/claudecode-workspace/claude_4/nebula-mcp-server
uv pip install -e .
nebula-mcp-server
```

## 配置加载（核心功能）

**配置文件查找顺序：**

1. `NEBULA_CONFIG_PATH` 环境变量指定的路径
2. 当前工作目录下的 `nebula.env` 文件（**首选**）
3. 当前工作目录下的 `.env` 文件（**次选**）
4. 环境变量（兜底）

**这意味着：**
- MCP 服务器**全局安装**后
- 用户在**自己的项目根目录**放置 `nebula.env` 或 `.env` 文件
- 调用 `connect_nebula` 时自动从项目目录读取配置

## 在 Claude Code 中配置

### 全局配置

在 Claude Code 的 `settings.json` 中添加：

```json
{
  "mcpServers": {
    "nebula-mcp-server": {
      "command": "uv",
      "args": ["run", "nebula-mcp-server"]
    }
  }
}
```

### 或使用全局安装后的命令

```json
{
  "mcpServers": {
    "nebula-mcp-server": {
      "command": "nebula-mcp-server"
    }
  }
}
```

## 使用示例

### 1. 在项目中创建 .env 文件

在项目根目录创建 `D:/your-project/.env`：

```env
# 目标服务器配置
TARGET_HOST=10.0.0.50
TARGET_USERNAME=paas
TARGET_PASSWORD=your_password

# NebulaGraph 配置
NEBULA_SPACE=my_space
NEBULA_PASSWORD=nebula_password
NEBULA_HOSTS=192.168.1.200:9669
```

### 2. 调用 MCP 工具

```
1. 调用 connect_nebula 工具建立连接
2. 调用 exec_ngql 执行查询
3. 完成后调用 disconnect_nebula 断开连接
```

### 3. 切换项目

如果用户同时有多个项目，每个项目有自己的数据库配置：

```
project-a/
├── .env  # 配置 A 项目的数据库

project-b/
├── .env  # 配置 B 项目的数据库
```

用户只需要在不同项目目录下使用 Claude Code，MCP 会自动读取对应目录下的配置文件。

## 配置文件说明

| 配置项 | 说明 | 必填 |
|--------|------|------|
| `TARGET_HOST` | 目标服务器 IP | 是 |
| `TARGET_PORT` | 目标服务器 SSH 端口，默认 22 | 否 |
| `TARGET_USERNAME` | 目标服务器用户名（paas） | 是 |
| `TARGET_PASSWORD` | 目标服务器密码（与密钥二选一） | 否 |
| `TARGET_KEY_PATH` | 目标服务器 SSH 密钥路径 | 否 |
| `BASTION_HOST` | 跳板机 IP（可选） | 否 |
| `BASTION_USERNAME` | 跳板机用户名 | 否 |
| `BASTION_PASSWORD` | 跳板机密码 | 否 |
| `BASTION_KEY_PATH` | 跳板机 SSH 密钥路径 | 否 |
| `NEBULA_SPACE` | NebulaGraph space 名称 | 是 |
| `NEBULA_PASSWORD` | NebulaGraph 连接密码 | 是 |
| `NEBULA_HOSTS` | NebulaGraph 主机地址:端口 | 是 |
| `DOCKER_CONTAINER` | Nebula 容器名称，默认 nebula | 否 |

## 安全注意事项

1. **敏感信息**：不要将 `.env` 文件提交到版本控制系统
2. **密钥文件**：优先使用 SSH 密钥而非密码认证
3. **日志输出**：所有日志输出到 stderr，不会通过 stdout 输出

## 依赖

- `mcp>=1.0.0` - MCP SDK
- `paramiko>=3.0.0` - SSH 客户端
- `python-dotenv>=1.0.0` - 环境变量管理