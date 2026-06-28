import { authReq } from './request'

export function login(data: { username: string; password: string }) {
  return authReq.post('/login', data)
}

export function getProfile() {
  return authReq.get('/profile')
}
