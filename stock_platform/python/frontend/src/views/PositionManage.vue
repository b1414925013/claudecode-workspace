<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">持仓管理</h2>
      <div class="flex items-center space-x-4">
        <select v-model="filterAccountId" @change="loadData" class="border rounded px-3 py-2">
          <option value="">全部账号</option>
          <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
        </select>
        <button @click="showAddModal = true" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          添加持仓
        </button>
      </div>
    </div>

    <!-- 持仓列表 -->
    <div class="bg-white rounded-lg shadow p-6">
      <table style="width: 100%; table-layout: fixed;">
        <thead>
          <tr class="border-b">
            <th style="width: 96px;" class="text-center py-2">股票代码</th>
            <th style="width: 112px;" class="text-center py-2">股票名称</th>
            <th style="width: 80px;" class="text-center py-2">数量</th>
            <th style="width: 100px;" class="text-center py-2">持仓成本</th>
            <th style="width: 80px;" class="text-center py-2">现价</th>
            <th style="width: 80px;" class="text-center py-2">当天涨跌</th>
            <th style="width: 80px;" class="text-center py-2">当天涨幅</th>
            <th style="width: 100px;" class="text-center py-2">总市值</th>
            <th style="width: 100px;" class="text-center py-2">账号</th>
            <th style="width: 120px;" class="text-center py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pos in positions" :key="pos.id" class="border-b hover:bg-gray-50">
            <td style="width: 96px;" class="text-center py-2">{{ pos.stock_code }}</td>
            <td style="width: 112px;" class="text-center py-2">{{ pos.stock_name }}</td>
            <td style="width: 80px;" class="text-center py-2">{{ pos.quantity }}</td>
            <td style="width: 100px;" class="text-center py-2">{{ pos.avg_cost.toFixed(3) }}</td>
            <td style="width: 80px;" class="text-center py-2">{{ pos.current_price ? pos.current_price.toFixed(2) : '-' }}</td>
            <td style="width: 80px;" class="text-center py-2" :class="pos.change_value > 0 ? 'text-red-600' : pos.change_value < 0 ? 'text-green-600' : ''">
              {{ pos.change_value != null ? (pos.change_value > 0 ? '+' : '') + pos.change_value.toFixed(2) : '-' }}
            </td>
            <td style="width: 80px;" class="text-center py-2" :class="pos.change_percent > 0 ? 'text-red-600' : pos.change_percent < 0 ? 'text-green-600' : ''">
              {{ pos.change_percent != null ? (pos.change_percent > 0 ? '+' : '') + pos.change_percent.toFixed(2) + '%' : '-' }}
            </td>
            <td style="width: 100px;" class="text-center py-2">{{ pos.market_value ? pos.market_value.toFixed(2) : '-' }}</td>
            <td style="width: 100px;" class="text-center py-2">{{ getAccountName(pos.account_id) }}</td>
            <td class="text-center py-2 space-x-2">
              <button @click="openAdjustModal(pos)" class="text-blue-600 hover:text-blue-800">调整</button>
              <button @click="deletePosition(pos.id)" class="text-red-600 hover:text-red-800">删除</button>
            </td>
          </tr>
          <tr v-if="positions.length === 0">
            <td colspan="9" class="text-center py-4 text-gray-500">暂无持仓</td>
          </tr>
          <tr class="bg-gray-100 font-semibold">
            <td colspan="7" class="text-center py-2">合计</td>
            <td class="text-center py-2">{{ totalMarketValue.toFixed(2) }}</td>
            <td class="text-center py-2"></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 添加持仓弹窗 -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-bold mb-4">添加持仓</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">账号</label>
            <select v-model="newPosition.account_id" class="w-full border rounded px-3 py-2">
              <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">股票代码</label>
            <input v-model="newPosition.stock_code" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">股票名称</label>
            <input v-model="newPosition.stock_name" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">数量</label>
            <input v-model.number="newPosition.quantity" type="number" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">平均成本</label>
            <input v-model.number="newPosition.avg_cost" type="number" step="0.01" class="w-full border rounded px-3 py-2" />
          </div>
        </div>
        <div class="flex justify-end space-x-2 mt-6">
          <button @click="showAddModal = false" class="px-4 py-2 border rounded hover:bg-gray-100">取消</button>
          <button @click="addPosition" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">添加</button>
        </div>
      </div>
    </div>

    <!-- 调整持仓弹窗 -->
    <div v-if="showAdjustModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-bold mb-4">调整持仓（加仓/减仓）</h3>
        <div class="space-y-4">
          <div class="text-sm text-gray-600">股票：{{ adjustPosition.stock_name }} ({{ adjustPosition.stock_code }})</div>
          <div class="text-sm text-gray-600">当前数量：{{ adjustPosition.quantity }}，成本：{{ adjustPosition.avg_cost.toFixed(3) }}</div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">调整数量（正数加仓，负数减仓）</label>
            <input v-model.number="adjustData.quantity" type="number" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">新价格</label>
            <input v-model.number="adjustData.avg_cost" type="number" step="0.01" class="w-full border rounded px-3 py-2" />
          </div>
        </div>
        <div class="flex justify-end space-x-2 mt-6">
          <button @click="showAdjustModal = false" class="px-4 py-2 border rounded hover:bg-gray-100">取消</button>
          <button @click="adjustPositionSubmit" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { positionApi, accountApi } from '../api'
import type { Position, Account } from '../types'

const emit = defineEmits(['refresh'])

const positions = ref<Position[]>([])
const accounts = ref<Account[]>([])
const showAddModal = ref(false)
const showAdjustModal = ref(false)
const filterAccountId = ref<number | ''>('')

const newPosition = ref({
  account_id: 0,
  stock_code: '',
  stock_name: '',
  quantity: 0,
  avg_cost: 0,
})

const adjustPosition = ref<Position>({
  id: 0,
  account_id: 0,
  stock_code: '',
  stock_name: '',
  quantity: 0,
  avg_cost: 0,
  created_at: '',
  updated_at: '',
})

const adjustData = ref({
  quantity: 0,
  avg_cost: 0,
})

const getAccountName = (id: number) => {
  const acc = accounts.value.find(a => a.id === id)
  return acc ? acc.name : '-'
}

const totalMarketValue = computed(() => {
  return positions.value.reduce((sum, pos) => sum + (pos.market_value || 0), 0)
})

const loadData = async () => {
  try {
    positions.value = await positionApi.list(filterAccountId.value || undefined)
    accounts.value = await accountApi.list()
  } catch (e) {
    console.error('Failed to load data:', e)
  }
}

const addPosition = async () => {
  try {
    await positionApi.create(newPosition.value)
    showAddModal.value = false
    newPosition.value = { account_id: 0, stock_code: '', stock_name: '', quantity: 0, avg_cost: 0 }
    await loadData()
    emit('refresh')
  } catch (e) {
    console.error('Failed to add position:', e)
  }
}

const openAdjustModal = (pos: Position) => {
  adjustPosition.value = pos
  adjustData.value = { quantity: 0, avg_cost: pos.avg_cost }
  showAdjustModal.value = true
}

const adjustPositionSubmit = async () => {
  try {
    await positionApi.update(adjustPosition.value.id, {
      account_id: adjustPosition.value.account_id,
      stock_code: adjustPosition.value.stock_code,
      stock_name: adjustPosition.value.stock_name,
      quantity: adjustData.value.quantity,
      avg_cost: adjustData.value.avg_cost,
    })
    showAdjustModal.value = false
    await loadData()
    emit('refresh')
  } catch (e) {
    console.error('Failed to adjust position:', e)
  }
}

const deletePosition = async (id: number) => {
  if (confirm('确定要删除这条持仓吗？')) {
    try {
      await positionApi.delete(id)
      await loadData()
      emit('refresh')
    } catch (e) {
      console.error('Failed to delete position:', e)
    }
  }
}

onMounted(loadData)
</script>