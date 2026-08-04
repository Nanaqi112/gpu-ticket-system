import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/tickets',
    name: 'TicketList',
    component: () => import('../views/TicketList.vue')
  },
  {
    path: '/tickets/add',
    name: 'AddTicket',
    component: () => import('../views/AddTicket.vue')
  },
  {
    path: '/tickets/:id',
    name: 'TicketDetail',
    component: () => import('../views/TicketDetail.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router