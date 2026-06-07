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
            album = item.get("album") or {}
            pic_url = album.get("picUrl") or ""
            if not pic_url and album.get("picId"):
                pic_url = f"https://p1.music.126.net/{album['picId']}.jpg"
            songs.append(Song(
                id=str(item["id"]),
                name=item["name"],
                artist=",".join([a.get("name", "") for a in item.get("artists", [])]),
                album=album.get("name", ""),
                duration=item.get("duration", 0) // 1000,
                platform=Platform.NETEASE,
                cover_url=pic_url
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

    async def get_rankings(self, ranking_type: str = "hot"):
        # 网易云热歌榜
        url = "https://music.163.com/api/playlist/detail"
        params = {"id": 3778678}  # 热歌榜
        response = await self.client.get(url, params=params, headers=self.headers)
        data = response.json()
        songs = []
        for item in data.get("result", {}).get("tracks", [])[:20]:
            album = item.get("album") or {}
            pic_url = album.get("picUrl") or ""
            if not pic_url and album.get("picId"):
                pic_url = f"https://p1.music.126.net/{album['picId']}.jpg"
            songs.append(Song(
                id=str(item["id"]),
                name=item["name"],
                artist=",".join([a.get("name", "") for a in item.get("artists", [])]),
                album=album.get("name", ""),
                duration=item.get("duration", 0) // 1000,
                platform=Platform.NETEASE,
                cover_url=pic_url
            ))
        return songs