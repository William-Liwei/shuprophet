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
      path: '/agent',
      name: 'agent',
      component: () => import('../views/AgentView.vue'),
      meta: { title: '智能助理' }
    },
    {
      path: '/app',
      name: 'app',
      component: () => import('../views/MainAppView.vue'),
      meta: { title: '数据探索' }
    },
    {
      path: '/algorithms',
      name: 'algorithms',
      component: () => import('../views/AlgorithmsView.vue'),
      meta: { title: '算法文库' }
    },
    {
      path: '/solutions',
      name: 'solutions',
      component: () => import('../views/SolutionsView.vue'),
      meta: { title: '解决方案' }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: { title: '关于项目' }
    },
    {
      path: '/community',
      name: 'community',
      component: () => import('../views/CommunityView.vue'),
      meta: { title: '社区广场' }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { title: '登录' }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { title: '注册' }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { title: '个人中心', requiresAuth: true }
    },
    {
      path: '/user/:id',
      name: 'user-profile',
      component: () => import('../views/UserProfileView.vue'),
      meta: { title: '用户主页' }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: { title: '管理后台' }
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    next('/login')
  } else {
    next()
  }
})

export default router