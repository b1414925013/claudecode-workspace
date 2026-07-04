<script setup lang="ts">
import NavBar from './components/layout/NavBar.vue'
</script>

<template>
  <div class="app-shell">
    <NavBar />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}
.main-content {
  flex: 1;
  overflow: hidden;
}
</style>
