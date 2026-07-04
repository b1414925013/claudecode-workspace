<script setup lang="ts">
import { ref } from 'vue'
import type { TagDef } from '../../types/nebula'
import SimpleTable from '../common/SimpleTable.vue'

const props = defineProps<{ items: TagDef[] }>()
const emit = defineEmits<{ update: [items: TagDef[]] }>()

const showDialog = ref(false)
const editingIdx = ref(-1)
const form = ref<TagDef>({ id: '', name: '', props: [] })

const columns = [
  { key: 'name', label: '标签名' },
  { key: 'props', label: '属性' },
]

function addNew() {
  editingIdx.value = -1
  form.value = { id: crypto.randomUUID(), name: '', props: [] }
  showDialog.value = true
}

function editRow(row: TagDef) {
  editingIdx.value = props.items.indexOf(row)
  form.value = JSON.parse(JSON.stringify(row))
  showDialog.value = true
}

function confirmDelete(row: TagDef) {
  const next = props.items.filter(r => r !== row)
  emit('update', next)
}

function save() {
  if (!form.value.name.trim()) return
  const next = [...props.items]
  if (editingIdx.value >= 0) {
    next[editingIdx.value] = { ...form.value }
  } else {
    next.push({ ...form.value })
  }
  emit('update', next)
  showDialog.value = false
}

function addProp() {
  form.value.props.push({ name: '', type: 'string' })
}

function removeProp(idx: number) {
  form.value.props.splice(idx, 1)
}
</script>

<template>
  <div class="editor-section">
    <div class="editor-header">
      <span class="editor-title">点类型 (Tag) 定义</span>
      <button class="btn btn-primary" @click="addNew">+ 添加 Tag</button>
    </div>
    <SimpleTable :columns="columns" :rows="items" @edit="editRow" @delete="confirmDelete" />

    <Teleport to="body">
      <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
        <div class="modal-box">
          <h3 class="modal-title">{{ editingIdx >= 0 ? '编辑' : '新增' }} Tag</h3>
          <div class="form-field">
            <label>标签名</label>
            <input v-model="form.name" class="input" placeholder="例如: person" />
          </div>
          <div class="form-field">
            <label>属性</label>
            <div v-for="(p, pi) in form.props" :key="pi" class="prop-row">
              <input v-model="p.name" class="input prop-name" placeholder="属性名" />
              <select v-model="p.type" class="input prop-type">
                <option v-for="t in ['string','int','float','double','bool','date']" :key="t" :value="t">{{ t }}</option>
              </select>
              <input v-model="p.default" class="input prop-default" placeholder="默认值(可选)" />
              <button class="btn-sm btn-delete" @click="removeProp(pi)">✕</button>
            </div>
            <button class="btn btn-text" @click="addProp">+ 添加属性</button>
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
.btn-sm {
  padding: 3px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.15s;
}
.btn-delete {
  background: transparent;
  color: var(--danger);
  border-color: var(--danger);
}
.btn-delete:hover {
  background: var(--danger);
  color: #fff;
}
</style>
