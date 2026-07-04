<script setup lang="ts">
import { ref } from 'vue'
import { useNebulaParser } from '../composables/useNebulaParser'
import NGqlEditor from '../components/visualizer/NGqlEditor.vue'
import GraphCanvas from '../components/visualizer/GraphCanvas.vue'
import FloatingInfoCard from '../components/visualizer/FloatingInfoCard.vue'
import GraphToolbar from '../components/visualizer/GraphToolbar.vue'

const nGqlInput = ref(`-- Nebula Graph 示例
CREATE TAG IF NOT EXISTS person(name string, age int, city string);
CREATE TAG IF NOT EXISTS movie(title string, year int);

CREATE EDGE IF NOT EXISTS knows(weight int);
CREATE EDGE IF NOT EXISTS likes(rating float);

INSERT VERTEX person(name, age, city) VALUES "p1": ("张三", 30, "北京");
INSERT VERTEX person(name, age, city) VALUES "p2": ("李四", 25, "上海");
INSERT VERTEX person(name, age, city) VALUES "p3": ("王五", 35, "深圳");
INSERT VERTEX movie(title, year) VALUES "m1": ("流浪地球", 2019);
INSERT VERTEX movie(title, year) VALUES "m2": ("哪吒", 2020);

INSERT EDGE knows(weight) VALUES "p1" -> "p2": (5);
INSERT EDGE knows(weight) VALUES "p2" -> "p3": (3);
INSERT EDGE likes(rating) VALUES "p1" -> "m1": (4.5);
INSERT EDGE likes(rating) VALUES "p2" -> "m2": (4.0);
INSERT EDGE likes(rating) VALUES "p3" -> "m1": (3.8);
`)

const { parsed, tagColors, edgeColors, error, summary } = useNebulaParser(nGqlInput)

// Editor panel width (default 40%)
const editorWidth = ref(40)
const editorVisible = ref(true)
let dragStart = 0
let dragBase = 0

function onResizeStart(e: MouseEvent) {
  dragStart = e.clientX
  dragBase = editorWidth.value
  document.addEventListener('mousemove', onResizeMove)
  document.addEventListener('mouseup', onResizeEnd)
}
function onResizeMove(e: MouseEvent) {
  const total = window.innerWidth
  const delta = ((e.clientX - dragStart) / total) * 100
  editorWidth.value = Math.max(15, Math.min(70, dragBase + delta))
}
function onResizeEnd() {
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeEnd)
}

// Floating info card
const cardVisible = ref(false)
const cardPos = ref({ x: 0, y: 0 })
const selectedNode = ref({ vid: '', tagName: '', props: {} as Record<string, string>, neighbors: [] as string[] })

function onNodeClick(data: { id: string; vid: string; tagName: string; props: Record<string, string>; neighbors: string[] }) {
  selectedNode.value = data
  cardPos.value = { x: window.innerWidth - 360, y: Math.min(data.neighbors.length * 24 + 80, window.innerHeight - 100) }
  cardVisible.value = true
}

function onBackgroundClick() {
  cardVisible.value = false
}

// Graph canvas ref
const graphRef = ref<InstanceType<typeof GraphCanvas>>()

function handleSearch(query: string) {
  if (!query.trim() || !graphRef.value) return
  graphRef.value.focusNode(query.trim())
}
</script>

<template>
  <div class="visualizer-layout">
    <!-- Left: nGQL Editor -->
    <div v-if="editorVisible" class="editor-panel" :style="{ width: editorWidth + '%' }">
      <NGqlEditor
        v-model="nGqlInput"
        :summary="summary"
        :error="error"
      />
    </div>

    <!-- Resize handle -->
    <div v-if="editorVisible" class="resize-handle" @mousedown="onResizeStart" />

    <!-- Right: Graph + Toolbar -->
    <div class="graph-area">
      <GraphCanvas
        ref="graphRef"
        :parsed="parsed"
        :tag-colors="tagColors"
        :edge-colors="edgeColors"
        @node-click="onNodeClick"
        @background-click="onBackgroundClick"
      />

      <!-- Floating Toolbar -->
      <div class="toolbar-float">
        <GraphToolbar
          @search="handleSearch"
          @zoom-in="graphRef?.focusNode"
          @zoom-out=""
          @reset-view="graphRef?.fit()"
          @toggle-physics="(on: boolean) => graphRef?.togglePhysics(on)"
        />
      </div>

      <!-- Editor toggle pill -->
      <button class="toggle-editor" @click="editorVisible = !editorVisible" :title="editorVisible ? '收起编辑器' : '展开编辑器'">
        {{ editorVisible ? '◀' : '▶' }}
      </button>
    </div>

    <!-- Floating Info Card -->
    <FloatingInfoCard
      :visible="cardVisible"
      :x="cardPos.x"
      :y="cardPos.y"
      :vid="selectedNode.vid"
      :tag-name="selectedNode.tagName"
      :props="selectedNode.props"
      :neighbors="selectedNode.neighbors"
      @close="cardVisible = false"
      @focus-neighbor="(vid: string) => { graphRef?.focusNode(vid); cardVisible = false }"
    />
  </div>
</template>

<style scoped>
.visualizer-layout {
  display: flex;
  height: 100%;
  position: relative;
}
.editor-panel {
  flex-shrink: 0;
  overflow: hidden;
}
.resize-handle {
  width: 4px;
  cursor: col-resize;
  background: transparent;
  flex-shrink: 0;
  z-index: 5;
  transition: background 0.15s;
}
.resize-handle:hover {
  background: var(--accent);
}
.graph-area {
  flex: 1;
  position: relative;
  overflow: hidden;
}
.toolbar-float {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
}
.toggle-editor {
  position: absolute;
  top: 12px;
  left: 8px;
  z-index: 10;
  width: 24px;
  height: 24px;
  background: rgba(26, 26, 46, 0.8);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.toggle-editor:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>
