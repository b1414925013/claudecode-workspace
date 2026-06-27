<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>数据库凭据</h2>
      <el-button type="primary" @click="openDialog()">新增凭据</el-button>
    </div>
    <el-card style="margin-bottom: 20px">
      <el-form :inline="true" :model="query">
        <el-form-item label="环境">
          <el-select v-model="query.env_id" clearable placeholder="全部" style="width: 160px">
            <el-option v-for="e in envList" :key="e.id" :label="e.label" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据库类型">
          <el-select v-model="query.db_type" clearable placeholder="全部" style="width: 140px">
            <el-option label="MySQL" value="mysql" />
            <el-option label="Redis" value="redis" />
            <el-option label="PostgreSQL" value="postgresql" />
            <el-option label="MongoDB" value="mongodb" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="服务名">
          <el-input v-model="query.service_name" placeholder="搜索" style="width: 160px" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchList">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-card v-loading="loading">
      <el-table :data="list" stripe>
        <el-table-column prop="service_name" label="服务名" width="150" />
        <el-table-column prop="db_type" label="类型" width="80" />
        <el-table-column prop="host" label="地址" width="180" />
        <el-table-column prop="port" label="端口" width="70" />
        <el-table-column prop="database_name" label="数据库" width="150" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column label="密码" width="120">
          <template>{{ '******' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleReveal(row)">查看密码</el-button>
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:page="query.page" :page-size="query.size" :total="total" layout="total, prev, pager, next" style="margin-top: 16px; justify-content: flex-end" @current-change="fetchList" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑凭据' : '新增凭据'" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="环境" prop="env_id">
          <el-select v-model="form.env_id" :disabled="isEdit">
            <el-option v-for="e in envList" :key="e.id" :label="e.label" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="服务名" prop="service_name">
          <el-input v-model="form.service_name" />
        </el-form-item>
        <el-form-item label="数据库类型" prop="db_type">
          <el-select v-model="form.db_type">
            <el-option label="MySQL" value="mysql" />
            <el-option label="Redis" value="redis" />
            <el-option label="PostgreSQL" value="postgresql" />
            <el-option label="MongoDB" value="mongodb" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="地址" prop="host">
          <el-input v-model="form.host" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="form.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="数据库名">
          <el-input v-model="form.database_name" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getEnvironments } from '@/api/environment'
import { listCredentials, createCredential, updateCredential, deleteCredential, revealCredential } from '@/api/secret'
import { ElMessage } from 'element-plus'

const envList = ref<any[]>([])
const list = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

const query = reactive({ page: 1, size: 20, env_id: undefined as number | undefined, db_type: undefined as string | undefined, service_name: '' })
const form = reactive({ env_id: undefined as number | undefined, service_name: '', db_type: 'mysql', host: '', port: 3306, database_name: '', username: '', password: '' })
const rules = {
  env_id: [{ required: true, message: '必选', trigger: 'change' }],
  service_name: [{ required: true, message: '必填', trigger: 'blur' }],
  host: [{ required: true, message: '必填', trigger: 'blur' }],
  username: [{ required: true, message: '必填', trigger: 'blur' }],
  password: [{ required: true, message: '必填', trigger: 'blur' }],
}

async function fetchList() {
  loading.value = true
  try {
    const res: any = await listCredentials(query)
    list.value = res.data.items
    total.value = res.data.total
  } catch {} finally { loading.value = false }
}

function openDialog(row?: any) {
  isEdit.value = !!row
  if (row) {
    form.env_id = row.env_id
    form.service_name = row.service_name
    form.db_type = row.db_type
    form.host = row.host
    form.port = row.port
    form.database_name = row.database_name || ''
    form.username = row.username
    form.password = ''
  } else {
    Object.assign(form, { env_id: undefined, service_name: '', db_type: 'mysql', host: '', port: 3306, database_name: '', username: '', password: '' })
  }
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      const id = list.value.find(i => i.service_name === form.service_name)?.id
      if (id) await updateCredential(id, form)
    } else {
      await createCredential(form)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    fetchList()
  } catch {} finally { saving.value = false }
}

async function handleDelete(id: number) {
  try { await deleteCredential(id); ElMessage.success('删除成功'); fetchList() } catch {}
}

async function handleReveal(row: any) {
  try {
    const res: any = await revealCredential(row.id)
    await navigator.clipboard.writeText(res.data.password)
    ElMessage.success(`密码已复制到剪贴板: ${res.data.password}`)
  } catch {}
}

onMounted(async () => {
  const res: any = await getEnvironments({ page: 1, size: 100 })
  envList.value = res.data.items
  fetchList()
})
</script>
