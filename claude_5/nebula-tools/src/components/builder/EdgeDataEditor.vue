<script setup lang="ts">
import { ref, computed } from 'vue'
import type { EdgeData, EdgeTypeDef } from '../../types/nebula'
import SimpleTable from '../common/SimpleTable.vue'

const props = defineProps<{ items: EdgeData[]; edgeTypes: EdgeTypeDef[] }>()
const emit = defineEmits<{ update: [items: EdgeData[]] }>()

const showDialog = ref(false)
const editingIdx = ref(-1)
const form = ref<EdgeData>({ id: '', edgeType: '', fromVid: '', toVid: '', props: {} })

const columns = [
  { key: 'edgeType', label: '类型', width: '80px' },
  { key: 'fromVid', label: 'From', width: '100px' },
  { key: 'toVid', label: 'To', width: '100px' },
  { key: 'rank', label: 'Rank', width: '60px' },
  { key: 'props', label: '属性值' },
]

const selectedEdgeType = computed(() => props.edgeTypes.find(e => e.name === form.value.edgeType))

function addNew() {
  editingIdx.value = -1
  form.value = { id: crypto.randomUUID(), edgeType: '', fromVid: '', toVid: '', props: {} }
  showDialog.value = true
}
function editRow(row: EdgeData) {
  editingIdx.value = props.items.indexOf(row)
  form.value = JSON.parse(JSON.stringify(row))
  showDialog.value = true
}
function confirmDelete(row: EdgeData) {
  emit('update', props.items.filter(r => r !== row))
}
function save() {
  if (!form.value.edgeType || !form.value.fromVid || !form.value.toVid) return
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
      <span class="editor-title">边数据 (Edge)</span>
      <button class="btn btn-primary" @click="addNew">+ 添加 Edge</button>
    </div>
    <SimpleTable :columns="columns" :rows="items" @edit="editRow" @delete="confirmDelete" />

    <Teleport to="body">
      <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
        <div class="modal-box">
          <h3 class="modal-title">{{ editingIdx >= 0 ? '编辑' : '新增' }} Edge</h3>
          <div class="form-row">
            <div class="form-field flex-1">
              <label>Edge 类型</label>
              <select v-model="form.edgeType" class="input">
                <option value="" disabled>选择类型</option>
                <option v-for="e in edgeTypes" :key="e.name" :value="e.name">{{ e.name }}</option>
              </select>
            </div>
            <div class="form-field flex-1">
              <label>Rank (可选)</label>
              <input v-model="form.rank" class="input" type="number" placeholder="0" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-field flex-1">
              <label>From VID</label>
              <input v-model="form.fromVid" class="input" placeholder="起始点 ID" />
            </div>
            <div class="form-field flex-1">
              <label>To VID</label>
              <input v-model="form.toVid" class="input" placeholder="目标点 ID" />
            </div>
          </div>
          <div v-if="selectedEdgeType" class="form-field">
            <label>属性值</label>
            <div v-for="p in selectedEdgeType.props" :key="p.name" class="prop-row">
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
.form-row {
  display: flex;
  gap: 12px;
}
.flex-1 { flex: 1; }
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
</style>
