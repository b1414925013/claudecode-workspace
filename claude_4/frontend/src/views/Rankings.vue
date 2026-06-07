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
