<template>
  <div class="header">
    <div class="header-top">
      <h1 class="title">2048</h1>
      <div class="scores">
        <div class="score-box">
          <span class="score-label">分数</span>
          <span class="score-value" :key="score">{{ score }}</span>
        </div>
        <div class="score-box">
          <span class="score-label">最高分</span>
          <span class="score-value">{{ bestScore }}</span>
        </div>
      </div>
    </div>
    <div class="header-bottom">
      <p class="subtitle">合并数字，达到 <strong>2048</strong>！</p>
      <button class="btn" @click="$emit('newGame')">新游戏</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  score: number
  bestScore: number
}>()

defineEmits<{
  newGame: []
}>()
</script>

<style scoped>
.header {
  width: 100%;
  max-width: 500px;
  margin-bottom: 12px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title {
  font-size: 4rem;
  font-weight: 900;
  line-height: 1;
  color: var(--text-color);
}

.scores {
  display: flex;
  gap: 8px;
}

.score-box {
  background: var(--score-bg);
  color: #fff;
  border-radius: var(--radius);
  padding: 8px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
}

.score-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  opacity: 0.8;
  letter-spacing: 0.5px;
}

.score-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.header-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.subtitle {
  font-size: 0.9rem;
  color: var(--text-color);
  opacity: 0.8;
}

.btn {
  background: var(--btn-bg);
  color: #f9f6f2;
  border: none;
  border-radius: var(--radius);
  padding: 10px 20px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}

.btn:hover {
  background: var(--btn-hover);
}

@media (max-width: 500px) {
  .title { font-size: 3rem; }
  .score-box { padding: 6px 14px; min-width: 60px; }
  .score-value { font-size: 1.2rem; }
}
</style>
