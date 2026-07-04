<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  search: [query: string]
  zoomIn: []
  zoomOut: []
  resetView: []
  screenshot: []
  togglePhysics: [on: boolean]
}>()

const physicsOn = ref(false)
const searchQuery = ref('')

function onSearch() {
  emit('search', searchQuery.value)
}
</script>

<template>
  <div class="toolbar">
    <div class="toolbar-group">
      <input
        v-model="searchQuery"
        class="search-input"
        placeholder="搜索节点..."
        @input="onSearch"
      />
    </div>
    <div class="toolbar-group">
      <button class="tb-btn" title="放大" @click="emit('zoomIn')">＋</button>
      <button class="tb-btn" title="缩小" @click="emit('zoomOut')">−</button>
      <button class="tb-btn" title="重置视角" @click="emit('resetView')">⟲</button>
    </div>
    <div class="toolbar-group">
      <button class="tb-btn" title="截图" @click="emit('screenshot')">📷</button>
      <button
        class="tb-btn"
        :class="{ active: physicsOn }"
        title="物理引擎"
        @click="physicsOn = !physicsOn; emit('togglePhysics', physicsOn)"
      >⚡</button>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}
.toolbar-group {
  display: flex;
  align-items: center;
  gap: 4px;
}
.toolbar-group + .toolbar-group {
  padding-left: 8px;
  border-left: 1px solid var(--border);
}
.search-input {
  width: 140px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
}
.search-input:focus {
  border-color: var(--accent);
}
.tb-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 15px;
  transition: background 0.15s, color 0.15s;
}
.tb-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.tb-btn.active {
  background: var(--accent);
  color: #fff;
}
</style>
