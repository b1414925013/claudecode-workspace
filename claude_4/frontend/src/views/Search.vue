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
