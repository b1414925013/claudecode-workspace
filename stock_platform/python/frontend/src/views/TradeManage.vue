<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">交易记录</h2>
      <button @click="showAddModal = true" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        记录交易
      </button>
    </div>

    <!-- 交易列表 -->
    <div class="bg-white rounded-lg shadow p-6">
      <table class="min-w-full">
        <thead>
          <tr class="border-b">
            <th class="text-center py-2">股票代码</th>
            <th class="text-center py-2">股票名称</th>
            <th class="text-center py-2">类型</th>
            <th class="text-center py-2">数量</th>
            <th class="text-center py-2">价格</th>
            <th class="text-center py-2">手续费</th>
            <th class="text-center py-2">日期</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trade in trades" :key="trade.id" class="border-b hover:bg-gray-50">
            <td class="text-center py-2">{{ trade.stock_code }}</td>
            <td class="text-center py-2">{{ trade.stock_name }}</td>
            <td class="text-center py-2">
              <span :class="trade.trade_type === 'buy' ? 'text-green-600' : 'text-red-600'">
                {{ trade.trade_type === 'buy' ? '买入' : '卖出' }}
              </span>
            </td>
            <td class="text-center py-2">{{ trade.quantity }}</td>
            <td class="text-center py-2">{{ trade.price.toFixed(2) }}</td>
            <td class="text-center py-2">{{ trade.commission.toFixed(2) }}</td>
            <td class="text-center py-2">{{ formatDate(trade.trade_date) }}</td>
          </tr>
          <tr v-if="trades.length === 0">
            <td colspan="7" class="text-center py-4 text-gray-500">暂无交易记录</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 添加交易弹窗 -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-bold mb-4">记录交易</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">账号</label>
            <select v-model="newTrade.account_id" class="w-full border rounded px-3 py-2">
              <option v-for="acc in accounts" :key="acc.id" :value="acc.id">{{ acc.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">股票代码</label>
            <select v-model="newTrade.stock_code" @change="onStockCodeChange" class="w-full border rounded px-3 py-2">
              <option value="">请选择</option>
              <option v-for="pos in accountPositions" :key="pos.id" :value="pos.stock_code">
                {{ pos.stock_code }} - {{ pos.stock_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">股票名称</label>
            <input v-model="newTrade.stock_name" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">交易类型</label>
            <select v-model="newTrade.trade_type" class="w-full border rounded px-3 py-2">
              <option value="buy">买入</option>
              <option value="sell">卖出</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">数量</label>
            <input v-model.number="newTrade.quantity" type="number" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">价格</label>
            <input v-model.number="newTrade.price" type="number" step="0.01" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">手续费</label>
            <input v-model.number="newTrade.commission" type="number" step="0.01" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">交易日期</label>
            <input v-model="newTrade.trade_date" type="date" class="w-full border rounded px-3 py-2" />
          </div>
        </div>
        <div class="flex justify-end space-x-2 mt-6">
          <button @click="showAddModal = false" class="px-4 py-2 border rounded hover:bg-gray-100">取消</button>
          <button @click="addTrade" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { tradeApi, accountApi, positionApi } from '../api'
import type { Trade, Account, Position } from '../types'

const emit = defineEmits(['refresh'])

const trades = ref<Trade[]>([])
const accounts = ref<Account[]>([])
const accountPositions = ref<Position[]>([])
const showAddModal = ref(false)

const newTrade = ref({
  account_id: 0,
  stock_code: '',
  stock_name: '',
  trade_type: 'buy',
  quantity: 0,
  price: 0,
  commission: 0,
  trade_date: '',
})

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const loadData = async () => {
  try {
    trades.value = await tradeApi.list()
    accounts.value = await accountApi.list()
  } catch (e) {
    console.error('Failed to load data:', e)
  }
}

const addTrade = async () => {
  try {
    const tradeDate = new Date(newTrade.value.trade_date)
    await tradeApi.create({
      ...newTrade.value,
      trade_date: tradeDate.toISOString(),
    })
    showAddModal.value = false
    newTrade.value = {
      account_id: 0,
      stock_code: '',
      stock_name: '',
      trade_type: 'buy',
      quantity: 0,
      price: 0,
      commission: 0,
      trade_date: '',
    }
    await loadData()
    emit('refresh')
  } catch (e) {
    console.error('Failed to add trade:', e)
  }
}

onMounted(loadData)

watch(() => newTrade.value.account_id, async (newAccountId) => {
  if (newAccountId) {
    try {
      accountPositions.value = await positionApi.listByAccount(newAccountId)
      newTrade.value.stock_code = ''
      newTrade.value.stock_name = ''
    } catch (e) {
      console.error('Failed to load positions:', e)
    }
  } else {
    accountPositions.value = []
  }
})

const onStockCodeChange = () => {
  const pos = accountPositions.value.find(p => p.stock_code === newTrade.value.stock_code)
  if (pos) {
    newTrade.value.stock_name = pos.stock_name
  }
}
</script>