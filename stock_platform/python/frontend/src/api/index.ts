import type { Account, Position, Trade, Dividend, Statistics, Summary, StockPrice } from '../types'
import { API_BASE } from '../config'

async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`)
  }
  return response.json()
}

// 账号管理
export const accountApi = {
  list: () => fetchApi<Account[]>(`${API_BASE}/accounts`),
  get: (id: number) => fetchApi<Account>(`${API_BASE}/accounts/${id}`),
  create: (data: Omit<Account, 'id' | 'created_at'>) =>
    fetchApi<Account>(`${API_BASE}/accounts`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`${API_BASE}/accounts/${id}`, {
      method: 'DELETE',
    }),
}

// 持仓管理
export const positionApi = {
  list: (accountId?: number) =>
    fetchApi<Position[]>(`${API_BASE}/positions${accountId ? `?account_id=${accountId}` : ''}`),
  listByAccount: (accountId: number) =>
    fetchApi<Position[]>(`${API_BASE}/positions/account/${accountId}`),
  get: (id: number) => fetchApi<Position>(`${API_BASE}/positions/${id}`),
  create: (data: Omit<Position, 'id' | 'created_at' | 'updated_at'>) =>
    fetchApi<Position>(`${API_BASE}/positions`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id: number, data: Omit<Position, 'id' | 'created_at' | 'updated_at'>) =>
    fetchApi<Position>(`${API_BASE}/positions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id: number) =>
    fetchApi<{ message: string }>(`${API_BASE}/positions/${id}`, {
      method: 'DELETE',
    }),
}

// 交易记录
export const tradeApi = {
  list: (params?: { account_id?: number; start_date?: string; end_date?: string }) => {
    const query = new URLSearchParams()
    if (params?.account_id) query.append('account_id', String(params.account_id))
    if (params?.start_date) query.append('start_date', params.start_date)
    if (params?.end_date) query.append('end_date', params.end_date)
    const queryStr = query.toString()
    return fetchApi<Trade[]>(`${API_BASE}/trades${queryStr ? `?${queryStr}` : ''}`)
  },
  create: (data: Omit<Trade, 'id' | 'profit' | 'created_at'>) =>
    fetchApi<Trade>(`${API_BASE}/trades`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

// 分红记录
export const dividendApi = {
  list: (accountId?: number) =>
    fetchApi<Dividend[]>(`${API_BASE}/dividends${accountId ? `?account_id=${accountId}` : ''}`),
  create: (data: Omit<Dividend, 'id' | 'created_at'>) =>
    fetchApi<Dividend>(`${API_BASE}/dividends`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

// 统计分析
export const statisticsApi = {
  get: (params?: { account_id?: number; start_date?: string; end_date?: string }) => {
    const query = new URLSearchParams()
    if (params?.account_id) query.append('account_id', String(params.account_id))
    if (params?.start_date) query.append('start_date', params.start_date)
    if (params?.end_date) query.append('end_date', params.end_date)
    const queryStr = query.toString()
    return fetchApi<Statistics>(`${API_BASE}/statistics${queryStr ? `?${queryStr}` : ''}`)
  },
  summary: () => fetchApi<Summary>(`${API_BASE}/summary`),
}

// 股票价格
export const stockPriceApi = {
  syncAll: () => fetchApi<{ message: string }>(`${API_BASE}/stock-prices/sync`, { method: 'POST' }),
  syncOne: (stockCode: string) =>
    fetchApi<StockPrice>(`${API_BASE}/stock-prices/${stockCode}`, { method: 'POST' }),
  getLatest: (stockCode: string) =>
    fetchApi<StockPrice>(`${API_BASE}/stock-prices/${stockCode}/latest`),
}