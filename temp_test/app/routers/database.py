# -*- coding: utf-8 -*-
"""
数据库控制台子路由

把 D:\\develop\\databases 五大绿色版数据库（MySQL / PostgreSQL / Redis /
ClickHouse / NebulaGraph）的访问能力接到 HTTP：
    GET  /database/status  并发探测五个端口，返回在线状态
    POST /database/exec    在指定库上执行一条命令（SQL / Redis 命令行 / nGQL）

连接参数与 db_crud.py 保持一致；本接口面向本机开发/演示用途，
命令会真实执行，请勿暴露到公网。
"""
import asyncio
import shlex
import threading
import time

from fastapi import APIRouter, HTTPException

from app.config import DB_CONFIG
from app.models import DbStatusItem, DbStatusResponse, DbExecRequest, DbExecResponse

router = APIRouter(prefix="/database", tags=["数据库控制台"])

# 五个库的连接参数：全部来自项目根 config.json（改端口/密码只需编辑该文件）
MYSQL = DB_CONFIG["mysql"]
PG = DB_CONFIG["pg"]
REDIS_CONF = DB_CONFIG["redis"]
CLICKHOUSE = DB_CONFIG["clickhouse"]
NEBULA = DB_CONFIG["nebula"]

# 展示元数据：key -> (名称, 端口, 说明)，端口取自配置
DB_META = {
    "mysql": ("MySQL", MYSQL["port"], "root/root · 默认连接服务器，可 USE py_demo"),
    "pg": ("PostgreSQL", PG["port"], "postgres/postgres · 默认库 postgres"),
    "redis": ("Redis", REDIS_CONF["port"], "无密码 · 输入命令行，如 SET k v / HGETALL h"),
    "clickhouse": ("ClickHouse", CLICKHOUSE["port"], "default/clickhouse · HTTP 接口"),
    "nebula": ("NebulaGraph", NEBULA["port"], "root/nebula · nGQL，先 USE demo"),
}

# 结果集最多返回的行数，防止一次查询拖垮页面
MAX_ROWS = 200


def _cell(v) -> str:
    """把任意数据库返回值转成可展示字符串（bytes 解码、容器转 JSON 风格）。"""
    if v is None:
        return "NULL"
    if isinstance(v, bytes):
        try:
            return v.decode("utf-8")
        except UnicodeDecodeError:
            return repr(v)
    return str(v)


@router.get("/status", response_model=DbStatusResponse, summary="探测五个数据库的在线状态")
async def db_status() -> DbStatusResponse:
    """GET 接口：并发 TCP 探测五个库的端口（每个 1.5 秒超时），立即返回状态。"""

    async def probe(key: str) -> DbStatusItem:
        name, port, note = DB_META[key]
        host = DB_CONFIG[key]["host"]
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=1.5)
            writer.close()
            online = True
        except (OSError, asyncio.TimeoutError):
            online = False
        return DbStatusItem(key=key, name=name, port=port, online=online,
                            note=note if online else f"离线 · 请运行 databases\\{key}_latest\\启动.bat")

    items = await asyncio.gather(*(probe(k) for k in DB_META))
    return DbStatusResponse(items=list(items))


def _exec_mysql(command: str) -> tuple[list[str], list[list[str]], int | None, str]:
    """在 MySQL 上执行单条 SQL，返回 (列名, 行, 受影响行数, 摘要)。"""
    import pymysql

    conn = pymysql.connect(host=MYSQL["host"], port=MYSQL["port"], user=MYSQL["user"],
                           password=MYSQL["password"], charset="utf8mb4",
                           autocommit=True, connect_timeout=5)
    try:
        with conn.cursor() as cur:
            cur.execute(command)
            if cur.description:                      # 有结果集（SELECT/SHOW 等）
                cols = [d[0] for d in cur.description]
                rows = [[_cell(v) for v in row] for row in cur.fetchmany(MAX_ROWS)]
                return cols, rows, None, f"查询成功，返回 {len(rows)} 行"
            return [], [], cur.rowcount, f"执行成功，受影响 {cur.rowcount} 行"
    finally:
        conn.close()


def _exec_pg(command: str) -> tuple[list[str], list[list[str]], int | None, str]:
    """在 PostgreSQL 上执行单条 SQL，返回 (列名, 行, 受影响行数, 摘要)。"""
    import psycopg2

    conn = psycopg2.connect(host=PG["host"], port=PG["port"], user=PG["user"],
                            password=PG["password"], dbname=PG["dbname"],
                            connect_timeout=5)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(command)
            if cur.description:
                cols = [d[0] for d in cur.description]
                rows = [[_cell(v) for v in row] for row in cur.fetchmany(MAX_ROWS)]
                return cols, rows, None, f"查询成功，返回 {len(rows)} 行"
            return [], [], cur.rowcount, f"执行成功，受影响 {cur.rowcount} 行"
    finally:
        conn.close()


def _exec_redis(command: str) -> tuple[list[str], list[list[str]], int | None, str]:
    """执行一条 Redis 命令行（shlex 分参，支持引号），统一转换结果展示。"""
    import redis

    # protocol=2：Redis 5.0 不支持 RESP3 的 HELLO 命令，强制走 RESP2
    r = redis.Redis(host=REDIS_CONF["host"], port=REDIS_CONF["port"],
                    decode_responses=True, socket_timeout=5, protocol=2)
    args = shlex.split(command)
    if not args:
        raise ValueError("命令为空")
    result = r.execute_command(*args)
    if isinstance(result, dict):                     # HGETALL 等：转两列
        return ["field", "value"], [[_cell(k), _cell(v)] for k, v in result.items()], \
               None, f"返回 {len(result)} 个键值对"
    if isinstance(result, (list, tuple, set)):       # LRANGE / KEYS 等：转单列
        items = list(result)
        return ["value"], [[_cell(v)] for v in items], None, f"返回 {len(items)} 项"
    return [], [], None, _cell(result)               # 标量：OK / 数字 / 字符串


def _exec_clickhouse(command: str) -> tuple[list[str], list[list[str]], int | None, str]:
    """在 ClickHouse 上执行单条 SQL：查询类走 query，其余走 command。"""
    import clickhouse_connect

    client = clickhouse_connect.get_client(host=CLICKHOUSE["host"], port=CLICKHOUSE["port"],
                                           username=CLICKHOUSE["username"],
                                           password=CLICKHOUSE["password"],
                                           connect_timeout=5)
    head = command.lstrip()[:10].upper()
    if head.startswith(("SELECT", "SHOW", "DESCRIBE", "DESC ", "EXISTS", "WITH", "EXPLAIN")):
        rs = client.query(command)
        cols = list(rs.column_names)
        rows = [[_cell(v) for v in row] for row in rs.result_rows[:MAX_ROWS]]
        return cols, rows, None, f"查询成功，返回 {len(rows)} 行"
    summary = client.command(command)
    return [], [], None, f"执行成功" + (f"：{_cell(summary)}" if summary else "")


# NebulaGraph 全局长驻会话：保持 USE 等会话态跨请求生效（RLock 保证串行）
_nebula_lock = threading.RLock()
_nebula_pool = None
_nebula_session = None


def _get_nebula_session():
    """懒创建并复用全局 NebulaGraph 会话；失效后由调用方重置重建。

    config.json 的 nebula.ssl 为可选段，用于 TLS 加密连接：
        { "ca_certs": "ca.crt 路径",                    # 单向认证：仅校验服务端
          "certfile": "客户端证书 .crt",                 # 双向认证：额外提供
          "keyfile":  "客户端私钥 .key" }                #   客户端证书与私钥
    """
    global _nebula_pool, _nebula_session
    with _nebula_lock:
        if _nebula_session is not None:
            return _nebula_session
        import ssl

        from nebula3.gclient.net import ConnectionPool
        from nebula3.Config import Config as NebulaConfig, SSL_config

        cfg = NebulaConfig()
        cfg.timeout_ms = 8000
        cfg.max_connection_pool_size = 2
        # 按配置构造 SSL 参数：填了 ca_certs 才启用 TLS，否则明文连接
        ssl_conf = None
        ssl_cfg = NEBULA.get("ssl")
        if ssl_cfg and ssl_cfg.get("ca_certs"):
            ssl_conf = SSL_config()
            ssl_conf.ca_certs = ssl_cfg["ca_certs"]
            ssl_conf.cert_reqs = ssl.CERT_REQUIRED      # 校验服务端证书
            if ssl_cfg.get("certfile") and ssl_cfg.get("keyfile"):
                ssl_conf.certfile = ssl_cfg["certfile"]  # 双向认证：出示客户端证书
                ssl_conf.keyfile = ssl_cfg["keyfile"]
        pool = ConnectionPool()
        if not pool.init([(NEBULA["host"], NEBULA["port"])], cfg, ssl_conf=ssl_conf):
            raise ConnectionError("NebulaGraph 连接池初始化失败（SSL 配置有误或服务不可达）")
        session = pool.get_session(NEBULA["user"], NEBULA["password"])
        _nebula_pool, _nebula_session = pool, session
        return _nebula_session


def _reset_nebula_session() -> None:
    """释放并清空全局会话（执行异常时调用，下次请求自动重建）。"""
    global _nebula_pool, _nebula_session
    with _nebula_lock:
        try:
            if _nebula_session is not None:
                _nebula_session.release()
            if _nebula_pool is not None:
                _nebula_pool.close()
        except Exception:
            pass
        _nebula_pool = None
        _nebula_session = None


def _exec_nebula(command: str) -> tuple[list[str], list[list[str]], int | None, str]:
    """在 NebulaGraph 上执行一条 nGQL，返回结果集或执行摘要。

    会话全局长驻：USE demo 等会话状态跨请求保持。
    """
    with _nebula_lock:
        session = _get_nebula_session()
        try:
            rs = session.execute(command)
        except Exception:
            _reset_nebula_session()              # 会话失效，下次请求重建
            raise
        if not rs.is_succeeded():
            raise ValueError(rs.error_msg() or "nGQL 执行失败")
        if rs.row_size() > 0:
            # 兼容不同 nebula3-python 版本：keys() 元素可能是 str 或 Value
            cols = [k if isinstance(k, str) else str(k.cast()) for k in rs.keys()]
            rows = [[_cell(v) for v in rs.row_values(i)]
                    for i in range(min(rs.row_size(), MAX_ROWS))]
            return cols, rows, None, f"查询成功，返回 {len(rows)} 行"
        return [], [], None, "执行成功"


# db 标识 -> 执行器
EXECUTORS = {
    "mysql": _exec_mysql,
    "pg": _exec_pg,
    "redis": _exec_redis,
    "clickhouse": _exec_clickhouse,
    "nebula": _exec_nebula,
}


@router.post("/exec", response_model=DbExecResponse, summary="在指定数据库上执行一条命令")
async def db_exec(req: DbExecRequest) -> DbExecResponse:
    """POST 接口：真实执行命令并返回结果集/受影响行数。

    异常：
        db 标识不存在返回 400；连接失败或命令错误时 ok=False 并附错误信息
        （不抛 500，方便前端在控制台里直接展示原因）。
    """
    executor = EXECUTORS.get(req.db)
    if executor is None:
        raise HTTPException(status_code=400,
                            detail=f"未知数据库标识：{req.db}，可选：{list(EXECUTORS)}")
    t0 = time.perf_counter()
    try:
        cols, rows, affected, message = executor(req.command)
        ok = True
    except Exception as e:                           # 驱动错误统一转可读结果
        cols, rows, affected = [], [], None
        message = f"{type(e).__name__}: {e}"
        ok = False
    elapsed = int((time.perf_counter() - t0) * 1000)
    return DbExecResponse(ok=ok, columns=cols, rows=rows, affected=affected,
                          message=message, elapsed_ms=elapsed)
