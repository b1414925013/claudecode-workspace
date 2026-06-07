import { createRouter, createWebHistory } from 'vue-router'
import Search from '../views/Search.vue'
import Rankings from '../views/Rankings.vue'
import Library from '../views/Library.vue'

const routes = [
  { path: '/', component: Search },
  { path: '/rankings', component: Rankings },
  { path: '/library', component: Library }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
