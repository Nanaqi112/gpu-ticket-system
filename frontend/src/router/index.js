import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tickets',
    name: 'TicketList',
    component: () => import('../views/TicketList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tickets/add',
    name: 'AddTicket',
    component: () => import('../views/AddTicket.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/tickets/:id',
    name: 'TicketDetail',
    component: () => import('../views/TicketDetail.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 如果没有用户信息，尝试获取
  if (!userStore.user && to.meta.requiresAuth !== false) {
    await userStore.fetchUserInfo()
  }

  // 不需要认证的页面
  if (to.meta.requiresAuth === false) {
    // 如果已登录，跳转到首页
    if (userStore.isLoggedIn && to.name === 'Login') {
      next('/')
      return
    }
    next()
    return
  }

  // 需要认证的页面
  if (!userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 需要管理员权限的页面
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next('/')
    return
  }

  next()
})

export default router