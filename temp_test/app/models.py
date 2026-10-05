# -*- coding: utf-8 -*-
"""
Pydantic 模型定义（集中管理）
"""
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ─── Base64 ────────────────────────────────────────────────────────────────────

class B64Request(BaseModel):
    """Base64 编解码通用请求体。"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="待编码的明文，或待解码的 Base64 字符串",
        examples=["Hello, 命名转换所！"],
    )
    urlsafe: bool = Field(False, description="是否使用 URL 安全字母表（用 - 和 _ 代替 + 和 /）")


class B64EncodeResponse(BaseModel):
    """POST /b64/encode 的响应体。"""
    encoded: str = Field(description="Base64 编码结果")


class B64DecodeResponse(BaseModel):
    """POST /b64/decode 的响应体。"""
    decoded: str = Field(description="Base64 解码还原出的明文")


# ─── 时间戳 ────────────────────────────────────────────────────────────────────

class TimestampRequest(BaseModel):
    """POST /ts/to-date 的请求体。"""
    timestamp: int = Field(
        ...,
        description="Unix 时间戳，自动识别秒级(10位)/毫秒级(13位)/微秒级(16位)",
        examples=[1791045023],
    )


class DateRequest(BaseModel):
    """POST /ts/to-timestamp 的请求体。"""
    date_text: str = Field(
        ...,
        min_length=4,
        max_length=64,
        description="日期时间文本，支持 2026-10-04 12:30:00、2026/10/4、ISO 8601 等格式",
        examples=["2026-10-04 12:30:00"],
    )


class DateResponse(BaseModel):
    """POST /ts/to-date 的响应体：时间戳换算出的各格式日期时间。"""
    timestamp_input: int = Field(description="原始输入的时间戳")
    unit: str = Field(description="识别出的单位：seconds / milliseconds / microseconds")
    iso_utc: str = Field(description="UTC 时区的 ISO 8601 字符串")
    iso_local: str = Field(description="本地时区的 ISO 8601 字符串")
    datetime_local: str = Field(description="本地时间：年-月-日 时:分:秒")
    date_only: str = Field(description="仅日期：年-月-日")
    time_only: str = Field(description="仅时间：时:分:秒")
    weekday_cn: str = Field(description="星期几（中文）")


class TimestampResponse(BaseModel):
    """POST /ts/to-timestamp 的响应体：日期文本换算出的时间戳。"""
    date_text: str = Field(description="输入的日期文本")
    datetime_local: str = Field(description="解析得到的本地时间：年-月-日 时:分:秒")
    timestamp_seconds: int = Field(description="秒级时间戳（10 位）")
    timestamp_milliseconds: int = Field(description="毫秒级时间戳（13 位）")
    iso_utc: str = Field(description="对应 UTC 时区的 ISO 8601 字符串")


# ─── 命名转换 ─────────────────────────────────────────────────────────────────

class ConvertRequest(BaseModel):
    """POST /convert 的请求体：待转换的英文文本。"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="输入文本，支持空格/下划线/横杠/驼峰/数字混合，如 helloWorld、user_name、HTTP-server",
        examples=["helloWorld", "user_name", "HTTP server"],
    )


class ConvertResponse(BaseModel):
    """POST /convert 的响应体：各种命名格式的转换结果。"""
    model_config = ConfigDict(populate_by_name=True)
    words: list[str] = Field(description="拆分出的单词列表")
    snake_case: str = Field(description="蛇形：snake_case")
    camel_case: str = Field(alias="camelCase", description="小驼峰：camelCase")
    pascal_case: str = Field(alias="PascalCase", description="大驼峰：PascalCase")
    upper_snake_case: str = Field(alias="CONSTANT_CASE", description="下划线型（大写常量）：CONSTANT_CASE")
    kebab_case: str = Field(alias="kebab-case", description="横杠：kebab-case")
    dot_case: str = Field(alias="dot.case", description="点分：dot.case")
    title_case: str = Field(alias="Title Case", description="标题式（空格分隔）：Title Case")
    lower_plain: str = Field(alias="lowercase", description="全小写连写：lowercase")
    upper_plain: str = Field(alias="UPPERCASE", description="全大写连写：UPPERCASE")


# ─── JSONPath 查询 ────────────────────────────────────────────────────────────

class JsonPathRequest(BaseModel):
    """POST /jsonpath/query 的请求体：JSON 文档 + 路径表达式。"""
    doc: Any = Field(
        ...,
        description="待查询的 JSON 文档（任意嵌套结构：对象/数组/标量均可）",
    )
    expr: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="JSONPath 表达式，如 $.store.book[?(@.price < 10)].title",
        examples=["$..author", "$.store.book[0].title"],
    )


class JsonPathMatch(BaseModel):
    """单个匹配节点的明细：路径 + 值。"""
    path: str = Field(description="匹配节点的 JSONPath 路径")
    value: Any = Field(description="匹配节点的值")


class JsonPathResponse(BaseModel):
    """POST /jsonpath/query 的响应体：全部匹配结果。"""
    expr: str = Field(description="执行的 JSONPath 表达式")
    count: int = Field(description="匹配到的节点数量")
    values: list[Any] = Field(description="匹配值列表（仅值，方便直接消费）")
    matches: list[JsonPathMatch] = Field(description="匹配节点明细（路径 + 值）")


# ─── 数据库控制台 ──────────────────────────────────────────────────────────────

class DbStatusItem(BaseModel):
    """单个数据库的在线状态。"""
    key: str = Field(description="数据库标识：mysql / pg / redis / clickhouse / nebula")
    name: str = Field(description="显示名称")
    port: int = Field(description="服务端口")
    online: bool = Field(description="端口是否可连通")
    note: str = Field(description="补充说明（引擎/账户提示）")


class DbStatusResponse(BaseModel):
    """GET /database/status 的响应体。"""
    items: list[DbStatusItem] = Field(description="五个数据库的状态列表")


class DbExecRequest(BaseModel):
    """POST /database/exec 的请求体：目标库 + 待执行命令。"""
    db: str = Field(
        ...,
        description="目标数据库标识：mysql / pg / redis / clickhouse / nebula",
        examples=["mysql"],
    )
    command: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="待执行的单条命令：MySQL/PG/ClickHouse 为 SQL，Redis 为命令行（空格分参），Nebula 为 nGQL",
        examples=["SELECT * FROM student ORDER BY id"],
    )


class DbExecResponse(BaseModel):
    """POST /database/exec 的响应体：执行结果。"""
    ok: bool = Field(description="是否执行成功")
    columns: list[str] = Field(description="结果列名（无结果集时为空）")
    rows: list[list[str]] = Field(description="结果行（最多返回 200 行，值统一转字符串）")
    affected: int | None = Field(default=None, description="受影响行数（DML 语句时有值）")
    message: str = Field(description="执行摘要或错误信息")
    elapsed_ms: int = Field(description="执行耗时（毫秒）")
