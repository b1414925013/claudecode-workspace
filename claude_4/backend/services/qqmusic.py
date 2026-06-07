from .base import BaseMusicService
from models import Song, Platform

class QQMusicService(BaseMusicService):
    async def search(self, keyword: str, page: int = 1, limit: int = 20):
        url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
        params = {
            "w": keyword,
            "p": page,
            "n": limit,
            "format": "json"
        }
        headers = {"Referer": "https://y.qq.com"}
        response = await self.client.get(url, params=params, headers=headers)
        data = response.json()

        songs = []
        for item in data.get("data", {}).get("song", {}).get("list", []):
            singer = item.get("singer") or []
            songs.append(Song(
                id=str(item.get("songmid", "")),
                name=item.get("songname", ""),
                artist=singer[0].get("name", "") if singer else "",
                album=item.get("albumname", ""),
                duration=item.get("interval", 0),
                platform=Platform.QQ,
                cover_url=f"https://y.gtimg.cn/music/photo_new/T002R300x300M000{item.get('albummid', '')}.jpg"
            ))
        return songs

    async def get_play_url(self, song_id: str):
        # 使用QQ音乐v1获取播放链接
        url = f"https://u.y.qq.com/cgi-bin/musicu.fcg"
        data = {
            "req_1": {
                "module": "vkey.GetVkeyList",
                "method": "GetVkey",
                "param": {
                    "songmid": [song_id],
                    "songtype": [0]
                }
            }
        }
        response = await self.client.post(url, json=data)
        result = response.json()
        purl = result.get("req_1", {}).get("data", {}).get("midurlinfo", [])
        if purl:
            return "https://isure.stream.qqmusic.qq.com/" + purl[0]["purl"]
        return ""

    async def get_lyrics(self, song_id: str):
        url = f"https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"
        params = {
            "songmid": song_id,
            "format": "json"
        }
        headers = {"Referer": "https://y.qq.com"}
        response = await self.client.get(url, params=params, headers=headers)
        data = response.json()
        return data.get("lyric", "")

    async def get_rankings(self, ranking_type: str = "hot"):
        # QQ音乐热歌榜
        url = "https://c.y.qq.com/v8/fcg-bin/fcg_myqq_toplist.fcg"
        params = {"format": "json", "topid": 26}  # 热歌榜
        headers = {"Referer": "https://y.qq.com"}
        response = await self.client.get(url, params=params, headers=headers)
        data = response.json()
        songs = []
        for item in data.get("songlist", [])[:20]:
            s = item.get("data", {})
            singer = s.get("singer") or []
            songs.append(Song(
                id=str(s.get("songmid", "")),
                name=s.get("songname", ""),
                artist=singer[0].get("name", "") if singer else "",
                album=s.get("albumname", ""),
                duration=s.get("interval", 0),
                platform=Platform.QQ,
                cover_url=f"https://y.gtimg.cn/music/photo_new/T002R300x300M000{s.get('albummid', '')}.jpg"
            ))
        return songs