import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/nebula-tools/'),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../pages/Home.vue'),
    },
    {
      path: '/visualize',
      name: 'visualize',
      component: () => import('../pages/Visualizer.vue'),
    },
    {
      path: '/builder',
      name: 'builder',
      component: () => import('../pages/Builder.vue'),
    },
  ],
})

export default router
