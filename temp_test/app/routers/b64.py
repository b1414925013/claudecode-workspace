# -*- coding: utf-8 -*-
"""
Base64 编解码子路由
"""
import base64
import re

from fastapi import APIRouter, HTTPException

from app.models import B64Request, B64EncodeResponse, B64DecodeResponse

router = APIRouter(prefix="/b64", tags=["Base64 编解码"])


def _b64_decode_bytes(text: str, urlsafe: bool) -> bytes:
    """把 Base64 字符串解码为原始字节串（带清洗与字母表自动兼容）。"""
    cleaned = re.sub(r"\s+", "", text)
    if urlsafe or "-" in cleaned or "_" in cleaned:
        cleaned = cleaned.replace("-", "+").replace("_", "/")
    return base64.b64decode(cleaned, validate=True)


@router.post("/encode", response_model=B64EncodeResponse, summary="明文编码为 Base64")
async def b64_encode_api(req: B64Request) -> B64EncodeResponse:
    """POST 接口：将明文按 utf-8 编码后转为 Base64，可选 URL 安全字母表。"""
    raw = req.text.encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw) if req.urlsafe else base64.b64encode(raw)
    return B64EncodeResponse(encoded=encoded.decode("ascii"))


@router.post("/decode", response_model=B64DecodeResponse, summary="Base64 解码为明文")
async def b64_decode_api(req: B64Request) -> B64DecodeResponse:
    """POST 接口：将 Base64 字符串还原为明文；输入非法时返回 400。"""
    try:
        raw = _b64_decode_bytes(req.text, req.urlsafe)
    except ValueError:
        raise HTTPException(status_code=400, detail="不是有效的 Base64 字符串，无法解码")
    try:
        return B64DecodeResponse(decoded=raw.decode("utf-8"))
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="已解出字节串，但它不是有效的 UTF-8 文本")
