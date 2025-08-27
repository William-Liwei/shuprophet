import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: '项目概览' }
    },
    {
      path: '/app',
      name: 'app',
      component: () => import('../views/MainAppView.vue'),
      meta: { title: '核心功能' }
    },
    {
      path: '/algorithms',
      name: 'algorithms',
      component: () => import('../views/AlgorithmsView.vue'),
      meta: { title: '算法文库' }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: { title: '关于项目' }
    }
  ]
})

export default router