import request from './request'

export function getEnvironments(params?: any) {
  return request.get('/environments', { params })
}

export function createEnvironment(data: any) {
  return request.post('/environments', data)
}

export function updateEnvironment(id: number, data: any) {
  return request.put(`/environments/${id}`, data)
}

export function deleteEnvironment(id: number) {
  return request.delete(`/environments/${id}`)
}

export function getNamespaces(id: number) {
  return request.get(`/environments/${id}/namespaces`)
}

export function checkHealth(id: number) {
  return request.get(`/environments/${id}/health`)
}
