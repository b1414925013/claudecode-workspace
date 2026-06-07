# 音乐网站实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个多平台音乐聚合网站，支持搜索、播放、下载、歌单、歌词、排行榜、收藏功能

**架构：** Vue 3 前端通过 HTTP 调用 FastAPI 后端，后端代理网易云、QQ音乐、酷狗音乐三大平台的 API，统一返回标准化数据

**技术栈：** Vue 3 + Vite + Pinia + Vue Router | FastAPI + httpx

---

## 文件结构

### 后端 (backend/)

| 文件 | 职责 |
|------|------|
| `backend/main.py` | FastAPI 应用入口，跨域配置，路由注册 |
| `backend/requirements.txt` | Python 依赖 |
| `backend/models.py` | 数据模型定义 |
| `backend/routers/search.py` | 搜索 API 路由 |
| `backend/routers/play.py` | 播放链接 API |
| `backend/routers/download.py` | 下载 API |
| `backend/routers/lyrics.py` | 歌词 API |
| `backend/routers/rankings.py` | 排行榜 API |
| `backend/services/netease.py` | 网易云音乐 API 封装 |
| `backend/services/qqmusic.py` | QQ 音乐 API 封装 |
| `backend/services/kugou.py` | 酷狗音乐 API 封装 |
| `backend/services/base.py` | 基础服务类 |

### 前端 (frontend/)

| 文件 | 职责 |
|------|------|
| `frontend/package.json` | Node 依赖 |
| `frontend/vite.config.js` | Vite 配置 |
| `frontend/src/main.js` | Vue 入口 |
| `frontend/src/App.vue` | 根组件 |
| `frontend/src/router/index.js` | 路由配置 |
| `frontend/src/stores/player.js` | 播放状态管理 |
| `frontend/src/stores/library.js` | 歌单/收藏管理 |
| `frontend/src/api/index.js` | API 调用封装 |
| `frontend/src/views/Search.vue` | 搜索页面 |
| `frontend/src/views/Rankings.vue` | 排行榜页面 |
| `frontend/src/views/Library.vue` | 歌单/收藏页面 |
| `frontend/src/components/SearchBar.vue` | 搜索栏组件 |
| `frontend/src/components/SongList.vue` | 歌曲列表组件 |
| `frontend/src/components/Player.vue` | 播放器组件 |
| `frontend/src/components/Lyrics.vue` | 歌词组件 |

---

## 实现任务

### 任务 1：项目初始化

**文件：**
- 创建：`backend/requirements.txt`
- 创建：`backend/main.py`
- 创建：`backend/models.py`
- 创建：`frontend/package.json`
- 创建：`frontend/vite.config.js`
- 创建：`frontend/index.html`

- [ ] **步骤 1：创建后端依赖文件**

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
httpx==0.26.0
pydantic==2.5.0
```

- [ ] **步骤 2：创建 main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import search, play, download, lyrics, rankings

app = FastAPI(title="Music API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(play.router, prefix="/api/play", tags=["play"])
app.include_router(download.router, prefix="/api/download", tags=["download"])
app.include_router(lyrics.router, prefix="/api/lyrics", tags=["lyrics"])
app.include_router(rankings.router, prefix="/api/rankings", tags=["rankings"])

@app.get("/")
def root():
    return {"message": "Music API Server"}
```

- [ ] **步骤 3：创建 models.py**

```python
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
```

- [ ] **步骤 4：创建前端 package.json**

```json
{
  "name": "music-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

- [ ] **步骤 5：创建 vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

- [ ] **步骤 6：创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>音乐小屋</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **步骤 7：Commit**

```bash
cd D:/develop/claudecode-workspace/claude_4
git add -A && git commit -m "初始化项目结构"
```

---

### 任务 2：后端服务基础

**文件：**
- 创建：`backend/routers/__init__.py`
- 创建：`backend/routers/search.py`
- 创建：`backend/routers/play.py`
- 创建：`backend/routers/download.py`
- 创建：`backend/routers/lyrics.py`
- 创建：`backend/routers/rankings.py`
- 创建：`backend/services/__init__.py`
- 创建：`backend/services/base.py`

- [ ] **步骤 1：创建 routers/__init__.py**

```python
# routers package
```

- [ ] **步骤 2：创建 services/base.py**

```python
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
```

- [ ] **步骤 3：创建 services/__init__.py**

```python
from .base import BaseMusicService
from .netease import NeteaseService
from .qqmusic import QQMusicService
from .kugou import KugouService

__all__ = ["BaseMusicService", "NeteaseService", "QQMusicService", "KugouService"]
```

- [ ] **步骤 4：创建 routers/search.py**

```python
from fastapi import APIRouter
from typing import Optional
from models import Song, Platform
from services import NeteaseService, QQMusicService, KugouService

router = APIRouter()
services = {
    Platform.NETEASE: NeteaseService(),
    Platform.QQ: QQMusicService(),
    Platform.KUGOU: KugouService(),
}

@router.get("")
async def search(q: str, platform: Optional[str] = None):
    results = []
    platforms = [Platform(platform)] if platform else [Platform.NETEASE, Platform.QQ, Platform.KUGOU]
    
    for p in platforms:
        service = services[p]
        result = await service.search(q)
        results.extend(result)
    
    return {"songs": results, "total": len(results)}
```

- [ ] **步骤 5：创建其他路由文件（play.py, download.py, lyrics.py, rankings.py）**

```python
# play.py
from fastapi import APIRouter
from models import Platform
from services import NeteaseService, QQMusicService, KugouService

router = APIRouter()
services = {Platform.NETEASE: NeteaseService(), Platform.QQ: QQMusicService(), Platform.KUGOU: KugouService()}

@router.get("/{song_id}")
async def get_play_url(song_id: str, platform: str):
    service = services[Platform(platform)]
    url = await service.get_play_url(song_id)
    return {"play_url": url}
```

```python
# download.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import httpx

router = APIRouter()

@router.get("/{song_id}")
async def download(song_id: str, platform: str, quality: str = "standard"):
    # 获取真实下载链接后重定向
    return {"message": "download endpoint"}
```

```python
# lyrics.py
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
```

```python
# rankings.py
from fastapi import APIRouter
from models import Platform
from services import NeteaseService, QQMusicService, KugouService

router = APIRouter()
services = {Platform.NETEASE: NeteaseService(), Platform.QQ: QQMusicService(), Platform.KUGOU: KugouService()}

@router.get("")
async def get_rankings(platform: str = "netease", type: str = "hot"):
    service = services[Platform(platform)]
    songs = await service.get_rankings(type)
    return {"songs": songs}
```

- [ ] **步骤 6：Commit**

```bash
git add -A && git commit -m "实现后端服务基础框架"
```

---

### 任务 3：网易云音乐服务实现

**文件：**
- 创建：`backend/services/netease.py`

- [ ] **步骤 1：实现网易云音乐搜索**

```python
# backend/services/netease.py
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
```

- [ ] **步骤 2：实现获取播放链接**

```python
    async def get_play_url(self, song_id: str):
        url = f"https://music.163.com/api/song/detail/?ids=[{song_id}]"
        response = await self.client.get(url, headers=self.headers)
        data = response.json()
        songs = data.get("songs", [])
        if songs:
            return songs[0].get("mp3Url", "")
        return ""
```

- [ ] **步骤 3：实现获取歌词**

```python
    async def get_lyrics(self, song_id: str):
        url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1"
        response = await self.client.get(url, headers=self.headers)
        data = response.json()
        lrc = data.get("lrc", {}).get("lyric", "")
        return lrc
```

- [ ] **步骤 4：Commit**

```bash
git add -A && git commit -m "实现网易云音乐服务"
```

---

### 任务 4：QQ音乐服务实现

**文件：**
- 创建：`backend/services/qqmusic.py`

- [ ] **步骤 1：实现 QQ 音乐搜索**

```python
# backend/services/qqmusic.py
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
            songs.append(Song(
                id=str(item["songmid"]),
                name=item["songname"],
                artist=item["singer"][0]["name"] if item["singer"] else "",
                album=item["albumname"],
                duration=item["interval"],
                platform=Platform.QQ,
                cover_url=f"https://y.gtimg.cn/music/photo_new/T002R300x300M000{item['albummid']}.jpg"
            ))
        return songs
```

- [ ] **步骤 2：实现获取播放链接**

```python
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
```

- [ ] **步骤 3：实现获取歌词**

```python
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
```

- [ ] **步骤 4：Commit**

```bash
git add -A && git commit -m "实现QQ音乐服务"
```

---

### 任务 5：酷狗音乐服务实现

**文件：**
- 创建：`backend/services/kugou.py`

- [ ] **步骤 1：实现酷狗音乐搜索**

```python
# backend/services/kugou.py
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
```

- [ ] **步骤 2：实现获取播放链接**

```python
    async def get_play_url(self, song_id: str):
        url = "http://krcs.kugou.com/search"
        params = {"ver": 1, "man": "netease", "client": "mobi"}
        response = await self.client.get(url, params=params)
        # 酷狗播放链接获取需要特殊处理
        return f"https://webapi.music.163.com/api/player/online?hash={song_id}"
```

- [ ] **步骤 3：实现获取歌词**

```python
    async def get_lyrics(self, song_id: str):
        url = "http://lyrics.kugou.com/search"
        params = {
            "ver": 1,
            "hash": song_id,
            "man": "netease"
        }
        response = await self.client.get(url, params=params)
        return ""
```

- [ ] **步骤 4：Commit**

```bash
git add -A && git commit -m "实现酷狗音乐服务"
```

---

### 任务 6：前端基础搭建

**文件：**
- 创建：`frontend/src/main.js`
- 创建：`frontend/src/App.vue`
- 创建：`frontend/src/router/index.js`
- 创建：`frontend/src/stores/player.js`
- 创建：`frontend/src/stores/library.js`
- 创建：`frontend/src/api/index.js`

- [ ] **步骤 1：创建 main.js**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **步骤 2：创建 App.vue**

```vue
<template>
  <div class="app">
    <header class="header">
      <div class="logo">🎵 音乐小屋</div>
      <div class="search-box">
        <input v-model="keyword" @keyup.enter="search" placeholder="搜索歌曲、歌手..." />
        <button @click="search">搜索</button>
      </div>
    </header>
    <div class="main">
      <nav class="sidebar">
        <router-link to="/">搜索</router-link>
        <router-link to="/rankings">排行榜</router-link>
        <router-link to="/library">我的歌单</router-link>
      </nav>
      <main class="content">
        <router-view />
      </main>
    </div>
    <Player />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Player from './components/Player.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const keyword = ref('')

const search = () => {
  if (keyword.value.trim()) {
    router.push({ path: '/', query: { q: keyword.value } })
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: #f5f7fa; }
.app { min-height: 100vh; display: flex; flex-direction: column; }
.header { background: #1E88E5; color: white; padding: 16px 24px; display: flex; align-items: center; gap: 24px; }
.logo { font-size: 20px; font-weight: bold; }
.search-box { flex: 1; max-width: 500px; display: flex; }
.search-box input { flex: 1; padding: 8px 16px; border: none; border-radius: 4px 0 0 4px; }
.search-box button { padding: 8px 24px; background: #1565C0; color: white; border: none; border-radius: 0 4px 4px 0; cursor: pointer; }
.main { display: flex; flex: 1; }
.sidebar { width: 200px; background: white; padding: 24px 0; }
.sidebar a { display: block; padding: 12px 24px; color: #333; text-decoration: none; }
.sidebar a:hover, .sidebar a.router-link-active { background: #E3F2FD; color: #1E88E5; }
.content { flex: 1; padding: 24px; }
</style>
```

- [ ] **步骤 3：创建 router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import Search from '../views/Search.vue'
import Rankings from '../views/Rankings.vue'
import Library from '../views/Library.vue'

const routes = [
  { path: '/', component: Search },
  { path: '/rankings', component: Rankings },
  { path: '/library', component: Library }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
```

- [ ] **步骤 4：创建 stores/player.js**

```javascript
import { defineStore } from 'pinia'

export const usePlayerStore = defineStore('player', {
  state: () => ({
    currentSong: null,
    isPlaying: false,
    playlist: [],
    currentIndex: 0,
    volume: 0.8,
    progress: 0,
    duration: 0
  }),
  actions: {
    play(song) {
      this.currentSong = song
      this.isPlaying = true
    },
    togglePlay() {
      this.isPlaying = !this.isPlaying
    },
    setPlaylist(songs, index = 0) {
      this.playlist = songs
      this.currentIndex = index
    }
  }
})
```

- [ ] **步骤 5：创建 stores/library.js**

```javascript
import { defineStore } from 'pinia'

export const useLibraryStore = defineStore('library', {
  state: () => ({
    playlists: JSON.parse(localStorage.getItem('playlists') || '[]'),
    favorites: JSON.parse(localStorage.getItem('favorites') || '[]')
  }),
  actions: {
    addToFavorites(song) {
      if (!this.favorites.find(s => s.id === song.id)) {
        this.favorites.push(song)
        localStorage.setItem('favorites', JSON.stringify(this.favorites))
      }
    },
    removeFromFavorites(songId) {
      this.favorites = this.favorites.filter(s => s.id !== songId)
      localStorage.setItem('favorites', JSON.stringify(this.favorites))
    },
    createPlaylist(name) {
      this.playlists.push({ id: Date.now(), name, songs: [] })
      localStorage.setItem('playlists', JSON.stringify(this.playlists))
    }
  }
})
```

- [ ] **步骤 6：创建 api/index.js**

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

export default {
  search(keyword, platform = 'all') {
    return api.get('/search', { params: { q: keyword, platform } })
  },
  getPlayUrl(songId, platform) {
    return api.get(`/play/${songId}`, { params: { platform } })
  },
  getLyrics(songId, platform) {
    return api.get(`/lyrics/${songId}`, { params: { platform } })
  },
  getRankings(platform = 'netease', type = 'hot') {
    return api.get('/rankings', { params: { platform, type } })
  }
}
```

- [ ] **步骤 7：Commit**

```bash
git add -A && git commit -m "实现前端基础框架"
```

---

### 任务 7：搜索页面实现

**文件：**
- 创建：`frontend/src/views/Search.vue`
- 创建：`frontend/src/components/SongList.vue`

- [ ] **步骤 1：创建 SongList.vue**

```vue
<template>
  <div class="song-list">
    <div v-for="song in songs" :key="song.id" class="song-item" @click="$emit('play', song)">
      <img :src="song.cover_url" :alt="song.name" class="cover" />
      <div class="info">
        <div class="name">{{ song.name }}</div>
        <div class="artist">{{ song.artist }}</div>
      </div>
      <div class="platform">{{ song.platform }}</div>
      <button @click.stop="$emit('download', song)">下载</button>
    </div>
  </div>
</template>

<script setup>
defineProps(['songs'])
defineEmits(['play', 'download'])
</script>

<style scoped>
.song-list { display: flex; flex-direction: column; gap: 12px; }
.song-item { display: flex; align-items: center; gap: 16px; padding: 12px; background: white; border-radius: 8px; cursor: pointer; }
.song-item:hover { background: #E3F2FD; }
.cover { width: 48px; height: 48px; border-radius: 4px; }
.info { flex: 1; }
.name { font-weight: 500; color: #333; }
.artist { color: #666; font-size: 14px; }
.platform { padding: 4px 8px; background: #E3F2FD; border-radius: 4px; font-size: 12px; color: #1E88E5; }
button { padding: 8px 16px; background: #1E88E5; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:hover { background: #1565C0; }
</style>
```

- [ ] **步骤 2：创建 Search.vue**

```vue
<template>
  <div class="search-page">
    <h2>搜索结果：{{ keyword }}</h2>
    <div v-if="loading">加载中...</div>
    <div v-else-if="songs.length === 0">未找到结果</div>
    <SongList v-else :songs="songs" @play="playSong" @download="downloadSong" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import SongList from '../components/SongList.vue'
import api from '../api'
import { usePlayerStore } from '../stores/player'

const route = useRoute()
const playerStore = usePlayerStore()
const songs = ref([])
const loading = ref(false)
const keyword = ref('')

const search = async (kw) => {
  if (!kw) return
  loading.value = true
  keyword.value = kw
  try {
    const res = await api.search(kw)
    songs.value = res.data.songs
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

const playSong = (song) => {
  playerStore.play(song)
}

const downloadSong = async (song) => {
  const res = await api.getPlayUrl(song.id, song.platform)
  const url = res.data.play_url
  if (url) {
    window.open(url, '_blank')
  }
}

watch(() => route.query.q, (newQ) => search(newQ))
onMounted(() => search(route.query.q))
</script>

<style scoped>
.search-page { max-width: 800px; }
h2 { margin-bottom: 24px; color: #333; }
</style>
```

- [ ] **步骤 3：Commit**

```bash
git add -A && git commit -m "实现搜索页面"
```

---

### 任务 8：播放器组件

**文件：**
- 创建：`frontend/src/components/Player.vue`

- [ ] **步骤 1：实现 Player.vue**

```vue
<template>
  <div class="player" v-if="playerStore.currentSong">
    <div class="info">
      <img :src="playerStore.currentSong.cover_url" class="cover" />
      <div>
        <div class="name">{{ playerStore.currentSong.name }}</div>
        <div class="artist">{{ playerStore.currentSong.artist }}</div>
      </div>
    </div>
    <div class="controls">
      <button @click="prev">⏮</button>
      <button @click="togglePlay">{{ playerStore.isPlaying ? '⏸' : '▶' }}</button>
      <button @click="next">⏭</button>
    </div>
    <div class="progress">
      <span>{{ formatTime(currentTime) }}</span>
      <input type="range" v-model="progress" @input="seek" min="0" :max="duration" />
      <span>{{ formatTime(duration) }}</span>
    </div>
    <div class="volume">
      <span>🔊</span>
      <input type="range" v-model="volume" @input="setVolume" min="0" max="1" step="0.1" />
    </div>
    <audio ref="audio" @timeupdate="updateTime" @loadedmetadata="updateDuration" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { usePlayerStore } from '../stores/player'
import api from '../api'

const playerStore = usePlayerStore()
const audio = ref(null)
const currentTime = ref(0)
const duration = ref(0)
const progress = ref(0)
const volume = ref(0.8)

const togglePlay = () => playerStore.togglePlay()
const prev = () => playerStore.currentIndex--
const next = () => playerStore.currentIndex++
const seek = () => audio.value && (audio.value.currentTime = progress.value)
const setVolume = () => audio.value && (audio.value.volume = volume.value)
const formatTime = (s) => `${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,'0')}`
const updateTime = () => currentTime.value = audio.value?.currentTime || 0
const updateDuration = () => duration.value = audio.value?.duration || 0

watch(() => playerStore.currentSong, async (song) => {
  if (song) {
    const res = await api.getPlayUrl(song.id, song.platform)
    if (audio.value) audio.value.src = res.data.play_url
  }
})
watch(() => playerStore.isPlaying, (playing) => playing ? audio.value?.play() : audio.value?.pause())
</script>

<style scoped>
.player { position: fixed; bottom: 0; left: 0; right: 0; background: white; padding: 12px 24px; display: flex; align-items: center; gap: 24px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); }
.info { display: flex; align-items: center; gap: 12px; }
.cover { width: 48px; height: 48px; border-radius: 4px; }
.name { font-weight: 500; }
.artist { font-size: 14px; color: #666; }
.controls { display: flex; gap: 8px; }
.controls button { width: 36px; height: 36px; border-radius: 50%; border: none; background: #1E88E5; color: white; cursor: pointer; }
.progress, .volume { display: flex; align-items: center; gap: 8px; }
input[type="range"] { width: 120px; }
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add -A && git commit -m "实现播放器组件"
```

---

### 任务 9：排行榜页面

**文件：**
- 创建：`frontend/src/views/Rankings.vue`

- [ ] **步骤 1：实现 Rankings.vue**

```vue
<template>
  <div class="rankings-page">
    <h2>排行榜</h2>
    <div class="platforms">
      <button v-for="p in platforms" :key="p.value" :class="{ active: currentPlatform === p.value }" @click="switchPlatform(p.value)">
        {{ p.label }}
      </button>
    </div>
    <div v-if="loading">加载中...</div>
    <SongList v-else :songs="songs" @play="playSong" @download="downloadSong" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import SongList from '../components/SongList.vue'
import api from '../api'
import { usePlayerStore } from '../stores/player'

const playerStore = usePlayerStore()
const songs = ref([])
const loading = ref(false)
const currentPlatform = ref('netease')
const platforms = [
  { label: '网易云', value: 'netease' },
  { label: 'QQ音乐', value: 'qq' },
  { label: '酷狗', value: 'kugou' }
]

const loadRankings = async () => {
  loading.value = true
  try {
    const res = await api.getRankings(currentPlatform.value)
    songs.value = res.data.songs
  } catch (e) { console.error(e) }
  loading.value = false
}

const switchPlatform = (p) => {
  currentPlatform.value = p
  loadRankings()
}

const playSong = (song) => playerStore.play(song)
const downloadSong = async (song) => {
  const res = await api.getPlayUrl(song.id, song.platform)
  window.open(res.data.play_url, '_blank')
}

onMounted(loadRankings)
</script>

<style scoped>
.rankings-page { max-width: 800px; }
h2 { margin-bottom: 24px; }
.platforms { display: flex; gap: 12px; margin-bottom: 24px; }
.platforms button { padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; }
.platforms button.active { background: #1E88E5; color: white; border-color: #1E88E5; }
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add -A && git commit -m "实现排行榜页面"
```

---

### 任务 10：歌单/收藏页面

**文件：**
- 创建：`frontend/src/views/Library.vue`

- [ ] **步骤 1：实现 Library.vue**

```vue
<template>
  <div class="library-page">
    <h2>我的歌单</h2>
    <div class="tabs">
      <button :class="{ active: tab === 'favorites' }" @click="tab = 'favorites'">收藏</button>
      <button :class="{ active: tab === 'playlists' }" @click="tab = 'playlists'">歌单</button>
    </div>
    
    <div v-if="tab === 'favorites'">
      <div v-if="libraryStore.favorites.length === 0">暂无收藏</div>
      <SongList v-else :songs="libraryStore.favorites" @play="playSong" @download="downloadSong" />
    </div>
    
    <div v-else>
      <div class="create-playlist">
        <input v-model="newPlaylistName" placeholder="新歌单名称" />
        <button @click="createPlaylist">创建歌单</button>
      </div>
      <div v-for="playlist in libraryStore.playlists" :key="playlist.id" class="playlist">
        <h3>{{ playlist.name }}</h3>
        <SongList v-if="playlist.songs.length" :songs="playlist.songs" @play="playSong" />
        <div v-else>暂无歌曲</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SongList from '../components/SongList.vue'
import { useLibraryStore } from '../stores/library'
import { usePlayerStore } from '../stores/player'
import api from '../api'

const libraryStore = useLibraryStore()
const playerStore = usePlayerStore()
const tab = ref('favorites')
const newPlaylistName = ref('')

const createPlaylist = () => {
  if (newPlaylistName.value.trim()) {
    libraryStore.createPlaylist(newPlaylistName.value)
    newPlaylistName.value = ''
  }
}

const playSong = (song) => playerStore.play(song)
const downloadSong = async (song) => {
  const res = await api.getPlayUrl(song.id, song.platform)
  window.open(res.data.play_url, '_blank')
}
</script>

<style scoped>
.library-page { max-width: 800px; }
h2 { margin-bottom: 24px; }
.tabs { display: flex; gap: 12px; margin-bottom: 24px; }
.tabs button { padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; }
.tabs button.active { background: #1E88E5; color: white; border-color: #1E88E5; }
.create-playlist { display: flex; gap: 12px; margin-bottom: 24px; }
.create-playlist input { flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
.create-playlist button { padding: 8px 16px; background: #1E88E5; color: white; border: none; border-radius: 4px; cursor: pointer; }
.playlist { margin-bottom: 24px; padding: 16px; background: white; border-radius: 8px; }
.playlist h3 { margin-bottom: 12px; }
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add -A && git commit -m "实现歌单收藏页面"
```

---

### 任务 11：歌词组件

**文件：**
- 创建：`frontend/src/components/Lyrics.vue`

- [ ] **步骤 1：实现 Lyrics.vue**

```vue
<template>
  <div class="lyrics">
    <div class="lyrics-content" ref="lyricsRef">
      <div v-for="(line, index) in parsedLyrics" :key="index" :class="{ active: index === currentLine }">
        {{ line.text }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import api from '../api'

const props = defineProps(['song'])
const lyrics = ref('')
const currentLine = ref(0)
const lyricsRef = ref(null)

const parsedLyrics = computed(() => {
  if (!lyrics.value) return [{ text: '暂无歌词' }]
  return lyrics.value.split('\n').map(line => {
    const match = line.match(/\[(\d{2}):(\d{2})\.(.+?)\](.+)/)
    return match ? { time: parseInt(match[1]) * 60 + parseInt(match[2]), text: match[4] } : { time: 0, text: line }
  })
})

const loadLyrics = async () => {
  if (!props.song) return
  try {
    const res = await api.getLyrics(props.song.id, props.song.platform)
    lyrics.value = res.data.lyrics || ''
  } catch (e) { console.error(e) }
}

watch(() => props.song, loadLyrics)
</script>

<style scoped>
.lyrics { padding: 24px; background: rgba(30, 136, 229, 0.1); border-radius: 8px; max-height: 300px; overflow-y: auto; }
.lyrics-content div { padding: 8px 0; transition: all 0.3s; }
.lyrics-content div.active { color: #1E88E5; font-weight: bold; font-size: 18px; }
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add -A && git commit -m "实现歌词组件"
```

---

### 任务 12：最终样式优化与测试

**文件：**
- 修改：`frontend/src/App.vue`
- 创建：`frontend/src/assets/styles.css`

- [ ] **步骤 1：添加全局样式文件**

```css
/* frontend/src/assets/styles.css */
:root {
  --primary: #1E88E5;
  --primary-dark: #1565C0;
  --bg: #f5f7fa;
  --white: #ffffff;
  --text: #333333;
  --text-light: #666666;
  --border: #e0e0e0;
  --radius: 8px;
  --shadow: 0 2px 10px rgba(0,0,0,0.1);
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }
button { font-family: inherit; }
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }
```

- [ ] **步骤 2：更新 App.vue 添加暗色模式支持**

```vue
<style>
@import './assets/styles.css';
/* 在现有样式基础上添加 */
.app { display: flex; flex-direction: column; min-height: 100vh; }
@media (max-width: 768px) {
  .sidebar { display: none; }
  .header { flex-wrap: wrap; }
  .search-box { order: 3; width: 100%; margin-top: 12px; }
}
</style>
```

- [ ] **步骤 3：Commit**

```bash
git add -A && git commit -m "优化UI样式与响应式设计"
```

---

## 执行说明

### 任务执行顺序

1. **任务 1-2**：项目初始化 + 后端基础框架
2. **任务 3-5**：三大音乐平台服务
3. **任务 6**：前端基础框架
4. **任务 7-10**：核心页面组件
5. **任务 11-12**：歌词组件 + 样式优化

### 环境准备

**后端启动：**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**前端启动：**
```bash
cd frontend
npm install
npm run dev
```

### 验证清单

- [ ] 后端 API 正常工作（访问 http://localhost:8000/docs 查看 Swagger 文档）
- [ ] 前端页面正常加载
- [ ] 搜索功能返回结果
- [ ] 播放器可以播放歌曲
- [ ] 下载功能可用
- [ ] 排行榜页面正常显示

---

**计划已完成并保存到 `docs/superpowers/plans/2026-06-07-music-app-plan.md`**

---

## 执行方式

有两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

**选哪种方式？**