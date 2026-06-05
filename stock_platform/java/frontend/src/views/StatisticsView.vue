<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">统计分析</h2>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总收益</div>
        <div :class="['text-3xl font-bold', stats.total_profit >= 0 ? 'text-red-600' : 'text-green-600']">
          {{ stats.total_profit.toFixed(2) }}
        </div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总成本</div>
        <div class="text-3xl font-bold text-blue-600">{{ stats.total_cost.toFixed(2) }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总市值</div>
        <div class="text-3xl font-bold text-purple-600">{{ stats.total_market_value.toFixed(2) }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">收益率</div>
        <div :class="['text-3xl font-bold', stats.return_rate >= 0 ? 'text-red-600' : 'text-green-600']">
          {{ (stats.return_rate * 100).toFixed(2) }}%
        </div>
      </div>
    </div>

    <!-- 交易统计 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总交易数</div>
        <div class="text-3xl font-bold text-blue-600">{{ stats.total_trades }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">盈利交易</div>
        <div class="text-3xl font-bold text-green-600">{{ stats.winning_trades }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">亏损交易</div>
        <div class="text-3xl font-bold text-red-600">{{ stats.losing_trades }}</div>
      </div>
    </div>

    <!-- 胜率 -->
    <div class="bg-white rounded-lg shadow p-6 mb-8">
      <h3 class="text-lg font-bold mb-4">胜率</h3>
      <div class="flex items-center">
        <div class="w-full bg-gray-200 rounded-full h-4">
          <div
            class="bg-green-600 h-4 rounded-full"
            :style="{ width: (stats.win_rate * 100) + '%' }"
          ></div>
        </div>
        <span class="ml-4 text-xl font-bold text-green-600">{{ (stats.win_rate * 100).toFixed(1) }}%</span>
      </div>
    </div>

    <!-- 同步股票价格按钮 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-bold mb-4">股票价格同步</h3>
      <button
        @click="syncPrices"
        :disabled="syncing"
        class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
      >
        {{ syncing ? '同步中...' : '同步所有持仓价格' }}
      </button>
      <p v-if="syncMessage" class="mt-4 text-green-600">{{ syncMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { statisticsApi, stockPriceApi } from '../api'
import type { Statistics } from '../types'

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

const syncing = ref(false)
const syncMessage = ref('')

const loadStats = async () => {
  try {
    stats.value = await statisticsApi.get()
  } catch (e) {
    console.error('Failed to load statistics:', e)
  }
}

const syncPrices = async () => {
  syncing.value = true
  syncMessage.value = ''
  try {
    const result = await stockPriceApi.syncAll()
    syncMessage.value = result.message || '同步成功'
    await loadStats()
  } catch (e) {
    syncMessage.value = '同步失败'
    console.error('Failed to sync prices:', e)
  } finally {
    syncing.value = false
  }
}

onMounted(loadStats)
</script>