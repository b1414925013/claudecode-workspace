# -*- coding: utf-8 -*-
"""
命名格式转换 API（FastAPI 主应用）

启动：
    fastapi dev app/main.py --host 127.0.0.1 --port 8801
    # 或
    uvicorn app.main:app --host 127.0.0.1 --port 8801

调用示例：
    curl -X POST http://127.0.0.1:8801/convert \
         -H "Content-Type: application/json" \
         -d '{"text": "helloWorld user_name HTTP-server"}'
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.models import ConvertRequest, ConvertResponse
from app.routers import b64, database, jsonpath, timestamp
from app.utils import split_words, to_camel

app = FastAPI(
    title="命名格式转换 API",
    description=(
        "输入英文字母，输出蛇形/驼峰/下划线等全部常见命名形式。\n\n"
        "同时提供 Base64 编解码（/b64）、时间戳转换（/ts）、"
        "JSONPath 查询（/jsonpath）与数据库控制台（/database）四个子模块。"
    ),
    version="1.0.0",
)

# 允许跨域访问：便于网页以本地文件方式打开时也能直接调用本接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 挂载子路由 ────────────────────────────────────────────────────────────────
app.include_router(b64.router)
app.include_router(timestamp.router)
app.include_router(jsonpath.router)
app.include_router(database.router)


# ─── 路由 ─────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    """GET 首页：返回命名转换工具网页（index.html）。"""
    return FileResponse(Path(__file__).parent.parent / "index.html")


@app.post("/convert", response_model=ConvertResponse, summary="英文名转换为各种命名格式")
async def convert(req: ConvertRequest) -> ConvertResponse:
    """POST 接口：输入英文文本，返回蛇形/小驼峰/大驼峰/下划线常量/横杠/点分等全部形式。"""
    words = split_words(req.text)
    if not words:
        raise HTTPException(status_code=400, detail="输入中未识别到任何英文单词或数字")

    lower_words = [w.lower() for w in words]
    return ConvertResponse(
        words=words,
        snake_case="_".join(lower_words),
        camel_case=to_camel(words),
        PascalCase="".join(w.capitalize() for w in words),
        CONSTANT_CASE="_".join(w.upper() for w in words),
        **{"kebab-case": "-".join(lower_words),
           "dot.case": ".".join(lower_words),
           "Title Case": " ".join(w.capitalize() for w in words),
           "lowercase": "".join(lower_words),
           "UPPERCASE": "".join(w.upper() for w in words)},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8801)
