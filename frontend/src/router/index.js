import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

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
      component: () => import('../views/Login.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/Register.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/Home.vue'),
    },
    {
     path: '/admin/subject',
     name: 'admin-subject',
     component: () => import('../views/admin/Subject.vue')
    },
   {
    path: '/chapters/:chapterId/quizzes',
    component: () => import('../views/admin/Quiz.vue'),
    props: true
   },
   {
     path: '/admin/users',
     name: 'admin-users',
     component: () => import('../views/admin/User.vue')
    },
    { path: '/user', 
      component: () => import('../views/user/home.vue')
     },
     { path: '/user/subject', 
      component: () => import('../views/user/subject.vue')
     },
     {
      path: '/quiz/:id',
      component: () => import('../views/user/Quiz.vue'),
      props: true
    },
    {path: '/score', 
      component: () => import('../views/user/Score.vue')
     },
     {path: '/summary', 
      component: () => import('../views/user/Summary.vue')
     },
  ],
})

export default router
