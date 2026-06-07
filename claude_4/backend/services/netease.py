from .base import BaseMusicService
from models import Song, Platform
import hashlib
import time

class NeteaseService(BaseMusicService):
    def __init__(self):
        super().__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    async def search(self, keyword: str, page: int = 1, limit: int = 20):
        # 网易云搜索API
        url = "https://music.163.com/api/search/get"
        data = {
            "s": keyword,
            "type": 1,
            "limit": limit,
            "offset": (page - 1) * limit
        }
        response = await self.client.post(url, data=data, headers=self.headers)
        result = response.json()

        songs = []
        for item in result.get("result", {}).get("songs", []):
            songs.append(Song(
                id=str(item["id"]),
                name=item["name"],
                artist=",".join([a["name"] for a in item["artists"]]),
                album=item["album"]["name"],
                duration=item["duration"] // 1000,
                platform=Platform.NETEASE,
                cover_url=item["album"]["picUrl"]
            ))
        return songs

    async def get_play_url(self, song_id: str):
        url = f"https://music.163.com/api/song/detail/?ids=[{song_id}]"
        response = await self.client.get(url, headers=self.headers)
        data = response.json()
        songs = data.get("songs", [])
        if songs:
            return songs[0].get("mp3Url", "")
        return ""

    async def get_lyrics(self, song_id: str):
        url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1"
        response = await self.client.get(url, headers=self.headers)
        data = response.json()
        lrc = data.get("lrc", {}).get("lyric", "")
        return lrc