<template>
  <Transition name="overlay">
    <div v-if="status !== 'playing'" class="overlay" @click.self="$emit('newGame')">
      <div class="overlay-content">
        <h2 class="overlay-title" v-if="status === 'won'">🎉 恭喜你赢了！</h2>
        <h2 class="overlay-title lose" v-else>😞 游戏结束</h2>
        <p class="overlay-score">得分：<strong>{{ score }}</strong></p>
        <button class="btn" @click="$emit('newGame')">再来一局</button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import type { GameStatus } from '../types/game'

defineProps<{
  status: GameStatus
  score: number
}>()

defineEmits<{
  newGame: []
}>()
</script>

<style scoped>
.overlay {
  position: absolute;
  inset: 0;
  background: var(--overlay-bg);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  border-radius: var(--radius);
  backdrop-filter: blur(2px);
}

.overlay-content {
  text-align: center;
  padding: 32px;
}

.overlay-title {
  font-size: 2rem;
  margin-bottom: 12px;
  color: var(--text-color);
}

.overlay-score {
  font-size: 1.1rem;
  margin-bottom: 24px;
  color: var(--text-color);
}

.btn {
  background: var(--btn-bg);
  color: #f9f6f2;
  border: none;
  border-radius: var(--radius);
  padding: 12px 32px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}

.btn:hover {
  background: var(--btn-hover);
}

.overlay-enter-active { transition: opacity 0.3s ease; }
.overlay-leave-active { transition: opacity 0.2s ease; }
.overlay-enter-from, .overlay-leave-to { opacity: 0; }
</style>
