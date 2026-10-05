# -*- coding: utf-8 -*-
"""
app.config —— 应用配置加载（数据库连接参数等）

从项目根目录的 config.json 读取配置；文件不存在、字段缺失或
JSON 损坏时回退到内置默认值（与 D:\\develop\\databases 各绿色版
出厂配置一致），保证开箱即用。
"""
import json
from pathlib import Path

# 配置文件位置：项目根目录（app/ 的上一级）
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

# 内置默认值：config.json 缺失或字段不全时的兜底
DEFAULTS: dict = {
    "mysql":      {"host": "127.0.0.1", "port": 3307, "user": "root", "password": "root"},
    "pg":         {"host": "127.0.0.1", "port": 5432, "user": "postgres",
                   "password": "postgres", "dbname": "postgres"},
    "redis":      {"host": "127.0.0.1", "port": 6379},
    "clickhouse": {"host": "127.0.0.1", "port": 8123, "username": "default",
                   "password": "clickhouse"},
    "nebula":     {"host": "127.0.0.1", "port": 9669, "user": "root",
                   "password": "nebula", "space": "demo",
                   # ssl 为可选段：不需要 TLS 加密时保持 null 即可；
                   # 服务端开启 SSL 后按需填证书路径（见 README / database.py）
                   "ssl": None},
}


def load_config() -> dict:
    """加载 config.json 并与默认值深合并（文件字段优先，缺失字段用默认值兜底）。"""
    cfg = json.loads(json.dumps(DEFAULTS))          # 深拷贝，避免污染 DEFAULTS
    if CONFIG_PATH.exists():
        try:
            # utf-8-sig：容忍记事本等编辑器写入的 BOM 头
            user = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
            for key, section in user.items():
                if key in cfg and isinstance(section, dict):
                    cfg[key].update(section)        # 逐字段覆盖，未写的字段保留默认
        except (json.JSONDecodeError, OSError):
            pass                                    # 配置损坏时静默回退默认值
    return cfg


# 模块级加载一次；运行期改 config.json 需重启服务生效
DB_CONFIG: dict = load_config()
