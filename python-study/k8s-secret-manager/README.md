# K8s Secret Manager

基于 Python FastAPI + Tortoise-ORM + MySQL 的 K8s 多环境运维管理后台。

## 技术栈

- **项目构建**: uv workspace（单项目多微服务 Monorepo）
- **后端框架**: FastAPI + Tortoise-ORM + MySQL
- **K8s 操作**: kubernetes-python-sdk（主）+ kubectl（备）
- **认证授权**: JWT（HS256）+ bcrypt 密码哈希
- **加密存储**: AES-256-CBC（凭据密码加密）
- **前端**: Vue 3 + Element Plus（管理界面）
- **部署**: Systemd / Docker Compose / K8s

## 项目结构

```
k8s-secret-manager/
├── packages/
│   ├── core/               # 共享核心库
│   │   └── src/ksm_core/   # 配置、DB、异常、安全、加密、K8s 客户端
│   ├── auth-service/       # 认证授权服务（登录、用户CRUD、角色权限）
│   ├── env-service/        # 环境管理服务（集群CRUD、命名空间、连通性）
│   ├── secret-service/     # 密钥管理服务（Secret查询、凭据管理、审计）
│   ├── toolbox-service/    # 工具箱服务（在线工具、导航链接）
│   └── api-gateway/        # API 网关（聚合路由、审计日志、仪表盘）
├── deploy/
│   ├── docker-compose.yml  # Docker Compose 部署
│   ├── k8s/                # Kubernetes 部署清单
│   └── systemd/            # Systemd 服务单元文件
├── docs/
│   └── sql/init.sql        # 数据库 DDL
└── scripts/
    └── init_db.py          # 数据库初始化和管理员创建脚本
```

## 快速开始

### 1. 环境要求

- Python >= 3.12
- uv >= 0.4
- MySQL 8.0+

### 2. 初始化

```bash
# 克隆项目
git clone <repo-url> k8s-secret-manager
cd k8s-secret-manager

# 配置环境变量
cp .env.example .env
# 编辑 .env 修改数据库连接信息

# 安装依赖
uv sync --all-packages

# 初始化数据库（创建表 + 默认管理员 admin / admin123）
uv run python scripts/init_db.py
```

### 3. 启动服务

独立启动微服务（开发模式）：

```bash
# 方式一：各服务独立终端
uv run --package ksm-gateway uvicorn ksm_gateway.main:app --reload --port 8000
uv run --package ksm-auth uvicorn ksm_auth.main:app --reload --port 8001
uv run --package ksm-env uvicorn ksm_env.main:app --reload --port 8002
uv run --package ksm-secret uvicorn ksm_secret.main:app --reload --port 8003
uv run --package ksm-toolbox uvicorn ksm_toolbox.main:app --reload --port 8004

# 方式二：或直接运行脚本（每个服务）
uv run --package ksm-auth python -m ksm_auth.main
```

API 文档访问：http://localhost:8000/docs

### 4. 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin  | admin123 | 管理员 |

## API 概览

| 模块 | 路径前缀 | 主要功能 |
|------|---------|---------|
| 认证 | `/api/v1/auth` | 登录、个人信息 |
| 用户管理 | `/api/v1/users` | 用户CRUD、密码重置、环境授权 |
| 环境管理 | `/api/v1/environments` | 环境CRUD、命名空间列表、连通性检测 |
| Secret查询 | `/api/v1/secrets` | Secret列表、密钥查看、缓存同步 |
| 凭据管理 | `/api/v1/credentials` | 凭据CRUD、明文查看(审计)、导出 |
| 审计日志 | `/api/v1/audit-logs` | 日志查询、CSV导出 |
| 工具箱 | `/api/v1/tools` | JSON/Base64/URL/时间戳/正则/UUID/IP/端口 |
| 导航链接 | `/api/v1/links` | 链接CRUD |
| 仪表盘 | `/api/v1/dashboard` | 统计概览 |

## 部署方案

### Docker Compose

```bash
docker compose -f deploy/docker-compose.yml up -d --build
```

### Systemd

```bash
# 1. 部署项目到 /opt/k8s-secret-manager
# 2. 复制 .env.example 为 .env 并配置
# 3. 安装服务
sudo cp deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start ksm-auth ksm-env ksm-secret ksm-toolbox ksm-gateway
sudo systemctl enable ksm-auth ksm-env ksm-secret ksm-toolbox ksm-gateway
```

### Kubernetes

```bash
kubectl apply -f deploy/k8s/
```

## 开发指南

### 添加新依赖

```bash
uv add --package <package-name> <dependency>
```

### 运行测试

```bash
uv run --package ksm-core pytest
```
