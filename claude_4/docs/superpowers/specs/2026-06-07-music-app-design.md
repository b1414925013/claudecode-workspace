# 音乐网站设计规格

## 项目概述

免费听歌、下载歌曲的多平台音乐聚合网站，支持网易云音乐、QQ音乐、酷狗音乐三大平台。

## 技术栈

### 前端
- Vue 3 + Vite
- 状态管理：Pinia
-路由：Vue Router
- HTTP 客户端：Axios

### 后端
- FastAPI (Python 3.10+)
- HTTP 客户端：httpx
- 音乐源：网易云音乐、QQ音乐、酷狗音乐 API

## 目录结构

```
music-app/
├── frontend/ # Vue 3 前端
│   ├── src/
│   │   ├── components/ # UI组件
│   │   ├── views/      # 页面视图
│   │   ├── stores/     # Pinia 状态管理
│   │   ├── api/        # API 调用模块
│   │   ├── router/     # 路由配置
│   │   └── assets/     # 静态资源
│   ├── package.json
│   └── vite.config.js
├── backend/            # FastAPI 后端
│   ├── main.py         # 应用入口
│   ├── routers/        # API 路由
│   │   ├── search.py   # 搜索路由
│   │   ├── play.py     # 播放路由
│   │   ├── download.py # 下载路由
│   │   └── lyrics.py   # 歌词路由
│   ├── services/       # 音乐平台服务
│   │   ├── netease.py  # 网易云音乐
│   │   ├── qqmusic.py  # QQ音乐
│   │   └── kugou.py    # 酷狗音乐
│   └── requirements.txt
└── docs/              # 文档
```

## 功能规格

### 1. 歌曲搜索
- 支持关键词搜索歌曲、歌手、专辑
- 多平台同时搜索，统一展示结果
- 显示来源平台标识
- 搜索历史记录

### 2. 在线播放
- 歌曲在线播放
- 播放/暂停/上一首/下一首
- 进度条拖拽
- 音量控制
- 播放模式切换（列表循环/单曲循环/随机播放）

### 3. 歌曲下载
- 多音质选择（标准/高品质/无损）
- 显示文件大小
- 下载进度展示
- 下载完成后通知

### 4. 播放列表
- 创建歌单
- 歌单命名/重命名
- 添加/移除歌曲
- 歌单排序
- 本地存储歌单数据

### 5. 歌词显示
- 滚动歌词同步
- 歌词时间轴
- 当前行高亮
- 无歌词时显示占位

### 6. 排行榜
- 各平台热歌榜
- 榜单分类（华语/欧美/日韩等）
- 点击歌曲直接播放

### 7. 收藏功能
- 收藏/取消收藏歌曲
- 收藏列表管理
- 本地存储收藏数据

## UI 设计

###视觉风格
- 科技蓝主题
- 蓝色主调 (#1E88E5)
- 卡片式布局
- 清晰的信息层次

### 页面布局
```
┌──────────────────────────────────────────┐
│ 🔵 Logo    [搜索框]              👤用户 │
├────────┬─────────────────────────────────┤
│        │                                 │
│  📋 歌单 │     主内容区域                  │
│  🎵 播放 │     (搜索结果/排行榜/详情)      │
│ 📊 排行 │                                 │
│  ❤️收藏 │                                 │
│        │                                 │
├────────┴─────────────────────────────────┤
│ ◀◀  ▶  ▶▶  ━━━━●━━━━━━━━  🔊 ━━●━  歌名 │
└──────────────────────────────────────────┘
```

### 响应式设计
- 桌面端：侧边栏 + 主内容区
- 平板端：可收起侧边栏
- 移动端：底部导航 + 全屏播放

## API 设计

### 后端接口

####搜索
- `GET /api/search?q={keyword}&platform={all|netease|qq|kugou}`
  - 返回：歌曲列表

#### 歌曲详情
- `GET /api/song/{song_id}?platform={platform}`
  - 返回：歌曲详情、播放链接

#### 歌词
- `GET /api/lyrics/{song_id}?platform={platform}`
  - 返回：歌词内容

#### 下载
- `GET /api/download/{song_id}?platform={platform}&quality={standard|high|lossless}`
  - 返回：音频文件流

#### 排行榜
- `GET /api/rankings?platform={platform}&type={type}`
  - 返回：排行榜歌曲列表

## 数据模型

### 歌曲
```typescript
interface Song {
  id: string;
  name: string;
  artist: string;
  album: string;
  duration: number; // 秒
  platform: 'netease' | 'qq' | 'kugou';
  coverUrl: string;
  playUrl: string;
}
```

### 歌单
```typescript
interface Playlist {
  id: string;
  name: string;
  songs: Song[];
  createdAt: Date;
}
```

## 约束与限制

- 后端代理绕过 CORS 限制
- 搜索结果限制每次返回 20 条
- 下载需要处理跨域重定向
- 本地存储使用 localStorage
- 排行榜缓存30 分钟

## 开发计划

1. 项目初始化（前端 + 后端）
2. 后端服务搭建（FastAPI + 路由）
3. 音乐平台 API 对接
4. 前端页面搭建
5. 核心功能实现
6. UI 样式优化
7. 测试与调试
