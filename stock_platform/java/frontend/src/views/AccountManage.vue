<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">账号管理</h2>

    <!-- 添加账号 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h3 class="text-lg font-bold mb-4">添加新账号</h3>
      <div class="flex gap-4">
        <input
          v-model="newAccount.name"
          type="text"
          placeholder="账号名称"
          class="border rounded px-3 py-2 flex-1"
        />
        <select v-model="newAccount.accountType" class="border rounded px-3 py-2">
          <option value="cash">现金账户</option>
          <option value="margin">融资账户</option>
        </select>
        <button @click="addAccount" class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
          添加
        </button>
      </div>
    </div>

    <!-- 账号列表 -->
    <div class="bg-white rounded-lg shadow">
      <table class="min-w-full">
        <thead>
          <tr class="border-b bg-gray-50">
            <th class="text-center py-3">ID</th>
            <th class="text-center py-3">账号名称</th>
            <th class="text-center py-3">类型</th>
            <th class="text-center py-3">创建时间</th>
            <th class="text-center py-3">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in accounts" :key="account.id" class="border-b hover:bg-gray-50">
            <td class="text-center py-3">{{ account.id }}</td>
            <td class="text-center py-3">{{ account.name }}</td>
            <td class="text-center py-3">{{ account.account_type === 'cash' ? '现金账户' : '融资账户' }}</td>
            <td class="text-center py-3">{{ formatDate(account.created_at) }}</td>
            <td class="text-center py-3">
              <button @click="deleteAccount(account.id)" class="text-red-600 hover:text-red-800">删除</button>
            </td>
          </tr>
          <tr v-if="accounts.length === 0">
            <td colspan="5" class="text-center py-8 text-gray-500">暂无账号</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { accountApi } from '../api'
import type { Account } from '../types'

const emit = defineEmits(['refresh'])

const accounts = ref<Account[]>([])
const newAccount = ref({ name: '', accountType: 'cash' })

const loadAccounts = async () => {
  try {
    accounts.value = await accountApi.list()
  } catch (e) {
    console.error('Failed to load accounts:', e)
  }
}

const addAccount = async () => {
  if (!newAccount.value.name) return
  try {
    await accountApi.create({ name: newAccount.value.name, account_type: newAccount.value.accountType })
    newAccount.value = { name: '', accountType: 'cash' }
    await loadAccounts()
    emit('refresh')
  } catch (e) {
    console.error('Failed to add account:', e)
  }
}

const deleteAccount = async (id: number) => {
  try {
    await accountApi.delete(id)
    await loadAccounts()
    emit('refresh')
  } catch (e) {
    console.error('Failed to delete account:', e)
  }
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(loadAccounts)
</script>