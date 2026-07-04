<script setup lang="ts">
import { ref, computed } from 'vue'
import type { VertexData, TagDef } from '../../types/nebula'
import SimpleTable from '../common/SimpleTable.vue'

const props = defineProps<{ items: VertexData[]; tags: TagDef[] }>()
const emit = defineEmits<{ update: [items: VertexData[]] }>()

const showDialog = ref(false)
const editingIdx = ref(-1)
const form = ref<VertexData>({ id: '', vid: '', tagName: '', props: {} })

const columns = [
  { key: 'vid', label: 'VID', width: '120px' },
  { key: 'tagName', label: 'Tag', width: '100px' },
  { key: 'props', label: '属性值' },
]

const selectedTag = computed(() => props.tags.find(t => t.name === form.value.tagName))

function addNew() {
  editingIdx.value = -1
  form.value = { id: crypto.randomUUID(), vid: '', tagName: '', props: {} }
  showDialog.value = true
}
function editRow(row: VertexData) {
  editingIdx.value = props.items.indexOf(row)
  form.value = JSON.parse(JSON.stringify(row))
  showDialog.value = true
}
function confirmDelete(row: VertexData) {
  emit('update', props.items.filter(r => r !== row))
}
function save() {
  if (!form.value.vid.trim() || !form.value.tagName) return
  const next = [...props.items]
  if (editingIdx.value >= 0) next[editingIdx.value] = { ...form.value }
  else next.push({ ...form.value })
  emit('update', next)
  showDialog.value = false
}
</script>

<template>
  <div class="editor-section">
    <div class="editor-header">
      <span class="editor-title">顶点数据 (Vertex)</span>
      <button class="btn btn-primary" @click="addNew">+ 添加 Vertex</button>
    </div>
    <SimpleTable :columns="columns" :rows="items" @edit="editRow" @delete="confirmDelete" />

    <Teleport to="body">
      <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
        <div class="modal-box">
          <h3 class="modal-title">{{ editingIdx >= 0 ? '编辑' : '新增' }} Vertex</h3>
          <div class="form-field">
            <label>VID</label>
            <input v-model="form.vid" class="input" placeholder="顶点 ID" />
          </div>
          <div class="form-field">
            <label>Tag</label>
            <select v-model="form.tagName" class="input">
              <option value="" disabled>选择 Tag</option>
              <option v-for="t in tags" :key="t.name" :value="t.name">{{ t.name }}</option>
            </select>
            <p v-if="tags.length === 0" class="form-hint">请先在 Tag 定义页面创建点类型</p>
          </div>
          <div v-if="selectedTag" class="form-field">
            <label>属性值</label>
            <div v-for="p in selectedTag.props" :key="p.name" class="prop-row">
              <span class="prop-label">{{ p.name }} ({{ p.type }})</span>
              <input
                v-model="form.props[p.name]"
                class="input"
                :type="p.type === 'int' || p.type === 'float' || p.type === 'double' ? 'number' : p.type === 'bool' ? 'checkbox' : 'text'"
                :placeholder="p.default ?? p.type"
              />
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDialog = false">取消</button>
            <button class="btn btn-primary" @click="save">保存</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.editor-section {
  padding: 16px;
}
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.editor-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}
.prop-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.prop-label {
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 100px;
}
.form-hint {
  font-size: 12px;
  color: var(--warning);
  margin-top: 4px;
}
</style>
