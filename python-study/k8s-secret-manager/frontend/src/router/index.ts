import { createRouter, createWebHashHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login/LoginView.vue'),
    },
    {
      path: '/',
      component: MainLayout,
      redirect: '/dashboard',
      children: [
        { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/DashboardView.vue') },
        { path: 'environments', name: 'Environments', component: () => import('@/views/environments/EnvListView.vue') },
        { path: 'secrets', name: 'Secrets', component: () => import('@/views/secrets/SecretListView.vue') },
        { path: 'credentials', name: 'Credentials', component: () => import('@/views/credentials/CredentialListView.vue') },
        { path: 'toolbox', name: 'Toolbox', component: () => import('@/views/toolbox/ToolboxView.vue') },
        { path: 'users', name: 'Users', component: () => import('@/views/users/UserManageView.vue') },
        { path: 'audit-logs', name: 'AuditLogs', component: () => import('@/views/audit-logs/AuditLogView.vue') },
      ],
    },
  ],
})

router.beforeEach((to, _from) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'Login' && !token) {
    return { name: 'Login' }
  }
})

export default router
