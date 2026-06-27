<template>
  <el-container style="height: 100vh">
    <el-aside width="220px" style="background: #304156">
      <div class="logo">
        <el-icon :size="24" color="#409eff"><Lock /></el-icon>
        <span>KSM 管理后台</span>
      </div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon><span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/environments">
          <el-icon><Setting /></el-icon><span>环境管理</span>
        </el-menu-item>
        <el-menu-item index="/secrets">
          <el-icon><Key /></el-icon><span>Secret 查询</span>
        </el-menu-item>
        <el-menu-item index="/credentials">
          <el-icon><Lock /></el-icon><span>数据库凭据</span>
        </el-menu-item>
        <el-menu-item index="/toolbox">
          <el-icon><Tools /></el-icon><span>开发者工具箱</span>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/users">
          <el-icon><User /></el-icon><span>用户管理</span>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/audit-logs">
          <el-icon><Document /></el-icon><span>审计日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: flex-end; padding: 0 20px">
        <el-dropdown @command="handleCommand">
          <span style="cursor: pointer; display: flex; align-items: center; gap: 6px">
            <el-icon><UserFilled /></el-icon>
            {{ auth.user?.nickname || auth.user?.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">{{ auth.user?.role === 'admin' ? '管理员' : '开发者' }}</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main style="background: #f0f2f5; padding: 20px">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getProfile } from '@/api/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const isAdmin = computed(() => auth.user?.role === 'admin')

onMounted(async () => {
  if (!auth.user) {
    try {
      const res: any = await getProfile()
      auth.setUser(res.data)
    } catch {
      auth.logout()
      router.push('/login')
    }
  }
})

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
</style>
