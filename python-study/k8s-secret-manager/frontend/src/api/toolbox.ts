import { gatewayReq } from './request'

export function getAuditLogs(params?: any) {
  return gatewayReq.get('/audit-logs', { params })
}

export function exportAuditLogs(params?: any) {
  return gatewayReq.get('/audit-logs/export', { params, responseType: 'blob' })
}

export function getDashboardStats() {
  return gatewayReq.get('/dashboard/stats')
}
