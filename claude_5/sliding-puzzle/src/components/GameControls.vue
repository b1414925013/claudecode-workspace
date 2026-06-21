<template>
  <div class="controls">
    <button class="btn" @click="$emit('shuffle')">🔀 打乱</button>
    <div class="control-group">
      <label class="control-label">棋盘</label>
      <select class="select" :value="size" @change="onSizeChange">
        <option :value="3">3×3</option>
        <option :value="4">4×4</option>
        <option :value="5">5×5</option>
      </select>
    </div>
    <button class="btn" :disabled="isSolving" @click="$emit('solve')">💡 解算</button>
    <div class="control-group">
      <label class="control-label">模式</label>
      <button class="btn btn-sm" @click="$emit('toggleMode')">{{ mode === 'number' ? '🔢' : '🖼️' }}</button>
    </div>
    <button class="btn btn-icon" @click="$emit('toggleDark')" :title="isDark ? '亮色模式' : '深色模式'">
      {{ isDark ? '☀️' : '🌙' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import type { PuzzleSize, GameMode } from '../types/puzzle'

defineProps<{ size: PuzzleSize; isDark: boolean; mode: GameMode; isSolving: boolean }>()

const emit = defineEmits<{
  shuffle: []; changeSize: [size: PuzzleSize]; toggleDark: []; toggleMode: []; solve: []
}>()

function onSizeChange(e: Event) {
  emit('changeSize', parseInt((e.target as HTMLSelectElement).value) as PuzzleSize)
}
</script>

<style scoped>
.controls {
  width: 100%; max-width: 500px; display: flex; align-items: center;
  gap: 8px; margin-top: 12px; flex-wrap: wrap;
}
.btn {
  background: var(--btn-bg); color: #f9f6f2; border: none; border-radius: var(--radius);
  padding: 9px 14px; font-size: 0.8rem; font-weight: 700; cursor: pointer;
  transition: background 0.15s; white-space: nowrap;
}
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn:not(:disabled):hover { background: var(--btn-hover); }
.btn-sm { padding: 9px 12px; font-size: 1rem; line-height: 1; }
.btn-icon { padding: 9px 10px; font-size: 1.1rem; line-height: 1; }
.control-group { display: flex; align-items: center; gap: 4px; }
.control-label { font-size: 0.75rem; color: var(--text-color); opacity: 0.8; }
.select {
  background: var(--btn-bg); color: #f9f6f2; border: none; border-radius: var(--radius);
  padding: 8px 10px; font-size: 0.8rem; font-weight: 600; cursor: pointer; outline: none;
}
.select:hover { background: var(--btn-hover); }
</style>
