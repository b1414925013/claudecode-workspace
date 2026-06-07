<template>
  <div class="library-page">
    <h2>我的歌单</h2>
    <div class="tabs">
      <button :class="{ active: tab === 'favorites' }" @click="tab = 'favorites'">收藏</button>
      <button :class="{ active: tab === 'playlists' }" @click="tab = 'playlists'">歌单</button>
    </div>

    <div v-if="tab === 'favorites'">
      <div v-if="libraryStore.favorites.length === 0" class="empty">暂无收藏</div>
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
        <div v-else class="empty">暂无歌曲</div>
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
.playlist h3 { margin-bottom: 12px; color: #333; }
.empty { padding: 24px; text-align: center; color: #999; }
</style>
