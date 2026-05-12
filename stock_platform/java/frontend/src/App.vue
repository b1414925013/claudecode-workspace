<template>
  <div class="min-h-screen bg-gray-100">
    <!-- 导航栏 -->
    <nav class="bg-blue-600 text-white p-4 shadow-lg">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-xl font-bold">股票收益记录平台</h1>
        <div class="space-x-4">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="currentTab = tab.key"
            :class="['px-4 py-2 rounded', currentTab === tab.key ? 'bg-blue-800' : 'hover:bg-blue-700']"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <div class="container mx-auto p-6">
      <!-- 仪表盘 -->
      <Dashboard v-if="currentTab === 'dashboard'" />

      <!-- 账号管理 -->
      <AccountManage v-if="currentTab === 'accounts'" @refresh="refreshData" />

      <!-- 持仓管理 -->
      <PositionManage v-if="currentTab === 'positions'" @refresh="refreshData" />

      <!-- 交易记录 -->
      <TradeManage v-if="currentTab === 'trades'" @refresh="refreshData" />

      <!-- 分红记录 -->
      <DividendManage v-if="currentTab === 'dividends'" @refresh="refreshData" />

      <!-- 统计分析 -->
      <StatisticsView v-if="currentTab === 'statistics'" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Dashboard from './views/Dashboard.vue'
import AccountManage from './views/AccountManage.vue'
import PositionManage from './views/PositionManage.vue'
import TradeManage from './views/TradeManage.vue'
import DividendManage from './views/DividendManage.vue'
import StatisticsView from './views/StatisticsView.vue'

const tabs = [
  { key: 'dashboard', label: '仪表盘' },
  { key: 'accounts', label: '账号管理' },
  { key: 'positions', label: '持仓管理' },
  { key: 'trades', label: '交易记录' },
  { key: 'dividends', label: '分红记录' },
  { key: 'statistics', label: '统计分析' },
]

const currentTab = ref('dashboard')

const refreshData = () => {
  // 触发刷新
}
</script>