<template>
  <div class="header">
    <div class="header-top">
      <h1 class="title">数字华容道</h1>
      <div class="stats">
        <div class="stat-box">
          <span class="stat-label">步数</span>
          <span class="stat-value">{{ moves }}</span>
        </div>
        <div class="stat-box">
          <span class="stat-label">时间</span>
          <span class="stat-value">{{ formattedTime }}</span>
        </div>
      </div>
    </div>
    <div class="header-bottom">
      <p class="subtitle">移动方块，按顺序排列 <strong>1~{{ maxNumber }}</strong></p>
      <button class="btn" @click="$emit('newGame')">新游戏</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PuzzleSize } from '../types/puzzle'

const props = defineProps<{
  moves: number
  timer: number
  size: PuzzleSize
}>()

defineEmits<{ newGame: [] }>()

const maxNumber = computed(() => props.size * props.size - 1)

const formattedTime = computed(() => {
  const m = Math.floor(props.timer / 60)
  const s = props.timer % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})
</script>

<style scoped>
.header { width: 100%; max-width: 500px; margin-bottom: 12px; }
.header-top { display: flex; justify-content: space-between; align-items: flex-start; }
.title { font-size: 2.5rem; font-weight: 900; line-height: 1; color: var(--text-color); }
.stats { display: flex; gap: 8px; }
.stat-box {
  background: var(--score-bg); color: #fff; border-radius: var(--radius);
  padding: 8px 16px; display: flex; flex-direction: column; align-items: center; min-width: 70px;
}
.stat-label { font-size: 0.7rem; text-transform: uppercase; opacity: 0.8; }
.stat-value { font-size: 1.3rem; font-weight: 700; font-variant-numeric: tabular-nums; }
.header-bottom { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.subtitle { font-size: 0.85rem; color: var(--text-color); opacity: 0.8; }
.btn {
  background: var(--btn-bg); color: #f9f6f2; border: none; border-radius: var(--radius);
  padding: 10px 20px; font-size: 0.9rem; font-weight: 700; cursor: pointer;
  transition: background 0.15s; white-space: nowrap;
}
.btn:hover { background: var(--btn-hover); }
@media (max-width: 500px) {
  .title { font-size: 2rem; }
  .stat-box { padding: 6px 12px; min-width: 60px; }
  .stat-value { font-size: 1.1rem; }
}
</style>
