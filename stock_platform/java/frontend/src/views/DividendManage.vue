<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">分红记录</h2>

    <!-- 添加分红 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h3 class="text-lg font-bold mb-4">添加分红</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <select v-model="form.accountId" class="border rounded px-3 py-2">
          <option value="">选择账户</option>
          <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
        </select>
        <input v-model="form.stockCode" type="text" placeholder="股票代码" class="border rounded px-3 py-2" />
        <input v-model="form.stockName" type="text" placeholder="股票名称" class="border rounded px-3 py-2" />
        <input v-model.number="form.dividendAmount" type="number" placeholder="分红金额" class="border rounded px-3 py-2" />
        <input v-model="form.dividendDate" type="date" class="border rounded px-3 py-2" />
        <button @click="addDividend" class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 col-span-5">
          添加
        </button>
      </div>
    </div>

    <!-- 分红列表 -->
    <div class="bg-white rounded-lg shadow">
      <table class="min-w-full">
        <thead>
          <tr class="border-b bg-gray-50">
            <th class="text-center py-3">股票代码</th>
            <th class="text-center py-3">股票名称</th>
            <th class="text-center py-3">分红金额</th>
            <th class="text-center py-3">分红日期</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="div in dividends" :key="div.id" class="border-b hover:bg-gray-50">
            <td class="text-center py-3">{{ div.stock_code }}</td>
            <td class="text-center py-3">{{ div.stock_name }}</td>
            <td class="text-center py-3 text-green-600">{{ div.dividend_amount.toFixed(2) }}</td>
            <td class="text-center py-3">{{ formatDate(div.dividend_date) }}</td>
          </tr>
          <tr v-if="dividends.length === 0">
            <td colspan="4" class="text-center py-8 text-gray-500">暂无分红记录</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { dividendApi, accountApi } from '../api'
import type { Dividend, Account } from '../types'

const emit = defineEmits(['refresh'])

const dividends = ref<Dividend[]>([])
const accounts = ref<Account[]>([])
const form = ref({ accountId: '', stockCode: '', stockName: '', dividendAmount: 0, dividendDate: '' })

const loadData = async () => {
  try {
    accounts.value = await accountApi.list()
    const result = await dividendApi.list({ page: 1, perPage: 100 })
    dividends.value = result.items
  } catch (e) {
    console.error('Failed to load data:', e)
  }
}

const addDividend = async () => {
  if (!form.value.accountId || !form.value.stockCode || !form.value.dividendDate) return
  try {
    await dividendApi.create({
      account_id: Number(form.value.accountId),
      stock_code: form.value.stockCode,
      stock_name: form.value.stockName,
      dividend_amount: form.value.dividendAmount,
      dividend_date: form.value.dividendDate,
    })
    form.value = { accountId: '', stockCode: '', stockName: '', dividendAmount: 0, dividendDate: '' }
    await loadData()
    emit('refresh')
  } catch (e) {
    console.error('Failed to add dividend:', e)
  }
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(loadData)
</script>