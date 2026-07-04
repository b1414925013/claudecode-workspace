<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { TagDef, EdgeTypeDef, VertexData, EdgeData } from '../types/nebula'
import { usePersistState } from '../composables/usePersistState'
import { useNebulaGenerator } from '../composables/useNebulaGenerator'
import TagDefEditor from '../components/builder/TagDefEditor.vue'
import EdgeDefEditor from '../components/builder/EdgeDefEditor.vue'
import VertexDataEditor from '../components/builder/VertexDataEditor.vue'
import EdgeDataEditor from '../components/builder/EdgeDataEditor.vue'
import ScriptPreview from '../components/builder/ScriptPreview.vue'

const route = useRoute()
const router = useRouter()
const { generate } = useNebulaGenerator()

const activeTab = computed(() => (route.query.tab as string) || 'tag')

function setTab(tab: string) {
  router.replace({ query: { ...route.query, tab } })
}

const spaceName = usePersistState('nebula-tools:space', '')
const tags = usePersistState<TagDef[]>('nebula-tools:tags', [])
const edgeTypes = usePersistState<EdgeTypeDef[]>('nebula-tools:edgeTypes', [])
const vertices = usePersistState<VertexData[]>('nebula-tools:vertices', [])
const edges = usePersistState<EdgeData[]>('nebula-tools:edges', [])

const script = computed(() => generate(tags.value, edgeTypes.value, vertices.value, edges.value, spaceName.value || undefined))

const tabs = [
  { key: 'tag', label: '🏷️ Tag 定义' },
  { key: 'edge', label: '🔗 Edge 定义' },
  { key: 'vertex', label: '📦 Vertex 数据' },
  { key: 'edgeData', label: '🔀 Edge 数据' },
]

function clearAll() {
  if (!confirm('确认清空所有数据？此操作不可恢复。')) return
  tags.value = []
  edgeTypes.value = []
  vertices.value = []
  edges.value = []
  spaceName.value = ''
}
</script>

<template>
  <div class="builder-layout">
    <div class="builder-top">
      <div class="tab-bar">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="setTab(tab.key)"
        >
          {{ tab.label }}
        </button>
        <div class="tab-spacer" />
        <div class="tab-extra">
          <input v-model="spaceName" class="input space-input" placeholder="Space 名称(可选)" />
          <button class="btn btn-danger" @click="clearAll">清空</button>
        </div>
      </div>

      <div class="tab-content">
        <TagDefEditor v-if="activeTab === 'tag'" :items="tags" @update="tags = $event" />
        <EdgeDefEditor v-if="activeTab === 'edge'" :items="edgeTypes" @update="edgeTypes = $event" />
        <VertexDataEditor v-if="activeTab === 'vertex'" :items="vertices" :tags="tags" @update="vertices = $event" />
        <EdgeDataEditor v-if="activeTab === 'edgeData'" :items="edges" :edgeTypes="edgeTypes" @update="edges = $event" />
      </div>
    </div>

    <div class="builder-bottom">
      <ScriptPreview :script="script" />
    </div>
  </div>
</template>

<style scoped>
.builder-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.builder-top {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.tab-bar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 0 8px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.tab-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.tab-btn:hover { color: var(--text-primary); }
.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
.tab-spacer { flex: 1; }
.tab-extra {
  display: flex;
  align-items: center;
  gap: 8px;
}
.space-input {
  width: 160px;
  font-size: 12px;
  padding: 4px 8px;
}
.tab-content {
  flex: 1;
  overflow-y: auto;
}
.builder-bottom {
  height: 40%;
  min-height: 180px;
  flex-shrink: 0;
}
</style>
