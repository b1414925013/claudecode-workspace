<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>用户管理</h2>
      <el-button type="primary" @click="openDialog()">新增用户</el-button>
    </div>
    <el-card v-loading="loading">
      <el-table :data="list" stripe>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="role" label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">{{ row.role === 'admin' ? '管理员' : '开发者' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }"><el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button link type="primary" @click="openResetPwd(row)">重置密码</el-button>
            <el-button link type="primary" @click="openEnvPerm(row)">环境授权</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:page="query.page" :page-size="query.size" :total="total" layout="total, prev, pager, next" style="margin-top: 16px" @current-change="fetchList" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="管理员" value="admin" />
            <el-option label="开发者" value="developer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="pwdVisible" title="重置密码" width="400px">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResetPwd">确认</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="envPermVisible" title="环境授权" width="400px">
      <el-checkbox-group v-model="selectedEnvs">
        <el-checkbox v-for="e in envList" :key="e.id" :label="e.id" style="display: block; margin-bottom: 8px">{{ e.label }}</el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="envPermVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEnvPerm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { authReq } from '@/api/request'
import { getEnvironments } from '@/api/environment'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const query = reactive({ page: 1, size: 20, keyword: '' })
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const form = reactive({ username: '', password: '', nickname: '', email: '', role: 'developer' })
const rules = { username: [{ required: true, message: '必填', trigger: 'blur' }], password: [{ required: true, message: '必填', trigger: 'blur' }] }

const pwdVisible = ref(false)
const pwdFormRef = ref()
const pwdForm = reactive({ user_id: 0, new_password: '' })
const pwdRules = { new_password: [{ required: true, min: 6, message: '至少6位', trigger: 'blur' }] }

const envPermVisible = ref(false)
const envList = ref<any[]>([])
const selectedEnvs = ref<number[]>([])
const currentUserId = ref(0)

async function fetchList() {
  loading.value = true
  try {
    const res: any = await authReq.get('/users', { params: query })
    list.value = res.data.items
    total.value = res.data.total
  } catch {} finally { loading.value = false }
}

function openDialog(row?: any) {
  isEdit.value = !!row
  if (row) {
    form.username = row.username
    form.password = ''
    form.nickname = row.nickname || ''
    form.email = row.email || ''
    form.role = row.role
  } else {
    Object.assign(form, { username: '', password: '', nickname: '', email: '', role: 'developer' })
  }
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      const id = list.value.find(i => i.username === form.username)?.id
      if (id) await authReq.put(`/users/${id}`, { nickname: form.nickname, email: form.email, role: form.role })
    } else {
      await authReq.post('/users', form)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    fetchList()
  } catch {} finally { saving.value = false }
}

async function handleDelete(id: number) {
  try { await authReq.delete(`/users/${id}`); ElMessage.success('已删除'); fetchList() } catch {}
}

function openResetPwd(row: any) {
  pwdForm.user_id = row.id
  pwdForm.new_password = ''
  pwdVisible.value = true
}

async function handleResetPwd() {
  const valid = await pwdFormRef.value?.validate().catch(() => false)
  if (!valid) return
  try {
    await authReq.put(`/users/${pwdForm.user_id}/reset-password`, { new_password: pwdForm.new_password })
    ElMessage.success('密码已重置')
    pwdVisible.value = false
  } catch {}
}

async function openEnvPerm(row: any) {
  currentUserId.value = row.id
  const res: any = await authReq.get(`/users/${row.id}/env-permissions`)
  selectedEnvs.value = res.data.env_ids
  envPermVisible.value = true
}

async function saveEnvPerm() {
  await authReq.put(`/users/${currentUserId.value}/env-permissions`, { env_ids: selectedEnvs.value })
  ElMessage.success('权限已更新')
  envPermVisible.value = false
}

onMounted(async () => {
  fetchList()
  const res: any = await getEnvironments({ page: 1, size: 100 })
  envList.value = res.data.items
})
</script>
