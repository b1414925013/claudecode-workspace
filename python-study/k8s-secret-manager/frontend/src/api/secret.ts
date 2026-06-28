import { secretReq } from './request'

export function listSecrets(params: { env_id: number; namespace: string }) {
  return secretReq.get('/secrets/list', { params })
}

export function getSecretDetail(params: { env_id: number; namespace: string; secret_name: string; key: string }) {
  return secretReq.get('/secrets/detail', { params })
}

export function syncSecrets(data: any) {
  return secretReq.post('/secrets/sync', data)
}

export function listCredentials(params?: any) {
  return secretReq.get('/credentials', { params })
}

export function createCredential(data: any) {
  return secretReq.post('/credentials', data)
}

export function getCredential(id: number) {
  return secretReq.get(`/credentials/${id}`)
}

export function updateCredential(id: number, data: any) {
  return secretReq.put(`/credentials/${id}`, data)
}

export function deleteCredential(id: number) {
  return secretReq.delete(`/credentials/${id}`)
}

export function revealCredential(id: number) {
  return secretReq.post(`/credentials/${id}/reveal`)
}

export function exportCredentials(params?: any) {
  return secretReq.post('/credentials/export', params)
}
