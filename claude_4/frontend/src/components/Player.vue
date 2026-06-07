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
      <input type="range" v-model.number="progress" @input="seek" min="0" :max="duration" />
      <span>{{ formatTime(duration) }}</span>
    </div>
    <div class="volume">
      <span>🔊</span>
      <input type="range" v-model.number="volume" @input="setVolume" min="0" max="1" step="0.1" />
    </div>
    <audio ref="audioRef" @timeupdate="updateTime" @loadedmetadata="updateDuration" @ended="next" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { usePlayerStore } from '../stores/player'
import api from '../api'

const playerStore = usePlayerStore()
const audioRef = ref(null)
const currentTime = ref(0)
const duration = ref(0)
const progress = ref(0)
const volume = ref(0.8)

const togglePlay = () => playerStore.togglePlay()

const prev = () => {
  if (playerStore.currentIndex > 0) {
    playerStore.currentIndex--
    const prevSong = playerStore.playlist[playerStore.currentIndex]
    if (prevSong) playerStore.play(prevSong)
  }
}

const next = () => {
  if (playerStore.currentIndex < playerStore.playlist.length - 1) {
    playerStore.currentIndex++
    const nextSong = playerStore.playlist[playerStore.currentIndex]
    if (nextSong) playerStore.play(nextSong)
  }
}

const seek = () => {
  if (audioRef.value) {
    audioRef.value.currentTime = progress.value
  }
}
const setVolume = () => {
  if (audioRef.value) {
    audioRef.value.volume = volume.value
  }
}
const formatTime = (s) => `${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,'0')}`
const updateTime = () => {
  currentTime.value = audioRef.value?.currentTime || 0
  progress.value = audioRef.value?.currentTime || 0
}
const updateDuration = () => {
  duration.value = audioRef.value?.duration || 0
}

watch(() => playerStore.currentSong, async (song) => {
  if (song && audioRef.value) {
    const res = await api.getPlayUrl(song.id, song.platform)
    if (res.data.play_url) {
      audioRef.value.src = res.data.play_url
      audioRef.value.play()
    }
  }
})

watch(() => playerStore.isPlaying, (playing) => {
  if (audioRef.value) {
    playing ? audioRef.value.play() : audioRef.value.pause()
  }
})
</script>

<style scoped>
.player { position: fixed; bottom: 0; left: 0; right: 0; background: white; padding: 12px 24px; display: flex; align-items: center; gap: 24px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); z-index: 100; }
.info { display: flex; align-items: center; gap: 12px; min-width: 200px; }
.cover { width: 48px; height: 48px; border-radius: 4px; }
.name { font-weight: 500; font-size: 14px; }
.artist { font-size: 12px; color: #666; }
.controls { display: flex; gap: 8px; }
.controls button { width: 36px; height: 36px; border-radius: 50%; border: none; background: #1E88E5; color: white; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; }
.progress, .volume { display: flex; align-items: center; gap: 8px; }
.progress span { font-size: 12px; color: #666; min-width: 35px; }
input[type="range"] { width: 120px; height: 4px; cursor: pointer; }
</style>
