from .base import BaseMusicService
from models import Song, Platform

class QQMusicService(BaseMusicService):
    async def search(self, keyword: str, page: int = 1, limit: int = 20):
        # TODO: 实现QQ音乐搜索
        return []

    async def get_play_url(self, song_id: str):
        # TODO: 实现获取播放链接
        return None

    async def get_lyrics(self, song_id: str):
        # TODO: 实现获取歌词
        return None