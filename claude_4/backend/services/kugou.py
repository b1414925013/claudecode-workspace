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
                id=str(item["hash"]),
                name=item["songname"],
                artist=item["singername"],
                album=item["album_name"] or "",
                duration=item["duration"],
                platform=Platform.KUGOU,
                cover_url=item.get("imgurl", "").replace("{size}", "400")
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