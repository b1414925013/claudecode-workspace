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
      <button @click.stop="addToFavorites(song)">❤</button>
    </div>
  </div>
</template>

<script setup>
import { useLibraryStore } from '../stores/library'

defineProps(['songs'])
defineEmits(['play', 'download'])

const libraryStore = useLibraryStore()

const addToFavorites = (song) => {
  libraryStore.addToFavorites(song)
}
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
