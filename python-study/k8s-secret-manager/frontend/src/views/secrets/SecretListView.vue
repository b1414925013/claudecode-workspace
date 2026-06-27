<template>
  <div>
    <h2 style="margin-bottom: 20px">Secret 查询</h2>
    <el-card style="margin-bottom: 20px">
      <el-form :inline="true" :model="query">
        <el-form-item label="集群环境">
          <el-select v-model="query.env_id" placeholder="选择环境" style="width: 200px">
            <el-option v-for="e in envList" :key="e.id" :label="e.label" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="命名空间">
          <el-select v-model="query.namespace" placeholder="选择命名空间" style="width: 200px" :disabled="!query.env_id">
            <el-option v-for="ns in namespaces" :key="ns.name" :label="ns.name" :value="ns.name" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :disabled="!query.env_id || !query.namespace" @click="fetchSecrets">查询</el-button>
          <el-button :disabled="!query.env_id || !query.namespace" @click="handleSync">同步缓存</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-card v-loading="loading">
      <el-table :data="secrets" stripe @row-click="showDetail" style="cursor: pointer">
        <el-table-column prop="name" label="Secret 名称" min-width="250" />
        <el-table-column prop="type" label="类型" width="140" />
        <el-table-column prop="keys" label="包含 Keys" min-width="200">
          <template #default="{ row }">{{ row.keys?.join(', ') }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailVisible" :title="`Secret: ${currentSecret}`" width="600px">
      <el-form label-width="80px">
        <el-form-item label="选择 Key">
          <el-select v-model="selectedKey" @change="fetchValue">
            <el-option v-for="k in currentKeys" :key="k" :label="k" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="原始值">
          <el-input v-model="secretValue" type="textarea" :rows="8" readonly />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button v-if="secretValue" @click="copyValue">复制值</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getEnvironments, getNamespaces } from '@/api/environment'
import { listSecrets, getSecretDetail, syncSecrets } from '@/api/secret'
import { ElMessage } from 'element-plus'

const envList = ref<any[]>([])
const namespaces = ref<any[]>([])
const secrets = ref<any[]>([])
const loading = ref(false)
const query = ref({ env_id: undefined as number | undefined, namespace: '' })
const detailVisible = ref(false)
const currentSecret = ref('')
const currentKeys = ref<string[]>([])
const selectedKey = ref('')
const secretValue = ref('')

watch(() => query.value.env_id, async (envId) => {
  if (!envId) return
  try {
    const [envRes, nsRes]: any = await Promise.all([getEnvironments({ page: 1, size: 100 }), getNamespaces(envId)])
    namespaces.value = nsRes.data.namespaces
  } catch {}
})

async function fetchSecrets() {
  loading.value = true
  try {
    const res: any = await listSecrets({ env_id: query.value.env_id!, namespace: query.value.namespace })
    secrets.value = res.data.secrets
  } catch {} finally { loading.value = false }
}

async function handleSync() {
  try {
    await syncSecrets({ env_id: query.value.env_id, namespace: query.value.namespace })
    ElMessage.success('同步完成')
    fetchSecrets()
  } catch {}
}

function showDetail(row: any) {
  currentSecret.value = row.name
  currentKeys.value = row.keys || []
  selectedKey.value = ''
  secretValue.value = ''
  detailVisible.value = true
}

async function fetchValue(key: string) {
  if (!key) return
  try {
    const res: any = await getSecretDetail({ env_id: query.value.env_id!, namespace: query.value.namespace, secret_name: currentSecret.value, key })
    secretValue.value = res.data.value
  } catch {}
}

function copyValue() {
  navigator.clipboard.writeText(secretValue.value)
  ElMessage.success('已复制')
}

onMounted(async () => {
  const res: any = await getEnvironments({ page: 1, size: 100 })
  envList.value = res.data.items
})
</script>
