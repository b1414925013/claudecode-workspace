from fastapi import APIRouter
from models import Platform
from services import NeteaseService, QQMusicService, KugouService

router = APIRouter()
services = {Platform.NETEASE: NeteaseService(), Platform.QQ: QQMusicService(), Platform.KUGOU: KugouService()}

@router.get("")
async def get_rankings(platform: str = "netease", ranking_type: str = "hot"):
    service = services[Platform(platform)]
    songs = await service.get_rankings(ranking_type)
    return {"songs": songs}