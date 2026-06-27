<template>
  <div>
    <h2 style="margin-bottom: 20px">审计日志</h2>
    <el-card style="margin-bottom: 20px">
      <el-form :inline="true" :model="query">
        <el-form-item label="操作类型">
          <el-input v-model="query.action" placeholder="如 login/view_secret" style="width: 200px" clearable />
        </el-form-item>
        <el-form-item label="用户">
          <el-input v-model="query.username" placeholder="用户名" style="width: 150px" clearable />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="query.resource_type" clearable placeholder="全部" style="width: 140px">
            <el-option label="环境" value="environment" />
            <el-option label="凭据" value="db_credential" />
            <el-option label="用户" value="user" />
            <el-option label="Secret" value="secret" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchList">查询</el-button>
          <el-button @click="handleExport">导出 CSV</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-card v-loading="loading">
      <el-table :data="list" stripe>
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column prop="action" label="操作" width="180" />
        <el-table-column prop="resource_type" label="资源类型" width="100" />
        <el-table-column prop="resource_name" label="资源名称" width="200" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP" width="140" />
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
      <el-pagination v-model:page="page" :page-size="20" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="fetchList" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '@/api/request'

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const query = reactive({ action: '', username: '', resource_type: '' })

async function fetchList() {
  loading.value = true
  try {
    const res: any = await request.get('/audit-logs', { params: { ...query, page: page.value, size: 20 } })
    list.value = res.data.items
    total.value = res.data.total
  } catch {} finally { loading.value = false }
}

async function handleExport() {
  try {
    const res = await request.get('/audit-logs/export', { params: query, responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res]))
    const a = document.createElement('a')
    a.href = url
    a.download = `audit_logs_${Date.now()}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch {}
}

onMounted(fetchList)
</script>
