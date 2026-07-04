<script setup lang="ts">
defineProps<{
  columns: { key: string; label: string; width?: string }[]
  rows: Record<string, any>[]
}>()
const emit = defineEmits<{
  edit: [row: Record<string, any>]
  delete: [row: Record<string, any>]
}>()
</script>

<template>
  <table class="simple-table">
    <thead>
      <tr>
        <th v-for="col in columns" :key="col.key" :style="col.width ? { width: col.width } : {}">
          {{ col.label }}
        </th>
        <th class="th-actions">操作</th>
      </tr>
    </thead>
    <tbody>
      <tr v-if="rows.length === 0">
        <td :colspan="columns.length + 1" class="empty-row">暂无数据</td>
      </tr>
      <tr v-for="(row, idx) in rows" :key="idx">
        <td v-for="col in columns" :key="col.key" class="cell">
          {{ typeof row[col.key] === 'object' ? JSON.stringify(row[col.key]) : row[col.key] ?? '-' }}
        </td>
        <td class="cell-actions">
          <button class="btn-sm btn-edit" @click="emit('edit', row)">编辑</button>
          <button class="btn-sm btn-delete" @click="emit('delete', row)">删除</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.simple-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.simple-table th {
  text-align: left;
  padding: 8px 10px;
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
.th-actions {
  width: 100px;
  text-align: center;
}
.simple-table td {
  padding: 8px 10px;
  border-bottom: 1px solid rgba(42, 42, 78, 0.5);
  color: var(--text-primary);
}
.cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.empty-row {
  text-align: center;
  color: var(--text-muted);
  padding: 20px !important;
}
.cell-actions {
  display: flex;
  gap: 4px;
  justify-content: center;
}
.btn-sm {
  padding: 3px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.15s;
}
.btn-edit {
  background: transparent;
  color: var(--accent);
  border-color: var(--accent);
}
.btn-edit:hover {
  background: var(--accent);
  color: #fff;
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
