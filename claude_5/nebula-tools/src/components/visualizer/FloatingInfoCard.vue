<script setup lang="ts">
defineProps<{
  visible: boolean
  x: number
  y: number
  vid: string
  tagName: string
  props: Record<string, string>
  neighbors: string[]
}>()

const emit = defineEmits<{
  close: []
  focusNeighbor: [vid: string]
}>()
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="info-card"
      :style="{ left: x + 'px', top: y + 'px' }"
    >
      <div class="card-head">
        <span class="card-tag" :style="{ background: 'var(--accent)' }">{{ tagName }}</span>
        <span class="card-vid">{{ vid }}</span>
        <button class="card-close" @click="emit('close')">✕</button>
      </div>

      <div class="card-body">
        <div class="section-title">属性</div>
        <div v-for="(val, key) in props" :key="key" class="prop-line">
          <span class="prop-key">{{ key }}</span>
          <span class="prop-val">{{ val }}</span>
        </div>
        <div v-if="Object.keys(props).length === 0" class="empty">无属性</div>

        <div v-if="neighbors.length > 0" class="neighbors-section">
          <div class="section-title">关联 ({{ neighbors.length }})</div>
          <div
            v-for="nid in neighbors.slice(0, 20)"
            :key="nid"
            class="neighbor-link"
            @click="emit('focusNeighbor', nid)"
          >
            {{ nid }}
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.info-card {
  position: fixed;
  z-index: 100;
  min-width: 240px;
  max-width: 340px;
  background: var(--bg-float);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  font-size: 13px;
  transform: translate(10px, -50%);
  overflow: hidden;
}
.card-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
}
.card-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  color: #fff;
  font-weight: 500;
}
.card-vid {
  flex: 1;
  font-weight: 600;
  font-family: var(--font-mono);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-close {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
  padding: 2px;
  line-height: 1;
}
.card-close:hover { color: var(--text-primary); }
.card-body {
  padding: 10px 12px;
  max-height: 300px;
  overflow-y: auto;
}
.section-title {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 8px 0 4px;
}
.section-title:first-child { margin-top: 0; }
.prop-line {
  display: flex;
  gap: 6px;
  padding: 2px 0;
  font-size: 12px;
}
.prop-key { color: var(--text-secondary); min-width: 60px; }
.prop-val { color: var(--text-primary); font-family: var(--font-mono); font-size: 11px; }
.empty { color: var(--text-muted); font-style: italic; font-size: 12px; }
.neighbors-section { margin-top: 4px; }
.neighbor-link {
  padding: 3px 6px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--accent);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.neighbor-link:hover { background: var(--bg-hover); }
</style>
