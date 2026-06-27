<template>
  <div>
    <h2 style="margin-bottom: 20px">仪表盘</h2>
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in cards" :key="card.label">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon :size="32" :color="card.color"><component :is="card.icon" /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-card style="margin-top: 20px">
      <template #header>最近操作日志</template>
      <el-table :data="recentLogs" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="action" label="操作" width="160" />
        <el-table-column prop="resource_type" label="资源类型" width="120" />
        <el-table-column prop="resource_name" label="资源名称" min-width="200" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { DataAnalysis, Setting, Key, User } from '@element-plus/icons-vue'
import { getDashboardStats } from '@/api/toolbox'

const loading = ref(false)
const cards = ref([
  { icon: Setting, label: '集群环境', value: 0, color: '#409eff' },
  { icon: Key, label: 'Secret 缓存', value: 0, color: '#67c23a' },
  { icon: User, label: '活跃用户', value: 0, color: '#e6a23c' },
  { icon: DataAnalysis, label: '数据库凭据', value: 0, color: '#f56c6c' },
])
const recentLogs = ref<any[]>([])

onMounted(async () => {
  try {
    const res: any = await getDashboardStats()
    cards.value[0].value = res.data.env_count
    cards.value[1].value = res.data.secret_count
    cards.value[2].value = res.data.user_count
    cards.value[3].value = res.data.credential_count
    recentLogs.value = res.data.recent_logs || []
  } catch {}
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
}
.stat-label {
  font-size: 14px;
  color: #999;
}
</style>
