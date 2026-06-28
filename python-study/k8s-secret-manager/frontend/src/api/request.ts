import axios from 'axios'
import { ElMessage } from 'element-plus'

function createServiceRequest(basePath: string) {
  const instance = axios.create({
    baseURL: basePath,
    timeout: 30000,
  })

  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  instance.interceptors.response.use(
    (response) => {
      const data = response.data
      if (data.code !== 0) {
        ElMessage.error(data.message || '请求失败')
        return Promise.reject(data)
      }
      return data
    },
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('token')
        window.location.href = '/#/login'
        ElMessage.error('登录已过期，请重新登录')
      } else {
        ElMessage.error(error.response?.data?.message || '网络错误')
      }
      return Promise.reject(error)
    },
  )

  return instance
}

/** 认证服务（auth-service:8001）- 前缀 /api/v1/auth */
export const authReq = createServiceRequest('/api/v1/auth')

/** 环境管理服务（env-service:8002）- 前缀 /api/v1/env */
export const envReq = createServiceRequest('/api/v1/env')

/** 密钥管理服务（secret-service:8003）- 前缀 /api/v1/secret */
export const secretReq = createServiceRequest('/api/v1/secret')

/** 工具箱服务（toolbox-service:8004）- 前缀 /api/v1/toolbox */
export const toolboxReq = createServiceRequest('/api/v1/toolbox')

/** API 网关（api-gateway:8000）- 前缀 /api/v1/gateway */
export const gatewayReq = createServiceRequest('/api/v1/gateway')
