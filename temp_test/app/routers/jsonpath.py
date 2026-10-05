# -*- coding: utf-8 -*-
"""
JSONPath 查询子路由

基于 jsonpath-ng（扩展版解析器）：接收任意 JSON 文档与一条
JSONPath 表达式，返回全部匹配节点的路径与值。
"""
from jsonpath_ng.ext import parse
from jsonpath_ng.exceptions import JSONPathError

from fastapi import APIRouter, HTTPException

from app.models import JsonPathRequest, JsonPathResponse, JsonPathMatch

router = APIRouter(prefix="/jsonpath", tags=["JSONPath 查询"])


def _clean_path(datum) -> str:
    """从 DatumInContext 链重建标准 JSONPath 路径（如 $.store.book[0].title）。

    jsonpath-ng 的 str(full_path) 会输出带歧义消除括号的内部表示
    （如 $.(((store.book).[0]).title)），不适合展示；
    改为沿 context 链自叶向根收集各层路径段后重新拼接。
    """
    segments = []
    d = datum
    while d is not None:
        seg = str(d.path)
        if seg == "$":           # 链顶为根节点，停止收集
            break
        segments.append(seg)
        d = d.context
    path = "$"
    for seg in reversed(segments):
        # 下标/切片 "[0]" 与递归下降 "..author" 直接拼接，字段名前置一个点
        path += seg if seg.startswith(("[", "..")) else "." + seg
    return path


@router.post("/query", response_model=JsonPathResponse, summary="JSONPath 表达式查询 JSON 文档")
async def jsonpath_query_api(req: JsonPathRequest) -> JsonPathResponse:
    """POST 接口：按表达式查询 JSON 文档，返回全部匹配节点（路径 + 值）。

    异常：
        表达式语法非法时返回 400（附解析器错误信息）；
        查询不到节点时正常返回 200，count 为 0。
    """
    try:
        expr_obj = parse(req.expr)
    except JSONPathError as e:
        raise HTTPException(status_code=400, detail=f"JSONPath 表达式无法解析：{e}")

    # find 返回 DatumInContext 列表，沿 context 链可重建该节点的完整路径
    found = expr_obj.find(req.doc)
    matches = [JsonPathMatch(path=_clean_path(m), value=m.value) for m in found]
    return JsonPathResponse(
        expr=req.expr,
        count=len(matches),
        values=[m.value for m in matches],
        matches=matches,
    )
