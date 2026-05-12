<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">账号管理</h2>
      <button @click="showAddModal = true" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        添加账号
      </button>
    </div>

    <!-- 账号列表 -->
    <div class="bg-white rounded-lg shadow p-6">
      <table class="min-w-full">
        <thead>
          <tr class="border-b">
            <th class="text-center py-2">ID</th>
            <th class="text-center py-2">名称</th>
            <th class="text-center py-2">类型</th>
            <th class="text-center py-2">创建时间</th>
            <th class="text-center py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in accounts" :key="account.id" class="border-b hover:bg-gray-50">
            <td class="text-center py-2">{{ account.id }}</td>
            <td class="text-center py-2">{{ account.name }}</td>
            <td class="text-center py-2">{{ account.account_type === 'cash' ? '现金账户' : '融资账户' }}</td>
            <td class="text-center py-2">{{ formatDate(account.created_at) }}</td>
            <td class="text-center py-2">
              <button @click="deleteAccount(account.id)" class="text-red-600 hover:text-red-800">删除</button>
            </td>
          </tr>
          <tr v-if="accounts.length === 0">
            <td colspan="5" class="text-center py-4 text-gray-500">暂无账号</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 添加账号弹窗 -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-bold mb-4">添加账号</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">账号名称</label>
            <input v-model="newAccount.name" type="text" class="w-full border rounded px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">账号类型</label>
            <select v-model="newAccount.account_type" class="w-full border rounded px-3 py-2">
              <option value="cash">现金账户</option>
              <option value="margin">融资账户</option>
            </select>
          </div>
        </div>
        <div class="flex justify-end space-x-2 mt-6">
          <button @click="showAddModal = false" class="px-4 py-2 border rounded hover:bg-gray-100">取消</button>
          <button @click="addAccount" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { accountApi } from '../api'
import type { Account } from '../types'

const emit = defineEmits(['refresh'])

const accounts = ref<Account[]>([])
const showAddModal = ref(false)
const newAccount = ref({
  name: '',
  account_type: 'cash',
})

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const loadAccounts = async () => {
  try {
    accounts.value = await accountApi.list()
  } catch (e) {
    console.error('Failed to load accounts:', e)
  }
}

const addAccount = async () => {
  try {
    await accountApi.create(newAccount.value)
    showAddModal.value = false
    newAccount.value = { name: '', account_type: 'cash' }
    await loadAccounts()
    emit('refresh')
  } catch (e) {
    console.error('Failed to add account:', e)
  }
}

const deleteAccount = async (id: number) => {
  if (confirm('确定要删除这个账号吗？')) {
    try {
      await accountApi.delete(id)
      await loadAccounts()
      emit('refresh')
    } catch (e) {
      console.error('Failed to delete account:', e)
    }
  }
}

onMounted(loadAccounts)
</script>