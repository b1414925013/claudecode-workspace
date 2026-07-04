<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const tools = [
  {
    title: 'Visualizer',
    icon: '◉',
    description: '输入 nGQL 脚本，自动解析并渲染为交互式图可视化。支持点、边、属性展示，适合数据探索与调试。',
    path: '/visualize',
    color: '#4E79A7',
  },
  {
    title: 'Builder',
    icon: '⚙',
    description: '通过 GUI 表单定义点类型、边类型及数据，自动生成完整的 nGQL 脚本。支持一键复制与下载。',
    path: '/builder',
    color: '#59A14F',
  },
]
</script>

<template>
  <div class="home">
    <div class="hero">
      <h1 class="hero-title">Nebula Tools</h1>
      <p class="hero-subtitle">Nebula Graph 可视化工具集 — 解析 nGQL 脚本与 GUI 构建</p>
    </div>
    <div class="cards">
      <div
        v-for="tool in tools"
        :key="tool.title"
        class="card"
        :style="{ '--card-color': tool.color }"
        @click="router.push(tool.path)"
      >
        <div class="card-icon">{{ tool.icon }}</div>
        <div class="card-body">
          <h2 class="card-title">{{ tool.title }}</h2>
          <p class="card-desc">{{ tool.description }}</p>
        </div>
        <div class="card-action">打开 →</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
  gap: 48px;
}
.hero {
  text-align: center;
}
.hero-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}
.hero-subtitle {
  margin-top: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}
.cards {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  justify-content: center;
}
.card {
  width: 320px;
  padding: 28px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.card:hover {
  transform: translateY(-3px);
  border-color: var(--card-color, var(--accent));
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}
.card-icon {
  font-size: 36px;
  line-height: 1;
}
.card-body {
  flex: 1;
}
.card-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}
.card-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}
.card-action {
  font-size: 13px;
  color: var(--card-color, var(--accent));
  font-weight: 500;
}
</style>
