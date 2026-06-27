<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2>环境管理</h2>
      <el-button type="primary" @click="openDialog()">新增环境</el-button>
    </div>
    <el-card>
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="label" label="标签" width="160" />
        <el-table-column prop="cluster_api" label="集群地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="k8s_sdk_mode" label="操作模式" width="100" />
        <el-table-column prop="sort_order" label="排序" width="60" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="checkEnvHealth(row)">连通性</el-button>
            <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:page="query.page"
        :page-size="query.size"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end"
        @current-change="fetchList"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑环境' : '新增环境'" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="标签" prop="label">
          <el-input v-model="form.label" />
        </el-form-item>
        <el-form-item label="集群地址" prop="cluster_api">
          <el-input v-model="form.cluster_api" />
        </el-form-item>
        <el-form-item label="操作模式" prop="k8s_sdk_mode">
          <el-select v-model="form.k8s_sdk_mode">
            <el-option label="自动(优先SDK)" value="auto" />
            <el-option label="仅SDK" value="sdk" />
            <el-option label="仅kubectl" value="kubectl" />
          </el-select>
        </el-form-item>
        <el-form-item label="Kubeconfig" prop="kubeconfig">
          <el-input v-model="form.kubeconfig" type="textarea" :rows="6" />
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
import { getEnvironments, createEnvironment, updateEnvironment, deleteEnvironment, checkHealth } from '@/api/environment'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const query = reactive({ page: 1, size: 20 })
const formRef = ref()
const form = reactive({ name: '', label: '', cluster_api: '', kubeconfig: '', k8s_sdk_mode: 'auto', kubeconfig_type: 'content', namespace_config: {}, sort_order: 0 })
const rules = {
  name: [{ required: true, message: '必填', trigger: 'blur' }],
  label: [{ required: true, message: '必填', trigger: 'blur' }],
  cluster_api: [{ required: true, message: '必填', trigger: 'blur' }],
  kubeconfig: [{ required: true, message: '必填', trigger: 'blur' }],
}

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getEnvironments(query)
    list.value = res.data.items
    total.value = res.data.total
  } catch {} finally { loading.value = false }
}

function openDialog(row?: any) {
  isEdit.value = !!row
  if (row) {
    Object.assign(form, { name: row.name, label: row.label, cluster_api: row.cluster_api, kubeconfig: '', k8s_sdk_mode: row.k8s_sdk_mode, kubeconfig_type: 'content', namespace_config: {}, sort_order: row.sort_order })
  } else {
    Object.assign(form, { name: '', label: '', cluster_api: '', kubeconfig: '', k8s_sdk_mode: 'auto', kubeconfig_type: 'content', namespace_config: {}, sort_order: 0 })
  }
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) {
      const id = list.value.find(i => i.name === form.name)?.id
      if (id) await updateEnvironment(id, form)
    } else {
      await createEnvironment(form)
    }
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    dialogVisible.value = false
    fetchList()
  } catch {} finally { saving.value = false }
}

async function handleDelete(id: number) {
  try {
    await deleteEnvironment(id)
    ElMessage.success('删除成功')
    fetchList()
  } catch {}
}

async function checkEnvHealth(row: any) {
  try {
    const res: any = await checkHealth(row.id)
    if (res.data.status === 'ok') {
      ElMessage.success(`集群正常 | 版本: ${res.data.version} | 节点: ${res.data.node_count}`)
    } else {
      ElMessage.warning(`集群异常: ${res.data.message}`)
    }
  } catch { ElMessage.error('连接失败') }
}

onMounted(fetchList)
</script>
