<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">分红记录</h2>
      <button @click="showAddModal = true" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        添加分红
      </button>
    </div>

    <!-- 分红列表 -->
    <div class="bg-white rounded-lg shadow p-6">
      <table class="min-w-full">
        <thead>
          <tr class="border-b">
            <th class="text-center py-2">股票代码</th>
            <th class="text-center py-2">股票名称</th>
            <th class="text-center py-2">分红金额</th>
            <th class="text-center py-2">分红日期</th>
            <th class="text-center py-2">账号</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="div in dividends" :key="div.id" class="border-b hover:bg-gray-50">
            <td class="text-center py-2">{{ div.stock_code }}</td>
            <td class="text-center py-2">{{ div.stock_name }}</td>
            <td class="text-center py-2 text-green-600">{{ div.dividend_amount.toFixed(2) }}</td>
            <td class="text-center py-2">{{ formatDate(div.dividend_date) }}</td>
            <td class="text-center py-2">{{ getAccountName(div.account_id) }}</td>
          </tr>
          <tr v-if="dividends.length === 0">
            <td colspan="5" class="text-center py-4 text-gray-500">暂无分红记录</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 添加分红弹窗 -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-bold mb-4">添加分红</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">账号</label>
            <select v-model="newDividend.account_id" class="w-full border rounded px-3 py-2">
              <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">股票代码</label>
            <select v-model="newDividend.stock_code" @change="onStockCodeChange" class="w-full border rounded px-3 py-2">
              <option value="">请选择</option>
              <option v-for="pos in accountPositions" :key="pos.id" :value="pos.stock_code">
                {{ pos.stock_code }} - {{ pos.stock_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">股票名称</label>
            <input v-model="newDividend.stock_name" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">分红金额</label>
            <input v-model.number="newDividend.dividend_amount" type="number" step="0.01" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">分红日期</label>
            <input v-model="newDividend.dividend_date" type="date" class="w-full border rounded px-3 py-2" />
          </div>
        </div>
        <div class="flex justify-end space-x-2 mt-6">
          <button @click="showAddModal = false" class="px-4 py-2 border rounded hover:bg-gray-100">取消</button>
          <button @click="addDividend" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { dividendApi, accountApi, positionApi } from '../api'
import type { Dividend, Account, Position } from '../types'

const emit = defineEmits(['refresh'])

const dividends = ref<Dividend[]>([])
const accounts = ref<Account[]>([])
const accountPositions = ref<Position[]>([])
const showAddModal = ref(false)

const newDividend = ref({
  account_id: 0,
  stock_code: '',
  stock_name: '',
  dividend_amount: 0,
  dividend_date: '',
})

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const getAccountName = (id: number) => {
  const acc = accounts.value.find(a => a.id === id)
  return acc ? acc.name : '-'
}

const loadData = async () => {
  try {
    dividends.value = await dividendApi.list()
    accounts.value = await accountApi.list()
  } catch (e) {
    console.error('Failed to load data:', e)
  }
}

const addDividend = async () => {
  try {
    const dividendDate = new Date(newDividend.value.dividend_date)
    await dividendApi.create({
      ...newDividend.value,
      dividend_date: dividendDate.toISOString(),
    })
    showAddModal.value = false
    newDividend.value = {
      account_id: 0,
      stock_code: '',
      stock_name: '',
      dividend_amount: 0,
      dividend_date: '',
    }
    await loadData()
    emit('refresh')
  } catch (e) {
    console.error('Failed to add dividend:', e)
  }
}

onMounted(loadData)

watch(() => newDividend.value.account_id, async (newAccountId) => {
  if (newAccountId) {
    try {
      accountPositions.value = await positionApi.listByAccount(newAccountId)
      newDividend.value.stock_code = ''
      newDividend.value.stock_name = ''
    } catch (e) {
      console.error('Failed to load positions:', e)
    }
  } else {
    accountPositions.value = []
  }
})

const onStockCodeChange = () => {
  const pos = accountPositions.value.find(p => p.stock_code === newDividend.value.stock_code)
  if (pos) {
    newDividend.value.stock_name = pos.stock_name
  }
}
</script>