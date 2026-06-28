import { envReq } from './request'

export function getEnvironments(params?: any) {
  return envReq.get('/environments', { params })
}

export function createEnvironment(data: any) {
  return envReq.post('/environments', data)
}

export function updateEnvironment(id: number, data: any) {
  return envReq.put(`/environments/${id}`, data)
}

export function deleteEnvironment(id: number) {
  return envReq.delete(`/environments/${id}`)
}

export function getNamespaces(id: number) {
  return envReq.get(`/environments/${id}/namespaces`)
}

export function checkHealth(id: number) {
  return envReq.get(`/environments/${id}/health`)
}
