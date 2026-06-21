<template>
  <Transition name="overlay">
    <div v-if="status === 'won'" class="overlay">
      <div class="overlay-content">
        <h2 class="overlay-title">🎉 恭喜完成！</h2>
        <p class="overlay-score">用了 <strong>{{ moves }}</strong> 步，耗时 <strong>{{ formattedTime }}</strong></p>
        <button class="btn" @click="$emit('newGame')">再来一局</button>
      </div>
    </div>
  </Transition>

  <Transition name="overlay">
    <div v-if="status === 'solving'" class="overlay">
      <div class="overlay-content">
        <h2 class="overlay-title">🤔 正在求解中...</h2>
        <p class="overlay-score">请稍候</p>
      </div>
    </div>
  </Transition>

  <Transition name="overlay">
    <div v-if="status === 'solved'" class="overlay">
      <div class="overlay-content">
        <h2 class="overlay-title">💡 解算完成！</h2>
        <p class="overlay-score">共 {{ solverPath.length }} 步</p>
        <div class="solver-buttons">
          <button class="btn" @click="$emit('applySolverStep')">下一步 ({{ solverStep }} / {{ solverPath.length }})</button>
          <button class="btn btn-secondary" @click="$emit('closeSolver')">关闭</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { GameStatus } from '../types/puzzle'

const props = defineProps<{
  status: GameStatus; moves: number; timer: number
  solverPath: number[]; solverStep: number
}>()

defineEmits<{ newGame: []; applySolverStep: []; closeSolver: [] }>()

const formattedTime = computed(() => {
  const m = Math.floor(props.timer / 60)
  const s = props.timer % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})
</script>

<style scoped>
.overlay {
  position: absolute; inset: 0; background: var(--overlay-bg); display: flex;
  justify-content: center; align-items: center; z-index: 100;
  border-radius: var(--radius); backdrop-filter: blur(2px);
}
.overlay-content { text-align: center; padding: 32px; }
.overlay-title { font-size: 1.8rem; margin-bottom: 12px; color: var(--text-color); }
.overlay-score { font-size: 1rem; margin-bottom: 24px; color: var(--text-color); }
.solver-buttons { display: flex; gap: 10px; justify-content: center; }
.btn {
  background: var(--btn-bg); color: #f9f6f2; border: none; border-radius: var(--radius);
  padding: 12px 24px; font-size: 0.95rem; font-weight: 700; cursor: pointer; transition: background 0.15s;
}
.btn:hover { background: var(--btn-hover); }
.btn-secondary { background: transparent; border: 2px solid var(--btn-bg); color: var(--text-color); }
.btn-secondary:hover { background: var(--btn-bg); color: #f9f6f2; }
.overlay-enter-active { transition: opacity 0.3s ease; }
.overlay-leave-active { transition: opacity 0.2s ease; }
.overlay-enter-from, .overlay-leave-to { opacity: 0; }
</style>
