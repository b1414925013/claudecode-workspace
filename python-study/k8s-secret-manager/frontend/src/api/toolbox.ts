import request from './request'

export function getAuditLogs(params?: any) {
  return request.get('/audit-logs', { params })
}

export function exportAuditLogs(params?: any) {
  return request.get('/audit-logs/export', { params, responseType: 'blob' })
}

export function getDashboardStats() {
  return request.get('/dashboard/stats')
}
