# K8s Secret Manager

基于 Python FastAPI + Tortoise-ORM + MySQL + Vue 3 的 K8s 多环境运维管理后台。

## 技术栈

- **后端**: Python FastAPI + Tortoise-ORM + MySQL
- **前端**: Vue 3 + Element Plus + Pinia + Vue Router
- **K8s 操作**: kubernetes-python-sdk（主）+ kubectl（备）
- **认证授权**: JWT（HS256）+ bcrypt 密码哈希
- **加密存储**: AES-256-CBC（凭据密码加密）
- **构建**: uv workspace（Monorepo）/ Vite
- **部署**: Systemd / Docker Compose / K8s

## 项目结构

```
k8s-secret-manager/
├── backend/                    # 后端微服务（uv workspace）
│   ├── packages/
│   │   ├── core/               # 共享核心库
│   │   │   └── src/ksm_core/   # 配置、DB、异常、安全、加密、K8s 客户端
│   │   ├── auth-service/       # 认证授权服务（端口 8001）
│   │   ├── env-service/        # 环境管理服务（端口 8002）
│   │   ├── secret-service/     # 密钥管理服务（端口 8003）
│   │   ├── toolbox-service/    # 工具箱服务（端口 8004）
│   │   └── api-gateway/        # API 网关（端口 8000）
│   ├── deploy/                 # 部署配置
│   ├── docs/                   # SQL 及设计文档
│   ├── scripts/                # 初始化脚本
│   ├── pyproject.toml          # uv workspace 配置
│   └── .env                    # 环境变量
├── frontend/                   # 前端 Vue 3 项目
│   ├── src/
│   │   ├── api/                # API 接口层
│   │   ├── views/              # 页面组件
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # Pinia 状态管理
│   │   └── layouts/            # 布局组件
│   ├── vite.config.ts          # Vite 配置 + API 代理
│   └── package.json
├── logs/                       # 运行时日志
└── README.md
```

## 快速开始

### 1. 环境要求

- Python >= 3.12
- uv >= 0.4
- Node.js >= 18
- MySQL 8.0+

### 2. 初始化

```bash
# 安装后端依赖
cd backend
uv sync --all-packages

# 配置环境变量（首次使用）
cp .env.example .env
# 编辑 .env 修改数据库连接信息

# 初始化数据库（创建表 + 默认管理员 admin / admin123）
uv run python scripts/init_db.py

# 安装前端依赖
cd ../frontend
npm install
```

### 3. 启动服务

#### 后端微服务（5 个独立进程）

```bash
cd backend
uv run --package ksm-gateway uvicorn ksm_gateway.main:app --reload --port 8000
uv run --package ksm-auth uvicorn ksm_auth.main:app --reload --port 8001
uv run --package ksm-env uvicorn ksm_env.main:app --reload --port 8002
uv run --package ksm-secret uvicorn ksm_secret.main:app --reload --port 8003
uv run --package ksm-toolbox uvicorn ksm_toolbox.main:app --reload --port 8004
```

#### 前端开发服务器

```bash
cd frontend
npm run dev
```

前端默认运行在 **http://localhost:5173**，API 文档访问 **http://localhost:8000/docs**

### 4. 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin  | admin123 | 管理员 |

## 前端代理配置

开发模式下，前端通过 Vite 代理将 API 请求转发到后端微服务（配置在 `frontend/vite.config.ts` 中）：

| 路径前缀 | 代理目标 | 后端服务 |
|---------|---------|---------|
| `/api/v1/auth`    | `http://localhost:8001` | auth-service |
| `/api/v1/env`     | `http://localhost:8002` | env-service |
| `/api/v1/secret`  | `http://localhost:8003` | secret-service |
| `/api/v1/toolbox` | `http://localhost:8004` | toolbox-service |
| `/api/v1/gateway` | `http://localhost:8000` | api-gateway |

## API 概览

| 模块 | 服务 | 路径前缀 | 主要端点 |
|------|------|---------|---------|
| 认证 | auth-service (8001) | `/api/v1/auth` | `POST /login`, `GET /profile` |
| 用户管理 | auth-service (8001) | `/api/v1/auth` | `GET/POST /users`, `GET/PUT/DELETE /users/{id}`, `PUT /users/{id}/reset-password`, `GET/PUT /users/{id}/env-permissions` |
| 环境管理 | env-service (8002) | `/api/v1/env` | `GET/POST /environments`, `GET/PUT/DELETE /environments/{id}`, `GET /environments/{id}/namespaces`, `GET /environments/{id}/health` |
| Secret查询 | secret-service (8003) | `/api/v1/secret` | `GET /secrets/list`, `GET /secrets/detail`, `POST /secrets/sync` |
| 凭据管理 | secret-service (8003) | `/api/v1/secret` | `GET/POST /credentials`, `GET/PUT/DELETE /credentials/{id}`, `POST /credentials/{id}/reveal`, `POST /credentials/export` |
| 审计日志 | api-gateway (8000) | `/api/v1/gateway` | `GET /audit-logs`, `GET /audit-logs/export` |
| 工具箱 | toolbox-service (8004) | `/api/v1/toolbox` | `POST /tools/json-format`, `POST /tools/url-encode`, `POST /tools/url-decode`, `POST /tools/base64-encode`, `POST /tools/base64-decode`, `POST /tools/timestamp`, `POST /tools/regex-test`, `POST /tools/ip-query`, `POST /tools/port-check`, `GET /tools/uuid` |
| 导航链接 | toolbox-service (8004) | `/api/v1/toolbox` | `GET/POST /links`, `PUT/DELETE /links/{id}` |
| 仪表盘 | api-gateway (8000) | `/api/v1/gateway` | `GET /dashboard/stats` |

## 部署方案

### Docker Compose

```bash
cd backend
docker compose -f deploy/docker-compose.yml up -d --build
```

### Systemd

```bash
# 1. 部署项目到 /opt/k8s-secret-manager
# 2. 复制 .env.example 为 .env 并配置
# 3. 安装服务
sudo cp backend/deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start ksm-auth ksm-env ksm-secret ksm-toolbox ksm-gateway
sudo systemctl enable ksm-auth ksm-env ksm-secret ksm-toolbox ksm-gateway
```

### Kubernetes

```bash
kubectl apply -f backend/deploy/k8s/
```

## 开发指南

### 添加后端依赖

```bash
cd backend
uv add --package <package-name> <dependency>
```

### 运行测试

```bash
cd backend
uv run --package ksm-core pytest
```
