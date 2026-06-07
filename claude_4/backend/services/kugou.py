from .base import BaseMusicService
from models import Song, Platform

class KugouService(BaseMusicService):
    async def search(self, keyword: str, page: int = 1, limit: int = 20):
        # TODO: 实现酷狗音乐搜索
        return []

    async def get_play_url(self, song_id: str):
        # TODO: 实现获取播放链接
        return None

    async def get_lyrics(self, song_id: str):
        # TODO: 实现获取歌词
        return None