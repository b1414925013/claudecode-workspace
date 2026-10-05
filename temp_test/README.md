# naming-api

命名格式转换 API + Base64 编解码 + 时间戳转换 + JSONPath 查询 + 数据库控制台，基于 FastAPI。

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（默认 8801 端口）
uvicorn app.main:app --host 127.0.0.1 --port 8801
```

访问 http://127.0.0.1:8801/ 使用网页版工具，http://127.0.0.1:8801/docs 查看交互式文档。

## 项目结构

```
naming-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 主应用（/convert 端点 + 子路由挂载）
│   ├── models.py         # Pydantic 模型（集中管理）
│   ├── utils.py          # 工具函数（命名转换、时间戳解析）
│   └── routers/
│       ├── __init__.py
│       ├── b64.py        # Base64 编解码子路由（/b64）
│       ├── timestamp.py  # 时间戳转换子路由（/ts）
│       ├── jsonpath.py   # JSONPath 查询子路由（/jsonpath）
│       └── database.py   # 数据库控制台子路由（/database，五大绿色版库）
├── index.html            # 前端工具箱（命名/Base64/时间戳/JSONPath/数据库 五合一标签页）
├── requirements.txt      # pip 依赖列表
├── pyproject.toml        # 项目元数据（可选）
└── .gitignore
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/convert` | 英文名 → 蛇形/驼峰/下划线常量/横杠/点分等全部形式 |
| GET  | `/` | 命名转换网页（index.html） |
| POST | `/b64/encode` | 明文 → Base64 |
| POST | `/b64/decode` | Base64 → 明文 |
| POST | `/ts/to-date` | 时间戳 → 日期时间（秒/毫秒/微秒自动识别） |
| POST | `/ts/to-timestamp` | 日期时间 → 时间戳 |
| POST | `/jsonpath/query` | JSONPath 表达式查询 JSON 文档（返回路径 + 值） |
| GET  | `/database/status` | 探测 MySQL/PG/Redis/ClickHouse/Nebula 在线状态 |
| POST | `/database/exec` | 在指定库上执行一条命令（SQL / Redis 命令 / nGQL） |

## 调用示例

```bash
# 命名转换
curl -X POST http://127.0.0.1:8801/convert \
  -H "Content-Type: application/json" \
  -d '{"text": "helloWorld user_name HTTP-server"}'

# Base64 编码
curl -X POST http://127.0.0.1:8801/b64/encode \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello"}'

# 时间戳转换
curl -X POST http://127.0.0.1:8801/ts/to-date \
  -H "Content-Type: application/json" \
  -d '{"timestamp": 1791045023}'

# JSONPath 查询
curl -X POST http://127.0.0.1:8801/jsonpath/query \
  -H "Content-Type: application/json" \
  -d '{"doc": {"store": {"book": [{"title": "Moby Dick"}]}}, "expr": "$..book[*].title"}'
```
