import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/admin',
      name: 'admin_home',
      component: () => import('@/views/admin/HomeView.vue') 
    },
    {
      path: '/user',
      name: 'user_home',
      component: () => import('@/views/user/HomeView.vue') 
    },
    {
      path: '/admin/lots',
      name: 'lots',
      component: () => import('@/views/admin/Lots.vue') 
    },
    {
      path: '/admin/spots',
      name: 'spots',
      component: () => import('@/views/admin/Spots.vue') 
    },
    {
      path: '/admin/Users',
      name: 'Users',
      component: () => import('@/views/admin/Users.vue') 
    },
    {
      path: '/admin/Summary',
      name: 'Summary',
      component: () => import('@/views/admin/Summary.vue') 
    },
    {
      path: '/parking',
      name: 'parking',
      component: () => import('@/views/user/Parking.vue') 
    },
        {
      path: '/history',
      name: 'history',
      component: () => import('@/views/user/History.vue') 
    },
  ],
})

export default router