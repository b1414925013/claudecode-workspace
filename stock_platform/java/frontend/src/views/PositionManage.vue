<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">持仓管理</h2>

    <!-- 添加/编辑持仓 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h3 class="text-lg font-bold mb-4">{{ isEditing ? '编辑持仓' : '添加持仓' }}</h3>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <select v-model="form.accountId" class="border rounded px-3 py-2">
          <option value="">选择账户</option>
          <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
        </select>
        <input v-model="form.stockCode" type="text" placeholder="股票代码" class="border rounded px-3 py-2" />
        <input v-model="form.stockName" type="text" placeholder="股票名称" class="border rounded px-3 py-2" />
        <input v-model.number="form.quantity" type="number" placeholder="数量" class="border rounded px-3 py-2" />
        <input v-model.number="form.avgCost" type="number" placeholder="平均成本" class="border rounded px-3 py-2" />
        <button @click="submitForm" class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
          {{ isEditing ? '更新' : '添加' }}
        </button>
      </div>
      <button v-if="isEditing" @click="cancelEdit" class="mt-4 text-gray-600 hover:text-gray-800">取消编辑</button>
    </div>

    <!-- 持仓列表 -->
    <div class="bg-white rounded-lg shadow">
      <table class="min-w-full">
        <thead>
          <tr class="border-b bg-gray-50">
            <th class="text-center py-3">股票代码</th>
            <th class="text-center py-3">股票名称</th>
            <th class="text-center py-3">数量</th>
            <th class="text-center py-3">成本</th>
            <th class="text-center py-3">现价</th>
            <th class="text-center py-3">市值</th>
            <th class="text-center py-3">盈亏</th>
            <th class="text-center py-3">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pos in positions" :key="pos.id" class="border-b hover:bg-gray-50">
            <td class="text-center py-3">{{ pos.stock_code }}</td>
            <td class="text-center py-3">{{ pos.stock_name }}</td>
            <td class="text-center py-3">{{ pos.quantity }}</td>
            <td class="text-center py-3">{{ pos.avg_cost.toFixed(2) }}</td>
            <td class="text-center py-3">{{ pos.current_price ? pos.current_price.toFixed(2) : '-' }}</td>
            <td class="text-center py-3">{{ pos.market_value ? pos.market_value.toFixed(2) : '-' }}</td>
            <td class="text-center py-3" :class="getProfitClass(pos)">
              {{ getProfitText(pos) }}
            </td>
            <td class="text-center py-3">
              <button @click="editPosition(pos)" class="text-blue-600 hover:text-blue-800 mr-2">编辑</button>
              <button @click="deletePosition(pos.id)" class="text-red-600 hover:text-red-800">删除</button>
            </td>
          </tr>
          <tr v-if="positions.length === 0">
            <td colspan="8" class="text-center py-8 text-gray-500">暂无持仓</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { positionApi, accountApi } from '../api'
import type { Position, Account } from '../types'

const emit = defineEmits(['refresh'])

const positions = ref<Position[]>([])
const accounts = ref<Account[]>([])
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const form = ref({ accountId: '', stockCode: '', stockName: '', quantity: 0, avgCost: 0 })

const loadData = async () => {
  try {
    accounts.value = await accountApi.list()
    const result = await positionApi.list({ page: 1, perPage: 100 })
    positions.value = result.items
  } catch (e) {
    console.error('Failed to load data:', e)
  }
}

const submitForm = async () => {
  if (!form.value.accountId || !form.value.stockCode || !form.value.stockName) return
  try {
    const data = {
      accountId: Number(form.value.accountId),
      stockCode: form.value.stockCode,
      stockName: form.value.stockName,
      quantity: form.value.quantity,
      avgCost: form.value.avgCost,
    }
    if (isEditing.value && editingId.value) {
      await positionApi.update(editingId.value, data)
    } else {
      await positionApi.create(data)
    }
    resetForm()
    await loadData()
    emit('refresh')
  } catch (e) {
    console.error('Failed to submit form:', e)
  }
}

const editPosition = (pos: Position) => {
  isEditing.value = true
  editingId.value = pos.id
  form.value = {
    accountId: String(pos.account_id),
    stockCode: pos.stock_code,
    stockName: pos.stock_name,
    quantity: pos.quantity,
    avgCost: pos.avg_cost,
  }
}

const deletePosition = async (id: number) => {
  try {
    await positionApi.delete(id)
    await loadData()
    emit('refresh')
  } catch (e) {
    console.error('Failed to delete position:', e)
  }
}

const cancelEdit = () => {
  resetForm()
}

const resetForm = () => {
  isEditing.value = false
  editingId.value = null
  form.value = { accountId: '', stockCode: '', stockName: '', quantity: 0, avgCost: 0 }
}

const getProfitClass = (pos: Position) => {
  if (!pos.market_value || !pos.current_price) return ''
  const cost = pos.quantity * pos.avg_cost
  const profit = pos.market_value - cost
  return profit >= 0 ? 'text-red-600' : 'text-green-600'
}

const getProfitText = (pos: Position) => {
  if (!pos.market_value || !pos.current_price) return '-'
  const cost = pos.quantity * pos.avg_cost
  const profit = pos.market_value - cost
  return profit.toFixed(2)
}

onMounted(loadData)
</script>