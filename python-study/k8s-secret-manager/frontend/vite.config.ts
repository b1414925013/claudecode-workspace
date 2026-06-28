import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api/v1/auth':    { target: 'http://localhost:8001', changeOrigin: true },
      '/api/v1/env':     { target: 'http://localhost:8002', changeOrigin: true },
      '/api/v1/secret':  { target: 'http://localhost:8003', changeOrigin: true },
      '/api/v1/toolbox': { target: 'http://localhost:8004', changeOrigin: true },
      '/api/v1/gateway': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
