from fastapi import APIRouter
from models import Platform
from services import NeteaseService, QQMusicService, KugouService

router = APIRouter()
services = {Platform.NETEASE: NeteaseService(), Platform.QQ: QQMusicService(), Platform.KUGOU: KugouService()}

@router.get("")
async def get_rankings(platform: str = "netease", type: str = "hot"):
    service = services[Platform(platform)]
    songs = await service.get_rankings(type)
    return {"songs": songs}