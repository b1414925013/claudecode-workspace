import request from './request'

export function listSecrets(params: { env_id: number; namespace: string }) {
  return request.get('/secrets/list', { params })
}

export function getSecretDetail(params: { env_id: number; namespace: string; secret_name: string; key: string }) {
  return request.get('/secrets/detail', { params })
}

export function syncSecrets(data: any) {
  return request.post('/secrets/sync', data)
}

export function listCredentials(params?: any) {
  return request.get('/credentials', { params })
}

export function createCredential(data: any) {
  return request.post('/credentials', data)
}

export function getCredential(id: number) {
  return request.get(`/credentials/${id}`)
}

export function updateCredential(id: number, data: any) {
  return request.put(`/credentials/${id}`, data)
}

export function deleteCredential(id: number) {
  return request.delete(`/credentials/${id}`)
}

export function revealCredential(id: number) {
  return request.post(`/credentials/${id}/reveal`)
}

export function exportCredentials(params?: any) {
  return request.post('/credentials/export', params)
}
