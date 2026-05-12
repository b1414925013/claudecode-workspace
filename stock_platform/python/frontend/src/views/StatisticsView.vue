<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">统计分析</h2>

    <!-- 筛选条件 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <div class="flex flex-wrap gap-4 items-center">
        <div>
          <label class="block text-sm text-gray-600 mb-1">账号</label>
          <select v-model="filter.account_id" @change="loadStatistics" class="border rounded px-3 py-2">
            <option :value="undefined">全部</option>
            <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">开始日期</label>
          <input v-model="filter.start_date" type="date" @change="loadStatistics" class="border rounded px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">结束日期</label>
          <input v-model="filter.end_date" type="date" @change="loadStatistics" class="border rounded px-3 py-2" />
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总市值</div>
        <div class="text-3xl font-bold text-blue-600">{{ stats.total_market_value.toFixed(2) }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总成本</div>
        <div class="text-3xl font-bold text-gray-600">{{ stats.total_cost.toFixed(2) }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总收益</div>
        <div :class="['text-3xl font-bold', stats.total_profit >= 0 ? 'text-red-600' : 'text-green-600']">
          {{ stats.total_profit.toFixed(2) }}
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">收益率</div>
        <div :class="['text-3xl font-bold', stats.return_rate >= 0 ? 'text-red-600' : 'text-green-600']">
          {{ (stats.return_rate * 100).toFixed(2) }}%
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">胜率</div>
        <div class="text-3xl font-bold text-purple-600">{{ (stats.win_rate * 100).toFixed(2) }}%</div>
      </div>
    </div>

    <!-- 详细统计 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总交易数</div>
        <div class="text-2xl font-bold">{{ stats.total_trades }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">盈利交易</div>
        <div class="text-2xl font-bold text-green-600">{{ stats.winning_trades }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">亏损交易</div>
        <div class="text-2xl font-bold text-red-600">{{ stats.losing_trades }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { statisticsApi, accountApi } from '../api'
import type { Statistics, Account } from '../types'

const stats = ref<Statistics>({
  total_profit: 0,
  total_cost: 0,
  total_market_value: 0,
  return_rate: 0,
  win_rate: 0,
  total_trades: 0,
  winning_trades: 0,
  losing_trades: 0,
  avg_holding_days: 0,
})

const accounts = ref<Account[]>([])

const filter = ref({
  account_id: undefined as number | undefined,
  start_date: '',
  end_date: '',
})

const loadStatistics = async () => {
  try {
    stats.value = await statisticsApi.get({
      account_id: filter.value.account_id,
      start_date: filter.value.start_date || undefined,
      end_date: filter.value.end_date || undefined,
    })
  } catch (e) {
    console.error('Failed to load statistics:', e)
  }
}

onMounted(async () => {
  try {
    accounts.value = await accountApi.list()
    await loadStatistics()
  } catch (e) {
    console.error('Failed to load data:', e)
  }
})
</script>