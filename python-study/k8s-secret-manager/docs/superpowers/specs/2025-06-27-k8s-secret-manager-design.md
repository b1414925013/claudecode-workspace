# K8s 多环境运维管理后台 — 设计文档

## 项目概述

基于 Python FastAPI + Tortoise-ORM + MySQL 的 K8s 多环境运维管理后台，采用 **uv workspace 单项目多微服务架构**。提供多集群环境管理、Secret/密钥统一管理、数据库凭据管理、开发者工具箱、用户权限体系等功能。

## 架构设计

### 总体架构

采用 **uv Workspace Monorepo** 模式：

```
k8s-secret-manager/         ← uv workspace root
├── packages/
│   ├── core/               ← 共享核心库（非独立部署）
│   ├── auth-service/       ← 认证授权服务
│   ├── env-service/        ← 环境管理服务
│   ├── secret-service/     ← Secret/密钥管理服务
│   ├── toolbox-service/    ← 开发者工具箱服务
│   └── api-gateway/        ← API 网关（统一入口）
└── frontend/               ← Vue 3 前端
```

### 架构决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 项目管理 | uv workspace | 统一依赖管理、版本锁定、单仓库多微服务 |
| Web 框架 | FastAPI | 异步、自动 OpenAPI、类型安全 |
| ORM | Tortoise-ORM | 异步原生、与 FastAPI 配合自然 |
| 微服务通信 | 内部通过 DB 共享 + API Gateway 路由聚合 | 降低服务间耦合 |
| K8s 操作 | kubernetes-python-sdk 为主，subprocess kubectl 为备 | SDK 稳定性更好 |

## 数据库设计

### E-R 简述

- **ksm_users**: 用户表（含角色：admin / developer）
- **ksm_environments**: K8s 集群环境配置
- **ksm_db_credentials**: 数据库/中间件凭据（AES 加密存储密码）
- **ksm_secret_cache**: K8s Secret 缓存快照
- **ksm_audit_logs**: 操作审计日志
- **ksm_toolbox_links**: 外部导航链接
- **ksm_env_permissions**: 环境-用户授权（多对多）

### 建表语句

见 `scripts/init_db.py` 或数据库管理工具执行 `docs/sql/init.sql`。

## 接口设计

基于 RESTful 风格，全局统一返回格式：

```json
// 成功
{ "code": 0, "message": "success", "data": {...}, "request_id": "uuid" }

// 分页
{ "code": 0, "message": "success", "data": { "items":[], "total":N, "page":1, "size":20, "pages":N }, "request_id": "uuid" }

// 错误
{ "code": 40001, "message": "参数校验失败", "detail": {...}, "request_id": "uuid" }
```

### 接口模块

| 模块 | 前缀 | 主要路由 |
|------|------|---------|
| 认证 | `/api/v1/auth` | login, logout, profile, refresh |
| 用户管理 | `/api/v1/users` | CRUD + 重置密码 + 环境授权 |
| 环境管理 | `/api/v1/environments` | CRUD + 命名空间列表 + 连通性检测 |
| Secret 管理 | `/api/v1/secrets` | 列表/详情/查看原始值/同步 |
| 凭据管理 | `/api/v1/credentials` | CRUD + 明文查看(审计) + 导出 |
| 审计日志 | `/api/v1/audit-logs` | 分页查询 + CSV 导出 |
| 工具箱 | `/api/v1/tools` | JSON/Base64/URL/时间戳/正则/IP/端口/UUID |
| 导航链接 | `/api/v1/links` | 增删改查 |
| 仪表盘 | `/api/v1/dashboard` | 统计概览 |

## 关键技术方案

### K8s 双方案

1. **kubernetes-python-sdk（主）**: 通过 `config.load_kube_config()` 或 `config.load_kube_config_from_dict()` 加载凭证，使用 `CoreV1Api` 操作资源
2. **kubectl（备）**: 通过 `subprocess.run` 执行命令，使用 `---` 前后标记包裹输出避免截取异常

### Secret 密码加密存储

- 凭据密码使用 **AES-256-CBC** 加密后存入数据库
- 前端展示默认脱敏（显示 `******`）
- 点击"查看明文"时记录审计日志

### 缓存策略

- 从 K8s 集群拉取的 Secret 数据写入 `ksm_secret_cache` 表
- 默认 TTL = 5 分钟
- 支持手动强制同步刷新

## 安全设计

- 密码 bcrypt 哈希
- JWT 鉴权（HS256，8h 过期）
- 敏感操作审计留痕
- 接口限流（slowapi）
- 全局异常捕获，不泄露敏感信息
- 密码查看记录详细操作日志

## 部署方案

支持三种模式：

1. **Systemd** - 各服务独立 systemd unit 管理
2. **Docker Compose** - 单机多容器部署
3. **K8s** - 各服务独立 Deployment + Service

## 前端

Vue 3 + Element Plus + Vite + Pinia + Axios。简单管理页面，包含：
- 登录页
- 仪表盘
- 环境管理
- Secret 查询
- 凭据管理
- 工具箱
- 用户管理（admin）
- 审计日志（admin）

## 分步实施计划

### Phase 1 — 项目骨架和核心库
1. uv workspace 初始化
2. core 包搭建（配置、数据库、异常、响应）
3. 安全层（JWT、密码哈希、AES）

### Phase 2 — 认证和用户
4. auth-service（登录、用户 CRUD）
5. 环境授权管理

### Phase 3 — 环境管理
6. env-service（集群 CRUD、命名空间、连通性检测）

### Phase 4 — Secret 和凭据管理
7. K8s 客户端封装（SDK + kubectl）
8. secret-service（Secret 查询、缓存）
9. 凭据管理（CRUD、密码查看、审计）

### Phase 5 — 工具和服务支撑
10. toolbox-service（在线工具 + 导航链接）
11. audit-log 查询导出
12. API Gateway 聚合

### Phase 6 — 前端
13. Vue 3 项目搭建
14. 各页面组件开发
