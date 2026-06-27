import json
import socket
import uuid
import re
import base64
from urllib.parse import quote, unquote
from datetime import datetime, timezone
from ksm_core.models import ToolboxLink
from ksm_core.exceptions import NotFoundException


def json_format(text: str, indent: int = 2) -> str:
    parsed = json.loads(text)
    return json.dumps(parsed, indent=indent, ensure_ascii=False)


def url_encode(text: str) -> str:
    return quote(text)


def url_decode(text: str) -> str:
    return unquote(text)


def b64_encode(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def b64_decode(text: str) -> str:
    return base64.b64decode(text).decode("utf-8", errors="replace")


def timestamp_convert(value: str) -> dict:
    try:
        ts = int(value)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return {"timestamp": ts, "datetime": dt.isoformat()}
    except ValueError:
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
            try:
                dt = datetime.strptime(value, fmt)
                return {"timestamp": int(dt.timestamp()), "datetime": dt.isoformat()}
            except ValueError:
                continue
        raise ValueError(f"无法解析时间: {value}")


def regex_test(pattern: str, text: str, flags: str = "") -> dict:
    re_flags = 0
    if "i" in flags:
        re_flags |= re.IGNORECASE
    if "m" in flags:
        re_flags |= re.MULTILINE
    if "s" in flags:
        re_flags |= re.DOTALL
    matches = re.findall(pattern, text, re_flags)
    return {"matches": matches[:100], "count": len(matches)}


def generate_uuids(count: int = 1) -> list[str]:
    return [str(uuid.uuid4()) for _ in range(count)]


def check_port(host: str, port: int, timeout: int = 3) -> dict:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        return {"host": host, "port": port, "open": result == 0}
    finally:
        sock.close()


async def get_links(category: str = None) -> list[dict]:
    qs = ToolboxLink.filter(is_active=True).order_by("sort_order")
    if category:
        qs = qs.filter(category=category)
    links = await qs
    return [{
        "id": l.id, "title": l.title, "url": l.url,
        "icon": l.icon, "category": l.category, "sort_order": l.sort_order,
    } for l in links]


async def create_link(data: dict) -> ToolboxLink:
    return await ToolboxLink.create(**data)


async def update_link(link_id: int, data: dict) -> ToolboxLink:
    link = await ToolboxLink.get_or_none(id=link_id)
    if not link:
        raise NotFoundException("链接不存在")
    await link.update_from_dict(data)
    await link.save()
    return link


async def delete_link(link_id: int):
    link = await ToolboxLink.get_or_none(id=link_id)
    if not link:
        raise NotFoundException("链接不存在")
    await link.delete()
