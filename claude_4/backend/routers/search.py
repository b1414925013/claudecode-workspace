from fastapi import APIRouter
from typing import Optional
from models import Song, Platform
from services import NeteaseService, QQMusicService, KugouService

router = APIRouter()
services = {
    Platform.NETEASE: NeteaseService(),
    Platform.QQ: QQMusicService(),
    Platform.KUGOU: KugouService(),
}

@router.get("")
async def search(q: str, platform: Optional[str] = None):
    results = []
    platforms = [Platform(platform)] if platform else [Platform.NETEASE, Platform.QQ, Platform.KUGOU]

    for p in platforms:
        service = services[p]
        result = await service.search(q)
        results.extend(result)

    return {"songs": results, "total": len(results)}