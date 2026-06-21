<template>
  <div class="controls">
    <button class="btn" :disabled="!canUndo" @click="$emit('undo')">
      ↩ 撤销
    </button>

    <div class="control-group">
      <label class="control-label">棋盘</label>
      <select class="select" :value="boardSize" @change="onSizeChange">
        <option :value="4">4×4</option>
        <option :value="5">5×5</option>
        <option :value="6">6×6</option>
      </select>
    </div>

    <button class="btn btn-icon" @click="$emit('toggleDark')" :title="isDark ? '切换亮色模式' : '切换深色模式'">
      {{ isDark ? '☀️' : '🌙' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import type { BoardSize } from '../types/game'

defineProps<{
  canUndo: boolean
  boardSize: BoardSize
  isDark: boolean
}>()

const emit = defineEmits<{
  undo: []
  changeSize: [size: BoardSize]
  toggleDark: []
}>()

function onSizeChange(e: Event) {
  const val = parseInt((e.target as HTMLSelectElement).value) as BoardSize
  emit('changeSize', val)
}
</script>

<style scoped>
.controls {
  width: 100%;
  max-width: 500px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
}

.btn {
  background: var(--btn-bg);
  color: #f9f6f2;
  border: none;
  border-radius: var(--radius);
  padding: 10px 16px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn:not(:disabled):hover {
  background: var(--btn-hover);
}

.btn-icon {
  padding: 10px 12px;
  font-size: 1.2rem;
  line-height: 1;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
}

.control-label {
  font-size: 0.8rem;
  color: var(--text-color);
  opacity: 0.8;
}

.select {
  background: var(--btn-bg);
  color: #f9f6f2;
  border: none;
  border-radius: var(--radius);
  padding: 9px 12px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  outline: none;
}

.select:hover {
  background: var(--btn-hover);
}

@media (max-width: 500px) {
  .controls { flex-wrap: wrap; }
  .control-group { margin-left: 0; }
}
</style>
