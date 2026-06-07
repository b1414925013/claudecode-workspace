from fastapi import APIRouter
from models import Platform
from services import NeteaseService, QQMusicService, KugouService

router = APIRouter()
services = {Platform.NETEASE: NeteaseService(), Platform.QQ: QQMusicService(), Platform.KUGOU: KugouService()}

@router.get("/{song_id}")
async def get_lyrics(song_id: str, platform: str):
    service = services[Platform(platform)]
    lyrics = await service.get_lyrics(song_id)
    return {"lyrics": lyrics}