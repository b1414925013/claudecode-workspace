<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const links = [
  { path: '/', label: 'Home', icon: '⌂' },
  { path: '/visualize', label: 'Visualizer', icon: '◉' },
  { path: '/builder', label: 'Builder', icon: '⚙' },
]
</script>

<template>
  <nav class="navbar">
    <span class="navbar-brand">Nebula Tools</span>
    <div class="navbar-links">
      <router-link
        v-for="link in links"
        :key="link.path"
        :to="link.path"
        class="nav-link"
        :class="{ active: router.currentRoute.value.path === link.path }"
      >
        <span class="nav-icon">{{ link.icon }}</span>
        {{ link.label }}
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  gap: 24px;
  height: 44px;
  padding: 0 20px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  user-select: none;
}
.navbar-brand {
  font-weight: 600;
  font-size: 14px;
  color: var(--accent);
  letter-spacing: 0.03em;
}
.navbar-links {
  display: flex;
  gap: 4px;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-secondary);
  transition: background 0.15s, color 0.15s;
}
.nav-link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.nav-link.active {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.nav-icon {
  font-size: 14px;
}
</style>
