import httpx
from abc import ABC, abstractmethod

class BaseMusicService(ABC):
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    @abstractmethod
    async def search(self, keyword: str, page: int = 1, limit: int = 20):
        pass

    @abstractmethod
    async def get_play_url(self, song_id: str):
        pass

    @abstractmethod
    async def get_lyrics(self, song_id: str):
        pass

    async def close(self):
        await self.client.aclose()