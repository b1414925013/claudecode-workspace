from .base import BaseMusicService
from models import Song, Platform

class KugouService(BaseMusicService):
    async def search(self, keyword: str, page: int = 1, limit: int = 20):
        url = "http://mobilecdn.kugou.com/api/v3/search/song"
        params = {
            "keyword": keyword,
            "page": page,
            "pagesize": limit,
            "showtype": 1
        }
        response = await self.client.get(url, params=params)
        data = response.json()

        songs = []
        for item in data.get("data", {}).get("info", []):
            songs.append(Song(
                id=str(item.get("hash", "")),
                name=item.get("songname", ""),
                artist=item.get("singername", ""),
                album=item.get("album_name", ""),
                duration=item.get("duration", 0),
                platform=Platform.KUGOU,
                cover_url=item.get("imgurl", "").replace("{size}", "400") if item.get("imgurl") else ""
            ))
        return songs

    async def get_play_url(self, song_id: str):
        # 酷狗播放链接获取
        url = f"https://www.kugou.com/song/{song_id}"
        response = await self.client.get(url)
        return ""

    async def get_lyrics(self, song_id: str):
        url = "http://lyrics.kugou.com/search"
        params = {
            "ver": 1,
            "hash": song_id,
            "man": "netease"
        }
        response = await self.client.get(url, params=params)
        return ""

    async def get_rankings(self, ranking_type: str = "hot"):
        # 酷狗热歌榜
        url = "http://mobilecdn.kugou.com/api/v3/rank/hot"
        params = {"page": 1, "pagesize": 20}
        response = await self.client.get(url, params=params)
        data = response.json()
        songs = []
        for item in data.get("data", {}).get("info", []):
            songs.append(Song(
                id=str(item.get("hash", "")),
                name=item.get("songname", ""),
                artist=item.get("singername", ""),
                album=item.get("album_name", ""),
                duration=item.get("duration", 0),
                platform=Platform.KUGOU,
                cover_url=item.get("imgurl", "").replace("{size}", "400") if item.get("imgurl") else ""
            ))
        return songs