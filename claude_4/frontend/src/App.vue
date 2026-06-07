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
