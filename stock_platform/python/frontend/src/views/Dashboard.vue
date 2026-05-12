<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">仪表盘</h2>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总账号数</div>
        <div class="text-3xl font-bold text-blue-600">{{ summary.total_accounts }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总持仓数</div>
        <div class="text-3xl font-bold text-green-600">{{ summary.total_positions }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总交易数</div>
        <div class="text-3xl font-bold text-purple-600">{{ summary.total_trades }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-gray-500 text-sm">总收益</div>
        <div :class="['text-3xl font-bold', totalProfit >= 0 ? 'text-red-600' : 'text-green-600']">
          {{ totalProfit.toFixed(2) }}
        </div>
      </div>
    </div>

    <!-- 最近交易 -->
    <div class="bg-white rounded-lg shadow p-6 mb-8">
      <h3 class="text-lg font-bold mb-4">最近交易</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead>
            <tr class="border-b">
              <th class="text-center py-2">股票代码</th>
              <th class="text-center py-2">股票名称</th>
              <th class="text-center py-2">类型</th>
              <th class="text-center py-2">数量</th>
              <th class="text-center py-2">价格</th>
              <th class="text-center py-2">日期</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trade in recentTrades" :key="trade.id" class="border-b hover:bg-gray-50">
              <td class="text-center py-2">{{ trade.stock_code }}</td>
              <td class="text-center py-2">{{ trade.stock_name }}</td>
              <td class="text-center py-2">
                <span :class="trade.trade_type === 'buy' ? 'text-green-600' : 'text-red-600'">
                  {{ trade.trade_type === 'buy' ? '买入' : '卖出' }}
                </span>
              </td>
              <td class="text-center py-2">{{ trade.quantity }}</td>
              <td class="text-center py-2">{{ trade.price.toFixed(2) }}</td>
              <td class="text-center py-2">{{ formatDate(trade.trade_date) }}</td>
            </tr>
            <tr v-if="recentTrades.length === 0">
              <td colspan="6" class="text-center py-4 text-gray-500">暂无交易记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 持仓列表 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-bold mb-4">当前持仓</h3>
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead>
            <tr class="border-b">
              <th class="text-center py-2">股票代码</th>
              <th class="text-center py-2">股票名称</th>
              <th class="text-center py-2">数量</th>
              <th class="text-center py-2">持仓成本</th>
              <th class="text-center py-2">现价</th>
              <th class="text-center py-2">总市值</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pos in positions" :key="pos.id" class="border-b hover:bg-gray-50">
              <td class="text-center py-2">{{ pos.stock_code }}</td>
              <td class="text-center py-2">{{ pos.stock_name }}</td>
              <td class="text-center py-2">{{ pos.quantity }}</td>
              <td class="text-center py-2">{{ pos.avg_cost.toFixed(2) }}</td>
              <td class="text-center py-2">{{ pos.current_price ? pos.current_price.toFixed(2) : '-' }}</td>
              <td class="text-center py-2">{{ pos.market_value ? pos.market_value.toFixed(2) : '-' }}</td>
            </tr>
            <tr v-if="positions.length === 0">
              <td colspan="6" class="text-center py-4 text-gray-500">暂无持仓</td>
            </tr>
            <tr class="bg-gray-100 font-semibold">
              <td colspan="5" class="text-center py-2">合计</td>
              <td class="text-center py-2">{{ totalMarketValue.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { statisticsApi, tradeApi, positionApi } from '../api'
import type { Summary, Trade, Position } from '../types'

const summary = ref<Summary>({
  total_accounts: 0,
  total_positions: 0,
  total_trades: 0,
  total_cost: 0,
  total_profit: 0,
})

const recentTrades = ref<Trade[]>([])
const positions = ref<Position[]>([])

const totalMarketValue = computed(() => {
  return positions.value.reduce((sum, pos) => sum + (pos.market_value || 0), 0)
})

const totalCost = computed(() => {
  return positions.value.reduce((sum, pos) => sum + (pos.quantity * pos.avg_cost), 0)
})

const totalProfit = computed(() => {
  return totalMarketValue.value - totalCost.value
})

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(async () => {
  try {
    summary.value = await statisticsApi.summary()
    recentTrades.value = await tradeApi.list()
    recentTrades.value = recentTrades.value.slice(0, 5)
    positions.value = await positionApi.list()
  } catch (e) {
    console.error('Failed to load dashboard data:', e)
  }
})
</script>