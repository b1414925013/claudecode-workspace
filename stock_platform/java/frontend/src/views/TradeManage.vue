<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">交易记录</h2>

    <!-- 添加交易 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h3 class="text-lg font-bold mb-4">添加交易</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <select v-model="form.accountId" class="border rounded px-3 py-2">
          <option value="">选择账户</option>
          <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
        </select>
        <input v-model="form.stockCode" type="text" placeholder="股票代码" class="border rounded px-3 py-2" />
        <input v-model="form.stockName" type="text" placeholder="股票名称" class="border rounded px-3 py-2" />
        <select v-model="form.tradeType" class="border rounded px-3 py-2">
          <option value="buy">买入</option>
          <option value="sell">卖出</option>
        </select>
        <input v-model.number="form.quantity" type="number" placeholder="数量" class="border rounded px-3 py-2" />
        <input v-model.number="form.price" type="number" placeholder="价格" class="border rounded px-3 py-2" />
        <input v-model.number="form.commission" type="number" placeholder="手续费" class="border rounded px-3 py-2" />
        <input v-model="form.tradeDate" type="date" class="border rounded px-3 py-2" />
        <button @click="addTrade" class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 col-span-4">
          添加
        </button>
      </div>
    </div>

    <!-- 交易列表 -->
    <div class="bg-white rounded-lg shadow">
      <table class="min-w-full">
        <thead>
          <tr class="border-b bg-gray-50">
            <th class="text-center py-3">股票代码</th>
            <th class="text-center py-3">股票名称</th>
            <th class="text-center py-3">类型</th>
            <th class="text-center py-3">数量</th>
            <th class="text-center py-3">价格</th>
            <th class="text-center py-3">手续费</th>
            <th class="text-center py-3">日期</th>
            <th class="text-center py-3">盈亏</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trade in trades" :key="trade.id" class="border-b hover:bg-gray-50">
            <td class="text-center py-3">{{ trade.stock_code }}</td>
            <td class="text-center py-3">{{ trade.stock_name }}</td>
            <td class="text-center py-3">
              <span :class="trade.trade_type === 'buy' ? 'text-green-600' : 'text-red-600'">
                {{ trade.trade_type === 'buy' ? '买入' : '卖出' }}
              </span>
            </td>
            <td class="text-center py-3">{{ trade.quantity }}</td>
            <td class="text-center py-3">{{ trade.price.toFixed(2) }}</td>
            <td class="text-center py-3">{{ trade.commission.toFixed(2) }}</td>
            <td class="text-center py-3">{{ formatDate(trade.trade_date) }}</td>
            <td class="text-center py-3" :class="trade.profit && trade.profit >= 0 ? 'text-red-600' : 'text-green-600'">
              {{ trade.profit ? trade.profit.toFixed(2) : '-' }}
            </td>
          </tr>
          <tr v-if="trades.length === 0">
            <td colspan="8" class="text-center py-8 text-gray-500">暂无交易记录</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tradeApi, accountApi } from '../api'
import type { Trade, Account } from '../types'

const emit = defineEmits(['refresh'])

const trades = ref<Trade[]>([])
const accounts = ref<Account[]>([])
const form = ref({ accountId: '', stockCode: '', stockName: '', tradeType: 'buy', quantity: 0, price: 0, commission: 0, tradeDate: '' })

const loadData = async () => {
  try {
    accounts.value = await accountApi.list()
    const result = await tradeApi.list({ page: 1, perPage: 100 })
    trades.value = result.items
  } catch (e) {
    console.error('Failed to load data:', e)
  }
}

const addTrade = async () => {
  if (!form.value.accountId || !form.value.stockCode || !form.value.tradeDate) return
  try {
    await tradeApi.create({
      account_id: Number(form.value.accountId),
      stock_code: form.value.stockCode,
      stock_name: form.value.stockName,
      trade_type: form.value.tradeType,
      quantity: form.value.quantity,
      price: form.value.price,
      commission: form.value.commission,
      trade_date: form.value.tradeDate,
    })
    form.value = { accountId: '', stockCode: '', stockName: '', tradeType: 'buy', quantity: 0, price: 0, commission: 0, tradeDate: '' }
    await loadData()
    emit('refresh')
  } catch (e) {
    console.error('Failed to add trade:', e)
  }
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(loadData)
</script>