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
@import './assets/styles.css';
.app { min-height: 100vh; display: flex; flex-direction: column; }
.header { background: var(--primary); color: white; padding: 16px 24px; display: flex; align-items: center; gap: 24px; position: sticky; top: 0; z-index: 50; }
.logo { font-size: 20px; font-weight: bold; }
.search-box { flex: 1; max-width: 500px; display: flex; }
.search-box input { flex: 1; padding: 8px 16px; border: none; border-radius: 4px 0 0 4px; outline: none; }
.search-box button { padding: 8px 24px; background: var(--primary-dark); color: white; border: none; border-radius: 0 4px 4px 0; cursor: pointer; }
.search-box button:hover { opacity: 0.9; }
.main { display: flex; flex: 1; }
.sidebar { width: 200px; background: white; padding: 24px 0; border-right: 1px solid var(--border); min-height: calc(100vh - 60px); }
.sidebar a { display: block; padding: 12px 24px; color: var(--text); text-decoration: none; transition: all 0.2s; }
.sidebar a:hover { background: var(--primary-light); color: var(--primary); }
.sidebar a.router-link-active { background: var(--primary-light); color: var(--primary); font-weight: 500; border-right: 3px solid var(--primary); }
.content { flex: 1; padding: 24px; margin-bottom: 80px; }

@media (max-width: 768px) {
  .sidebar { display: none; }
  .header { flex-wrap: wrap; gap: 12px; }
  .search-box { order: 3; width: 100%; max-width: 100%; }
  .content { padding: 16px; }
}
</style>
