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
