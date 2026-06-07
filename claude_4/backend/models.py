from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Platform(str, Enum):
    NETEASE = "netease"
    QQ = "qq"
    KUGOU = "kugou"

class Song(BaseModel):
    id: str
    name: str
    artist: str
    album: str
    duration: int
    platform: Platform
    cover_url: str
    play_url: Optional[str] = None

class SearchResult(BaseModel):
    songs: List[Song]
    total: int
    platform: Platform

class RankingType(str, Enum):
    HOT = "hot"
    NEW = "new"